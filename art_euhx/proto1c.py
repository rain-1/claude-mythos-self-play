"""Prototype 1c: two-seas standard map at 900^2, K=0.969.
Layers: inner sea, outer sea, regular threads, golden pair."""
import numpy as np
import stdmap_core as sm

rng = np.random.default_rng(7)
S = 900
K = 0.969
GOLD = (np.sqrt(5) - 1) / 2

def find_circle(Wtarget, lo, hi, x0=0.0, n=200000):
    def Wof(p):
        return sm.rotation_number(np.array([x0]), np.array([p]), K, nsteps=n)[0]
    for _ in range(44):
        mid = 0.5 * (lo + hi)
        if Wof(mid) < Wtarget: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)

p_gold = find_circle(GOLD, 0.60, 0.72)
p_mirr = find_circle(1 - GOLD, 0.28, 0.40)
print("golden p0=%.9f  mirror p0=%.9f" % (p_gold, p_mirr))

# seas: seed + classify
def chaotic_seeds(pcenter, spread, n):
    x = rng.random(n); p = (pcenter + rng.normal(0, spread, n))
    lam = sm.lyapunov_classify(x, p, K, nsteps=1500)
    return x[lam > 0.05], p[lam > 0.05]

xi, pi = chaotic_seeds(0.5, 0.02, 300)     # inner sea
xo, po = chaotic_seeds(0.0, 0.03, 300)     # outer sea
print("inner seeds %d outer seeds %d" % (len(xi), len(pi)))

acc_in, _, _ = sm.iterate_splat(xi, pi, K, 60000 * 300 // max(len(xi),1) // 300 * 300 if False else 60000, S)
acc_out, _, _ = sm.iterate_splat(xo, po, K, 60000, S)

# regular threads
n_side = 90
gx, gp = np.meshgrid(np.linspace(0, 1, n_side, endpoint=False) + 0.5 / n_side,
                     np.linspace(0, 1, n_side, endpoint=False) + 0.5 / n_side)
x0 = gx.ravel() + rng.normal(0, 0.002, n_side**2)
p0 = gp.ravel() + rng.normal(0, 0.002, n_side**2)
lam = sm.lyapunov_classify(x0, p0, K, nsteps=800)
reg = np.where(lam <= 0.02)[0]
reg = rng.choice(reg, size=min(360, reg.size), replace=False)
T = 4000
acc_reg, _, _ = sm.iterate_splat(x0[reg], p0[reg], K, T, S, weight=1.0 / T)

# golden pair
acc_g1, _, _ = sm.iterate_splat(np.array([0.0]), np.array([p_gold]), K, 600000, S)
acc_g2, _, _ = sm.iterate_splat(np.array([0.0]), np.array([p_mirr]), K, 600000, S)

np.save("p1c_in.npy", acc_in); np.save("p1c_out.npy", acc_out)
np.save("p1c_reg.npy", acc_reg); np.save("p1c_gold.npy", acc_g1 + acc_g2)
print("done")
