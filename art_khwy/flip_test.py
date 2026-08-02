"""Test: how does C change across a triple-concurrence wall?
Build a pencil (3 lines through ~origin) + n-3 random lines; nudge line k
across the concurrence; measure delta-C and the straddle count S."""
import numpy as np
from polylib import forced_graph
rng = np.random.default_rng(3)
n = 7
results = {}
for trial in range(4000):
    theta = rng.uniform(0, np.pi, n)
    r = np.empty(n)
    # lines 0,1,2 through a common point q
    q = rng.uniform(-0.5, 0.5, 2)
    for i in range(3):
        r[i] = np.cos(theta[i])*q[0] + np.sin(theta[i])*q[1]
    r[3:] = rng.uniform(-1, 1, n-3)
    eps = 1e-4
    ra = r.copy(); ra[2] -= eps
    rb = r.copy(); rb[2] += eps
    ca, _, _ = forced_graph(theta, ra)
    cb, _, _ = forced_graph(theta, rb)
    if ca is None or cb is None: continue
    dC = abs(len(cb) - len(ca))
    # straddle count: on each pencil line, position parity of the near-pair
    S = 0
    for i in range(3):
        others = [j for j in range(n) if j != i]
        ct, st = np.cos(theta), np.sin(theta)
        ts = []
        for j in others:
            d = ct[i]*st[j] - ct[j]*st[i]
            x = (ra[i]*st[j] - ra[j]*st[i]) / d
            y = (ct[i]*ra[j] - ct[j]*ra[i]) / d
            ts.append((-st[i]*x + ct[i]*y, j))
        ts.sort()
        pos = [a for a, (t, j) in enumerate(ts) if j in (0,1,2) and j != i]
        if not (len(pos) == 2 and pos[1] == pos[0]+1):
            S = None; break   # pair not adjacent (another line slips between): skip
        if pos[0] % 2 == 1: S += 1
    if S is None: continue
    key = (S, len(ca) % 2, len(cb) % 2, dC)
    results[key] = results.get(key, 0) + 1
print("S  parityBefore parityAfter |dC| : count")
for k in sorted(results):
    print(k, results[k])
