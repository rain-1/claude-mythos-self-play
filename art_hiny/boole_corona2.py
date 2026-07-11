"""The Sun of Nothing v4 — altitude-colored corona in breath time."""
import sys, os
import numpy as np
from glow import splat_segments, filmic, bloom, lerp_palette
from PIL import Image

S      = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
GAIN   = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
B0     = int(sys.argv[3])   if len(sys.argv) > 3 else 0
B1     = int(sys.argv[4])   if len(sys.argv) > 4 else 2500
PCTL   = float(sys.argv[5]) if len(sys.argv) > 5 else 99.5
OUT    = sys.argv[6]        if len(sys.argv) > 6 else "proto/corona2_a.png"
NPZ    = "cache/boole_orbit.npz"
LOGW   = 0.35
SS     = 2
W = H = S * SS
R0, ROUT, RIN = 0.42, 0.99, 0.15

d = np.load(NPZ)
flat, lens, durs, sides, peaks = d["flat"], d["lens"], d["durs"], d["sides"], d["peaks"]
NEall = len(lens)
offs = np.concatenate([[0], np.cumsum(lens)])
if B1 < 0 or B1 > NEall: B1 = NEall
sel = slice(B0, B1)
offs = offs[B0:B1 + 1]
lens = lens[sel]; durs = durs[sel]; sides = sides[sel]; peaks = peaks[sel]
NE = len(lens)

share = 1.0 + LOGW * np.log1p(durs.astype(np.float64))
share = share / share.sum() * 2 * np.pi
ang0 = np.concatenate([[0], np.cumsum(share)]) - np.pi / 2

VMAX = float(np.percentile(peaks, PCTL))
den = np.arcsinh(VMAX)

# altitude palette: ring = white-hot, then gold, then ember, then ice at the top
ALT = [(0.00, (1.30, 1.05, 0.75)),
       (0.10, (1.20, 0.75, 0.28)),
       (0.28, (1.00, 0.46, 0.12)),
       (0.46, (0.75, 0.40, 0.26)),
       (0.62, (0.42, 0.58, 1.15)),
       (0.82, (0.34, 0.62, 1.55)),
       (1.00, (0.70, 0.88, 1.60))]

half = min(W, H) / 2
cx = cy = (W - 1) / 2
acc = np.zeros((H, W, 3), np.float32)
BASE = GAIN * 1.8 * (2560 / W) ** 0.6

OFFS = np.array([-1.5, -0.75, 0.0, 0.75, 1.5]) * (W / 2560)
OWTS = np.exp(-0.5 * (OFFS / (0.9 * W / 2560)) ** 2); OWTS /= OWTS.sum()

bx0=[];by0=[];bx1=[];by1=[];bw=[];bc=[]
def flush():
    global bx0,by0,bx1,by1,bw,bc
    if bx0:
        splat_segments(acc, np.concatenate(bx0), np.concatenate(by0),
                       np.concatenate(bx1), np.concatenate(by1),
                       np.concatenate(bw), np.concatenate(bc))
        bx0=[];by0=[];bx1=[];by1=[];bw=[];bc=[]

for i in range(NE):
    prof = flat[offs[i]:offs[i + 1]].astype(np.float64)
    n = len(prof)
    u = np.arange(n) / max(n - 1, 1)
    rr = np.minimum(np.arcsinh(prof) / den, 1.0)
    r = R0 + rr * (ROUT - R0) if sides[i] else R0 - rr * (R0 - RIN)
    th = ang0[i] + u * (ang0[i + 1] - ang0[i])
    r = np.concatenate([[R0], r, [R0]])
    th = np.concatenate([[th[0]], th, [th[-1]]])
    rrx = np.concatenate([[0.0], rr, [0.0]])
    cols = lerp_palette(rrx, ALT).astype(np.float32)
    cseg = (cols[:-1] + cols[1:]) * 0.5
    m = len(r) - 1
    wbase = np.full(m, BASE)
    for off, ow in zip(OFFS, OWTS):
        ro = r + off / half
        px = cx + ro * half * np.cos(th)
        py = cy + ro * half * np.sin(th)
        bx0.append(px[:-1]); by0.append(py[:-1]); bx1.append(px[1:]); by1.append(py[1:])
        bw.append(wbase * ow); bc.append(cseg)
    if sum(len(v) for v in bx0) > 4_000_000:
        flush()
flush()

img = filmic(acc, k=1.0, gamma=0.88)
img = bloom(img, mask_lo=0.5, sigma=6 * SS, gain=0.7)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT, "| breaths:", NE, "| VCAP:", round(VMAX, 1))
