"""render_faces.py — THE FACES OF NUMBERS.
Chernoff faces for 1…100, every feature an arithmetic fact:
  face pigment  = smallest prime factor (2 aqua, 3 mint, 5 lemon, 7 apricot, 11+ lavender); primes are blush with a CORAL outline
  face width    = number of divisors d(n)
  face height   = number of distinct prime factors ω(n)
  eyes          = round and large for perfect squares, else small; separation = n mod 5
  eyebrows      = Möbius μ(n): raised (+1), flat (0, a square factor), frowning (−1)
  mouth         = σ(n)/n − 2: abundant numbers smile, deficient ones frown, the perfect ones (6, 28) are straight-faced
  nose          = digit sum
usage: python3 render_faces.py FINAL out_prefix
"""
import sys, json, time
import numpy as np
from sympy import divisor_count, primefactors, divisor_sigma, mobius, isprime, factorint
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import pastel as P

FINAL = int(sys.argv[1]); OUT = sys.argv[2]
SS = 2; W = H = FINAL * SS; rs = FINAL / 1024.0 * SS
t0 = time.time()
sheet = P.Sheet(W, H, seed=8)
NC = 10; x0, y0 = 0.07 * W, 0.025 * H; cell = 0.086 * W
PIGOF = {2: 'aqua', 3: 'mint', 5: 'lemon', 7: 'apricot'}

masks = {k: Image.new('F', (W, H), 0.0) for k in ['aqua', 'mint', 'lemon', 'apricot', 'lavender', 'blush']}
ink = Image.new('F', (W, H), 0.0); coral = Image.new('F', (W, H), 0.0); light = Image.new('F', (W, H), 0.0)
di, dc, dl = ImageDraw.Draw(ink), ImageDraw.Draw(coral), ImageDraw.Draw(light)
lw = max(1, int(round(1.2 * rs)))
labels = []; feats = []
for n in range(1, 101):
    i, j = (n - 1) % NC, (n - 1) // NC
    cx, cy = x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell
    d = int(divisor_count(n)); om = len(primefactors(n)); sig = float(divisor_sigma(n)) / n; mu = int(mobius(n))
    ds = sum(int(c) for c in str(n)); sq = int(round(n ** 0.5)) ** 2 == n; prime = isprime(n)
    spf = min(primefactors(n)) if n > 1 else None
    pig = 'blush' if prime else (PIGOF.get(spf, 'lavender') if n > 1 else None)
    a = cell * (0.16 + 0.026 * min(d, 12))            # half-width from divisor count
    b = cell * (0.24 + 0.05 * min(om, 4))             # half-height from distinct primes
    b = min(b, 0.44 * cell); a = min(a, 0.44 * cell)
    if pig:
        ImageDraw.Draw(masks[pig]).ellipse([cx - a, cy - b, cx + a, cy + b], fill=1.0)
    (dc if prime else di).ellipse([cx - a, cy - b, cx + a, cy + b], outline=1.0, width=int(round((2.2 if prime else 1.2) * rs)))
    # eyes
    sep = a * (0.30 + 0.09 * (n % 5)); ey = cy - 0.25 * b
    er = (0.16 * a if sq else 0.07 * a)
    for s in (-1, 1):
        di.ellipse([cx + s * sep - er, ey - er, cx + s * sep + er, ey + er], fill=1.0)
        if sq:
            dl.ellipse([cx + s * sep - 0.45 * er, ey - 0.45 * er, cx + s * sep + 0.45 * er, ey + 0.45 * er], fill=1.0)
        # eyebrow: slant by mobius
        bx0, bx1 = cx + s * sep - 0.22 * a, cx + s * sep + 0.22 * a
        by = ey - 0.28 * b
        slant = -mu * 0.10 * b * s                      # μ=+1 raised outward, −1 frown
        di.line([(bx0, by + slant * (-1)), (bx1, by + slant * (1))], fill=1.0, width=lw)
    # nose: digit sum
    nl = b * (0.10 + 0.03 * ds)
    di.line([(cx, cy - 0.12 * b), (cx - 0.08 * a, cy - 0.12 * b + nl), (cx + 0.05 * a, cy - 0.12 * b + nl)], fill=1.0, width=lw, joint='curve')
    # mouth: abundance
    curv = float(np.clip((sig - 2.0) * 2.2, -1, 1))
    mw = 0.55 * a; my = cy + 0.45 * b
    pts = [(cx + mw * t, my - curv * 0.22 * b * (1 - t * t) + curv * 0.11 * b) for t in np.linspace(-1, 1, 15)]
    di.line(pts, fill=1.0, width=lw, joint='curve')
    labels.append((str(n), cx, cy + b + 0.03 * cell, int(0.012 * H), 'serif', 'ma'))
    feats.append(dict(n=n, d=d, omega=om, sigma_over_n=round(sig, 4), mobius=mu, digitsum=ds, square=bool(sq), prime=bool(prime), spf=spf))

for k, im in masks.items():
    m = gaussian_filter(np.asarray(im, np.float32), 0.7 * rs)
    # pooling toward the rim
    sheet.wash(0.72 * m, k, granulate=0.10, edge=0.25, seed=hash(k) % 100)
sheet.lighten(gaussian_filter(np.asarray(light, np.float32), 0.3 * rs), 0.85)
sheet.wash(0.9 * gaussian_filter(np.asarray(ink, np.float32), 0.35 * rs), 'ink')
sheet.wash(1.2 * gaussian_filter(np.asarray(coral, np.float32), 0.35 * rs), 'coral')
sheet.wash(0.8 * P.text_density(W, H, labels), 'ink')
print('faces drawn [%.0fs]' % (time.time() - t0), flush=True)

title = 'The Faces of Numbers'
sub = ('One to a hundred as faces, every feature a fact: width is the number of divisors, height the number of distinct primes, '
       'pigment the smallest prime factor (primes blush, ringed in coral), big round eyes for squares, eyebrows by the Möbius function, '
       'the nose by digit sum, and the mouth by σ(n)/n — abundant numbers smile, deficient ones frown, 6 and 28 keep a perfectly straight face.')
fs_t = int(0.036 * H); fs_s = int(0.0125 * H)
items = [(title, 0.05 * W, 0.938 * H, fs_t, 'serif_bold', 'ls')]
for j_, line in enumerate(P.wrap(sub, fs_s, 'italic', 0.90 * W)):
    items.append((line, 0.05 * W, (0.958 + 0.0155 * j_) * H, fs_s, 'italic', 'ls'))
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')
json.dump(dict(features=feats, seconds=time.time() - t0), open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
