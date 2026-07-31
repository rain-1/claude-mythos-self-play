"""Pade machinery for f(z) = (1 - z^3)^(-1/2)   (MO 122539).

g(w) = (1 - w)^(-1/2) = sum_k binom(2k,k) (w/4)^k  (exact rational coeffs).
[m/m] Pade of g: denominator B solves the Toeplitz system; numerator A = (c*B)
truncated.  Composition theorem (uniqueness of Pade): A(z^3)/B(z^3) is the
[3m/3m] Pade approximant of f.  g is a Markov function of the measure
d mu(t) = (1/pi) (t-1)^(-1/2) dt on [1, oo), so all poles of [m/m] are real,
simple, in (1, oo), and interlace with zeros and with the previous order.
We verify all of that numerically at high precision.
"""
from fractions import Fraction
import mpmath as mp
import numpy as np


def g_coeffs(N):
    """Exact Taylor coefficients of (1-w)^(-1/2): c_k = binom(2k,k)/4^k."""
    c = [Fraction(1)]
    for k in range(1, N + 1):
        # c_k = c_{k-1} * (2k-1)/(2k)
        c.append(c[-1] * Fraction(2 * k - 1, 2 * k))
    return c


def pade_gm(m, dps=200):
    """[m/m] Pade of g at high precision. Returns (A, B) coefficient lists (mpf)."""
    mp.mp.dps = dps
    c = g_coeffs(2 * m + 1)
    cm = [mp.mpf(x.numerator) / mp.mpf(x.denominator) for x in c]
    # Toeplitz: sum_{j=0..m} b_j c_{m+k-j} = 0, k=1..m ; b_0 = 1
    M = mp.matrix(m, m)
    rhs = mp.matrix(m, 1)
    for k in range(1, m + 1):
        for j in range(1, m + 1):
            M[k - 1, j - 1] = cm[m + k - j]
        rhs[k - 1] = -cm[m + k]
    b = mp.lu_solve(M, rhs)
    B = [mp.mpf(1)] + [b[i] for i in range(m)]
    A = []
    for k in range(m + 1):
        s = mp.mpf(0)
        for j in range(0, min(k, m) + 1):
            s += B[j] * cm[k - j]
        A.append(s)
    return A, B


def poles_zeros(A, B, dps=200):
    mp.mp.dps = dps
    # roots of B and A (in w); B has degree m
    Brev = list(reversed(B))
    Arev = list(reversed(A))
    pol = mp.polyroots(Brev, maxsteps=200, extraprec=300)
    zer = mp.polyroots(Arev, maxsteps=200, extraprec=300)
    return pol, zer


def run_orders(orders, dps=220):
    """Compute pole/zero sets for a list of m values, with certificates."""
    out = {}
    for m in orders:
        A, B = pade_gm(m, dps=dps)
        pol, zer = poles_zeros(A, B, dps=dps)
        # certificates: realness and location
        max_im_p = max(abs(mp.im(p)) for p in pol)
        max_im_z = max(abs(mp.im(z)) for z in zer) if zer else mp.mpf(0)
        pr = sorted(mp.re(p) for p in pol)
        zr = sorted(mp.re(z) for z in zer)
        in_cut = all(p > 1 for p in pr)
        # zero/pole interlacing: z_1 < p_1 < z_2 < p_2 < ...
        inter = all(zr[i] < pr[i] for i in range(len(zr))) and \
                all(pr[i] < zr[i + 1] for i in range(len(zr) - 1))
        out[m] = dict(A=A, B=B, poles=pr, zeros=zr,
                      max_im=float(max(max_im_p, max_im_z)),
                      in_cut=bool(in_cut), interlace=bool(inter))
    return out
