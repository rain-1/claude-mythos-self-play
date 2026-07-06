import numpy as np, time
import stdmap_core as sm

S = 4096; K = 0.969; N = 8192
rng = np.random.default_rng(0)

def run(mode, batch, steps):
    x = rng.random(N); p = rng.random(N)
    acc32 = np.zeros(S * S, np.float32)
    acc64 = np.zeros(S * S, np.float64)
    bx = np.empty((batch, N)); bp = np.empty((batch, N))
    t0 = time.time()
    for s in range(steps):
        x, p = sm.step(x, p, K)
        bx[s % batch] = x; bp[s % batch] = p % 1.0
        if s % batch == batch - 1:
            fx = bx.ravel() * S; fy = bp.ravel() * S
            if mode == "nearest_bc":
                idx = fy.astype(np.int64) * S + fx.astype(np.int64)
                acc64 += np.bincount(idx, minlength=S * S)
            elif mode == "nearest_addat":
                idx = fy.astype(np.int64) * S + fx.astype(np.int64)
                np.add.at(acc32, idx, np.float32(1.0))
            elif mode == "bilinear_bc":
                ix = fx.astype(np.int64); iy = fy.astype(np.int64)
                ax = fx - ix; ay = fy - iy
                ix1 = (ix + 1) % S; iy1 = (iy + 1) % S
                idx = np.concatenate([iy * S + ix, iy * S + ix1, iy1 * S + ix, iy1 * S + ix1])
                wts = np.concatenate([(1 - ax) * (1 - ay), ax * (1 - ay), (1 - ax) * ay, ax * ay])
                acc64 += np.bincount(idx, weights=wts, minlength=S * S)
    dt = time.time() - t0
    pts = steps * N
    print("%s batch=%d: %.2e pts in %.1fs -> %.2e pts/s" % (mode, batch, pts, dt, pts / dt))

run("nearest_bc", 512, 1024)
run("nearest_addat", 512, 1024)
run("bilinear_bc", 512, 1024)
