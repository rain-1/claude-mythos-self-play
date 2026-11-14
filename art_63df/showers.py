"""Six Showers: the same five drops, summed with themselves n = 1..6 times and scaled back."""
import sys, numpy as np
from pond import *

def make(size, out, ss=2, seed=8):
    T = np.array([(0, 0), (1, 0), (0.5, 3 ** .5 / 2)]); t = 0.25
    M = []
    for i in range(3):
        A, B_ = T[i], T[(i + 1) % 3]
        M.append(np.array([A, A + t * (B_ - A)])); M.append(np.array([B_, B_ + t * (A - B_)]))
    C = Cloth(size, seed, ss); W = C.W; S = C.S
    boxes = [(52 + 300 * i, 62 + 372 * j, 52 + 300 * i + 296, 62 + 372 * j + 262) for j in range(2) for i in range(3)]
    inK = np.zeros((W, W), bool); Ff = np.zeros((W, W), np.float32)
    ponds = []; dropl = []; smax = None
    for n, box in zip(range(1, 7), boxes):
        P = Pond(M, n=n).fit(box)
        ponds.append(P)
        bx = (box[0] - 8, box[1] - 8, box[2] + 8, box[3] + 8)
        sy, sx, F, own = P.raster(C, bx)
        inK[sy, sx] |= F >= 0; Ff[sy, sx] = np.maximum(Ff[sy, sx], np.maximum(F, 0))
        print(n, "pieces", len(P.H), "s*", P.s, "c", P.c, "a_n", P.a, flush=True)
    L = 8
    levels = ponds[0].s * (np.arange(1, L) / L) ** 2.3
    B = np.digitize(Ff, levels)
    dropwax = (inK & (Ff < 0.014)).astype(np.float32)
    e = ((B != np.roll(B, 1, 0)) | (B != np.roll(B, 1, 1))) & inK
    hair = np.clip(ndi.gaussian_filter(e.astype(np.float32), 0.45 * S) * 3.0, 0, 1)
    ground = (~inK).astype(np.float32)
    for k in range(0, L):
        wax = np.maximum.reduce([(B < k).astype(np.float32) * inK, ground, dropwax, hair * 0.6])
        C.dye(INDIGO, 0.21 if k else 0.16, wax, crackle=0.28 + 0.04 * k, cell=24 + 3 * k)
    # ground: cream, with a soga lattice of small diamonds, rules, and brown lettering
    def motif(d, S_):
        step = 14.0
        for i in range(-2, 75):
            for j in range(-2, 85):
                x = (i + 0.5 * (j % 2)) * step; y = j * step * 0.866
                r = 1.9 * S_
                d.polygon([(x * S_ - r, y * S_), (x * S_, y * S_ - r), (x * S_ + r, y * S_), (x * S_, y * S_ + r)], fill=255)
        for r_, wd in ((20, 2.4), (29, 1.0)):
            pts = [(r_, r_), (1000 - r_, r_), (1000 - r_, 1000 - r_), (r_, 1000 - r_)]
            for a in range(4):
                A = np.array(pts[a]); Bp = np.array(pts[(a + 1) % 4])
                C.canting(d, [A + (Bp - A) * t for t in np.linspace(0, 1, 120)], wd, 0.25, blob=False)
        for P in ponds:
            hv = P.to_cloth(P.V); cen = hv.mean(0)
            Q = cen + (hv - cen) * 1.035
            pl = []
            for a in range(len(Q)):
                A = Q[a]; Bp = Q[(a + 1) % len(Q)]
                pl += [A + (Bp - A) * t for t in np.linspace(0, 1, 40, endpoint=False)]
            C.canting(d, pl, 1.6, 0.3, closed=True)
    mo = C.mask(motif)
    from fractions import Fraction
    names = ["one", "three", "six", "ten", "fifteen", "no"]
    fr = ["5/4", "1", "3/4", "1/2", "1/4", "0"]
    items = [(500, 842, "Six Showers on the Same Pond", 36, False, "mm"),
             (500, 888, "The six corner pieces of a triangle, added to themselves n times and scaled back.", 19.5, True, "mm"),
             (500, 915, "White is the sumset; the darkest water is the last to be covered, and its depth is Schneider's index c.", 19.5, True, "mm"),
             (500, 942, "Each shower lowers n · c(nM) by exactly one quarter, until the sixth leaves nothing to cover.", 19.5, True, "mm")]
    for P, box, n in zip(ponds, boxes, range(1, 7)):
        items.append(((box[0] + box[2]) / 2, box[3] + 30, "n = %d  ·  %s dry place%s  ·  n c = %s" % (n, names[n - 1], "" if n == 1 else "s", fr[n - 1]), 17.5, True, "mm"))
    txt = C.text_mask(items)
    # label plates: keep a clean patch behind the text
    plate = np.clip(ndi.gaussian_filter(txt, 7 * S) * 60, 0, 1)
    open_ = np.maximum(mo * (1 - plate), txt)
    open_ *= ground
    C.dye(SOGA, 1.25, 1 - open_, crackle=0.0, bleed=0.3, seep=0.0)
    C.dye(SOGA, 0.13, inK.astype(np.float32), crackle=0.6, cell=30)   # tea-stain the ground a little, veins through pond wax
    # red: last-covered point of each pond
    def red(d, S_):
        for P in ponds:
            if P.s < 1e-6: continue
            u = P.to_cloth(np.array([P.ux, P.uy])); r = (2.6 + 3.0 * P.s / ponds[0].s) * S_
            d.ellipse([u[0] * S_ - r, u[1] * S_ - r, u[0] * S_ + r, u[1] * S_ + r], fill=255)
    rm = C.mask(red, blur=0.3)
    C.discharge(rm, 0.85)
    C.dye(MENGKUDU, 1.25, 1 - rm, crackle=0, uneven=0.1, bleed=0, seep=0)
    C.finish().save(out)

if __name__ == "__main__":
    make(int(sys.argv[1]), sys.argv[2], ss=int(sys.argv[3]) if len(sys.argv) > 3 else 2)
