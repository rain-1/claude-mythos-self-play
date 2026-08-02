"""Wall type 2: two lines passing through parallel (crossing at infinity).
Rotate line k across theta_m; compare C parity on both sides."""
import numpy as np
from polylib import forced_graph
rng = np.random.default_rng(11)
n = 7
bad = 0; tot = 0; hist = {}
for trial in range(4000):
    theta = rng.uniform(0, np.pi, n)
    r = rng.uniform(-1, 1, n)
    k, m = rng.choice(n, 2, replace=False)
    eps = 1e-5
    ta = theta.copy(); ta[k] = (theta[m] - eps) % np.pi
    tb = theta.copy(); tb[k] = (theta[m] + eps) % np.pi
    ca, _, _ = forced_graph(ta, r)
    cb, _, _ = forced_graph(tb, r)
    if ca is None or cb is None: continue
    tot += 1
    key = (len(ca) % 2, len(cb) % 2, abs(len(cb)-len(ca)))
    hist[key] = hist.get(key, 0) + 1
    if (len(ca) - len(cb)) % 2: bad += 1
print(f"n={n}: {tot} parallel-wall crossings, parity violations: {bad}")
print(hist)
