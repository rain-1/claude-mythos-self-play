"""PANEL 2 -- Three Pasts, One Present.
The real plane through the three collision points P0,P1,P2 of the Alpoge map
(isometric chart: e1=(2,-3,0)/sqrt13, e2=(0,0,1), origin P0).
Field U = log |F(p) - q*|^2: three wells at the exact fiber over q*.
Rivers = gradient descent of U (the waters of the present draining into
its three pasts); cyan separatrix contours pass through the saddles.
Mirror symmetry u -> -u is exact: F o sigma = (a,-b,-c), |F-q*| invariant."""
import numpy as np, kit
from scipy.ndimage import gaussian_filter
import sys

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = 2
S = FINAL * SS
rs = FINAL / 1024.0
H = W = S

S13 = np.sqrt(13.0)
u0, u1 = -3.4, 3.4
v0, v1 = -2.0, 8.8

def Fq(u, v):
    """|F(p)-q*|^2 for p = P0 + u*e1 + v*e2 (isometric)."""
    x = 2.0 * u / S13
    y = -3.0 * u / S13
    z = -0.25 + v
    w = 1 + x * y
    a = w ** 3 * z + y * y * w * (4 + 3 * x * y)
    b = y + 3 * x * w ** 2 * z + 3 * x * y * y * (4 + 3 * x * y)
    c = 2 * x - 3 * x * x * y - x ** 3 * z
    return (a + 0.25) ** 2 + b * b + c * c

uu = np.linspace(u0, u1, W)[None, :] * np.ones((H, 1))
vv = np.linspace(v1, v0, H)[:, None] * np.ones((1, W))
g = Fq(uu, vv)
U = np.log(g + 1e-18)

# wells in chart coords
WELLS = [(0.0, 0.0), (S13 / 2, 6.75), (-S13 / 2, 6.75)]

# ---- saddles: refine grid minima of |grad U| away from wells ----
gy, gx = np.gradient(U, (v0 - v1) / (H - 1), (u1 - u0) / (W - 1))
gn = gx * gx + gy * gy
mask = np.ones_like(U, bool)
for (wu, wv) in WELLS:
    mask &= ((uu - wu) ** 2 + (vv - wv) ** 2) > 0.16
cand = np.where(mask & (gn < np.percentile(gn[mask], 0.02)))
pts = np.stack([uu[cand], vv[cand]], -1)
# cluster candidates
sad = []
for p in pts:
    if not any((p[0]-q[0])**2 + (p[1]-q[1])**2 < 0.25 for q in sad):
        sad.append(list(p))
# Newton refine on grad U = 0 via finite differences
def gradU(u, v, h=1e-5):
    return np.array([(np.log(Fq(u+h,v))-np.log(Fq(u-h,v)))/(2*h),
                     (np.log(Fq(u,v+h))-np.log(Fq(u,v-h)))/(2*h)])
def hessU(u, v, h=1e-4):
    g0 = gradU(u, v)
    return np.stack([(gradU(u+h,v)-gradU(u-h,v))/(2*h),
                     (gradU(u,v+h)-gradU(u,v-h))/(2*h)], 1), g0
refined = []
for (su, sv) in sad:
    p = np.array([su, sv])
    for _ in range(30):
        Hm, g0 = hessU(*p)
        try:
            step = np.linalg.solve(Hm, -g0)
        except np.linalg.LinAlgError:
            break
        p = p + np.clip(step, -0.2, 0.2)
        if np.linalg.norm(step) < 1e-10:
            break
    if np.linalg.norm(gradU(*p)) < 1e-6 and u0 < p[0] < u1 and v0 < p[1] < v1:
        if not any((p[0]-q[0])**2+(p[1]-q[1])**2 < 1e-3 for q in refined):
            refined.append(list(p))
print("saddles:", [(round(p[0],5), round(p[1],5), round(float(np.log(Fq(*p))),5)) for p in refined])
sadlev = sorted(set(round(float(np.log(Fq(*p))), 6) for p in refined))

buf = np.zeros((H, W, 3), np.float32)

# 1. depth-glow base: valleys luminous, plateaus dark; tint by basin
qs = np.quantile(U, np.linspace(0.001, 0.999, 512))
lev = np.interp(U, qs, np.linspace(0, 1, 512))
warm = np.array([0.30, 0.175, 0.075])
depth = (1 - lev) ** 2.1
buf += warm * (0.12 + 1.0 * depth[..., None])

# 2. quantile-spaced equipotential rings (uniform cadence across anisotropy)
ring = kit.contour_ridge(lev, 0.031, 0.95 * SS * rs ** 0.5)
fade = 1 - np.clip((lev - 0.80) / 0.13, 0, 1)
fade = fade * fade * (3 - 2 * fade)
# ink budget: damp ring ink where contours crowd below ~5 px apart
gy2, gx2 = np.gradient(lev)
gpx = np.hypot(gx2, gy2)
crowd = 1.0 / (1.0 + (gpx / 0.031 * 5.0) ** 1.5)
ring = ring * fade * crowd
ringcol = kit.ramp(1 - lev, kit.DUSK)
buf += 0.50 * ring[..., None] * ringcol * (0.40 + 0.65 * (1 - lev[..., None]))

