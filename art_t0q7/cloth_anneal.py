#!/usr/bin/env python3
"""Simulated annealing for min-area sigma. Moves: segment reversal (2-opt),
pair swap, block rotation. Objective: area_grid at moderate M, refined at end."""
import numpy as np, json, sys, time
from cloth_lib import area_grid, area_exact, sigma_rev, sigma_blockrev

def anneal(n, iters, M, seed, T0=0.02, T1=1e-5, start="rev"):
    rng = np.random.default_rng(seed)
    if start == "rev": s = sigma_rev(n)
    elif start == "blockrev": s = sigma_blockrev(n, max(2, int(np.sqrt(n))))
    else: s = rng.permutation(n)
    cur = area_grid(s, M)
    best = cur; bests = s.copy()
    t0 = time.time()
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        c = s.copy()
        m = rng.integers(0, 3)
        i, j = sorted(rng.integers(0, n, 2))
        if i == j: continue
        if m == 0:      # segment reversal of sigma values
            c[i:j+1] = c[i:j+1][::-1]
        elif m == 1:    # swap
            c[i], c[j] = c[j], c[i]
        else:           # rotate block
            k = rng.integers(1, j - i + 1)
            c[i:j+1] = np.roll(c[i:j+1], k)
        a = area_grid(c, M)
        if a < cur or rng.random() < np.exp(-(a - cur) / max(T, 1e-12)):
            s, cur = c, a
            if a < best: best, bests = a, c.copy()
        if it % max(1, iters // 10) == 0:
            print(f"  n={n} it={it} cur={cur:.5f} best={best:.5f} T={T:.2e} "
                  f"({time.time()-t0:.0f}s)", flush=True)
    fine = area_grid(bests, 8192)
    print(f"n={n} DONE best={best:.6f} fine={fine:.6f} rev={(n+1)/(2*n):.6f} "
          f"({time.time()-t0:.0f}s)", flush=True)
    return bests, fine

if __name__ == "__main__":
    n = int(sys.argv[1]); iters = int(sys.argv[2]); M = int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    start = sys.argv[5] if len(sys.argv) > 5 else "rev"
    s, a = anneal(n, iters, M, seed, start=start)
    json.dump({"n": n, "area": a, "sigma": [int(v) for v in s], "start": start},
              open(f"cloth_anneal_{n}_{seed}_{start}.json", "w"))
    print("saved", f"cloth_anneal_{n}_{seed}_{start}.json")

def anneal_warm(n, iters, M, seed, sigma0, label):
    import numpy as _np
    rng = np.random.default_rng(seed)
    s = np.array(sigma0)
    cur = area_grid(s, M); best = cur; bests = s.copy()
    t0 = time.time()
    T0, T1 = 0.006, 5e-6
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        c = s.copy()
        m = rng.integers(0, 3)
        i, j = sorted(rng.integers(0, n, 2))
        if i == j: continue
        if m == 0: c[i:j+1] = c[i:j+1][::-1]
        elif m == 1: c[i], c[j] = c[j], c[i]
        else:
            k = rng.integers(1, j - i + 1); c[i:j+1] = np.roll(c[i:j+1], k)
        a = area_grid(c, M)
        if a < cur or rng.random() < np.exp(-(a - cur) / max(T, 1e-12)):
            s, cur = c, a
            if a < best: best, bests = a, c.copy()
        if it % max(1, iters // 8) == 0:
            print(f"  [{label}] it={it} cur={cur:.5f} best={best:.5f} ({time.time()-t0:.0f}s)", flush=True)
    fine = area_grid(bests, 8192)
    print(f"[{label}] DONE best={best:.6f} fine={fine:.6f} ({time.time()-t0:.0f}s)", flush=True)
    json.dump({"n": n, "area": fine, "sigma": [int(v) for v in bests]},
              open(f"cloth_anneal_{label}.json", "w"))
