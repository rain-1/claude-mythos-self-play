"""Fast coalescing-walk simulation: only unique representatives are stepped
(after a merge, walkers are identical forever), so cost per step shrinks
with the walker count. Records the merge profile and per-sample positions."""
import numpy as np
import web_core


def init_positions(Ws, stride, seed, forward):
    rng = np.random.default_rng(seed + (0 if forward else 1))
    n0 = Ws // (2 * stride)
    base = np.sort(rng.choice(Ws // 2, size=n0, replace=False)) * 2
    return base + (0 if forward else 1)


def run(Ws, T, seed, stride, forward=True, sample_set=None, n_probe=2048):
    """Simulate; return (profile_ts, profile_n, X, M).
    X[j] = wrapped position of each ORIGINAL walker at the j-th sorted sample
    time; M[j] = its group mass. X/M are None if sample_set is None."""
    pos0 = init_positions(Ws, stride, seed, forward)
    n0 = pos0.size
    R = pos0.copy()                       # unique representative positions
    o2r = np.arange(n0)                   # original -> representative index
    every = max(T // n_probe, 1)
    ts, ns = [], []
    samples = None
    if sample_set is not None:
        utimes = np.sort(np.unique(sample_set))
        order = {int(t): j for j, t in enumerate(utimes)}
        X = np.zeros((len(utimes), n0), np.float32)
        M = np.zeros((len(utimes), n0), np.int32)
        tset = set(int(t) for t in utimes)
    trange = range(T + 1) if forward else range(T, -1, -1)
    for t in trange:
        tt = t if forward else T - t      # elapsed steps
        if tt % every == 0 and t != trange[-1]:
            ts.append(t); ns.append(R.size)
        if sample_set is not None and t in tset:
            j = order[t]
            X[j] = R[o2r]
            cnt = np.bincount(o2r, minlength=R.size)
            M[j] = cnt[o2r]
        if (forward and t < T) or (not forward and t > 0):
            xi = web_core.xi_at(R, t if forward else t - 1, seed)
            R = (R + (xi if forward else -xi)) % Ws
            u, inv = np.unique(R, return_inverse=True)
            if u.size < R.size:
                o2r = inv[o2r]
                R = u
    if sample_set is None:
        return np.array(ts), np.array(ns, float), None, None
    return np.array(ts), np.array(ns, float), X, M


def unwrap(X, Ws):
    """Remove k*Ws winding jumps along the time axis (per walker)."""
    d = np.diff(X.astype(np.float64), axis=0)
    d -= Ws * np.round(d / Ws)
    return np.concatenate([X[:1].astype(np.float64),
                           X[:1] + np.cumsum(d, axis=0)]).astype(np.float32)
