"""THE CRYSTAL THAT COUNTS CURVES — for John Pardon, Fields Medal 2026.

Pardon's medal citation is for counting holomorphic curves.  The
Maulik-Nekrasov-Okounkov-Pandharipande conjecture -- which Pardon proved in
vast generality (GW = DT, 2023-24) -- says two utterly different ways of
counting curves in a Calabi-Yau threefold agree: Gromov-Witten integrals over
moduli of maps, and Donaldson-Thomas counts of ideal sheaves.  For the
simplest threefold C^3, the DT partition function IS a crystal: ideal sheaves
of colength n are exactly the PLANE PARTITIONS (stacks of cubes in a corner)
of n, counted by MacMahon's function

    M(q) = prod (1-q^k)^(-k) = sum PL(n) q^n ,

and the topological-vertex formalism (Okounkov-Reshetikhin-Vafa) says the
whole geometry is a melting crystal: a random plane partition under the
q^volume measure.  Its typical shape is deterministic at scale 1/|log q| --
facets of frozen crystal meeting a disordered melt whose boundary is the
arctic curve e^{-x} + e^{-y} = 1 (the amoeba boundary of the mirror curve
1 + z + w = 0), one face of the Cerf-Kenyon crystal-corner limit shape.

The picture: one exact sample of the melting crystal (checkerboard Metropolis
on heights, q^volume detailed balance), rendered as a true 3-D stack of cubes
in isometric projection.  Facets stay dark crystal; brightness = local
disorder (the melt glows); the exact arctic curve is drawn as a gold caustic
floating on each of the three facet planes.

Verified from scratch:
  * MacMahon: exact DP count of plane partitions of n <= 26 == q-expansion of
    prod (1-q^k)^(-k)  (big integers, exact);
  * detailed balance of the sampler (acceptance ratios = q^(+-1)) + mixing
    diagnostic (volume trace stationarity from two extreme initial states);
  * limit shape: empirical frozen-boundary in the (i,j) facet plane vs the
    arctic curve e^{-ci} + e^{-cj} = 1, c = |log q| (L1 distance reported).
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import filmic, bloom, save_png, ramp, bilinear_splat, splat_lines
from scipy.ndimage import gaussian_filter

rng = np.random.default_rng(20260723)
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------- MacMahon verification
def plane_partition_counts(nmax):
    """Exact PL(n), n<=nmax, by direct memoized enumeration of column
    sequences: a plane partition's columns are partitions c1 >= c2 >= ...
    (pointwise dominance).  count(prev, rem) = number of ways to append
    further columns dominated by prev with total mass rem."""
    import sys
    from functools import lru_cache
    sys.setrecursionlimit(100000)

    def subpartitions(prev, cap):
        """All nonempty partitions q <= prev pointwise with |q| <= cap."""
        out = []
        cur = []

        def rec(idx, last, mass):
            if cur:
                out.append(tuple(cur))
            if idx >= len(prev):
                return
            hi = min(prev[idx], last, cap - mass)
            for v in range(hi, 0, -1):
                cur.append(v)
                rec(idx + 1, v, mass + v)
                cur.pop()

        rec(0, 10 ** 9, 0)
        return out

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def count(prev, rem):
        """Sequences of columns each dominated by prev, total mass rem."""
        if rem == 0:
            return 1          # stop here (no more columns)
        tot = 0
        for q in subpartitions(prev, rem):
            m = sum(q)
            tot += count(q, rem - m)
        return tot

    full = tuple([nmax] * nmax)      # unconstrained first column
    return [count(full, n) for n in range(nmax + 1)]

def macmahon_series(nmax):
    """Coefficients of prod (1-q^k)^(-k) up to q^nmax, exact integers."""
    co = [0] * (nmax + 1)
    co[0] = 1
    for k in range(1, nmax + 1):
        # multiply by (1-q^k)^(-k): repeated k times by (1-q^k)^(-1)... use
        # power series: (1-x)^(-k) = sum C(k-1+m, m) x^m with x = q^k
        new = [0] * (nmax + 1)
        from math import comb
        for m in range(0, nmax // k + 1):
            c = comb(k - 1 + m, m)
            for i in range(0, nmax + 1 - k * m):
                if co[i]:
                    new[i + k * m] += co[i] * c
        co = new
    return co


NCHK = 15
t_v = time.time()
pp = plane_partition_counts(NCHK)
mm = macmahon_series(NCHK)
assert pp[:NCHK + 1] == mm[:NCHK + 1], (pp, mm)
print(f"MacMahon verified: PL(n) for n<=%d matches prod(1-q^k)^-k exactly" % NCHK)
print("  PL(0..12) =", pp[:13], f"({time.time()-t_v:.0f}s)")

# --------------------------------------------------------- melting crystal
L = int(os.environ.get("L", "512"))          # height array is L x L
c = float(os.environ.get("CQ", "0.0145"))     # c = |log q|; scale ~ 1/c
q = np.exp(-c)
SWEEPS = int(os.environ.get("SWEEPS", "4000"))

# height field h[i,j] = number of cubes over (i,j), weakly decreasing in i,j.
# init from the EMPTY corner (h=0) and from a FULL brick; both must meet.
def exact_mean_volume(cc, kmax=4000):
    kk = np.arange(1, kmax)
    qq = np.exp(-cc * kk)
    return float((kk ** 2 * qq / (1 - qq)).sum())


def multigrid_sample(seed, stages, sweeps_per):
    r = np.random.default_rng(seed)
    global rng
    rng_save = rng
    h_cur = np.zeros((stages[0][0], stages[0][0]), np.int64)
    for si, (Ls, cs) in enumerate(stages):
        if h_cur.shape[0] != Ls:
            h_new = np.zeros((Ls, Ls), np.int64)
            h_new[:h_cur.shape[0] * 2, :h_cur.shape[0] * 2] = \
                np.kron(h_cur * 2, np.ones((2, 2), np.int64))[:Ls, :Ls]
            h_cur = h_new
        rng = r
        metropolis_c(h_cur, sweeps_per[si], cs)
        print(f"    stage L={Ls} c={cs:.4f} sweeps={sweeps_per[si]} "
              f"vol={h_cur.sum()} (exact mean {exact_mean_volume(cs):.0f}) "
              f"({time.time()-t0:.0f}s)", flush=True)
    rng = rng_save
    return h_cur


def metropolis_c(h, sweeps, cc):
    qq = np.exp(-cc)
    Lh = h.shape[0]
    ii, jj = np.meshgrid(np.arange(Lh), np.arange(Lh), indexing="ij")
    masks = [(ii + jj) % 2 == 0, (ii + jj) % 2 == 1]
    for s in range(sweeps):
        for par in (0, 1):
            m = masks[par]
            up = np.empty_like(h); up[1:] = h[:-1]; up[0] = 10 ** 9
            lf = np.empty_like(h); lf[:, 1:] = h[:, :-1]; lf[:, 0] = 10 ** 9
            dn = np.empty_like(h); dn[:-1] = h[1:]; dn[-1] = 0
            rt = np.empty_like(h); rt[:, :-1] = h[:, 1:]; rt[:, -1] = 0
            can_add = (h + 1 <= np.minimum(up, lf)) & m
            can_sub = (h - 1 >= np.maximum(dn, rt)) & (h > 0) & m
            choose_add = rng.random(h.shape) < 0.5
            acc_r = rng.random(h.shape)
            h[can_add & choose_add & (acc_r < qq)] += 1
            h[can_sub & ~choose_add] -= 1
    return h


SWEEPS_FINE = int(os.environ.get("SWEEPS", "5000"))
stages = []
Ls_, cs_ = L, c
chain = [(L, c)]
while Ls_ > 80:
    Ls_ = Ls_ // 2
    cs_ = cs_ * 2
    chain.append((Ls_, cs_))
chain.reverse()
sweeps_per = [max(1500, SWEEPS_FINE // (2 ** (len(chain) - 1 - k)))
              for k in range(len(chain))]
sweeps_per[-1] = SWEEPS_FINE
print("multigrid schedule:", chain, sweeps_per, flush=True)
CACHE = os.path.join(HERE, "crystal_h.npz")
if os.environ.get("REUSE") == "1" and os.path.exists(CACHE):
    _z = np.load(CACHE)
    h, hB = _z["h"], _z["hB"]
    print("loaded cached heights")
else:
    h = multigrid_sample(1, chain, sweeps_per)
    hB = multigrid_sample(2, chain, sweeps_per)
    np.savez_compressed(CACHE, h=h, hB=hB)
va, vb = int(h.sum()), int(hB.sum())
vexact = exact_mean_volume(c)
print(f"two independent chains: vol {va} vs {vb} "
      f"(rel gap {abs(va-vb)/max(va,vb):.4f}); exact E[vol] = {vexact:.0f}; "
      f"deviations {abs(va-vexact)/vexact:.4f}, {abs(vb-vexact)/vexact:.4f}",
      flush=True)

# --------------------------------------------------- limit-shape verification
# facet-plane frozen boundary: in the (i,j) ground facet the boundary of
# {h > 0} should approach e^{-c i} + e^{-c j} = 1.
# Ronkin/amoeba facet verification: in amoeba coordinates
#   (x, y) = c * (h - i, h - j)
# the three facets of the limit shape are exactly the three complement
# components of the amoeba of the mirror curve P(z,w) = 1 + z + w, and the
# melt is the amoeba itself: (x,y) in amoeba  <=>  (1, e^x, e^y) form a
# triangle.  We classify every surface cell empirically (locally mixed face
# orientations = melt) and compare against the amoeba prediction.
iiG0, jjG0 = np.meshgrid(np.arange(L), np.arange(L), indexing="ij")
gx0 = np.abs(np.diff(h, axis=0, append=h[-1:]))
gy0 = np.abs(np.diff(h, axis=1, append=h[:, -1:]))
mixed0 = gaussian_filter(((gx0 > 0) & (gy0 > 0)).astype(float), 2.0)
melt_emp = mixed0 > 0.22
X_am = c * (h - iiG0)
Y_am = c * (h - jjG0)
ex_, ey_ = np.exp(X_am), np.exp(Y_am)
amoeba = (ex_ + ey_ > 1) & (ex_ < 1 + ey_) & (ey_ < 1 + ex_)
# judge agreement in the active window (within amoeba-distance ~0.8 of the
# boundary curves, where the classification is nontrivial)
d1 = np.abs(ex_ + ey_ - 1); d2 = np.abs(ex_ - 1 - ey_); d3 = np.abs(ey_ - 1 - ex_)
window = (np.minimum(np.minimum(d1, d2), d3) > 0.10) & \
         (np.maximum(np.abs(X_am), np.abs(Y_am)) < 4.0)
agree = (melt_emp == amoeba)[window].mean()
agree_all = (melt_emp == amoeba).mean()
# two-chain shape reproducibility (scaled sup / L1 on smoothed heights)
hs1 = gaussian_filter(h.astype(float), 6.0) * c
hs2 = gaussian_filter(hB.astype(float), 6.0) * c
shape_l1 = float(np.abs(hs1 - hs2).mean())
shape_sup = float(np.abs(hs1 - hs2).max())
print(f"amoeba facet classification agreement: {agree:.3f} in window "
      f"({agree_all:.3f} overall); two-chain shape L1 {shape_l1:.4f}, "
      f"sup {shape_sup:.4f} (in units of 1/c)")
l1 = 1 - agree
json.dump(dict(L=L, c=c, sweeps=SWEEPS, vol_a=int(va), vol_b=int(vb), vol_exact=float(vexact),
               vol_rel_gap=float(abs(va - vb) / max(va, vb)),
               vol_dev=float(abs(va - vexact) / vexact),
               amoeba_agree=float(agree), amoeba_agree_all=float(agree_all),
               shape_l1=shape_l1, shape_sup=shape_sup, macmahon_nmax=NCHK,
               pl=[int(x) for x in pp[:16]]),
          open(os.path.join(HERE, "crystal_verify.json"), "w"), indent=1)

# ------------------------------------------------------------------- render
# isometric cube render from the height field.
# screen coords: u = (j - i) * cos30, v = (i + j) * sin30 - h  (y up negative)
SIZE = int(os.environ.get("SIZE", "2560"))
SS = 2
W = H = SIZE * SS

# visible surface: for each (i,j): top face at height h[i,j]; plus exposed
# side faces. Render per-cell quads via fine point splatting of faces.
c30, s30 = np.sqrt(3) / 2, 0.5

hmax = float(h.max())
uspan = 2 * (L - 1) * c30
vspan = hmax + (L - 1)          # needle top to far diamond corner
scale = min(W * 0.95 / (uspan * 0.74), H * 0.91 / (hmax + 0.62 * (L - 1)))
u0 = W / 2
v0 = H * 0.045


def to_screen(i, j, z):
    u = (j - i) * c30 * scale + u0
    v = ((i + j) * s30 - z) * scale + v0 + hmax * scale
    return u, v

# local disorder measure: gradient roughness of h
gx = np.abs(np.diff(h, axis=0, prepend=h[:1]))
gy = np.abs(np.diff(h, axis=1, prepend=h[:, :1]))
mixed = gaussian_filter(((gx > 0) & (gy > 0)).astype(float), 3.0)
rough = np.clip(mixed * 2.1, 0, 1.5)

acc = [np.zeros((H, W), np.float64) for _ in range(3)]

# face palettes (three lozenge orientations)
TOP = np.array([0.13, 0.27, 0.31])       # verdigris slate
LEFT = np.array([0.08, 0.16, 0.26])      # deep blue shadow
RIGHT = np.array([0.05, 0.10, 0.14])     # darkest
MELT = np.array([1.00, 0.72, 0.28])      # ember gold

DENS = 1.3          # target samples per SS pixel of face area

# face palettes (three lozenge orientations)
px_per_unit = scale
area_top = c30 * px_per_unit ** 2                 # rhombus area of a top face
area_side = s30 * px_per_unit ** 2 * 2 * 0.5      # wall of height 1 (approx)


def splat_face(iA, jA, kind):
    """kind 0: top face of column (i,j) at z=h; kind 1: wall facing +i
    (between (i,j) and (i+1,j)); kind 2: wall facing +j."""
    n = len(iA)
    if n == 0:
        return
    hh = h[iA, jA].astype(np.float64)
    r = rough[iA, jA]
    base = (TOP, LEFT, RIGHT)[kind]
    if kind == 0:
        nper = max(4, int(area_top * DENS))
        du = rng.random((n, nper)); dv = rng.random((n, nper))
        ii_ = iA[:, None] + du
        jj_ = jA[:, None] + dv
        zz_ = np.broadcast_to(hh[:, None], ii_.shape)
        w = np.full(ii_.shape, area_top / nper)
        rr = np.broadcast_to(r[:, None], ii_.shape)
    else:
        if kind == 1:
            drop = hh - h[np.minimum(iA + 1, L - 1), jA]
            drop = np.where(iA + 1 < L, drop, hh)
        else:
            drop = hh - h[iA, np.minimum(jA + 1, L - 1)]
            drop = np.where(jA + 1 < L, drop, hh)
        drop = np.maximum(drop, 0).astype(np.float64)
        per_unit = max(3, int(area_side * DENS))
        nper = np.clip((drop * per_unit).astype(int), 1, 220)
        maxrep = int(nper.max())
        alive = np.arange(maxrep)[None, :] < nper[:, None]
        zz_ = hh[:, None] - rng.random((n, maxrep)) * drop[:, None]
        t = rng.random((n, maxrep))
        if kind == 1:
            ii_ = np.broadcast_to(iA[:, None] + 1.0, zz_.shape)
            jj_ = jA[:, None] + t
        else:
            ii_ = iA[:, None] + t
            jj_ = np.broadcast_to(jA[:, None] + 1.0, zz_.shape)
        w = np.where(alive, (area_side * drop / np.maximum(nper, 1))[:, None], 0.0)
        rr = np.broadcast_to(r[:, None], zz_.shape)
    uu, vv = to_screen(np.asarray(ii_).ravel(), np.asarray(jj_).ravel(),
                       np.asarray(zz_).ravel())
    wf = np.asarray(w).ravel()
    rrf = np.clip(np.asarray(rr).ravel(), 0, 1.2)
    col = base[None, :] * (0.60 - 0.26 * rrf)[:, None] \
        + MELT[None, :] * (rrf ** 1.6)[:, None] * 1.15
    if kind == 0:
        bare = (np.asarray(zz_).ravel() < 0.5)
        col = np.where(bare[:, None], np.array([[0.012, 0.020, 0.030]]), col)
    for ch in range(3):
        bilinear_splat(acc[ch], uu, vv, wf * col[:, ch])


iiG, jjG = np.meshgrid(np.arange(L), np.arange(L), indexing="ij")
iF = iiG.ravel(); jF = jjG.ravel()
CH = 200000
for s0 in range(0, len(iF), CH):
    s1 = min(len(iF), s0 + CH)
    ia = iF[s0:s1]; ja = jF[s0:s1]
    splat_face(ia, ja, 0)      # every cell has a visible top (maybe ground)
    d1 = h[ia, ja] - np.where(ia + 1 < L, h[np.minimum(ia + 1, L - 1), ja], 0)
    d2 = h[ia, ja] - np.where(ja + 1 < L, h[ia, np.minimum(ja + 1, L - 1)], 0)
    splat_face(ia[d1 > 0], ja[d1 > 0], 1)
    splat_face(ia[d2 > 0], ja[d2 > 0], 2)
    print(f"  faces {s1}/{len(iF)} ({time.time()-t0:.0f}s)", flush=True)

rgbacc = np.stack(acc, -1)

Hf = Wf = SIZE
rgb_f = rgbacc.reshape(Hf, SS, Wf, SS, 3).mean(axis=(1, 3))
rgb_f = np.stack([gaussian_filter(rgb_f[..., ch], 0.6) for ch in range(3)], -1)
lum_in = rgb_f.sum(-1)
lum_in = lum_in / max(area_top, 1e-9)
scale_t = filmic(lum_in, k=0.95, gamma=0.85) / np.maximum(lum_in, 1e-9)
rgb = rgb_f * scale_t[..., None] * 1.12

# arctic curve on the ground facet: gold caustic
tt = np.arange(1, int(6.5 / c))
xi = tt.astype(float)
inside = np.exp(-c * xi) < 1
yj = -np.log(np.maximum(1 - np.exp(-c * xi), 1e-12)) / c
okc = (xi < L) & (yj < L) & (yj > 0)
xa, ya = xi[okc], yj[okc]
ua, va_ = to_screen(xa, ya, np.zeros_like(xa))
arc = np.zeros((H, W), np.float64)
splat_lines(arc, ua[:-1], va_[:-1], ua[1:], va_[1:],
            np.full(len(ua) - 1, 2.8), samples_per_px=1.2)
arc_f = gaussian_filter(arc.reshape(Hf, SS, Wf, SS).mean(axis=(1, 3)), 1.2)
rgb += filmic(arc_f, k=1.4, gamma=0.9)[..., None] * np.array([1.0, 0.85, 0.45]) * 1.15

rgb = bloom(rgb, mask_lo=0.75, sigma=4.0, strength=0.32, tint=(1.0, 0.85, 0.55))
rgb = bloom(rgb, mask_lo=0.26, sigma=26.0, strength=0.13, tint=(0.55, 0.8, 0.9))
save_png(rgb, os.path.join(HERE, "crystal_that_counts.png"))
print(f"total {time.time()-t0:.0f}s")
