"""render_lipo2.py — the book without sevens, arcs composited 'over' (MO 515601).
d(n) crosses out every 7 of n.  Each n <= N containing a 7 sends an arc down to d(n); colour = place of the
leading 7 (units/tens/hundreds/thousands/ten-thousands), arcs drawn big-to-small with low alpha.
usage: render_lipo2.py W H out.png [key=val ...]"""
import sys, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '.')
from caption import caption, font
ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))
TINT = [(255, 170, 120), (110, 215, 170), (120, 180, 250), (185, 140, 250), (250, 130, 175)]
def d7(n):
    s = str(n).replace('7', ''); return int(s) if s else 0
W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
N = P('N', 10000); SS = 3
ns = [n for n in range(1, N + 1) if '7' in str(n)]
paper = (253, 251, 249)
im = Image.new('RGB', (W * SS, H * SS), paper); dr = ImageDraw.Draw(im, 'RGBA')
ml, mr, base, hs = P('ml', 0.05), P('mr', 0.05), P('base', 0.70), P('hs', 0.85)
X = lambda v: (ml + (1 - ml - mr) * v / N) * W * SS
yb = base * H * SS
arcs = sorted(((X(n) - X(d7(n))) / 2, n) for n in ns)[::-1]
alpha = P('alpha', 60); lw = max(1, int(P('lw', 1.0) * SS))
for r, n in arcs:
    d = d7(n); s = str(n); place = len(s) - 1 - s.index('7')
    c = TINT[min(place, 4)]
    cx = (X(n) + X(d)) / 2
    a = int(alpha * P('k%d' % place, 1.0))
    dr.arc([cx - r, yb - r * hs, cx + r, yb + r * hs], 180, 360, fill=c + (a,), width=lw)
im = im.resize((W, H), Image.LANCZOS)
arr = np.asarray(im).astype(np.float32)
b = int(base * H); h2 = min(H - b, b)
pap = np.array(paper, np.float32)
refl = arr[b - h2:b][::-1]
fade = (np.linspace(1, 0, h2) ** 1.6)[:, None, None] * P('mir', 0.35)
arr[b:b + h2] = pap + (refl - pap) * fade
im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(im)
d.line([(int(ml * W), b), (int((1 - mr) * W), b)], fill=(150, 135, 160), width=max(1, W // 1400))
fs = int(W * 0.011)
for v in range(0, N + 1, N // 10):
    xx = X(v) / SS; d.line([(xx, b - 5), (xx, b + 5)], fill=(150, 135, 160), width=2)
    f = font('m', fs); lab = f'{v:,}'; w = d.textlength(lab, font=f)
    d.text((xx - w / 2, b + 12), lab, font=f, fill=(130, 115, 140))
caption(im, int(W * (1 - mr)), int(H * P('capy', 0.80)), P('title', 'The Book Without Sevens'),
        [(f'every n ≤ {N:,} that contains a 7 sends an arc down to the number left when its sevens are crossed out', 'i', 0.55),
         ('colour = place of the leading seven: units peach, tens mint, hundreds sky, thousands lilac', 'r', 0.44),
         ('MathOverflow 515601: can this map be built from + × − 1/g and the floor function?', 'r', 0.44)],
        int(W * 0.03), align='right')
im.save(out)
