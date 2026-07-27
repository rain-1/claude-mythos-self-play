"""Exact Borwein integral engine.

I_n = integral_0^inf prod_{k=0}^n sinc(t/(2k+1)) dt.

Fourier route: sinc(t/a) has FT  a*pi*1_{[-1/a,1/a]}(w)  (convention F[f](w)=int f e^{-iwt}).
Then int_R prod f_k = (1/2pi) * (F0 * F1 * ... * Fn)(0)   (convolution at 0).
Normalize: let g_a = (a/2)*1_{[-1/a,1/a]} be the *probability* box of half-width 1/a.
prod sinc(t/a_k) FT = prod (2pi/(2)) ... cleaner to just build:
  h_n = 1_{[-1,1]} conv g_{3} conv g_{5} ... conv g_{2n+1}
Then I_n (full line) = pi * h_n(0), and one-sided = pi/2 * h_n(0).
h_n is piecewise polynomial with rational breakpoints/coeffs -> exact via Fraction.
"""
from fractions import Fraction as F

class PP:
    """piecewise polynomial: sorted breakpoints b[0..m], coeffs[i] = poly on (b[i],b[i+1]) in powers of x."""
    def __init__(self, bps, polys):
        self.b = bps; self.p = polys
    def eval(self, x):
        if x <= self.b[0] or x >= self.b[-1]: return F(0)
        for i in range(len(self.p)):
            if self.b[i] <= x <= self.b[i+1]:
                acc = F(0)
                for c in reversed(self.p[i]): acc = acc*x + c
                return acc
        return F(0)

def polyint(c):
    """antiderivative coeffs of poly coeffs c (c[j] x^j)."""
    return [F(0)] + [c[j]/ (j+1) for j in range(len(c))]

def peval(c, x):
    acc = F(0)
    for cc in reversed(c): acc = acc*x + cc
    return acc

def conv_box(pp, w):
    """convolve pp with probability box of half-width w: (1/(2w)) int_{x-w}^{x+w} pp(u) du."""
    # antiderivative of pp as a piecewise poly with continuity
    A = []  # antiderivative coeffs per piece, plus running constant
    consts = [F(0)]
    for i, c in enumerate(pp.p):
        ic = polyint(c)
        A.append(ic)
    # cumulative constants so antiderivative is continuous, F(b0)=0
    run = F(0); C = []
    for i in range(len(pp.p)):
        C.append(run - peval(A[i], pp.b[i]))
        run = run + peval(A[i], pp.b[i+1]) - peval(A[i], pp.b[i])
    total = run
    def Fanti(x):
        if x <= pp.b[0]: return F(0)
        if x >= pp.b[-1]: return total
        for i in range(len(pp.p)):
            if pp.b[i] <= x <= pp.b[i+1]:
                return peval(A[i], x) + C[i]
    # new breakpoints: b_i +- w
    news = sorted(set([b + w for b in pp.b] + [b - w for b in pp.b]))
    nb, npol = [news[0]], []
    inv = F(1, 2) / w
    for i in range(len(news)-1):
        lo, hi = news[i], news[i+1]
        # on (lo,hi), h(x) = inv*(Fanti(x+w) - Fanti(x-w)); both x+w and x-w stay within one source piece
        # build poly by shifting: find pieces
        def piece_poly_at(xq):
            # returns (coeffs, is_flat_low, is_flat_high) for antiderivative near point xq
            if xq <= pp.b[0]: return None, F(0)
            if xq >= pp.b[-1]: return None, total
            for j in range(len(pp.p)):
                if pp.b[j] <= xq <= pp.b[j+1]:
                    return (A[j], C[j]), None
            raise RuntimeError
        mid = (lo+hi)/2
        hi_part, hi_const = piece_poly_at(mid + w)
        lo_part, lo_const = piece_poly_at(mid - w)
        # compose A(x+w): shift polynomial
        def shift(coeffs, s):
            # returns coeffs of p(x+s)
            n = len(coeffs); out = [F(0)]*n
            # binomial expansion
            from math import comb
            for j in range(n):
                cj = coeffs[j]
                if cj == 0: continue
                for i2 in range(j+1):
                    out[i2] += cj * comb(j, i2) * s**(j-i2)
            return out
        if hi_part is not None:
            ph = shift(hi_part[0], w); ph[0] += hi_part[1]
        else:
            ph = [hi_const]
        if lo_part is not None:
            pl = shift(lo_part[0], -w); pl[0] += lo_part[1]
        else:
            pl = [lo_const]
        m = max(len(ph), len(pl))
        ph += [F(0)]*(m-len(ph)); pl += [F(0)]*(m-len(pl))
        npol.append([inv*(ph[j]-pl[j]) for j in range(m)])
        nb.append(hi)
    return PP(nb, npol)

if __name__ == '__main__':
    # start: indicator of [-1,1] (height 1)
    h = PP([F(-1), F(1)], [[F(1)]])
    print("n  a_n  h_n(0)  (I_n = pi/2 * h_n(0), one-sided)")
    vals = []
    for n in range(0, 9):
        if n > 0:
            a = 2*n+1
            h = conv_box(h, F(1, a))
        v = h.eval(F(0))
        vals.append(v)
        print(n, 2*n+1, v, float(1-v))
    # plateau half-widths: 1 - sum 1/(2k+1)
    s = F(0)
    for n in range(1, 9):
        s += F(1, 2*n+1)
        print("plateau half-width after", 2*n+1, ":", 1-s, float(1-s))
