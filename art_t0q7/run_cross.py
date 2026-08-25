import numpy as np, json
from cloth_anneal import anneal
res = {}
for n, iters in ((10,25000),(12,30000),(14,30000),(16,35000),(20,35000),(24,40000),(32,40000),(48,40000)):
    best = (2.0, None)
    for seed in (1, 2):
        s, a = anneal(n, iters, 512, seed, T0=0.03, start="rev" if seed==1 else "rand")
        if a < best[0]: best = (a, [int(v) for v in s])
    rev = (n+1)/(2*n)
    res[n] = {"best": best[0], "rev": rev, "beats": bool(best[0] < rev - 1e-9), "sigma": best[1]}
    print(f"CROSS n={n}: best {best[0]:.6f} rev {rev:.6f} beats={best[0] < rev - 1e-9}", flush=True)
    json.dump(res, open("cloth_crossover.json", "w"))
print("CROSSDONE")
