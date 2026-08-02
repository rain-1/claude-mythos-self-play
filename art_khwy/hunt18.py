"""n=7: hunt an 18-gon = single 18-cycle after dropping a line-triple's
three mutual crossings (21-,20-,19-gons are parity-impossible)."""
import numpy as np, sys, time
from itertools import combinations
from polylib import drop_triangle_graph, forced_graph

def score(theta, r, n):
    """Best (fewest components) over all dropped triangles; returns
    (ncomp, tri) or (99, None)."""
    best = (99, None)
    for tri in combinations(range(n), 3):
        comps, edges = drop_triangle_graph(theta, r, tri)
        if comps is None: continue
        if len(comps) < best[0]:
            best = (len(comps), tri)
    return best

def hunt(n, seed, maxtime=600):
    rng = np.random.default_rng(seed)
    t0 = time.time()
    gbest = 99
    while time.time() - t0 < maxtime:
        theta = rng.uniform(0, np.pi, n)
        r = rng.uniform(-1, 1, n)
        cur, tri = score(theta, r, n)
        if cur == 99: continue
        T = 1.5
        for it in range(3000):
            if time.time() - t0 > maxtime: break
            T *= 0.9985
            th2, r2 = theta.copy(), r.copy()
            k = rng.integers(n)
            if rng.random() < 0.5:
                th2[k] += rng.normal(0, 0.05*(0.2+T))
            else:
                r2[k] += rng.normal(0, 0.08*(0.2+T))
            c2, tri2 = score(th2, r2, n)
            if c2 == 99: continue
            if c2 <= cur or rng.random() < np.exp(-(c2-cur)/max(T,0.02)):
                theta, r, cur, tri = th2, r2, c2, tri2
                if cur == 1:
                    print(f"n={n} DROP-TRI SINGLE CYCLE tri={tri} seed={seed} t={time.time()-t0:.0f}s")
                    np.save(f"win18_n{n}_theta.npy", theta)
                    np.save(f"win18_n{n}_r.npy", r)
                    np.save(f"win18_n{n}_tri.npy", np.array(tri))
                    return
            gbest = min(gbest, cur)
        if gbest == 1: return
    print(f"n={n} seed={seed}: best ncomp={gbest} (no single cycle)")

if __name__ == "__main__":
    n = int(sys.argv[1]); seed = int(sys.argv[2])
    mt = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    hunt(n, seed, mt)
