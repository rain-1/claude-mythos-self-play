import numpy as np, time
from nim import nmul
p = 1048573
corank = np.load('corank.npy')
sing_n = [int(n) for n in np.where(corank > 0)[0] + 1]
idx = np.arange(1, 1302, dtype=np.int32)
M0 = (nmul(idx[:, None], idx[None, :]) % p).astype(np.int64)
t0 = time.time()
out = {}
for n in sing_n:
    A = M0[:n, :n].copy()
    piv = []; r = 0
    for c in range(n):
        col = A[r:, c] % p
        nz = np.nonzero(col)[0]
        if nz.size == 0: continue
        q = r + nz[0]
        if q != r: A[[r, q]] = A[[q, r]]
        A[r] = A[r] % p
        inv = pow(int(A[r, c]), p-2, p)
        if r+1 < n:
            f = (A[r+1:, c] % p * inv) % p
            A[r+1:] -= f[:, None] * A[r][None, :]
        piv.append(c); r += 1
    out[n] = (np.setdiff1d(np.arange(n), np.array(piv)) + 1).astype(np.int32)
    if n % 100 < 2: print(n, len(out[n]), f'{time.time()-t0:.0f}s', flush=True)
np.savez('freecols.npz', **{str(k): v for k, v in out.items()})
print('done', time.time()-t0)