# 3. separatrix contours through each saddle level, lit by saddle proximity
sadglow = np.zeros((H, W), np.float32)
for L in sadlev:
    sep = kit.locus_glow(U - L, 1.3 * SS * rs ** 0.5)
    prox = np.zeros((H, W), np.float32)
    for (pu, pv) in refined:
        if abs(float(np.log(Fq(pu, pv))) - L) < 1e-4:
            prox += np.exp(-(((uu - pu) ** 2 + (vv - pv) ** 2)) / 1.8)
    sadglow += sep * (0.25 + 1.6 * prox)
buf += sadglow[..., None] * kit.CYAN * 0.8

# 4. rivers: gradient descent streamlines seeded on rim + uniform
rng = np.random.default_rng(7)
NRIV = int(2400 * rs)
seeds = []
# seed only inside the luminous basin (lev < 0.88): the void stays void
from scipy.interpolate import RegularGridInterpolator
lev_i = RegularGridInterpolator((np.linspace(v1, v0, H), np.linspace(u0, u1, W)), lev,
                                bounds_error=False, fill_value=1.0)
while len(seeds) < NRIV:
    cu = rng.uniform(u0, u1, 4 * NRIV)
    cv = rng.uniform(v0, v1, 4 * NRIV)
    ok = lev_i(np.stack([cv, cu], -1)) < 0.88
    for su, sv in zip(cu[ok], cv[ok]):
        seeds.append((su, sv))
        if len(seeds) >= NRIV:
            break
ink = np.zeros((H, W, 3), np.float32)
scale_u = W / (u1 - u0); scale_v = H / (v1 - v0)
DT = 0.020
for (su, sv) in seeds:
    p = np.array([su, sv]); path = [p.copy()]
    for _ in range(900):
        if min((p[0]-wu)**2+(p[1]-wv)**2 for (wu,wv) in WELLS) < 0.0016:
            break
        g0 = gradU(*p)
        n = np.linalg.norm(g0)
        if not np.isfinite(n):
            break
        step = -g0 / (n + 1e-9) * DT
        p = p + step
        if not (u0 - 0.2 < p[0] < u1 + 0.2 and v0 - 0.2 < p[1] < v1 + 0.2):
            break
        path.append(p.copy())
    if len(path) < 6:
        continue
    P = np.array(path)
    # destiny coloring: hue by the well this water reaches
    dend = [ (P[-1,0]-wu)**2 + (P[-1,1]-wv)**2 for (wu,wv) in WELLS ]
    kwell = int(np.argmin(dend))
    if dend[kwell] > 0.01:
        continue   # strays carry no story; keep the void clean
    col = (np.array([0.55, 1.0, 0.82]) if kwell == 0 else np.array([1.0, 0.82, 0.45]))
    px = (P[:, 0] - u0) * scale_u
    py = (v1 - P[:, 1]) * scale_v
    # braid the trunk: smooth lateral jitter so bundles read as ropes not hairlines
    n = len(px)
    if n > 4:
        from scipy.ndimage import gaussian_filter1d
        tx = np.gradient(px); ty = np.gradient(py)
        tn = np.hypot(tx, ty) + 1e-9
        nxv, nyv = -ty / tn, tx / tn
        off = gaussian_filter1d(rng.normal(0, 1, n), 7) * 6.5 * SS * rs
        px = px + nxv * off; py = py + nyv * off
    kit.line_splat(ink, np.stack([px, py], -1), col, amp_per_px=0.022)
ink = gaussian_filter(ink, (0.8 * SS, 0.8 * SS, 0))
# chroma-preserving soft knee so trunks glow without clipping white
lum = ink.max(-1, keepdims=True)
knee = (1 - np.exp(-1.15 * lum)) / (1.15 * lum + 1e-9)
buf += ink * knee * 1.6

# 5. the three wells: gold stars (twins) + verdigris-gold (origin past)
def px_of(wu, wv): return ((wu - u0) * scale_u, (v1 - wv) * scale_v)
kit.splat_star(buf, px_of(0, 0), np.array([0.75, 1.0, 0.8]), 3.0, 3.4 * SS * rs, 15 * SS * rs, 0.5)
for k in (1, 2):
    kit.splat_star(buf, px_of(*WELLS[k]), kit.GOLD, 3.0, 3.4 * SS * rs, 15 * SS * rs, 0.5)

buf = kit.bloom(buf, 5 * SS * rs, 0.5, thresh=0.62)
out = kit.filmic(buf, 1.3, 0.94)
kit.save(out, f"wells_{FINAL}.png", down=SS)
