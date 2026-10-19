"""Hero: the Choudhry-Wroblewski curve as gold cloisonné on a guilloché brooch
engraved with the level sets of  a^5 + b^5 + (-a-b)^5  (= const * |z|^2 Re z^3).

usage: python3 hero.py OUT.png SIZE SS [variant]
"""
import sys, time
from fractions import Fraction
import numpy as np
from brooch import render, build_grid, tonemap, hexrgb

W3 = np.exp(2j * np.pi / 3)


def Z(a, b):
    # (a, b, -a-b) on the plane x1+x2+x3=0  ->  complex coordinate
    return (a * (1 - W3 ** 2) + b * (W3 - W3 ** 2)) / np.sqrt(3)


def CW(u, v=1.0):
    a = u / v
    b = 2 * u * v ** 4 * (3 * u ** 10 + v ** 10) / ((u ** 5 + v ** 5) * (u ** 10 - 4 * u ** 5 * v ** 5 - v ** 10))
    c = (u ** 10 + 4 * u ** 5 * v ** 5 - v ** 10) / (u ** 10 - 4 * u ** 5 * v ** 5 - v ** 10)
    d = (u ** 5 - v ** 5) / (u ** 5 + v ** 5)
    return a, b, c, d


def images(q):
    # the 6 symmetries that fix a^5+b^5+(-a-b)^5 : rotations by 120deg and conjugation
    out = []
    for k in range(3):
        for cj in (False, True):
            out.append(W3 ** k * (np.conj(q) if cj else q))
    return out


def polylines(Rz, n=400001):
    th = np.linspace(-np.pi / 2, np.pi / 2, n)[1:-1]
    t = np.tan(th)
    a, b, c, d = CW(t)
    zs = [Z(a, b), Z(c, d)]
    segs = []
    for q in zs:
        for p in images(q):
            ok = np.isfinite(p) & (np.abs(p) < Rz * 1.02)
            step = Rz / 900
            run = []
            for i in range(len(p)):
                if ok[i] and (not run or abs(p[i] - run[-1]) < 0.02 * Rz):
                    if not run or abs(p[i] - run[-1]) >= step:
                        run.append(p[i])
                else:
                    for A, B in zip(run[:-1], run[1:]):
                        segs.append((A.real, A.imag, B.real, B.imag))
                    run = [p[i]] if ok[i] else []
            for A, B in zip(run[:-1], run[1:]):
                segs.append((A.real, A.imag, B.real, B.imag))
    return np.array(segs, np.float64)


def rational_points(Rz, H=4):
    pts = set()
    for u in range(-H, H + 1):
        for v in range(1, H + 1):
            fr = Fraction(u, v)
            if fr.denominator != v:
                continue
            if u in (0,) or abs(fr) == 1:
                continue
            try:
                a, b, c, d = CW(float(u), float(v))
            except ZeroDivisionError:
                continue
            for q in (Z(a, b), Z(c, d)):
                for p in images(q):
                    if np.isfinite(p) and abs(p) < 0.93 * Rz:
                        pts.add((round(p.real, 9), round(p.imag, 9)))
    return np.array(sorted(pts), np.float64)


def Gf(z):
    return np.abs(z) ** 2 * np.real(z ** 3)


def d6(q):
    out = []
    for k in range(6):
        r = np.exp(1j * np.pi * k / 3)
        out.append(r * q)
        out.append(r * np.conj(q))
    return out


def contour_segs(c, Rz, n=6000):
    """the level set |G|^(1/5) = c : one branch per 60-degree sector."""
    segs = []
    for k in range(6):
        th0 = k * np.pi / 3
        th = th0 + np.linspace(-np.pi / 6, np.pi / 6, n)[1:-1]
        r = c / np.abs(np.cos(3 * th)) ** 0.2
        p = r * np.exp(1j * th)
        ok = r < Rz * 1.03
        for i in range(len(p) - 1):
            if ok[i] and ok[i + 1]:
                segs.append((p[i].real, p[i].imag, p[i + 1].real, p[i + 1].imag))
    return segs


