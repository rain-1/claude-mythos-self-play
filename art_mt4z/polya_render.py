"""'The Nine Hundred Million Winters' — Polya's conjecture and its breach.

Main chart: y = L(x)/sqrt(x) over log2(x), x in [2, 2^30], where
L(x) = sum_{n<=x} lambda(n) (Liouville).  Polya conjectured (1919) L(x) <= 0
for x >= 2; the walk stays under water for nine hundred million integers and
then pierces the surface at x = 906,150,257 (verified from scratch here) by a
sliver invisible at this scale — the inset magnifies the breach archipelago.
"""
import time
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation
import rkit

FINAL = 2560
SS = 2
S = FINAL * SS
rs = FINAL / 4096 * SS
t0 = time.time()

BLK = 4096
blocks = np.fromfile('blocks.i16', dtype=np.int16).astype(np.int64)
cum = np.cumsum(blocks)
xb = (np.arange(1, len(blocks) + 1, dtype=np.float64)) * BLK

# exact prefix for x <= 2^25
def lam_range(lo, hi):
    primes = []
    sieve = np.ones(32770, dtype=bool); sieve[:2] = False
    for p in range(2, 32770):
        if sieve[p]:
            primes.append(p); sieve[p * p::p] = False
    out = np.empty(hi - lo + 1, dtype=np.int8)
    CH = 1 << 22
    for c0 in range(lo, hi + 1, CH):
        c1 = min(c0 + CH - 1, hi)
        n = np.arange(c0, c1 + 1, dtype=np.int64)
        res = n.copy(); par = np.zeros(len(n), dtype=np.int8)
        for p in primes:
            if p * p > c1: break
            start = ((c0 + p - 1) // p) * p
            idx = np.arange(start - c0, len(n), p)
            while len(idx):
                div = res[idx] % p == 0
                idx = idx[div]
                res[idx] //= p; par[idx] ^= 1
                idx = idx[res[idx] % p == 0]
        par ^= (res > 1)
        out[c0 - lo:c1 - lo + 1] = np.where(par == 0, 1, -1)
    return out

XE = 1 << 25
lam = lam_range(1, XE)
lam[0] = 1
Lexact = np.cumsum(lam.astype(np.int64))
print(f'exact lambda to 2^25 in {time.time()-t0:.0f}s; L(2^25) = {Lexact[-1]} '
      f'(block cum: {cum[XE // BLK - 1]})')
assert Lexact[-1] == cum[XE // BLK - 1]

# assemble plot series in (x/1e9, L/sqrt(x)) — LINEAR x
xe_s = np.arange(2048, XE + 1, 2048, dtype=np.float64)
ye_s = Lexact[2047::2048] / np.sqrt(xe_s)
mask_b = xb > XE
xs = np.concatenate([xe_s, xb[mask_b]]) / 1e9
ys = np.concatenate([ye_s, cum[mask_b] / np.sqrt(xb[mask_b])])
print(f'series: {len(xs)} pts,  y range [{ys.min():.3f}, {ys.max():.4f}]')

# canvas mapping
X0, X1 = -0.012, 1.085
Y0, Y1 = -1.50, 0.30
def px(lx):
    return (np.asarray(lx) - X0) / (X1 - X0) * (S - 1)
def py(v):
    return (Y1 - np.asarray(v)) / (Y1 - Y0) * (S - 1)

rgb = np.zeros((S, S, 3), np.float32)
# inset backing mask (computed early so the waterline can dodge the glass)
IX0e, IX1e = int(0.055 * S), int(0.575 * S)
IY0e, IY1e = int(0.075 * S), int(0.415 * S)
backing_mask = np.zeros((S, S), np.float32)
backing_mask[IY0e:IY1e, IX0e:IX1e] = 1.0
from scipy.ndimage import gaussian_filter as gfb
backing_mask = gfb(backing_mask, 2.5 * rs)
# ------------------------------------------- per-column envelope of the walk
cols = np.clip(px(xs).astype(np.int64), 0, S - 1)
colmin = np.full(S, np.inf); colmax = np.full(S, -np.inf)
np.minimum.at(colmin, cols, ys)
np.maximum.at(colmax, cols, ys)
ok = np.isfinite(colmin)
idx = np.arange(S)
c_first, c_last = idx[ok][0], idx[ok][-1]
colmin = np.interp(idx, idx[ok], colmin[ok])
colmax = np.interp(idx, idx[ok], colmax[ok])
datacols = ((idx >= c_first) & (idx <= c_last))[None, :]
from scipy.ndimage import gaussian_filter1d
colmin = gaussian_filter1d(colmin, 0.7 * rs)
colmax = gaussian_filter1d(colmax, 0.7 * rs)

rows_v = np.linspace(Y1, Y0, S)[:, None]
top = colmax[None, :]; bot = colmin[None, :]
wpx = 2.0 * rs * (Y1 - Y0) / S
inband = (rows_v <= top) & (rows_v >= bot)
edge_top = np.exp(-((rows_v - top) / wpx) ** 2)
edge_bot = np.exp(-((rows_v - bot) / wpx) ** 2)
walk_col = np.array([0.55, 0.88, 0.95], np.float32)
body = np.maximum.reduce([edge_top, edge_bot, 0.85 * inband.astype(np.float32)]) * datacols
rgb += (body[..., None] * walk_col * 0.85).astype(np.float32)
# gild the emergence
emerge = np.clip(top / (2 * wpx), 0, 1) * edge_top * datacols
rgb += (emerge[..., None] * np.array([1.0, 0.80, 0.34]) * 1.3).astype(np.float32)
# abyss between waterline and the walk
below = (rows_v < 0) & (rows_v > top) & datacols
depth = np.where(below, (0 - rows_v) / 1.50, 0)
nearc = np.where(below, np.clip(1 - (rows_v - top) / 0.10, 0, 1), 0)
fill = (0.20 * (1 - depth) ** 1.6 + 0.30 * nearc ** 2.2).astype(np.float32)
rgb += fill[..., None] * np.array([0.10, 0.22, 0.38], np.float32)
# axis hairlines at 0.2..1.0 e9
ax = np.zeros((S, S), np.float32)
for xv in [0.2, 0.4, 0.6, 0.8, 1.0]:
    rkit.line_splat(ax, px(np.array([xv])), py(np.array([Y1])),
                    px(np.array([xv])), py(np.array([Y0])), np.array([40.0 * rs]), npts=800)
rgb += gaussian_filter(ax, 0.8 * rs)[..., None] * np.array([0.30, 0.40, 0.52]) * 0.10
print(f'envelope band {time.time()-t0:.0f}s')

# --------------------------------------------------- waterline (the law)
wl = np.zeros((S, S), np.float32)
rkit.line_splat(wl, px(np.array([X0])), py(np.array([0.0])),
                px(np.array([X1])), py(np.array([0.0])), 6500.0 * rs, npts=int(S * 0.7))
wld = grey_dilation(wl, size=int(max(2, 1.0 * rs))) * (1 - 0.93 * backing_mask)
rgb += gaussian_filter(wld, 1.0 * rs)[..., None] * np.array([0.85, 0.72, 0.38]) * 0.55
rgb += gaussian_filter(wld, 9.0 * rs)[..., None] * np.array([0.85, 0.72, 0.38]) * 0.16

# --------------------------------------------------- the breach beacon
xbr = 0.906150257
bc = np.zeros((S, S), np.float32)
rkit.line_splat(bc, px(np.array([xbr])), py(np.array([0.0])),
                px(np.array([xbr])), py(np.array([0.235])), np.array([500.0 * rs]),
                npts=1200)
bcd = grey_dilation(bc, size=int(max(2, 1.2 * rs)))
gold = np.array([1.0, 0.80, 0.34])
rgb += bcd[..., None] * gold * 0.055
rgb += gaussian_filter(bcd, 6 * rs)[..., None] * gold * 0.22
# breach star at the waterline
star = np.zeros((S, S), np.float32)
rkit.splat_points(star, [float(px(xbr))], [float(py(0.0))], 2600.0 * rs)
rgb += gaussian_filter(star, 3.0 * rs)[..., None] * np.array([1.0, 0.92, 0.65]) * 0.9
rgb += gaussian_filter(star, 16.0 * rs)[..., None] * gold * 0.5
print(f'beacon {time.time()-t0:.0f}s')

# --------------------------------------------------- inset: the archipelago
isl = np.load('polya_island_full.npy')
xi, Li = isl[0], isl[1]
# inset frame in canvas coords
IX0, IX1 = int(0.055 * S), int(0.575 * S)
IY0, IY1 = int(0.075 * S), int(0.415 * S)
# island data window
WX0, WX1 = 906.10e6, 906.53e6
WY0, WY1 = -1450.0, 980.0
mwin = (xi >= WX0) & (xi <= WX1)
xw, Lw = xi[mwin].astype(np.float64), Li[mwin].astype(np.float64)
def ipx(v):
    return IX0 + (np.asarray(v) - WX0) / (WX1 - WX0) * (IX1 - IX0)
def ipy(v):
    return IY1 - (np.asarray(v) - WY0) / (WY1 - WY0) * (IY1 - IY0)
# frame: dark glass backing
backing = np.zeros((S, S), np.float32)
backing[IY0:IY1, IX0:IX1] = 1.0
backing = gaussian_filter(backing, 2.5 * rs)
rgb *= (1 - 0.90 * backing[..., None])
rgb += backing[..., None] * np.array([0.012, 0.020, 0.038])
# inset frame stroke
fr = np.zeros((S, S), np.float32)
for (xa, ya, xb2, yb2) in [(IX0, IY0, IX1, IY0), (IX0, IY1, IX1, IY1),
                           (IX0, IY0, IX0, IY1), (IX1, IY0, IX1, IY1)]:
    rkit.line_splat(fr, np.array([float(xa)]), np.array([float(ya)]),
                    np.array([float(xb2)]), np.array([float(yb2)]),
                    np.array([1400.0 * rs]), npts=2600)
rgb += grey_dilation(fr, size=int(max(2, rs)))[..., None] * np.array([0.45, 0.55, 0.66]) * 0.35
# inset waterline
iw = np.zeros((S, S), np.float32)
rkit.line_splat(iw, np.array([float(ipx(WX0))]), np.array([float(ipy(0))]),
                np.array([float(ipx(WX1))]), np.array([float(ipy(0))]),
                np.array([240.0 * rs]), npts=int(S * 0.4))
rgb += grey_dilation(iw, size=int(max(2, rs)))[..., None] * np.array([0.85, 0.72, 0.38]) * 0.16
# island thread: thin to ~3 pts/px
stepi = max(1, len(xw) // ((IX1 - IX0) * 3))
xw2, Lw2 = xw[::stepi], Lw[::stepi]
above = Lw2 > 0
it = np.zeros((S, S), np.float32)
ia = np.zeros((S, S), np.float32)
rkit.line_splat(it, ipx(xw2[:-1]), ipy(Lw2[:-1]), ipx(xw2[1:]), ipy(Lw2[1:]),
                2.2 * rs, npts=6)
seg_above = above[:-1] | above[1:]
if seg_above.any():
    rkit.line_splat(ia, ipx(xw2[:-1][seg_above]), ipy(Lw2[:-1][seg_above]),
                    ipx(xw2[1:][seg_above]), ipy(Lw2[1:][seg_above]),
                    4.5 * rs, npts=6)
itd = grey_dilation(it, size=int(max(2, rs)))
iad = grey_dilation(ia, size=int(max(2, 1.2 * rs)))
rgb += itd[..., None] * np.array([0.45, 0.75, 0.85]) * 0.5
rgb += gaussian_filter(itd, 2.5 * rs)[..., None] * np.array([0.45, 0.75, 0.85]) * 0.35
rgb += iad[..., None] * gold * 0.5
rgb += gaussian_filter(iad, 4.0 * rs)[..., None] * gold * 0.65
# gold fill above waterline inside inset
colg = np.full(S, np.nan)
ci = np.clip(ipx(xw2).astype(int), 0, S - 1)
np.maximum.reduceat  # noqa
for c, Lv in zip(ci, Lw2):
    if np.isnan(colg[c]) or Lv > colg[c]:
        colg[c] = Lv
rowsv = np.linspace(WY1, WY0, IY1 - IY0)
sub = np.zeros((IY1 - IY0, S), np.float32)
for c in range(IX0, IX1):
    Lv = colg[c]
    if not np.isnan(Lv) and Lv > 0:
        m = (rowsv > 0) & (rowsv < Lv)
        sub[m, c] = np.clip(rowsv[m] / max(Lv, 1), 0, 1) ** 0.5
rgb[IY0:IY1] += (sub[..., None] * gold * 0.22)[:, :, :]
# peak star at L = 829
ipk = np.argmax(Lw)
pk = np.zeros((S, S), np.float32)
rkit.splat_points(pk, [float(ipx(xw[ipk]))], [float(ipy(Lw[ipk]))], 1500.0 * rs)
rgb += gaussian_filter(pk, 2.5 * rs)[..., None] * np.array([1.0, 0.95, 0.75]) * 0.8
rgb += gaussian_filter(pk, 12.0 * rs)[..., None] * gold * 0.4
# lens beams: inset corners -> breach star
lb = np.zeros((S, S), np.float32)
for (cx, cy) in [(IX1, IY0), (IX1, IY1)]:
    rkit.line_splat(lb, np.array([float(cx)]), np.array([float(cy)]),
                    np.array([float(px(xbr))]), np.array([float(py(0.0))]),
                    np.array([120.0 * rs]), npts=2000)
rgb += gaussian_filter(lb, 1.5 * rs)[..., None] * np.array([0.75, 0.65, 0.40]) * 0.30
print(f'inset {time.time()-t0:.0f}s')

# --------------------------------------------------- finish
rgb = rkit.bloom(rgb, sigma=5 * rs, gain=0.5, mask_thresh=0.55)
rgb = rkit.filmic(rgb, k=1.4, gamma=0.88)
out = rkit.downscale(rgb, FINAL)
out = rkit.caption(out, [
    'THE NINE HUNDRED MILLION WINTERS',
    "polya's conjecture (1919): counting integers with an odd vs even number of prime factors, the odd kind never falls behind -",
    'L(x) = sum of liouville lambda(n), n <= x, stays <= 0 for all x >= 2. the coastline below is L(x)/sqrt(x), linear in x, computed',
    'from scratch: lambda sieved for every n <= 2^30 (own segmented C sieve, verified against sympy; L(10^6) = -530 as published),',
    'the conjecture holds for 906,150,254 consecutive integers - and breaks at x = 906,150,257 (Tanaka 1980, reproduced exactly:',
    'first L(x) > 0, L = +1). the inset magnifies the breach: an archipelago of 136 positive islands, 305,426 integers in all,',
    'peak L = +829 at x = 906,316,571, closing again by 906,488,079; within 2^30 the sea holds everywhere else (came within 2 at',
    'x = 48,512). haselgrove had proved the pretense must end (1958); the sea looked like a law for forty years.',
    'claude fable 5, 2026-07-31'],
    size=11.0)
rkit.to_img(out, 'polya_final.png')
print(f'saved polya_final.png  {time.time()-t0:.0f}s')
