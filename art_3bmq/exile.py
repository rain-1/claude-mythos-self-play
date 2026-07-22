"""THE CROSSINGS IN EXILE.

H(t) = A + tB with A,B real symmetric: for real t all eigenvalues are REAL
(the 51-vote MO front-page fact). The crossings the spectrum avoids on the
real road did not vanish -- they live in the complex t-plane as exceptional
points, the zeros of the discriminant  D(t) = prod_{i<j}(l_i(t)-l_j(t))^2,
strung in conjugate pairs off the axis. Bottom band: the N real eigenvalue
threads, near-misses glowing. Sky above: log|D| starfield -- each avoided
crossing sits directly below the exiled star that governs it; the closer
the star to the road, the tighter the squeeze.

VERIFIED per star: eigenvalue pair coalesces (gap < 1e-6), monodromy around
the star is a transposition (the two threads EXCHANGE), and each low star's
Re(t) matches the local minimum-gap location on the road.

usage: python3 exile.py SIZE OUT SEED N
"""
import sys, os
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom
from PIL import Image

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 640
OUT = sys.argv[2] if len(sys.argv) > 2 else "art_3bmq/proto/exile_proto.png"
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 1
N = int(sys.argv[4]) if len(sys.argv) > 4 else 9

TA, TB = -2.0, 2.0
IMTOP = float(os.environ.get("IMTOP", 1.05))
SKYFRAC = 0.60
SS = 2
S = SIZE * SS
rs = S / 1280.0
SKY_H = int(S * SKYFRAC)
BAND_H = S - SKY_H

rng = np.random.default_rng(SEED)
A = rng.normal(0, 1, (N, N)); A = (A + A.T) / np.sqrt(2 * N)
Bm = rng.normal(0, 1, (N, N)); Bm = (Bm + Bm.T) / np.sqrt(2 * N)

def eigs_c(t):
    """eigenvalues of A + t B for complex t (vectorized over flat t)."""
    t = np.asarray(t, complex)
    M = A[None, :, :] + t[:, None, None] * Bm[None, :, :]
    return np.linalg.eigvals(M)

def Dlog(t):
    """log|disc| for flat complex t array."""
    lam = eigs_c(t)
    out = np.zeros(t.shape, float)
    for i in range(N):
        for j in range(i + 1, N):
            out += 2 * np.log(np.abs(lam[:, i] - lam[:, j]) + 1e-300)
    return out

def Dval(t):
    lam = eigs_c(np.atleast_1d(t))
    d = np.ones(lam.shape[0], complex)
    for i in range(N):
        for j in range(i + 1, N):
            d *= (lam[:, i] - lam[:, j]) ** 2
    return d

# ---------------- find exceptional points ---------------------------------
gx = np.linspace(TA - 0.2, TB + 0.2, 260)
gy = np.linspace(0.015, IMTOP + 0.25, 130)
GX, GY = np.meshgrid(gx, gy)
tt = (GX + 1j * GY).ravel()
ld = Dlog(tt).reshape(GY.shape)
# local minima cells as Newton starts
cand = []
for r in range(1, ld.shape[0] - 1):
    for c in range(1, ld.shape[1] - 1):
        w = ld[r - 1:r + 2, c - 1:c + 2]
        if ld[r, c] == w.min() and ld[r, c] < np.median(ld) - 2:
            cand.append(GX[r, c] + 1j * GY[r, c])
eps_found = []
h = 1e-7
for t0 in cand:
    t = complex(t0)
    okc = True
    for _ in range(60):
        d0 = Dval(t)[0]
        dp = (Dval(t + h)[0] - Dval(t - h)[0]) / (2 * h)
        if dp == 0:
            okc = False; break
        step = d0 / dp
        t = t - step
        if abs(step) < 1e-13:
            break
    else:
        okc = False
    if not okc or not np.isfinite(t):
        continue
    if t.imag <= 0.02 or not (TA - 0.3 < t.real < TB + 0.3) or t.imag > IMTOP + 0.35:
        continue
    if any(abs(t - u) < 1e-6 for u in eps_found):
        continue
    lam = eigs_c(np.array([t]))[0]
    gap = np.min(np.abs(lam[:, None] - lam[None, :])[~np.eye(N, dtype=bool)])
    if gap < 1e-6:
        eps_found.append(t)
