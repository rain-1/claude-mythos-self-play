"""stalls.py — 'Eighteen Turns of One Wish List'  (Pollak's circle argument for parking functions)
Seventeen camels come in one at a time to a round caravanserai of EIGHTEEN stalls (seventeen and the
one that was lent).  Each has a favourite stall; if it is taken it walks on clockwise to the next
free one.  One stall is left empty.  Turn every wish one stall round and the empty stall turns with
it: of the eighteen turnings exactly one leaves the lent stall (red keystone, top) empty.
Each roundel is one turning.  Outer ring: the 18 stalls, coloured by how far their camel had to walk
past its wish (gold = none), night blue = the empty stall.  Inner ring: how many camels wished for it.
usage: stalls.py SIZE out.png"""
import sys, numpy as np
from scipy import ndimage as ndi
from mosaic import Mosaic, polar_tess, tess, C, rnd, save, text_mask, marble, incise

N = 17; K = N + 1
def park(w):
    occ = [-1] * K; disp = [0] * K
    for i, s in enumerate(w):
        d = 0
        while occ[(s + d) % K] >= 0: d += 1
        occ[(s + d) % K] = i; disp[(s + d) % K] = d
    return occ, disp
def choose():
    best = None
    for seed in range(4000):
        r = np.random.default_rng(seed); w = r.integers(0, K, N)
        occ, disp = park(w); cnt = np.bincount(w, minlength=K)
        ok = max(disp) >= 5 and sum(d == 0 for d, o in zip(disp, occ) if o >= 0) in (9, 10) and cnt.max() == 3 and len(set(disp)) >= 6
        if ok: return w
    raise SystemExit('no list')
W0 = choose()
# sanity: exactly one turning leaves stall 0 empty
empt = [park((W0 + t) % K)[0].index(-1) for t in range(K)]
assert sorted(empt) == list(range(K))
TSTAR = empt.index(0)

DISP = ["gol0", "apr0", "apr2", "ros0", "ros1", "mau0", "mau1", "mau1", "mau1"]
WISH = ["lap1", "tur2", "tur4", "mar0"]

def roundel(M, cx, cy, h, q, w, key, winner):
    """one turning, laid in rings about its own centre. h = row height, q = rows multiplier"""
    S = M.S; R = 14 * q * h; n = M.n
    x0, x1, y0, y1 = int(max(cx - R - 3, 0)), int(min(cx + R + 3, n)), int(max(cy - R - 3, 0)), int(min(cy + R + 3, n))
    sl = (slice(y0, y1), slice(x0, x1)); X = M.X[sl]; Y = M.Y[sl]
    T, xc, yc = polar_tess(X, Y, cx, cy, h, key, w=h * 1.05)
    rho = np.hypot(X - cx, Y - cy); rows = rho / (h * q)
    ang = np.mod(np.degrees(np.arctan2(X - cx, -(Y - cy))) + 10.0, 360.0)       # clockwise from top, stall 0 centred on top
    st = np.minimum((ang / 20.0).astype(np.int32), K - 1)
    occ, disp = park(w); cnt = np.bincount(w, minlength=K)
    col = np.empty(X.shape + (3,), np.float32); col[:] = C("lap0"); mat = np.zeros(X.shape, np.uint8)
    core = rows < 3; wish = (rows >= 4) & (rows < 7); stall = (rows >= 8) & (rows < 12); rim = (rows >= 12.6) & (rows < 14)
    col[core] = C("lap1")
    wcol = np.array([C(WISH[min(c, 3)]) for c in cnt]); col[wish] = wcol[st[wish]]
    scol = np.array([C("lap0") if occ[s] < 0 else C(DISP[disp[s]]) for s in range(K)])
    if occ[0] < 0: scol[0] = C("red1")
    col[stall] = scol[st[stall]]
    gold = stall & (np.array([occ[s] >= 0 and disp[s] == 0 for s in range(K)])[st])
    mat[gold] = 1
    col[rim] = C("gol1") if winner else C("mar1")
    if winner: mat[rim] = 1
    key_m = (rows >= 12.6) & (rows < 14) & (st == 0)
    col[key_m] = C("red0"); mat[key_m] = 0
    inside = rows < 14
    M.lay(inside, T, col, mat=mat, sl=sl)
    # cut the joints of the design: ring edges and stall walls
    wj = 1.7 * S + 0.6
    d = np.full(X.shape, 1e6, np.float32)
    for rr in (3, 4, 7, 8, 12, 12.6, 14): d = np.minimum(d, np.abs(rho - rr * q * h))
    a = np.radians(np.abs(np.mod(ang, 20.0) - 10.0) - 10.0)                     # 0 at a stall wall
    wall = np.abs(np.sin(a)) * rho
    d = np.where(wish | stall | key_m | (rim & (np.abs(ang - 10) < 14)), np.minimum(d, wall), d)
    e = M.edge[sl]; e[inside] = np.minimum(e[inside], (d - wj * 0.5)[inside])
    return core, sl, X, Y

