"""Panel 3 data: log|det M_n| curve, sampled extension, kernel at n=383."""
import numpy as np, time
from nim import nmul

N = 1300
idx = np.arange(1, 2600, dtype=np.int32)
Mfull = nmul(idx[:, None], idx[None, :]).astype(np.float64)

t0 = time.time()
logdet = np.full(N, -np.inf)
for n in range(1, N + 1):
    s, ld = np.linalg.slogdet(Mfull[:n, :n])
    logdet[n-1] = ld if s != 0 else -np.inf
np.save('logdet.npy', logdet)
print('slogdet 1..1300 done', time.time()-t0, flush=True)

# sampled extension 1300..2560 (poster verified nonsingular to 2048)
ext_n = np.unique(np.geomspace(1310, 2560, 24).astype(int))
ext_ld = []
for n in ext_n:
    s, ld = np.linalg.slogdet(Mfull[:n, :n])
    ext_ld.append(ld if s != 0 else -np.inf)
np.save('ext_n.npy', ext_n); np.save('ext_ld.npy', np.array(ext_ld))
print('extension done', time.time()-t0, flush=True)

# kernel basis mod p at n=383 (corank should be 63)
p = 1048573
n = 383
A = (nmul(idx[:n, None], idx[None, :n]) % p).astype(np.int64)
# row-reduce to RREF mod p, track pivot columns
Ar = A.copy(); piv_cols = []; r = 0
for c in range(n):
    col = Ar[r:, c] % p
    nz = np.nonzero(col)[0]
    if nz.size == 0: continue
    q = r + nz[0]
    if q != r: Ar[[r, q]] = Ar[[q, r]]
    Ar[r] = (Ar[r] * pow(int(Ar[r, c] % p), p-2, p)) % p
    others = np.concatenate([np.arange(0, r), np.arange(r+1, n)])
    f = Ar[others, c] % p
    Ar[others] = (Ar[others] - f[:, None] * Ar[r][None, :]) % p
    piv_cols.append(c); r += 1
    if r == n: break
piv = np.array(piv_cols)
free = np.setdiff1d(np.arange(n), piv)
print('n=383 rank', r, 'corank', n - r, 'free cols (1-based):', (free+1)[:80])
# kernel vectors: for each free col f: x_f = 1, x_piv = -RREF[:, f]
K = np.zeros((len(free), n), dtype=np.int64)
for t, fc in enumerate(free):
    K[t, fc] = 1
    K[t, piv] = (-Ar[:r, fc]) % p
# verify
chk = (A @ K.T) % p
print('kernel verified (max residue):', int(np.abs(chk).max()))
# center representatives to [-p/2, p/2] for rendering
Kc = np.where(K > p // 2, K - p, K)
np.save('kernel383.npy', Kc); np.save('free383.npy', free)
print('done', time.time()-t0)
