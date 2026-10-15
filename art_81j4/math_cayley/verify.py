"""Exact verification of the coefficient-extraction formula for Cayley's formula.

A(n) := n! [x^n y^{n-1}] log(1 + sum_{m>=1} x^m/m! (1+y)^{C(m,2)})
      = sum over compositions (b_1..b_k) of n, b_i>=1:
           (-1)^{k-1}/k * n!/(b_1!...b_k!) * binom(sum_i C(b_i,2), n-1)
B(n) := same with binom(..., n)   (unicyclic connected graphs, OEIS A057500)
"""
from fractions import Fraction
from math import comb, factorial
from functools import lru_cache
import sys

def compositions_sum(n, e):
    # D[k][m][s] would be big; instead DP over (parts used k, total size m, edges s)
    # weight = prod 1/b_i!, track s = sum C(b_i,2) exactly.
    # dp[m] = dict k -> dict s -> Fraction
    dp = [dict() for _ in range(n + 1)]
    dp[0] = {0: {0: Fraction(1)}}
    for m in range(1, n + 1):
        cur = {}
        for b in range(1, m + 1):
            for k, d in dp[m - b].items():
                tgt = cur.setdefault(k + 1, {})
                for s, w in d.items():
                    s2 = s + comb(b, 2)
                    tgt[s2] = tgt.get(s2, 0) + w / factorial(b)
        dp[m] = cur
    tot = Fraction(0)
    for k, d in dp[n].items():
        for s, w in d.items():
            tot += Fraction((-1) ** (k - 1), k) * w * comb(s, e)
    return tot * factorial(n)

def partitions_check(n, e):
    # same sum over SET PARTITIONS with weight (-1)^{k-1}(k-1)!, via block-size multiset
    from sympy.utilities.iterables import partitions
    tot = 0
    for p in partitions(n):
        k = sum(p.values())
        cnt = factorial(n)
        for b, mult in p.items():
            cnt //= factorial(b) ** mult * factorial(mult)
        s = sum(comb(b, 2) * mult for b, mult in p.items())
        tot += (-1) ** (k - 1) * factorial(k - 1) * cnt * comb(s, e)
    return tot

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    A057500 = [0, 0, 1, 15, 222, 3660, 68295, 1436568, 33779340, 880107840, 25201854045,
               787368574080, 26667815195274, 973672928417280]  # n=1..14, from oeis.org/A057500/b057500.txt
    print("n | A(n) | n^(n-2) | ok | B(n) unicyclic | A057500 | ok")
    for n in range(1, N + 1):
        A = compositions_sum(n, n - 1)
        A2 = partitions_check(n, n - 1)
        B = compositions_sum(n, n)
        assert A.denominator == 1 and B.denominator == 1 and A == A2
        cay = Fraction(n) ** (n - 2)
        ref = A057500[n - 1] if n <= len(A057500) else None
        print(n, int(A), cay, A == cay, int(B), ref, (ref is None) or int(B) == ref)

    # Check the coefficient recurrence obtained from (1+y) d/dy G = (x^2/2) d^2/dx^2 G with C = log G:
    # (e+1) c_{n,e+1} = (C(n,2) - e) c_{n,e} + 1/2 sum_{k=1}^{n-1} C(n,k) k (n-k) sum_{a+b=e} c_{k,a} c_{n-k,b}
    M = 10
    c = {(n, e): compositions_sum(n, e) for n in range(1, M + 1) for e in range(0, comb(n, 2) + 1)}
    get = lambda n, e: c.get((n, e), 0)
    ok = True
    for n in range(1, M + 1):
        for e in range(0, comb(n, 2)):
            conv = sum(comb(n, k) * k * (n - k) * get(k, a) * get(n - k, e - a)
                       for k in range(1, n) for a in range(0, e + 1))
            ok &= (e + 1) * get(n, e + 1) == (comb(n, 2) - e) * get(n, e) + Fraction(conv, 2)
    print("edge-recurrence holds for n <=", M, ":", ok)
    print("c_{n,e} = 0 for e < n-1 (n<=10):", all(get(n, e) == 0 for n in range(1, M + 1) for e in range(0, n - 1)))
