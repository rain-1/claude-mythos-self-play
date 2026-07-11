"""The Families of Loss v5 — octave spiral, line-calibrated.

Every integer sits on ONE spiral thread (one turn per octave). The thread is
inked where the game says 'loss': garnet dashes (odd), cyan/violet sparks
(2p/4p), radial steel chains (2p->4p, verified L(4p)=>L(2p)), a golden 2^k
spine, and 114 wild embers. Winning numbers are the gaps — primes are the
holes in the carpet.
"""
import sys, os
import numpy as np
from glow import splat_points, splat_segments, filmic, bloom
from scipy.ndimage import gaussian_filter
from PIL import Image

S     = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
GAIN  = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
OUT   = sys.argv[3]        if len(sys.argv) > 3 else "proto/game_e.png"
SS    = 2
W = H = S * SS
cx = cy = (W - 1) / 2
NMAX = 1 << 29
LG0, LG1 = 2.0, 29.0
R0, R1 = 0.075 * W, 0.475 * W
DR = (R1 - R0) / (LG1 - LG0)
FADE_END = 28.55          # dissolve the last part-octave (end of data)

bits = np.fromfile("cache/losing.bits", dtype=np.uint8)
L = np.unpackbits(bits, bitorder="little").astype(bool)
wild = np.loadtxt("cache/wild.txt", dtype=np.int64)[:, 0]
fam = np.load("cache/families.npz")
two_p, four_p = fam["two_p"], fam["four_p"]

def polar_xy(nvals):
    lg = np.log2(nvals.astype(np.float64))
    r = R0 + DR * (lg - LG0)
    th = 2 * np.pi * (lg % 1.0)
    return cx + r * np.cos(th), cy - r * np.sin(th)

def endfade(nvals):
    lg = np.log2(nvals.astype(np.float64))
    return np.clip((29.0 - lg) / (29.0 - FADE_END), 0, 1) ** 1.5

acc = np.zeros((H, W, 3), np.float32)

# ---- odd-loss carpet: exact run arcs, constant ink per px --------------------
oddL = L[1::2]
d = np.diff(oddL.astype(np.int8))
starts = np.nonzero(d == 1)[0] + 1
ends = np.nonzero(d == -1)[0] + 1
if oddL[0]: starts = np.concatenate([[0], starts])
if oddL[-1]: ends = np.concatenate([ends, [len(oddL)]])
ns = 2 * starts + 1; ne = 2 * (ends - 1) + 1
runlen = (ends - starts).astype(np.float64)
print("runs:", len(ns))

LVL_FOG = 1.9 * GAIN
FOG_COL = np.array([0.60, 0.105, 0.105])
dlg = np.log2(ne.astype(np.float64) + 2) - np.log2(ns.astype(np.float64))
big = dlg > 0.004
x0, y0 = polar_xy(ns[~big]); x1, y1 = polar_xy(ne[~big] + 0.999)
wf = LVL_FOG * endfade(ns[~big])
# short runs at inner radii are sub-pixel arcs: ink ∝ length handled by splat
# three radial-offset strokes to survive the LANCZOS downscale
dxu = x0 - cx; dyu = y0 - cy
rn = np.hypot(dxu, dyu); dxu /= rn; dyu /= rn
OSC = W / 2560.0
for off, ow in ((-0.8*OSC, 0.28), (0.0, 0.44), (0.8*OSC, 0.28)):
    splat_segments(acc, x0 + off * dxu, y0 + off * dyu, x1 + off * dxu, y1 + off * dyu,
                   wf * ow * 3.0, FOG_COL)
ib = np.nonzero(big)[0]
bx0=[];by0=[];bx1=[];by1=[];bw=[]
for i in ib:
    npt = int(dlg[i] * 1200) + 2
    nn = np.exp2(np.linspace(np.log2(ns[i]), np.log2(ne[i] + 0.999), npt))
    xs, ys = polar_xy(nn)
    bx0.append(xs[:-1]); by0.append(ys[:-1]); bx1.append(xs[1:]); by1.append(ys[1:])
    bw.append(np.full(npt - 1, LVL_FOG * endfade(np.array([ns[i]]))[0]))
