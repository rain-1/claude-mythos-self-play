import json
from cloth_anneal import anneal_warm
import cloth_anneal
# low-T pure-descent polish
d = json.load(open("cloth_anneal_512b.json"))
# monkeypatch T0/T1 via a custom loop: reuse anneal_warm but its T0 is hardcoded 0.006
# so instead just call with fewer wild moves: temporarily edit constants
import numpy as np, time
from cloth_lib import area_grid
n = 512; s = np.array(d["sigma"]); rng = np.random.default_rng(77)
cur = area_grid(s, 704); best = cur; bests = s.copy()
t0 = time.time()
iters = 80000; T0, T1 = 2.5e-5, 1e-6
for it in range(iters):
    T = T0 * (T1/T0) ** (it/iters)
    c = s.copy()
    m = rng.integers(0, 3)
    i, j = sorted(rng.integers(0, n, 2))
    if i == j: continue
    if m == 0: c[i:j+1] = c[i:j+1][::-1]
    elif m == 1: c[i], c[j] = c[j], c[i]
    else:
        k = rng.integers(1, j-i+1); c[i:j+1] = np.roll(c[i:j+1], k)
    a = area_grid(c, 704)
    if a < cur or rng.random() < np.exp(-(a-cur)/max(T, 1e-12)):
        s, cur = c, a
        if a < best: best, bests = a, c.copy()
    if it % 10000 == 0:
        print(f"it={it} cur={cur:.5f} best={best:.5f} ({time.time()-t0:.0f}s)", flush=True)
fine = area_grid(bests, 8192)
print(f"DONE best={best:.6f} fine={fine:.6f}", flush=True)
json.dump({"n": n, "area": fine, "sigma": [int(v) for v in bests]}, open("cloth_anneal_512c.json", "w"))
