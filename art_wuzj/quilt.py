"""quilt.py — the explicit bijection Z^2 -> Z with every 2x2 window summing to 0 (MO 515677, answer by balanced ternary).
x_i: i-th positive integer whose balanced-ternary digits vanish at odd positions; x_{-i} = -x_i; y_j = 3 x_j.
phi(i, j) = (-1)^j x_i + (-1)^i y_j."""
import numpy as np
from itertools import product

def bt(v):
    d = []
    while v:
        r = v % 3
        if r == 2: r = -1
        d.append(r); v = (v - r) // 3
    return d

def evens(N):
    out = []
    v = 1
    while len(out) < N:
        d = bt(v)
        if all(d[k] == 0 for k in range(1, len(d), 2)):
            out.append(v)
        v += 1
    return out

def phi_grid(K):
    xs = evens(K + 1)
    x = lambda i: 0 if i == 0 else (xs[i - 1] if i > 0 else -xs[-i - 1])
    I = np.arange(-K, K + 1)
    P = np.array([[(-1) ** (j % 2) * x(i) + (-1) ** (i % 2) * 3 * x(j) for i in I] for j in I])   # rows = j
    return I, P

if __name__ == '__main__':
    I, P = phi_grid(12)
    print(P[10:15, 10:15])
    W = P[:-1, :-1] + P[1:, :-1] + P[:-1, 1:] + P[1:, 1:]
    print('all windows zero:', np.all(W == 0), 'distinct:', len(set(P.ravel())) == P.size, 'max', np.abs(P).max())
    s = set(P.ravel().tolist()); m = 0
    while m in s and -m in s: m += 1
    print('contains all |v| <', m)
