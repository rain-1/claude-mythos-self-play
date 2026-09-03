"""Extra certificate for The Tree and Its Path. By Wilson's algorithm the branch from any
vertex u toward the root is a loop-erased random walk, so the number of tree steps from u
until the branch first leaves the ball of radius r around u scales like r^{5/4}
(the LERW / SLE_2 growth exponent, Kenyon 2000 / Lawler–Schramm–Werner).
Same seed as the piece."""
import sys, math, numpy as np
from ust import wilson, depth_from_root, degree_census

N = int(sys.argv[1]) if len(sys.argv) > 1 else 320
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
parent, root = wilson(N, seed)
depth = depth_from_root(parent, root, N)
counts, deg = degree_census(parent, N)
n = N * N
ii, jj = np.divmod(np.arange(n), N)
rng = np.random.default_rng(7)
# start vertices in the central half (so balls up to r=N/4 stay inside the box)
cand = np.nonzero((ii > N // 4) & (ii < 3 * N // 4) & (jj > N // 4) & (jj < 3 * N // 4))[0]
us = rng.choice(cand, 20000, replace=False)
radii = np.geomspace(3, N / 4, 12)
first = np.full((len(radii), len(us)), -1, np.int64)
cur = us.copy()
alive = np.ones(len(us), bool)
for step in range(1, depth.max() + 2):
    nxt = parent[cur]
    alive &= nxt >= 0
    cur = np.where(alive, nxt, cur)
    d = np.hypot(ii[cur] - ii[us], jj[cur] - jj[us])
    for a, r in enumerate(radii):
        m = (first[a] < 0) & alive & (d >= r)
        first[a][m] = step
    if not alive.any():
        break
xs, ys = [], []
for a, r in enumerate(radii):
    ok = first[a] > 0
    if ok.sum() > 1000:
        xs.append(r); ys.append(np.median(first[a][ok]))
lx, ly = np.log(xs), np.log(ys)
slope, icpt = np.polyfit(lx, ly, 1)
print('degree fractions', np.round(counts, 5))
print('branch steps to leave B(u,r) vs r: log-log slope %.3f  (LERW prediction 5/4 = 1.25); %d starts, %d radii' % (slope, len(us), len(xs)))
for x, y in zip(xs, ys):
    print('  r %6.1f   median steps %8.1f   r^1.25 = %8.1f' % (x, y, x ** 1.25))
