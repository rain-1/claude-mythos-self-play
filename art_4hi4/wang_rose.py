"""THE ROSE OF VANISHING SHADOWS — for Hong Wang, Fields Medal 2026.

The four-corner Cantor set C (the canonical purely-unrectifiable 1-set) casts
a shadow in every direction.  Besicovitch's projection theorem says almost
every shadow has measure zero; the Favard length (the mean shadow) dies as the
set is refined.  Wang-Zahl (2025): despite living on nothing, a set owning a
needle in every direction of R^3 is forced to full dimension -- Kakeya.

The rose: polar angle = direction of projection; radius walks outward through
GENERATIONS of the set (growth rings of refinement, gens 2/4/6/9); along each
ray the ring shows that direction's shadow, lit by its exact multiplicity
(how many generation-n squares cover each point of the shadow).  Almost every
ray's shadow shatters into filaments and fades; at the exceptional rational
directions tan(theta) in {1/2, 2} (and their mirror images) the digit sums fill
an interval exactly, and an unbroken soft spoke survives to the rim; along the
anti-diagonal the digits collide and the fire doubles.  The pupil holds the
deed: the dust itself, one grain per line of light.
"""
import numpy as np
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import filmic, bloom, save_png, ramp, bilinear_splat
from scipy.ndimage import gaussian_filter

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "rose_of_vanishing_shadows.png")
SIZE = int(os.environ.get("SIZE", "4096"))

THBINS = int(os.environ.get('THBINS', '32768'))          # angle bins over [0, pi)
RB = 2048               # radial bins per ring raster
GENS = [3, 5, 7, 9]          # generation per ring, inner -> outer
R_EDGES = [0.205, 0.365, 0.545, 0.745, 0.985]

digs = np.array([0.0, 0.75])


def cantor_pts(g):
    K = np.zeros(1)
    for k in range(g):
        K = (K[:, None] + digs[None, :] * 4.0 ** (-k)).ravel()
    return K + 0.5 * 4.0 ** (-g)   # interval centers


thetas = (np.arange(THBINS) + 0.5) / THBINS * np.pi
cs, sn = np.cos(thetas), np.sin(thetas)
# common limit-hull half-width: shadows of every generation share this hull,
# so filaments ALIGN and fork radially from ring to ring.
hull = (np.abs(cs) + np.abs(sn)) * 0.5          # (THBINS,)

FN = 2 * RB
freqs = np.fft.rfftfreq(FN)                      # cycles per bin


