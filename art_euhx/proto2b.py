"""Prototype 2b: Anderson fireflies at L=512, modes from several energy shifts."""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
from PIL import Image
from scipy.ndimage import gaussian_filter
import time

L = 512
W = 8.0
rng = np.random.default_rng(11)
V = rng.uniform(-W / 2, W / 2, L * L)

def H_of(V, L):
    d = sp.diags(V)
    e = np.ones(L - 1)
    t1 = sp.diags([e, e], [-1, 1], shape=(L, L))
    I = sp.identity(L)
    return (d - (sp.kron(I, t1) + sp.kron(t1, I))).tocsc()

H = H_of(V, L)
sigmas = [-4.0, -2.0, 0.0, 2.0, 4.0]
modes = []; energies = []
for sg in sigmas:
    t0 = time.time()
    vals, vecs = eigsh(H, k=24, sigma=sg, which="LM")
    print("sigma %.1f: %.1fs, E=[%.2f,%.2f]" % (sg, time.time() - t0, vals.min(), vals.max()))
    for i in range(vals.size):
        modes.append(vecs[:, i] ** 2); energies.append(vals[i])
modes = np.array(modes); energies = np.array(energies)
np.save("p2_modes.npy", modes.astype(np.float32)); np.save("p2_E.npy", energies)
np.save("p2_V.npy", V.astype(np.float32))
print("total modes", len(energies))
