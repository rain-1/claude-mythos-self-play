"""The Braid of Rings — leapfrogging vortex ring worldtubes in spacetime.

Comoving chart: X = drift-removed axial position + time; (Y,Z) = the ring
circle. Each ring sweeps a glowing tube; leapfrog = tubes alternately
swallowing each other. Impulse pi*sum(G R^2) is conserved through every pass.
"""
import sys, os
import numpy as np
from glow import splat_segments, filmic, bloom, lerp_palette
from PIL import Image
from dyson import simulate, hamiltonian

WPX    = int(sys.argv[1]) if len(sys.argv) > 1 else 1600
HPX    = int(sys.argv[2]) if len(sys.argv) > 2 else 900
GAIN   = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
TSIM   = int(sys.argv[4]) if len(sys.argv) > 4 else 40000
NRING  = int(sys.argv[5]) if len(sys.argv) > 5 else 2
OUT    = sys.argv[6] if len(sys.argv) > 6 else "proto/rings_a.png"
SS     = 2
W, H = WPX * SS, HPX * SS

# ---- simulate ----------------------------------------------------------------
dt = 2e-3
if NRING == 2:
    G = np.array([1.0, 1.0]); sig0 = [1.0, 1.0]; Z0 = [0.0, 0.9]; a0 = 0.08
else:
    G = np.array([1.0, 1.0, 1.0]); sig0 = [1.0, 1.0, 1.0]; Z0 = [0.0, 0.75, 1.5]; a0 = 0.08
ts, ss, zs, a0R0 = simulate(sig0, Z0, G, a0, dt, TSIM, keep_every=10)
R = np.sqrt(ss)                     # (F, n)
F = len(ts)
P = np.pi * (G * ss).sum(axis=1)
print("impulse rel drift:", np.ptp(P) / P[0])

# comoving
zbar = zs.mean(axis=1)
drift = np.polyfit(ts, zbar, 1)[0]
zt = zs - (drift * ts)[:, None] - zs[0].mean()

# ---- scene layout --------------------------------------------------------------
s0 = 0.30 * H                       # world unit (ring radius 1) in px
tspan = ts[-1]
tsc = 0.80 * W / tspan              # time -> X px
XW = zt * s0 * 1.0 + (ts * tsc)[:, None]  # (F,n) world X per ring (px-ish units)

PITCH = np.deg2rad(float(os.environ.get('PITCH','48')))              # tilt: see the tube slightly from above
FOC = float(os.environ.get('FOC','1.7')) * H                       # perspective focal length (px)

def project(X, Y, Zv):
    """world: X along axis (px), Y depth toward viewer, Zv up (world px)."""
    Y2 = Y * np.cos(PITCH) - Zv * np.sin(PITCH)
    Z2 = Y * np.sin(PITCH) + Zv * np.cos(PITCH)
    f = FOC / (FOC + Y2 + 2.2 * s0)
    return (X - W * 0.40) * f + W * 0.40, H * 0.52 - Z2 * f, f

# ---- two-pass framing: sample the whole scene bbox, then affine-fit ----------
def scene_bbox():
    thb = np.linspace(0, 2 * np.pi, 64, endpoint=False)
    xs = []; ys = []
    for i in range(len(G)):
        for jth in range(0, 64):
            c, s = np.cos(thb[jth]), np.sin(thb[jth])
            px, py, _ = project(XW[:, i], R[:, i] * s0 * c, R[:, i] * s0 * s)
            xs.append(px); ys.append(py)
    xs = np.concatenate(xs); ys = np.concatenate(ys)
    return xs.min(), xs.max(), ys.min(), ys.max()

_x0, _x1, _y0, _y1 = scene_bbox()
_scale = min(0.94 * W / (_x1 - _x0), 0.82 * H / (_y1 - _y0))
_ox = (W - (_x1 - _x0) * _scale) / 2 - _x0 * _scale
_oy = (H - (_y1 - _y0) * _scale) / 2 - _y0 * _scale

def project_fit(X, Y, Zv):
    px, py, f = project(X, Y, Zv)
    return px * _scale + _ox, py * _scale + _oy, f

HUES = [np.array([1.05, 0.62, 0.16]),   # amber
        np.array([0.20, 0.85, 0.95]),   # teal
        np.array([0.85, 0.45, 1.00])]   # violet (3rd ring)

acc = np.zeros((H, W, 3), np.float32)
NTH = int(os.environ.get('NTH','44'))
BASE = GAIN * 0.16 * (3200 / W) ** 0.6

th = np.linspace(0, 2 * np.pi, NTH, endpoint=False)
# global depth normalization across the scene
_, _, fA = project(XW.ravel(), (R * s0).ravel(), np.zeros(R.size))
_, _, fB = project(XW.ravel(), -(R * s0).ravel(), np.zeros(R.size))
FN0, FN1 = min(fB.min(), fA.min()), max(fB.max(), fA.max())
for i in range(len(G)):
    hue = HUES[i]
    Xf = XW[:, i]                # (F,)
    Rf = R[:, i] * s0            # (F,)
    # longitudinal threads: one polyline per theta
    for jth in range(NTH):
        c, s = np.cos(th[jth]), np.sin(th[jth])
        Y = Rf * c               # depth
        Zv = Rf * s              # up
        px, py, f = project_fit(Xf, Y, Zv)
        # brightness: strong depth opacity (front bright, far side whispers)
        fn = (f - FN0) / max(FN1 - FN0, 1e-9)
        shade = (0.22 + 0.78 * fn) ** 2.6 * (0.80 + 0.20 * s)
        wseg = BASE * (shade[:-1] + shade[1:]) * 0.5
        col = np.broadcast_to(hue, (F - 1, 3))
        splat_segments(acc, px[:-1], py[:-1], px[1:], py[1:], wseg, col)
    # ring hoops every K frames, brighter
    KH = F // 30
    thh = np.linspace(0, 2 * np.pi, 500)
    for fidx in range(0, F, KH):
        Y = Rf[fidx] * np.cos(thh); Zv = Rf[fidx] * np.sin(thh)
        px, py, f = project_fit(np.full(len(thh), Xf[fidx]), Y, Zv)
        fn = (f - FN0) / max(FN1 - FN0, 1e-9)
        shade = (0.22 + 0.78 * fn) ** 2.6
        wseg = BASE * 2.2 * (shade[:-1] + shade[1:]) * 0.5
        splat_segments(acc, px[:-1], py[:-1], px[1:], py[1:], wseg,
                       np.broadcast_to(hue * 1.15, (len(thh) - 1, 3)))

img = filmic(acc, k=1.0, gamma=0.88)
img = bloom(img, mask_lo=0.5, sigma=6 * SS, gain=0.6)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((WPX, HPX), Image.LANCZOS).save(OUT)
print("saved", OUT)
