"""Prototype: 2-D Anderson localization. Tight-binding H = -sum hop + V, V~U[-W/2,W/2].
Mid-band eigenmodes via shift-invert eigsh -> exponentially localized fireflies."""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
from PIL import Image
import time

L = 256
W = 8.0
rng = np.random.default_rng(11)
V = rng.uniform(-W / 2, W / 2, L * L)

def H_of(V, L):
    d = sp.diags(V)
    e = np.ones(L)
    t1 = sp.diags([e[:-1], e[:-1]], [-1, 1], shape=(L, L))
    I = sp.identity(L)
    hop = sp.kron(I, t1) + sp.kron(t1, I)
    return (d - hop).tocsc()

H = H_of(V, L)
t0 = time.time()
k = 36
vals, vecs = eigsh(H, k=k, sigma=0.0, which="LM")
print("eigsh %d modes at L=%d in %.1fs; E in [%.3f, %.3f]" % (k, L, time.time() - t0, vals.min(), vals.max()))

# stats: IPR and localization length
psi2 = vecs ** 2
ipr = (psi2 ** 2).sum(axis=0)
print("participation ratio (1/IPR) sites:", np.round(1 / ipr[:8], 1), "... of", L * L)

# localization length: fit log|psi| vs r from mode center
X, Y = np.meshgrid(np.arange(L), np.arange(L))
xis = []
for i in range(k):
    m = psi2[:, i].reshape(L, L)
    cy, cx = np.unravel_index(np.argmax(m), m.shape)
    r = np.hypot(X - cx, Y - cy).ravel()
    lg = 0.5 * np.log(m.ravel() + 1e-300)
    sel = (r > 2) & (r < L / 3) & (lg > -300)
    A = np.polyfit(r[sel], lg[sel], 1)
    xis.append(-1 / A[0])
xis = np.array(xis)
print("localization length xi: median %.1f  range [%.1f, %.1f]" % (np.median(xis), xis.min(), xis.max()))

# render: sum modes with hue by energy
img = np.zeros((L, L, 3))
Emin, Emax = vals.min(), vals.max()
for i in range(k):
    m = psi2[:, i].reshape(L, L)
    m = m / m.max()
    lg = np.clip((np.log10(m + 1e-12) + 6) / 6, 0, 1)   # 6 decades of skirt
    t = (vals[i] - Emin) / (Emax - Emin + 1e-9)
    col = np.array([0.35 + 0.6 * t, 0.45 + 0.25 * np.sin(np.pi * t), 0.95 - 0.55 * t])
    img += lg[..., None] ** 2.2 * col
img = 1 - np.exp(-1.6 * img)
img = np.clip(img, 0, 1) ** (1 / 1.8)
Image.fromarray((img * 255).astype(np.uint8)).resize((768, 768), Image.NEAREST).save("proto2.png")
print("saved proto2.png")
