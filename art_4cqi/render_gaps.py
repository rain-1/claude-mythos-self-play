"""render_gaps.py — WHOSE GAP COMES NEXT: the field of consecutive prime-gap pairs (g_n, g_{n+1}) for the primes
below 10^9, drawn as a loom.  Warp threads: one per gap size g (horizontal), weight = how common the gap is; weft
threads: one per next gap g'.  At every crossing a knot: size by the number of pairs, pigment by the LEAN — warm
where the pair occurs more often than independence predicts, cool where less.  Coral: the conditional mean
E[g' | g], which falls as g grows (the negative lag-one correlation, r = -0.028); ink: the unconditional mean.
    python3 render_gaps.py FINAL GMAX
"""
import sys, json, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from pastel import *
FINAL = int(sys.argv[1]); GY = int(sys.argv[2]) if len(sys.argv) > 2 else 120; GX = int(sys.argv[3]) if len(sys.argv) > 3 else 48
SS = 2; W = FINAL * SS; H = int(W * 1.6); rs = FINAL / 1024 * SS
d = np.load('cache/gaps_pairs.npz'); pair = d['pair'].astype(np.float64); marg = d['marg'].astype(np.float64); cm = d['cm']; corr = float(d['corr'])
K = pair.shape[0]
tot = pair.sum()
ind = np.outer(pair.sum(1), pair.sum(0)) / tot          # independence prediction
ratio = np.where(pair > 0, pair / np.maximum(ind, 1e-9), 1.0)
lean = np.log(ratio)
gys = [1] + list(range(2, GY + 1, 2)); gxs = [1] + list(range(2, GX + 1, 2))
mx = 0.11; my = 0.06; spanx = (1 - 2 * mx) * W; spany = (0.90 - my) * H
def X(gp): return mx * W + (gp - 1) / (GX - 1) * spanx          # next gap along x
def Y(g): return 0.90 * H - (g - 1) / (GY - 1) * spany        # this gap along y (up = larger)
sheet = Sheet(W, H, seed=71)
# threads
thr = Image.new('F', (W, H), 0.0); td = ImageDraw.Draw(thr)
mmax = marg[2:GY + 1].max()
for g in gys:
    wgt = 0.08 + 0.42 * (marg[g] / mmax) ** 0.5
    td.line([(mx * W, Y(g)), ((1 - mx) * W, Y(g))], fill=float(wgt), width=int(round(1.0 * rs)))
for g in gxs:
    wgt = 0.08 + 0.42 * (marg[g] / mmax) ** 0.5
    td.line([(X(g), 0.90 * H), (X(g), my * H)], fill=float(wgt), width=int(round(1.0 * rs)))
sheet.wash(gaussian_filter(np.asarray(thr, np.float32), 0.4 * rs), 'ink')
# knots
warm = ['lemon', 'apricot', 'blush']; cool = ['mint', 'aqua', 'lavender']
lay = {p: Image.new('F', (W, H), 0.0) for p in warm + cool}
dr = {p: ImageDraw.Draw(lay[p]) for p in lay}
pmax = np.log(pair[2:GY + 1, 2:GX + 1].max())
colsp = spanx / (len(gxs) - 1)
for g in gys:
    for gp in gxs:
        c = pair[g, gp]
        if c < 1: continue
        r = 0.5 * colsp * max(0.08, np.log(c) / pmax) ** 1.3
        L = lean[g, gp]
        fam = warm if L > 0 else cool
        z = abs(L) * np.sqrt(c)
        t = np.clip(z / 12, 0, 1) * np.clip(abs(L) / 0.25, 0, 1) ** 0.5   # significance x size of the lean
        h = t * (len(fam) - 1); i0 = int(np.floor(h)); i1 = min(i0 + 1, len(fam) - 1); fr = h - i0
        dens = 0.35 + 0.6 * t
        for p, wgt in ((fam[i0], 1 - fr), (fam[i1], fr)):
            if wgt > 0.02:
                dr[p].ellipse([X(gp) - r, Y(g) - r, X(gp) + r, Y(g) + r], fill=float(dens * wgt))
for p in lay:
    sheet.wash(gaussian_filter(np.asarray(lay[p], np.float32), 0.7 * rs), p, granulate=0.08, seed=hash(p) % 100)
# means
mean_gap = float((marg * np.arange(K)).sum() / marg.sum())
ink = Image.new('F', (W, H), 0.0); idr = ImageDraw.Draw(ink)
idr.line([(X(mean_gap), 0.90 * H), (X(mean_gap), my * H)], fill=0.9, width=int(round(1.6 * rs)))
sheet.wash(gaussian_filter(np.asarray(ink, np.float32), 0.4 * rs), 'ink')
cor = Image.new('F', (W, H), 0.0); cdr = ImageDraw.Draw(cor)
pts = [(X(cm[g]), Y(g)) for g in gys if pair[g].sum() >= 200]
cdr.line(pts, fill=1.0, width=int(round(3.0 * rs)), joint='curve')
for x_, y_ in pts:
    cdr.ellipse([x_ - 3.5 * rs, y_ - 3.5 * rs, x_ + 3.5 * rs, y_ + 3.5 * rs], fill=1.0)
sheet.wash(gaussian_filter(np.asarray(cor, np.float32), 0.6 * rs), 'coral')
# axes text
items = []
for g in [2, 6, 12, 20, 30, 40, 60, 80, 100, 120]:
    if g <= GY: items.append((str(g), mx * W - 10 * rs, Y(g), 13 * rs, 'italic', 'rm'))
    if g <= GX: items.append((str(g), X(g), 0.90 * H + 10 * rs, 13 * rs, 'italic', 'ma'))
items.append(('this gap', mx * W - 10 * rs, my * H - 14 * rs, 13 * rs, 'italic', 'rd'))
items.append(('next gap', (1 - mx) * W, 0.90 * H + 26 * rs, 13 * rs, 'italic', 'ra'))
items.append((f'mean gap {mean_gap:.1f}', X(mean_gap) + 6 * rs, my * H - 4 * rs, 13 * rs, 'italic', 'ld'))
sheet.wash(text_density(W, H, items) * 0.9, 'ink')
sheet.caption_strip(0.935, 0.99, 0.5)
title = 'Whose Gap Comes Next'
sub = (f'Every pair of consecutive prime gaps below 10⁹ ({int(tot):,} pairs) as a loom: a knot at (this gap, next gap), sized by how often, '
       'warm where the pair is more common than independence would predict, cool where less. The coral thread is the mean next gap given this one — '
       f'it leans left as this gap grows (correlation −{-corr:.3f}): a long silence tends to be followed by a shorter one.')
lines_ = wrap(sub, 17 * rs, 'italic', 0.88 * W)
items = [(title, W / 2, 0.950 * H, 36 * rs, 'serif_bold', 'mm')] + [(ln, W / 2, (0.966 + 0.011 * i) * H, 17 * rs, 'italic', 'mm') for i, ln in enumerate(lines_)]
sheet.wash(text_density(W, H, items), 'ink')
img = sheet.develop()
out = f'cache/gaps_{FINAL}.png' if FINAL < 2048 else f'gaps_{FINAL}.png'
finish(img, (FINAL, int(FINAL * 1.6)), out)
