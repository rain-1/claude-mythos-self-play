# render_walk.py — the easily bored sequence (MO 377105) walked on the triangular lattice:
# digit 1 = turn +120 deg, digit 0 = turn -120 deg, then step.  No 000/111 in the sequence <=> the turtle never
# walks once round a single small triangle.  Colour = time along the walk (sorbet wheel); revisits glaze darker.
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from sorbet import Sheet, PIG, absorb, wheel_tint, text_mask, text_w, discs
W = int(sys.argv[1]); out = sys.argv[2]; n = int(sys.argv[3]); H = int(W * float(sys.argv[4])) if len(sys.argv) > 4 else W
rot = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
b = np.fromfile(sys.argv[6] if len(sys.argv) > 6 else 'bored.bin', np.uint8)[:n].astype(int)
t = np.cumsum(np.where(b == 1, 1, -1)) * (2 * np.pi / 3)
z = np.concatenate([[0], np.cumsum(np.exp(1j * t))]) * np.exp(1j * rot)
# fit into the frame (leave caption room at the bottom)
fx0, fx1, fy0, fy1 = [float(v) for v in __import__('os').environ.get('FRAME', '0.06,0.94,0.05,0.80').split(',')]
fx0, fx1, fy0, fy1 = fx0 * W, fx1 * W, fy0 * H, fy1 * H
xr, yr = z.real, -z.imag
s = min((fx1 - fx0) / np.ptp(xr), (fy1 - fy0) / np.ptp(yr))
X = fx0 + (fx1 - fx0 - s * np.ptp(xr)) / 2 + (xr - xr.min()) * s
Y = fy0 + (fy1 - fy0 - s * np.ptp(yr)) / 2 + (yr - yr.min()) * s
print('edge px', s)
SS = 2
sh = Sheet(W, H, seed=33)
NC = 72
GR = ['coral', 'strawberry', 'bubblegum', 'lilac', 'periwinkle', 'sky', 'mint']
def grad(t):
    t = np.clip(t, 0, 0.9999) * (len(GR) - 1); i = int(t); f = t - i
    a, c_ = np.array(PIG[GR[i]]), np.array(PIG[GR[i + 1]])
    return tuple(a ** (1 - f) * c_ ** f)
lw = max(1.0, s * float(__import__("os").environ.get("LWF", "0.62")))
def poly_layer(segs, width, dx=0.0, dy=0.0):
    im = Image.new('F', (W * SS, H * SS), 0.0); dr = ImageDraw.Draw(im)
    for (a, c) in segs:
        pts = [((X[i] + dx) * SS, (Y[i] + dy) * SS) for i in range(a, c + 1)]
        # draw each edge separately so revisits ADD (glaze)
        for p, q in zip(pts[:-1], pts[1:]):
            dr.line([p, q], fill=1.0, width=max(1, int(round(width * SS))))
    return np.asarray(im, np.float32).reshape(H, SS, W, SS).mean(axis=(1, 3))
# soft shadow of the whole walk
bounds = np.linspace(0, n, NC + 1).astype(int)
im = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(im)
dr.line(list(zip(X + s * 0.10, Y + s * 0.16)), fill=255, width=max(1, int(lw * 1.6)), joint='curve')
shadow = gaussian_filter(np.asarray(im, np.float32) / 255, s * 0.25)
sh.wash(shadow, 'periwinkle', float(__import__('os').environ.get('SHK', '0.5')))
for c in range(NC):
    a, e = bounds[c], bounds[c + 1]
    # accumulate edge visits within the chunk via ImageDraw 'F' add: draw edges into separate passes
    im = Image.new('F', (W * SS, H * SS), 0.0); dr = ImageDraw.Draw(im)
    dr.line([(X[i] * SS, Y[i] * SS) for i in range(a, e + 1)], fill=1.0, width=max(1, int(round(lw * SS))), joint='curve')
    L = np.asarray(im, np.float32).reshape(H, SS, W, SS).mean(axis=(1, 3))
    sh.wash(L, grad((c + 0.5) / NC), float(__import__('os').environ.get('PIGK', '2.2')))
# icing gloss: a thin lighter line offset up-left along the whole path
if __import__('os').environ.get('GLOSS', '1') == '1':
    im = Image.new('F', (W * SS, H * SS), 0.0); dr = ImageDraw.Draw(im)
    dr.line([((X[i] - lw * 0.18) * SS, (Y[i] - lw * 0.22) * SS) for i in range(n + 1)], fill=1.0, width=max(1, int(round(lw * 0.30 * SS))), joint='curve')
    gloss = np.asarray(im, np.float32).reshape(H, SS, W, SS).mean(axis=(1, 3))
# revisit glaze: count edge visits on the lattice, draw multiply-visited edges again with extra density
key = {}
for i in range(n):
    e = (round(min(X[i], X[i+1]), 2), round(min(Y[i], Y[i+1]), 2), round(max(X[i], X[i+1]), 2), round(max(Y[i], Y[i+1]), 2))
    key[e] = key.get(e, 0) + 1
