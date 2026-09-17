"""drawers.py — FIVE DRAWERS: every partition of 24 sorted by Dyson's rank (largest part minus number of parts)
modulo 5.  Ramanujan: p(5n+4) ≡ 0 (mod 5); Dyson (1944) guessed the rank sorts them into five equal drawers,
Atkin–Swinnerton-Dyer proved it (1954).  Ferrers diagrams shelf-packed in five drawers, one pigment per drawer;
coral outline = the self-conjugate partitions (rank 0, their own mirror).
    python3 drawers.py FINAL
"""
import sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from pastel import *

def partitions(n, maxpart=None):
    if maxpart is None: maxpart = n
    if n == 0:
        yield (); return
    for k in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - k, k):
            yield (k,) + rest

n = 24
parts = list(partitions(n))
assert len(parts) == 1575
rank = np.array([p[0] - len(p) for p in parts])
cls = rank % 5
counts = np.bincount(cls, minlength=5)
def conj(p):
    return tuple(sum(1 for x in p if x > i) for i in range(p[0]))
selfconj = np.array([conj(p) == p for p in parts])
print('drawers', counts.tolist(), 'self-conjugate', int(selfconj.sum()), 'ranks', rank.min(), rank.max())
json.dump(dict(n=n, p_n=len(parts), drawers=counts.tolist(), self_conjugate=int(selfconj.sum()),
               rank_range=[int(rank.min()), int(rank.max())],
               rank_hist={int(r): int(c) for r, c in zip(*np.unique(rank, return_counts=True))}), open('cert_drawers.json', 'w'), indent=1)

FINAL = int(sys.argv[1]); SS = 2; W = H = FINAL * SS; rs = FINAL / 1024 * SS
PIGS = ['lemon', 'apricot', 'blush', 'lavender', 'aqua']
mx = 0.05; top = 0.055; bottom = 0.895
DW = (1 - 2 * mx) * W
# shelf packing in cell units; find the unit u so that the five drawers fill the height
def pack(u, gap_cells=1.0):
    layouts = []; total_h = 0
    for k in range(5):
        idx = [i for i in range(len(parts)) if cls[i] == k]
        idx.sort(key=lambda i: (-len(parts[i]), rank[i], parts[i]))
        x = 0; line = 0; lines = [[]]; hmax = [0]
        for i in idx:
            wcell = parts[i][0]; hcell = len(parts[i])
            if (x + wcell) * u > DW and lines[-1]:
                lines.append([]); hmax.append(0); x = 0
            lines[-1].append((i, x)); hmax[-1] = max(hmax[-1], hcell); x += wcell + gap_cells
        layouts.append((lines, hmax))
        total_h += sum((h + gap_cells) for h in hmax) * u
    return layouts, total_h
avail = (bottom - top) * H - 5 * 0.03 * H
lo, hi = 1.0 * rs, 12.0 * rs
for _ in range(30):                       # bisection on the unit: largest u whose packing fits the height
    u = (lo + hi) / 2
    layouts, th = pack(u)
    if th > avail: hi = u
    else: lo = u
u = lo; layouts, th = pack(u)
print('unit', u / rs, 'total height fraction', th / H)
sheet = Sheet(W, H, seed=61)
layers = {p: Image.new('F', (W, H), 0.0) for p in PIGS}
draws = {p: ImageDraw.Draw(layers[p]) for p in PIGS}
coral = Image.new('F', (W, H), 0.0); cd = ImageDraw.Draw(coral)
ink_items = []
y = top * H
inkim = Image.new('F', (W, H), 0.0); idr = ImageDraw.Draw(inkim)
for k in range(5):
    lines, hmax = layouts[k]
    y_dr0 = y
    for line, hm in zip(lines, hmax):
        for i, x in line:
            p = parts[i]
            x0 = mx * W + x * u
            dens = 0.72 + 0.28 * abs(rank[i]) / 23
            for row, w_ in enumerate(p):
                for col in range(w_):
                    cx0 = x0 + col * u; cy0 = y + row * u
                    draws[PIGS[k]].rectangle([cx0 + 0.12 * u, cy0 + 0.12 * u, cx0 + 0.88 * u, cy0 + 0.88 * u], fill=dens)
            if selfconj[i]:
                # coral outline around the diagram's staircase
                pts = [(x0, y)]
                for row, w_ in enumerate(p):
                    pts += [(x0 + w_ * u, y + row * u), (x0 + w_ * u, y + (row + 1) * u)]
                pts += [(x0, y + len(p) * u), (x0, y)]
                cd.line(pts, fill=1.0, width=int(round(1.2 * rs)))
        y += (hm + 1.6) * u
    # drawer rule + label
    idr.line([(mx * W, y - 0.5 * u), ((1 - mx) * W, y - 0.5 * u)], fill=0.6, width=int(round(1.0 * rs)))
    ink_items.append((f'rank ≡ {k} (mod 5)   ·   {counts[k]} partitions', mx * W, y - 0.55 * u - 4 * rs, 13 * rs, 'italic', 'ld'))
    y += 0.03 * H
for p in PIGS:
    sheet.wash(gaussian_filter(np.asarray(layers[p], np.float32), 0.35 * rs), p, granulate=0.08, seed=PIGS.index(p) + 2)
sheet.wash(gaussian_filter(np.asarray(coral, np.float32), 0.4 * rs) * 0.95, 'coral')
sheet.wash(np.asarray(inkim, np.float32), 'ink')
sheet.wash(text_density(W, H, ink_items) * 0.9, 'ink')
sheet.caption_strip(0.915, 0.985, 0.5)
title = 'Five Drawers'
sub = ('All 1,575 partitions of 24 as Ferrers diagrams, sorted into drawers by Dyson\'s rank — largest part minus number of parts — modulo 5. '
       'Ramanujan proved p(5n+4) is divisible by 5; Dyson guessed in 1944 that the rank explains it, five drawers of 315; Atkin and Swinnerton-Dyer proved it in 1954. '
       'Coral: the self-conjugate partitions, each its own mirror.')
lines_ = wrap(sub, 18 * rs, 'italic', 0.86 * W)
items = [(title, W / 2, 0.933 * H, 40 * rs, 'serif_bold', 'mm')] + [(ln, W / 2, (0.957 + 0.016 * i) * H, 18 * rs, 'italic', 'mm') for i, ln in enumerate(lines_)]
sheet.wash(text_density(W, H, items), 'ink')
img = sheet.develop()
out = f'cache/drawers_{FINAL}.png' if FINAL < 2048 else f'drawers_{FINAL}.png'
finish(img, (FINAL, FINAL), out)
