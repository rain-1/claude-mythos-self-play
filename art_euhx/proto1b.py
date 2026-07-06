"""Prototype 1b: dark-field standard map. Threads = equal-mass regular orbits,
mist = chaotic occupation, gold = the golden KAM circle."""
import numpy as np
from PIL import Image
import stdmap_core as sm

rng = np.random.default_rng(7)
S = 900
K = 0.96
GOLD_W = (np.sqrt(5) - 1) / 2

# --- seeds: stratified grid, classified ---
n_side = 90
gx, gp = np.meshgrid(np.linspace(0, 1, n_side, endpoint=False) + 0.5 / n_side,
                     np.linspace(0, 1, n_side, endpoint=False) + 0.5 / n_side)
x0 = gx.ravel() + rng.normal(0, 0.002, n_side**2)
p0 = gp.ravel() + rng.normal(0, 0.002, n_side**2)
lam = sm.lyapunov_classify(x0, p0, K, nsteps=800)
chaotic = lam > 0.05

# --- regular threads: subsample to ~700 seeds, equal mass per orbit ---
reg = np.where(~chaotic)[0]
reg = rng.choice(reg, size=min(700, reg.size), replace=False)
T_reg = 4000
acc_reg, _, _ = sm.iterate_splat(x0[reg], p0[reg], K, T_reg, S, weight=1.0 / T_reg)

# rotation numbers for the regular seeds (for hue)
W_reg = sm.rotation_number(x0[reg], p0[reg], K, nsteps=8000)

# hue-weighted splat: deposit W value too (mean-W per pixel via 2 buffers)
acc_regW = np.zeros((S, S), np.float32)
xx = x0[reg].copy(); pp = p0[reg].copy()
x = xx.copy(); p = pp.copy()
Wc = W_reg.astype(np.float32)
flatW = acc_regW.ravel()
for _ in range(T_reg):
    x, p = sm.step(x, p, K)
    pv = p % 1.0
    fx = x * S; fy = pv * S
    ix = np.floor(fx).astype(np.int64); iy = np.floor(fy).astype(np.int64)
    ax = (fx - ix).astype(np.float32); ay = (fy - iy).astype(np.float32)
    ix0 = ix % S; iy0 = iy % S; ix1 = (ix + 1) % S; iy1 = (iy + 1) % S
    w = np.float32(1.0 / T_reg)
    np.add.at(flatW, iy0 * S + ix0, w * (1 - ax) * (1 - ay) * Wc)
    np.add.at(flatW, iy0 * S + ix1, w * ax * (1 - ay) * Wc)
    np.add.at(flatW, iy1 * S + ix0, w * (1 - ax) * ay * Wc)
    np.add.at(flatW, iy1 * S + ix1, w * ax * ay * Wc)

# --- chaotic mist: few long orbits ---
cha = np.where(chaotic)[0]
cha = rng.choice(cha, size=min(400, cha.size), replace=False)
T_cha = 30000
acc_cha, _, _ = sm.iterate_splat(x0[cha], p0[cha], K, T_cha, S, weight=1.0)

# --- the golden circle: bisect W(p0)=GOLD_W on x0=0 ---
def Wof(p):
    return sm.rotation_number(np.array([0.0]), np.array([p]), K, nsteps=200000)[0]
lo, hi = 0.60, 0.72
for _ in range(40):
    mid = 0.5 * (lo + hi)
    if Wof(mid) < GOLD_W: lo = mid
    else: hi = mid
p_gold = 0.5 * (lo + hi)
print("golden circle p0 =", p_gold, " W =", Wof(p_gold), " target", GOLD_W)
acc_gold, xg, pg = sm.iterate_splat(np.array([0.0]), np.array([p_gold]), K, 400000, S, weight=1.0)
print("gold orbit p-band:", (pg % 1).min(), (pg % 1).max())

np.save("p1_reg.npy", acc_reg); np.save("p1_regW.npy", acc_regW)
np.save("p1_cha.npy", acc_cha); np.save("p1_gold.npy", acc_gold)
print("chaotic fraction:", chaotic.mean())
