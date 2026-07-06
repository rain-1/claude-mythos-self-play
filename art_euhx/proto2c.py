"""Prototype 2c: Anderson with a disorder GRADIENT (W ramps along x).
Mid-band modes: airy on the weak side, clenched jewels on the strong side."""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
import time

L = 640
rng = np.random.default_rng(11)
wx = np.linspace(1.2, 15.0, L)                    # disorder amplitude vs x (column)
Vgrid = rng.uniform(-0.5, 0.5, (L, L)) * wx[None, :]   # (row y, col x)
V = Vgrid.ravel()

d = sp.diags(V)
e = np.ones(L - 1)
t1 = sp.diags([e, e], [-1, 1], shape=(L, L))
I = sp.identity(L)
H = (d - (sp.kron(I, t1) + sp.kron(t1, I))).tocsc()   # kron(I,t1): x-hop within row

modes = []; energies = []
for sg in [0.0, 0.35, -0.35, 0.7]:
    t0 = time.time()
    vals, vecs = eigsh(H, k=60, sigma=sg, which="LM")
    print("sigma %.2f: %.0fs" % (sg, time.time() - t0), flush=True)
    for i in range(vals.size):
        modes.append((vecs[:, i] ** 2).astype(np.float32)); energies.append(vals[i])
modes = np.array(modes)
np.save("p2c_modes.npy", modes); np.save("p2c_E.npy", np.array(energies))
np.save("p2c_V.npy", Vgrid.astype(np.float32)); np.save("p2c_wx.npy", wx)
print("modes:", len(energies))
