"""
05 — The Line That Forgets
Carried forward from the 2026-07-04 run's also-ran list: a finite-field
(F_p^2) discrete KAKEYA set, built by greedy overlap-maximizing line
placement. Previously abandoned as "too slow to vectorize well" -- this run
found the vectorization: for a fixed slope m, choosing the best intercept b
over ALL b simultaneously is a single fancy-index gather, not a python loop,
which brings the whole greedy down to a very manageable cost.

A Kakeya set in the plane over the finite field F_p contains one full line in
EVERY one of the p+1 directions of P^1(F_p) (p finite slopes + 1 vertical),
yet Dvir's celebrated 2008 polynomial-method proof shows it can never be much
smaller than the whole plane: |K| >= c_2 * p(p+1)/2, roughly HALF the grid.
Every single direction needs its own witness line, and those p+1 lines are
forced to overlap enormously to keep the union small -- most points end up
belonging to only ONE line (remembering only their own direction); a much
smaller core belongs to many.

We build a genuinely small K greedily: process the p+1 directions one at a
time; for each, place its line wherever it overlaps the ALREADY-COVERED set
the most (a full vectorized search over every possible position, not a
sample). Colour by AGE (which direction's turn first claimed a cell -- deep
violet to gold) and by MULTIPLICITY (how many of the p+1 directions actually
pass through a cell, dimmed to bright -- most of the field is a dim wash
remembering only one direction; a sparse lattice of bright nodes remembers
several at once).
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import time

P = 1013  # prime
assert all(P % d != 0 for d in range(2, int(P**0.5)+1)), "P must be prime"

t0 = time.time()
covered = np.zeros((P, P), dtype=bool)   # [row=y, col=x]
age = np.full((P, P), -1, dtype=np.int32)      # which direction-index first claimed this cell
mult = np.zeros((P, P), dtype=np.int32)        # how many of the p+1 lines pass through

cols = np.arange(P)
rows = np.arange(P)

direction_index = 0
vertical_col = None
slope_b = {}   # m -> chosen intercept b_star, so we can redraw any single line later

# --- vertical direction first: pick the column with the most already-true cells
# (covered is all-False right now, so this just picks column 0 -- still correct
# and cheap; kept general in case the order is changed later).
col_sums = covered.sum(axis=0)
best_c = int(np.argmax(col_sums))
vertical_col = best_c
covered[:, best_c] = True
age[:, best_c] = np.where(age[:, best_c] == -1, direction_index, age[:, best_c])
mult[:, best_c] += 1
direction_index += 1

# --- p finite slopes: for slope m, the candidate line for intercept b visits
# (row=(m*x+b) mod P, col=x) for x=0..P-1. Choose b maximizing overlap with
# `covered`, via ONE vectorized gather over all (b, x) pairs at once.
order = np.arange(P)
for m in order:
    s = (m * cols) % P                      # shape (P,), s[x]
    # R[b, x] = (s[x] + b) mod P  -> gather covered[R[b,x], x]
    R = (s[None, :] + rows[:, None]) % P    # shape (P, P): rows=b, cols=x
    hits = covered[R, cols[None, :]]         # shape (P, P) bool: hits[b, x]
    overlap_count = hits.sum(axis=1)         # shape (P,) -- overlap for each candidate b
    b_star = int(np.argmax(overlap_count))
    slope_b[int(m)] = b_star
    line_rows = (s + b_star) % P
    was_covered = covered[line_rows, cols]
    covered[line_rows, cols] = True
    newly = ~was_covered
    age[line_rows[newly], cols[newly]] = direction_index
    mult[line_rows, cols] += 1
    direction_index += 1
    if m % 200 == 0:
        print(f"slope {m}/{P}, |K| so far = {covered.sum()}, elapsed {time.time()-t0:.1f}s")

# ---------------------------------------------------------------------------
# Most directions, viewed on the raster grid, do NOT look like a line: for a
# generic slope m, x and x+1 land P rows apart in the wrapped y=(mx+b) mod P
# coordinate, so consecutive points are visually uncorrelated -- a perfectly
# deterministic single line renders as scatter. Only slopes near 0 (m small)
# or near "vertical" (m near P, i.e. -1/m near 0) stay visually coherent, plus
# the one true vertical direction. We mark those cells specially so the piece
# can show BOTH truths at once: a hazy near-random background (the many
# directions that forget how to look like a line) and a sparse fan of genuine
# bright diagonal ribbons (the few that still remember).
# ---------------------------------------------------------------------------
COHERENT_THRESH = 22
coherent = np.zeros((P, P), dtype=bool)
coherent[:, vertical_col] = True
for m, b_star in slope_b.items():
    if m <= COHERENT_THRESH or m >= P - COHERENT_THRESH:
        s = (m * cols) % P
        line_rows = (s + b_star) % P
        coherent[line_rows, cols] = True
n_coherent_dirs = 1 + sum(1 for m in slope_b if m <= COHERENT_THRESH or m >= P - COHERENT_THRESH)
print(f"coherent directions (visually a line, |slope|<= {COHERENT_THRESH} or vertical): {n_coherent_dirs} / {direction_index}")

t1 = time.time()
size_K = int(covered.sum())
full = P * P
trivial_lower = P * (P + 1) / 2
print(f"P={P}: |K|={size_K}  ({size_K/full*100:.2f}% of the plane), "
      f"trivial lower bound p(p+1)/2 = {trivial_lower:.0f} ({trivial_lower/full*100:.2f}%), "
      f"build time {t1-t0:.1f}s")
print(f"directions placed: {direction_index} (expected {P+1})")
print(f"multiplicity stats: max={mult.max()}, mean-on-K={mult[covered].mean():.3f}, "
      f"fraction of K with mult==1: {(mult[covered]==1).mean()*100:.1f}%")

# ---------------------------------------------------------------------------
# Render as TWO layers:
#   background = the incoherent majority: covered but NOT part of a coherent
#     line, rasterized NEAREST from the P-grid (blocky, grainy -- an honest
#     scatter, no interpolation on an arithmetic object) -- "the directions
#     that forgot how to be a line"
#   overlay    = the coherent minority: EXPLICITLY DRAWN as connected straight
#     strokes (a coherent line still has huge pixel gaps between consecutive
#     points once |slope|>2-3 -- point-scatter alone doesn't read as a line
#     even for a "coherent" direction; drawing the literal segments between
#     wrap points is what makes them read as a woven fan of threads instead
#     of another patch of noise) -- "the few that still remember"
# ---------------------------------------------------------------------------
CANVAS = 4096
scale = CANVAS / P
mult_f = mult.astype(np.float64)
mult_norm = np.clip(mult_f / 4.0, 0, 1)

incoherent_mask = covered & ~coherent

bg_val = np.where(incoherent_mask, 0.09 + 0.20*mult_norm**0.7, 0.0)
teal = np.array([0.09, 0.30, 0.37])
bg_rgb = bg_val[..., None] * teal[None, None, :]
void = np.array([0.015, 0.015, 0.03])
bg_rgb[~covered] = void

bg_small = Image.fromarray((np.clip(bg_rgb, 0, 1) * 255).astype(np.uint8), 'RGB')
bg_big = bg_small.resize((CANVAS, CANVAS), Image.NEAREST)
bg = np.asarray(bg_big).astype(np.float64) / 255.0

overlay = Image.new('RGB', (CANVAS, CANVAS), (0, 0, 0))
draw = ImageDraw.Draw(overlay)

def hue_for_slope(m):
    # near 0 -> warm gold; toward the threshold edge -> rose/amber
    t = min(m, P - m) / COHERENT_THRESH
    hue = 0.11 + 0.06 * t
    return hue

def hsv_to_rgb255(h, s, v):
    i = int(h * 6.0) % 6
    f = h * 6.0 - int(h * 6.0)
    p_ = v * (1 - s); q = v * (1 - f * s); t_ = v * (1 - (1 - f) * s)
    table = [(v,t_,p_), (q,v,p_), (p_,v,t_), (p_,q,v), (t_,p_,v), (v,p_,q)]
    r, g, b = table[i]
    return (int(r*255), int(g*255), int(b*255))

def draw_wrapped_line(m, b_star, width, color):
    s = (m * np.arange(P)) % P
    ys = (s + b_star) % P
    xs = np.arange(P)
    dy = np.diff(ys.astype(int))
    wrap_pts = np.where(np.abs(dy) > P / 2)[0]
    seg_starts = [0] + list(wrap_pts + 1)
    seg_ends = list(wrap_pts + 1) + [P]
    for s0, s1 in zip(seg_starts, seg_ends):
        if s1 - s0 < 2:
            continue
        pts = [(xs[k]*scale, ys[k]*scale) for k in range(s0, s1)]
        draw.line(pts, fill=color, width=width)

for m, b_star in slope_b.items():
    if m <= COHERENT_THRESH or m >= P - COHERENT_THRESH:
        col = hsv_to_rgb255(hue_for_slope(m), 0.62, 0.95)
        draw_wrapped_line(m, b_star, width=3, color=col)
draw.line([(vertical_col*scale, 0), (vertical_col*scale, CANVAS)],
          fill=hsv_to_rgb255(0.11, 0.62, 1.0), width=3)

ov = np.asarray(overlay).astype(np.float64) / 255.0
rgb = bg + ov

# bloom on the coherent ribbons only (they're the true bright foci)
lum = 0.2126*rgb[...,0]+0.7152*rgb[...,1]+0.0722*rgb[...,2]
mask = np.clip((lum-0.45)/0.55, 0, 1)**2
bsrc = rgb*mask[...,None]
bl1 = gaussian_filter(bsrc, sigma=(2,2,0))
bl2 = gaussian_filter(bsrc, sigma=(9,9,0))
final = rgb + 0.45*bl1 + 0.28*bl2
final = final/(1.0+final)
final = np.clip(final,0,1)**(1/2.2)

out = (final*255).astype(np.uint8)
Image.fromarray(out, 'RGB').save('/home/user/claude-mythos-self-play/art_nifty/05_the_line_that_forgets.png')
print("saved 05, total time", time.time()-t0, "s")
