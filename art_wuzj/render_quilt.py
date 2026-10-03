"""render_quilt.py — 'Every Square Sums to Nothing': the balanced-ternary bijection Z^2 -> Z
(MO 515677) as a sorbet quilt.  Each patch holds one integer; every integer has exactly one patch;
every tie (a vertex of the grid) closes a 2x2 window whose four numbers sum to 0.
usage: render_quilt.py K S out.png"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
from sorbet import Sheet, PIG, absorb, wheel_tint, text_mask, FONTS
from quilt import phi_grid

K, S, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
I, P = phi_grid(K)
n = 2 * K + 1
W = H = S
cell = 0.80 * S / n
x0 = (W - n * cell) / 2
y0 = 0.075 * S
sh = Sheet(W, H, seed=515677)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
u = (xx - x0) / cell; v = (yy - y0) / cell          # cell coordinates
ci = np.floor(u).astype(int); cj = np.floor(v).astype(int)
inside = (ci >= 0) & (ci < n) & (cj >= 0) & (cj < n)
fu, fv = u - ci, v - cj
cic, cjc = np.clip(ci, 0, n - 1), np.clip(cj, 0, n - 1)
val = P[cjc, cic]
mag = np.log1p(np.abs(val)) / np.log1p(np.abs(P).max())
# pillow: patch density shaped by distance to its seams
e = np.minimum(np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv))
gap = 0.012
pill = np.clip((e - gap) / 0.05, 0, 1) ** 0.6
shade = 0.86 + 0.14 * np.clip(1 - (fu + fv) * 0.6, 0, 1)      # light from the upper left
# --- weave: balanced-ternary digits of each patch's integer as threads ---
from quilt import bt
M = max(len(bt(int(abs(q)))) for q in P.ravel())
ME = (M + 1) // 2                        # number of even / odd digit slots
DIG = np.zeros((n, n, 2 * ME), int)
for jj in range(n):
    for ii in range(n):
        d = bt(int(P[jj, ii]))
        for k, dk in enumerate(d):
            DIG[jj, ii, k] = dk
warm = ['butter', 'peach', 'strawberry', 'bubblegum', 'rose']
cool = ['mint', 'sky', 'periwinkle', 'lilac', 'sky']
pad = 0.07
def band(f, slots):
    """position inside the patch -> slot index (most significant first) and in-thread profile"""
    t = (f - pad) / (1 - 2 * pad) * slots
    k = np.floor(t).astype(int); g = t - k
    prof = np.clip((0.40 - np.abs(g - 0.5)) / 0.05, 0, 1)
    ok = (t >= 0) & (t < slots)
    # geometric slot -> digit rank, centre outward alternating (small numbers keep only the middle threads)
    order = sorted(range(slots), key=lambda q: (abs(q - (slots - 1) / 2), -q))
    rank = np.zeros(slots, int)
    for r_, q in enumerate(order): rank[q] = r_
    return rank[np.clip(k, 0, slots - 1)], prof * ok
kv, pv = band(fu, ME)        # vertical threads <- even digits 0,2,4..
kh, ph = band(fv, ME)        # horizontal threads <- odd digits 1,3,5..
dv = DIG[cjc, cic, 2 * kv]; dh = DIG[cjc, cic, 2 * kh + 1]
Aw = np.stack([absorb(c) for c in warm]); Ac = np.stack([absorb(c) for c in cool])
def thread(dig, k, prof):
    A = np.where((dig > 0)[..., None], Aw[np.minimum(k, 4)], Ac[np.minimum(k, 4)])
    return A * ((dig != 0) * prof)[..., None]
# over/under: a woven checker decides which thread is on top (top thread slightly stronger)
over = ((kv + kh) % 2 == 0)
Tv = thread(dv, kv, pv) * np.where(over, 1.0, 0.7)[..., None]
Th = thread(dh, kh, ph) * np.where(over, 0.7, 1.0)[..., None]
# soft ground tint of the patch by sign
ground = np.where((val > 0)[..., None], absorb('peach'), absorb('sky')) * 0.10 * (val != 0)[..., None]
dens = pill * shade * inside
sh.wash_rgb((Tv + Th) * (1.9 * dens)[..., None] + ground * dens[..., None])
# quilting stitches along the seams: short dashes
seam = np.minimum(np.abs(fu - 0.5 * 0) , 1)  # placeholder
st = np.zeros((H, W), np.float32)
for k in range(n + 1):
    for axis in (0, 1):
        pass
dash = (np.cos(2 * np.pi * (u + v) * 4) > 0.2)
on_v = np.abs(e - 0.03) < 0.008
st = (on_v & dash & inside).astype(np.float32)
sh.wash(gaussian_filter(st, 0.6) * 0.55, 'plum')
# ties at every interior vertex: a coral cross-stitch knot
im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
L = 0.09 * cell; lw = max(1, int(0.022 * cell))
for a in range(1, n):
    for b in range(1, n):
        X, Y = x0 + a * cell, y0 + b * cell
        dr.line([(X - L, Y - L), (X + L, Y + L)], fill=1.0, width=lw)
        dr.line([(X - L, Y + L), (X + L, Y - L)], fill=1.0, width=lw)
tie = gaussian_filter(np.asarray(im, np.float32), 0.5)
sh.lighten(gaussian_filter(tie, 1.5).clip(0, 1), 0.7)
sh.wash(tie * 1.5, 'coral')
# numbers
items = []
for jj in range(n):
    for ii in range(n):
        items.append((f'{P[jj, ii]}'.replace('-', '−'), x0 + (ii + 0.5) * cell, y0 + (jj + 0.53) * cell,
                      (0.13 if abs(P[jj, ii]) < 100 else 0.11) * cell, 'serif', 'mm'))
tm = text_mask(W, H, items)
lab = np.clip((0.15 - np.hypot(fu - 0.5, fv - 0.5)) / 0.02, 0, 1) * inside
sh.lighten(lab, 0.55)
sh.wash(np.clip(1 - np.abs(np.hypot(fu - 0.5, fv - 0.5) - 0.15) / 0.010, 0, 1) * inside * 0.5, 'lilac')
sh.wash(tm * 1.5, 'ink')
# the zero patch: a paper-white patch with a coral ring
zi = zj = K
cz = (x0 + (K + 0.5) * cell, y0 + (K + 0.5) * cell)
rr = np.hypot(xx - cz[0], yy - cz[1]) / cell
sh.wash(np.exp(-((rr - 0.24) / 0.03) ** 2) * 1.6, 'coral')
TITLE = sys.argv[4] if len(sys.argv) > 4 else ''
if TITLE:
    yb = y0 + n * cell + 0.045 * S
    cap = [(TITLE, W / 2, yb, 0.028 * S, 'serif_bold', 'mm'),
           (sys.argv[5], W / 2, yb + 0.036 * S, 0.0165 * S, 'italic', 'mm'),
           (sys.argv[6], W / 2, yb + 0.063 * S, 0.0108 * S, 'mono', 'mm')]
    sh.wash(text_mask(W, H, cap) * 3.4, 'ink')
sh.develop(dmax=1.7, glow=0.10).save(out)
