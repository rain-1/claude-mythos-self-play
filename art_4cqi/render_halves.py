"""render_halves.py — TWO HALVES, ONE SHAPE: every convex polyomino of area A on one sheet.  The ones that can be
cut into two congruent halves are filled — lavender when the halves are carried onto each other by a half-turn,
mint by a reflection, apricot by a translation (or a quarter-turn) — with the cut in coral; the ones that cannot
be cut are left whole, as pale ink outlines.  The single shape that can only be halved into NON-convex pieces is
filled coral and shown again, magnified, in the inset.
    python3 render_halves.py A FINAL
"""
import sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from pastel import *
A = int(sys.argv[1]); FINAL = int(sys.argv[2]); SS = 2; W = H = FINAL * SS; rs = FINAL / 1024 * SS
d = json.load(open(f'cache/halves_{A}.json'))
polys = d['polys']
def bbox(cells):
    ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
    return max(ys) + 1, max(xs) + 1
def kind(p):
    if not p['best']: return 'none'
    if not p['any_convex']: return 'special'
    s = p['best']['sym']
    if s == 'rotation 180': return 'turn'
    if s.startswith('reflection'): return 'mirror'
    return 'slide'
PIG = dict(turn='lavender', mirror='mint', slide='apricot', special='blush')
kinds = [kind(p) for p in polys]
from collections import Counter
cnt = Counter(kinds); print(cnt)
# order: specials first, then cuttable by kind, then uncuttable; within, by height then width
order = sorted(range(len(polys)), key=lambda i: (-bbox(polys[i]['cells'])[0], -bbox(polys[i]['cells'])[1], polys[i]['cells']))
INSETS = [int(a) for a in sys.argv[3].split(',')] if len(sys.argv) > 3 else []
mx = 0.045; top = 0.05; bottom = 0.90 - 0.11 * len(INSETS)
DW = (1 - 2 * mx) * W
def pack(u, gap=1.2):
    x = 0; lines = [[]]; hmax = [0]
    for i in order:
        h, w = bbox(polys[i]['cells'])
        if (x + w) * u > DW and lines[-1]:
            lines.append([]); hmax.append(0); x = 0
        lines[-1].append((i, x)); hmax[-1] = max(hmax[-1], h); x += w + gap
    return lines, hmax, sum((h + gap) for h in hmax) * u
lo, hi = 0.5 * rs, 30 * rs
for _ in range(30):
    u = (lo + hi) / 2
    lines, hmax, th = pack(u)
    if th > (bottom - top) * H: hi = u
    else: lo = u
u = lo; lines, hmax, th = pack(u)
print('unit', u / rs, 'height frac', th / H, 'lines', len(lines))
sheet = Sheet(W, H, seed=83)
lay = {p: Image.new('F', (W, H), 0.0) for p in set(PIG.values())}
dr = {p: ImageDraw.Draw(lay[p]) for p in lay}
inkim = Image.new('F', (W, H), 0.0); idr = ImageDraw.Draw(inkim)
cutim = Image.new('F', (W, H), 0.0); cdr = ImageDraw.Draw(cutim)
def draw_poly(i, x0, y0, u, inset=False):
    p = polys[i]; k = kinds[i]; cells = set(map(tuple, p['cells']))
    g = 0.08 * u
    for (cy, cx) in cells:
        box = [x0 + cx * u + g, y0 + cy * u + g, x0 + (cx + 1) * u - g, y0 + (cy + 1) * u - g]
        if k == 'none':
            idr.rectangle(box, outline=0.55, width=max(1, int(round(0.6 * rs))))
        else:
            dr[PIG[k]].rectangle(box, fill=0.85)
    # outline of the whole shape (unit edges with exactly one side inside)
    def edges(cs):
        E = []
        for (cy, cx) in cs:
            for (ny, nx, e) in (((cy - 1, cx), 0, ((cx, cy), (cx + 1, cy))), ((cy + 1, cx), 0, ((cx, cy + 1), (cx + 1, cy + 1))),
                                ((cy, cx - 1), 0, ((cx, cy), (cx, cy + 1))), ((cy, cx + 1), 0, ((cx + 1, cy), (cx + 1, cy + 1)))):
                if (ny, nx) not in cs:
                    E.append(e)
        return E
    if k != 'none':
        wd = max(1, int(round((1.6 if inset else 0.8) * rs)))
        for (a, b) in edges(cells):
            idr.line([(x0 + a[0] * u, y0 + a[1] * u), (x0 + b[0] * u, y0 + b[1] * u)], fill=0.8, width=wd)
        S = set(map(tuple, p['best']['half']))
        # the cut: unit edges between S and its complement
        wd = max(1, int(round((3.0 if inset else 1.6) * rs)))
        for (cy, cx) in S:
            for (ny, nx, e) in (((cy - 1, cx), 0, ((cx, cy), (cx + 1, cy))), ((cy + 1, cx), 0, ((cx, cy + 1), (cx + 1, cy + 1))),
                                ((cy, cx - 1), 0, ((cx, cy), (cx, cy + 1))), ((cy, cx + 1), 0, ((cx + 1, cy), (cx + 1, cy + 1)))):
                if (ny, nx) in cells and (ny, nx) not in S:
                    cdr.line([(x0 + e[0][0] * u, y0 + e[0][1] * u), (x0 + e[1][0] * u, y0 + e[1][1] * u)], fill=1.0, width=wd)
