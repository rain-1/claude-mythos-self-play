"""Final Anderson piece at L=2048: disorder gradient W(x) from clean to violent,
mid-band eigenmodes at several energies -> the mobility-edge crossing rendered
as a field of fireflies going from wide nebulae (weak disorder) to tight sparks
(strong disorder)."""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
import time

L = 2048
rng = np.random.default_rng(11)
wx = np.linspace(1.0, 16.0, L)                      # disorder amplitude ramps with column x
Vgrid = rng.uniform(-0.5, 0.5, (L, L)) * wx[None, :]
V = Vgrid.ravel().astype(np.float64)

d = sp.diags(V)
e = np.ones(L - 1)
t1 = sp.diags([e, e], [-1, 1], shape=(L, L))
I = sp.identity(L)
H = (d - (sp.kron(I, t1) + sp.kron(t1, I))).tocsc()
print("H built, nnz=%d" % H.nnz, flush=True)

sigmas = [-6.0, -3.0, -1.0, 0.0, 1.0, 3.0, 6.0]
K_PER = 48
modes = []; energies = []
for sg in sigmas:
    t0 = time.time()
    vals, vecs = eigsh(H, k=K_PER, sigma=sg, which="LM")
    dt = time.time() - t0
    print("sigma=%.1f done in %.0fs  E=[%.3f,%.3f]" % (sg, dt, vals.min(), vals.max()), flush=True)
    for i in range(vals.size):
        modes.append((vecs[:, i] ** 2).astype(np.float32))
        energies.append(vals[i])

modes = np.array(modes); energies = np.array(energies)
np.save("anderson_modes.npy", modes)
np.save("anderson_E.npy", energies)
np.save("anderson_V.npy", Vgrid.astype(np.float32))
np.save("anderson_wx.npy", wx)
print("TOTAL MODES", len(energies), flush=True)
print("DONE")
