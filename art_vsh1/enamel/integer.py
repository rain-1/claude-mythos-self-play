"""Companion: the two smallest known INTEGER coincidences of a^5+b^5+(-a-b)^5,
each on its own gold line of the guilloché (wave engraving, sorbet enamel).
usage: python3 integer.py OUT.png SIZE SS
"""
import sys, time
import numpy as np
from brooch import render, build_grid, tonemap, hexrgb
from hero import Z, Gf, d6, contour_segs
from caption import caption

PAIRS = [((-1037, 455), (105, 1153)), ((-44667, 25403), (3914, 51858))]

if __name__ == "__main__":
    out, S, ss = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    cx, cy = S / 2, S * 0.455
    Rbez, Rin, Rz = 0.405 * S, 0.355 * S, 2.6
    lines = 22.0
    P = np.array([lines, 0.16, 30.0, 5.0, 3.0, 0.0, 0.0])
    warm = np.array([hexrgb(h) for h in ["#fff0b8", "#ffd9b0", "#ffc4c8", "#f9bfe0"]])
    cool = np.array([hexrgb(h) for h in ["#d6f5c8", "#c4efe4", "#c6e2f7", "#d2cdf7"]])
    gold = np.array([0.98, 0.80, 0.50])
    segs, pearls = [], []
    for k, ((a, b), (c, d)) in enumerate(PAIRS):
        z, w = Z(float(a), float(b)), Z(float(c), float(d))
        ck = (0.42 + 0.30 * k) * Rz
        ck = np.round(ck * lines) / lines
        lam = ck / abs(Gf(z)) ** 0.2
        segs += contour_segs(ck, Rz)
        for side, q in ((0, z * lam), (1, w * lam)):
            for p in d6(q):
                if abs(p) < 0.97 * Rz:
                    pearls.append((p.real, p.imag, 0.030 * Rz) + ((1.0, 0.975, 0.95) if side == 0 else (0.99, 0.88, 0.95)))
    segs = np.array(segs); pearls = np.array(pearls)
    ww = 0.0095 * Rz
    ng, gcell, gofs, gidx = build_grid(segs, Rz, ww)
    t0 = time.time()
    img = render(S, S, ss, cx, cy, Rin, Rbez, Rz, P, warm, cool, segs, ng, gcell, gofs, gidx,
                 ww, pearls, gold, 180, 64, 0.10, 0.35 / (np.pi * lines), 0, S)
    print("render", time.time() - t0, len(pearls))
    rng = np.random.default_rng(11)
    img = img * (1 + rng.normal(0, 0.006, (S, S, 1)).astype(np.float32))
    im = __import__("PIL.Image", fromlist=["Image"]).fromarray(tonemap(img, 1.0))
    caption(im, "Two Lines in Whole Numbers",
            "1258\u2075 \u2212 1153\u2075 \u2212 105\u2075  =  1037\u2075 \u2212 582\u2075 \u2212 455\u2075        55772\u2075 \u2212 51858\u2075 \u2212 3914\u2075  =  44667\u2075 \u2212 25403\u2075 \u2212 19264\u2075",
            "the two smallest known whole-number coincidences of a\u2075 + b\u2075 + (\u2212a\u2212b)\u2075, each on its own gold line with all its symmetric twins:",
            int(S * 0.893),
            line3="inner line: the only one with every entry below ten thousand (exhaustive search); outer line: the next one found, below sixty thousand")
    im.save(out)