im = Image.new('F', (W * SS, H * SS), 0.0); dr = ImageDraw.Draw(im)
for (x0, y0, x1, y1), m in key.items():
    if m > 1: dr.line([(x0 * SS, y0 * SS), (x1 * SS, y1 * SS)], fill=float(min(m - 1, 4)), width=max(1, int(round(lw * SS * 0.6))))
G = np.asarray(im, np.float32).reshape(H, SS, W, SS).mean(axis=(1, 3))
sh.wash(G, 'plum', 0.25)
print('distinct edges', len(key), 'max visits', max(key.values()))
# start / end pearls
pr = max(4, lw * 2.4)
for (px, py, col) in ((X[0], Y[0], 'coral'), (X[-1], Y[-1], 'coral')):
    sh.lighten(np.clip(discs(W, H, [px], [py], [pr * 1.8], sigma=pr * 0.4), 0, 1), 0.8)
    sh.wash(discs(W, H, [px], [py], [pr], sigma=0.7), col, 2.4)
    sh.lighten(np.clip(discs(W, H, [px - pr * 0.3], [py - pr * 0.3], [pr * 0.35], sigma=pr * 0.15), 0, 1), 0.8)
# ---- legend by construction (top-left): the first thirty digits typeset as u u, and the two turns
if __import__('os').environ.get('LEGEND', '1') == '1':
    lx0, ly0 = 0.06 * W, 0.075 * H
    fs = 0.026 * W
    u = ''.join(map(str, b[:15]))
    wu = text_w(u, fs, 'mono')
    gap = fs * 0.9
    sh.wash(text_mask(W, H, [(u, lx0, ly0, fs, 'mono', 'lm')]), 'coral', 2.4)
    sh.wash(text_mask(W, H, [(u, lx0 + wu + gap, ly0, fs, 'mono', 'lm')]), 'periwinkle', 3.2)
    # turn icons: incoming stroke then a 120-degree turn
    def icon(x, y, sgn, tint):
        L0 = 0.035 * W
        p0 = np.array([x, y + L0 * 0.0]); d0 = np.array([1.0, 0.0])
        p1 = p0 + d0 * L0
        ang = sgn * 2 * np.pi / 3
        d1 = np.array([np.cos(ang), -np.sin(ang)])
        p2 = p1 + d1 * L0
        im = Image.new('F', (W * SS, H * SS), 0.0); dr = ImageDraw.Draw(im)
        dr.line([tuple(p0 * SS), tuple(p1 * SS), tuple(p2 * SS)], fill=1.0, width=int(0.006 * W * SS), joint='curve')
        r = 0.006 * W
        dr.ellipse([(p2[0] - r) * SS, (p2[1] - r) * SS, (p2[0] + r) * SS, (p2[1] + r) * SS], fill=1.0)
        sh.wash(np.asarray(im, np.float32).reshape(H, SS, W, SS).mean(axis=(1, 3)), tint, 1.6)
        return p1
    iy = ly0 + 0.075 * H
    q1 = icon(lx0 + 0.01 * W, iy, +1, wheel_tint(0.62))
    q0 = icon(lx0 + 0.15 * W, iy - 0.03 * H, -1, wheel_tint(0.62))
    items = [('1 : turn left', lx0 + 0.005 * W, iy + 0.030 * H, 0.0125 * W, 'italic', 'lm'),
             ('0 : turn right', lx0 + 0.145 * W, iy + 0.030 * H, 0.0125 * W, 'italic', 'lm'),
             ('the first thirty digits are already a square, u u', lx0, ly0 + 0.030 * H, 0.0118 * W, 'italic', 'lm')]
    sh.wash(text_mask(W, H, items), 'ink', 2.2)
# ---- caption, bottom right
cx = 0.95 * W; cy = 0.84 * H
items = [('Never Three the Same Way', cx, cy, 0.034 * W, 'serif_bold', 'rm'),
         ('sixty thousand digits of the easily bored sequence, walked on the triangular lattice', cx, cy + 0.030 * H, 0.0135 * W, 'italic', 'rm'),
         ('each digit is chosen to make the shortest, least-repeated echo of what came before (MO 377105) —', cx, cy + 0.048 * H, 0.0112 * W, 'italic', 'rm'),
         ('no 000 or 111 in 300,000 digits, so the walker never once goes round a single small triangle;', cx, cy + 0.063 * H, 0.0112 * W, 'italic', 'rm'),
         ('yet its zigzags of clusters reappear as zigzags of clusters of clusters · colour = time · coral: first and last step', cx, cy + 0.078 * H, 0.0112 * W, 'italic', 'rm')]
sh.wash(text_mask(W, H, items), 'ink', 2.6)
if __import__('os').environ.get('GLOSS', '1') == '1':
    sh.lighten(np.clip(gloss, 0, 1), 0.55)
img = sh.develop(dmax=2.3)
img.save(out)
np.save('walk_xy.npy', np.stack([X, Y]))
