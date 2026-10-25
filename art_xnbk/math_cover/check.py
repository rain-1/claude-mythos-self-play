# MO 516229: f(n,m)=n^2+2n+(2n+1)m, g(n,m)=n^2+3n+(2n+1)m, n>=1, m>=0.
import numpy as np
L = 2_000_000
cov = np.zeros(L + 1, bool)
n = 1
while n * n + 2 * n <= L:
    d = 2 * n + 1
    cov[n * n + 2 * n::d] = True
    cov[n * n + 3 * n::d] = True
    n += 1
unc = np.nonzero(~cov)[0][1:]
# primes up to 4L+8
P = 4 * L + 8
sv = np.ones(P + 1, bool); sv[:2] = False
for p in range(2, int(P ** 0.5) + 1):
    if sv[p]: sv[p * p::p] = False
N = np.arange(L + 1)
twin = sv[4 * N + 5] & sv[4 * N + 7]
mism = [int(x) for x in np.nonzero((~cov) != twin)[0] if x > 0]
print('uncovered count', len(unc), 'first', unc[:30].tolist())
print('twin-type count', int(twin[1:].sum()))
print('mismatches', len(mism), mism[:40])
for x in mism[:15]:
    print(x, 4 * x + 5, sv[4 * x + 5], 4 * x + 7, sv[4 * x + 7], 'covered' if cov[x] else 'uncovered')
print('---- corrected: d | 4N+3 (f) and d | 4N+5 (g)')
sq = np.zeros(P + 1, bool)
for p in range(3, int(P ** 0.5) + 1):
    if sv[p]: sq[p * p] = True
ok = lambda M: sv[M] | sq[M]   # prime or prime square
pred = ok(4 * N + 3) & ok(4 * N + 5)
mism = [int(x) for x in np.nonzero((~cov) != pred)[0] if x > 0]
print('mismatches', len(mism), mism[:20])
tw = sv[4 * N + 3] & sv[4 * N + 5]
print('uncovered:', int((~cov[1:]).sum()), ' twin (4N+3,4N+5):', int(tw[1:].sum()), ' prime-square cases:', int((pred & ~tw)[1:].sum()),
      [int(x) for x in np.nonzero(pred & ~tw)[0][:12]])
