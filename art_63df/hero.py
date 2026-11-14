import sys, json, numpy as np
from pond import *

def make(size, out, ss=2, seed=3, n=1, L=7, title=True, mseed=5, NIN=8):
    rng = np.random.default_rng(mseed)
    NV = 9
    th = np.linspace(0, 2 * np.pi, NV + 1)[:-1] + rng.normal(scale=0.10, size=NV) + 0.3
    hullp = np.stack([np.cos(th) * (1 + 0.05 * rng.normal(size=NV)), 0.93 * np.sin(th) * (1 + 0.05 * rng.normal(size=NV))], 1)
    bank = []
    for i in range(NV):
        A, B_ = hullp[i], hullp[(i + 1) % NV]
        for t in (0.0, 0.25, 0.5, 0.75): bank.append(A + (B_ - A) * t)
    inner = []
    while len(inner) < NIN:
        p = rng.uniform(-0.8, 0.8, 2)
        if np.hypot(p[0], p[1] / 0.93) < 0.74 and all(np.hypot(*(p - q)) > 0.30 for q in inner): inner.append(p)
    M = np.vstack([np.array(bank), np.array(inner)])
    P = Pond([m[None] for m in M], n=n).fit((95, 70, 905, 835))
    C = Cloth(size, seed, ss)
    W = C.W; S = C.S
    sy, sx, F, own = P.raster(C, (60, 40, 940, 860))
    inK = np.zeros((W, W), bool); Ff = np.zeros((W, W), np.float32)
    inK[sy, sx] = F >= 0; Ff[sy, sx] = np.maximum(F, 0)
    levels = np.linspace(0, P.s, L + 1)[1:-1] * 1.0
    B = np.digitize(Ff, levels)            # 0..L-1
    print("s*", P.s, "c", P.c, "a_n", P.a, "last point", P.ux, P.uy, "active", P.active())
    drops = P.to_cloth(M)
    # --- wax objects reused
    dropwax = C.mask(lambda d, S_: C.cecek(d, drops, 4.2, 0.1))
    # ripples: fine canting line along every band boundary (keeps a pale hairline between tones)
    edge = np.zeros((W, W), np.float32)
    e = (B != np.roll(B, 1, 0)) | (B != np.roll(B, 1, 1))
    edge[e & inK] = 1
    edge = ndi.maximum_filter(edge, size=max(1, int(round(0.9 * S))))
    hair = np.clip(ndi.gaussian_filter(edge, 0.45 * S) * 1.6, 0, 1)
    ground = (~inK).astype(np.float32)
    # ---- indigo baths: lightest band is waxed first
    for k in range(1, L):
        wax = np.maximum.reduce([(B < k).astype(np.float32) * inK, ground, dropwax, hair * (0.75 if k < 3 else 0.5)])
        C.dye(INDIGO, 0.25 + 0.012 * k, wax, crackle=0.22 + 0.035 * k, cell=22 + 3 * k)
    # ---- soga bath for the ground: pond waxed, cecek dots and border lines resist
    gpts = []
    step = 11.0
    for i in range(int(1000 / step) + 2):
        for j in range(int(1000 / step) + 2):
            x = (i + 0.5 * (j % 2)) * step; y = j * step * 0.866
            gpts.append((x, y))
    gpts = np.array(gpts)
    def frame(d, S_):
        C.cecek(d, gpts, 1.55, 0.3)
        for off, wd in ((22, 2.2), (30, 1.0), (872, 1.0), (880, 2.2)):
            pass
        # border rules
        for r, wd in ((18, 2.6), (27, 1.1)):
            pts = [(r, r), (1000 - r, r), (1000 - r, 1000 - r), (r, 1000 - r)]
            for a in range(4):
                A = np.array(pts[a]); Bp = np.array(pts[(a + 1) % 4])
                C.canting(d, [A + (Bp - A) * t for t in np.linspace(0, 1, 120)], wd, 0.25, blob=False)
        C.canting(d, [(60 + 880 * t, 872) for t in np.linspace(0, 1, 160)], 1.2, 0.3, blob=False)
        # hull outline: a double wax line round the pond
        hv = P.to_cloth(P.V)
        cen = hv.mean(0)
        for grow, wd in ((1.022, 2.4), (1.045, 1.0)):
            Q = cen + (hv - cen) * grow
            pl = []
            for a in range(len(Q)):
                A = Q[a]; Bp = Q[(a + 1) % len(Q)]
                pl += [A + (Bp - A) * t for t in np.linspace(0, 1, 40, endpoint=False)]
            C.canting(d, pl, wd, 0.3, closed=True)
    fr = C.mask(frame)
    items = []
    if title:
        items = [(500, 899, "The Last Place the Rain Reaches", 34, False, "mm"),
                 (500, 935, "%d drops; each ring grows into the whole pond. The red point is covered last, at s = %.4f," % (len(M), P.s), 19, True, "mm"),
                 (500, 960, "so Schneider's non-convexity index of the drops is s/(1 − s) = %.4f.  (MathOverflow 516522)" % P.c, 19, True, "mm")]
    txt = C.text_mask(items) if items else 0
    wax = np.maximum.reduce([inK.astype(np.float32), fr, txt + np.zeros((W, W), np.float32)])
    C.dye(SOGA, 1.0, wax, crackle=0.55, cell=30)
    C.dye(INDIGO, 0.10, wax, crackle=0.2, cell=41)
    # ---- the red: last point, and stitches to the drops whose rings meet there
    u = P.to_cloth(np.array([P.ux, P.uy]))
    act = P.active()
    def red(d, S_):
        r = 7.5 * S_
        d.ellipse([u[0] * S_ - r, u[1] * S_ - r, u[0] * S_ + r, u[1] * S_ + r], fill=255)
        for i in act:
            m = P.to_cloth(P.piece_point(i))
            L_ = np.hypot(*(m - u)); k = int(L_ / 9)
            for t in range(2, k - 1):
                a = u + (m - u) * (t / k); b = u + (m - u) * ((t + 0.5) / k)
                d.line([tuple(a * S_), tuple(b * S_)], fill=255, width=max(1, int(1.6 * S_)))
    rm = C.mask(red, blur=0.4)
    C.discharge(rm, 0.85)
    C.dye(MENGKUDU, 1.25, 1 - rm, crackle=0, uneven=0.1, bleed=0, seep=0)
    C.finish().save(out)
    return P

if __name__ == "__main__":
    size = int(sys.argv[1]); out = sys.argv[2]; ms = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    make(size, out, mseed=ms, ss=int(sys.argv[4]) if len(sys.argv) > 4 else 2)
