"""MO 513798: max k-gon on n lines.

Reduction (odd n, k = n(n-1)/2 = full Eulerian bound):
A simple k-gon with k=C(n,2) sides on n lines must use every pairwise
intersection exactly once as a corner. Along each line (n-1 crossings,
sorted), the sides on that line form a perfect matching by segments with
no crossing in their interior => forced matching {(0,1),(2,3),...}.
Segments on two different lines can only meet at the lines' unique
intersection point, which is never interior to a forced segment => the
union is automatically a non-crossing 2-regular graph on C(n,2) vertices.
So: k = n(n-1)/2 achievable  <=>  some arrangement's forced graph is a
SINGLE cycle.
"""
import numpy as np
import sys

def components(theta, r):
    """Given n lines x cos t + y sin t = r, return list of cycle lengths
    of the forced odd-matching graph, or None if degenerate."""
    n = len(theta)
    ct, st = np.cos(theta), np.sin(theta)
    # intersection of line i and j
    pts = {}
    for i in range(n):
        for j in range(i+1, n):
            d = ct[i]*st[j] - ct[j]*st[i]
            if abs(d) < 1e-12: return None
            x = (r[i]*st[j] - r[j]*st[i]) / d
            y = (ct[i]*r[j] - ct[j]*r[i]) / d
            pts[(i,j)] = (x,y)
    # adjacency: vertex = pair (i,j); on each line sort crossings, match (0,1)(2,3)...
    adj = {v: [] for v in pts}
    for i in range(n):
        others = [j for j in range(n) if j != i]
        # param along line i: direction (-st, ct)
        ts = []
        for j in others:
            key = (min(i,j), max(i,j))
            x,y = pts[key]
            t = -st[i]*x + ct[i]*y
            ts.append((t, key))
        ts.sort()
        m = len(ts)
        if m % 2: return None
        for a in range(0, m, 2):
            u, v = ts[a][1], ts[a+1][1]
            adj[u].append(v); adj[v].append(u)
    # cycle decomposition
    seen = set(); comps = []
    for v0 in pts:
        if v0 in seen: continue
        c = 0; prev = None; v = v0
        while v not in seen:
            seen.add(v); c += 1
            nxt = adj[v][0] if adj[v][0] != prev else adj[v][1]
            prev, v = v, nxt
        comps.append(c)
    return sorted(comps)

def trial(n, rng):
    theta = rng.uniform(0, np.pi, n)
    r = rng.uniform(-1, 1, n)
    return components(theta, r), (theta, r)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    from collections import Counter
    hist = Counter(); best = None
    for t in range(trials):
        comps, cfg = trial(n, rng)
        if comps is None: continue
        hist[tuple(comps)] += 1
        if best is None or len(comps) < len(best[0]):
            best = (comps, cfg)
            if len(comps) == 1:
                print("SINGLE CYCLE FOUND at trial", t)
                np.save(f"art_khwy/win_n{n}_theta.npy", cfg[0])
                np.save(f"art_khwy/win_n{n}_r.npy", cfg[1])
                break
    print(f"n={n} trials={trials}")
    for k, v in sorted(hist.items(), key=lambda kv: -kv[1])[:15]:
        print(f"  {v:7d}  ncomp={len(k)}  {k}")
    print("best:", best[0])
