"""Exact binary tree of partial sums of +-1/k, collision-merged, + measure fog + density.

Positions exact as int64 multiples of 1/L, L = lcm(1..28).
Saves: per level n<=NT: arrays of (parent_pos, child_pos, mass) edges; fog rows for n up to NF.
"""
import numpy as np
from math import lcm

L = lcm(*range(1, 29))          # 80313433200
NT = 22                          # exact tree depth
XMAX = 4.0

# ---- exact tree with collision merging ----
levels = []   # list of (positions int64 array, mass float array)
pos = np.array([0], dtype=np.int64); mass = np.array([1.0])
edges = []    # per level: (px, cx, m) in float units
for n in range(1, NT+1):
    w = L // n
    child = np.concatenate([pos - w, pos + w])
    cmass = np.concatenate([mass, mass]) * 0.5
    par   = np.concatenate([pos, pos])
    # merge collisions among children
    order = np.argsort(child, kind='stable')
    child, cmass, par = child[order], cmass[order], par[order]
    uniq, inv = np.unique(child, return_inverse=True)
    um = np.zeros(len(uniq)); np.add.at(um, inv, cmass)
    edges.append((par.astype(np.float64)/L, child.astype(np.float64)/L,
                  cmass, n))
    ncol = len(child) - len(uniq)
    if n >= 10:
        print("level", n, "children", len(child), "distinct", len(uniq), "collisions", ncol)
    pos, mass = uniq, um
np.savez_compressed('tree_edges.npz',
    **{f'par{n}': e[0] for e in edges for n in [e[3]]},
    **{f'chi{n}': e[1] for e in edges for n in [e[3]]},
    **{f'mas{n}': e[2] for e in edges for n in [e[3]]})

# ---- fog: measure on fine grid from level NT+1 to NF ----
NG = 1 << 22
xg = np.linspace(-XMAX, XMAX, NG, endpoint=False)
dx = xg[1] - xg[0]
f = np.zeros(NG)
idx = np.clip(((pos.astype(np.float64)/L + XMAX)/dx).astype(np.int64), 0, NG-1)
np.add.at(f, idx, mass)

def shift_lin(f, s):
    """f shifted by s (units), linear interp."""
    sh = s / dx
    i0 = int(np.floor(sh)); fr = sh - i0
    g = np.zeros_like(f)
    if i0 >= 0:
        g[i0:] = f[:NG-i0] * (1-fr)
        if i0+1 < NG: g[i0+1:] += f[:NG-i0-1] * fr
    else:
        g[:i0] = f[-i0:] * (1-fr)
        g[:i0-1] += f[-i0+1:] * fr if i0-1 < 0 else 0
    return g

NF = 3000
save_ns = np.unique(np.round(np.geomspace(NT+1, NF, 620)).astype(int))
rows = []
row_ns = []
DS = 1 << 11   # downsample fog rows to 2048 for storage of the weather band
for n in range(NT+1, NF+1):
    s = 1.0/n
    f = 0.5*(shift_lin(f, s) + shift_lin(f, -s))
    if n in set(save_ns.tolist()):
        rows.append(f.reshape(DS, -1).sum(axis=1))
        row_ns.append(n)
rows = np.array(rows)
np.savez_compressed('fog_rows.npz', rows=rows, ns=np.array(row_ns), xmax=XMAX)
print("fog rows", rows.shape)

# ---- final density (smooth) via char.fn FFT for the bottom shore + shelf detail ----
T = 60.0; dt = 0.002
t = np.arange(0, T, dt)
n_arr = np.arange(1, 200001)
logabs = np.zeros_like(t); sgn = np.ones_like(t)
# product over n: do in chunks by n for exact small n, tail via series
NP = 4000
for n in range(1, NP+1):
    c = np.cos(t/n)
    logabs += np.log(np.abs(c) + 1e-300)
    sgn *= np.sign(c)
# tail n>NP: -t^2/2 * sum_{n>NP} 1/n^2 approx zeta tail
z2 = float(np.sum(1.0/np.arange(NP+1, 400000, dtype=np.float64)**2)) + 1.0/399999
z4 = float(np.sum(1.0/np.arange(NP+1, 400000, dtype=np.float64)**4))
logabs += -t**2/2*z2 - t**4/12*z4
phi = sgn * np.exp(logabs)
xs = np.linspace(-4, 4, 4001)
# rho(x) = (1/pi) * int cos(xt) phi(t) dt  -- direct matrix (4001 x 30000) chunked
rho = np.zeros_like(xs)
for i in range(0, len(xs), 200):
    xx = xs[i:i+200][:, None]
    rho[i:i+200] = (np.cos(xx*t[None, :]) @ phi) * dt / np.pi
np.save('rho_curve.npy', np.stack([xs, rho]))
print("rho(0)=", rho[2000], "rho(2)=", rho[3000], "rho(1)=", rho[2500])
print("max rho", rho.max())
