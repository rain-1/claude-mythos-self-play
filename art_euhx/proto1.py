"""Prototype: standard map phase portrait at small res + golden-circle hunt."""
import numpy as np
from PIL import Image
import stdmap_core as sm

rng = np.random.default_rng(7)
S = 768
K = 0.96

# --- classify a spread of seeds ---
N = 4000
x0 = rng.random(N); p0 = rng.random(N)
lam = sm.lyapunov_classify(x0, p0, K, nsteps=800)
print("lyapunov percentiles:", np.percentile(lam, [5, 25, 50, 75, 95]).round(4))
chaotic = lam > 0.05
print("chaotic fraction:", chaotic.mean().round(3))

# --- render layers ---
reg_idx = np.where(~chaotic)[0]
cha_idx = np.where(chaotic)[0][:300]
acc_reg, _, _ = sm.iterate_splat(x0[reg_idx], p0[reg_idx], K, 3000, S)
acc_cha, _, _ = sm.iterate_splat(x0[cha_idx], p0[cha_idx], K, 20000, S)
np.save("proto1_reg.npy", acc_reg); np.save("proto1_cha.npy", acc_cha)

def tone(a, k):
    a = np.log1p(a)
    a = a / np.percentile(a[a > 0], 99.5) if (a > 0).any() else a
    return 1 - np.exp(-k * np.clip(a, 0, 2))

img = np.zeros((S, S, 3), np.float32)
r = tone(acc_reg, 3.0); c = tone(acc_cha, 3.0)
# regular = amber, chaos = indigo haze
img[..., 0] += 1.00 * r + 0.25 * c
img[..., 1] += 0.78 * r + 0.35 * c
img[..., 2] += 0.45 * r + 0.75 * c
Image.fromarray((np.clip(img, 0, 1) ** (1 / 1.9) * 255).astype(np.uint8)[::-1]).save("proto1.png")
print("saved proto1.png")

# --- golden circle hunt: rotation number vs p0 along x0=0.0 ---
GOLD = (np.sqrt(5) - 1) / 2
pgrid = np.linspace(0.55, 0.75, 400)
W = sm.rotation_number(np.zeros_like(pgrid), pgrid, K, nsteps=40000)
i = np.argmin(np.abs(W - GOLD))
print("closest W to golden:", W[i], "at p0=", pgrid[i])
np.save("proto1_W.npy", np.stack([pgrid, W]))
