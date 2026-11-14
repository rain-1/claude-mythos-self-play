"""Twenty-five circles to the repeat: the torus packing of MO 490278 as a repeating batik cloth."""
import sys, json, numpy as np
from batik import *

def make(size, out, ss=2, seed=21, U=318.0):
    D = json.load(open("math_torus/packing25.json"))
    P = np.array(D["P"]); dd = D["d"]; faces = D["faces"]; adj = {int(k): v for k, v in D["adj"].items()}
    C = Cloth(size, seed, ss); W = C.W; S = C.S
    x0, y0, x1, y1 = 34, 34, 966, 858          # pattern window (cloth units)
    ox, oy = 500 - 1.5 * U + 12, 446 + 1.5 * U - 30   # torus origin on the cloth
    px = (np.arange(W) + 0.5) / S; py = (np.arange(W) + 0.5) / S
    X, Y = np.meshgrid(((px - ox) / U).astype(np.float32), ((oy - py) / U).astype(np.float32))
    win = (px[None, :] > x0) & (px[None, :] < x1) & (py[:, None] > y0) & (py[:, None] < y1)
    q = np.stack([X.ravel() % 1.0, Y.ravel() % 1.0], 1)
    # periodic images
    sh = np.array([(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1)], float)
    PP = (P[None] + sh[:, None]).reshape(-1, 2)
    r, idx = cKDTree(PP).query(q, k=1, workers=-1)
    r = r.reshape(W, W).astype(np.float32); idx = (idx % 25).reshape(W, W)
    FC = np.array([f["c"] for f in faces]); FK = np.array([f["k"] for f in faces])
    FF = (FC[None] + sh[:, None]).reshape(-1, 2)
    fd, fi = cKDTree(FF).query(q, k=1, workers=-1)
    fd = fd.reshape(W, W)
    fk = FK[fi % len(FC)].reshape(W, W)
    del q
    R = dd / 2
    disc = r < R * 0.965
    gapT = (~disc) & (fk == 3) & win
    gapS = (~disc) & (fk == 4) & win
    # angle from own centre, for the spokes towards the neighbours it touches
    cen = PP[cKDTree(PP).query(np.stack([X.ravel() % 1.0, Y.ravel() % 1.0], 1), k=1, workers=-1)[1]]
    vx = (X.ravel() % 1.0 - cen[:, 0]).reshape(W, W); vy = (Y.ravel() % 1.0 - cen[:, 1]).reshape(W, W)
    del cen
    spoke = np.zeros((W, W), np.float32)
    petal = np.zeros((W, W), np.float32)
    for i in range(25):
        m = (idx == i) & disc
        if not m.any(): continue
        for j in adj[i]:
            v = P[j] - P[i]; v -= np.round(v); v /= np.hypot(*v)
            along = vx[m] * v[0] + vy[m] * v[1]; across = np.abs(-vx[m] * v[1] + vy[m] * v[0])
            t = along / R
            # a leaf-shaped petal pointing at each neighbour, and a fine wax vein down its middle
            wleaf = 0.20 * R * np.sin(np.clip((t - 0.16) / 0.66, 0, 1) * np.pi) ** 0.8
            pm = ((t > 0.16) & (t < 0.82) & (across < wleaf)).astype(np.float32)
            petal[m] = np.maximum(petal[m], pm)
            sm = ((t > 0.24) & (t < 0.74) & (across < 0.018 * R)).astype(np.float32)
            spoke[m] = np.maximum(spoke[m], sm)
    ring = (disc & (r > R * 0.865)).astype(np.float32)
    eye = (r < R * 0.105).astype(np.float32)
    winf = win.astype(np.float32)
    # 1. soga: the body of every disc (petals, ring and eye stay cream)
    body = disc & win
    wax = 1 - body.astype(np.float32) * (1 - np.maximum.reduce([petal, ring, eye]))
    C.dye(SOGA, 1.05, wax, crackle=0.35, cell=27)
    # 2. indigo: the triangular gaps, hard; and lightly over the soga bodies (sogan brown-black)
    C.dye(INDIGO, 1.15, 1 - gapT.astype(np.float32), crackle=0.30, cell=31)
    wax2 = 1 - body.astype(np.float32) * (1 - np.maximum.reduce([petal, ring, eye]))
    C.dye(INDIGO, 0.22, wax2, crackle=0.2, cell=37)
    # petals: pale blue, with the vein kept white
    wax3 = 1 - petal * body * (1 - spoke)
    C.dye(INDIGO, 0.22, wax3, crackle=0.0, bleed=0.2)
    # 3. the red: the thirteen square gaps of every repeat
    C.dye(KUNING, 0.55, 1 - gapS.astype(np.float32), crackle=0.3, cell=33)
    C.dye(SOGA, 0.16, 1 - gapS.astype(np.float32), crackle=0.5, cell=29)
    rm = ndi.gaussian_filter((gapS & (fd < 0.115 * dd)).astype(np.float32), 0.3 * S)
    C.dye(MENGKUDU, 1.25, 1 - rm, crackle=0.0, uneven=0.12, bleed=0, seep=0)
    # 4. border and caption: soga ground outside the window, cream rules and letters
    def frame(d, S_):
        for r_, wd in ((16, 2.6), (25, 1.0)):
            pts = [(r_, r_), (1000 - r_, r_), (1000 - r_, 1000 - r_), (r_, 1000 - r_)]
            for a in range(4):
                A = np.array(pts[a]); Bp = np.array(pts[(a + 1) % 4])
                C.canting(d, [A + (Bp - A) * t for t in np.linspace(0, 1, 120)], wd, 0.25, blob=False)
    fr = C.mask(frame)
    items = [(500, 898, "Twenty-Five Circles to the Repeat", 34, False, "mm"),
             (500, 938, "The best known packing of 25 equal circles on a square torus. The gaps are 24 triangles and", 19, True, "mm"),
             (500, 964, "13 squares (red-eyed), so 13 d² + 6√3 d² = 1: that is the whole equation.  (MathOverflow 490278)", 19, True, "mm")]
    txt = C.text_mask(items)
    C.dye(SOGA, 1.0, np.maximum.reduce([winf, fr, txt]), crackle=0.5, cell=30)
    C.dye(INDIGO, 0.5, np.maximum.reduce([winf, fr, txt]), crackle=0.25, cell=43)
    # one repeat marked by running stitches of cream (scraped) thread
    def stitch(d, S_):
        a = np.array([ox + U, oy - U]); pts = [a, a + (U, 0), a + (U, -U), a + (0, -U)]
        for k in range(4):
            A = pts[k]; Bp = pts[(k + 1) % 4]; n = 34
            for t in range(n):
                p = A + (Bp - A) * ((t + 0.15) / n); q_ = A + (Bp - A) * ((t + 0.62) / n)
                d.line([tuple(p * S_), tuple(q_ * S_)], fill=255, width=max(1, int(2.4 * S_)))
    st = C.mask(stitch, blur=0.25)
    C.discharge(st, 0.92, to=(0.97, 0.95, 0.90))
    C.finish().save(out)

if __name__ == "__main__":
    make(int(sys.argv[1]), sys.argv[2], ss=int(sys.argv[3]) if len(sys.argv) > 3 else 2)
