"""Exact tower profiles: y_n(x) = -log10(1 - h_n(x)), rational-exact evaluation."""
from fractions import Fraction as F
import numpy as np
from bisect import bisect_right
from borwein_exact import PP, conv_box

hs = []
h = PP([F(-1), F(1)], [[F(1)]])
hs.append(h)
for n in range(1, 9):
    h = conv_box(h, F(1, 2*n+1))
    hs.append(h)

def eval_pp(pp, x):
    if x <= pp.b[0] or x >= pp.b[-1]: return F(0)
    i = bisect_right(pp.b, x) - 1
    if i >= len(pp.p): i = len(pp.p)-1
    acc = F(0)
    for c in reversed(pp.p[i]): acc = acc*x + c
    return acc

plateau = [F(1)]
s = F(0)
for n in range(1, 9):
    s += F(1, 2*n+1)
    plateau.append(1-s)

out = {}
for n in range(9):
    pp = hs[n]
    p = plateau[n] if plateau[n] > 0 else F(0)
    # x-grid: dense near plateau edge, mirror later
    xs = sorted(set(
        [F(i, 800) for i in range(0, 961)] +                       # uniform to 1.2
        ([F(p) + F(i, 40000) for i in range(-200, 201)] if plateau[n] > 0 else []) +
        [F(i, 8000) for i in range(0, 400)]                          # dense near 0 for capped towers
    ))
    xs = [x for x in xs if 0 <= x <= F(6, 5)]
    ys = []
    for x in xs:
        v = 1 - eval_pp(pp, x)
        if v <= 0:
            ys.append(np.inf)
        else:
            ys.append(-(np.log10(float(v.numerator)) - np.log10(float(v.denominator)))
                      if v.numerator < 10**300 else float('nan'))
    # log10 of Fraction robustly:
    ys = []
    for x in xs:
        v = 1 - eval_pp(pp, x)
        if v <= 0:
            ys.append(np.inf)
        else:
            import math
            num, den = v.numerator, v.denominator
            l = (math.log10(num) if num < 10**308 else len(str(num))*np.log(10)/np.log(10)) 
            # safe: use string lengths for huge ints
            def log10big(z):
                sz = str(z)
                if len(sz) <= 15: return math.log10(z)
                return math.log10(int(sz[:15]) + 1e-9) + (len(sz)-15)
            ys.append(-(log10big(num) - log10big(den)))
    out[f'x{n}'] = np.array([float(x) for x in xs])
    out[f'y{n}'] = np.array(ys)
    finite = [y for y in ys if np.isfinite(y)]
    print(n, "plateau", float(p), "max finite y", max(finite))
np.savez('tower_profiles.npz', **out)
