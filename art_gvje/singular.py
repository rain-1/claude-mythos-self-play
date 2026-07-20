"""Reproduce + extend the MO 513363 data: corank over Q of M_n = [i (x) j]_{1<=i,j<=n}.

Rank mod a ~2^20 prime lower-bounds rank over Q and equals it unless the prime
divides certain minors; two independent primes, take max rank.
Elimination trick: keep bulk un-modded (entries stay < n*p^2 << 2^63), mod only
the pivot row/column each step -> pure int64 multiply-subtract inner loop.
"""
import numpy as np, sys, time
from nim import nmul

N = 1300
idx = np.arange(1, N + 1, dtype=np.int32)
M0 = nmul(idx[:, None], idx[None, :]).astype(np.int64)
print('table built', M0.shape, flush=True)

def rank_mod(Mfull, n, p):
    A = np.mod(Mfull[:n, :n], p).copy()
    rank = 0
    rows = A.shape[0]
    r = 0
    for c in range(n):
        col = np.mod(A[r:, c], p)
        nz = np.nonzero(col)[0]
        if nz.size == 0:
            continue
        piv = r + nz[0]
        if piv != r:
            A[[r, piv]] = A[[piv, r]]
        A[r] = np.mod(A[r], p)
        inv = pow(int(A[r, c]), p - 2, p)
        if r + 1 < rows:
            factors = (np.mod(A[r+1:, c], p) * inv) % p
            A[r+1:] -= factors[:, None] * A[r][None, :]
        rank += 1
        r += 1
        if r == rows:
            break
    return rank

primes = [1048573, 1048583]
t0 = time.time()
coranks = np.zeros((len(primes), N), dtype=np.int32)
for pi, p in enumerate(primes):
    for n in range(1, N + 1):
        coranks[pi, n-1] = n - rank_mod(M0, n, p)
        if n % 100 == 0:
            print(f'p={p} n={n} corank={coranks[pi,n-1]} t={time.time()-t0:.0f}s', flush=True)
corank = np.min(coranks, axis=0)   # max rank = min corank
np.save('corank.npy', corank)

sing = np.where(corank > 0)[0] + 1
# condense to intervals
ivs = []
for s in sing:
    if ivs and s == ivs[-1][1] + 1: ivs[-1][1] = s
    else: ivs.append([s, s])
print('singular intervals:', ivs)
print('MO claim: [19,28] [43,44] [55,55] [259,508] [517,764] [773,1018] [1035,1161] (then nonsingular to 1260)')
print('corank peaks: n=23 ->', corank[22], '(MO: 3);  n=383 ->', corank[382], '(MO: 63)')
print('max corank overall:', corank.max(), 'at n=', int(np.argmax(corank))+1)
