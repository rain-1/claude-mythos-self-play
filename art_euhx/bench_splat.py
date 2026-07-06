"""Benchmark: batched-bincount splat vs per-step add.at at S=4096."""
import numpy as np, time
import stdmap_core as sm

S = 4096
K = 0.969
N = 4096            # ensemble
BATCH = 64          # steps per flush
rng = np.random.default_rng(0)
x = rng.random(N); p = rng.random(N)

acc = np.zeros(S * S, np.float64)
bx = np.empty((BATCH, N)); bp = np.empty((BATCH, N))
t0 = time.time()
steps = 512
for s in range(steps):
    x, p = sm.step(x, p, K)
    bx[s % BATCH] = x; bp[s % BATCH] = p % 1.0
    if s % BATCH == BATCH - 1:
        fx = bx.ravel() * S; fy = bp.ravel() * S
        ix = fx.astype(np.int64); iy = fy.astype(np.int64)
        ax = (fx - ix).astype(np.float32); ay = (fy - iy).astype(np.float32)
        ix1 = (ix + 1) % S; iy1 = (iy + 1) % S
        idx = np.concatenate([iy * S + ix, iy * S + ix1, iy1 * S + ix, iy1 * S + ix1])
        wts = np.concatenate([(1 - ax) * (1 - ay), ax * (1 - ay), (1 - ax) * ay, ax * ay])
        acc += np.bincount(idx, weights=wts, minlength=S * S)
dt = time.time() - t0
pts = steps * N
print("bincount-batched: %.2e pts in %.1fs -> %.2e pts/s" % (pts, dt, pts / dt))
