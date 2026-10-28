"""Hill-climb in J-space for ground states with large minimal period (certified by LP 3x3 = periodic value).
Usage: python3 longsearch.py SEED SECONDS OUT"""
import sys, json, time
import numpy as np
from gs import strip_opt, lp_bound, period_lattice

PMAX = 11


def evaluate(J):
    es, gs_ = [], []
    for p in range(1, PMAX + 1):
        e, g = strip_opt(J, p)
        es.append(e); gs_.append(g)
    es = np.array(es)
    est = es.min()
    tol = 1e-9 * max(1, np.abs(J).max())
    ps = int(np.argmax(es <= est + tol)) + 1
    area, pv, h, s, fd = period_lattice(gs_[ps - 1])
    lb = lp_bound(J, 3, 3)
    return dict(J=J.tolist(), e=es.tolist(), estar=float(est), pstar=ps, area=int(area), pv=int(pv), h=int(h),
                s=int(s), fd=fd.tolist(), lp33=float(lb), gap=float(est - lb))


def score(r):
    # prefer large certified area; uncertified (gap) cases scored by area too but flagged
    return r["area"] + (0.5 if r["gap"] < 1e-7 else 0) + 0.01 * r["pstar"]


if __name__ == "__main__":
    seed, secs, out = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    rng = np.random.default_rng(seed)
    t0 = time.time()
    found = []
    while time.time() - t0 < secs:
        J = rng.normal(size=16)
        cur = evaluate(J); sc = score(cur)
        for step in range(60):
            if time.time() - t0 > secs:
                break
            J2 = np.array(cur["J"]) + rng.normal(size=16) * rng.choice([0.02, 0.1, 0.3])
            r = evaluate(J2); s2 = score(r)
            if s2 >= sc:
                cur, sc = r, s2
                if r["area"] >= 9:
                    found.append(r)
                    print(round(time.time() - t0), "area", r["area"], (r["pv"], r["h"], r["s"]), "gap", r["gap"], flush=True)
        json.dump(found, open(out, "w"))
    json.dump(found, open(out, "w"))