splat_segments(acc, np.concatenate(bx0), np.concatenate(by0),
               np.concatenate(bx1), np.concatenate(by1), np.concatenate(bw), FOG_COL)
print("fog done")

# ---- family sparks: per-point mass = level * circumference / count(octave) ----
def line_mass(nvals, level, fade_slope=0.030, fade_floor=0.30):
    k = np.floor(np.log2(nvals.astype(np.float64))).astype(int)
    cnt = np.bincount(k, minlength=32).astype(np.float64)
    rmid = R0 + DR * (k + 0.5 - LG0)
    fade = np.clip(1.20 - fade_slope * k, fade_floor, 1.0)
    return level * 2 * np.pi * rmid / np.maximum(cnt[k], 1) * fade * endfade(nvals)

xs, ys = polar_xy(two_p)
splat_points(acc, xs, ys, line_mass(two_p, 1.8 * GAIN), np.array([0.40, 0.78, 1.20]))
xs, ys = polar_xy(four_p)
splat_points(acc, xs, ys, line_mass(four_p, 1.3 * GAIN), np.array([0.82, 0.50, 1.20]))

# ---- chains (radial hatch): per-chain mass spread over its DR length -----------
d4 = four_p; d2 = 2 * (four_p // 4)
x0, y0 = polar_xy(d2); x1, y1 = polar_xy(d4)
k4 = np.floor(np.log2(d4.astype(np.float64))).astype(int)
cnt4 = np.bincount(k4, minlength=32).astype(np.float64)
rmid4 = R0 + DR * (k4 + 0.5 - LG0)
fade4 = np.clip(1.20 - 0.034 * k4, 0.22, 1.0)
wch = 0.85 * GAIN * 2 * np.pi * rmid4 / np.maximum(cnt4[k4], 1) / DR * fade4 * endfade(d4)
splat_segments(acc, x0, y0, x1, y1, wch, np.array([0.55, 0.65, 1.10]))
print("families done")

# ---- golden spine ----------------------------------------------------------------
pk = np.array([1 << k for k in range(2, 29) if L[1 << k]], dtype=np.int64)
xs, ys = polar_xy(pk)
tmp = np.zeros((H, W), np.float32)
np.add.at(tmp, (np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)), 1.0)
b1 = gaussian_filter(tmp, 1.1 * SS); b1 /= max(b1.max(), 1e-9)
b2 = gaussian_filter(tmp, 3.5 * SS); b2 /= max(b2.max(), 1e-9)
for c, v in enumerate((1.35, 1.05, 0.45)):
    acc[:, :, c] += b1 * v * 1.5 * GAIN
for c, v in enumerate((1.10, 0.75, 0.25)):
    acc[:, :, c] += b2 * v * 0.8 * GAIN

# ---- wild embers -------------------------------------------------------------------
xs, ys = polar_xy(wild)
tmp = np.zeros((H, W), np.float32)
np.add.at(tmp, (np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)), 1.0)
halo = gaussian_filter(tmp, 3.4 * SS); halo /= max(halo.max(), 1e-9)
core = gaussian_filter(tmp, 1.0 * SS); core /= max(core.max(), 1e-9)
for c, v in enumerate((1.35, 0.55, 0.22)):
    acc[:, :, c] += halo * v * 2.4 * GAIN
for c, v in enumerate((1.55, 1.20, 0.90)):
    acc[:, :, c] += core * v * 1.9 * GAIN

print("acc mean lum:", float(acc.mean()))
img = filmic(acc, k=1.25, gamma=0.88)
img = bloom(img, mask_lo=0.55, sigma=5 * SS, gain=0.5)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT)
