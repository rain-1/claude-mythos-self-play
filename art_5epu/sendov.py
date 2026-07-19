"""COMPANION B — 'The Razor's Edge'  (Sendov, the metric lens).

Sendov's conjecture: if every zero of p lies in |z|<=1, then every zero has a
critical point within distance 1. The bound is TIGHT only at the extremal
p = z^n - 1: its n roots are the n-th roots of unity, and p' = n z^{n-1} sends
ALL n-1 critical points to the origin -- so every root is EXACTLY distance 1 from
the critical pile. We draw that equality case:
  * the covering: a unit disk D(root,1) around each root -- for the extremal all
    n disks pass through the origin, so their overlap (a flower-of-life rose)
    peaks at the centre where the critical pile sits (glowing covering-depth);
  * the n leashes = n radii, each of length EXACTLY 1 (angle-lit);
  * the collapsed critical pile blazing at the origin;
and, in ghost, the RAZOR'S EDGE: perturb the roots by a hair and the perfect
collapse shatters -- the n-1 critical points fly apart to the rim (cyan sparks),
the leashes slacken. The equality is a knife-edge in configuration space.

Run:  python3 sendov.py [FINAL]
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import tonemap, fast_bloom, splat, line_splat, downscale, lerp_ramp, fatten

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 640
SS = 2
S = FINAL * SS
R = 2.15
rs = FINAL / 640.0
PXU = S/(2*R)

def w2p(z):
    z = np.atleast_1d(z)
    return np.stack([(z.real + R)/(2*R)*S, (R - z.imag)/(2*R)*S], -1)

def circle_pts(c, rad):
    m = max(64, int(2*np.pi*rad*PXU))
    t = np.linspace(0, 2*np.pi, m)
    return c + rad*np.exp(1j*t)

GOLD = np.array([0.96, 0.76, 0.38], np.float32)
CYAN = np.array([0.52, 0.92, 1.0],  np.float32)

n = 13
roots = np.exp(2j*np.pi*np.arange(n)/n)     # extremal: p = z^n - 1
# critical pile: p' = n z^{n-1} -> all crit at 0 (verify via direct coeffs)
pcoef = np.zeros(n+1); pcoef[0] = 1.0; pcoef[-1] = -1.0
crit_exact = np.roots(np.polyder(pcoef))
assert np.abs(crit_exact).max() < 1e-9, "extremal crit not at origin"
leash = 1.0   # every root is exactly distance 1 from the origin pile

buf = np.zeros((S, S, 3), np.float32)

# ---- (1) covering-depth glow: how many unit disks D(root,1) cover each pixel
xs = np.linspace(-R, R, S, dtype=np.float32); ys = np.linspace(R, -R, S, dtype=np.float32)
X, Y = np.meshgrid(xs, ys)
depth = np.zeros((S, S), np.float32)
for z0 in roots:
    depth += ((X - z0.real)**2 + (Y - z0.imag)**2 <= 1.0).astype(np.float32)
gd = (depth / n) ** 2.2                     # steep -> only the deep-overlap core glows
buf += GOLD * (gd * 0.52)[..., None]
del depth, gd, X, Y

ink = np.zeros((S, S, 3), np.float32)       # thin strokes -> fattened later

# ---- (2) flower-of-life rose: the unit circles themselves (the covering) ----
for k in range(n):
    splat(ink, w2p(circle_pts(roots[k], 1.0)), GOLD*0.95, 0.30, S)

# ---- (3) unit disk boundary (where the roots live) + outer envelope r=2 -----
splat(ink, w2p(circle_pts(0, 1.0)), np.array([0.48, 0.58, 0.72], np.float32), 0.20, S)
splat(ink, w2p(circle_pts(0, 2.0)), np.array([0.34, 0.40, 0.54], np.float32), 0.09, S)

# ---- (4) the n leashes = n radii of length exactly 1 -----------------------
for k in range(n):
    line_splat(ink, w2p(roots[k])[0], w2p(0)[0], GOLD*0.75, 0.30, S)

# ---- (5) RAZOR'S EDGE: track the n-1 critical points shattering outward -----
# a fixed asymmetric perturbation direction; grow its amplitude t: 0 -> 1.
rng = np.random.default_rng(5)
dth = rng.normal(0, 1.0, n); dth -= dth.mean()          # asymmetric angular kick
NT = 240
tt = np.linspace(0, 1, NT)
prev = None
tracks = [[] for _ in range(n-1)]
for t in tt:
    pert = roots * np.exp(1j * (0.22 * t) * dth)
    cp = np.roots(np.polyder(np.poly(pert)))
    if prev is None:
        order = np.argsort(np.angle(cp + 1e-9))
        cp = cp[order]
    else:                                                # nearest-neighbour match
        used = np.zeros(len(cp), bool); newcp = np.empty(n-1, complex)
        for i in range(n-1):
            d = np.abs(cp - prev[i]); d[used] = 1e9
            j = d.argmin(); used[j] = True; newcp[i] = cp[j]
        cp = newcp
    prev = cp
    for i in range(n-1):
        tracks[i].append(cp[i])

shat = np.zeros((S, S, 3), np.float32)       # shatter trajectory strokes (fattened)
fl = np.zeros((S, S, 3), np.float32)         # blazing point-sources (pile + sparks)
for i in range(n-1):
    P = w2p(np.array(tracks[i]))
    for k in range(len(P)-1):
        a = k/(len(P)-1)                                 # brighten toward the rim
        line_splat(shat, P[k], P[k+1], CYAN*(0.5+0.5*a), 0.24 + 0.28*a, S)
    splat(fl, P[-1][None, :], (0.55, 0.95, 1.0), 30.0*SS*rs, S)   # landing spark

# ---- (6) roots on the rim + the blazing central critical pile --------------
splat(fl, w2p(roots), (0.95, 0.86, 0.62), 26.0*SS*rs, S)
splat(fl, w2p(np.array([0.0+0j])), (0.55, 0.97, 1.0), 150.0*SS*rs, S)

# fatten thin strokes so they survive the downscale; blaze the point-sources
buf += fatten(ink, 1.0*SS*rs) + fatten(shat, 0.9*SS*rs)
buf += fl*1.4 + fast_bloom(fl, 3*SS*rs)*1.05 + fast_bloom(fl, 13*SS*rs)*0.55

# ---- bloom + tone ----------------------------------------------------------
bloom = fast_bloom(buf, 5*SS*rs)*0.45 + fast_bloom(buf, 18*SS*rs)*0.3
out = downscale(tonemap(buf + bloom, k=1.5, gamma=0.86), SS)
name = "variants/sendov_v1.png" if FINAL <= 800 else "sendov.png"
out.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), name))
print("saved", name, out.size,
      f"| extremal z^{n}-1: every leash={leash:.1f} exactly; "
      f"shatter endpoint max|crit|={max(abs(tr[-1]) for tr in tracks):.3f}")