y = top * H
for line, hm in zip(lines, hmax):
    for i, x in line:
        draw_poly(i, mx * W + x * u, y, u)
    y += (hm + 1.2) * u
specials = [i for i in range(len(polys)) if kinds[i] == 'special']
# inset strip: the exceptional shapes of another area (cache/halves_<INSET>.json), magnified, with a rule above
inset_items = []
if INSETS:
    idr.line([(mx * W, (bottom + 0.02) * H), ((1 - mx) * W, (bottom + 0.02) * H)], fill=0.6, width=int(round(1.0 * rs)))
    saved = polys, kinds
    for row, AI in enumerate(INSETS):
        d2 = json.load(open(f'cache/halves_{AI}.json'))
        ex = [p for p in d2['polys'] if p['best'] and not p['any_convex']]
        ui = 8.5 * rs
        xi = mx * W + 4 * rs; yi = (bottom + 0.045 + 0.11 * row) * H
        for p in ex:
            polys = polys + [p]; kinds = kinds + ['special']
            draw_poly(len(polys) - 1, xi, yi, ui, inset=True)
            h, w = bbox(p['cells'])
            xi += (w + 2.0) * ui
        ntxt = (f'Area {AI}: of {d2["n"]:,} convex polyominoes, {d2["cuttable"]:,} can be halved into congruent pieces, and '
                f'{"only this one" if len(ex) == 1 else "only these " + str(len(ex))} must be halved into pieces that are not themselves convex'
                + (' — the polyomino case of the phenomenon MO 515286 asks about.' if row == 0 else '.'))
        inset_lines = wrap(ntxt, 16 * rs, 'italic', (1 - mx) * W - xi - 10 * rs)
        inset_items += [(ln, xi + 8 * rs, yi + 2 * rs + j * 21 * rs, 16 * rs, 'italic', 'la') for j, ln in enumerate(inset_lines)]
    polys, kinds = saved
for p in lay:
    sheet.wash(gaussian_filter(np.asarray(lay[p], np.float32), 0.35 * rs), p, granulate=0.08, seed=hash(p) % 50)
sheet.wash(gaussian_filter(np.asarray(inkim, np.float32), 0.3 * rs), 'ink')
sheet.wash(gaussian_filter(np.asarray(cutim, np.float32), 0.4 * rs), 'coral')
sheet.caption_strip(0.915, 0.985, 0.5)
title = 'Two Halves, One Shape'
n = len(polys); nc = sum(1 for k in kinds if k != 'none')
sub = (f'All {n:,} convex polyominoes of area {A}. The {nc} that can be cut into two congruent halves are filled — lavender for a half-turn, mint for a mirror, apricot for a slide — with the cut in coral; '
       f'the {n - nc:,} that cannot are left whole' + (f'. Blush: the {len(specials)} whose congruent halves must both be non-convex.' if specials else '.'))
lines_ = wrap(sub, 18 * rs, 'italic', 0.88 * W)
items = [(title, W / 2, 0.933 * H, 40 * rs, 'serif_bold', 'mm')] + [(ln, W / 2, (0.957 + 0.016 * i) * H, 18 * rs, 'italic', 'mm') for i, ln in enumerate(lines_)]
sheet.wash(text_density(W, H, items + inset_items), 'ink')
img = sheet.develop()
out = f'cache/halves_{A}_{FINAL}.png' if FINAL < 2048 else f'halves_{FINAL}.png'
finish(img, (FINAL, FINAL), out)
json.dump(dict(A=A, counts=dict(cnt), specials=[polys[i] for i in specials]), open(f'cert_halves_{A}.json', 'w'), indent=1)
