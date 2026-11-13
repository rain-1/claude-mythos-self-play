"""Census in sprinkled gold: every n from 4 to 2,000,000 is one flake at
   x = log n,  y = log c / log n,   c = T(n,n-1)-(n-1)  (so a(n) = (n+1)c - 1).
Brightness is the conditional law of y given x (each column normalised), so a stationary law would be
a picture that does not change from left to right.  silver = n prime (c = 1, the bottom line) and the
n whose last straight stretch is too short to prove a(n) prime; cinnabar = a(n) composite (25 of them)."""
import sys, numpy as np
from makie import *
from scipy.ndimage import gaussian_filter

def render(size=1024, out='census.png', seed=5, npz='math_gcd/fast_2_2000000.npz'):
    u = size / 1024.0
    d = np.load(npz); A, C, L, P, F = d['A'], d['C'], d['L'], d['P'], d['F']
    n = np.arange(2, 2 + len(A)).astype(np.float64); W = n - 2 - L
    cert = (W + 1) ** 2 > A
    Pn = Panel(size, seed=seed, ss=2, sheen=0.6)
    xl, xr = 0.045 * size, 0.955 * size
    yb, yt = 0.875 * size, 0.07 * size
    n0, n1 = 3.6, 2.0e6
    ymax = 1.17
    X = xl + (xr - xl) * (np.log(n) - np.log(n0)) / (np.log(n1) - np.log(n0))
    yv = np.log(C) / np.log(n)
    Y = yb + (yt - yb) * yv / ymax
    ok = (n >= n0)
    def hist(sel):
        H, _, _ = np.histogram2d(Y[sel], X[sel], bins=size, range=[[0, size], [0, size]])
        return H.astype(np.float32)
    Hall = hist(ok)
    col = np.maximum(Hall.sum(0, keepdims=True), 1)
    # number of n per column grows like n: the left is single flakes, the right a continuum
    Hc = hist(ok & cert & (C > 1)) / col
    mF = 0.5 * np.log(n)
    Hlo = hist(ok & cert & (C > 1) & (F < 0.7 * mF)) / col
    Hhi = hist(ok & cert & (C > 1) & (F > 1.35 * mF)) / col
    Hmid = Hc - Hlo - Hhi
    Hs = hist(ok & (C == 1)) / col
    rows = size * 1.0
    # a flat law would have p = 1/rows per pixel: gain is in those units
    for Hk, metal in [(Hlo, AKAGANE), (Hmid, KIN), (Hhi, AOKIN)]:
        dens = np.clip(Hk * rows * 0.06 / max(1, u ** 0.75) ** 1.2, 0, 1) ** 0.8
        Pn.dust(np.clip(dens, 0, 0.96), metal, grain=0.42 * max(1, u ** 0.75), sparkle=0.07, gain=0.85)
    # the solid ripples (fixed small c) get a burnished pass: columns where one row holds > 0.4% of the mass
    rip = np.clip((Hc - 0.004) / 0.01, 0, 1)
    rip = np.maximum(rip, gaussian_filter(rip, 0.6 * u))
    Pn.leaf(np.clip(rip, 0, 1), KIN, height=1.0 * u, tone=0.9, burnish=0.3, glow=0.25)
    # bottom line: n prime
    ps = np.clip(Hs * 6, 0, 1); ps = np.maximum(ps, gaussian_filter(ps, 0.8 * u) * 1.5)
    Pn.leaf(np.clip(ps, 0, 1), GIN, height=1.0 * u, tone=0.9, glow=0.3)
    # uncertified: silver beads; composite: cinnabar beads
    unc = ok & ~cert & (P == 1)
    comp = ok & (P == 0)
    def beads(sel, r):
        def fn(dr, s):
            for x, y in zip(X[sel], Y[sel]):
                dr.ellipse([(x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s], fill=255)
        return Pn.mask(fn)
    Pn.leaf(beads(unc, 0.95 * u), GIN, height=1.0 * u, tone=1.0, burnish=0.7, glow=0.5)
    mc = beads(comp, 4.2 * u)
    Pn.leaf(mc, SHU, height=2.5 * u, tone=1.05, burnish=0.8, glow=2.2)
    # a hairline frame: the right edge is where the computation stopped
    fx0, fx1, fy0, fy1 = xl - 0.012 * size, xr + 0.012 * size, yt - 0.03 * size, yb + 0.035 * size
    def frame(dr, s):
        dr.rectangle([fx0 * s, fy0 * s, fx1 * s, fy1 * s], outline=255, width=max(1, int(1.3 * u * s)))
    Pn.leaf(Pn.mask(frame), KIN, height=0.8 * u, tone=0.55, burnish=0.1, glow=0.05)
    # captions
    tm = Pn.text_mask([
        (0.045 * size, 0.948 * size, "Twenty-Five Red Stars over the River", 21 * u, False, "ls"),
        (0.045 * size, 0.972 * size, "every n from 4 to 2,000,000 is one flake: left to right log n, upward log c / log n, where a(n) = (n+1) c − 1", 12.5 * u, True, "ls"),
        (0.955 * size, 0.948 * size, "gold: a(n) proved prime by its last straight stretch (99.9%)", 11 * u, True, "rs"),
        (0.955 * size, 0.972 * size, "silver: not proved that way, yet prime · red: composite", 11 * u, True, "rs")])
    Pn.leaf(tm, AOKIN, height=0.8 * u, tone=0.8, burnish=0.1, glow=0.1)
    Pn.finish().save(out)
    print(out, 'uncertified', int(unc.sum()), 'composite', int(comp.sum()))

if __name__ == '__main__':
    render(int(sys.argv[1]), sys.argv[2])
