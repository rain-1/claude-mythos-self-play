"""HERO: the two chaotic seas of the standard map at K=0.969, 4096^2.
4 workers: 2 inner-sea, 2 outer-sea. Each also records per-x-bin p-extremes
of its sea (for the barrier verification) and its seed list.
"""
import numpy as np
import multiprocessing as mp
import stdmap_core as sm

S = 4096
K = 0.969
NBIN = 4096          # x-bins for barrier check
T_STEPS = 125000
N_ENS = 8192

def worker(args):
    wid, which = args
    rng = np.random.default_rng(1000 + wid)
    # SAFE seeding strips (mirror curve max p=0.4704, golden curve min p=0.5296):
    # inner: p in [0.485, 0.515] only; outer: p in [0.714,0.786]|[0.214,0.286]|[-0.036,0.036]
    if which == "inner":
        centers, spread = [0.5], 0.012
    else:
        centers, spread = [0.0, 0.25, 0.75], 0.012
    xs, ps = [], []
    need = N_ENS
    while need > 0:
        n = need * 3
        c = rng.choice(centers, n)
        dp = np.clip(rng.normal(0, spread, n), -2.5 * spread, 2.5 * spread)
        x = rng.random(n); p = (c + dp) % 1.0
        lam = sm.lyapunov_classify(x, p, K, nsteps=2000)
        good = lam > 0.08
        xs.append(x[good][:need]); ps.append(p[good][:need])
        need -= xs[-1].size
    x = np.concatenate(xs); p = np.concatenate(ps)

    acc = np.zeros(S * S, np.float32)
    pmax = np.full(NBIN, -1.0); pmin = np.full(NBIN, 2.0)
    BATCH = 256
    bx = np.empty((BATCH, x.size)); bp = np.empty((BATCH, x.size))
    for s in range(T_STEPS):
        x, p = sm.step(x, p, K)
        bx[s % BATCH] = x; bp[s % BATCH] = p % 1.0
        if s % BATCH == BATCH - 1:
            fx = bx.ravel(); fyv = bp.ravel()
            idx = (fyv * S).astype(np.int64) * S + (fx * S).astype(np.int64)
            np.add.at(acc, idx, np.float32(1.0))
            xb = (fx * NBIN).astype(np.int64)
            np.maximum.at(pmax, xb, fyv)
            np.minimum.at(pmin, xb, fyv)
    np.save("hero_sea_%s_%d.npy" % (which, wid), acc.reshape(S, S))
    np.save("hero_ext_%s_%d.npy" % (which, wid), np.stack([pmin, pmax]))
    return which, wid

if __name__ == "__main__":
    jobs = [(0, "inner"), (1, "inner"), (2, "outer"), (3, "outer")]
    with mp.Pool(4) as pool:
        for r in pool.imap_unordered(worker, jobs):
            print("done", r, flush=True)
    print("ALL DONE")
