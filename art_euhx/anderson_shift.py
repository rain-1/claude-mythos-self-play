"""Compute eigenmodes for ONE sigma shift, save to disk, exit (fresh process
per shift guarantees the sparse-LU factorization memory is fully released
before the next shift - the L=2048 attempt OOM'd at 15GB doing this in-process)."""
import sys
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
import time

L = 1400
sigma = float(sys.argv[1])
idx = int(sys.argv[2])
K_PER = 48

rng = np.random.default_rng(11)
wx = np.linspace(1.0, 16.0, L)
Vgrid = rng.uniform(-0.5, 0.5, (L, L)) * wx[None, :]
V = Vgrid.ravel().astype(np.float64)

d = sp.diags(V)
e = np.ones(L - 1)
t1 = sp.diags([e, e], [-1, 1], shape=(L, L))
I = sp.identity(L)
H = (d - (sp.kron(I, t1) + sp.kron(t1, I))).tocsc()

t0 = time.time()
vals, vecs = eigsh(H, k=K_PER, sigma=sigma, which="LM")
print("shift %d (sigma=%.2f) done in %.0fs  E=[%.3f,%.3f]" % (idx, sigma, time.time() - t0, vals.min(), vals.max()), flush=True)

np.save("ashift_modes_%d.npy" % idx, (vecs ** 2).astype(np.float32))
np.save("ashift_E_%d.npy" % idx, vals)
if idx == 0:
    np.save("anderson_V.npy", Vgrid.astype(np.float32))
    np.save("anderson_wx.npy", wx)
