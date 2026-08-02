"""Print the actual edge diff across one triple-flip with S=1."""
import numpy as np
from polylib import forced_graph
rng = np.random.default_rng(3)
n = 7
found = 0
for trial in range(4000):
    theta = rng.uniform(0, np.pi, n)
    r = np.empty(n)
    q = rng.uniform(-0.5, 0.5, 2)
    for i in range(3):
        r[i] = np.cos(theta[i])*q[0] + np.sin(theta[i])*q[1]
    r[3:] = rng.uniform(-1, 1, n-3)
    eps = 1e-4
    ra = r.copy(); ra[2] -= eps
    rb = r.copy(); rb[2] += eps
    ca, ea, _ = forced_graph(theta, ra)
    cb, eb, _ = forced_graph(theta, rb)
    if ca is None or cb is None: continue
    S = 0; ok = True
    ct, st = np.cos(theta), np.sin(theta)
    for i in range(3):
        others = [j for j in range(n) if j != i]
        ts = []
        for j in others:
            d = ct[i]*st[j] - ct[j]*st[i]
            x = (ra[i]*st[j] - ra[j]*st[i]) / d
            y = (ct[i]*ra[j] - ct[j]*ra[i]) / d
            ts.append((-st[i]*x + ct[i]*y, j))
        ts.sort()
        pos = [a for a, (t, j) in enumerate(ts) if j in (0,1,2) and j != i]
        if not (len(pos) == 2 and pos[1] == pos[0]+1): ok = False; break
        if pos[0] % 2 == 1: S += 1
    if not ok or S != 1: continue
    sa, sb = set(map(tuple, map(sorted, ea))), set(map(tuple, map(sorted, eb)))
    def name(v):
        return f"v{v//n}{v%n}"
    print(f"trial {trial}: S=1, C {len(ca)}->{len(cb)}")
    print("  removed:", sorted(tuple(map(name, e)) for e in sa - sb))
    print("  added:  ", sorted(tuple(map(name, e)) for e in sb - sa))
    found += 1
    if found >= 4: break
