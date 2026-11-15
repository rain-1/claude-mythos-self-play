"""The Wythoff pairing on a sunflower.  Seed n sits at angle n/phi (turns) and radius sqrt(n).
LEMMA (checked below): with t = frac(k*phi),
   a_k = floor(k phi)   sits at angle  -t/phi    turns   (the wide sector, 222.5 degrees)
   b_k = floor(k phi^2) sits at angle  +t/phi^2  turns   (the wedge, 137.5 degrees)
so the twin of a seed is found by reflecting it in the seam, shrinking the angle by phi and
growing the radius by sqrt(phi).  Rings of equal k are therefore circles outside the wedge and
the same circles pushed out by sqrt(phi) inside it.
usage: python3 sunflower.py SIZE out.png"""
import sys, numpy as np
from math import isqrt
from scipy.spatial import cKDTree
from mosaic import *

PHI = (1 + 5 ** .5) / 2
def wythoff(k):
    a = (k + isqrt(5 * k * k)) // 2
    return a, a + k

def check(N=10 ** 6):
    for k in range(1, N):
        a, b = wythoff(k); t = (k * PHI) % 1.0
        fa = (a / PHI) % 1.0; fb = (b / PHI) % 1.0
        assert abs(fa - (1 - t / PHI)) < 1e-6 and abs(fb - t / PHI ** 2) < 1e-6, k
    return True

RINGS = ["grn2", "grn1", "grn0", "och0", "apr2", "ter0", "umb0", "umb1"]
BW = 3.15