eps_found = np.array(sorted(eps_found, key=lambda z: z.real))
print(f"exceptional points in window: {len(eps_found)}")

# ---------------- verify: monodromy is a transposition ---------------------
def monodromy_perm(t0, rad, M=2400):
    th = np.linspace(0, 2 * np.pi, M, endpoint=True)
    loop = t0 + rad * np.exp(1j * th)
    lam = eigs_c(loop)
    cur = lam[0].copy()
    order = np.arange(N)
    for k in range(1, M):
        nxt = lam[k]
        # greedy matching
        used = np.zeros(N, bool)
        newo = np.empty(N, int)
        for i in range(N):
            d = np.abs(nxt - cur[i])
            d[used] = np.inf
            j = int(np.argmin(d))
            newo[i] = j; used[j] = True
        cur = nxt[newo]
    # final permutation: match loop-end back to loop-start
    start = lam[0]
    perm = np.empty(N, int)
    used = np.zeros(N, bool)
    for i in range(N):
        d = np.abs(start - cur[i])
        d[used] = np.inf
        j = int(np.argmin(d)); perm[i] = j; used[j] = True
    return perm

ver = 0
nchk = min(8, len(eps_found))
for t0 in eps_found[:nchk]:
    others = eps_found[np.abs(eps_found - t0) > 1e-9]
    dmin = np.min(np.abs(others - t0)) if len(others) else 1.0
    dmin = min(dmin, np.min(np.abs(np.conj(others) - t0)) if len(others) else 1.0, 2 * t0.imag)
    rad = min(0.30 * dmin, 0.06)
    perm = monodromy_perm(complex(t0), rad)
    moved = np.sum(perm != np.arange(N))
    ver += (moved == 2)
print(f"monodromy check: {ver}/{nchk} EPs give a clean transposition")

# ---------------- real road: eigenvalue flow -------------------------------
ts = np.linspace(TA, TB, S)
Ms = A[None] + ts[:, None, None] * Bm[None]
lam_r = np.linalg.eigvalsh(Ms)          # (S, N) sorted
lo, hi = lam_r.min(), lam_r.max()
pad = 0.10 * (hi - lo)
lo -= pad; hi += pad

# pair hues: ramp across N-1 adjacent gaps  (cyan -> gold -> rose)
PSTOP = np.array([
    [0.35, 0.80, 0.95],
    [0.55, 0.88, 0.72],
    [1.00, 0.80, 0.35],
    [1.00, 0.55, 0.35],
    [0.95, 0.40, 0.55],
])
def pair_col(k):
    u = k / max(N - 2, 1)
    t = u * (len(PSTOP) - 1)
    i = min(int(t), len(PSTOP) - 2)
    return PSTOP[i] + (t - i) * (PSTOP[i + 1] - PSTOP[i])

# associate each EP with the colliding pair index (nearest-gap at Re t)
ep_pair = []
for t0 in eps_found:
    col = int(np.clip(round((t0.real - TA) / (TB - TA) * (S - 1)), 0, S - 1))
    gaps = np.diff(lam_r[col])
    ep_pair.append(int(np.argmin(gaps)))

# low stars should sit above their avoided crossing: verify
nver = 0
for t0, k in zip(eps_found, ep_pair):
    if t0.imag < 0.25:
        gaps = np.diff(lam_r, axis=1)[:, k]
        wsel = np.abs(ts - t0.real) < 0.35
        tmin = ts[wsel][np.argmin(gaps[wsel])]
        nver += (abs(tmin - t0.real) < 0.08)
nlow = sum(1 for t0 in eps_found if t0.imag < 0.25)
print(f"road check: {nver}/{nlow} low stars sit above their avoided crossing")

# ---------------- render ---------------------------------------------------
img = np.zeros((S, S, 3), np.float32)

