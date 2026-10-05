# E(a,b,c) for all a+b+c <= N (K=3), layer by layer; saves the slice a+b+c = N
import numpy as np, sys
N = int(sys.argv[1])
E = np.zeros((N + 1, N + 1, N + 1))
a, b, c = np.meshgrid(*[np.arange(N + 1)] * 3, indexing='ij')
S = a + b + c
for s in range(1, N + 1):
    m = (S == s)
    aa, bb, cc = a[m], b[m], c[m]
    nz = (aa > 0).astype(int) + (bb > 0) + (cc > 0)
    tot = np.zeros(aa.shape)
    for d, (x, y, z) in enumerate([(aa - 1, bb, cc), (aa, bb - 1, cc), (aa, bb, cc - 1)]):
        ok = [aa, bb, cc][d] > 0
        tot += np.where(ok, E[np.maximum(x, 0), np.maximum(y, 0), np.maximum(z, 0)], 0)
    val = np.where(nz == 1, aa + bb + cc, tot / np.maximum(nz, 1))
    E[aa, bb, cc] = val
np.save(f'field_{N}.npy', E[S == N].astype(np.float64)); np.save(f'fieldidx_{N}.npy', np.stack([a[S == N], b[S == N], c[S == N]], 1))
sl = E[S == N]; idx = np.stack([a[S == N], b[S == N], c[S == N]], 1)
i = np.argmin(np.where((idx > 0).all(1), sl, np.inf)); print('argmin interior', idx[i], sl[i])