def build(size, seed=5, N=987, rot=0.0):
    M = Mosaic(size, seed); S = M.S; X, Y = M.X, M.Y
    h = 17.0 * S
    x0, x1, y0, y1 = 210 * S, 3886 * S, 210 * S, 3500 * S
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 10 * S
    Rh = 985 * S; c = Rh / np.sqrt(N)
    inbox = (X > x0) & (X < x1) & (Y > y0) & (Y < y1)
    # ---------- seeds
    n = np.arange(1, N + 1)
    ang = 2 * np.pi * ((n / PHI) % 1.0 + rot) - np.pi / 2          # seam points (almost) straight up; wedge runs clockwise
    rad = c * np.sqrt(n - 0.5)
    sx = cx + rad * np.cos(ang); sy = cy + rad * np.sin(ang)
    # pair index and role of every seed
    kk = np.zeros(N + 1, np.int32); role = np.zeros(N + 1, np.int8)
    k = 1
    while True:
        a, b = wythoff(k)
        if a > N: break
        kk[a] = k; role[a] = 1
        if b <= N: kk[b] = k; role[b] = 2
        k += 1
    assert (role[1:] > 0).all()
    band = np.floor(np.sqrt(kk) / BW).astype(np.int32)
    # the lemma, as counts: every ring holds as many seeds inside the wedge as outside, while its twins fit
    kmax_b = max(kk[i] for i in range(1, N + 1) if role[i] == 2)
    for bnd in range(band.max() + 1):
        ks = [q for q in range(1, kmax_b + 1) if int(np.sqrt(q) / BW) == bnd]
        na = sum(1 for i in range(1, N + 1) if role[i] == 1 and band[i] == bnd and kk[i] <= kmax_b)
        nb = sum(1 for i in range(1, N + 1) if role[i] == 2 and band[i] == bnd)
        assert na == nb == len(ks)
    head = np.hypot(X - cx, Y - cy) < Rh
    ys, xs = np.nonzero(head)
    tree = cKDTree(np.c_[sx, sy])
    d, idx = tree.query(np.c_[xs + 0.5, ys + 0.5], k=2, workers=-1)
    # distance to the Voronoi edge between the two nearest seeds
    p1 = np.c_[sx, sy][idx[:, 0]]; p2 = np.c_[sx, sy][idx[:, 1]]
    sep = np.hypot(*(p2 - p1).T)
    e = (d[:, 1] ** 2 - d[:, 0] ** 2) / (2 * sep) - 0.055 * c * np.sqrt(np.pi)
    e = np.minimum(e, Rh - np.hypot(xs + .5 - cx, ys + .5 - cy) - 1.5 * S)
    sid = idx[:, 0] + 1
    cols = np.array([C(RINGS[b % len(RINGS)]) for b in band], np.float32)
    cols[1] = C("red0"); cols[2] = C("red0")
    # the wedge is laid in the paler stones of the same ring so the slip reads at a glance
    M.rgb[ys, xs] = cols[sid]
    M.edge[ys, xs] = e; M.tid[ys, xs] = h32(sid, 9001)
    M.mat[ys, xs] = np.where(np.isin(sid, [1, 2]), 1, 0)
    # ---------- sky: fans (opus a ventaglio)
    Rf = 9 * h
    j = np.floor(Y / Rf)
    def centre(jr):
        off = np.where(np.mod(jr, 2) == 0, 0.0, Rf)
        i = np.round((X - off) / (2 * Rf))
        return i * 2 * Rf + off, jr * Rf, i
    ax, ay, ai = centre(j + 1)
    low = np.hypot(X - ax, Y - ay) < Rf
    bx, by, bi = centre(j)
    fx = np.where(low, ax, bx); fy = np.where(low, ay, by)
    fk = (h32(np.where(low, ai, bi), np.where(low, j + 1, j), 4242) % np.uint32(100000)).astype(np.int32)
    T, xc, yc = polar_tess(X, Y, fx, fy, h, fk, w=1.08 * h)
    rho = np.hypot(xc - fx, yc - fy) / Rf
    up = np.clip((Y - y0) / (y1 - y0), 0, 1)
    upf = np.clip((fy - y0) / (y1 - y0), 0, 1)
    base = np.where((upf < 0.30)[..., None], C("lap0"), np.where((upf < 0.62)[..., None], C("lap1"), C("lap2")))
    base = base * (1 - 0.0) + 0.0
    mixc = np.where((upf < 0.45)[..., None], C("lap1"), C("tur1"))
    t = np.clip((rho - 0.25) / 0.75, 0, 1)[..., None]
    col = base * (1 - 0.55 * t) + mixc * 0.55 * t
    rim = rho > 0.89
    col = np.where(rim[..., None], C("lap3") * 0.9 + 0.1 * C("tur3"), col)
    out_head = inbox & ~head
    M.lay(out_head, T, col, mat=2)
    fanseam = np.where(low, ai, bi) + 4096 * np.where(low, j + 1, j)
    # seams between fans
    gx = np.abs(np.diff(fanseam, axis=1, prepend=fanseam[:, :1])) > 0
    gy = np.abs(np.diff(fanseam, axis=0, prepend=fanseam[:1])) > 0
    seam = ndi.distance_transform_edt(~(gx | gy)).astype(np.float32)
    np.minimum(M.edge, np.where(out_head, seam - 1.2 * S, 99), out=M.edge)
    # ---------- petals: two whorls of 34, rows run along each petal
    fig = head.copy()
    rs = np.random.RandomState(seed)
    def petals(nump, phase, L, Wd, cmain, cedge, cmid, key0):
        for i in range(nump):
            th = 2 * np.pi * (i + phase) / nump + 0.04 * rs.randn()
            Li = L * (1 + 0.07 * rs.randn()); bend = 0.10 * rs.randn()
            ux, uy = np.cos(th), np.sin(th)
            R0 = Rh - 0.5 * h
            bx0, by0 = cx + ux * R0, cy + uy * R0
            ext = Li + Wd + 4 * h
            xa = int(max(0, min(bx0, bx0 + ux * Li) - Wd - 3 * h)); xb = int(min(size, max(bx0, bx0 + ux * Li) + Wd + 3 * h)) + 1
            ya = int(max(0, min(by0, by0 + uy * Li) - Wd - 3 * h)); yb = int(min(size, max(by0, by0 + uy * Li) + Wd + 3 * h)) + 1
            if xb <= xa or yb <= ya: continue
            sl = (slice(ya, yb), slice(xa, xb)); Xs, Ys = X[sl], Y[sl]
            s = (Xs - bx0) * ux + (Ys - by0) * uy
            q = -(Xs - bx0) * uy + (Ys - by0) * ux
            sp = np.clip(s / Li, 0, 1)
            q = q - bend * Li * sp ** 2                       # a slight curl
            wprof = Wd * (0.55 + 0.45 * np.sin(np.pi * np.clip(sp * 1.25, 0, 1)) ) * np.clip((1 - sp) / 0.42, 0, 1) ** 0.75
            m = (s > -2 * h) & (s < Li) & (np.abs(q) < wprof) & inbox[sl] & ~head[sl]
            if not m.any(): continue
            T = tess(s + 40 * h, q + 60.5 * h, h * 0.96, key0 + i, w=1.5 * h)
            qc = T.vc - 60.5 * h; sc = (T.uc - 40 * h) / Li
            edge = np.abs(qc) > (Wd * (0.55 + 0.45 * np.sin(np.pi * np.clip(sc * 1.25, 0, 1))) * np.clip((1 - sc) / 0.42, 0, 1) ** 0.75 - 1.15 * h)
            colp = np.where(edge[..., None], cedge, cmain)
            colp = np.where((np.abs(qc) < 0.6 * h)[..., None] & (sc < 0.8)[..., None], cmid, colp)
            colp = np.where((sc < 0.12)[..., None], cedge * 0.9, colp)
            M.lay(m, T, colp.astype(np.float32), mat=1, sl=sl)
            M.cut(m, sl=sl)
            fig[sl] |= m
    petals(34, 0.5, 505 * S, 96 * S, C("gol2"), C("gol3"), C("och0"), 7000)
    petals(34, 0.0, 560 * S, 104 * S, C("gol1"), C("gol2"), C("gol0"), 8000)
    # a dark collar of two rows round the head
    T, xc, yc = polar_tess(X, Y, cx, cy, h, 6100, w=1.1 * h, r0=Rh - 30 * h)
    collar = (T.row >= 30) & (T.row < 32) & inbox
    thc = (np.arctan2(yc - cy, xc - cx) + np.pi / 2) / (2 * np.pi) % 1.0
    tick = (np.minimum(thc, 1 - thc) < 0.004) | (np.abs(thc - 1 / PHI ** 2) < 0.004)
    M.lay(collar, T, np.where(tick[..., None], C("mar0"), C("umb1")))
    M.cut(collar); M.cut(head)
    # ---------- border and slab
    bw = 3 * h
    bo = (X > x0 - bw) & (X < x1 + bw) & (Y > y0 - bw) & (Y < y1 + bw) & ~inbox
    dd = np.maximum(np.maximum(x0 - X, X - x1), np.maximum(y0 - Y, Y - y1))
    horiz = np.maximum(y0 - Y, Y - y1) >= np.maximum(x0 - X, X - x1)
    T = tess(np.where(horiz, X, Y), dd + 50 * h, h, 505 + horiz.astype(np.int32), w=1.1 * h)
    col = np.where(((T.row - 50) == 1)[..., None], C("umb1"), C("mar0"))
    M.lay(bo, T, col); M.cut(horiz & bo); M.cut(inbox)
    out_m = ~inbox & ~bo
    slab = marble(size, seed + 9)
    txt = text_mask(size, [
        ("THE SEAM IN THE SUNFLOWER", size / 2, 3742 * S, 104 * S, "Regular", 15 * S),
        ("987 seeds, numbered outward. Seed ⌊kφ⌋ and seed ⌊kφ²⌋ are twins and take the colour of the band that k falls in.",
         size / 2, 3850 * S, 49 * S, "Italic", 0.6 * S),
        ("Every second twin lies in one wedge of 137.5°, right of the seam at noon: there each band returns, pushed out by √φ.",
         size / 2, 3922 * S, 49 * S, "Italic", 0.6 * S),
    ])
    slab = incise(slab, txt, S)
    dout = ndi.distance_transform_edt(out_m).astype(np.float32)
    slab *= (1 - 0.18 * np.exp(-dout / (10 * S)))[..., None]
    M.mat[out_m] = 9; M.rgb[out_m] = slab[out_m]
    return M

if __name__ == "__main__":
    size = int(sys.argv[1]); out = sys.argv[2]
    if len(sys.argv) > 3: print("lemma checked to 10^6:", check())
    save(build(size).finish(), out)