# ---- sky: log|D| = sum log|t-t_k|^2 + smooth remainder (coarse+upsampled)
sky_re = np.linspace(TA, TB, S)
sky_im = np.linspace(IMTOP, 0.0, SKY_H)      # top row = high Im
csize = (SKY_H // 8, S // 8)
cgx = np.linspace(TA, TB, csize[1])
cgy = np.linspace(IMTOP, 0.0, csize[0])
CX, CY = np.meshgrid(cgx, cgy)
ct = (CX + 1j * np.maximum(CY, 0.012)).ravel()
cl = Dlog(ct).reshape(csize)
# subtract known-star singular part
sing_c = np.zeros(csize)
for t0 in eps_found:
    sing_c += 2 * np.log(np.abs(CX + 1j * CY - t0) + 1e-12)
    sing_c += 2 * np.log(np.abs(CX + 1j * CY - np.conj(t0)) + 1e-12)  # mirror
rem = cl - sing_c
remf = ndzoom(rem, (SKY_H / csize[0], S / csize[1]), order=3)[:SKY_H, :S]
SXX, SYY = np.meshgrid(sky_re, sky_im)
sing_f = np.zeros((SKY_H, S))
for t0 in eps_found:
    sing_f += 2 * np.log(np.abs(SXX + 1j * SYY - t0) + 1e-12)
    sing_f += 2 * np.log(np.abs(SXX + 1j * SYY - np.conj(t0)) + 1e-12)
U = remf + sing_f

# quantile contour rings, brightness rising toward stars
flat = np.sort(U.ravel())
ecdf = np.searchsorted(flat, U) / U.size
NLEV = 56
lev = ecdf * NLEV
gyv, gxv = np.gradient(lev)
gmag = np.hypot(gyv, gxv) + 1e-9
ldist = np.abs(((lev + 0.5) % 1.0) - 0.5) / gmag
ring = np.exp(-(ldist / (1.0 * rs)) ** 2)
crowd = 1.0 / (1.0 + (gmag * 6) ** 1.4)
depth = 1 - ecdf                        # deep = near stars
stard = np.full((SKY_H, S), np.inf)
for t0 in eps_found:
    px = (t0.real - TA) / (TB - TA) * (S - 1)
    py = (IMTOP - t0.imag) / IMTOP * (SKY_H - 1)
    stard = np.minimum(stard, np.hypot((np.arange(SKY_H)[:, None] - py),
                                       (np.arange(S)[None, :] - px)))
gate = np.exp(-(stard / (S * 0.075)) ** 2)
ringcol = (0.32 * ring * crowd * (0.03 + 0.97 * gate) * (0.25 + 0.75 * depth ** 1.4))
skycol = np.zeros((SKY_H, S, 3), np.float32)
skycol += ringcol[..., None] * np.array([0.45, 0.55, 0.85])[None, None, :]
# violet haze by depth
skycol += (0.045 * depth ** 2.2)[..., None] * np.array([0.45, 0.30, 0.75])[None, None, :]

# stars: additive gaussian splats colored by pair hue
yy = np.arange(SKY_H)[:, None]
xx = np.arange(S)[None, :]
for t0, k in zip(eps_found, ep_pair):
    px = (t0.real - TA) / (TB - TA) * (S - 1)
    py = (IMTOP - t0.imag) / IMTOP * (SKY_H - 1)
    if not (0 <= py < SKY_H):
        continue
    r2 = (yy - py) ** 2 + (xx - px) ** 2
    core = np.exp(-r2 / (2 * (2.6 * rs) ** 2))
    halo = np.exp(-r2 / (2 * (11 * rs) ** 2))
    c = pair_col(k)
    skycol += 1.7 * core[..., None] * (0.30 + 0.70 * c)[None, None, :]
    skycol += 0.55 * halo[..., None] * c[None, None, :]
    # plumb line: faint luminous column to the road
    colmask = np.exp(-((xx - px) / (1.7 * rs)) ** 2)
    below = (yy > py)
    fade = np.exp(-(yy - py) / (SKY_H * 0.55)) * below
    pull = np.exp(-t0.imag / 0.45)
    skycol += (0.05 + 0.14 * pull) * (colmask * fade)[..., None] * c[None, None, :]

img[:SKY_H] = skycol

# ---- the seam: the real axis
seam_y = SKY_H
sy = np.arange(S)[:, None]
seam = np.exp(-((np.arange(S)[:, None] * 0 + np.arange(S)[None, :] * 0)) )  # placeholder
seamrow = np.exp(-((np.arange(S) - 0) * 0))
# draw as a horizontal glow band
yy_full = np.arange(S)[:, None]
seam_glow = np.exp(-((yy_full - seam_y) / (1.5 * rs)) ** 2)
img += 0.30 * seam_glow[..., None] * np.array([0.70, 0.78, 0.95])[None, None, :]

# ---- road band: eigenvalue threads
band = np.zeros((BAND_H, S, 3), np.float32)
rows = (hi - lam_r) / (hi - lo) * (BAND_H - 1)     # (S cols, N)
r0 = np.floor(rows).astype(int)
fr = rows - r0
cols = np.arange(S)
THREAD = np.array([0.62, 0.72, 0.88])
for i in range(N):
    tc = 0.78 * THREAD + 0.22 * pair_col(min(i, N - 2))
    for dy, wgt in ((0, 1 - fr[:, i]), (1, fr[:, i])):
        rr = np.clip(r0[:, i] + dy, 0, BAND_H - 1)
        np.add.at(band[..., 0], (rr, cols), 0.85 * wgt * tc[0])
        np.add.at(band[..., 1], (rr, cols), 0.85 * wgt * tc[1])
        np.add.at(band[..., 2], (rr, cols), 0.85 * wgt * tc[2])
# thicken threads
band = np.stack([gaussian_filter(band[..., i], (1.1 * rs, 0.4 * rs)) for i in range(3)], -1) * 2.6 * max(1.0, rs)
# near-miss glow per adjacent pair
gaps = np.diff(lam_r, axis=1)                       # (S, N-1)
gscale = np.percentile(gaps, 4)
yyb = np.arange(BAND_H)[:, None]
tintb = np.zeros_like(band)
for k in range(N - 1):
    amp = np.exp(-(gaps[:, k] / (2.5 * gscale)) ** 2)
    if amp.max() < 0.05:
        continue
    mids = (hi - 0.5 * (lam_r[:, k] + lam_r[:, k + 1])) / (hi - lo) * (BAND_H - 1)
    c = pair_col(k)
    sel = amp > 0.03
    idx = np.where(sel)[0]
    if len(idx) == 0:
        continue
    # tint the two participating threads + a tight kiss-glow at the miss
    for row_set in (k, k + 1):
        rrow = (hi - lam_r[:, row_set]) / (hi - lo) * (BAND_H - 1)
        rr0 = np.floor(rrow).astype(int)
        frr = rrow - rr0
        for dy, wgt in ((0, 1 - frr), (1, frr)):
            rrc = np.clip(rr0 + dy, 0, BAND_H - 1)
            for ch in range(3):
                np.add.at(tintb[..., ch], (rrc, cols), 1.6 * amp * wgt * c[ch])
    sig = 4.0 * rs
    hw = int(5 * sig)
    for ci in idx[::max(1, len(idx) // 300)]:
        yc = int(round(mids[ci]))
        y0, y1 = max(0, yc - hw), min(BAND_H, yc + hw)
        x0, x1 = max(0, ci - hw), min(S, ci + hw)
        r2 = ((np.arange(y0, y1)[:, None] - mids[ci]) ** 2
              + (np.arange(x0, x1)[None, :] - ci) ** 2)
        band[y0:y1, x0:x1] += (0.034 * amp[ci] ** 2 * np.exp(-r2 / (2 * sig ** 2)))[..., None] * c[None, None, :]

tintb = np.stack([gaussian_filter(tintb[..., i], (1.0 * rs, 0.5 * rs)) for i in range(3)], -1) * 2.4 * max(1.0, rs)
band += tintb
img[SKY_H:] = img[SKY_H:] + band

# ---------------- post -----------------------------------------------------
lum = img @ np.array([0.3, 0.55, 0.15])
mask = np.clip((lum - 0.55) / 1.1, 0, 1)[..., None] * img
b1 = np.stack([gaussian_filter(mask[..., i], 2.2 * rs) for i in range(3)], -1)
ds = 8
small = mask[::ds, ::ds]
b2 = np.stack([gaussian_filter(small[..., i], 34 * rs / ds) for i in range(3)], -1)
b2 = ndzoom(b2, (ds, ds, 1), order=1)[:S, :S]
out = img + 1.1 * b1 + 0.6 * b2
out = 1 - np.exp(-1.45 * out)
out = np.clip(out, 0, 1) ** (1 / 1.3)
pil = Image.fromarray((out * 255).astype(np.uint8))
pil = pil.resize((SIZE, SIZE), Image.LANCZOS)
pil.save(OUT)
print("saved", OUT)
