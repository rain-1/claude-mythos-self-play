"""MO 41939 balls-and-colours: pick ordered pair (A,B) of distinct balls
uniformly, paint B with A's colour; E[steps to monochrome] = (n-1)^2.

1) exact small-n verification via Markov chain on colour-count partitions
2) ensemble mean at larger n (vectorized lockstep)
3) one full history at n=512 for the tapestry render
"""
import numpy as np
import pickle
from itertools import combinations
from functools import lru_cache
import time


def exact_ET(n):
    """Exact E[T] from all-distinct start, via states = sorted count
    multisets (partitions of n into positive parts)."""
    # enumerate partitions of n
    def parts(n, mx):
        if n == 0:
            yield ()
            return
        for p in range(min(n, mx), 0, -1):
            for rest in parts(n - p, p):
                yield (p,) + rest
    P = [tuple(sorted(pt, reverse=True)) for pt in parts(n, n)]
    idx = {pt: i for i, pt in enumerate(P)}
    N = len(P)
    A = np.zeros((N, N))
    b = np.ones(N)
    denom = n * (n - 1)
    for pt, i in idx.items():
        if len(pt) == 1:
            A[i, i] = 1.0
            b[i] = 0.0
            continue
        A[i, i] = 1.0
        # transition: choose colour a (count x) as painter, colour bcol
        # (count y) as painted: prob x*y/denom -> counts (x+1, y-1)
        stay = 0.0
        for ai in range(len(pt)):
            for bi in range(len(pt)):
                if ai == bi:
                    # same colour painting itself: nothing changes
                    stay += pt[ai] * (pt[ai] - 1) / denom
                    continue
                pr = pt[ai] * pt[bi] / denom
                new = list(pt)
                new[ai] += 1
                new[bi] -= 1
                new = tuple(sorted((c for c in new if c > 0), reverse=True))
                A[i, idx[new]] -= pr
        A[i, i] -= stay
    # E_i = 1 + sum_j p_ij E_j  (absorbing E=0) -> (I - P) E = 1
    E = np.linalg.solve(A, b)
    start = tuple([1] * n)
    return E[idx[start]]


def ensemble_mean(n, R, seed=0, cap_factor=8):
    rng = np.random.default_rng(seed)
    colors = np.tile(np.arange(n), (R, 1))
    counts = np.ones((R, n), dtype=np.int32)
    T = np.zeros(R, dtype=np.int64)
    done = np.zeros(R, dtype=bool)
    cap = cap_factor * (n - 1) ** 2
    rows = np.arange(R)
    t = 0
    while not done.all() and t < cap:
        t += 1
        a = rng.integers(0, n, R)
        b = (a + 1 + rng.integers(0, n - 1, R)) % n   # b != a uniform
        act = ~done
        ca = colors[rows, a]
        cb = colors[rows, b]
        diff = act & (ca != cb)
        r = rows[diff]
        counts[r, cb[diff]] -= 1
        counts[r, ca[diff]] += 1
        colors[r, b[diff]] = ca[diff]
        newly = diff & (counts[rows, ca] == n)
        T[~done & newly] = t
        done |= newly
    T[~done] = cap
    return T


def one_history(n=512, seed=11):
    """Full event log of one run: list of (t, painter_ball, painted_ball,
    old_colour, new_colour); plus final colour + ancestry threading."""
    rng = np.random.default_rng(seed)
    colors = np.arange(n).copy()
    counts = np.ones(n, dtype=np.int64)
    events = []
    t = 0
    while counts.max() < n:
        t += 1
        a = int(rng.integers(0, n))
        b = int((a + 1 + rng.integers(0, n - 1)) % n)
        ca, cb = colors[a], colors[b]
        if ca != cb:
            counts[cb] -= 1
            counts[ca] += 1
            colors[b] = ca
            events.append((t, a, b, int(cb), int(ca)))
    return {"n": n, "T": t, "events": events, "winner": int(colors[0])}


if __name__ == "__main__":
    t0 = time.time()
    for n in range(2, 9):
        e = exact_ET(n)
        print(f"n={n}: exact E[T]={e:.6f}  (n-1)^2={(n-1)**2}")
    print("exact solve", time.time() - t0)
    t0 = time.time()
    for n, R in [(32, 4000), (128, 1500)]:
        T = ensemble_mean(n, R, seed=1)
        print(f"n={n}: mean T={T.mean():.1f} +- {T.std()/np.sqrt(len(T)):.1f}"
              f"  target {(n-1)**2}")
    print("ensembles", time.time() - t0)
    h = one_history(512, seed=11)
    print("history n=512: T =", h["T"], " (511^2 =", 511**2, ")")
    pickle.dump(h, open("colors_history.pkl", "wb"))
