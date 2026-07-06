"""Final 'Two Ways Home' piece. Reverse diffusion of a 9-point multi-scale
constellation: forks happen at several sigma levels (a family tree of splits),
not just one. Probability-flow ODE (gold threads) vs reverse SDE (cool mist),
both exact from the same closed-form Gaussian-mixture score. High-res portrait.
"""
import numpy as np
from PIL import Image

rng = np.random.default_rng(5)
Wpx, Hpx = 1536, 2048

# 9-point constellation: multi-scale nested pairs -> forks at different heights
MU = np.array([0.05, 0.12, 0.27, 0.31, 0.50, 0.63, 0.665, 0.83, 0.95])
WT = np.array([0.10, 0.09, 0.11, 0.10, 0.20, 0.10, 0.09, 0.11, 0.10]); WT /= WT.sum()
SIG0 = 0.0032
S_MAX, S_MIN = 0.62, 0.0040
sig = np.geomspace(S_MAX, S_MIN, Hpx)

def score(x, s):
    v = s * s + SIG0 * SIG0
    d = x[:, None] - MU[None, :]
    g = WT[None, :] * np.exp(-0.5 * d * d / v) / np.sqrt(v)
    num = (g * (-d / v)).sum(1); den = g.sum(1)
    return num / np.maximum(den, 1e-300)

def rho(x, s):
    v = s * s + SIG0 * SIG0
    d = x[:, None] - MU[None, :]
    return (WT[None, :] * np.exp(-0.5 * d * d / v) / np.sqrt(2 * np.pi * v)).sum(1)

X0, X1 = -0.30, 1.30
def to_px(x):
    return (x - X0) / (X1 - X0) * Wpx

def init(n):
    i = rng.choice(MU.size, n, p=WT)
    return MU[i] + np.sqrt(S_MAX ** 2 + SIG0 ** 2) * rng.standard_normal(n)

# --- ODE threads (probability-flow, RK2/midpoint in log-sigma substeps) ---
NT = 5200
xt = init(NT)
order0 = np.argsort(xt)
acc_t = np.zeros((Hpx, Wpx), np.float32)
SUB = 7
for r in range(Hpx):
    s_hi = sig[r - 1] if r > 0 else S_MAX
    s_lo = sig[r]
    ss = np.geomspace(s_hi, s_lo, SUB + 1)
    for k in range(SUB):
        a, b = ss[k], ss[k + 1]
        dv = a * a - b * b
        k1 = score(xt, a)
        xmid = xt + 0.25 * dv * k1
        k2 = score(xmid, np.sqrt(0.5 * (a * a + b * b)))
        xt = xt + 0.5 * dv * k2
    fx = to_px(xt)
    ix = np.clip(fx.astype(np.int64), 0, Wpx - 2)
    ax = (fx - ix).astype(np.float32)
    np.add.at(acc_t[r], ix, 1 - ax); np.add.at(acc_t[r], ix + 1, ax)
order1 = np.argsort(xt)
print("thread order preserved (non-crossing):", np.array_equal(order0, order1))

# --- SDE mist (Euler-Maruyama in sigma^2, exact-in-law reverse diffusion) ---
NS = 900000
xs = init(NS)
acc_s = np.zeros((Hpx, Wpx), np.float32)
ks_rows = list(range(0, Hpx, Hpx // 10))
ks_err = []
for r in range(Hpx):
    s_hi = sig[r - 1] if r > 0 else S_MAX
    s_lo = sig[r]
    dv = s_hi * s_hi - s_lo * s_lo
    xs = xs + dv * score(xs, s_hi) + np.sqrt(dv) * rng.standard_normal(NS)
    fx = to_px(xs)
    ix = np.clip(fx.astype(np.int64), 0, Wpx - 2)
    ax = (fx - ix).astype(np.float32)
    np.add.at(acc_s[r], ix, 1 - ax); np.add.at(acc_s[r], ix + 1, ax)
    if r in ks_rows:
        grid = np.linspace(X0, X1, 6000)
        pdf = rho(grid, s_lo); cdf = np.cumsum(pdf); cdf /= cdf[-1]
        emp = np.searchsorted(np.sort(xs), grid) / NS
        ks_err.append(np.abs(emp - cdf).max())
print("SDE KS errors at 10 checkpoints:", np.round(ks_err, 4))

np.save("d3_threads.npy", acc_t)
np.save("d3_mist.npy", acc_s)
print("saved arrays")
