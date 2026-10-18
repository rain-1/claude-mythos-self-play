"""Even-n search: minimise violation for n-gons with unit sides in [0,1]^2.
Sides are exactly 1 by construction (angle parametrisation).  Violation =
max over {closure gap, box excess, (delta - nonadjacent clearance)+, (delta - fold)+}.
usage: python3 even.py n seconds delta out.json
"""
import os, sys, json, time
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["NUMBA_NUM_THREADS"] = "1"
import numpy as np
from poly import solve, verts_from_p, residual, exact_check, turns, canon, interior_angles
import search as S
import explore as X

rng = np.random.default_rng(int(time.time() * 1e6) % 2**32)


def breakdown(p, n, delta):
    r = residual(p, n, delta, delta, 1.0, 1.0)
    clos = float(np.hypot(r[0], r[1]))
    box = float(np.max(np.abs(r[2:2 + 4 * n])))
    fold = float(np.max(np.abs(r[2 + 4 * n:2 + 5 * n])))
    sep = float(np.max(np.abs(r[2 + 5 * n:]))) if len(r) > 2 + 5 * n else 0.0
    return dict(viol=max(clos, box, fold, sep), closure=clos, box=box, fold=fold, sep=sep)


def is_square(p, n):
    if n != 4: return False
    V = verts_from_p(p, n)
    return np.all(np.abs(interior_angles(V) - 90) < 5) or np.all(np.abs(interior_angles(V) - 270) < 5)


def main(n, seconds, delta, out):
    t0 = time.time(); top = []; tries = 0

    def consider(p):
        if is_square(p, n): return
        b = breakdown(p, n, delta)
        top.append((b["viol"], p.copy(), b))
        top.sort(key=lambda t: t[0])
        del top[40:]

    while time.time() - t0 < seconds * 0.5:
        u = rng.random()
        p0 = X.zigzag_seed(n) if u < 0.25 else S.GENS[rng.integers(4)](n)
        p, _ = solve(p0, n, margin=delta, fold=delta, max_nfev=150 * n); tries += 1
        consider(p)
    while time.time() - t0 < seconds:  # basin hopping from the best
        base = top[min(int(rng.exponential(5)), len(top) - 1)][1]
        p, _ = solve(X.move(base, n), n, margin=delta, fold=delta, max_nfev=150 * n); tries += 1
        consider(p)
    best = []
    seen = set()
    for v, p, b in top:
        V = verts_from_p(p, n)
        key = round(v, 7)
        if key in seen: continue
        seen.add(key)
        best.append(dict(viol=v, breakdown=b, theta=p.tolist(), verts=V.tolist(),
                         turns=turns(V), exact=exact_check(V)))
    json.dump(dict(n=n, delta=delta, tries=tries, best=best[:10]), open(out, "w"))
    print(f"n={n} delta={delta} tries={tries} best viol={best[0]['viol']:.3e}", best[0]["breakdown"],
          "turns", best[0]["turns"])


if __name__ == "__main__":
    main(int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
