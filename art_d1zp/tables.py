"""THE LONGER THE TABLE — engraved plate.  Ten dials, n = 3..12 guests.
Dark lathe-work sector = T_n, the share of guests who can hold more than 1/(n-1) of everything, under the nested law
with its best p; the pale notch on the rim = p_n, the chance of being sent one bridge further.
n = 3 (1/3, not attained) and n = 4 (0.400695, arXiv 2611.29223) are theorems; n >= 5 is conjecture (math_lions/RESULTS.md).
usage: tables.py W out.png"""
import sys, math, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
W = int(sys.argv[1]); OUT = sys.argv[2]; SS = 2; Wb = W * SS; S = Wb / 2048.0
def T(n, p):
    q = 1 - p
    num = sum(math.comb(n, k) * q ** k * p ** (n - k) * k for k in range(1, n - 1)) + n * q ** (n - 1) * p * (n - 2)
    return num / (n * (1 - p ** n))
def best(n):
    if n == 3: return 1.0, 1 / 3
    ps = np.linspace(1e-4, 1 - 1e-4, 200001); v = np.array([T(n, p) for p in ps[::200]]); i = v.argmax() * 200
    lo, hi = ps[max(i - 400, 0)], ps[min(i + 400, len(ps) - 1)]
    for _ in range(80):
        a, b = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if T(n, a) < T(n, b): lo = a
        else: hi = b
    return (lo + hi) / 2, T(n, (lo + hi) / 2)
vals = {n: best(n) for n in range(3, 13)}
ink = (28, 36, 84); red = (205, 52, 42); pen = (78, 78, 90)
im = Image.new('RGB', (Wb, Wb), (244, 238, 222)); dr = ImageDraw.Draw(im)
F = lambda nm, sz: ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{nm}.ttf', int(sz * S))
# frame: double rule with corner ticks
m = int(70 * S)
dr.rectangle([m, m, Wb - m, Wb - m], outline=ink, width=int(3 * S)); dr.rectangle([m + 10 * S, m + 10 * S, Wb - m - 10 * S, Wb - m - 10 * S], outline=ink, width=max(1, int(1 * S)))
cols, rows = 5, 2; R = 142 * S; gx = (Wb - 2 * m - 80 * S) / cols; top = 390 * S; gy = 740 * S
for idx, n in enumerate(range(3, 13)):
    p, t = vals[n]; cx = m + 40 * S + gx * (idx % cols + 0.5); cy = top + gy * (idx // cols) + R
    a0 = -90.0; a1 = a0 + 360 * t
    # dark sector: concentric lathe-work whose lines swell
    for k in range(1, 61):
        r = R * k / 61.0; wv = 1.0 + 1.6 * (0.5 + 0.5 * math.sin(k * 0.9 + n))
        dr.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=ink, width=max(1, int(wv * S)))
    # rosette over the sector: a wavy ring pair
    for ph in (0.0, math.pi):
        pts = []
        for a in np.linspace(a0, a1, 400):
            rr = R * (0.72 + 0.045 * math.sin(math.radians(a - a0) * 24 / max(t, 0.2) / 2 + ph)); pts.append((cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a))))
        dr.line(pts, fill=(244, 238, 222), width=int(3 * S))
    # light part: sparse radial ticks
    for a in np.arange(a1 + 3, a0 + 360 - 1, 3.0):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        dr.line([(cx + 0.90 * R * ca, cy + 0.90 * R * sa), (cx + R * ca, cy + R * sa)], fill=ink, width=max(1, int(1 * S)))
    dr.ellipse([cx - R, cy - R, cx + R, cy + R], outline=ink, width=int(2.5 * S))
    dr.ellipse([cx - R - 9 * S, cy - R - 9 * S, cx + R + 9 * S, cy + R + 9 * S], outline=ink, width=max(1, int(1 * S)))
    for a in (a0, a1):
        dr.line([(cx, cy), (cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))], fill=ink if n != 4 or a == a0 else red, width=int((2 if n != 4 or a == a0 else 4) * S))
    dr.ellipse([cx - 5 * S, cy - 5 * S, cx + 5 * S, cy + 5 * S], fill=ink)
    # the seats: n small rings round the table
    for k in range(n):
        a = math.radians(-90 + 360 * (k + 0.5) / n); sx, sy = cx + (R + 31 * S) * math.cos(a), cy + (R + 31 * S) * math.sin(a); rs = 11 * S
        dr.ellipse([sx - rs, sy - rs, sx + rs, sy + rs], outline=ink, width=int(2 * S))
    dr.text((cx, cy + R + 78 * S), f'{n} guests', font=F('Italic', 30), fill=pen, anchor='mt')
    dr.text((cx, cy + R + 116 * S), ('1/3' if n == 3 else f'{t:.6f}'), font=F('Bold', 34), fill=red if n == 4 else ink, anchor='mt')
    dr.text((cx, cy + R + 158 * S), ('p → 1, never reached' if n == 3 else f'p = {p:.4f}'), font=F('Regular', 23), fill=pen, anchor='mt')
    dr.text((cx, cy + R + 188 * S), ('theorem' if n == 3 else 'theorem (2026)' if n == 4 else 'conjecture'), font=F('Italic', 22), fill=red if n == 4 else pen, anchor='mt')
dr.text((Wb / 2, m + 60 * S), 'THE LONGER THE TABLE', font=F('Regular', 62), fill=ink, anchor='mt')
dr.text((Wb / 2, m + 140 * S), 'how large a part of the company can each hold more than an (n − 1)th of everything on it', font=F('Italic', 30), fill=pen, anchor='mt')
by = top + 2 * gy - 120 * S
L = ['Engraved part of each dial: the share of guests above the line, when the plates are filled from the canal of No Last Bridge with the best chance p',
     'of being sent one bridge further.  T(p) = [ Σ k·C(n,k)(1−p)^k p^(n−k) for k ≤ n−2,  plus (n−2)·n(1−p)^(n−1) p ] / n(1−p^n).  For four guests T = p(2−p)/((1+p)(1+p²)),',
     'largest at the root of p⁴−4p³−3p²−2p+2, where T solves 16x⁴+8x³+99x²−32x−4 = 0.  For five and six a search over laws on 0…36 found the same shape and nothing better.']
for i, l in enumerate(L): dr.text((Wb / 2, by + i * 36 * S), l, font=F('Regular', 23.5), fill=pen, anchor='mt')
im = im.resize((W, W), Image.LANCZOS)
a = np.asarray(im, np.float32) / 255
r = np.random.default_rng(3).standard_normal((W, W)).astype(np.float32)
a *= (1 + 0.012 * gaussian_filter(r, 0.8)[..., None] / 0.3 + 0.010 * (gaussian_filter(r, 40) / gaussian_filter(r, 40).std())[..., None])
Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)).save(OUT); print('saved', OUT, {n: (round(v[0], 6), round(v[1], 6)) for n, v in vals.items()})
