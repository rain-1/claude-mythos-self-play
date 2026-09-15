"""render_ledger.py — THE LEDGER PIECE (Erdős discrepancy).
A ±1 sequence x_1..x_N whose every homogeneous-progression ledger S_d(k) = x_d + ... + x_{kd}
stays within [-2, 2]. Row (ring) d is tiled by the cells ((k-1)d, kd], each tinted by the ledger
value after k answers: warm for +, cool for -, paper for zero. Coral marks the cell that cannot be
filled: n = N+1 (Konev–Lisitsa: no such sequence of length 1161; Tao: none of any length).

usage: python3 render_ledger.py FINAL seq.json out_prefix [mode=loom|rose] [D]
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
import pastel as P

FINAL = int(sys.argv[1]); SEQ = sys.argv[2]; OUT = sys.argv[3]
MODE = sys.argv[4] if len(sys.argv) > 4 else 'loom'
D = int(sys.argv[5]) if len(sys.argv) > 5 else 0
SS = 2; W = H = FINAL * SS; rs = FINAL / 1024.0 * SS
t0 = time.time()

dat = json.load(open(SEQ)); x = np.array(dat['x'], np.int64); N = len(x)
# ledgers
ledger = {}
for d in range(1, N + 1):
    ledger[d] = np.cumsum(x[d - 1::d])
assert max(np.abs(v).max() for v in ledger.values()) <= 2
print('N', N, 'ledgers ok', flush=True)

# value -> (pigment, density)
VAL = {2: ('apricot', 1.35), 1: ('lemon', 0.62), 0: (None, 0.0), -1: ('aqua', 0.62), -2: ('cornflower', 1.35)}

sheet = P.Sheet(W, H, seed=11)
val_img = Image.new('I', (W, H), 0)     # value + 3 (0 = outside)
dr = ImageDraw.Draw(val_img)
dep_img = Image.new('F', (W, H), 1.0); ddr = ImageDraw.Draw(dep_img)   # per-ring density weight

if MODE == 'loom':
    D = D or 160
    x0, x1 = 0.06 * W, 0.94 * W
    y0, y1 = 0.075 * H, 0.86 * H
    # row heights ∝ d^-0.35 (fine rows get a little more room)
    hw = np.arange(1, D + 1) ** -0.35; hw = hw / hw.sum() * (y1 - y0)
    ytop = y0 + np.concatenate([[0], np.cumsum(hw)[:-1]])
    gap = 0.12                                        # paper gap between rows, fraction of row
    for d in range(1, D + 1):
        S = ledger[d]; K = len(S)
        ya, yb = ytop[d - 1] + gap * hw[d - 1] * 0.5, ytop[d - 1] + hw[d - 1] * (1 - gap * 0.5)
        for k in range(1, K + 1):
            xa = x0 + (k - 1) * d / N * (x1 - x0); xb = x0 + k * d / N * (x1 - x0)
            v = int(S[k - 1])
            if v != 0:
                dr.rectangle([xa, ya, xb - 0.6 * rs, yb], fill=v + 3)
    coral_seg = [(x1, y0), (x1, y1)]
elif MODE == 'rose':
    D = D or 110
    cx, cy = W / 2, 0.445 * H
    R = 0.425 * H; t = R * 0.88 / D
    for d in range(1, D + 1):
        S = ledger[d]; K = len(S)
        ro = R - (d - 1) * t; ri = ro - t * 0.94
        for k in range(1, K + 1):
            v = int(S[k - 1])
            if v == 0:
                continue
            a0 = 360.0 * (k - 1) * d / N - 90; a1 = 360.0 * k * d / N - 90
            if a1 - a0 > 0.25:
                a1 -= 0.12
            # pie slice outer, then cut inner
            dr.pieslice([cx - ro, cy - ro, cx + ro, cy + ro], a0, a1, fill=v + 3)
        dr.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=0)
        ddr.ellipse([cx - ro, cy - ro, cx + ro, cy + ro], fill=float(1.0 / (1 + 0.06 * np.log(d))))
    coral_seg = [(cx, cy - R - 12 * rs), (cx, cy - R + D * t)]
vals = np.asarray(val_img); depw = np.asarray(dep_img, np.float32)
print('cells drawn [%.0fs]' % (time.time() - t0), flush=True)

# pooling edges: each cell pools pigment toward its rim
inside = vals > 0
edt = distance_transform_edt(inside)
pool = np.exp(-edt / (2.2 * rs)).astype(np.float32)
WARM = ['lemon', 'apricot', 'blush', 'orchid']; COOL = ['lavender', 'cornflower', 'aqua', 'mint']
DENS = {1: 0.85, 2: 1.65}
# ring depth -> position along the family (0 at the rim, 1 at the heart), via the depth image
if MODE == 'rose':
    yy, xx = np.mgrid[:H, :W]; rr = np.hypot(xx - cx, yy - cy)
    u = np.clip((R - rr) / (D * t), 0, 1).astype(np.float32); del rr, xx, yy
else:
    yy = np.arange(H, dtype=np.float32)[:, None]
    u = np.clip((yy - y0) / (y1 - y0), 0, 1).astype(np.float32) * np.ones((1, W), np.float32)
pos = u * (len(WARM) - 1)
for sign, fam in ((1, WARM), (-1, COOL)):
    for a in range(2):
        m = ((vals == sign * (a + 1) + 3)).astype(np.float32)
        if m.sum() == 0:
            continue
        base = DENS[a + 1] * m * (0.78 + 0.5 * pool) * depw
        for j, pig in enumerate(fam):
            wj = np.clip(1 - np.abs(pos - j), 0, 1)
            d_ = gaussian_filter(base * wj, 0.5 * rs)
            sheet.wash(d_, pig, granulate=0.2, seed=20 + 4 * a + j + (0 if sign > 0 else 8))
del edt, pool, pos, u

if MODE == 'rose':
    segs = []
    for n_ in range(1, N + 1):
        a = np.deg2rad(360.0 * (n_ - 0.5) / N - 90)
        r0 = R + 4 * rs; r1 = R + (11 if x[n_ - 1] > 0 else 7) * rs
        if x[n_ - 1] < 0: r0, r1 = R + 1.5 * rs, R + 5 * rs
        segs.append((cx + r0 * np.cos(a), cy + r0 * np.sin(a), cx + r1 * np.cos(a), cy + r1 * np.sin(a)))
    tick = P.draw_lines_density(W, H, segs, 1.1 * rs, sigma=0.4 * rs)
    sheet.wash(np.clip(tick, 0, 1) * 0.9, 'ink')
# the cell that cannot be filled: coral hairline at n = N+1
cor = P.polyline_density(W, H, coral_seg, 2.2 * rs, sigma=0.6 * rs)
sheet.wash(np.clip(cor, 0, 1) * 1.3, 'coral')

# captions
title = 'The Longest Honest Answer' if N >= 1160 else 'The Longest Honest Answer (proto N=%d)' % N
sub = 'You answered yes or no 1,160 times, and every ledger — every d, 2d, 3d, … — stayed within two. There is no 1,161st answer that keeps them all.' if N >= 1160 else 'proto N=%d' % N
ts = 30 * rs; ss = 17 * rs
lines = P.wrap(sub, ss, 'italic', 0.62 * W)
items = [(title, W / 2, 0.918 * H, ts, 'serif_bold', 'mm')]
for i, l in enumerate(lines):
    items.append((l, W / 2, 0.955 * H + i * 1.35 * ss, ss, 'italic', 'mm'))
sheet.wash(P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + '_%d.png' % FINAL)
json.dump(dict(N=N, C=2, D=D, mode=MODE, seq_file=SEQ, solver=dat.get('solver'), sat_seconds=dat.get('seconds'),
               max_abs_ledger=int(max(np.abs(v).max() for v in ledger.values()))), open(OUT + '_%d_cert.json' % FINAL, 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
