"""render_tide.py — THE TIDE OF FOUR PRIMES (MO 409058), pastel strata chart.

Share of n <= N whose proper-divisor divisibility graph is planar, stacked by prime
signature (p, p², p³, p⁴, pq, p²q, p³q, pqr) as warm sediment strata; the non-planar
share is the cool sea rising from above.  x = log10 N (1 .. 12).  The 1/2 line, the exact
first tie / first non-planar lead / last planar lead, and an inset of D(N) = planar − non-planar
through the ±1 steps of the crossing (11 lead changes inside 500 integers).
"""
import sys, json, time, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
sys.path.insert(0, '.')
from pastel import Watercolor, absorption, _blur

t0 = time.time()
def log(*a): print(f'[{time.time() - t0:7.1f}s]', *a, flush=True)
ap = argparse.ArgumentParser()
ap.add_argument('--W', type=int, default=1600); ap.add_argument('--H', type=int, default=1100)
ap.add_argument('--final', type=float, default=0.5)
ap.add_argument('--out', default='tide_proto.png')
args = ap.parse_args()
W, H = args.W, args.H; rs = W / 1600.0
rng = np.random.default_rng(11)

rows = json.load(open('tide_data.json'))
win = json.load(open('planar_window.json'))
Ns = np.array([r['N'] for r in rows], float)
keys = ['p', 'p2', 'p3', 'p4', 'pq', 'p2q', 'p3q', 'pqr']
comp = np.array([[r[k] for k in keys] for r in rows], float)
comp[:, 0] += 1  # n = 1 rides with the primes stratum (empty graph)
P = comp.sum(1)
shares = comp / Ns[:, None]
nonplanar = 1 - P / Ns
log('rows', len(rows), 'last N', Ns[-1], 'planar share', P[-1] / Ns[-1])

# ---- chart frame
x0, x1 = int(0.07 * W), int(0.965 * W)
y0, y1 = int(0.125 * H), int(0.80 * H)          # plot box (y0 top)
lx0, lx1 = 1.0, np.log10(Ns[-1])
def X(N): return x0 + (np.log10(N) - lx0) / (lx1 - lx0) * (x1 - x0)
def Y(s): return y1 - s * (y1 - y0)

PIG = {
    'p':   absorption('#f28b74'), 'p2': absorption('#f4a077'), 'p3': absorption('#f6b27a'), 'p4': absorption('#f8c27e'),
    'pq':  absorption('#f5cf80'), 'p2q': absorption('#e9d78a'), 'p3q': absorption('#d3d994'), 'pqr': absorption('#bfdc9c'),
    'sea': absorption('#8fc9e6'), 'sea2': absorption('#a7b9ee'),
    'ink': absorption('#57505b'), 'graphite': absorption('#8b93a3'), 'coral': absorption('#ef6f5e')}
wc = Watercolor(H, W, seed=5, warm=1.0)

# rasterise strata as polygons between cumulative curves
xs = X(Ns)
cum = np.cumsum(shares, axis=1)
def band(lower, upper):
    im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
    pts = [(float(x), float(Y(u))) for x, u in zip(xs, upper)] + [(float(x), float(Y(l))) for x, l in zip(xs[::-1], lower[::-1])]
    dr.polygon(pts, fill=1.0)
    return np.array(im, np.float32)
prev = np.zeros(len(Ns))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
for i, k in enumerate(keys):
    b = band(prev, cum[:, i])
    # sediment texture: soft horizontal laminae + granulation
    lam = 0.85 + 0.15 * np.sin(yy / (3.2 * rs) + 0.6 * np.sin(xx / (40 * rs)))
    wc.wash(gaussian_filter(b, 1.0 * rs) * lam * (0.9 - 0.06 * i), PIG[k], strength=1.0, granulate=0.25, edge=0.35, edge_sigma=2.5 * rs)
    prev = cum[:, i]
# the sea: non-planar share, from the top of the planar stack to 1
sea = band(cum[:, -1], np.ones(len(Ns)))
depth = np.clip((Y(cum[:, -1]).mean() - yy) / (y1 - y0), 0, 1)   # deeper toward the top
seaf = gaussian_filter(sea, 1.0 * rs)
wc.wash(seaf * (0.55 + 0.45 * (1 - (yy - y0) / (y1 - y0)).clip(0, 1)), PIG['sea'], strength=0.9, granulate=0.3, edge=0.5, edge_sigma=3 * rs)
wc.wash(seaf * 0.35 * np.clip((yy - y0) / (y1 - y0), 0, 1) ** 2, PIG['sea2'], strength=0.7)
# wave crests along the shoreline (the planar/non-planar boundary): a few thin lighter lines above
log('strata washed')

