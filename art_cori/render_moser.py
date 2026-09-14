"""render_moser.py — WHAT LOOKS LIKE POWERS OF TWO.
n points on a circle, every chord drawn; the regions they cut are pastel cells tinted by their number of sides.
The seduction: 1, 2, 4, 8, 16 regions for n = 1..5 — and 31 for n = 6 (the formula is 1 + C(n,2) + C(n,4)).
A strip at the bottom shows the six small circles with their counts; coral marks the 31st region.

usage: python3 render_moser.py FINAL n out_prefix [jitter]
"""
import sys, json, time
import numpy as np
from math import comb
from scipy.ndimage import label, distance_transform_edt, gaussian_filter
from PIL import Image, ImageDraw
import pastel as P

FINAL = int(sys.argv[1]); NPTS = int(sys.argv[2]); OUT = sys.argv[3]
JIT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
SS = 2; W = H = FINAL * SS; rs = FINAL / 1024.0 * SS
t0 = time.time()
rng = np.random.default_rng(1)

SIDE_PIG = {3: 'apricot', 4: 'aqua', 5: 'lavender', 6: 'mint', 7: 'blush', 8: 'lemon', 9: 'pistachio', 10: 'cornflower', 11: 'orchid'}

def chord_regions(cx, cy, R, n, Wc, Hc, width, jitter=0.0, phase=0.0):
    """rasterise all chords of n circle points; return (labels, nreg, sides per region, chord segs, pts)"""
    ang = phase + 2 * np.pi * np.arange(n) / n + jitter * rng.uniform(-1, 1, n) * 2 * np.pi / n
    pts = np.stack([cx + R * np.cos(ang), cy + R * np.sin(ang)], -1)
    im = Image.new('I', (Wc, Hc), 0); dr = ImageDraw.Draw(im)
    segs = []; cid = 0
    for i in range(n):
        for j in range(i + 1, n):
            cid += 1
            dr.line([tuple(pts[i]), tuple(pts[j])], fill=cid, width=int(max(1, round(width))))
            segs.append((pts[i][0], pts[i][1], pts[j][0], pts[j][1]))
    # the circle itself as chord id 0 boundary (outside = -1)
    yy, xx = np.mgrid[:Hc, :Wc]
    inside = np.hypot(xx - cx, yy - cy) < R
    chords = np.asarray(im)
    free = inside & (chords == 0)
    lab, nreg = label(free)
    # drop raster slivers (< 3 px^2) into the walls so they are neither counted nor tinted
    ar = np.bincount(lab.ravel(), minlength=nreg + 1)
    small = ar < 3; small[0] = False
    lab[small[lab]] = 0
    keep = np.unique(lab); remap = np.zeros(nreg + 1, np.int64); remap[keep] = np.arange(len(keep))
    lab = remap[lab]; nreg = len(keep) - 1
    # sides: distinct chord ids (plus the arc) adjacent to each region
    ncho = cid + 1
    keys = []
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a = lab[max(0, dy):Hc + min(0, dy), max(0, dx):Wc + min(0, dx)]
        b = chords[max(0, -dy):Hc + min(0, -dy), max(0, -dx):Wc + min(0, -dx)]
        arc = ~inside[max(0, -dy):Hc + min(0, -dy), max(0, -dx):Wc + min(0, -dx)]
        m = (a > 0) & ((b > 0) | arc)
        keys.append((a[m].astype(np.int64) * ncho + np.where(arc[m], 0, b[m])))
    keys = np.unique(np.concatenate(keys))
    regs = keys // ncho
    sides = np.bincount(regs, minlength=nreg + 1)
    return lab, nreg, sides, np.array(segs), pts

sheet = P.Sheet(W, H, seed=5)
cx, cy, R = W / 2, 0.405 * H, 0.372 * H
lab, nreg, sides, segs, pts = chord_regions(cx, cy, R, NPTS, W, H, 1.0, JIT)
print('n', NPTS, 'regions', nreg, 'formula', 1 + comb(NPTS, 2) + comb(NPTS, 4), 'sides hist', np.bincount(sides)[:14], '[%.0fs]' % (time.time() - t0), flush=True)
areas = np.bincount(lab.ravel(), minlength=nreg + 1)
# exact region count for the regular polygon by Euler: 1 + C(n,2) + sum over interior points of (k_p - 1),
# k_p = number of chords through p; points found by intersecting all chord pairs and clustering (tol 1e-9 R)
def exact_regions(n):
    ang = 2 * np.pi * np.arange(n) / n; px, py = np.cos(ang), np.sin(ang)
    P_ = []
    import itertools
    for (i, j, k, l) in itertools.combinations(range(n), 4):
        # chords (i,k) and (j,l) cross (alternating order on the circle)
        x1, y1, x2, y2 = px[i], py[i], px[k], py[k]; x3, y3, x4, y4 = px[j], py[j], px[l], py[l]
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        P_.append((x1 + t * (x2 - x1), y1 + t * (y2 - y1)))
    P_ = np.array(P_); key = np.round(P_ / 1e-9).astype(np.int64)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    # a point where k chords meet is counted C(k,2) times: solve C(k,2) = cnt
    k = np.round((1 + np.sqrt(1 + 8 * cnt)) / 2).astype(int)
    return 1 + comb(n, 2) + int((k - 1).sum()), int(len(cnt)), int((k > 2).sum())
