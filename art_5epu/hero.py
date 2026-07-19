"""HERO — 'The Trinity of Saddles'  (electrostatic / Morse lens on p' = 0).

For a polynomial p with all zeros in the unit disk, the equipotential net
U(z) = log|p(z)| encodes where p'=0: the level sets |p|=r are Cassini
lemniscates that PINCH into figure-eights exactly at the critical points (zeros
of p'). Each critical point is a saddle of U -- the place the level-set topology
changes. Here the zeros clump into THREE clusters; the striking critical points
are the ones stranded in the GAPS between clusters (the far-from-any-root
saddles -- the dramatic end of the Sendov/Gauss-Lucas story), which chain into a
Y-shaped watershed with a lone saddle at the barycentre.

Layers:
  * equipotential net, graded deep-indigo(valleys) -> warm-gold(high ground);
  * SEPARATRIX contours (level sets through each critical value) in cyan, the
    watershed skeleton that self-crosses at every saddle, super-lit at the joints;
  * critical points as cyan stars, roots as hot cores; faint Morse-basin tint.

Verified per-render: all zeros in |z|<=1; Gauss-Lucas (crit in convex hull);
Sendov (every root within 1 of a critical point).

Run:  python3 hero.py [FINAL]     FINAL = final px size (default 560 proto; 4096 final)
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import tonemap, fast_bloom, splat, downscale
from scipy.spatial import ConvexHull

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 560
SS = 2
S = FINAL * SS
R = 1.28
rs = FINAL / 560.0          # resolution scale: keep line/point sizes a constant
                            # fraction of the frame so the proto predicts the final

# ---------------------------------------------------------------- polynomial
def build_zeros():
    rng = np.random.default_rng(1)
    specs = [(0.62, 0.55, 0.15, 8), (2.75, 0.70, 0.12, 8), (4.75, 0.50, 0.18, 7)]
    z = []
    for ang, rr, sp, k in specs:
        c = rr * np.exp(1j*ang)
        for _ in range(k):
            z.append(c + sp*(rng.normal() + 1j*rng.normal()))
    z = np.array(z)
    return z[np.abs(z) <= 0.99]

zeros = build_zeros()
n = len(zeros)
pc = np.poly(zeros)
crit = np.roots(np.polyder(pc))
critvals = np.log(np.abs(np.polyval(pc, crit)) + 1e-300).real

# ------- verify the theorems on THIS polynomial ----------------------------
assert np.all(np.abs(zeros) <= 1.0 + 1e-9)
pts = np.column_stack([zeros.real, zeros.imag]); hull = ConvexHull(pts)
def in_hull(c):
    return all(eq[0]*c.real + eq[1]*c.imag + eq[2] <= 1e-6 for eq in hull.equations)
gl = all(in_hull(c) for c in crit)
sendov = float(np.abs(zeros[:, None] - crit[None, :]).min(axis=1).max())
print(f"[hero] FINAL={FINAL} n={n} zeros, {len(crit)} crit | Gauss-Lucas={gl} "
      f"| Sendov max-leash={sendov:.4f} (<=1)")

def w2p(z):
    z = np.atleast_1d(z)
    return np.stack([(z.real + R)/(2*R)*S, (R - z.imag)/(2*R)*S], -1)

# ---------------------------------------------------------------- field grids
xs = np.linspace(-R, R, S, dtype=np.float32); ys = np.linspace(R, -R, S, dtype=np.float32)
X, Y = np.meshgrid(xs, ys)
U = np.zeros((S, S), np.float32)
for z0 in zeros:
    U += np.log(np.hypot(X - z0.real, Y - z0.imag) + 1e-9).astype(np.float32)
gy, gx = np.gradient(U); gmag = np.hypot(gx, gy) + 1e-9
del gx, gy
rad = np.hypot(X, Y)

buf = np.zeros((S, S, 3), np.float32)

# ---- (1) Morse-basin tint (nearest root), memory-safe running argmin -------
PAL = np.array([
    (0.95, 0.45, 0.28), (0.93, 0.72, 0.33), (0.55, 0.82, 0.55),
    (0.34, 0.66, 0.92), (0.62, 0.45, 0.92), (0.95, 0.38, 0.55),
    (0.40, 0.80, 0.78), (0.88, 0.60, 0.30),
], np.float32)
basin = np.zeros((S, S), np.int16)
bestd = np.full((S, S), 1e18, np.float32)
for i, z0 in enumerate(zeros):
    dd = (X - z0.real)**2 + (Y - z0.imag)**2
    m = dd < bestd
    bestd[m] = dd[m]; basin[m] = i
del bestd
tint = PAL[basin % len(PAL)]
env = np.exp(-(np.clip(U, None, U.max()) - (U.max()-3.0))**2 / 6.0)
env *= np.clip(1.0 - (rad - 0.6)/0.7, 0.0, 1.0)
buf += tint * (0.055 * env)[..., None]
del tint, env, basin

# ---- (2) equipotential net, graded by level -------------------------------
dU = 0.42
frac = np.abs((U/dU + 0.5) % 1.0 - 0.5)
contour = np.exp(-((frac*dU/gmag)/(0.9*SS*rs))**2)
lev = np.clip((U - (critvals.min()-1.5)) / (U.max() - critvals.min() + 1.5), 0, 1)
fade = np.clip(1.0 - (rad - 0.98)/0.30, 0.0, 1.0) + 0.06*np.exp(-((rad-1.05)/0.35)**2)
lowc  = np.array([0.18, 0.20, 0.42], np.float32)
highc = np.array([0.92, 0.74, 0.36], np.float32)
netcol = lowc*(1-lev[..., None]) + highc*lev[..., None]
buf += netcol * (contour*fade)[..., None] * 1.35
del contour, netcol, frac, lev

# ---- (3) separatrix contours through critical values, lit at the joints ----
near = np.zeros((S, S), np.float32)
for c in crit:
    near = np.maximum(near, np.exp(-((X-c.real)**2 + (Y-c.imag)**2)/(0.045**2)).astype(np.float32))
sep = np.zeros((S, S), np.float32)
for cv in critvals:
    sep = np.maximum(sep, np.exp(-((np.abs(U-cv)/gmag)/(1.0*SS*rs))**2).astype(np.float32))
sep *= fade
buf += np.array([0.50, 0.90, 1.0], np.float32) * (sep*(0.72 + 2.6*near))[..., None]
del sep, near, U, gmag, X, Y, rad, fade

# ---- (4) critical stars + roots -------------------------------------------
splat(buf, w2p(crit),  (0.65, 0.97, 1.0), 7.0*SS*rs, S)
splat(buf, w2p(zeros), (1.0, 0.90, 0.68), 9.0*SS*rs, S)

# ---- bloom + tone ----------------------------------------------------------
bloom = fast_bloom(buf, 7*SS*rs)*0.5 + fast_bloom(buf, 22*SS*rs)*0.35
img8 = tonemap(buf + bloom, k=1.45, gamma=0.86)
out = downscale(img8, SS)
name = "variants/hero_v1.png" if FINAL <= 700 else "hero.png"
out.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), name))
print("saved", name, out.size)
