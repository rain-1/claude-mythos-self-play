"""The Sun of Nothing v2 — Boole orbit in induced-map time.

Angle = breath index (each excursion of constant sign = one breath of the
first-return map), radius = the excursion's true height profile
asinh(|x|). Outward petals = x>0, inward = x<0 (the map alternates sides).
Destiny color per petal = peak height. The ring at R0 is Nothing; the
tallest ice flares are the window onto Infinity.
"""
import sys, os
import numpy as np
from glow import splat_segments, filmic, bloom, lerp_palette
from PIL import Image

S      = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
T      = int(sys.argv[2])   if len(sys.argv) > 2 else 8_000_000
X0     = float(sys.argv[3]) if len(sys.argv) > 3 else 1.54217
WMODE  = sys.argv[4]        if len(sys.argv) > 4 else "logd"   # equal | logd
GAIN   = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
OUT    = sys.argv[6]        if len(sys.argv) > 6 else "proto/petals_a.png"
SS     = 2
W = H = S * SS
R0, ROUT, RIN = 0.42, 0.985, 0.03
MAXSEG = 1500          # subsample long excursions to this many segments

# ---- simulate (chunked scalar loop) -----------------------------------------
x = X0
xs = np.empty(T + 1, np.float64)
xs[0] = x
for t in range(T):
    x = x - 1.0 / x
    xs[t + 1] = x

s = xs > 0
cuts = np.nonzero(s[1:] != s[:-1])[0] + 1
bounds = np.concatenate([[0], cuts, [T + 1]])
NE = len(bounds) - 1
durs = np.diff(bounds).astype(np.float64)
peaks = np.array([np.abs(xs[a:b]).max() for a, b in zip(bounds[:-1], bounds[1:])])
outward = np.array([s[a] for a in bounds[:-1]])

# ---- angular shares ----------------------------------------------------------
if WMODE == "equal":
    share = np.ones(NE)
else:
    share = 1.0 + np.log1p(durs) * 0.55
share = share / share.sum() * 2 * np.pi
ang0 = np.concatenate([[0], np.cumsum(share)]) - np.pi / 2

VMAX = peaks.max()
den = np.arcsinh(VMAX)
logden = np.log10(max(VMAX, 10.0))

PAL = [(0.00, (1.00, 0.38, 0.08)),
       (0.30, (1.00, 0.70, 0.22)),
       (0.55, (0.95, 0.90, 0.65)),
       (0.78, (0.55, 0.78, 1.00)),
       (1.00, (0.88, 0.95, 1.00))]

half = min(W, H) / 2
cx = cy = (W - 1) / 2
acc = np.zeros((H, W, 3), np.float32)
BASE = GAIN * 0.9 * (2560 / W) ** 0.6

# accumulate segment lists in batches
bx0 = []; by0 = []; bx1 = []; by1 = []; bw = []; bc = []
def flush():
    global bx0, by0, bx1, by1, bw, bc
    if bx0:
        splat_segments(acc, np.concatenate(bx0), np.concatenate(by0),
                       np.concatenate(bx1), np.concatenate(by1),
                       np.concatenate(bw), np.concatenate(bc))
        bx0 = []; by0 = []; bx1 = []; by1 = []; bw = []; bc = []

for i in range(NE):
    a, b = bounds[i], bounds[i + 1]
    seg = np.abs(xs[a:b])
    D = b - a
    if D > MAXSEG:  # subsample, keep the peak start and the tail
        idx = np.unique(np.round(np.linspace(0, D - 1, MAXSEG)).astype(int))
        seg = seg[idx]
        u = idx / (D - 1)
    else:
        u = np.arange(D) / max(D - 1, 1)
    rr = np.arcsinh(seg) / den
    r = R0 + rr * (ROUT - R0) if outward[i] else R0 - rr * (R0 - RIN)
    th = ang0[i] + u * (ang0[i + 1] - ang0[i])
    # prepend anchor on the ring at petal start (the launch spoke)
    r = np.concatenate([[R0], r, [R0]])
    th = np.concatenate([[th[0]], th, [th[-1]]])
    px = cx + r * half * np.cos(th)
    py = cy + r * half * np.sin(th)
    tt = min(np.log10(max(peaks[i], 1.0)) / logden, 1.0)
    c = lerp_palette(tt, PAL).astype(np.float32)
    n = len(px) - 1
    bx0.append(px[:-1]); by0.append(py[:-1]); bx1.append(px[1:]); by1.append(py[1:])
    # launch/plunge spokes dimmer
    wv = np.full(n, BASE); wv[0] *= 0.35; wv[-1] *= 0.35
    bw.append(wv); bc.append(np.broadcast_to(c, (n, 3)))
    if sum(len(v) for v in bx0) > 3_000_000:
        flush()
flush()

img = filmic(acc, k=1.0, gamma=0.85)
img = bloom(img, mask_lo=0.5, sigma=5 * SS, gain=0.55)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT, "| breaths:", NE, "| max peak:", round(float(VMAX), 1),
      "| top-5 shares deg:", np.round(np.sort(share)[-5:] * 180 / np.pi, 1))
