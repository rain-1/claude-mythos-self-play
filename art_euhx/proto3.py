"""Prototype 3: 'Two Ways Home' — reverse diffusion, flow vs SDE.
Canvas: x horizontal, noise level sigma vertical (log ladder, sigma_max top).
Gold threads = probability-flow ODE; blue mist = reverse SDE. Same marginals.
Score is EXACT (closed-form Gaussian mixture)."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

rng = np.random.default_rng(5)
Wpx, Hpx = 768, 1024
# constellation: 6 points, one close pair (late fork)
MU = np.array([0.10, 0.30, 0.47, 0.52, 0.72, 0.90])
WT = np.array([0.16, 0.12, 0.16, 0.14, 0.28, 0.14]); WT /= WT.sum()
SIG0 = 0.0045
S_MAX, S_MIN = 0.55, 0.0055
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

X0, X1 = -0.35, 1.35
def to_px(x):
    return (x - X0) / (X1 - X0) * Wpx

# initial samples ~ rho_{sigma_max}
def init(n):
    i = rng.choice(MU.size, n, p=WT)
    return MU[i] + np.sqrt(S_MAX ** 2 + SIG0 ** 2) * rng.standard_normal(n)

# --- ODE threads ---
NT = 2600
xt = init(NT)
order0 = np.argsort(xt)
acc_t = np.zeros((Hpx, Wpx), np.float32)
SUB = 6
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
inv = np.sum(np.argsort(np.argsort(xt)) != np.argsort(np.argsort(init(0) if False else xt)))
# non-crossing check: order preserved?
order1 = np.argsort(xt)
print("thread order preserved:", np.array_equal(order0, order1))

# --- SDE mist ---
NS = 150000
xs = init(NS)
acc_s = np.zeros((Hpx, Wpx), np.float32)
ks_rows = [0, Hpx // 4, Hpx // 2, 3 * Hpx // 4, Hpx - 1]
ks_err_flow, ks_err_sde = [], []
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
        # KS vs closed form on a grid
        grid = np.linspace(X0, X1, 4000)
        pdf = rho(grid, s_lo); cdf = np.cumsum(pdf); cdf /= cdf[-1]
        emp = np.searchsorted(np.sort(xs), grid) / NS
        ks_err_sde.append(np.abs(emp - cdf).max())
print("SDE KS errors at checkpoints:", np.round(ks_err_sde, 4))

np.save("p3_threads.npy", acc_t); np.save("p3_mist.npy", acc_s)

# --- quick composite ---
t = acc_t / np.percentile(acc_t[acc_t > 0], 99)
t = 1 - np.exp(-2.2 * t)
m = np.log1p(acc_s); m /= np.percentile(m[m > 0], 99.5)
m = 1 - np.exp(-2.0 * np.clip(m - 0.12, 0, None))
img = np.zeros((Hpx, Wpx, 3))
img[..., 0] += 0.10 * m; img[..., 1] += 0.16 * m; img[..., 2] += 0.34 * m
img[..., 0] += 1.15 * t; img[..., 1] += 0.82 * t; img[..., 2] += 0.38 * t
img = 1 - np.exp(-img)
img = np.clip(img, 0, 1) ** (1 / 1.75)
Image.fromarray((img * 255).astype(np.uint8)).save("proto3.png")
print("saved proto3.png")
