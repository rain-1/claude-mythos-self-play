"""Multi-start search for unit-side simple polygons in the unit square.
usage: python3 search.py n seconds out.json [margin]
"""
import os, sys, json, time
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["NUMBA_NUM_THREADS"] = "1"
import numpy as np
from poly import solve, verts_from_p, p_from_verts, exact_check, turns, canon, residual

rng = np.random.default_rng(int(time.time() * 1e6) % 2**32)


def start_randwalk(n):
    P = rng.random(2)
    th = []
    cur = P.copy()
    for k in range(n):
        for _ in range(50):
            t = rng.uniform(0, 2 * np.pi)
            q = cur + [np.cos(t), np.sin(t)]
            if 0 <= q[0] <= 1 and 0 <= q[1] <= 1:
                break
        th.append(t); cur = q
    return np.r_[P, th]


def start_turns(n):
    # random turn-sign sequence with sharp turns (|turn| ~ 90..180 deg)
    P = rng.random(2)
    t = rng.uniform(0, 2 * np.pi); th = [t]
    bias = rng.uniform(0.3, 0.7)
    for k in range(n - 1):
        sgn = 1 if rng.random() < bias else -1
        t = t + sgn * rng.uniform(np.radians(100), np.radians(175)); th.append(t)
    return np.r_[P, th]


def start_zigzag(n):
    # zigzag of n-1 edges between two lines, closed; then perturbed + random orientation
    m = n - 1
    h = rng.uniform(0.05, 0.99)
    a = np.arcsin(min(h, 0.999))
    th = [a if k % 2 == 0 else -a for k in range(m)]
    base = rng.uniform(0, 2 * np.pi)
    th = np.array(th) + base
    V = np.zeros(2)
    end = np.sum(np.c_[np.cos(th), np.sin(th)], axis=0)
    close = np.arctan2(-end[1], -end[0])
    th = np.r_[th, close] + rng.normal(0, rng.uniform(0.02, 0.4), n)
    return np.r_[rng.random(2) * 0.5, th]


def start_vertex_rw(n):
    # random closed vertex loop then convert
    V = rng.random((n, 2))
    return p_from_verts(V)


GENS = [start_randwalk, start_turns, start_zigzag, start_vertex_rw]


def run(n, seconds, margin, fold=0.03):
    t0 = time.time(); found = []; tried = 0; best = []
    while time.time() - t0 < seconds:
        g = GENS[tried % len(GENS)]
        p0 = g(n); tried += 1
        # stage 1: soft, stage 2: full
        p, r = solve(p0, n, margin=margin, fold=fold, max_nfev=400 * n)
        cost = float(np.max(np.abs(r)))
        V = verts_from_p(p, n)
        chk = exact_check(V)
        best.append((cost, V.tolist(), g.__name__))
        if chk["ok"] and chk["clearance"] >= 0.8 * margin:
            found.append(dict(verts=V.tolist(), turns=turns(V), canon=canon(turns(V)),
                              clearance=chk["clearance"], len_err=chk["len_err"],
                              box_err=chk["box_err"], gen=g.__name__))
    best.sort(key=lambda b: b[0])
    return found, tried, best[:20]


if __name__ == "__main__":
    n = int(sys.argv[1]); sec = float(sys.argv[2]); out = sys.argv[3]
    margin = float(sys.argv[4]) if len(sys.argv) > 4 else 0.005
    found, tried, best = run(n, sec, margin)
    json.dump(dict(n=n, tried=tried, found=found, best=best), open(out, "w"))
    cs = {}
    for f in found: cs[f["canon"]] = cs.get(f["canon"], 0) + 1
    print(n, "tried", tried, "found", len(found), "distinct turn classes", len(cs))
    for k, v in sorted(cs.items(), key=lambda x: -x[1])[:15]: print("  ", k, v)
    print("best residuals", [round(b[0], 6) for b in best[:5]])
