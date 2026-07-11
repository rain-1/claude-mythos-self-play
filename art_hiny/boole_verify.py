"""Boole map T(x) = x - 1/x — verify the math before any pixels.

1. Measure preservation (Boole 1857): for nice f, ∫ f(x-1/x) dx = ∫ f(x) dx.
   Empirical check: push a huge Lebesgue-ish sample through T; occupation of
   fixed windows is preserved (in the infinite-measure sense, compare window
   counts of the pushforward of a wide uniform sample).
2. Excursion clock: during a high excursion x² decreases by 2 - 1/x² per step
   (exact identity: T(x)² = x² - 2 + 1/x²).
3. Lamperti/Thaler generalized arcsine law: fraction of time with x>0 over a
   long orbit is arcsine-distributed (excursion durations are stable-1/2).
"""
import numpy as np

rng = np.random.default_rng(7)

# ---- 1. exact identity check (T(x)^2 = x^2 - 2 + 1/x^2) --------------------
x = rng.uniform(-50, 50, 10)
lhs = (x - 1/x)**2
rhs = x*x - 2 + 1/(x*x)
print("identity max err:", np.abs(lhs-rhs).max())

# ---- 1b. measure preservation on windows -----------------------------------
# Take u ~ Uniform(-B, B), B huge. Pushforward by T. For a window W well inside,
# density of T(u) should equal density of u (both = N/(2B) per unit length).
B = 4000.0
N = 40_000_000
u = rng.uniform(-B, B, N)
v = u - 1.0/u
windows = [(-2,-1), (-0.5,0.5), (0.7,1.3), (2,5), (10,20), (100,150)]
print("\nwindow      count(u)   count(T u)   ratio")
for a,b in windows:
    cu = np.count_nonzero((u>a)&(u<b))
    cv = np.count_nonzero((v>a)&(v<b))
    print(f"[{a:6.1f},{b:6.1f}]  {cu:9d}  {cv:9d}   {cv/max(cu,1):.4f}")

# ---- 3. arcsine law for time-positive fraction ------------------------------
# Long orbits, many independent starts; fraction of steps with x>0.
M = 4000        # orbits
T = 200_000     # steps
x = rng.uniform(0.5, 2.0, M)   # arbitrary starts
pos = np.zeros(M, dtype=np.int64)
for t in range(T):
    x = x - 1.0/x
    pos += (x > 0)
frac = pos / T
# compare CDF to arcsine: F(t) = (2/pi) arcsin(sqrt(t))
qs = np.linspace(0.05, 0.95, 10)
emp = np.quantile(frac, qs)
theo = np.sin(np.pi*qs/2)**2   # inverse of arcsine CDF
print("\narcsine check   q   empirical   theoretical(sin^2(pi q/2))")
for q,e,t_ in zip(qs, emp, theo):
    print(f"   {q:.2f}    {e:.4f}    {t_:.4f}")
# KS distance
s = np.sort(frac)
F_theo = (2/np.pi)*np.arcsin(np.sqrt(np.clip(s,0,1)))
ks = np.abs(F_theo - np.arange(1,M+1)/M).max()
print("KS distance to arcsine:", round(ks,4), " (√M·KS =", round(ks*np.sqrt(M),2), ")")

# ---- orbit anatomy: excursion census for render planning --------------------
x0 = rng.uniform(0.5, 2.0, 1)[0]
x = x0
xs = np.empty(2_000_000)
for t in range(len(xs)):
    x = x - 1.0/x
    xs[t] = x
sgn = xs > 0
# excursion = maximal run of constant sign
change = np.nonzero(np.diff(sgn.astype(np.int8)))[0]
durs = np.diff(np.concatenate([[0], change, [len(xs)]]))
peaks = []
start = 0
bounds = np.concatenate([[0], change+1, [len(xs)]])
for i in range(len(bounds)-1):
    seg = xs[bounds[i]:bounds[i+1]]
    peaks.append(np.abs(seg).max())
peaks = np.array(peaks)
print("\nexcursions in 2e6 steps:", len(durs))
print("duration quantiles:", np.quantile(durs, [0.5, 0.9, 0.99, 1.0]).astype(int))
print("peak quantiles:", np.round(np.quantile(peaks, [0.5, 0.9, 0.99, 1.0]),1))
print("total time in top-10 excursions:", durs[np.argsort(durs)[-10:]].sum(), "/", len(xs))
