"""Discrete Brownian web + its time-reversal dual.

Lattice: sites (x,t) with x+t even carry a fair coin xi(x,t) in {-1,+1}.
FORWARD walker at even site (x,t) moves to (x + xi(x,t), t+1).
DUAL   walker at odd  site (y,t) moves BACKWARD to (y - xi(y,t-1), t-1).

Why the dual never crosses the forward web: a forward edge and a dual edge
sharing a lattice cell both read the SAME coin xi(c,t) at the cell's bottom
row, so they traverse PARALLEL diagonals; and parity (x+t even vs y+t odd)
keeps F(t)-D(t) odd, so paths never even touch. Both families coalesce.

xi is a splitmix64-style pointwise hash of (x,t,seed): evaluable at any
site in any order, cost O(#walkers) per step, nothing stored.
"""
import numpy as np

M1 = np.uint64(0x9E3779B97F4A7C15)
M2 = np.uint64(0xBF58476D1CE4E5B9)
M3 = np.uint64(0x94D049BB133111EB)


def xi_at(x, t, seed):
    """+-1 coin at sites x (int64 array) and scalar time t."""
    with np.errstate(over='ignore'):
        z = x.astype(np.uint64) * M1 + np.uint64(t) * M2 + np.uint64(seed) * M3
        z ^= z >> np.uint64(30); z *= M2
        z ^= z >> np.uint64(27); z *= M3
        z ^= z >> np.uint64(31)
    return ((z >> np.uint64(63)).astype(np.int64) << 1) - 1


def merge_profile(W, T, seed, stride, n_probe=4096):
    """Cheap pass recording the number of distinct forward walkers (and dual
    walkers) at n_probe times -> used to build the row warp. Returns
    (ts, nF, nD)."""
    every = max(T // n_probe, 1)
    pos = np.arange(0, W, 2 * stride, dtype=np.int64)
    dpos = np.arange(1, W, 2 * stride, dtype=np.int64)
    ts, nF, nD = [], [], []
    for t in range(T):
        if t % every == 0:
            ts.append(t); nF.append(np.unique(pos).size)
        pos = (pos + xi_at(pos, t, seed)) % W
    for t in range(T, 0, -1):
        dpos = (dpos - xi_at(dpos, t - 1, seed)) % W
        if (t - 1) % every == 0:
            nD.append(np.unique(dpos).size)
    nD = nD[::-1]
    return np.array(ts), np.array(nF, float), np.array(nD, float)


def warp_from_profile(ts, nF, nD, T, blend=0.5):
    """Row warp = blend * CDF(merge events, fwd+dual) + (1-blend) * linear.
    Merge-event density ~ |dnF/dt| + |dnD/dt|. Returns warp(s in [0,1])."""
    eF = -np.gradient(nF); eD = np.gradient(nD)  # dual loses walkers as t drops
    e = np.clip(eF, 0, None) + np.clip(np.abs(eD), 0, None)
    e = e + 1e-9
    cdf = np.cumsum(e); cdf = (cdf - cdf[0]) / (cdf[-1] - cdf[0])
    s_grid = ts / T

    def warp(s):
        c = np.interp(s, s_grid, cdf)
        return blend * c + (1 - blend) * s
    return warp


def verify(W=4096, T=512, seed=3, npairs=300):
    """Empirical non-crossing + parity check for forward/dual path pairs far
    from the periodic seam. Returns (ncross, nparity_bad, ncoalesce_seen)."""
    xs = np.arange(W // 2 - 300, W // 2 + 300, 2, dtype=np.int64)
    ys = xs + 1
    F = np.zeros((T + 1, xs.size), np.int64); F[0] = xs
    for t in range(T):
        F[t + 1] = F[t] + xi_at(F[t], t, seed)
    D = np.zeros((T + 1, ys.size), np.int64); D[T] = ys
    for t in range(T, 0, -1):
        D[t - 1] = D[t] - xi_at(D[t], t - 1, seed)
    ncross = nparity = 0
    rng = np.random.default_rng(0)
    for _ in range(npairs):
        i = rng.integers(xs.size); j = rng.integers(ys.size)
        d = F[:, i] - D[:, j]
        if np.any(d % 2 == 0):
            nparity += 1
        if np.unique(np.sign(d)).size > 1:
            ncross += 1
    ncoal = xs.size - np.unique(F[T]).size
    return ncross, nparity, ncoal
