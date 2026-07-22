"""THE COAST OF THE REAL -- refinement cascade.

Truth: f = sum_{i+j<=16} c_ij P_i(x) P_j(y)  (Legendre products, decaying
random coefficients). Theories: f_d = truncation to total degree <= d --
which IS the L2(square)-orthogonal projection of the truth onto
"less complicated polynomials" (the MO question's sense), no solve needed.

Each theory's coastline Z(f_d) is drawn as a glowing ridge; early theories
are faint cold ghosts, later ones brighten and warm; the truth burns gold.
VERIFIED: L2 errors fall monotonically (exact -- orthogonal projection).
The Hausdorff distance Z(f_d) -> Z(f) falls overall but JUMPS at the levels
where a new island of coastline is born far from the old theory's coast
(d=13, d=15 here): refinement is global in norm, not local in geography --
which is the answer the picture gives to the Phil.SE question.

usage: python3 refine.py SIZE OUT SEED
"""
import sys, os
import numpy as np
from numpy.polynomial import legendre as L
from scipy.ndimage import gaussian_filter, distance_transform_edt, label
from PIL import Image

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 640
OUT = sys.argv[2] if len(sys.argv) > 2 else "art_3bmq/proto/refine_proto.png"
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 5
DMAX = 16
GAMMA = float(os.environ.get("GAMMA", 0.80))
DS = list(range(1, DMAX + 1))     # every theory, d=1..16 (last = truth)
WIN = float(os.environ.get("WIN", 0.85))  # zoom window half-width

SS = 2
S = SIZE * SS
rs = S / 1280.0

rng = np.random.default_rng(SEED)
C = np.zeros((DMAX + 1, DMAX + 1))
for i in range(DMAX + 1):
    for j in range(DMAX + 1):
        if i + j <= DMAX:
            C[i, j] = rng.normal() * GAMMA ** (i + j)
C[0, 0] *= 0.25                    # keep the mean small -> more coastline

xs = np.linspace(-WIN, WIN, S)
# Vandermonde of Legendre polys: (S, DMAX+1)
VX = np.stack([L.legval(xs, np.eye(DMAX + 1)[k]) for k in range(DMAX + 1)], axis=1)

def field(Ct):
    return VX @ Ct @ VX.T          # f(y, x) with y rows? symmetric usage below

def trunc(d):
    Ct = C.copy()
    for i in range(DMAX + 1):
        for j in range(DMAX + 1):
            if i + j > d:
                Ct[i, j] = 0.0
    return Ct

# ---------------- verification: L2 error, Hausdorff, components ------------
# L2 norms are exact from coefficients: ||P_i P_j||^2 = 4/((2i+1)(2j+1))
W = np.array([[4.0 / ((2 * i + 1) * (2 * j + 1)) for j in range(DMAX + 1)]
              for i in range(DMAX + 1)])
print("seed", SEED, "gamma", GAMMA)
fields = {}
zmasks = {}
print(" d | L2 rel err | Hausdorff(px@%d) | coast components" % S)
F_true = field(C)
gx, gy = np.gradient(F_true)
gt = np.hypot(gx, gy) + 1e-12
zt = (np.abs(F_true) / gt) < 0.75
stats = []
for d in DS:
    Ct = trunc(d)
    Fd = field(Ct)
    fields[d] = Fd
    err = np.sqrt((W * (C - Ct) ** 2).sum() / (W * C ** 2).sum())
    gx, gy = np.gradient(Fd)
    g = np.hypot(gx, gy) + 1e-12
    zm = (np.abs(Fd) / g) < 0.75
    zmasks[d] = zm
    # Hausdorff between zm and zt in pixels
    if zm.any():
        dt_t = distance_transform_edt(~zt)
        dt_d = distance_transform_edt(~zm)
        hd = max(dt_t[zm].max(), dt_d[zt].max())
    else:
        hd = np.inf
    npos = label(Fd > 0)[1]; nneg = label(Fd < 0)[1]
    stats.append((d, err, hd, npos + nneg - 1))
    print(f"{d:3d} | {err:10.4f} | {hd:12.1f} | {npos + nneg - 1}")

# ---------------- render ---------------------------------------------------
acc = np.zeros((S, S, 3), np.float32)

# truth relief: dim field of |f| as deep ground
Ft = fields[DMAX]
rel = np.abs(Ft) / np.abs(Ft).max()
sgn = np.tanh(Ft / (0.45 * Ft.std()))
land = (0.5 + 0.5 * sgn)[..., None] * np.array([0.044, 0.035, 0.023])[None, None, :]
sea = (0.5 - 0.5 * sgn)[..., None] * np.array([0.024, 0.040, 0.068])[None, None, :]
depthfade = (1 - 0.45 * rel[..., None] ** 0.6)
acc += ((land + sea) * depthfade).astype(np.float32)

# theory cascade: every level d=1..16, cold faint -> warm bright, truth gold
STOPS = np.array([
    [0.34, 0.48, 0.80],    # slate blue (visible)
    [0.26, 0.62, 0.76],    # cold teal
    [0.30, 0.72, 0.62],    # verdigris
    [0.62, 0.78, 0.50],    # sea-green pale
    [0.90, 0.74, 0.38],    # old gold
    [1.00, 0.74, 0.24],    # truth gold
])
def ramp_col(u):
    t = u * (len(STOPS) - 1)
    k = min(int(t), len(STOPS) - 2)
    return STOPS[k] + (t - k) * (STOPS[k + 1] - STOPS[k])

for d in DS:
    u = (d - 1) / (DMAX - 1)
    Fd = fields[d]
    gx, gy = np.gradient(Fd)
    g = np.hypot(gx, gy) + 1e-12
    dpx = np.abs(Fd) / g
    w = (2.6 - 1.1 * u) * rs
    ridge = np.exp(-(dpx / w) ** 2)
    amp = 0.16 + 1.15 * u ** 3.2
    if d in (DMAX - 2, DMAX - 1):
        amp *= 0.70
    if d == DMAX:
        amp = 2.3
    acc += (amp * ridge)[..., None] * ramp_col(u)[None, None, :]

# bloom on the truth curve only
gx, gy = np.gradient(Ft)
g = np.hypot(gx, gy) + 1e-12
dpx = np.abs(Ft) / g
truth_ridge = np.exp(-(dpx / (1.8 * rs)) ** 2)
tr = truth_ridge[..., None] * np.array([1.0, 0.82, 0.40])[None, None, :]
b1 = np.stack([gaussian_filter(tr[..., i], 3.0 * rs) for i in range(3)], -1)
b2 = np.stack([gaussian_filter(tr[..., i], 14 * rs) for i in range(3)], -1)
acc += 0.9 * b1 + 0.55 * b2

img = 1 - np.exp(-1.5 * acc)
img = np.clip(img, 0, 1) ** (1 / 1.30)
pil = Image.fromarray((img * 255).astype(np.uint8))
pil = pil.resize((SIZE, SIZE), Image.LANCZOS)
pil.save(OUT)
print("saved", OUT)
