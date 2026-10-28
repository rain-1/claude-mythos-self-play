"""Independent check (written separately from gs.py): LP lower bound over shift-consistent
4x4-window measures for the period-21 examples.  python3 verify_lp44.py"""
import json, numpy as np, scipy.sparse as sp
from scipy.optimize import linprog
d = json.load(open('ground_states.json'))
m = n = 4
N = 1 << (m * n)
bits = ((np.arange(N)[:, None] >> np.arange(m * n)) & 1).reshape(N, m, n)   # [pattern, row, col]
def code(arr):  # arr (N, r, c) -> int code
    r, c = arr.shape[1:]
    return (arr.reshape(N, -1) << np.arange(r * c)).sum(1)
L = code(bits[:, :, :n - 1]); R = code(bits[:, :, 1:])
T = code(bits[:, :m - 1, :]); B = code(bits[:, 1:, :])
nL = 1 << (m * (n - 1)); nT = 1 << ((m - 1) * n)
rows = []
A1 = sp.coo_matrix((np.ones(N), (L, np.arange(N))), shape=(nL, N)) - sp.coo_matrix((np.ones(N), (R, np.arange(N))), shape=(nL, N))
A2 = sp.coo_matrix((np.ones(N), (T, np.arange(N))), shape=(nT, N)) - sp.coo_matrix((np.ones(N), (B, np.arange(N))), shape=(nT, N))
A = sp.vstack([A1, A2, sp.coo_matrix(np.ones((1, N)))]).tocsr()
b = np.r_[np.zeros(nL + nT), 1.0]
for e in d['examples'][:2]:
    J = np.array(e['J'])
    hard = e['family'].startswith('face')
    cost = np.zeros(N)
    for i in range(m - 1):
        for j in range(n - 1):
            t = bits[:, i, j] + 2 * bits[:, i, j + 1] + 4 * bits[:, i + 1, j] + 8 * bits[:, i + 1, j + 1]
            cost += J[t]
    cost /= (m - 1) * (n - 1)
    ub = [(0, 0) if (hard and c > 5) else (0, None) for c in cost] if hard else (0, None)
    if hard:   # forbid any pattern containing a forbidden tile
        forb = np.zeros(N, bool)
        for i in range(m - 1):
            for j in range(n - 1):
                t = bits[:, i, j] + 2 * bits[:, i, j + 1] + 4 * bits[:, i + 1, j] + 8 * bits[:, i + 1, j + 1]
                forb |= J[t] >= 10
        ub = [(0, 0) if f else (0, None) for f in forb]
    res = linprog(cost, A_eq=A, b_eq=b, bounds=ub, method='highs')
    print(e['family'], 'LP44 =', repr(res.fun), ' periodic e =', repr(e['energy_per_site']), ' gap =', e['energy_per_site'] - res.fun)
