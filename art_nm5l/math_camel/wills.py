"""Camel wills: herd n, k sons with DISTINCT unit shares 1/a_1 > ... > 1/a_k, every a_i | n+1,
and sum 1/a_i = n/(n+1)  (borrow one camel, divide, return it).
Equivalently N = n+1 and N-1 = sum of k distinct proper divisors of N.
Enumerate by Egyptian-fraction search: 1 = 1/a_1+...+1/a_k+1/N, a_1<...<a_k, a_i | N."""
import sys
from fractions import Fraction as F
from math import lcm, gcd
def search(k, rem, lo, L, chosen, out):
    # rem = remaining after chosen shares; need rem = (k more shares) + 1/N, lcm(chosen..) | N
    if k == 0:
        # rem must be 1/N with all a | N
        if rem.numerator == 1 and rem.denominator % L == 0:
            out.append((tuple(chosen), rem.denominator))
        return
    # next a > lo, 1/a < rem, and k/a + 1/a >= rem roughly: (k+1)/a >= rem (since 1/N <= 1/a)
    a = max(lo + 1, rem.denominator // rem.numerator + 1)
    while F(k + 1, a) >= rem:
        search(k - 1, rem - F(1, a), a, lcm(L, a), chosen + [a], out)
        a += 1
for k in range(1, int(sys.argv[1]) + 1):
    out = []
    search(k, F(1), 1, 1, [], out)
    herds = sorted(N - 1 for _, N in out)
    print(k, 'wills:', len(out), 'distinct herds:', len(set(herds)), 'largest:', herds[-1],
          'smallest:', herds[0], flush=True)
    if k <= 4:
        for a, N in sorted(out, key=lambda t: t[1]): print('   ', N - 1, a, [N // x for x in a])
