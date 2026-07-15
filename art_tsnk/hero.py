"""HERO — Lyness pentagon map: every orbit returns in exactly five steps.

(x,y) -> (y, (y+1)/x)   (Zamolodchikov periodicity, cluster type A2)
Invariant pencil: (x+1)(y+1)(x+y+1) = K xy, chart (ln x, ln y).
Rings: level sets — ellipses at the golden fixed point, pentagons at the rim.
Every ring carries the ENVELOPE of its 5-cycle chords (a caustic);
a few chosen rings are flooded with the chords themselves (light-fog).
"""
import sys, math, time
import numpy as np
sys.path.insert(0, '.')
from kit import *

t0 = time.time()
S       = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
TAG     = sys.argv[2] if len(sys.argv) > 2 else 'proto'
SS      = 2
R       = S * SS
RSCALE  = R / 2048

PHI     = (1 + 5**0.5) / 2
FX      = math.log(PHI)
CENTER  = np.array([2.05, 0.75])      # off-diagonal: breaks the mirror in-frame
HALF    = 9.6
NRING   = 112
R_IN, R_OUT = 0.06, 11.8              # ring radii range (chart units, along diag)
FADE_START  = 8.2                     # rings dissolve into void beyond this
RING_PTS = 6000
NENV    = 2400                        # chord samples for envelope curves
FOG_RADII  = [3.1, 5.4, 7.8]
FOG2_RADII = [7.8]   # rings that get real chord fog
NFOG    = 3200

GAIN_RING  = 1.0
GAIN_ENV1  = 1.05
GAIN_ENV2  = 0.55
GAIN_FOG1  = 0.55
GAIN_FOG2  = 0.42
EXPO       = 1.25

GOLD    = hex_rgb('ffd27a'); GOLD2 = hex_rgb('ffc457')
VIOLET  = hex_rgb('9a7bff'); CYAN  = hex_rgb('7fd8e8')
WHITE   = np.array([1.0, 0.96, 0.86], np.float32)
RING_PAL = [(0.00, hex_rgb('ffe9b8')), (0.18, hex_rgb('f2bd6f')),
            (0.45, hex_rgb('d97f35')), (0.75, hex_rgb('8f3f1c')),
            (1.00, hex_rgb('4a2113'))]

def to_px(X, Y):
    u = (X - (CENTER[0] - HALF)) / (2 * HALF)
    v = (Y - (CENTER[1] - HALF)) / (2 * HALF)
    return u * R, (1 - v) * R

PX_PER_UNIT = R / (2 * HALF)

def K_of_diag(r):
    X = FX + r / math.sqrt(2)
    x = math.exp(X)
    return (x + 1) ** 2 * (2 * x + 1) / x ** 2

def branch_y(x, K):
    a = x + 1
    b = (x + 1) * (x + 2) - K * x
    c = (x + 1) ** 2
    disc = b * b - 4 * a * c
    disc = np.where(disc > 0, disc, np.nan)
    s = np.sqrt(disc)
    return (-b + s) / (2 * a), (-b - s) / (2 * a)