def ring_raster(g):
    """Exact multiplicity of the generation-g shadow, per angle column.

    The four-corner set is K x K, so the projection multiplicity at angle t is
    hist(A cos t) * hist(B sin t) * box(4^-g|cos t|) * box(4^-g|sin t|)
    -- three FFT products per angle, exact (trapezoid) anti-aliasing.
    """
    K = cantor_pts(g) - 0.5
    out = np.zeros((THBINS, RB), np.float32)
    CH = 512
    for c0 in range(0, THBINS, CH):
        c1 = min(THBINS, c0 + CH)
        m = c1 - c0
        csb = cs[c0:c1]; snb = sn[c0:c1]
        hb = hull[c0:c1]
        # bin centers: s in [-hull, hull] -> [0, RB)
        scale = RB / (2 * hb)                       # bins per unit s
        HA = np.zeros((m, FN)); HB = np.zeros((m, FN))
        for vals, cf, Hm in ((K, csb, HA), (K, snb, HB)):
            P = vals[None, :] * cf[:, None]         # (m, 2^g)
            X = (P + hb[:, None]) * scale[:, None]  # fractional bin
            ix = np.floor(X).astype(np.int64)
            fx = X - ix
            base = np.arange(m)[:, None] * FN
            np.add.at(Hm.ravel(), (np.clip(ix, 0, FN - 1) + base).ravel(),
                      (1 - fx).ravel())
            np.add.at(Hm.ravel(), (np.clip(ix + 1, 0, FN - 1) + base).ravel(),
                      fx.ravel())
        FA = np.fft.rfft(HA, axis=1)
        FB = np.fft.rfft(HB, axis=1)
        # box kernels (width in bins), centered: use |sinc| phase-free form
        wA = (4.0 ** (-g)) * np.abs(csb) * scale    # box widths in bins
        wB = (4.0 ** (-g)) * np.abs(snb) * scale
        arg = np.pi * freqs[None, :]
        SA = np.sinc(freqs[None, :] * wA[:, None])
        SB = np.sinc(freqs[None, :] * wB[:, None])
        conv = np.fft.irfft(FA * FB * SA * SB, n=FN, axis=1)
        # product of two centered-at-mid histograms: result centered at sum of
        # centers; both were binned against the same origin so the convolution
        # lives at index (iA + iB) - the s=0 point sits at bin RB. Take the
        # central RB window [RB/2, 3RB/2).
        out[c0:c1] = np.maximum(conv[:, RB // 2: RB // 2 + RB], 0)
    colmass = out.sum(1, keepdims=True)
    out = out / np.maximum(colmass / RB, 1e-12)
    return out


def exact_shadow_length(g, ths):
    """Exact length of the union of projected gen-g squares, per angle."""
    K = cantor_pts(g) - 0.5
    A, B = np.meshgrid(K, K, indexing="ij")
    A = A.ravel(); B = B.ravel()
    n = len(A)
    out = np.empty(len(ths))
    CH = max(1, int(3.0e7 // n))
    for c0 in range(0, len(ths), CH):
        c1 = min(len(ths), c0 + CH)
        cb = np.cos(ths[c0:c1])[:, None]
        sb = np.sin(ths[c0:c1])[:, None]
        h = 0.5 * 4.0 ** (-g) * (np.abs(cb) + np.abs(sb))
        Pc = A[None, :] * cb + B[None, :] * sb
        st = np.sort(Pc - h, axis=1)
        # ends sorted BY START: sort (start,end) pairs by start
        order = np.argsort(Pc - h, axis=1)
        en = np.take_along_axis(Pc + h, order, axis=1)
        erun = np.maximum.accumulate(en, axis=1)
        gaps = np.maximum(0.0, st[:, 1:] - erun[:, :-1]).sum(axis=1)
        out[c0:c1] = (erun[:, -1] - st[:, 0]) - gaps
    return out


TH_SPARSE = np.linspace(0, np.pi, 721, endpoint=False) + np.pi / 1442
shadow_len = {}
rings = []
for g in GENS:
    rings.append(ring_raster(g))
    shadow_len[g] = exact_shadow_length(g, TH_SPARSE)
    print(f"gen {g}: ring done; exact Favard length = "
          f"{shadow_len[g].mean():.4f}  ({time.time()-t0:.1f}s)", flush=True)
fav = np.array([shadow_len[g].mean() for g in GENS])
ring_lum = (fav / fav[0]) ** 0.45
print("ring luminance scales:", np.round(ring_lum, 3))
np.savez(os.path.join(HERE, "rose_shadow_lengths.npz"),
         thetas=TH_SPARSE, gens=np.array(GENS),
         **{f"L{g}": shadow_len[g] for g in GENS})

# ---------------------------------------------------------------- polar paint
S = 2
H = W = SIZE * S
R = 0.5 * H
yy = (np.arange(H) + 0.5 - H / 2)
conc = np.zeros((H, W), np.float32)
ringid = np.full((H, W), -1, np.int8)
for r0 in range(0, H, 256):
    r1 = min(H, r0 + 256)
    dy = yy[r0:r1][:, None]
    dx = yy[None, :]
    rr = np.sqrt(dx * dx + dy * dy) / R
    th = np.mod(np.arctan2(dy, dx), np.pi) / np.pi * THBINS - 0.5
    ti = np.floor(th).astype(np.int64)
    tf = (th - ti).astype(np.float32)
    ti0 = np.mod(ti, THBINS); ti1 = np.mod(ti + 1, THBINS)
    out = np.zeros(rr.shape, np.float32)
    rid = np.full(rr.shape, -1, np.int8)
    for k in range(len(GENS)):
        e0, e1 = R_EDGES[k], R_EDGES[k + 1]
        m = (rr >= e0) & (rr < e1)
        if not m.any():
            continue
        u = (rr[m] - e0) / (e1 - e0) * (RB - 1)
        ui = np.floor(u).astype(np.int64)
        uf = (u - ui).astype(np.float32)
        ui1 = np.minimum(ui + 1, RB - 1)
        Rk = rings[k]
        v = ((Rk[ti0[m], ui] * (1 - tf[m]) + Rk[ti1[m], ui] * tf[m]) * (1 - uf) +
             (Rk[ti0[m], ui1] * (1 - tf[m]) + Rk[ti1[m], ui1] * tf[m]) * uf)
        out[m] = v * ring_lum[k]
        rid[m] = k
    conc[r0:r1] = out
    ringid[r0:r1] = rid
print(f"polar sample done ({time.time()-t0:.1f}s)", flush=True)

Hf = Wf = SIZE
conc = conc.reshape(Hf, S, Wf, S).mean(axis=(1, 3))
ringid = ringid.reshape(Hf, S, Wf, S).max(axis=(1, 3))

x = gaussian_filter(conc, 0.6)
lum = filmic(x, k=0.66, gamma=0.80)
hot = filmic(x, k=0.085, gamma=1.0) ** 2.8

# temperature by concentration: soft = verdigris depths, blazing = gold-white
stops = [
    (0.00, (0.012, 0.030, 0.050)),
    (0.22, (0.060, 0.280, 0.330)),   # verdigris
    (0.45, (0.360, 0.560, 0.500)),   # sea glass
    (0.68, (0.900, 0.660, 0.260)),   # amber
    (0.86, (1.000, 0.850, 0.470)),   # gold
    (1.00, (1.000, 0.960, 0.850)),   # white heat
]
tpos = filmic(x, k=0.40, gamma=0.9)
rgb = ramp(tpos, stops) * lum[..., None]
rgb += hot[..., None] * np.array([1.0, 0.96, 0.88]) * 1.05

# ------------------------------------------------------------------ the pupil
pup_r = R_EDGES[0] * 0.985
seal = np.zeros((Hf, Wf), np.float64)
Kp = cantor_pts(6) - 0.5
Ap, Bp = np.meshgrid(Kp, Kp, indexing="ij")
half = pup_r * 0.70 * Hf / 2
cx = cy = Hf / 2
xs = cx + Ap.ravel() * 2 * half
ys = cy - Bp.ravel() * 2 * half
bilinear_splat(seal, xs, ys, np.full(xs.size, (Hf / 1024.0) ** 2))
seal = gaussian_filter(seal, max(0.8, Hf / 4096))
sg = gaussian_filter(seal, 6.0 * Hf / 4096)
rgb += (filmic(seal, k=1.1, gamma=0.85) * 0.9 + sg * 0.30)[..., None] \
       * np.array([0.60, 0.88, 0.90])

rgb = bloom(rgb, mask_lo=0.72, sigma=5.0 * Hf / 4096, strength=0.40, tint=(1.0, 0.9, 0.75))
rgb = bloom(rgb, mask_lo=0.30, sigma=30.0 * Hf / 4096, strength=0.14, tint=(0.55, 0.8, 0.9))
save_png(rgb, OUT)
print(f"total {time.time()-t0:.1f}s")
