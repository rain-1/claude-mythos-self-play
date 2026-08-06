"""MC study of mu_n = E[T] for uniform random binary n x n; T-distribution; law hunt.
Also verifies the poster's worst-case construction T = 2n-3."""
import numpy as np, json, time
from sort_lib import T_of

rng = np.random.default_rng(20260806)

# ---- worst-case construction check ----
def poster_worst(n):
    A = np.ones((n, n), np.uint8)
    for (i, j) in [(1, 1), (1, 3), (n, 2), (n - 1, n)]:
        A[i - 1, j - 1] = 0
    for i in range(2, n - 1):
        A[i - 1, i] = 0      # (i, i+1)
        A[i - 1, i + 1] = 0  # (i, i+2)
    return A

for n in [5, 8, 12, 20, 50, 120]:
    t, _ = T_of(poster_worst(n))
    print(f"worst-case construction n={n}: T={t} (2n-3={2*n-3})", flush=True)
    assert t == 2 * n - 3

# ---- MC scaling ----
GRID = [(8, 40000), (12, 30000), (16, 20000), (24, 15000), (32, 12000),
        (48, 8000), (64, 6000), (96, 4000), (128, 3000), (192, 2000),
        (256, 1500), (384, 1000), (512, 700), (768, 400), (1024, 300),
        (1536, 160), (2048, 100), (3072, 50), (4096, 36), (6144, 16), (8192, 12)]

out = {}
for n, trials in GRID:
    t0 = time.time()
    Ts = []
    for _ in range(trials):
        A = rng.integers(0, 2, (n, n), dtype=np.int8).astype(np.uint8)
        t, _ = T_of(A)
        Ts.append(t)
    Ts = np.array(Ts)
    dist = {int(t): int((Ts == t).sum()) for t in np.unique(Ts)}
    mu = float(Ts.mean())
    se = float(Ts.std(ddof=1) / np.sqrt(len(Ts)))
    out[n] = dict(trials=trials, mu=mu, se=se, dist=dist)
    print(f"n={n:5d} trials={trials:6d} mu={mu:.4f}+-{se:.4f} dist={dist} [{time.time()-t0:.0f}s]",
          flush=True)
    json.dump(out, open("mc_scale.json", "w"), indent=1)
print("done")
