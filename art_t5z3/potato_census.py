"""potato_census.py — how many closed curves do two potatoes share at a random pose?

For N random rigid placements of B (uniform rotation, translation direction uniform, |τ| uniform in
[0.15, 1.9] — the poses whose surfaces cross), count the components of ∂A ∩ g∂B (sign regions on the
chart sphere minus one).  Also: along the hero's arc sweep at fine steps, the component count as a
function of the moment, and where it changes (each change is a tangency: a loop is born or dies, or
two loops merge/split — the "moment it stops being the same curve").
Writes cache/potato_census.json.
"""
import json, time
import numpy as np
from potato import make_bodies, Chart, random_rotation

A, B = make_bodies()
chart = Chart(A, 512, 1024)
rng = np.random.default_rng(2026)
t0 = time.time()
counts = []
N = 800
for i in range(N):
    R = random_rotation(rng)
    d = rng.standard_normal(3); d /= np.linalg.norm(d)
    tau = d * rng.uniform(0.15, 1.9)
    g = chart.field(B, tau, R)
    if g.min() > 0 or g.max() < 0:
        continue                      # no crossing (B outside, or A inside B / B inside A)
    counts.append(chart.components(g))
counts = np.array(counts)
hist = {int(k): int((counts == k).sum()) for k in np.unique(counts)}
print('random poses with crossing:', len(counts), 'of', N, 'component histogram', hist, round(time.time() - t0, 1), 's')

# fine sweep along the hero's arc
NT = 720
ts = np.linspace(0, 1, NT, endpoint=False); ang = 2 * np.pi * ts
e1 = np.array([1.0, 0.15, 0.35]); e1 /= np.linalg.norm(e1)
e2 = np.array([-0.2, 1.0, 0.45]); e2 -= e1 * (e2 @ e1); e2 /= np.linalg.norm(e2)
taus = 0.78 * (np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2)
sweep = []
for k, tau in enumerate(taus):
    g = chart.field(B, tau)
    sweep.append(chart.components(g) if (g.min() < 0 < g.max()) else 0)
sweep = np.array(sweep)
changes = [(int(k), int(sweep[k - 1]), int(sweep[k])) for k in range(1, NT) if sweep[k] != sweep[k - 1]]
print('arc sweep components: values', {int(k): int((sweep == k).sum()) for k in np.unique(sweep)}, 'changes', changes)

# the straight-line sweep (B through A along v): births and deaths
ts2 = np.linspace(0, 1, NT)
v = np.array([1.0, 0.35, 0.55]); v /= np.linalg.norm(v)
taus2 = (ts2[:, None] - 0.5) * 3.4 * v
sweep2 = []
for tau in taus2:
    g = chart.field(B, tau)
    sweep2.append(chart.components(g) if (g.min() < 0 < g.max()) else 0)
sweep2 = np.array(sweep2)
changes2 = [(round(float(ts2[k]), 4), int(sweep2[k - 1]), int(sweep2[k])) for k in range(1, NT) if sweep2[k] != sweep2[k - 1]]
print('line sweep changes', changes2)
json.dump(dict(random_hist=hist, random_crossing=int(len(counts)), random_total=N,
               arc_sweep_values={int(k): int((sweep == k).sum()) for k in np.unique(sweep)}, arc_changes=changes,
               line_changes=changes2, seconds=time.time() - t0), open('cache/potato_census.json', 'w'), indent=1)
print('done', time.time() - t0)
