"""THE SIGNAL IN THE STORM — stochastic resonance field render.

Rows: noise level D (log, quiet top -> storm bottom). Columns: time.
Brightness = fraction of the 64-walker ensemble in the far well.
Hue = measured coherence of <x>(t) at the drive frequency (cold -> amber).
Three witness walkers drawn at their true rows; the sub-threshold signal
itself crosses the silent zone as a whisper-thin thread.

Usage: python3 sr_render.py <size> <out.png>
"""
import numpy as np, sys, os, time
from scipy.ndimage import gaussian_filter, gaussian_filter1d, map_coordinates
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

t0 = time.time()
S   = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
OUT = sys.argv[2] if len(sys.argv) > 2 else "art_x61t/variants/sr_proto.png"
sc = S/2560.0
LW = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

d = np.load("art_x61t/data/sr_field.npz")
field, coh, D = d["field"], d["coh"], d["D"]
wit, wit_rows = d["wit"], d["wit_rows"]
A, PER = float(d["A"]), float(d["PER"])
R, C = field.shape

# ---- resample field to canvas ----
ry = np.linspace(0, R-1, S).astype(np.float32)
cx = np.linspace(0, C-1, S).astype(np.float32)
gy, gx = np.meshgrid(ry, cx, indexing="ij")
F = map_coordinates(field, [gy, gx], order=1)
F = gaussian_filter(F, (0.8*sc, 1.2*sc))

# ---- hue by coherence ----
cohS = gaussian_filter1d(np.interp(ry, np.arange(R), coh), 14.0*sc*2)
u0 = np.clip((cohS - cohS.min())/(cohS.max() - cohS.min()), 0, 1)
def sstep(a):
    a = np.clip(a, 0, 1); return a*a*(3 - 2*a)
u  = sstep((u0 - 0.64)/0.13)                             # hue gate: amber = the band
ug = sstep((u0 - 0.45)/0.33)                             # brightness gate
COLD = np.array([0.24, 0.42, 1.10], np.float32)   # indigo slate
WARM = np.array([1.55, 0.95, 0.35], np.float32)   # amber
COLD /= COLD @ LW; WARM /= WARM @ LW
hue = COLD[None, :]*(1-u[:, None]) + WARM[None, :]*u[:, None]   # [S,3]
gain = (0.055 + 1.65*ug).astype(np.float32)                     # brightness IS coherence

Lf = (F**1.35)*gain[:, None]*0.9
Lc = 0.92*(1.0 - np.exp(-1.5*Lf))                # compress luminance BEFORE colorizing
img = (Lc[:, :, None]*hue[:, None, :]).astype(np.float32)
print(f"field {time.time()-t0:.1f}s", flush=True)

# ---- splat helper ----
canvas = np.zeros((S, S, 3), dtype=np.float32)
def splat(x, y, rgbw):
    ok = (x >= 0) & (x < S-1) & (y >= 0) & (y < S-1)
    x, y, rgbw = x[ok], y[ok], rgbw[ok]
    x0 = x.astype(np.int32); y0 = y.astype(np.int32)
    fx = (x-x0).astype(np.float32); fy = (y-y0).astype(np.float32)
    for dx, dy, w in ((0,0,(1-fx)*(1-fy)), (1,0,fx*(1-fy)),
                      (0,1,(1-fx)*fy), (1,1,fx*fy)):
        np.add.at(canvas, (y0+dy, x0+dx), rgbw*w[:, None])

def thread(ts, ys, col, wgt, sub=6):
    """polyline splat with linear interpolation between samples"""
    n = len(ts)
    tt = np.interp(np.arange((n-1)*sub)/sub, np.arange(n), ts)
    yy = np.interp(np.arange((n-1)*sub)/sub, np.arange(n), ys)
    splat(tt, yy, np.tile(col*wgt/sub, ((n-1)*sub, 1)))

# ---- the sub-threshold signal: a whisper in the silence ----
tcol = np.arange(S, dtype=np.float32)
phase = 2*np.pi*(tcol/S)*10.0                    # NPER=10 periods
sigy = 0.085*S - np.sin(phase)*0.030*S
thread(tcol, sigy, np.array([1.3, 1.02, 0.55], np.float32), 0.55*sc, sub=4)

# ---- witness walkers ----
for k, wr in enumerate(wit_rows):
    yrow = wr/R*S
    amp = 0.032*S
    ys = yrow - wit[k]*amp
    uw = float(sstep((np.interp(wr/R*S, np.arange(S), u0) - 0.62)/0.18))
    col = COLD*(1-uw) + WARM*uw
    col = col/(col @ LW)
    xs = np.linspace(0, S-1, len(ys)).astype(np.float32)
    wcol = col*0.55 + 0.45*np.array([1.06, 1.0, 0.92], np.float32)
    thread(xs, ys.astype(np.float32), wcol, 3.4*sc, sub=8)
print(f"threads {time.time()-t0:.1f}s", flush=True)

img += gaussian_filter(canvas, (0.7*sc, 0.7*sc, 0))

# ---- bloom the resonance band ----
lum = img @ LW
thr = np.percentile(lum, 99.55)
mask = np.clip((lum-thr)/(thr+1e-9), 0, None)[..., None]*img
img = img + 0.55*gaussian_filter(mask, (2.5*sc, 2.5*sc, 0)) \
          + 0.25*gaussian_filter(mask, (10*sc, 10*sc, 0))

# ---- faint cold base so the silence isn't dead ----
yv = (np.arange(S, dtype=np.float32)/S)[:, None, None]
img = img + (0.0045 + 0.0045*yv)*np.array([0.10, 0.13, 0.26], np.float32)

x = 1 - np.exp(-1.9*img)
out = (255*np.clip(x, 0, 1)**(1/2.1)).astype(np.uint8)
Image.fromarray(out).save(OUT)
print(f"saved {OUT} {time.time()-t0:.1f}s")
