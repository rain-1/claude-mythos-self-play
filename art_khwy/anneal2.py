"""Strong aesthetic annealer: joint energy = big*(C-1) + spread energy.
Scale-invariant repulsion: E_rep = mean(1/d_ij) * median(d_ij), plus
outlier control: p99 radius / p50 radius. Runs several seeds, saves best.
Drop-triangle mode for n=7,9 (fixed dropped triple re-chosen each eval)."""
import numpy as np, sys, time
from itertools import combinations
from polylib import forced_graph, drop_triangle_graph, crossings

def vertex_cloud(theta, r):
    n = len(theta)
    X, Y, T = crossings(theta, r)
    if X is None: return None
    iu = np.triu_indices(n, 1)
    return np.stack([X[iu], Y[iu]], 1)

def spread_energy(P):
    d = np.linalg.norm(P[:,None,:]-P[None,:,:], axis=2)
    iu = np.triu_indices(len(P), 1)
    dv = d[iu]
    med = np.median(dv)
    rep = np.mean(med / np.maximum(dv, 1e-12))
    c = P.mean(0)
    rad = np.linalg.norm(P - c, axis=1)
    outlier = np.percentile(rad, 99) / max(np.percentile(rad, 60), 1e-12)
    return rep + 0.55 * max(outlier - 1.8, 0.0)

def energy(theta, r, mode, n):
    if mode == "full":
        comps, edges, _ = forced_graph(theta, r)
        if comps is None: return 1e12, None
        C = len(comps)
        tri = None
    else:
        best = None
        for t in combinations(range(n), 3):
            comps, edges = drop_triangle_graph(theta, r, t)
            if comps is None: continue
            if best is None or len(comps) < best[0]:
                best = (len(comps), t)
        if best is None: return 1e12, None
        C, tri = best
    P = vertex_cloud(theta, r)
    if P is None: return 1e12, None
    return 4000.0 * (C - 1) + spread_energy(P), tri

POLISH = False

def run(n, mode, seeds, iters, timecap):
    t0 = time.time()
    best = (1e18, None)
    for seed in seeds:
        rng = np.random.default_rng(seed)
        # start from existing witness if available
        tag0 = ("hero" if mode == "full" else "hero18") if POLISH else \
               ("win" if mode == "full" else "win18")
        try:
            theta = np.load(f"{tag0}_n{n}_theta.npy"); r = np.load(f"{tag0}_n{n}_r.npy")
        except FileNotFoundError:
            theta = rng.uniform(0, np.pi, n); r = rng.uniform(-1, 1, n)
        theta = theta + rng.normal(0, 0.01, n)
        E, tri = energy(theta, r, mode, n)
        T = 0.06 if POLISH else 0.35
        for it in range(iters):
            if time.time() - t0 > timecap: break
            T = max(T * 0.99985, 0.004)
            th2, r2 = theta.copy(), r.copy()
            k = rng.integers(n)
            amp = 1.0 if rng.random() < 0.8 else 4.0
            if rng.random() < 0.5: th2[k] += rng.normal(0, 0.012 * amp)
            else: r2[k] += rng.normal(0, 0.02 * amp)
            E2, tri2 = energy(th2, r2, mode, n)
            if E2 < E or rng.random() < np.exp(-(E2 - E) / T):
                theta, r, E, tri = th2, r2, E2, tri2
            if E < best[0]:
                best = (E, (theta.copy(), r.copy(), tri))
        print(f"n={n} seed={seed}: E={E:.4f} best={best[0]:.4f}")
    E, (theta, r, tri) = best
    tag = "hero" if mode == "full" else "hero18"
    np.save(f"{tag}_n{n}_theta.npy", theta)
    np.save(f"{tag}_n{n}_r.npy", r)
    if tri is not None:
        np.save(f"{tag}_n{n}_tri.npy", np.array(tri))
    print(f"n={n} FINAL E={E:.4f}")

if __name__ == "__main__":
    n = int(sys.argv[1]); mode = sys.argv[2]
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    POLISH = len(sys.argv) > 4 and sys.argv[4] == "polish"
    globals()["POLISH"] = POLISH
    run(n, mode, [1, 2, 3] if POLISH else [1, 2], 400000, cap)
