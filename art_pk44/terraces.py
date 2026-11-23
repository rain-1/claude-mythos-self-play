"""terraces.py -- 'Two Fifths Under Water'  (cut-paper shadow box; Fable 5.2, day 10)

The square with side zeta(2) = 1 + 1/4 + 1/9 + ... is cut by lines at the partial sums, both ways.
Field (m, n) is 1/m^2 wide and 1/n^2 deep, so its AREA is the weight 1/(mn)^2.  The fields with
max(m, n) = k form one terrace (an L), and terrace k is one sheet of paper higher than terrace k-1:
a hill that climbs to the far corner.  Square fields (m = n) are flooded: they are zeta(4)/zeta(2)^2
= 2/5 of the land.  The others are pale when m*n has an even number of prime factors (9/50 of the
land) and dark when odd (21/50).  K terraces are cut; what is left over lies under the red roof.
usage: terraces.py SIZE out.png [K]"""
import sys, numpy as np
from math import pi
from papercut import Box, rgb, mix, SERIF, SERIF_I
size = int(sys.argv[1]); out = sys.argv[2]; K = int(sys.argv[3]) if len(sys.argv) > 3 else 26
B = Box(size, seed=44, base='#0b1022'); u = B.u; S = size
H = pi**2 / 6
xs = np.concatenate([[0.0], np.cumsum(1.0 / np.arange(1, K + 1)**2)])       # xs[j] = sum_{i<=j} 1/i^2
P = 3260 * u; X0 = (S - P) / 2; YB = 3540 * u; sc = P / H
px = lambda X: X0 + X * sc
py = lambda Y: YB - Y * sc
def lam(n):
    c = 0; d = 2
    while d * d <= n:
        while n % d == 0: n //= d; c += 1
        d += 1
    return -1 if (c + (n > 1)) % 2 else 1
WATER = rgb('#d6dfd2'); PALE = rgb('#6f9da3'); DARK = rgb('#243263'); BACK = rgb('#0e1429'); RED = rgb('#c8402f')
rng = np.random.default_rng(7)
def cover(lo, hi, n=S):
    """1-D antialiased coverage of [lo, hi) on the pixel grid"""
    i = np.arange(n)
    return np.clip(np.minimum(i + 1, hi) - np.maximum(i, lo), 0, 1).astype(np.float32)
