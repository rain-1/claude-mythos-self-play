"""EVERY PLACE THE BLUE HAS NOT REACHED — sun print (cyanotype).  The process that computes the posts.

Row n is the line of whole numbers 1..X after n posts are in.  A place x is exposed once for every way of
writing x = post + post - post (with the subtracted post different from both others): putting a post there
would make some distance occur twice.  Doses add.  Unexposed paper stays white: the posts themselves
(never touched, by the Sidon property) and the places not yet reached.  The next post is the first white
place to the right of the last one.
usage: sieve.py W out.png"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
W = int(sys.argv[1]); OUT = sys.argv[2]; S = W / 2048.0
A = [int(l.split()[1]) for l in open('math_absent/b005282.txt') if l.strip() and l[0] != '#']
X = 425; R = 19                       # columns 1..X ; rows n = 0..R-1
def dose(n):
    c = np.zeros(X + 2, np.int32); a = A[:n]
    for i in range(n):
        for j in range(i, n):
            for k in range(n):
                if k == i or k == j: continue
                x = a[i] + a[j] - a[k]
                if 1 <= x <= X: c[x] += 1
    return c
rows = [dose(n) for n in range(R)]
for n in range(1, R):                 # the greedy rule, checked on the sheet itself
    c = rows[n]; nxt = next(x for x in range(A[n - 1] + 1, X + 1) if c[x] == 0)
    assert nxt == A[n], (n, nxt, A[n])
    assert all(c[a] == 0 for a in A[:30] if a <= X)
print('greedy rule verified for rows 1..%d; max dose %d' % (R - 1, max(r.max() for r in rows)))
def noise(shape, sig, seed):
    r = np.random.default_rng(seed).standard_normal(shape); r = gaussian_filter(r, sig, mode='wrap'); return r / r.std()
CW = 4 * S; RH = 78 * S; PW = int(X * CW); PH = int(R * RH)
ox = (W - PW) // 2; oy = int(150 * S)
pad = int(40 * S); Q0, Q1 = PH + 2 * pad, PW + 2 * pad
y2, x2 = np.mgrid[0:Q0, 0:Q1].astype(np.float32)
col_i = np.clip(((x2 - pad) / CW).astype(np.int64) + 1, 1, X); row_i = np.clip(((y2 - pad) / RH).astype(np.int64), 0, R - 1)
D = np.stack(rows)[row_i, col_i].astype(np.float32)
inside = (x2 >= pad) & (x2 < pad + PW) & (y2 >= pad) & (y2 < pad + PH)
# outside the ruled field the coat got a full, even exposure (no mask there)
D = np.where(inside, D, 9.0)
# height-as-blur: the mask lay flat, so edges are crisp; a hair of light creeps under
streak = 1 + 0.9 * gaussian_filter(np.random.default_rng(60).standard_normal((Q0, Q1)), (1.5 * S, 70 * S))
b = 1 - np.exp(-0.62 * D * np.clip(streak, 0.8, 1.2))
b = gaussian_filter(b, 0.55 * S)
# threads between the rows (laid across the paper: thin unexposed lines)
fy = (y2 - pad) / RH; thr = np.clip(1 - np.abs(fy - np.round(fy)) * RH / (1.1 * S), 0, 1) * (x2 > pad - 14 * S) * (x2 < pad + PW + 14 * S)
b = b * (1 - 0.80 * thr)
# pins: where each post was driven (row n-1 -> n boundary, i.e. the row in which it is first counted)
pin = np.zeros_like(b)
for m in range(1, R):
    a = A[m - 1]
    if a > X: continue
    px = pad + (a - 0.5) * CW; py = pad + (m + 0.0) * RH
    r = np.hypot(x2 + .5 - px, y2 + .5 - py); pin = np.maximum(pin, np.clip((5.2 * S - r) / (1.4 * S) + 0.5, 0, 1))
b = b * (1 - 0.95 * pin)
# brushed coat with ragged ends
rag = noise((Q0,), 6 * S, 10) * 8 * S + noise((Q0,), 1.5 * S, 20) * 4 * S; rag2 = noise((Q0,), 6 * S, 30) * 8 * S + noise((Q0,), 1.5 * S, 40) * 4 * S
coat = np.clip((x2 - pad * 0.30 - rag[:, None]) / (3 * S), 0, 1) * np.clip((Q1 - pad * 0.30 - rag2[:, None] - x2) / (3 * S), 0, 1)
tb = noise((Q1,), 30 * S, 50) * 3 * S; tb2 = noise((Q1,), 30 * S, 51) * 3 * S
coat *= np.clip((y2 - pad * 0.40 - tb[None, :]) / (2.5 * S), 0, 1) * np.clip((Q0 - pad * 0.40 - tb2[None, :] - y2) / (2.5 * S), 0, 1)
paper = np.array([0.957, 0.937, 0.878]); img = np.ones((W, W, 3)) * paper
img *= (1 + 0.016 * noise((W, W), 0.9 * S, 1)[..., None] + 0.012 * noise((W, W), 50 * S, 2)[..., None])
blue_lo = np.array([0.40, 0.60, 0.77]); blue_hi = np.array([0.030, 0.105, 0.275])
col = blue_lo[None, None, :] * (1 - b[..., None]) + blue_hi[None, None, :] * b[..., None]
t = np.clip(b * 2.4, 0, 1)[..., None]; unexp = paper * np.array([0.975, 0.985, 0.99])          # washed-out coat: a breath cooler than bare paper
col = unexp * (1 - t) + col * t
col *= (1 + 0.03 * noise((Q0, Q1), 0.8 * S, 70)[..., None])
sl = (slice(oy - pad, oy - pad + Q0), slice(ox - pad, ox - pad + Q1))
a_ = coat[..., None]; img[sl] = img[sl] * (1 - a_) + col * a_
im = Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)); dr = ImageDraw.Draw(im)
F = lambda nm, sz: ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{nm}.ttf', int(sz * S))
pc = (78, 78, 90); rc = (205, 52, 42)
# pencil: row numbers on the left, the posts' values along the top, a scale along the bottom
for n in range(R):
    dr.text((ox - pad - int(12 * S), oy + int((n + 0.5) * RH)), str(n), font=F('Italic', 19), fill=pc, anchor='rm')
dr.text((ox - pad - int(12 * S), oy - int(26 * S)), 'posts', font=F('Italic', 17), fill=pc, anchor='rm')
last = -99
for m, a in enumerate(A[:R + 1]):
    if a > X: break
    xpix = ox + (a - 0.5) * CW
    lift = int(22 * S) if xpix - last < 30 * S else 0
    dr.text((xpix, oy - pad - int(6 * S) - lift), str(a), font=F('Regular', 17), fill=pc, anchor='mb'); last = xpix if not lift else last
for v in range(50, X + 1, 50):
    xpix = ox + (v - 0.5) * CW
    dr.line([(xpix, oy + PH + pad + int(4 * S)), (xpix, oy + PH + pad + int(13 * S))], fill=pc, width=max(1, int(1.2 * S)))
    dr.text((xpix, oy + PH + pad + int(16 * S)), str(v), font=F('Regular', 15), fill=pc, anchor='mt')
# the one red: a ring round the first white place of the last row = the next post
nx = A[R - 1]; xpix = ox + (nx - 0.5) * CW; ypix = oy + (R - 0.5) * RH; rr = 17 * S
for w_ in range(int(3 * S)):
    dr.ellipse([xpix - rr - w_, ypix - rr - w_, xpix + rr + w_, ypix + rr + w_], outline=rc)
dr.text((xpix, oy + PH + pad + int(40 * S)), f'{nx}, the next post', font=F('Italic', 20), fill=rc, anchor='mt')
by = oy + PH + pad + int(70 * S)
dr.text((ox - pad, by), 'Every Place the Blue Has Not Reached', font=F('Regular', 54), fill=pc)
dr.text((ox - pad, by + int(72 * S)), 'Each row has one post more than the row above. A place is exposed once for every way it equals post + post − post:', font=F('Italic', 27), fill=pc)
dr.text((ox - pad, by + int(106 * S)), 'a post there would repeat a distance. The next post is pinned at the first white place. The white threads running', font=F('Italic', 27), fill=pc)
dr.text((ox - pad, by + int(140 * S)), 'the whole height are the posts themselves — the blue never touches them, in any row, before or after they are chosen.', font=F('Italic', 27), fill=pc)
dr.text((ox - pad, by + int(188 * S)), f'Whole numbers 1–{X} left to right, 4 px each; rows 0–{R - 1}; depth of blue = number of ways (doses add). The rule was checked on the sheet: every pin is the first white place of its row.',
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', int(16.5 * S)), fill=pc)
im.save(OUT); print('saved', OUT)
