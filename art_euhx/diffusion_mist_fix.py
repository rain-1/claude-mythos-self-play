"""Redo the SDE mist pass only: fix the splat clipping bug (unclipped ax at
clipped index caused huge false pos/neg pixels) and substep + clamp the
reverse SDE to avoid rare Euler-Maruyama blow-ups."""
import numpy as np

rng = np.random.default_rng(5)
Wpx, Hpx = 1536, 2048
MU = np.array([0.05, 0.12, 0.27, 0.31, 0.50, 0.63, 0.665, 0.83, 0.95])
WT = np.array([0.10, 0.09, 0.11, 0.10, 0.20, 0.10, 0.09, 0.11, 0.10]); WT /= WT.sum()
SIG0 = 0.0032
S_MAX, S_MIN = 0.62, 0.0040
sig = np.geomspace(S_MAX, S_MIN, Hpx)
X0, X1 = -0.30, 1.30

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

def to_px(x):
    return (x - X0) / (X1 - X0) * Wpx

def init(n):
    i = rng.choice(MU.size, n, p=WT)
    return MU[i] + np.sqrt(S_MAX ** 2 + SIG0 ** 2) * rng.standard_normal(n)

NS = 900000
xs = init(NS)
acc_s = np.zeros((Hpx, Wpx), np.float32)
ks_rows = list(range(0, Hpx, Hpx // 10))
ks_err = []
SUB = 4
CLAMP = (X0 - 0.15, X1 + 0.15)
n_clamped_total = 0
for r in range(Hpx):
    s_hi = sig[r - 1] if r > 0 else S_MAX
    s_lo = sig[r]
    if s_hi > s_lo:
        ss = np.geomspace(s_hi, s_lo, SUB + 1)
        for k in range(SUB):
            a, b = ss[k], ss[k + 1]
            dv = a * a - b * b
            xs = xs + dv * score(xs, a) + np.sqrt(dv) * rng.standard_normal(NS)
    bad = (xs < CLAMP[0]) | (xs > CLAMP[1])
    n_clamped_total += int(bad.sum())
    xs = np.clip(xs, CLAMP[0], CLAMP[1])

    fx = to_px(xs)
    ix0 = np.floor(fx).astype(np.int64)
    ax = (fx - ix0).astype(np.float32)
    ix0c = np.clip(ix0, 0, Wpx - 1)
    ix1c = np.clip(ix0 + 1, 0, Wpx - 1)
    np.add.at(acc_s[r], ix0c, 1 - ax)
    np.add.at(acc_s[r], ix1c, ax)
    if r in ks_rows:
        grid = np.linspace(X0, X1, 6000)
        pdf = rho(grid, s_lo); cdf = np.cumsum(pdf); cdf /= cdf[-1]
        emp = np.searchsorted(np.sort(xs), grid) / NS
        ks_err.append(np.abs(emp - cdf).max())

print("SDE KS errors at checkpoints:", np.round(ks_err, 4))
print("total clamped point-steps (safety net triggers):", n_clamped_total)
print("acc_s stats: min", acc_s.min(), "max", acc_s.max())
np.save("d3_mist.npy", acc_s)
print("saved fixed mist")