FULL = B.rect(px(0), py(H), px(H), py(0))
area = {'water': 0.0, 'pale': 0.0, 'dark': 0.0}
# night ground under everything, a little lighter than the box so the hill has a foot
B.lay(B.rect(px(0) - 46 * u, py(H) - 46 * u, px(H) + 46 * u, py(0) + 46 * u), rgb('#141b36'), 0.5, shadow=0.4, reach=3, soft=2)
for k in range(1, K + 1):
    w_u = (sc / k**2) / u                                   # width of this terrace in design px
    a0 = xs[k - 1]
    back = FULL * (1 - B.rect(px(0) - 1, py(a0), px(a0), py(0) + 1)) if k > 1 else FULL
    f = min(1.0, (sc / max(1, k - 1)**2) / u / 46.0)     # the shadow falls on the terrace below
    B.lay(back, BACK, float(k), shadow=0.62, reach=12.0 * f, soft=3.6 * f, edge=0.6 if w_u > 8 else 0.0, tex=0.6, k=k,
          contact=0.25 if w_u > 10 else 0.0, ao=0.28 if w_u > 20 else 0.0, ao_soft=12 * f)
    gap = (1.7 if w_u > 16 else (0.7 if w_u > 7 else 0.0)) * u
    M = np.zeros((S, S), np.float32); C = np.zeros((S, S, 3), np.float32)
    tiles = [(m, k) for m in range(1, k + 1)] + [(k, n) for n in range(1, k)]
    for m, n in tiles:
        x0, x1 = px(xs[m - 1]) + gap, px(xs[m]) - gap
        y0, y1 = py(xs[n]) + gap, py(xs[n - 1]) - gap
        if x1 <= x0 or y1 <= y0: x0, x1, y0, y1 = px(xs[m - 1]), px(xs[m]), py(xs[n]), py(xs[n - 1])
        ix0, ix1 = int(np.floor(x0)), int(np.ceil(x1)); iy0, iy1 = int(np.floor(y0)), int(np.ceil(y1))
        cx = np.clip(np.minimum(np.arange(ix0, ix1) + 1, x1) - np.maximum(np.arange(ix0, ix1), x0), 0, 1)
        cy = np.clip(np.minimum(np.arange(iy0, iy1) + 1, y1) - np.maximum(np.arange(iy0, iy1), y0), 0, 1)
        cov = (cy[:, None] * cx[None, :]).astype(np.float32)
        A = 1.0 / (m * n)**2
        if m == n: col = WATER * (1 + rng.uniform(-0.012, 0.012)); area['water'] += A
        elif lam(m * n) > 0: col = PALE * (1 + rng.uniform(-0.07, 0.07)) * np.array([1, 1 + rng.uniform(-.03, .03), 1]); area['pale'] += A
        else: col = DARK * (1 + rng.uniform(-0.10, 0.12)) * np.array([1 + rng.uniform(-.06, .06), 1, 1]); area['dark'] += A
        sub = M[iy0:iy1, ix0:ix1]
        C[iy0:iy1, ix0:ix1] = np.where((cov > sub)[..., None], col, C[iy0:iy1, ix0:ix1])
        M[iy0:iy1, ix0:ix1] = np.maximum(sub, cov)
    if gap > 0:
        B.lay(M, C, k + 0.12, shadow=0.38, reach=1.3, soft=0.9, edge=0.8 if w_u > 16 else 0.3, tex=1.0, k=k + 1, contact=0.0)
    else:
        B.lay(M, C, k + 0.12, shadow=0.0, edge=0.0, tex=0.8, k=k + 1)
    if k == 1:
        # the moon in the first pond: a paper disc, with three ripples cut out of its lower half
        cxm, cym, r = px(0.37), py(0.60), 0.150 * sc
        x, y = B.grid()
        moon = np.clip(r - np.hypot(x - cxm, y - cym) + 0.5, 0, 1)
        for j, (dy, hw) in enumerate(((0.42, 0.95), (0.62, 0.80), (0.80, 0.62))):
            yy = cym + dy * r; t = (0.026 - 0.004 * j) * r
            rip = np.clip(t - np.abs(y - yy - 0.02 * r * np.sin((x - cxm) / (0.11 * r))) + 0.5, 0, 1)
            moon *= 1 - rip
        B.lay(moon, rgb('#fffaea'), k + 0.3, shadow=0.30, reach=1.6, soft=1.2, edge=0.7, tex=0.5, k=3, contact=0.0)
        # a few stars in the pond, pin-pricks
        st = np.zeros((S, S), np.float32)
        for _ in range(46):
            sx, sy = px(rng.uniform(0.04, 0.96)), py(rng.uniform(0.04, 0.96))
            if np.hypot(sx - cxm, sy - cym) < 1.25 * r: continue
            st = np.maximum(st, np.clip(rng.uniform(1.6, 3.6) * u - np.hypot(x - sx, y - sy) + 0.5, 0, 1))
        B.ink(st, '#fffdf2', 0.95)
        # lily pads: small notched discs of a greener paper, in three drifts
        pads = np.zeros((S, S), np.float32)
        for gx, gy, nn, sp in ((0.74, 0.80, 15, 0.085), (0.17, 0.20, 12, 0.07), (0.80, 0.16, 9, 0.06), (0.14, 0.86, 7, 0.05)):
            for _ in range(nn):
                lx, ly = px(gx + rng.normal(0, sp)), py(gy + rng.normal(0, sp)); lr = rng.uniform(9, 21) * u
                if not (px(0.03) < lx < px(0.97) and py(0.97) < ly < py(0.03)): continue
                d = np.hypot(x - lx, y - ly); th = np.arctan2(y - ly, x - lx) - rng.uniform(0, 6.28)
                notch = np.abs(np.angle(np.exp(1j * th))) < 0.30
                pads = np.maximum(pads, np.clip(lr - d + 0.5, 0, 1) * ~notch)
        B.lay(pads, rgb('#9dbba6'), k + 0.25, shadow=0.34, reach=1.2, soft=0.9, edge=0.6, tex=0.7, k=4, contact=0.0)
        del x, y
    print('terrace', k, 'width %.1f u' % w_u, flush=True)
