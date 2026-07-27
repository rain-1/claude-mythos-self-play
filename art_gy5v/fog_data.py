"""Fog rows + smooth density (split from tree_data.py; tree_edges.npz already saved... check)."""
import numpy as np, os
from math import lcm

L = lcm(*range(1, 29))
NT = 22
XMAX = 4.0

# rebuild final tree level (cheap) to seed fog
pos = np.array([0], dtype=np.int64); mass = np.array([1.0])
for n in range(1, NT+1):
    w = L // n
    child = np.concatenate([pos - w, pos + w])
    cmass = np.concatenate([mass, mass]) * 0.5
    uniq, inv = np.unique(child, return_inverse=True)
    um = np.zeros(len(uniq)); np.add.at(um, inv, cmass)
    pos, mass = uniq, um

NG = 1 << 22
dx = 2*XMAX/NG
f = np.zeros(NG, dtype=np.float64)
idx = np.clip(np.round((pos.astype(np.float64)/L + XMAX)/dx).astype(np.int64), 0, NG-1)
np.add.at(f, idx, mass)

def shift_lin(f, s):
    sh = s/dx
    i0 = int(np.floor(sh)); fr = sh - i0
    g = np.zeros_like(f)
    src = np.roll(f, i0)  # wrap negligible: mass near edges ~0
    src2 = np.roll(f, i0+1)
    g = src*(1-fr) + src2*fr
    return g

NF = 3000
save_ns = set(np.unique(np.round(np.geomspace(NT+1, NF, 640)).astype(int)).tolist())
rows, row_ns = [], []
DS = 2048
for n in range(NT+1, NF+1):
    s = 1.0/n
    f = 0.5*(shift_lin(f, s) + shift_lin(f, -s))
    if n in save_ns:
        rows.append(f.reshape(DS, -1).sum(axis=1).astype(np.float32))
        row_ns.append(n)
rows = np.array(rows)
np.savez_compressed('fog_rows.npz', rows=rows, ns=np.array(row_ns), xmax=XMAX)
print("fog rows", rows.shape, "mass", float(f.sum()))

# smooth density curve
T = 60.0; dt = 0.002
t = np.arange(dt, T, dt)
NP = 4000
logabs = np.zeros_like(t); sgn = np.ones_like(t)
for n in range(1, NP+1):
    c = np.cos(t/n)
    logabs += np.log(np.abs(c) + 1e-300)
    sgn *= np.sign(c)
tail_n = np.arange(NP+1, 300000, dtype=np.float64)
z2 = float((1.0/tail_n**2).sum()); z4 = float((1.0/tail_n**4).sum())
logabs += -t**2/2*z2 - t**4/12*z4
phi = sgn*np.exp(logabs)
xs = np.linspace(-4, 4, 8001)
rho = np.zeros_like(xs)
for i in range(0, len(xs), 100):
    xx = xs[i:i+100][:, None]
    rho[i:i+100] = (np.cos(xx*t[None, :]) @ phi)*dt/np.pi + 1.0/(2*np.pi)*dt  # t=0 term: phi(0)=1, cos=1, half-weight? use trapezoid corr
np.save('rho_curve.npy', np.stack([xs, rho]))
i0 = 4000; i1 = 6000; i2 = 5000
print("rho(0)=", rho[i0], "rho(2)=", rho[i1], "rho(1)=", rho[i2], "max", rho.max())
