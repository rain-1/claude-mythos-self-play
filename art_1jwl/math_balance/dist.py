# exact distribution of the signed sums ±1^k ± ... ± n^k for n = 1..N  (counts as float64, reach exact)
import numpy as np, sys
def dists(k, N):
    """yields (n, T, cnt) where cnt[s+T] = number of sign choices with sum s (float64)"""
    c = np.array([1.0]); T = 0
    for n in range(1, N+1):
        w = n**k; T2 = T + w
        d = np.zeros(2*T2+1)
        d[0:2*T+1] += c            # sum - w  -> index (s-w)+T2 = (s+T)
        d[2*w:2*w+2*T+1] += c      # sum + w
        c = d; T = T2
        yield n, T, c
if __name__ == "__main__":
    k = int(sys.argv[1]); N = int(sys.argv[2])
    for n, T, c in dists(k, N):
        nz = np.nonzero(c)[0] - T
        m = np.abs(nz).min()
        print(n, T, len(nz), 2**n, m, c.max())