# ---- the rim: everything that was not cut stays bare paper, one sheet higher ------------------
a0 = xs[K]
B.lay(FULL * (1 - B.rect(px(0) - 1, py(a0), px(a0), py(0) + 1)), rgb('#1a2140'), K + 1.0, shadow=0.5, reach=1.0, soft=0.8, edge=0.5, tex=0.9, k=2, contact=0.0)
# ---- the red roof in the corner the pools climb towards --------------------------------------------
a0 = xs[K]; x0, x1, y0, y1 = px(a0), px(H), py(H), py(a0)
x, y = B.grid()
roof = B.rect(x0, y0, x1, y1)
tx, ty = (x - x0) / (x1 - x0), (y - y0) / (y1 - y0)
facet = np.where(ty < np.minimum(tx, 1 - tx), 1.16, np.where(tx < np.minimum(ty, 1 - ty), 1.06, np.where(1 - ty < np.minimum(tx, 1 - tx), 0.80, 0.90))).astype(np.float32)
B.lay(roof, RED[None, None, :] * facet[..., None], K + 3.0, shadow=0.55, reach=3.0, soft=1.6, edge=0.6, tex=0.5, k=2)
# ---- five egrets going home, high above the fields ------------------------------------------
def bird(cx, cy, s, ang, flap):
    """white bird seen from above: body, neck, two swept wings.  s = half wing span in px"""
    pts_b = []; t = np.linspace(0, 2 * np.pi, 40)
    body = np.stack([0.50 * np.cos(t) * (1 - 0.25 * np.cos(t)), 0.085 * np.sin(t)], 1) + [0.02, 0]
    wing = np.array([[0.16, 0.0], [0.10, 0.34], [-0.02, 0.72], [-0.20 * flap - 0.06, 1.0], [-0.16, 0.66], [-0.20, 0.30], [-0.15, 0.0]])
    ca, sa = np.cos(ang), np.sin(ang); R = np.array([[ca, -sa], [sa, ca]])
    m = np.zeros((S, S), np.float32)
    for poly in (body, wing, wing * [1, -1]):
        q = (poly * s) @ R.T + [cx, cy]
        m = np.maximum(m, B.poly(q, ss=2))
    return m
flock = [(1.34, 0.80, 128, 1.0), (1.15, 0.63, 120, 0.6), (1.40, 0.52, 112, 1.2), (1.20, 0.36, 110, 0.8), (1.06, 0.17, 104, 1.1)]
for bx, by, s, fl in flock:
    B.lay(bird(px(bx), py(by), s * u, -0.62, fl), rgb('#fbf8ee'), K + 16.0, shadow=0.42, reach=9.0, soft=3.4, edge=0.8, tex=0.4, k=1, contact=0.0)
# ---- mat and captions -----------------------------------------------------------------------
m_ = 60 * u
B.mat(px(0) - m_, py(H) - m_, px(H) + m_, py(0) + m_, colour='#f2eee3', z=K + 30)
tot = sum(area.values()); full = H * H
print('cut fraction of the land: %.6f' % (tot / full))
print('shares of the whole square: water %.5f (2/5), pale %.5f (9/50), dark %.5f (21/50)' % tuple(area[c] / full for c in ('water', 'pale', 'dark')))
cx = S / 2; yb = py(0) + m_
items = [(cx, yb + 118 * u, 'Two Fifths Under Water', SERIF, 96 * u, 'mm'),
         (cx, yb + 226 * u, 'A hill of fields, every one 1/m² wide and 1/n² deep, a terrace higher whenever m or n grows.  The square ones are flooded:', SERIF_I, 49 * u, 'mm'),
         (cx, yb + 290 * u, 'they are exactly two fifths of the land.  Pale fields 9 parts in 50, dark fields 21 (dark when m·n has an odd number of prime factors).', SERIF_I, 49 * u, 'mm'),
         (cx, yb + 372 * u, '%d terraces cut from paper, %d fields, %.1f%% of the land; the rest is the bare rim, and the pools climb to the red roof' % (K, K * K, 100 * tot / full), SERIF, 40 * u, 'mm')]
B.ink(B.text_mask(items), '#3b3a44', 0.82)
seal = B.rect(px(H) - 20 * u, yb + 92 * u, px(H) + 32 * u, yb + 144 * u)
B.ink(seal, '#c8402f', 0.9)
B.ink(B.text_mask([(px(H) + 6 * u, yb + 118 * u, '⅖', "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 40 * u, 'mm')]), '#f2eee3', 0.95)
B.save(out)
