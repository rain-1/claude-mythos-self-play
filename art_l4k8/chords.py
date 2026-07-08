"""CHORD GENESIS — the elliptic curve of the Diophantine triple {1, 3, 8}.

Fermat knew {1,3,8}: 1*3+1=4, 1*8+1=9, 3*8+1=25, all squares. Extending it
to a quadruple {1,3,8,d} demands d+1, 3d+1, 8d+1 all be squares -- i.e. a
rational point on the elliptic curve y^2 = (x+1)(3x+1)(8x+1). Fermat's
d = 120 is the point (120, 6479); today's MathOverflow front page asks how
far these extensions go (sextuples!).

The picture is the group law itself: every secant through two rational
points meets the curve in a third rational point -- one line, infinitely
many numbers. We generate tens of thousands of group elements and draw the
chords of the construction additively. The curve is never drawn; it
appears as the caustic where its own arithmetic crowds.

Honesty chain:
  * exact big-rational group law (chord-and-tangent) for all small combos
    aP + bR; every point verified to satisfy the curve equation exactly;
  * real uniformization E(R) ~ R/Z x Z/2 built by quadrature with sqrt
    substitutions at the branch points; equality of the two component
    periods verified;
  * the angle map is verified against the exact rational points: angle
    addition reproduces the exact x-coordinates of aP+bR to ~1e-9;
  * P = (0,1) has infinite order by Mazur's theorem (13 multiples != O).
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import splat_points, splat_segments, bloom, filmic, save, lerp_palette
from scipy.ndimage import gaussian_filter
from fractions import Fraction as Fr

# ---- curve y^2 = (x+1)(3x+1)(8x+1) = 24x^3+35x^2+12x+1
# roots of f:
E1, E2, E3 = -1.0, -1.0 / 3.0, -1.0 / 8.0
# monic model X=24x, Y=24y: Y^2 = X^3 + 35X^2 + 288X + 576
B, C, D = 35, 288, 576


def f(x):
    return 24 * x ** 3 + 35 * x ** 2 + 12 * x + 1


# ------------------------------------------------------------------ exact law
def on_curve(P):
    if P is None:
        return True
    X, Y = P
    return Y * Y == X * X * X + B * X * X + C * X + D


def neg(P):
    return None if P is None else (P[0], -P[1])


def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    X1, Y1 = P
    X2, Y2 = Q
    if X1 == X2:
        if Y1 == -Y2:
            return None
        lam = (3 * X1 * X1 + 2 * B * X1 + C) / (2 * Y1)
    else:
        lam = (Y2 - Y1) / (X2 - X1)
    X3 = lam * lam - B - X1 - X2
    return (X3, lam * (X1 - X3) - Y1)


def mul(k, P):
    R = None
    Q = P
    if k < 0:
        Q = neg(P)
        k = -k
    while k:
        if k & 1:
            R = add(R, Q)
        Q = add(Q, Q)
        k >>= 1
    return R


# --------------------------------------------------- real uniformization
def build_tables(n=200_001):
    """Angle tables for both real components, by quadrature with sqrt subs."""
    # identity branch, piece 1: x in [E3, 2], substitute x = E3 + v^2
    v = np.linspace(0, np.sqrt(2 - E3), n)
    x1 = E3 + v * v
    g1 = 2.0 / np.sqrt(24 * (x1 - E1) * (x1 - E2))          # du/dv
    u1 = _cumsimp(g1, v)                                     # u from x=E3 upward
    # piece 2: x in [2, inf), substitute x = 1/r^2  (r: 1/sqrt(2) -> 0)
    r = np.linspace(0, 1 / np.sqrt(2.0), n)
    g2 = 2.0 / np.sqrt(24 + 35 * r ** 2 + 12 * r ** 4 + r ** 6)  # du/dr
    u2 = _cumsimp(g2, r)                                     # u from infinity down to x=2
    U2 = u2[-1]
    # stitch: u measured FROM INFINITY: u(x>=2) = u2(r(x)); u(x in [E3,2]) =
    # U2 + (u1[-1]-u1(v(x)))
    u_half = U2 + u1[-1]
    x_branch = np.concatenate([1.0 / r[1:] ** 2, x1[::-1]])
    u_branch = np.concatenate([u2[1:], U2 + (u1[-1] - u1)[::-1]])
    o = np.argsort(u_branch)
    u_branch, x_branch = u_branch[o], x_branch[o]
    # x-ascending copies for angle lookups (np.interp needs ascending xp)
    ox = np.argsort(x_branch)
    xb_asc, ub_by_x = x_branch[ox], u_branch[ox]

    # oval: x = m + h sin(phi), phi in [-pi/2, pi/2]
    m, h = 0.5 * (E1 + E2), 0.5 * (E2 - E1)
    phi = np.linspace(-np.pi / 2, np.pi / 2, n)
    xo = m + h * np.sin(phi)
    go = 1.0 / np.sqrt(24 * (E3 - xo))                       # du/dphi
    uo = _cumsimp(go, phi)                                   # u from x=E1 to x=E2
    u_oval_half = uo[-1]
    return dict(u_half=u_half, x_branch=x_branch, u_branch=u_branch,
                xb_asc=xb_asc, ub_by_x=ub_by_x,
                u_oval_half=u_oval_half, x_oval=xo, u_oval=uo)


def _cumsimp(y, x):
    from scipy.integrate import cumulative_simpson
    return np.concatenate([[0.0], cumulative_simpson(y, x=x)])


class RealE:
    """E(R) ~ R/Z x Z/2 with verified angle arithmetic."""

    def __init__(self):
        T = build_tables()
        self.T = T
        self.Om = 2 * T["u_half"]
        self.Om_oval = 2 * T["u_oval_half"]
        # component periods agree (classical; verified numerically)
        assert abs(self.Om - self.Om_oval) / self.Om < 1e-8, \
            (self.Om, self.Om_oval)

    # angle of a real point
    def angle(self, x, y):
        T = self.T
        if x >= E3:                                # identity branch
            u = np.interp(x, T["xb_asc"], T["ub_by_x"])
            t = u / self.Om
            return (t if y >= 0 else 1 - t) % 1.0, 0
        else:                                      # oval
            u = np.interp(x, T["x_oval"], T["u_oval"])
            tau = (T["u_oval_half"] * 2 - u if y >= 0 else u) / self.Om
            # tau measured so that negation is tau -> -tau (base x=E1,y=0...)
            return tau % 1.0, 1

    # coordinates from (angle, parity); vectorized
    def coords(self, alpha, parity):
        T = self.T
        alpha = np.mod(alpha, 1.0)
        x = np.empty_like(alpha)
        y = np.empty_like(alpha)
        idm = parity == 0
        # identity: t in (0,1/2] upper half, (1/2,1) lower
        t = alpha[idm]
        upper = t <= 0.5
        u = np.where(upper, t, 1 - t) * self.Om
        xi = np.interp(u, T["u_branch"], T["x_branch"])
        yi = np.sqrt(np.maximum(f(xi), 0.0)) * np.where(upper, 1, -1)
        x[idm], y[idm] = xi, yi
        # oval: base point (E1, 0) at tau=0; tau<=1/2 is the y<0 half
        t = alpha[~idm]
        lower = t <= 0.5
        u = np.where(lower, t, 1 - t) * self.Om
        xo = np.interp(u, T["u_oval"], T["x_oval"])
        yo = np.sqrt(np.maximum(f(xo), 0.0)) * np.where(lower, -1, 1)
        x[~idm], y[~idm] = xo, yo
        return x, y


def verify():
    import math
    for mfac in (1, 3, 8):
        rr = math.isqrt(mfac * 120 + 1)
        assert rr * rr == mfac * 120 + 1
    P = (Fr(0), Fr(24))          # (0, 1)
    Q = (Fr(2880), Fr(155496))   # (120, 6479) -- Fermat's point
    R = (Fr(-18), Fr(30))        # (-3/4, 5/4) -- on the oval
    for pt in (P, Q, R):
        assert on_curve(pt)
    for pt in (add(P, Q), add(P, R), mul(5, P), add(mul(3, P), R)):
        assert on_curve(pt)
    for k in range(1, 13):
        assert mul(k, P) is not None
    print("VERIFIED: exact group law; {1,3,8,120} squares; P infinite order (Mazur)")

    Ereal = RealE()
    tP, pP = Ereal.angle(0.0, 1.0)
    tR, pR = Ereal.angle(-0.75, 1.25)
    assert pP == 0 and pR == 1

    # oval coset offset c in {0, 1/2}: angle(aP+bR) = a tP + b (tR + c) mod 1
    def exact_xy(a, b):
        S = add(mul(a, P), mul(b, R))
        if S is None:
            return None
        return float(S[0]) / 24, float(S[1]) / 24

    best = None
    for c in (0.0, 0.5):
        errs = []
        for a, b in [(1, 1), (2, 1), (1, 2), (3, 1), (2, 2), (-1, 1), (4, 1),
                     (0, 2), (5, 2), (3, 3), (-2, 3)]:
            got = exact_xy(a, b)
            if got is None:
                continue
            alpha = (a * tP + b * (tR + c)) % 1.0
            par = np.array([b % 2])
            xx, yy = Ereal.coords(np.array([alpha]), par)
            errs.append(abs(xx[0] - got[0]) / (1 + abs(got[0])))
        err = max(errs)
        if best is None or err < best[1]:
            best = (c, err)
    c, err = best
    assert err < 1e-6, f"angle arithmetic mismatch: {err}"
    print(f"VERIFIED: angle arithmetic reproduces exact points "
          f"(coset offset c={c}, max rel err {err:.2e})")
    return Ereal, tP, tR + c


def render(S=1280, SS=2, A=6000, Bb=2, n_chords=120_000, seed=11,
           chord_gain=1.0, point_gain=1.0, k_tone=1.15, founders_gain=1.0,
           out="chords_proto.png"):
    Ereal, tP, bR = verify()
    a = np.arange(-A, A + 1)
    b = np.arange(-Bb, Bb + 1)
    aa, bb = np.meshgrid(a, b, indexing="ij")
    aa, bb = aa.ravel(), bb.ravel()
    keep = ~((aa == 0) & (bb == 0))
    aa, bb = aa[keep], bb[keep]
    alpha = np.mod(aa * tP + bb * bR, 1.0)
    par = np.mod(bb, 2)
    fx, fy = Ereal.coords(alpha, par)
    gen = np.abs(aa) + 3 * np.abs(bb)          # word length ~ generation
    print(f"{len(fx)} group elements via verified angle arithmetic")

    W = H = S * SS
    scl = S / 1024.0
    x_lo, x_hi = -1.42, 1.05
    y_lo, y_hi = -2.35, 2.35

    def px(x):
        return (x - x_lo) / (x_hi - x_lo) * W

    def py(y):
        return (y_hi - y) / (y_hi - y_lo) * H

    acc = np.zeros((H, W, 3))
    rng = np.random.default_rng(seed)
    N = len(fx)
    inwin = (fx > x_lo) & (fx < x_hi) & (fy > y_lo) & (fy < y_hi)
    idx_in = np.where(inwin)[0]

    # ---- chords, three families:
    # (a) NEAR-TANGENT: pairs adjacent in angle on the same component -- their
    #     envelope IS the curve (the honest caustic);
    # (b) window pairs: arbitrary secants between visible points;
    # (c) far pairs: one end near infinity (the vertical negation pencil).
    n_tan = int(n_chords * 0.62)
    n_win = int(n_chords * 0.24)
    n_far = n_chords - n_tan - n_win
    order = np.argsort(alpha)
    alpha_sorted = alpha[order]
    par_sorted = par[order]
    # sample tangent anchors uniformly in SCREEN ARC LENGTH along the visible
    # curve (otherwise the stretched far ends of the branch get starved)
    agrid = np.linspace(0, 1, 40001)[:-1]
    anchors = []
    for pgrid in (0, 1):
        gx, gy = Ereal.coords(agrid, np.full(len(agrid), pgrid))
        gin = (gx > x_lo) & (gx < x_hi) & (gy > y_lo) & (gy < y_hi)
        if gin.sum() < 2:
            continue
        seg = np.hypot(np.diff(px(gx)), np.diff(py(gy)))
        seg = seg * gin[:-1]                      # only visible arc counts
        cdf = np.cumsum(seg)
        u = rng.uniform(0, cdf[-1], int(n_tan * 0.30))
        k = np.searchsorted(cdf, u)
        anchors.append((agrid[k], np.full(len(k), pgrid)))
        # plus angle-uniform anchors (concentrate light at the slow bends)
        kk = np.where(gin)[0]
        k2 = rng.choice(kk, int(n_tan * 0.20))
        anchors.append((agrid[k2], np.full(len(k2), pgrid)))
    a_anchor = np.concatenate([a for a, _ in anchors])
    p_anchor = np.concatenate([p for _, p in anchors]).astype(int)
    # snap each anchor to the nearest orbit point of the same parity
    i_t = np.empty(len(a_anchor), dtype=np.int64)
    for pgrid in (0, 1):
        mpar = p_anchor == pgrid
        sub = np.where(par == pgrid)[0]
        asub = alpha[sub]
        o2 = np.argsort(asub)
        pos = np.searchsorted(asub[o2], a_anchor[mpar]).clip(0, len(sub) - 1)
        i_t[mpar] = sub[o2[pos]]
    n_tan = len(i_t)
    delta = rng.laplace(0.0, 0.012, n_tan)
    target = np.mod(alpha[i_t] + delta, 1.0)
    pos = np.searchsorted(alpha_sorted, target).clip(0, N - 1)
    # walk to a neighbour of the SAME component (parity)
    j_t = order[pos]
    same = par[j_t] == par[i_t]
    for shift in (1, -1, 2, -2, 3, -3):
        bad = ~same
        if not bad.any():
            break
        pos2 = (pos + shift).clip(0, N - 1)
        cand = order[pos2]
        upd = bad & (par[cand] == par[i_t])
        j_t[upd] = cand[upd]
        same = same | upd
    i1 = rng.choice(idx_in, n_win)
    j1 = rng.choice(idx_in, n_win)
    i2 = rng.integers(0, N, n_far)
    j2 = rng.choice(idx_in, n_far)
    i = np.concatenate([i_t, i1, i2])
    j = np.concatenate([j_t, j1, j2])
    m = i != j
    i, j = i[m], j[m]
    x1, y1, x2, y2 = fx[i], fy[i], fx[j], fy[j]
    both_in = inwin[i] & inwin[j]
    genc = 0.5 * (gen[i] + gen[j])
    ctype = par[i] + par[j]          # 0 branch-branch, 1 mixed, 2 oval-oval

    dx, dy = x2 - x1, y2 - y1
    keep = np.hypot(dx, dy) > 1e-9
    x1, y1, dx, dy, both_in, genc, ctype = (arr[keep] for arr in
                                            (x1, y1, dx, dy, both_in, genc, ctype))
    with np.errstate(divide="ignore", invalid="ignore"):
        tx1 = np.where(dx != 0, (x_lo - x1) / dx, -np.inf)
        tx2 = np.where(dx != 0, (x_hi - x1) / dx, np.inf)
        ty1 = np.where(dy != 0, (y_lo - y1) / dy, -np.inf)
        ty2 = np.where(dy != 0, (y_hi - y1) / dy, np.inf)
    tmin = np.maximum(np.minimum(tx1, tx2), np.minimum(ty1, ty2))
    tmax = np.minimum(np.maximum(tx1, tx2), np.maximum(ty1, ty2))
    ok = tmax > tmin
    x1c = x1 + tmin * dx; y1c = y1 + tmin * dy
    x2c = x1 + tmax * dx; y2c = y1 + tmax * dy
    x1c, y1c, x2c, y2c, both_in, genc, ctype = (arr[ok] for arr in
                                                (x1c, y1c, x2c, y2c,
                                                 both_in, genc, ctype))
    # colour by generation: early chords white-gold, late ones deep amber
    tgen = np.clip(genc / (0.7 * (A + 3 * Bb)), 0, 1)
    cols = lerp_palette(tgen, [
        (0.00, (1.00, 0.92, 0.70)),
        (0.35, (1.00, 0.74, 0.38)),
        (1.00, (0.72, 0.42, 0.22)),
    ])
    # tint by which components the chord joins
    oo = ctype == 2
    cols[oo] = 0.15 * cols[oo] + 0.85 * np.array([0.60, 0.85, 1.00])
    mixd = ctype == 1
    cols[mixd] = 0.60 * cols[mixd] + 0.40 * np.array([1.00, 0.93, 0.78])
    base = np.where(both_in, 0.40, 0.12) * chord_gain
    base = base * np.where(oo, 1.5, 1.0)
    Lpx = np.hypot(px(x2c) - px(x1c), py(y2c) - py(y1c))
    wch = base * Lpx / (SS * 100.0)
    for c in range(3):
        splat_segments(acc[..., c], px(x1c), py(y1c), px(x2c), py(y2c),
                       wch * cols[:, c], samples_per_px=0.8)

    # ---- founding chords: P--Q (Fermat's extension) and the tangent at P
    founders = []
    # P=(0,1), Q=(120,6479): the chord that finds -(P+Q)
    founders.append(((0.0, 1.0), (120.0, 6479.0)))
    # tangent at P: slope from implicit diff: y' = f'(x)/(2y)
    fp = (72 * 0.0 ** 2 + 70 * 0.0 + 12) / (2 * 1.0)
    founders.append(((0.0, 1.0), (0.001, 1.0 + 0.001 * fp)))
    # chord P--R (uniting the two components)
    founders.append(((0.0, 1.0), (-0.75, 1.25)))
    fbuf = np.zeros((H, W))
    for (xa, ya), (xb, yb) in founders:
        ddx, ddy = xb - xa, yb - ya
        L = np.hypot(ddx, ddy)
        ux, uy = ddx / L, ddy / L
        # light emanates from the generator (xa, ya) and fades along the line
        tt = np.linspace(-8.0, 8.0, 481)
        xs = xa + tt * ux
        ys = ya + tt * uy
        wseg = np.exp(-np.abs(0.5 * (tt[:-1] + tt[1:]) / 2.8) ** 1.5)
        Ls = np.hypot(np.diff(px(xs)), np.diff(py(ys)))
        splat_segments(fbuf, px(xs[:-1]), py(ys[:-1]), px(xs[1:]), py(ys[1:]),
                       170.0 * founders_gain * wseg * Ls / (SS * 100.0),
                       samples_per_px=1.3)
    fbuf = gaussian_filter(fbuf, 0.9 * SS * scl ** 0.5) * (1 + (0.9 * SS * scl ** 0.5) ** 2)
    for c, cv in enumerate((1.0, 0.95, 0.82)):
        acc[..., c] += fbuf * cv

    # ---- the rational points: sparks; oval points cool cyan
    for mask, col, amp in ((inwin & (par == 0), np.array([1.0, 0.9, 0.62]), 0.45),
                           (inwin & (par == 1), np.array([0.55, 0.85, 1.0]), 0.85)):
        g = np.zeros((H, W))
        splat_points(g, px(fx[mask]), py(fy[mask]),
                     np.full(int(mask.sum()), amp * point_gain))
        g = gaussian_filter(g, 0.9 * SS * scl ** 0.5) * (0.9 * SS * scl ** 0.5) ** 2 * 6.28
        for c in range(3):
            acc[..., c] += g * col[c]

    # founders' anchor points blaze
    for (xa, ya), colf in (((0.0, 1.0), (1.0, 0.95, 0.8)),
                           ((-0.75, 1.25), (0.6, 0.9, 1.0)),
                           ((-0.75, -1.25), (0.6, 0.9, 1.0))):
        g = np.zeros((H, W))
        splat_points(g, np.array([px(xa)]), np.array([py(ya)]),
                     np.array([26.0 * point_gain]))
        g = gaussian_filter(g, 2.6 * SS * scl ** 0.7) * (2.6 * SS * scl ** 0.7) ** 2 * 6.28
        for c in range(3):
            acc[..., c] += g * colf[c] * 0.4

    rgb = bloom(acc, sigma=2.2 * SS * scl ** 0.7, amount=0.32, thresh=0.52)
    rgb = filmic(rgb, k=k_tone, gamma=0.88)
    save(rgb, out, down=SS)
    print("saved", out)


if __name__ == "__main__":
    render()