# ---- half line, crossing marks
def stroke_poly(pts, width, pig, strength, dash=None):
    im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
    if dash is None:
        dr.line(pts, fill=1.0, width=max(1, int(width)))
    else:
        for i in range(0, len(pts) - 1):
            pass
    wc.wash(gaussian_filter(np.array(im, np.float32), 0.7 * rs), PIG[pig], strength=strength)
stroke_poly([(x0, Y(0.5)), (x1, Y(0.5))], 1.6 * rs, 'ink', 0.9)
Nx = win['first_neg']
stroke_poly([(X(Nx), y0 - 8 * rs), (X(Nx), y1 + 6 * rs)], 2.2 * rs, 'coral', 1.4)
# axes: decade ticks
for k in range(1, int(lx1) + 1):
    stroke_poly([(X(10 ** k), y1), (X(10 ** k), y1 + 9 * rs)], 1.4 * rs, 'ink', 0.9)
stroke_poly([(x0, y1), (x1, y1)], 1.6 * rs, 'ink', 1.0)
for s in (0.25, 0.75, 1.0):
    stroke_poly([(x0, Y(s)), (x0 - 8 * rs, Y(s))], 1.4 * rs, 'ink', 0.9)
stroke_poly([(x0, y0), (x0, y1)], 1.6 * rs, 'ink', 1.0)

# ---- text
FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'; FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
FONT_I = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
mk = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(mk)
def T(x, y, s, size, face=FONT, anchor='la'):
    dr.text((x, y), s, fill=255, font=ImageFont.truetype(face, int(size)), anchor=anchor)
T(x0, int(0.03 * H), 'THE TIDE OF FOUR PRIMES', 0.036 * H, FONT_B)
T(x0, int(0.03 * H) + int(0.046 * H), 'share of n ≤ N whose proper divisors form a planar divisibility graph, stacked by prime signature', 0.0155 * H, FONT)
T(x0, int(0.03 * H) + int(0.046 * H) + int(0.02 * H), 'the sea is every n with a fourth prime factor, or a K₅ / K₃,₃ among its divisors', 0.0155 * H, FONT)
for k in range(1, int(lx1) + 1):
    T(X(10 ** k), y1 + 13 * rs, f'10{"⁰¹²³⁴⁵⁶⁷⁸⁹"[k] if k < 10 else "¹" + "⁰¹²³⁴⁵⁶⁷⁸⁹"[k - 10]}', 0.017 * H, FONT, 'ma')
T(x0 - 12 * rs, Y(0.5), '½', 0.02 * H, FONT_B, 'rm'); T(x0 - 12 * rs, Y(1.0), '1', 0.017 * H, FONT, 'rm'); T(x0 - 12 * rs, Y(0.0), '0', 0.017 * H, FONT, 'rm')
T(x0 - 12 * rs, Y(0.25), '¼', 0.017 * H, FONT, 'rm'); T(x0 - 12 * rs, Y(0.75), '¾', 0.017 * H, FONT, 'rm')
# stratum labels at the right edge, inside each band where it is thick enough
labels = {'p': 'p', 'pq': 'p·q', 'p2q': 'p²q', 'p3q': 'p³q', 'pqr': 'p·q·r'}
for i, k in enumerate(keys):
    if k in labels:
        j = int(0.55 * len(Ns))
        lo_ = prev_ = (cum[j, i - 1] if i > 0 else 0); hi_ = cum[j, i]
        if hi_ - lo_ > 0.03:
            T(xs[j], Y((lo_ + hi_) / 2), labels[k], 0.02 * H, FONT_I, 'mm')
T(X(10 ** 2.9), Y(0.86), 'non-planar', 0.024 * H, FONT_I, 'mm')
cert = win.get('certified_to')
if not cert:
    import re
    cps = [int(m.replace(',', '')) for m in re.findall(r'checkpoint N=([\d,]+)', open('planar_window.log').read())]
    cert = max(cps) if cps else None
