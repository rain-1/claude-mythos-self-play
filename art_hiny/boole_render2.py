"""The Sun of Nothing v3 — render cached excursion census as polar corona.

Rank-equalized destiny palette, fat soft strokes, breath-time angle.
"""
import sys, os
import numpy as np
from glow import splat_segments, filmic, bloom, lerp_palette
from PIL import Image

S      = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
GAIN   = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
NPZ    = sys.argv[3]        if len(sys.argv) > 3 else "cache/boole_orbit.npz"
OUT    = sys.argv[4]        if len(sys.argv) > 4 else "proto/petals_b.png"
LOGW   = float(sys.argv[5]) if len(sys.argv) > 5 else 0.35  # share ∝ 1+LOGW*ln(1+D)
B0     = int(sys.argv[6])   if len(sys.argv) > 6 else 0
B1     = int(sys.argv[7])   if len(sys.argv) > 7 else -1
PCTL   = float(sys.argv[8]) if len(sys.argv) > 8 else 100.0  # radius norm percentile of peaks
SS     = 2
W = H = S * SS
R0, ROUT, RIN = 0.44, 0.99, 0.02

d = np.load(NPZ)
flat, lens, durs, sides, peaks = d["flat"], d["lens"], d["durs"], d["sides"], d["peaks"]
NE = len(lens)
offs = np.concatenate([[0], np.cumsum(lens)])
if B1 < 0: B1 = NE
sel = slice(B0, B1)
offs = offs[B0:B1 + 1]
lens = lens[sel]; durs = durs[sel]; sides = sides[sel]; peaks = peaks[sel]
NE = len(lens)

share = 1.0 + LOGW * np.log1p(durs.astype(np.float64))
share = share / share.sum() * 2 * np.pi
ang0 = np.concatenate([[0], np.cumsum(share)]) - np.pi / 2

VMAX = float(np.percentile(peaks, PCTL)) if PCTL < 100 else float(peaks.max())
den = np.arcsinh(VMAX)

# rank-equalized destiny palette (peak rank -> palette position)
order = np.argsort(peaks, kind="stable")
rank = np.empty(NE)
rank[order] = np.arange(NE) / (NE - 1)
PAL = [(0.00, (0.55, 0.14, 0.05)),
       (0.35, (1.00, 0.45, 0.10)),
       (0.62, (1.00, 0.80, 0.30)),
       (0.82, (0.95, 0.93, 0.72)),
       (0.94, (0.60, 0.80, 1.00)),
       (1.00, (0.90, 0.96, 1.00))]
pcol = lerp_palette(rank, PAL).astype(np.float32)

half = min(W, H) / 2
cx = cy = (W - 1) / 2
acc = np.zeros((H, W, 3), np.float32)
BASE = GAIN * 0.30 * (2560 / W) ** 0.6

# fat soft stroke: 5 radial offsets, gaussian weights
OFFS = np.array([-2.0, -1.0, 0.0, 1.0, 2.0]) * (W / 2560)
OWTS = np.exp(-0.5 * (OFFS / (1.1 * W / 2560)) ** 2)
OWTS /= OWTS.sum()

bx0=[]; by0=[]; bx1=[]; by1=[]; bw=[]; bc=[]
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
    c = pcol[i]
    m = len(r) - 1
    wbase = np.full(m, BASE)
    wbase[0] *= 0.4; wbase[-1] *= 0.4
    for off, ow in zip(OFFS, OWTS):
        ro = r + off / half
        px = cx + ro * half * np.cos(th)
        py = cy + ro * half * np.sin(th)
        bx0.append(px[:-1]); by0.append(py[:-1]); bx1.append(px[1:]); by1.append(py[1:])
        bw.append(wbase * ow); bc.append(np.broadcast_to(c, (m, 3)))
    if sum(len(v) for v in bx0) > 4_000_000:
        flush()
flush()

img = filmic(acc, k=1.0, gamma=0.85)
img = bloom(img, mask_lo=0.45, sigma=5 * SS, gain=0.6)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT, "| breaths:", NE)