def main():
    n = int(sys.argv[1]); out = sys.argv[2]; S = n / 4096.0
    M = Mosaic(n, seed=4, grout=(0.50, 0.48, 0.46))
    X, Y = M.X, M.Y
    FX0, FX1, FY0, FY1 = 368 * S, 3728 * S, 200 * S, 3560 * S; cx, cy = (FX0 + FX1) / 2, (FY0 + FY1) / 2
    field = (X >= FX0) & (X < FX1) & (Y >= FY0) & (Y < FY1)
    h = 14.5 * S
    # ---- the night floor: rings about the middle, a few gold stars -------------------------
    T, xc, yc = polar_tess(X, Y, cx, cy, 17 * S, 101)
    rho = np.hypot(xc - cx, yc - cy) / (1680 * S)
    rs = np.random.RandomState(3); big = ndi.zoom(ndi.gaussian_filter(rs.randn(48, 48), 3), n / 48, order=1)[:n, :n]; big = big / np.abs(big).max()
    t = np.clip(0.50 - 0.42 * rho + 0.9 * big + 0.24 * (rnd(T.id, 2) - 0.5), 0, 1)[..., None]
    col = np.where(t < 0.5, C("lap0") * (1 - 2 * t) + C("lap1") * (2 * t), C("lap1") * (2 - 2 * t) + C("lap2") * (2 * t - 1)).astype(np.float32)
    star = rnd(T.id, 77) < 0.013
    col[star] = C("gol0"); mat = np.where(star, 1, 0).astype(np.uint8)
    M.lay(field, T, col, mat=mat)
    # ---- border band ------------------------------------------------------------------------
    dedge = np.minimum(np.minimum(X - FX0, FX1 - X), np.minimum(Y - FY0, FY1 - Y))
    band = field & (dedge < 64 * S)
    horiz = np.minimum(Y - FY0, FY1 - Y) <= np.minimum(X - FX0, FX1 - X)
    Tb_h = tess(X, dedge, 16 * S, 201, w=17 * S); Tb_v = tess(Y, dedge, 16 * S, 202, w=17 * S)
    rowb = (dedge // (16 * S)).astype(int)
    bcol = np.array([C("mar1"), C("umb0"), C("mar1"), C("lap0")])[np.clip(rowb, 0, 3)]
    M.lay(band & horiz, Tb_h, bcol); M.lay(band & ~horiz, Tb_v, bcol)
    # ---- eighteen turnings on a ring, the winner at the top ----------------------------------
    RB = 1318 * S
    for t in range(K):
        pos = (t - TSTAR) % K; a = np.radians(20.0 * pos)
        roundel(M, cx + RB * np.sin(a), cy - RB * np.cos(a), h, 1, (W0 + t) % K, 300 + t, pos == 0)
    # ---- the middle: the winning turning, four times as large, a moon in the well ------------
    core, sl, Xc, Yc = roundel(M, cx, cy, h, 4, (W0 + TSTAR) % K, 500, True)
    Tm, _, _ = polar_tess(Xc, Yc, cx, cy, h, 500, w=h * 1.05)
    moon = (np.hypot(Xc - cx + 20 * S, Yc - cy) < 96 * S) & ~(np.hypot(Xc - cx - 26 * S, Yc - cy + 26 * S) < 88 * S)
    M.lay(moon, Tm, C("mar0"), sl=sl); M.cut(moon, sl=sl)
    st2 = core & ~moon & (rnd(Tm.id, 78) < 0.03)
    M.lay(st2, Tm, C("gol0"), mat=1, sl=sl)
    # ---- surround -----------------------------------------------------------------------------
    M.mat[~field] = 9; slab = marble(n, 12, base=(0.935, 0.915, 0.87)); M.rgb[~field] = slab[~field]
    img = M.finish()
    # shadow line where floor meets slab
    sh = ndi.gaussian_filter(field.astype(np.float32), 5 * S)
    img = np.where(field[..., None], img, img * (0.80 + 0.20 * (1 - np.clip(sh * 2, 0, 1)))[..., None])
    mx = n / 2
    items = [("EIGHTEEN TURNS OF ONE WISH LIST", mx, 3722 * S, 104 * S, "Regular", 10 * S),
             ("Seventeen camels, eighteen stalls in a ring: each camel takes its favourite stall or the next free one clockwise, and one stall stays empty.", mx, 3808 * S, 46 * S, "Italic", 0),
             ("Turn every wish one stall round and the empty stall turns too. So of the eighteen turnings exactly one leaves the lent stall, under the red keystone, empty.", mx, 3868 * S, 46 * S, "Italic", 0),
             ("outer ring: how far each camel walked past its wish (gold = not at all)  ·  inner ring: how many wished for that stall  ·  hence 18¹⁶ lists that fit a row of seventeen", mx, 3944 * S, 38 * S, "Regular", 0)]
    img = incise(img, text_mask(n, items), S, depth=0.62)
    save(img, out)
    print('wishes', list(W0), 'winning turn', TSTAR)

if __name__ == "__main__":
    main()
