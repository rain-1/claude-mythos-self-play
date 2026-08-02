"""Hunt single cycles (n=11,13: full V-gon) by annealing on ncomp."""
import numpy as np, sys, time
from polylib import forced_graph, ncomp

def hunt(n, seed, maxtime=600):
    rng = np.random.default_rng(seed)
    t0 = time.time()
    best_global = 99
    while time.time() - t0 < maxtime:
        theta = rng.uniform(0, np.pi, n)
        r = rng.uniform(-1, 1, n)
        comps, _, _ = forced_graph(theta, r)
        if comps is None: continue
        cur = len(comps)
        T = 1.5
        for it in range(4000):
            T *= 0.999
            th2, r2 = theta.copy(), r.copy()
            k = rng.integers(n)
            if rng.random() < 0.5:
                th2[k] += rng.normal(0, 0.05*(0.2+T))
            else:
                r2[k] += rng.normal(0, 0.08*(0.2+T))
            comps2, _, _ = forced_graph(th2, r2)
            if comps2 is None: continue
            c2 = len(comps2)
            if c2 <= cur or rng.random() < np.exp(-(c2-cur)/max(T,0.02)):
                theta, r, cur = th2, r2, c2
                if cur == 1:
                    print(f"n={n} SINGLE CYCLE seed={seed} iter={it} t={time.time()-t0:.0f}s")
                    np.save(f"win_n{n}_theta.npy", theta)
                    np.save(f"win_n{n}_r.npy", r)
                    return theta, r
            best_global = min(best_global, cur)
    print(f"n={n} seed={seed}: no single cycle, best ncomp={best_global}")
    return None

if __name__ == "__main__":
    n = int(sys.argv[1]); seed = int(sys.argv[2])
    mt = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    hunt(n, seed, mt)
