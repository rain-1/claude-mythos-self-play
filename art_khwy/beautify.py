"""Aesthetic optimization of single-cycle arrangements.
Mode A: from the found witness, maximize min pairwise vertex distance
        (normalized by vertex-cloud radius), keeping C==1.
Mode B: start near the regular tangent arrangement (C=3 for n=11) and
        anneal the SMALLEST perturbation that reaches C==1, then polish
        with mode-A objective at low amplitude.
"""
import numpy as np, sys
from polylib import forced_graph, crossings

def beauty(theta, r):
    comps, edges, _ = forced_graph(theta, r)
    n = len(theta)
    if comps is None or len(comps) != 1: return -1e9, None
    X, Y, T = crossings(theta, r)
    iu = np.triu_indices(n, 1)
    px, py = X[iu], Y[iu]
    cx, cy = px.mean(), py.mean()
    rad = np.sqrt((px-cx)**2 + (py-cy)**2)
    R = np.percentile(rad, 95)
    P = np.stack([px, py], 1)
    d = np.linalg.norm(P[:,None,:]-P[None,:,:], axis=2)
    np.fill_diagonal(d, 1e9)
    mind = d.min()
    # also penalize extreme outliers (blown-up crossings far away)
    spread = rad.max() / max(R, 1e-9)
    score = mind / max(R, 1e-9) - 0.05 * max(spread - 1.6, 0)
    return score, (mind, R, spread)

def polish(theta, r, iters, sigma_t, sigma_r, seed=0):
    rng = np.random.default_rng(seed)
    n = len(theta)
    sc, _ = beauty(theta, r)
    for it in range(iters):
        th2, r2 = theta.copy(), r.copy()
        k = rng.integers(n)
        if rng.random() < 0.5: th2[k] += rng.normal(0, sigma_t)
        else: r2[k] += rng.normal(0, sigma_r)
        s2, _ = beauty(th2, r2)
        if s2 > sc:
            theta, r, sc = th2, r2, s2
    return theta, r, sc

if __name__ == "__main__":
    mode = sys.argv[1]; n = int(sys.argv[2])
    if mode == "A":
        theta = np.load(f"win_n{n}_theta.npy"); r = np.load(f"win_n{n}_r.npy")
        theta, r, sc = polish(theta, r, 30000, 0.02, 0.03, seed=1)
        theta, r, sc = polish(theta, r, 20000, 0.006, 0.01, seed=2)
        print(f"modeA n={n} final beauty={sc:.4f}")
        np.save(f"nice_n{n}_theta.npy", theta); np.save(f"nice_n{n}_r.npy", r)
    elif mode == "B":
        rng = np.random.default_rng(5)
        best = None
        a0 = np.pi * np.arange(n) / n
        for attempt in range(4000):
            amp = rng.uniform(0.01, 0.25)
            theta = (a0 + rng.normal(0, amp * 0.3, n)) % np.pi
            r = 1.0 + rng.normal(0, amp, n)
            comps, _, _ = forced_graph(theta, r)
            if comps is None or len(comps) != 1: continue
            pert = np.abs(r - 1.0).sum() + np.abs((theta - a0 + np.pi/2) % np.pi - np.pi/2).sum()
            if best is None or pert < best[0]:
                best = (pert, theta.copy(), r.copy())
        if best is None:
            print("modeB: none found"); sys.exit()
        pert, theta, r = best
        print(f"modeB n={n} min perturbation={pert:.3f}")
        theta, r, sc = polish(theta, r, 15000, 0.004, 0.006, seed=3)
        print(f"modeB polished beauty={sc:.4f}")
        np.save(f"reg_n{n}_theta.npy", theta); np.save(f"reg_n{n}_r.npy", r)
