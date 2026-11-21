"""Weyl's cyclic identity (MO 392723): legs a_0..a_n in independent uniform directions.
E_j = { |sum of the other legs| < a_j }  = 'the circle swept by leg j encloses home'.
Check sum_j P(E_j) = 1 two ways (quadrature of the Bessel formula; Monte Carlo), and tabulate the
distribution of N = number of j with E_j."""
import sys, numpy as np
from scipy import special, integrate
def W_bessel(b, others):
    # P(|R|<b) = b * int_0^inf J1(bt) prod J0(a t) dt ; integrate with a Gaussian regulariser -> extrapolate
    f = lambda t: b * special.j1(b * t) * np.prod([special.j0(a * t) for a in others])
    T = 4000.0; t = np.linspace(0, T, 4_000_001)
    v = b * special.j1(b * t) * np.prod([special.j0(a * t) for a in others], axis=0)
    # Cesaro (Fejer) summation kills the oscillating tail
    return float(np.trapezoid(v * (1 - t / T), t))
def mc(a, K=20_000_000, seed=1):
    rng = np.random.default_rng(seed); a = np.asarray(a); n = len(a)
    cnt = np.zeros(n); hist = np.zeros(n + 1); B = 2_000_000
    for _ in range(K // B):
        z = a * np.exp(2j * np.pi * rng.random((B, n)))
        S = z.sum(1, keepdims=True)
        E = np.abs(S - z) < a
        cnt += E.sum(0); hist += np.bincount(E.sum(1), minlength=n + 1)
    return cnt / K, hist / K
if __name__ == "__main__":
    a = [float(v) for v in sys.argv[1:]] or [4.0, 3.0, 2.4, 1.7, 1.1]
    wb = [W_bessel(a[j], a[:j] + a[j + 1:]) for j in range(len(a))]
    print('lengths', a); print('Bessel W', np.round(wb, 5), 'sum', round(sum(wb), 6))
    p, h = mc(a); print('MC     W', np.round(p, 5), 'sum', round(p.sum(), 5)); print('P(N=k)', np.round(h, 5), 'mean', round((h * np.arange(len(h))).sum(), 5))
    for n in (3, 4, 5, 8, 16):
        p, h = mc([1.0] * n, 10_000_000); print('equal legs n=%d' % n, 'W', round(p.mean(), 5), '1/n', round(1 / n, 5), 'P(N=k)', np.round(h, 4))
