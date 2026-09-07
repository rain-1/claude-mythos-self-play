"""runs.py — MO 514975: longest run of 1s vs longest run of 0s in a fair binary string.

R_n = longest run (of either symbol) in a uniform string of length n. The posted answer notes
max(L0, L1) ~ 1 + R_{n-1} (drop the first symbol; a run of the SAME symbol as the first is
one longer). Since L0 + L1 = max + min,

    l*(n) = E max = 1 + E R_{n-1},      l_*(n) = E min = 2 E R_n - E R_{n-1} - 1,
    l*(n) - l_*(n) = 2 - 2 (E R_n - E R_{n-1})  -->  2.

So the expected gap between the two longest runs tends to EXACTLY 2, and the ratio tends to 1
like 1 - 2/log2 n. Exact machinery: P(R_n <= L) = 2 * comp_L(n) / 2^n where comp_L counts
compositions of n with parts <= L (linear recurrence of order L), evaluated at n = 2^k by
matrix powers; brute force to n = 18 checks both the identity and the machinery.
"""
import numpy as np
from itertools import product


def longest_runs(bits):
    L = [0, 0]; cur = None; run = 0
    for b in bits:
        if b == cur:
            run += 1
        else:
            cur = b; run = 1
        L[b] = max(L[b], run)
    return L


def brute(n):
    tot_max = tot_min = tot_R = 0
    for bits in product((0, 1), repeat=n):
        a, b = longest_runs(bits)
        tot_max += max(a, b); tot_min += min(a, b); tot_R += max(a, b)
    return tot_max / 2 ** n, tot_min / 2 ** n


def ER_exact_small(n):
    """E R_n by brute force (R_n = longest run of either symbol)"""
    return brute(n)[0]


def Q_le(L, n):
    """P(longest run of 1s <= L) in a uniform string of length n (matrix power, any n).
    q(m) = 1 for m <= L; q(m) = sum_{j=0..L} q(m-1-j) / 2^(j+1) (a block of j ones then a zero)."""
    if n <= L:
        return 1.0
    d = L + 1
    M = np.zeros((d, d))
    M[0, :] = [0.5 ** (j + 1) for j in range(d)]
    for i in range(1, d):
        M[i, i - 1] = 1.0
    v = np.ones(d)                       # state at m = L: (q(L), q(L-1), ..., q(0))
    P = np.eye(d); B = M.copy(); e = n - L
    while e:
        if e & 1:
            P = P @ B
        B = B @ B; e >>= 1
    return (P @ v)[0]


def EL1(n, Lmax=None):
    """E[longest run of 1s] = sum_{L>=0} P(L1 > L)"""
    if n <= 0:
        return 0.0
    Lmax = Lmax or int(np.log2(n) + 45)
    return sum(1 - Q_le(L, n) for L in range(0, Lmax + 1))


def ER_either(n):
    """E[longest run of either symbol] = 1 + E L1(n-1) (difference-string bijection)"""
    return 1 + EL1(n - 1)


if __name__ == '__main__':
    print('brute force check (n, E max, 1+E L1(n-1), E min, 2 E L1(n) - E L1(n-1) - 1):')
    for n in range(2, 15):
        emax, emin = brute(n)
        a = EL1(n); b = EL1(n - 1)
        print(f'  n={n:2d}  {emax:.6f} {1 + b:.6f}   {emin:.6f} {2 * a - b - 1:.6f}')
    print('\nexact values at n = 2^k (E L1 = expected longest run of 1s):')
    print('   k        E L1(n)     E L1(n-1)      gap = l*-l_*     ratio l_*/l*    1-2/log2(n)')
    for k in range(3, 29):
        n = 2 ** k
        a = EL1(n); b = EL1(n - 1)
        lstar = 1 + b; lmin = 2 * a - b - 1
        print(f'  {k:2d}  {a:14.8f} {b:14.8f}   {lstar - lmin:14.10f}   {lmin / lstar:12.8f}   {1 - 2 / k:12.8f}')
