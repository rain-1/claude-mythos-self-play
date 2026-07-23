"""THE LEDGER OF REFLECTIONS -- det A_n, A_n[i,j]=[i+j is a power of 2].
There is exactly ONE permutation of {1..n} with every i+pi(i) a power of two
(permanent = 1, MO 513368); it is a cascade of nested interval reversals,
one stage per binary run of n.  Drawn on a log-spiral: each fan = one stage,
each arc = one transposition i <-> 2^{k+1}-i, gold stars = the self-paired
powers of two, r(n) of them.  Theorem (verified exactly, verify_ledger.py):
det A_n = (-1)^((n - r(n))/2).  Here n = 2730 = 101010101010_2, r = 12,
det = -1: the deepest cascade below 4096."""
import sys, numpy as np
from kit import splat, draw_polyline, wide_bloom, tonemap, save, ramp, typ

PROTO  = "final" not in sys.argv
S      = 2048 if PROTO else 8192
FINAL  = 1024 if PROTO else 4096
rs     = S / 2048.0
N      = 2730
OCT    = 12.0

def stages_of(n):
    out = []
    while n > 0:
        k = n.bit_length() - 1
        s = 1 << (k + 1)
        out.append((n, s - n, n, s))
        n = s - n - 1
    return out

ST = stages_of(N)
RO, RI = 1.0, 0.335            # abstract units; bbox-fit later
DIPF   = 0.72

def base_r(lg):
    return RO * (RI / RO) ** ((OCT - lg) / OCT)

def polar(x, rr):
    lg  = np.log2(np.maximum(x, 1e-9))
    phi = -np.pi/2 + 2*np.pi * (OCT - lg) / OCT
    return rr*np.cos(phi), rr*np.sin(phi)

COOL = [(0.00, (0.09, 0.28, 0.47)), (0.30, (0.12, 0.50, 0.68)),
        (0.58, (0.26, 0.74, 0.74)), (0.82, (0.62, 0.88, 0.70)),
        (1.00, (0.95, 0.86, 0.52))]
GOLD = np.array([1.00, 0.78, 0.34])

# ---- phase 1: collect all geometry in abstract coords ----------------------
jobs = []      # (X, Y, W, colorA, colorB, wselB)  per stage
rng = np.random.default_rng(7)
for si, (ns, lo, hi, ssum) in enumerate(ST):
    c = ssum // 2
    depmax = max(c - lo, 1)
    ds = np.arange(1, min(c - lo, hi - c) + 1)
    if len(ds) == 0: continue
    L = len(ds); dep = ds / depmax
    npts = 300 if PROTO else 1100
    u  = np.linspace(0, 1, npts)[None, :]
    i_ = (c - ds)[:, None].astype(float); j_ = (c + ds)[:, None].astype(float)
    lg = np.log2(i_) + (np.log2(j_) - np.log2(i_)) * u
    xx = 2.0 ** lg
    rb = base_r(lg)
    rr = rb * (1 - DIPF * (dep[:, None]**0.78) * np.sin(np.pi * u))
    X, Y = polar(xx, rr)
    fr = np.abs(((np.log2(ds) + 0.5) % 1.0) - 0.5) * 2
    strobe = 0.45 + 0.55 * np.cos(0.5*np.pi*fr)**3
    per_arc = np.minimum(2400.0 * L**(-0.60), 420.0) * strobe * (0.55 + 0.45*dep)
    W = (per_arc[:, None] / npts) * np.ones_like(u)
    cA = ramp(COOL, si / max(len(ST)-1, 1))
    cB = cA * np.array([0.55, 0.75, 1.05]) if si < 8 else cA * 0.75
    jobs.append((X, Y, W, cA, cB, dep[:, None], si))

lgs = np.linspace(0, np.log2(N), 6000)
RX, RY = polar(2.0**lgs, base_r(lgs))
SX, SY = [], []
for si, (ns, lo, hi, ssum) in enumerate(ST):
    c = ssum // 2
    x0, y0 = polar(np.array([float(c)]), np.array([base_r(np.log2(c))]))
    SX.append(x0[0]); SY.append(y0[0])

# bbox fit
allx = np.concatenate([j[0].ravel() for j in jobs] + [RX])
ally = np.concatenate([j[1].ravel() for j in jobs] + [RY])
x0, x1, y0, y1 = allx.min(), allx.max(), ally.min(), ally.max()
span = max(x1 - x0, y1 - y0)
scale = S * 0.92 / span
offx = (S - scale*(x1 - x0)) / 2 - scale * x0
offy = (S - scale*(y1 - y0)) / 2 - scale * y0
def fit(x, y): return x*scale + offx, y*scale + offy

# ---- phase 2: splat ---------------------------------------------------------
arcs  = np.zeros((S, S, 3), np.float32)
ring  = np.zeros((S, S), np.float32)
stars = np.zeros((S, S, 3), np.float32)

for X, Y, W, cA, cB, depc, si in jobs:
    Xs, Ys = fit(X, Y)
    Ys = Ys + rng.normal(0, 0.45*rs, size=(X.shape[0], 1))
    Wm = W * rs * rs
    for cc, wsel in ((cA, 1-depc), (cB, depc)):
        tmp = np.zeros((S, S), np.float32)
        splat(tmp, Xs.ravel(), Ys.ravel(), (Wm*wsel).ravel())
        for ch in range(3):
            arcs[..., ch] += tmp * cc[ch]

RXs, RYs = fit(RX, RY)
draw_polyline(ring, RXs, RYs, 5200 * rs * rs)

for si in range(len(SX)):
    Xs, Ys = fit(np.array([SX[si]]), np.array([SY[si]]))
    g = np.zeros((S, S), np.float32)
    splat(g, Xs, Ys, 1.0)
    boost = 1.0 + (2.6 if si == len(SX)-1 else 0.0)
    g = wide_bloom(g, 3.2*rs) * (5200 + 700*si) * rs * rs * boost
    for ch in range(3):
        stars[..., ch] += g * GOLD[ch]
    if si == len(SX)-1:
        th = np.linspace(0, 2*np.pi, 1200)
        rr0 = 0.030 * S
        h = np.zeros((S, S), np.float32)
        draw_polyline(h, Xs[0] + rr0*np.cos(th), Ys[0] + rr0*np.sin(th), 2200*rs*rs)
        h = wide_bloom(h, 1.6*rs)
        for ch in range(3):
            stars[..., ch] += h * GOLD[ch] * 0.55

img = np.zeros((S, S, 3), np.float32)
a_t = typ(arcs.sum(-1)); arcs /= a_t
img += arcs * 1.15
halo = np.stack([wide_bloom(arcs[...,ch], 6*rs) for ch in range(3)], -1)
img += halo * (1.0 / max(typ(halo.sum(-1)), 1e-9))
img += (ring / typ(ring))[...,None] * np.array([0.30, 0.42, 0.46]) * 0.5
s_t = typ(stars.sum(-1)); stars /= s_t
img += stars * 2.4
out = tonemap(img, k=1.05, gamma=0.85)
save(out, "proto_hero_spiral.png" if PROTO else "hero_ledger.png", FINAL)