ex_reg, n_pts, n_multi = exact_regions(NPTS)
print('exact regions (Euler over clustered crossings)', ex_reg, 'interior points', n_pts, 'of which multiple', n_multi, flush=True)
# pastel cells: pooling toward the cell walls, density by pigment class
edt = distance_transform_edt(lab > 0)
pool = 0.55 + 0.75 * np.exp(-edt / (2.4 * rs))
for s_, pig in SIDE_PIG.items():
    m = (sides == s_) if s_ < 11 else (sides >= 11)
    mask = m[lab] & (lab > 0)
    if mask.any():
        sheet.wash(mask * pool * 0.85, pig, granulate=0.08, seed=s_)
# chords in ink, thin
ink = P.draw_lines_density(W, H, segs, 0.5 * rs, sigma=0.35 * rs)
sheet.wash(0.55 * np.clip(ink, 0, 1), 'ink')
yy, xx = np.mgrid[:H, :W]
rim = np.exp(-((np.hypot(xx - cx, yy - cy) - R) / (0.8 * rs)) ** 2)
sheet.wash(0.7 * rim, 'ink')
print('mandala painted [%.0fs]' % (time.time() - t0), flush=True)

# ---- the strip: n = 1..7 ----
strip_y = 0.845 * H; r_s = 0.032 * H; xs = np.linspace(0.12, 0.88, 7) * W
counts = []
for k, n in enumerate(range(1, 8)):
    x0 = xs[k]
    if n == 1:
        lab_s, nr, sd, sg, pp = None, 1, None, np.zeros((0, 4)), np.array([[x0 + r_s, strip_y]])
    else:
        lab_s, nr, sd, sg, pp = chord_regions(x0, strip_y, r_s, n, W, H, 1.0, 0.35, phase=-np.pi / 2 + 0.4)
        nr = 1 + comb(n, 2) + comb(n, 4)
    counts.append(int(nr))
    disc = (np.hypot(xx - x0, yy - strip_y) < r_s).astype(np.float32)
    if lab_s is not None:
        edt_s = distance_transform_edt(lab_s > 0)
        pool_s = 0.62 + 0.55 * np.exp(-edt_s / (2.2 * rs))
        sheet.wash(0.55 * (lab_s > 0) * pool_s, 'coral' if n == 6 else 'aqua', granulate=0.05)
        if len(sg):
            sheet.wash(0.6 * np.clip(P.draw_lines_density(W, H, sg, 0.5 * rs, sigma=0.35 * rs), 0, 1), 'ink')
    else:
        sheet.wash(0.45 * disc, 'aqua')
    sheet.wash(0.7 * np.exp(-((np.hypot(xx - x0, yy - strip_y) - r_s) / (0.8 * rs)) ** 2), 'ink')
    sheet.wash(0.9 * P.text_density(W, H, [(str(nr), x0, strip_y + r_s + 0.012 * H, int(0.016 * H), 'serif_bold' if n == 6 else 'serif', 'ma')]),
               'coral' if n == 6 else 'ink')
print('strip', counts, '[%.0fs]' % (time.time() - t0), flush=True)

title = 'What Looks Like Powers of Two'
sub = (f'{NPTS} points on a circle, every chord drawn: {ex_reg:,} regions, each tinted by its number of sides. Below, the count for one to seven '
       'points in general position — it doubles five times and then does not. The rule was never doubling; it was 1 + C(n,2) + C(n,4). '
       'The regular polygon above loses a few regions where chords meet three at a time.')
fs_t = int(0.036 * H); fs_s = int(0.0125 * H)
items = [(title, 0.05 * W, 0.958 * H, fs_t, 'serif_bold', 'ls')]
for j_, line in enumerate(P.wrap(sub, fs_s, 'italic', 0.90 * W)):
    items.append((line, 0.05 * W, (0.976 + 0.016 * j_) * H, fs_s, 'italic', 'ls'))
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')
json.dump(dict(n=NPTS, regions_raster=int(nreg), regions_exact=ex_reg, interior_points=n_pts, multiple_points=n_multi, formula=1 + comb(NPTS, 2) + comb(NPTS, 4), sides_hist=np.bincount(sides).tolist(), strip_counts=counts,
               seconds=time.time() - t0), open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
