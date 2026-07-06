"""Is the golden pair the ONLY rotational barrier at K? Seed chaotic orbits in the
middle band and outside; watch their p-ranges over long runs."""
import numpy as np
import stdmap_core as sm

K = 0.969
GOLD = (np.sqrt(5) - 1) / 2

def Wof(p, n=200000):
    return sm.rotation_number(np.array([0.0]), np.array([p]), K, nsteps=n)[0]

lo, hi = 0.60, 0.72
for _ in range(45):
    mid = 0.5 * (lo + hi)
    if Wof(mid) < GOLD: lo = mid
    else: hi = mid
p_gold = 0.5 * (lo + hi)
print("K=%.4f golden p0=%.12f W=%.13f" % (K, p_gold, Wof(p_gold)))

# trace the golden circle: record its p as function of x (bin by x)
x = np.array([0.0]); p = np.array([p_gold])
nbin = 2000
pmin = np.full(nbin, 10.0); pmax = np.full(nbin, -10.0)
for _ in range(2000000):
    x, p = sm.step(x, p, K)
    b = int(x[0] * nbin) % nbin
    pv = p[0] % 1.0
    if pv < pmin[b]: pmin[b] = pv
    if pv > pmax[b]: pmax[b] = pv
print("golden circle band: p in [%.4f, %.4f], thickness max %.5f"
      % (pmin.min(), pmax.max(), (pmax - pmin).max()))

# chaotic orbit seeded in the MIDDLE band (near period-2 separatrix, p~0.5+)
rng = np.random.default_rng(1)
xm = rng.random(64); pm = np.full(64, 0.5) + rng.normal(0, 0.01, 64)
lam = sm.lyapunov_classify(xm, pm, K, nsteps=1500)
sel = lam > 0.05
print("mid-band chaotic seeds:", sel.sum())
xm, pm = xm[sel], pm[sel]
top = np.full(xm.shape, -10.0); bot = np.full(xm.shape, 10.0)
x, p = xm.copy(), pm.copy()
for _ in range(400000):
    x, p = sm.step(x, p, K)
    pv = p % 1.0
    top = np.maximum(top, pv); bot = np.minimum(bot, pv)
print("middle-sea p-range over all seeds: [%.4f, %.4f]" % (bot.min(), top.max()))
print("golden curve min p: %.4f  (sea must stay below)" % pmin.min())

# chaotic orbit seeded OUTSIDE (main island separatrix, p~0 layer)
xo = rng.random(64); po = rng.normal(0, 0.02, 64) % 1.0
lam = sm.lyapunov_classify(xo, po, K, nsteps=1500)
sel = lam > 0.05
print("outer chaotic seeds:", sel.sum())
xo, po = xo[sel], po[sel]
top = np.full(xo.shape, -10.0); bot = np.full(xo.shape, 10.0)
x, p = xo.copy(), po.copy()
for _ in range(400000):
    x, p = sm.step(x, p, K)
    pv = p % 1.0
    top = np.maximum(top, pv); bot = np.minimum(bot, pv)
print("outer-sea p-range (wrapped): min %.4f max %.4f" % (bot.min(), top.max()))
