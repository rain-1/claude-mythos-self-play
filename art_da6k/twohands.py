"""twohands.py — the circle as a topological fractal with two maps (MO 488999, theorem added 2026-09-03).

T = R/Z.  L >= 3, delta = 1/(2L), r = (L-2)/(L-1).  The fold
  f(x) = 1/2 - 1/L + 2x            on [0, delta]
       = 1/2 - r (x - delta)       on [delta, 1/2]
       = 1/L - 2 (x - 1/2)         on [1/2, 1/2 + delta]
       = r (x - 1/2 - delta)       on [1/2 + delta, 1]
has image [0, 1/2];  g = f + 1/2 has image [1/2, 1];  f(T) u g(T) = T.
Claim: every composition of N maps has image of diameter < eps for N = N(eps).

We compute the images of ALL 2^k words exactly (Fractions for the certificate, floats for the picture).
An arc is stored as a lift [lo, hi] with 0 <= hi - lo <= 1.
"""
from fractions import Fraction as Fr
import numpy as np, sys, json

def fold(L, exact=True):
    K = (lambda a, b: Fr(a, b)) if exact else (lambda a, b: a / b)
    d = K(1, 2 * L); r = K(L - 2, L - 1); half = K(1, 2); oneL = K(1, L)
    # breakpoints and lift values on [0,1]
    xs = [K(0, 1), d, half, half + d, K(1, 1)]
    ys = [half - oneL, half, oneL, K(0, 1), half - oneL]
    return xs, ys

def F_eval(xs, ys, x):
    """lift of f at x in [0,1] (piecewise linear through (xs,ys))"""
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    raise ValueError(x)

def image_of_arc(xs, ys, lo, hi, shift):
    """image (lift) of the arc [lo,hi] (hi-lo<=1) under f + shift.  Returns (lo', hi')."""
    if hi - lo >= 1:
        vals = ys
    else:
        a = lo - (lo // 1); b = a + (hi - lo)   # a in [0,1), b in [a, a+1)
        vals = [F_eval(xs, ys, a), F_eval(xs, ys, b if b <= 1 else b - 1)]
        for x in xs[1:-1]:
            if a <= x <= b or a <= x + 1 <= b:
                vals.append(F_eval(xs, ys, x))
        if b > 1:
            vals.append(ys[0])
    return min(vals) + shift, max(vals) + shift

def all_words(L, K, exact=True):
    """images of all words of length 1..K.  words[k] = list of (lo,hi) in word order (binary, f=0,g=1,
    first letter = outermost map = most significant bit)."""
    xs, ys = fold(L, exact)
    one = Fr(1) if exact else 1.0
    half = Fr(1, 2) if exact else 0.5
    levels = {0: [(0 * one, one)]}
    for k in range(1, K + 1):
        prev = levels[k - 1]
        cur = []
        # word w1 w2..wk : image = w1( image(w2..wk) );  order: w1 most significant
        for letter in (0, 1):
            sh = half if letter else 0 * one
            for (lo, hi) in prev:
                cur.append(image_of_arc(xs, ys, lo, hi, sh))
        levels[k] = cur
    return levels

def stats(levels):
    out = {}
    for k, arcs in levels.items():
        if k == 0: continue
        d = [hi - lo for lo, hi in arcs]
        out[k] = (max(d), sum(d) / len(d), min(d))
    return out

def coverage(arcs, nbins=3600):
    """how many arcs cover each point of the circle"""
    cov = np.zeros(nbins, int)
    for lo, hi in arcs:
        a = float(lo) % 1.0; ln = float(hi - lo)
        i0 = int(a * nbins); n = int(np.ceil(ln * nbins))
        idx = (i0 + np.arange(n + 1)) % nbins
        cov[idx] += 1
    return cov

if __name__ == '__main__':
    res = {}
    for L in (3, 4, 5, 6, 8, 12):
        lv = all_words(L, 14, exact=(L <= 6))
        st = stats(lv)
        print(f'L={L}: max diam by depth:', ' '.join(f'{float(st[k][0]):.4f}' for k in range(1, 15)))
        ratios = [float(st[k][0] / st[k - 1][0]) for k in range(2, 15)]
        print(f'      ratio of successive max diam: {ratios[-1]:.4f};  first depth with all arcs < 1/4:',
              next((k for k in range(1, 15) if st[k][0] < 0.25), None))
        cov = coverage(lv[10])
        print(f'      coverage at depth 10: min {cov.min()} max {cov.max()} (of 1024 arcs) — covers: {cov.min() > 0}')
        res[L] = {k: [float(x) for x in st[k]] for k in st}
    json.dump(res, open('twohands_stats.json', 'w'), indent=1)
