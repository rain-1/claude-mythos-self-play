"""Random hill-climb over unions of k segments: log every (a1,a2,a3) seen; push on the drop a_n - a_{n+1}."""
import sys, json, numpy as np
from convex_union import a_seq
seed = int(sys.argv[1]); n = int(sys.argv[2]); secs = float(sys.argv[3])
import time
rng = np.random.default_rng(seed); t0 = time.time()
log = open(f"search_n{n}_s{seed}.jsonl", "a")
def ev(P):
    try:
        a, _ = a_seq([p for p in P], n + 1, res=140, ncand=5, iters=16)
    except Exception as e:
        return None
    return a
best_overall = -9
while time.time() - t0 < secs:
    k = int(rng.integers(3, 9))
    kind = rng.random()
    if kind < 0.5:
        P = rng.normal(size=(k, 2, 2))
    else:  # arcs of a polygonal circle
        P = []
        for i in range(k):
            th = rng.uniform(0, 2*np.pi); L = rng.uniform(0.05, 1.2)
            P.append([(np.cos(th), np.sin(th)), (np.cos(th+L), np.sin(th+L))])
        P = np.array(P)
    w = rng.uniform(-0.3, 0.6)
    a = ev(P)
    if a is None: continue
    J = a[n-1] - a[n] + w * a[n-1]
    sig = 0.15
    for it in range(400):
        Q = P.copy()
        i = rng.integers(k); Q[i, rng.integers(2)] += rng.normal(scale=sig, size=2)
        b = ev(Q)
        if b is None: continue
        Jb = b[n-1] - b[n] + w * b[n-1]
        if Jb > J + 1e-9:
            P, a, J = Q, b, Jb
            log.write(json.dumps(dict(a=[float(x) for x in a], P=P.tolist())) + "\n"); log.flush()
        else:
            sig = max(sig * 0.985, 0.004)
        if time.time() - t0 > secs: break