def ring_loop(K, n):
    def disc_u(u):
        x = np.exp(u)
        b = (x + 1) * (x + 2) - K * x
        return b * b - 4 * (x + 1) ** 3
    ug = np.linspace(-40, 40, 20001)
    d = disc_u(ug)
    pos = d > 0
    i0 = np.searchsorted(ug, FX)
    if not pos[i0]:
        return None
    lo = i0
    while lo > 0 and pos[lo - 1]:
        lo -= 1
    hi = i0
    while hi < len(ug) - 1 and pos[hi + 1]:
        hi += 1
    def bisect(ua, ub):
        for _ in range(60):
            um = 0.5 * (ua + ub)
            ua, ub = (ua, um) if disc_u(um) <= 0 else (ua, ub)
            if disc_u(um) > 0:
                ub = um
        return ub
    def bisect2(bad, good):
        for _ in range(60):
            m = 0.5 * (bad + good)
            if disc_u(m) > 0:
                good = m
            else:
                bad = m
        return good
    u_lo = bisect2(ug[lo - 1], ug[lo]) if lo > 0 else ug[0]
    u_hi = bisect2(ug[hi + 1], ug[hi]) if hi < len(ug) - 1 else ug[-1]
    span = u_hi - u_lo
    u = u_lo + span * 0.5 * (1 - np.cos(np.linspace(0, math.pi, n // 2)))  # cluster at turns
    x = np.exp(u)
    y_up, y_dn = branch_y(x, K)
    good = np.isfinite(y_up) & np.isfinite(y_dn) & (y_up > 0) & (y_dn > 0)
    u, x, y_up, y_dn = u[good], x[good], y_up[good], y_dn[good]
    loopX = np.concatenate([u, u[::-1]])
    loopY = np.concatenate([np.log(y_up), np.log(y_dn[::-1])])
    return loopX, loopY

def resample_arc(loopX, loopY, n):
    dx = np.diff(np.append(loopX, loopX[0]))
    dy = np.diff(np.append(loopY, loopY[0]))
    seg = np.hypot(dx, dy)
    tcum = np.concatenate([[0], np.cumsum(seg)])
    tt = np.linspace(0, tcum[-1], n, endpoint=False)
    Xr = np.interp(tt, tcum, np.append(loopX, loopX[0]))
    Yr = np.interp(tt, tcum, np.append(loopY, loopY[0]))
    return Xr, Yr, tcum[-1]

def chord_endpoints(Xa, Ya, step):
    """apply f (step times) to points given in chart coords; return chart endpoint"""
    x, y = np.exp(Xa), np.exp(Ya)
    for _ in range(step):
        x, y = y, (y + 1) / x
    return np.log(x), np.log(y)

def envelope(Xa, Ya, Xb, Yb):
    """envelope of the 1-param closed family of chords A(t)->B(t):
    intersection of consecutive lines."""
    A = np.stack([Xa, Ya], 1)
    B = np.stack([Xb, Yb], 1)
    A2 = np.roll(A, -1, 0); B2 = np.roll(B, -1, 0)
    d1 = B - A; d2 = B2 - A2
    den = d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]
    rhs = A2 - A
    t = (rhs[:, 0] * d2[:, 1] - rhs[:, 1] * d2[:, 0]) / np.where(np.abs(den) < 1e-14, np.nan, den)
    P = A + d1 * t[:, None]
    return P[:, 0], P[:, 1]

# ---------------------------------------------------------------- layers
L_ring = canvas(R)
L_env1 = canvas_mono(R)
L_env2 = canvas_mono(R)
L_fog1 = canvas_mono(R)
L_fog2 = canvas_mono(R)
L_star = canvas(R)

radii = np.linspace(R_IN, R_OUT, NRING)
RING_MASS_PER_PX = 0.62

for j, r in enumerate(radii):
    K = K_of_diag(r)
    rp = ring_loop(K, RING_PTS)
    if rp is None:
        continue
    s = j / (NRING - 1)
    fade = 1.0 if r < FADE_START else max(0.0, 1 - (r - FADE_START) / (R_OUT - FADE_START)) ** 1.6
    ring_col = lerp_palette(RING_PAL, np.array([s]))[0]

    _, _, arc0 = resample_arc(rp[0], rp[1], 1500)
    nring_pts = int(np.clip(arc0 * PX_PER_UNIT * 1.6, 1200, 90000))
    Xr, Yr, arc = resample_arc(rp[0], rp[1], nring_pts)
    pX, pY = to_px(Xr, Yr)
    onscr = (pX > -8) & (pX < R + 8) & (pY > -8) & (pY < R + 8)
    n_on = int(onscr.sum())
    if n_on > 10:
        perim_px = arc * PX_PER_UNIT * (n_on / nring_pts)
        wr = RING_MASS_PER_PX * perim_px / n_on * fade
        splat_points(L_ring, pX[onscr], pY[onscr], wr, ring_col)

    # envelope caustics of the two chord families
    Xa, Ya, _ = resample_arc(rp[0], rp[1], int(NENV * max(1, RSCALE)))
    for step, L_env in ((1, L_env1),):
        Xb, Yb = chord_endpoints(Xa, Ya, step)
        eX, eY = envelope(Xa, Ya, Xb, Yb)
        good = np.isfinite(eX) & np.isfinite(eY)
        eXp, eYp = to_px(eX[good], eY[good])
        m = (eXp > -8) & (eXp < R + 8) & (eYp > -8) & (eYp < R + 8)
        if m.sum() > 10:
            # constant mass per px along envelope
            exm, eym = eXp[m], eYp[m]
            seg = np.hypot(np.diff(exm), np.diff(eym))
            seg = np.clip(seg, 0, 30)  # kill jump artifacts at cusps
            wpt = np.concatenate([[0], seg]) * 0.5 + np.concatenate([seg, [0]]) * 0.5
            splat_points_mono(L_env, R, exm, eym, wpt * 0.62 * fade)
    if j % 20 == 0:
        print(f'ring {j}/{NRING} r={r:.2f} K={K:.3g} t={time.time()-t0:.0f}s', flush=True)

# chord fog on the chosen rings
for r in FOG_RADII:
    K = K_of_diag(r)
    rp = ring_loop(K, RING_PTS)
    if rp is None:
        continue
    Xa, Ya, _ = resample_arc(rp[0], rp[1], NFOG)
    steps = [(1, L_fog1, 0.045)] + ([(2, L_fog2, 0.040)] if r in FOG2_RADII else [])
    for step, L_fog, cw in steps:
        Xb, Yb = chord_endpoints(Xa, Ya, step)
        aX, aY = to_px(Xa, Ya)
        bX, bY = to_px(Xb, Yb)
        splat_segments_mono(L_fog, R, aX, aY, bX, bY, cw)
print(f'fog done t={time.time()-t0:.0f}s', flush=True)

# hero orbits: three explicit 5-cycles — beads + bright chords
for hr, ph in ((2.4, 0.16), (5.9, 0.62)):
    K = K_of_diag(hr)
    rp = ring_loop(K, RING_PTS)
    Xa, Ya, _ = resample_arc(rp[0], rp[1], 1000)
    i = int(ph * 1000)
    p = (math.exp(Xa[i]), math.exp(Ya[i]))
    orb = [p]
    for _ in range(4):
        px_, py_ = orb[-1]
        orb.append((py_, (py_ + 1) / px_))
    pts = np.array([to_px(math.log(a), math.log(b)) for a, b in orb])
    import numpy as _np
    for k in range(5):
        a_, b_ = pts[k], pts[(k + 1) % 5]
        Lpx = _np.hypot(b_[0]-a_[0], b_[1]-a_[1])
        splat_segments(L_star, [a_[0]], [a_[1]], [b_[0]], [b_[1]], 0.048 * SS * Lpx, GOLD2)
    for k in range(5):
        a_, b_ = pts[k], pts[(k + 2) % 5]
        Lpx = _np.hypot(b_[0]-a_[0], b_[1]-a_[1])
        splat_segments(L_star, [a_[0]], [a_[1]], [b_[0]], [b_[1]], 0.026 * SS * Lpx, CYAN * 0.9)
    th = np.linspace(0, 2 * math.pi, 64, endpoint=False)
    ps = SS * RSCALE
    for a_ in pts:
        for rad, ww in ((0.0, 2.4), (1.1 * ps, 1.2), (2.2 * ps, 0.45)):
            splat_points(L_star, a_[0] + rad * np.cos(th), a_[1] + rad * np.sin(th),
                         ww * ps / 64, WHITE)

# the golden fixed point — compact blazing star
fx, fy = to_px(FX, FX)
th = np.linspace(0, 2 * math.pi, 256, endpoint=False)
ps = SS * RSCALE
for rad, ww in ((0, 10), (1.2 * ps, 5), (2.6 * ps, 2.2), (4.5 * ps, 0.9)):
    splat_points(L_star, fx + rad * np.cos(th), fy + rad * np.sin(th),
                 ww * ps / 256, np.array([1.0, 0.93, 0.72], np.float32))
# warm core glow — an inner sun at the golden point
yy, xx = np.mgrid[0:R, 0:R].astype(np.float32)
gsig = 1.6 * PX_PER_UNIT
core = np.exp(-(((xx - fx) ** 2 + (yy - fy) ** 2) / (2 * gsig ** 2))).astype(np.float32)
L_glow = core[..., None] * np.array([1.0, 0.72, 0.42], np.float32)[None, None, :]
del xx, yy, core
print(f'stars done t={time.time()-t0:.0f}s', flush=True)

# ---------------------------------------------------------------- compose
def norm99(L):
    v = L.mean(2)
    p = np.percentile(v[v > 0], 99.2) if (v > 0).any() else 1.0
    return L / max(p, 1e-9)

def norm99m(Lm, q=99.2):
    v = Lm[Lm > 0]
    p = np.percentile(v, q) if v.size else 1.0
    return (Lm / max(p, 1e-9)).reshape(R, R)

if RSCALE > 1.5:
    from scipy.ndimage import gaussian_filter as _gf
    L_star = L_star + 0.85 * _gf(L_star, (1.1 * SS * RSCALE / 2, 1.1 * SS * RSCALE / 2, 0))

img = (GAIN_RING * norm99(L_ring)
       + GAIN_ENV1 * norm99m(L_env1)[..., None] * GOLD[None, None, :]
       + GAIN_ENV2 * norm99m(L_env2)[..., None] * VIOLET[None, None, :]
       + GAIN_FOG1 * norm99m(L_fog1)[..., None] * (GOLD2[None, None, :] * 0.9)
       + GAIN_FOG2 * norm99m(L_fog2)[..., None] * VIOLET[None, None, :]
       + 1.9 * norm99(L_star) + 0.45 * L_glow)

img = bloom_add(img, tight=max(2, 0.0015 * R), wide=0.030 * R, t_amt=0.45, w_amt=0.22, thresh=0.75)
u8 = tonemap(img, k=EXPO, gamma=0.84, sat=1.08)
from PIL import Image
Image.fromarray(u8).resize((S, S), Image.LANCZOS).save(f'hero_{TAG}.png')
print(f'saved hero_{TAG}.png t={time.time()-t0:.0f}s')
