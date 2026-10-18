"""Quilled mandala of the capture tree: primes as coils, borrowing as stems."""
import numpy as np, sys, time
from scipy import ndimage as ndi
from matplotlib.path import Path
import quill as Q

def load(tsv):
    rec = {}
    for line in open(tsv):
        f = line.rstrip('\n').split('\t')
        par = [x for x in f[3].split(',') if x]
        rec[int(f[0])] = (int(f[1]), int(f[2]), [(int(a.split('^')[0]), int(a.split('^')[1])) for a in par])
    return rec

def ancestry(rec, gmax, pmax=None):
    leaves = sorted(p for p in rec if rec[p][1] == gmax and (pmax is None or p <= pmax))
    anc = set(); st = list(leaves)
    while st:
        p = st.pop()
        if p in anc: continue
        anc.add(p); st += [q for q, _ in rec[p][2]]
    # main parent = highest-generation parent (ties: largest)
    main = {p: max(rec[p][2], key=lambda t: (rec[t[0]][1], t[0]))[0] for p in anc if rec[p][2]}
    return leaves, anc, main

def teardrop(L, Wd, tip_sharp=1.0, n=200):
    """teardrop outline: round end at (0,0) radius Wd/2, tip at (L,0)."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    # polar-ish: r(θ) blends circle and point
    x = np.cos(t); y = np.sin(t)
    # map: points with x>0 stretched toward the tip
    s = (x + 1) / 2
    X = -Wd / 2 * (1 - s) + s * (L - Wd / 2 * 0) * s ** 0.0
    X = np.where(x < 0, x * Wd / 2, x * (L - 0))
    Y = y * Wd / 2 * np.where(x < 0, 1.0, (1 - x) ** (0.9 * tip_sharp) * (1 + 1.2 * x) ** 0.5)
    return np.c_[X, Y]

def eye(L, Wd, n=200):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = np.cos(t); y = np.sin(t)
    return np.c_[x * L / 2, y * Wd / 2 * (1 - x * x) ** 0.25 * np.abs(np.sin(t)) ** 0.0]

def place(shape_pts, cx, cy, ang):
    c, s = np.cos(ang), np.sin(ang)
    R = np.array([[c, -s], [s, c]])
    return shape_pts @ R.T + np.array([cx, cy])

def mask_of(poly, shp, off=(0, 0)):
    x0 = int(max(0, np.floor(poly[:, 0].min()) - 2)); x1 = int(min(shp[1], np.ceil(poly[:, 0].max()) + 3))
    y0 = int(max(0, np.floor(poly[:, 1].min()) - 2)); y1 = int(min(shp[0], np.ceil(poly[:, 1].max()) + 3))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    m = Path(poly).contains_points(np.c_[xx.ravel() + .5, yy.ravel() + .5]).reshape(yy.shape)
    return m, (y0, y1, x0, x1)

def coil_shape(H, A, poly, pitch, sw, hgt, col, outline=True, wall=None, pole=None, G=None, gild=False, smooth=0):
    m, (y0, y1, x0, x1) = mask_of(poly, H.shape)
    Hs = H[y0:y1, x0:x1]; As = A[y0:y1, x0:x1]
    inner = ndi.binary_erosion(m, iterations=max(1, int(round(sw * 1.4))))
    pl = None if pole is None else (pole[0] - x0, pole[1] - y0)
    Q.coil(Hs, As, inner, pitch=pitch, width=sw, height=hgt * 0.92, col=col, pole=pl, rim_gap=0.5, smooth=smooth)
    if outline:
        d = Q.seg_dist(Q.poly_segs(poly - np.array([x0, y0])), Hs.shape, pad=6)
        prof = Q.wall_profile(d, wall or sw * 1.25)
        oc = tuple(np.array(col) ** 1.5 * 0.98)
        Q.put(Hs, As, prof, hgt, oc)
        if gild and G is not None:
            g = np.clip(1.3 - d / ((wall or sw) * 0.75), 0, 1).astype(np.float32)
            Gs = G[y0:y1, x0:x1]; np.maximum(Gs, g, out=Gs)

def tight_coil(H, A, cx, cy, r, sw, hgt, col, G=None):
    n = 120; t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    poly = np.c_[cx + r * np.cos(t), cy + r * np.sin(t)]
    coil_shape(H, A, poly, pitch=sw * 1.7, sw=sw, hgt=hgt, col=col, wall=sw * 1.5, pole=(cx, cy), G=G, gild=True)

def stem(H, A, pts, sw, hgt, col):
    segs = np.hstack([pts[:-1], pts[1:]])
    Q.stroke(H, A, segs, sw * 1.2, hgt, col)

def bezier(p0, p1, p2, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2
