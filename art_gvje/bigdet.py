import numpy as np, time
from nim import nmul
ns = [3000, 3600, 4300, 5200, 6200, 7500, 9000, 10800, 13000, 15600, 18700, 21000]
res = []
t0 = time.time()
for n in ns:
    idx = np.arange(1, n+1, dtype=np.int32)
    M = nmul(idx[:, None], idx[None, :]).astype(np.float64)
    s, ld = np.linalg.slogdet(M)
    res.append((n, s, ld))
    print(n, s, ld, f'{time.time()-t0:.0f}s', flush=True)
    del M
np.save('bigdet.npy', np.array([(n, s, ld) for n, s, ld in res]))