CLASSES = [(2, 1), (3, 2), (5, 3), (6, 5), (7, 4), (7, 6), (9, 5), (8, 7)]


def solution_rings(Rz, lines, ncls=6, c0=0.20, c1=0.86):
    """each class of CW points -> one gold contour (rescaled solution)."""
    segs = []
    pearls = []
    for k, (u, v) in enumerate(CLASSES[:ncls]):
        a, b, c, d = CW(float(u), float(v))
        z, w = Z(a, b), Z(c, d)
        g = abs(Gf(z)) ** 0.2
        ck = (c0 + (c1 - c0) * k / max(ncls - 1, 1)) * Rz
        ck = (np.round(ck * lines) + 0.0) / lines         # sit on a groove valley
        lam = ck / g
        segs += contour_segs(ck, Rz)
        zl, wl = z * lam, w * lam
        for side, q in ((0, zl), (1, wl)):
            for p in d6(q):
                if abs(p) < 0.97 * Rz:
                    pearls.append((p.real, p.imag, k, side))
    return np.array(segs), np.array(pearls)


if __name__ == "__main__":
    out = sys.argv[1]
    S = int(sys.argv[2])
    ss = int(sys.argv[3])
    Wd, Hd = S, S
    cx, cy = S / 2, S * 0.455
    Rbez = 0.405 * S
    Rin = 0.355 * S
    Rz = 2.6
    lines = 26.0
    P = np.array([lines, 0.0, 0.0, 5.0, 3.0, 0.0, 0.0])
    if len(sys.argv) > 4:
        var = sys.argv[4]
        if var == "wave":
            P[1] = 0.22; P[2] = 36
        if var == "basket":
            P[5] = 1; P[6] = 180
    warm = np.array([hexrgb(h) for h in ["#ffe2b8", "#ffcfb0", "#ffb8bf", "#f7b3d6"]])
    cool = np.array([hexrgb(h) for h in ["#c9f0dc", "#bfe6f5", "#c3cdf7", "#dcc4f2"]])
    gold = np.array([0.98, 0.80, 0.50])
    segs, pr = solution_rings(Rz, lines)
    ww = 0.0075 * Rz
    ng, gcell, gofs, gidx = build_grid(segs, Rz, ww)
    pearls = np.zeros((len(pr), 6))
    pearls[:, :2] = pr[:, :2]
    pearls[:, 2] = 0.021 * Rz
    for i in range(len(pr)):
        pearls[i, 3:] = (1.0, 0.975, 0.95) if pr[i, 3] == 0 else (0.99, 0.90, 0.96)
    print("segments", len(segs), "pearls", len(pearls))
    t0 = time.time()
    img = render(Wd, Hd, ss, cx, cy, Rin, Rbez, Rz, P, warm, cool, segs, ng, gcell, gofs, gidx,
                 ww, pearls, gold, 180, 64, 0.10, 0.35 / (np.pi * lines), 0, Hd)
    print("render", time.time() - t0)
    np.save(out.replace(".png", ".npy"), img)
    from PIL import Image
    from caption import caption
    rng = np.random.default_rng(7)
    grain = rng.normal(0, 0.006, (Hd, Wd)).astype(np.float32)
    img = img * (1 + grain[..., None])
    im = Image.fromarray(tonemap(img, 1.0))
    caption(im, "Both Sides of One Line",
            "a\u2075 + b\u2075 + (\u2212a\u2212b)\u2075  =  c\u2075 + d\u2075 + (\u2212c\u2212d)\u2075,  engraved along its level lines",
            "each gold line carries one rational point of the Choudhry\u2013Wroblewski curve (u/v = 2, 3/2, 5/3, 6/5, 7/4, 7/6), rescaled:",
            int(Hd * 0.893),
            line3="white pearls are (a, b), rose pearls are (c, d), with all their symmetric twins; where the lines crowd into six rays lie the trivial zeros a = 0, b = 0, a + b = 0")
    im.save(out)
