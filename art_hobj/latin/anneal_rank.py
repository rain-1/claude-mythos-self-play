"""Play: look for Latin squares of low rank by annealing with cycle switches (rows / columns / symbols).
Energy = sqrt(sum of squared singular values beyond the k-th).  A hit (energy ~ 0) is verified exactly."""
import numpy as np, sys, math
from fractions import Fraction as F

def exact_rank(M):
    M = [[F(int(x)) for x in r] for r in M]; n = len(M); r = 0
    for c in range(n):
        p = next((i for i in range(r, n) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        for i in range(r + 1, n):
            f = M[i][c] / M[r][c]
            if f: M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r

def energy(L, k):
    s = np.linalg.svd(L.astype(float), compute_uv=False); return math.sqrt((s[k:] ** 2).sum())

def cycle_switch(L, rng):
    n = L.shape[0]; mode = rng.integers(3)
    if mode == 1: L = L.T
    if mode == 2:                                   # symbol switch = row switch in the conjugate square
        a, b = rng.choice(np.arange(1, n + 1), 2, replace=False); r0 = rng.integers(n)
        # in each row, positions of a and b; swap a<->b along a cycle of rows
        r = r0
        while True:
            ca = np.where(L[r] == a)[0][0]; cb = np.where(L[r] == b)[0][0]
            L[r, ca] = b; L[r, cb] = a
            # column cb now has two b? it had b at (r,cb) -> now a; column ca now has b twice: find other row with b in column ca
            rr = np.where((L[:, ca] == b) & (np.arange(n) != r))[0]
            if len(rr) == 0: break
            r = rr[0]
            if r == r0: break
        return L
    a, b = rng.choice(n, 2, replace=False); c0 = rng.integers(n); cols = [c0]; x = L[b, c0]
    while x != L[a, c0]:
        c = np.where(L[a] == x)[0][0]; cols.append(c); x = L[b, c]
    if len(cols) < n:
        t = L[a, cols].copy(); L[a, cols] = L[b, cols]; L[b, cols] = t
    return L.T if mode == 1 else L

def is_latin(L):
    n = L.shape[0]; s = list(range(1, n + 1))
    return all(sorted(r) == s for r in L.tolist()) and all(sorted(c) == s for c in L.T.tolist())

def run(n, k, iters, seed, T0=1.0, T1=0.02, start=None):
    rng = np.random.default_rng(seed)
    L = np.array([[(i + j) % n + 1 for j in range(n)] for i in range(n)]) if start is None else start.copy()
    for _ in range(200 * n): L = cycle_switch(L.copy(), rng)
    E = energy(L, k); best = (E, L.copy())
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        M = cycle_switch(L.copy(), rng); E2 = energy(M, k)
        if E2 <= E or rng.random() < math.exp(-(E2 - E) / T):
            L, E = M, E2
            if E < best[0]: best = (E, L.copy())
            if E < 1e-9: break
    return best

if __name__ == '__main__':
    n, k, iters, seeds = int(sys.argv[1]), int(sys.argv[2]), int(float(sys.argv[3])), int(sys.argv[4])
    for sd in range(seeds):
        E, L = run(n, k, iters, sd)
        assert is_latin(L)
        print(f'n={n} target rank {k} seed {sd}: residual {E:.4f}', 'EXACT RANK %d' % exact_rank(L) if E < 1e-6 else '', flush=True)
        if E < 1e-6: print(L); break
