"""post_layout.py — anneal a mirror-symmetric drawing of Post's lattice.
Variables: (x, y) per dual pair (mirrored), (x, y) per self-dual clone. Constraints: y(child) < y(parent) - gap.
Energy: crossings + beads touching foreign threads + node crowding + edge length + slant."""
import json, numpy as np, functools, sys
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
d = json.load(open('post_lattice.json'))
names = d['names']; cover = [tuple(e) for e in d['cover']]
def dual(nm):
    tr = {'R0': 'R1', 'R1': 'R0', 'M0': 'M1', 'M1': 'M0', 'L0': 'L1', 'L1': 'L0', 'V': 'E', 'E': 'V',
          'V0': 'E1', 'E1': 'V0', 'V1': 'E0', 'E0': 'V1', 'V2': 'E2', 'E2': 'V2', 'I0': 'I1', 'I1': 'I0'}
    if nm in tr: return tr[nm]
    if nm.startswith('S0'): return 'S1' + nm[2:]
    if nm.startswith('S1'): return 'S0' + nm[2:]
    return nm
idx = {k: i for i, k in enumerate(names)}
n = len(names)
down = {k: [a for a, b in cover if b == k] for k in names}
@functools.lru_cache(None)
def rk(k): return 0 if not down[k] else 1 + max(rk(a) for a in down[k])
E = np.array([(idx[a], idx[b]) for a, b in cover])
# initial
X = np.zeros(n); Y = np.array([float(rk(k)) for k in names])
for k in names:
    i = idx[k]
    if k.startswith('S1'): X[i] = -6 - 0.5 * ('^2' in k) + (0.8 if k[2:3] in '012' else 0)
    elif k.startswith('S0'): X[i] = -X[idx[dual(k)]] if dual(k) in idx and X[idx[dual(k)]] else 6
selfd = [idx[k] for k in names if dual(k) == k]
pairs = [(idx[k], idx[dual(k)]) for k in names if dual(k) != k and idx[k] < idx[dual(k)]]
for a, b in pairs:
    if X[a] == 0 and X[b] == 0: X[a] = -2.5 + rng.normal() * 0.5
    X[b] = -X[a]
for i in selfd: X[i] = rng.normal() * 0.3
X[idx['BF']] = 0
Y[idx['BF']] = 9.0

def segs_cross(p1, p2, p3, p4):
    d1 = np.cross(p2 - p1, p3 - p1); d2 = np.cross(p2 - p1, p4 - p1)
    d3 = np.cross(p4 - p3, p1 - p3); d4 = np.cross(p4 - p3, p2 - p3)
    return (d1 * d2 < 0) & (d3 * d4 < 0)

EA, EB = E[:, 0], E[:, 1]
share = (EA[:, None] == EA[None]) | (EA[:, None] == EB[None]) | (EB[:, None] == EA[None]) | (EB[:, None] == EB[None])
def energy(X, Y):
    p = np.stack([X, Y], 1)
    A, B = p[EA], p[EB]
    # crossings (all pairs)
    P1, P2 = A[:, None], B[:, None]; P3, P4 = A[None], B[None]
    def cr(u, v, w): return (v[..., 0] - u[..., 0]) * (w[..., 1] - u[..., 1]) - (v[..., 1] - u[..., 1]) * (w[..., 0] - u[..., 0])
    d1 = cr(P1, P2, P3); d2 = cr(P1, P2, P4); d3 = cr(P3, P4, P1); d4 = cr(P3, P4, P2)
    X_ = (d1 * d2 < 0) & (d3 * d4 < 0) & ~share
    ncross = X_.sum() / 2
    # bead near a foreign segment
    AB = B - A; L2 = (AB ** 2).sum(1) + 1e-9
    t = np.clip(((p[:, None] - A[None]) * AB[None]).sum(2) / L2[None], 0, 1)
    proj = A[None] + t[..., None] * AB[None]
    dist = np.sqrt(((p[:, None] - proj) ** 2).sum(2))
    foreign = (np.arange(n)[:, None] != EA[None]) & (np.arange(n)[:, None] != EB[None])
    near = (np.clip(0.45 - dist, 0, None) * foreign).sum()
    # crowding
    dd = np.sqrt(((p[:, None] - p[None]) ** 2).sum(2)) + np.eye(n) * 9
    crowd = np.clip(0.9 - dd, 0, None).sum() / 2
    # lengths & slant
    leng = (AB[:, 0] ** 2).sum() * 0.05 + ((AB[:, 1] - 1.0) ** 2).sum() * 0.05
    return 4.0 * ncross + 60 * near + 60 * crowd + leng + 0.02 * (X ** 2).sum(), ncross

def feasible(Y):
    return np.all(Y[EB] - Y[EA] >= 0.55)

cur = energy(X, Y)[0]; best = (cur, X.copy(), Y.copy())
T = 3.0
steps = int(sys.argv[2]) if len(sys.argv) > 2 else 40000
for it in range(steps):
    T = 3.0 * (0.002 / 3.0) ** (it / steps)
    X2, Y2 = X.copy(), Y.copy()
    k = rng.integers(n)
    if names[k] == 'BF': continue
    j = idx[dual(names[k])]
    if rng.random() < 0.6:
        dx = rng.normal() * 0.8
        if j == k: X2[k] += dx
        else: X2[k] += dx; X2[j] = -X2[k]
    else:
        dy = rng.normal() * 0.3
        Y2[k] += dy; Y2[j] = Y2[k]
        if not feasible(Y2): continue
    e = energy(X2, Y2)[0]
    if e < cur or rng.random() < np.exp((cur - e) / T):
        X, Y, cur = X2, Y2, e
        if e < best[0]: best = (e, X.copy(), Y.copy())
e, X, Y = best
print('best energy', e, 'crossings', energy(X, Y)[1])
json.dump({k: [float(X[idx[k]]), float(Y[idx[k]])] for k in names}, open(f'post_layout_{sys.argv[1] if len(sys.argv) > 1 else 0}.json', 'w'))
