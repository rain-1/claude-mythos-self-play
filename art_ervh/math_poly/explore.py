"""Explore the space of valid unit-side polygons for (odd) n by seeded MCMC-like moves.
Moves keep side lengths exactly 1 (angle parametrisation); the solver repairs closure/box/crossing.
usage: python3 explore.py n seconds out.json
"""
import os, sys, json, time
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["NUMBA_NUM_THREADS"] = "1"
import numpy as np
from poly import solve, verts_from_p, p_from_verts, exact_check, turns, canon
import search as S

rng = np.random.default_rng(int(time.time() * 1e6) % 2**32)
MARGIN = 0.006


def set_margin(n):
    global MARGIN
    MARGIN = min(0.006, 0.25 / (n - 1) ** 2) if n >= 13 else 0.006


def raised_zigzag(n):
    """teeth between bottom vertices at small random heights and top vertices; base edge y=0."""
    m = n - 1
    lo = rng.uniform(0.3, 0.45, m + 1) / m**2; lo[0] = lo[-1] = 0.0
    dtop = np.zeros(m + 1); dtop[1::2] = rng.uniform(0, 0.02, len(dtop[1::2])) / m**2
    def comps(top):
        y = lo.copy(); y[1::2] = top - dtop[1::2]
        dy = np.diff(y)
        return y, np.sqrt(np.clip(1 - dy ** 2, 0, None))
    a, b = 0.1, 1.0
    for _ in range(60):
        t = 0.5 * (a + b); y, c = comps(t)
        if c.sum() > 1: a = t
        else: b = t
    y, c = comps(t)
    th = np.r_[np.arctan2(np.diff(y), c), np.pi] + rng.normal(0, 0.003, n)
    return np.r_[0.0, 0.0, th]


def zigzag_seed(n):
    if n >= 7 and rng.random() < 0.7:
        return raised_zigzag(n)
    m = n - 1
    c = rng.dirichlet(np.ones(m) * rng.uniform(1, 20))
    c = np.clip(c, 1e-3, 0.999)
    a = np.arccos(c)
    sg = np.array([1 if k % 2 == 0 else -1 for k in range(m)])
    th = np.r_[sg * a, np.pi]
    p = np.r_[0.0, 0.0, th]
    # random symmetry of square + small noise in position
    if rng.random() < 0.5:
        p[2:] = -p[2:]; p[1] = 1.0
    rot = rng.integers(4) * np.pi / 2
    p[2:] += rot
    V = verts_from_p(p, n)
    V = V - V.min(0)
    return np.r_[V[0], p[2:] + rng.normal(0, 0.02, n)]


def valid(p, n):
    V = verts_from_p(p, n); c = exact_check(V)
    return (c["ok"] and c["clearance"] >= 0.8 * MARGIN), V, c


def repair(p, n):
    p, r = solve(p, n, margin=MARGIN, fold=0.04, max_nfev=150 * n)
    return p


def move(p, n):
    q = p.copy(); th = q[2:]
    u = rng.random()
    if u < 0.3:
        th += rng.normal(0, rng.choice([0.05, 0.15, 0.4]), n)
    elif u < 0.5:  # swap two edges (closure preserved)
        i, j = rng.choice(n, 2, replace=False); th[i], th[j] = th[j], th[i]
    elif u < 0.65:  # reverse a block of edges
        i = rng.integers(n); L = rng.integers(2, max(3, n - 1))
        idx = [(i + k) % n for k in range(L)]
        th[idx] = th[idx][::-1]
    elif u < 0.8:  # rotate a block of edge directions by angle
        i = rng.integers(n); L = rng.integers(2, n)
        idx = [(i + k) % n for k in range(L)]
        th[idx] += rng.normal(0, 0.5)
    else:  # reflect a block of edges across a random axis
        i = rng.integers(n); L = rng.integers(2, n)
        idx = [(i + k) % n for k in range(L)]
        ax = rng.uniform(0, np.pi); th[idx] = 2 * ax - th[idx]
    q[2:] = th
    q[:2] = q[:2] + rng.normal(0, 0.05, 2)
    return q


def main(n, seconds, out):
    set_margin(n)
    t0 = time.time(); pool = []; ntry = 0
    # seeds
    while time.time() - t0 < seconds * 0.25:
        g = rng.random()
        p0 = zigzag_seed(n) if g < 0.6 else S.GENS[rng.integers(4)](n)
        p = repair(p0, n); ntry += 1
        ok, V, c = valid(p, n)
        if ok: pool.append((p, V, c))
    nseed = len(pool)
    while time.time() - t0 < seconds and pool:
        # prefer under-represented classes
        cls = [canon(turns(x[1])) for x in pool]
        cnt = {k: cls.count(k) for k in set(cls)}
        w = np.array([1.0 / cnt[k] for k in cls]); w /= w.sum()
        base = pool[rng.choice(len(pool), p=w)][0]
        p = repair(move(base, n), n); ntry += 1
        ok, V, c = valid(p, n)
        if ok:
            pool.append((p, V, c))
            if len(pool) > 4000: pool.pop(rng.integers(len(pool)))
    res = [dict(verts=V.tolist(), turns=turns(V), canon=canon(turns(V)), clearance=c["clearance"],
                len_err=c["len_err"], box_err=c["box_err"]) for p, V, c in pool]
    json.dump(dict(n=n, tries=ntry, seeds=nseed, found=res), open(out, "w"))
    cs = {}
    for r in res: cs[r["canon"]] = cs.get(r["canon"], 0) + 1
    print(f"n={n} tries={ntry} seeds_ok={nseed} valid={len(res)} classes={len(cs)}")
    for k, v in sorted(cs.items(), key=lambda x: -x[1]): print("   ", k, v)


if __name__ == "__main__":
    main(int(sys.argv[1]), float(sys.argv[2]), sys.argv[3])
