"""render_phases.py — Nine Phases of a Zeta: value clouds of Z(sigma+it) for a descending ladder
of sigma, one pigment per moon, each in its own cell at a common scale; the origin is marked in
every cell and is swallowed as sigma passes the frontier sigma*.

usage: python3 render_phases.py SIZE NSAMP_PER_CELL OUT
"""
import sys, json, time, os
import numpy as np
from math import log, pi
from scipy.ndimage import gaussian_filter, zoom
from pastel import *
from cloud import sample_cloud

S = int(sys.argv[1]); NS = int(float(sys.argv[2])); OUT = sys.argv[3]
SS = 2; W = H = S * SS; rs = S / 1024.0
SSTAR = round(json.load(open('frontier2_N200.json'))['res']['sigma_star'], 4) if os.path.exists('frontier2_N200.json') else 1.0086
SIGS = [2.0, 1.6, 1.3, 1.1, SSTAR, 0.95, 0.8, 0.7, 0.6]
PIGS = ['aqua', 'mint', 'pistachio', 'lemon', 'coral', 'apricot', 'blush', 'orchid', 'lavender']
RIMS = json.load(open('rims_v2.json')) if os.path.exists('rims_v2.json') else {}

# grid: 3 x 3 cells inside the canvas above the caption
top, bottom = 0.045, 0.875
cell = (bottom - top) / 3 * H
cw = cell
x_left = (W - 3 * cw) / 2
# common value-plane scale: the biggest moon (sigma=0.6) spans about 1 +- 3.3
HALF = 2.75                      # half-width of a cell in value units (centre at z = 1)
def cell_px(ci, z):
    row, col = divmod(ci, 3)
    cx = x_left + (col + 0.5) * cw; cy = top * H + (row + 0.5) * cell
    return cx + (np.real(z) - 1.0) / HALF * (cw / 2), cy - np.imag(z) / HALF * (cell / 2)

sheet = Sheet(W, H, seed=21)
t0 = time.time()
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
for ci, (sg, pig) in enumerate(zip(SIGS, PIGS)):
    row, col = divmod(ci, 3)
    res = int(cw) // 2
    x0, x1 = 1 - HALF, 1 + HALF; y0, y1 = -HALF, HALF
    counts, C = sample_cloud(sg, NS, 2.0e6, res, x0, x1, y0, y1, nterms=110, seed=ci + 1)
    counts = counts[::-1]
    occ = counts[counts > 0]
    ref = np.percentile(occ, 35)
    d = np.log1p(counts / ref) / np.log1p(np.percentile(occ, 99.9) / ref)
    d = np.clip(d, 0, 1.15).astype(np.float32)
    d = zoom(d, 2, order=1)[:int(cell), :int(cw)]
    d = gaussian_filter(d, 0.6 * rs)
    # paste into the canvas
    cx0 = int(x_left + col * cw); cy0 = int(top * H + row * cell)
    D = np.zeros((H, W), np.float32)
    D[cy0:cy0 + d.shape[0], cx0:cx0 + d.shape[1]] = d
    amp = 1.9 if sg >= 1.5 else 1.55
    sheet.wash(D * amp, pig, granulate=0.22, seed=40 + ci)
    sheet.wash(D * 0.12 * amp, 'ink', seed=60 + ci)
    # rim (possible worlds) for this sigma, if we have it
    key = [k for k in RIMS if abs(float(k) - sg) < 1e-6]
    if key:
        pts = np.array(RIMS[key[0]]); z = pts[:, 0] + 1j * pts[:, 1]
        for _ in range(3 if sg >= 0.9 else 12):
            z = (np.roll(z, 1) + 2 * z + np.roll(z, -1)) / 4
        z = np.concatenate([z, z[:1]])
        px, py = cell_px(ci, z)
        dens = polyline_density(W, H, list(zip(px, py)), 1.2 * rs * SS / 2, sigma=0.5 * rs)
        sheet.wash(dens * 0.55, 'ink')
    # origin mark: ring + cross, coral if swallowed (sigma <= sigma*)
    ox, oy = cell_px(ci, 0j)
    rr = np.hypot(xx - ox, yy - oy)
    ring = ink_from_distance(np.abs(rr - 6 * rs), 1.0 * rs)
    cross = np.maximum(ink_from_distance(np.abs(xx - ox), 0.8 * rs) * (np.abs(yy - oy) < 15 * rs),
                       ink_from_distance(np.abs(yy - oy), 0.8 * rs) * (np.abs(xx - ox) < 15 * rs)) * (rr > 7.5 * rs)
    sheet.lighten(np.clip(1 - rr / (4.5 * rs), 0, 1), 0.85)
    swallowed = sg <= SSTAR + 1e-9
    sheet.wash(np.maximum(ring, cross) * 1.0, 'coral' if swallowed else 'ink')
    # the point 1
    ux, uy = cell_px(ci, 1 + 0j)
    sheet.wash(ink_from_distance(np.hypot(xx - ux, yy - uy), 2.2 * rs) * 0.8, 'ink')
    # label
    lab = f'σ* = {sg:.4f}' if abs(sg - SSTAR) < 1e-9 else f'σ = {sg:g}'
    lx, ly = cx0 + 0.06 * cw, cy0 + 0.08 * cell
    sheet.wash(text_density(W, H, [(lab, lx, ly, int(19 * rs), 'italic', 'lm')]) * (1.0 if swallowed else 0.85),
               'coral' if swallowed else 'ink')
    reach = np.exp(-sg * np.array([log(x) for x in __import__('zeta_g').gseq(400)[1:]])).sum()
    sub = f'Σ|terms| = {reach:.3f}'
    sheet.wash(text_density(W, H, [(sub, lx, ly + 24 * rs, int(13 * rs), 'italic', 'lm')]) * 0.7, 'ink')
    print(f'cell {ci}: sigma {sg}  max count {counts.max():.0f}  ({time.time()-t0:.0f}s)'); sys.stdout.flush()
del xx, yy

sheet.caption_strip(0.895, 0.985, f=0.62)
title = 'Nine Phases of a Zeta'
sub = (f'the values of Z(σ+it) on nine vertical lines, drawn where the line actually goes (t up to 2·10⁶), the ink loop around each '
       f'is the farthest any possible world reaches; the moon waxes as σ falls and swallows the origin at σ* ≈ {SSTAR}: '
       f'below that line Z has zeros, above it none — the triangle inequality only promises this from 1.073')
items = [(title, W * 0.5, H * 0.922, int(38 * rs), 'serif_bold', 'mm')]
words = sub.split(); lines = []; cur = ''
for w_ in words:
    trial = (cur + ' ' + w_).strip()
    if text_width(trial, int(15 * rs), 'italic') > W * 0.78:
        lines.append(cur); cur = w_
    else:
        cur = trial
lines.append(cur)
for i, ln in enumerate(lines):
    items.append((ln, W * 0.5, H * (0.950 + 0.018 * i), int(15 * rs), 'italic', 'mm'))
sheet.wash(text_density(W, H, items) * 0.95, 'ink')
img = sheet.develop(dmax=2.4)
finish(img, (S, S), OUT)
print('total', round(time.time() - t0), 's')