cert_s = ('10¹²' if cert == 10 ** 12 else f'{cert:.2e}'.replace('e+', '·10^')) if cert else '—'
T(X(Nx) - 10 * rs, y0 + 4 * rs, f'N = {Nx:,}', 0.019 * H, FONT_B, 'ra')
T(X(Nx) - 10 * rs, y0 + 4 * rs + 0.026 * H, 'non-planar takes the lead', 0.0155 * H, FONT_I, 'ra')
T(X(Nx) - 10 * rs, y0 + 4 * rs + 0.048 * H, f'first tie {win["first_tie"]:,} · last planar lead {win["last_planar_lead_in_window"]:,}', 0.0135 * H, FONT, 'ra')
T(X(Nx) - 10 * rs, y0 + 4 * rs + 0.068 * H, f'non-planar certified ahead at every N from there to {cert_s}', 0.0135 * H, FONT, 'ra')
T(X(Nx) - 10 * rs, y0 + 4 * rs + 0.088 * H, 'Landau: the planar share → 0 like (log log N)² / (2 log N)', 0.0135 * H, FONT, 'ra')
# footer
T(x0, int(0.875 * H), 'planar ⇔ signature ∈ {p, p², p³, p⁴, pq, p²q, p³q, pqr}; minimal non-planar signatures p⁵, p²q², p⁴q, p²qr, pqrs (n = 1 counted planar)', 0.0135 * H, FONT)
T(x0, int(0.875 * H) + 0.021 * H, 'exact counts from a Lucy–Hedgehog prime-count table, checked against a brute-force sieve; the crossing sieved integer by integer', 0.0135 * H, FONT)
T(x0, int(0.875 * H) + 0.042 * H, 'MO 409058 asks whether the planar ones are always more numerous. They are not — and the day they stop is an integer.', 0.0135 * H, FONT_I)
cap = np.array(mk, np.float32) / 255.0
wc.wash(cap, PIG['ink'], strength=1.7)

# ---- inset: D(N) walk through the crossing
ix0, ix1 = int(0.64 * W), int(0.955 * W); iy0, iy1 = int(0.15 * H), int(0.44 * H)
strip = np.zeros((H, W), np.float32); strip[iy0:iy1, ix0:ix1] = 1.0
strip = gaussian_filter(strip, 3 * rs)
wc.D *= (1.0 - 0.86 * strip)[..., None]
zN = np.array(win['zoom_N']); zD = np.array(win['zoom_D'])
m = (zN >= Nx - 900) & (zN <= Nx + 700)
zN, zD = zN[m], zD[m]
def IX(N): return ix0 + (N - zN[0]) / (zN[-1] - zN[0]) * (ix1 - ix0)
dmax = np.abs(zD).max() * 1.15
def IY(d): return (iy0 + iy1) / 2 - d / dmax * (iy1 - iy0) / 2
# zero line + the walk (planar-lead parts warm, non-planar parts cool)
stroke_poly([(ix0, IY(0)), (ix1, IY(0))], 1.2 * rs, 'graphite', 1.0)
pts = [(float(IX(n)), float(IY(d))) for n, d in zip(zN, zD)]
im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im); dr.line(pts, fill=1.0, width=max(1, int(2.4 * rs)))
walk = gaussian_filter(np.array(im, np.float32), 0.8 * rs)
above = (yy < IY(0)).astype(np.float32)
wc.wash(walk * above, PIG['coral'], strength=1.3); wc.wash(walk * (1 - above), PIG['sea'], strength=1.5)
# fill under/over the walk lightly
imf = Image.new('F', (W, H), 0.0); drf = ImageDraw.Draw(imf)
drf.polygon(pts + [(pts[-1][0], IY(0)), (pts[0][0], IY(0))], fill=1.0)
fill = np.array(imf, np.float32)
wc.wash(fill * above * 0.35, PIG['p2'], strength=0.8); wc.wash(fill * (1 - above) * 0.35, PIG['sea'], strength=0.8)
mk2 = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(mk2)
def T2(x, y, s, size, face=FONT, anchor='la'):
    dr.text((x, y), s, fill=255, font=ImageFont.truetype(face, int(size)), anchor=anchor)
T2(ix0 + 8 * rs, iy0 + 6 * rs, 'D(N) = planar − non-planar, one step per integer', 0.0145 * H, FONT_I)
T2(ix0 + 8 * rs, iy0 + 6 * rs + 0.022 * H, f'{len(win["changes"])} lead changes between N = {win["changes"][0][0]:,} and {win["changes"][-1][0]:,}', 0.0135 * H, FONT)
T2(ix0 + 8 * rs, iy1 - 0.03 * H, f'{zN[0]:,}', 0.013 * H, FONT); T2(ix1 - 8 * rs, iy1 - 0.03 * H, f'{zN[-1]:,}', 0.013 * H, FONT, anchor='ra')
wc.wash(np.array(mk2, np.float32) / 255.0, PIG['ink'], strength=1.6)
log('inset done')
fw, fh = int(W * args.final), int(H * args.final)
wc.save(args.out, final_size=(fw, fh), dmax=2.4)
log('saved', args.out)
