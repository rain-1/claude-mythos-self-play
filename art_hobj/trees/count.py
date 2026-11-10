"""g(n,k) = #{f:[n]->[n] : f^k is constant} = n! [x^n] T_k,  T_0 = x,  T_k = x exp(T_{k-1})
(rooted labelled trees of height <= k; the root is the fixed point).  MO 508368."""
from fractions import Fraction as F
from math import factorial, log
N = 40
def mul(a, b):
    c = [F(0)] * (N + 1)
    for i, x in enumerate(a):
        if x:
            for j in range(N + 1 - i):
                if b[j]: c[i + j] += x * b[j]
    return c
def exp(a):                                  # a[0] == 0
    e = [F(0)] * (N + 1); e[0] = F(1)
    for n in range(1, N + 1):
        e[n] = sum(k * a[k] * e[n - k] for k in range(1, n + 1)) / n
    return e
T = [F(0)] * (N + 1); T[1] = F(1); tab = {}
for k in range(1, N):
    E = exp(T); T = [F(0)] + E[:N]
    tab[k] = [int(T[n] * factorial(n)) for n in range(N + 1)]
if __name__ == '__main__':
    for n in range(1, 11): print(n, [tab[k][n] for k in range(1, n)] if n > 1 else [1])
    for n in (10, 20, 40):
        print('h(n,k)=log_n g:', n, [round(log(tab[k][n]) / log(n), 2) for k in range(1, min(n, 9))])
        print('  share of all n^(n-1) trees:', [round(tab[k][n] / n ** (n - 1), 4) for k in range(1, min(n, 13))])
