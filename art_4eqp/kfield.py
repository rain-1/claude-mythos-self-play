# Orthonormal Krawtchouk matrix  phi[k, x] = K_k(x; N) * sqrt(C(N,x) / (C(N,k) 2^N))     (MO 515696)
# where K_k(x; N) = C_k((1-z)^x (1+z)^(N-x)) = C(N,k) 2F1(-k,-x;-N;2).  phi is symmetric and orthogonal.
# EXACT: integer recurrence (k+1) K_{k+1} = (N-2x) K_k - (N-k+1) K_{k-1} on Python ints; logs taken from the
# big ints directly (the values span 2^-4096 .. 1, beyond float64).
import numpy as np, sys
from math import lgamma, log
L2 = log(2)
def log2abs(a):
    if a == 0: return -np.inf
    a = abs(a); b = a.bit_length()
    if b <= 60: return np.log2(float(a))
    return b - 60 + np.log2(float(a >> (b - 60)))
def quadrant(N):
    h = N // 2 + 1
    xs = list(range(h))
    lc = np.array([(lgamma(N + 1) - lgamma(n + 1) - lgamma(N - n + 1)) / L2 for n in range(N + 1)])
    LP = np.zeros((h, h)); S = np.zeros((h, h), np.int8)
    Km = [0] * h; K0 = [1] * h
    def put(k, row):
        LP[k] = [log2abs(a) for a in row]
        S[k] = [(a > 0) - (a < 0) for a in row]
        LP[k] += 0.5 * (lc[:h] - lc[k] - N)
    put(0, K0)
    for k in range(h - 1):
        K1 = [((N - 2 * x) * a - (N - k + 1) * b) // (k + 1) for x, a, b in zip(xs, K0, Km)]
        Km, K0 = K0, K1
        put(k + 1, K1)
    return LP, S
def full(N):
    LP, S = quadrant(N); h = LP.shape[0]
    k = np.arange(N + 1)[:, None]; x = np.arange(N + 1)[None, :]
    kk = np.minimum(k, N - k); xx = np.minimum(x, N - x)
    sgn = np.where((x > N // 2) & (kk % 2 == 1), -1, 1) * np.where((k > N // 2) & (xx % 2 == 1), -1, 1)
    return LP[kk, xx].astype(np.float32), (S[kk, xx] * sgn).astype(np.int8)
if __name__ == '__main__':
    N = int(sys.argv[1])
    LP, S = full(N)
    P = S * np.exp2(LP.astype(np.float64))
    if N <= 1200: print('orth err', np.abs(P @ P.T - np.eye(N + 1)).max())
    print('sym', np.abs(P - P.T).max(), 'zeros', int((S == 0).sum()))
    np.savez_compressed(f'kf{N}.npz', LP=LP, S=S)
