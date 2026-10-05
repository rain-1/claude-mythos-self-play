# MO 515413: Narayana polynomials C_n(t) = sum_k N(n,k+1) t^k, coefficients mod 2.
import numpy as np, sys
from math import comb
def table(M):
    T = np.zeros((M + 1, M + 1), np.uint8)
    for n in range(1, M + 1):
        for k in range(n):
            T[n, k] = (comb(n, k) * comb(n - 1, k) // (k + 1)) & 1
    return T
if __name__ == '__main__':
    M = int(sys.argv[1]); T = table(M); np.save(f'nar{M}.npy', T)
    # verify OP identity f(2^m+k) = f(k)(1+t^{2^m}) for 2^m+k <= M
    bad = 0
    for m in range(2, 12):
        for k in range(1, 2 ** m - 1):
            n = 2 ** m + k
            if n > M: break
            f = np.zeros(M + 1, np.uint8); f[:k] = T[k, :k]
            g = f.copy(); g[2 ** m:] ^= f[:M + 1 - 2 ** m]
            if not np.array_equal(g[:n], T[n, :n]): bad += 1
    print('identity failures', bad, 'density', T.sum() / (M * (M + 1) / 2))
