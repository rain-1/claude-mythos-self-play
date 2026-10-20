#!/usr/bin/python3
"""Find 2-colourings of the n x n grid with no monochromatic axis-parallel square.
Run with /usr/bin/python3 (has pysat)."""
import json, sys, time
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def squares(n):
    for s in range(1, n):
        for r in range(n - s):
            for c in range(n - s):
                yield [(r, c), (r, c + s), (r + s, c), (r + s, c + s)]


def check(g):
    n = len(g)
    for sq in squares(n):
        vals = {g[r][c] for r, c in sq}
        if len(vals) == 1:
            return False
    return True


def solve(n, ones=None, rot=None, timeout=None):
    """rot: None | 'anti90' (col(rot90 p)=1-col(p)) | 'sym180' (col(rot180 p)=col(p))
    | 'anti180'."""
    pool = IDPool()
    v = lambda r, c: pool.id((r, c))
    for r in range(n):
        for c in range(n):
            v(r, c)
    cls = []
    for sq in squares(n):
        lits = [v(r, c) for r, c in sq]
        cls.append(lits)                 # not all 0
        cls.append([-x for x in lits])   # not all 1
    rot90 = lambda r, c: (c, n - 1 - r)
    if rot == 'anti90':
        for r in range(n):
            for c in range(n):
                a, b = v(r, c), v(*rot90(r, c))
                cls += [[a, b], [-a, -b]]
    elif rot in ('sym180', 'anti180'):
        for r in range(n):
            for c in range(n):
                a, b = v(r, c), v(n - 1 - r, n - 1 - c)
                if rot == 'sym180':
                    cls += [[-a, b], [a, -b]]
                else:
                    cls += [[a, b], [-a, -b]]
    if ones is not None:
        lits = [v(r, c) for r in range(n) for c in range(n)]
        enc = CardEnc.equals(lits=lits, bound=ones, vpool=pool, encoding=EncType.seqcounter)
        cls += enc.clauses
    s = Cadical153(bootstrap_with=cls)
    t = time.time()
    ok = s.solve()
    dt = time.time() - t
    if not ok:
        return None, dt
    m = set(x for x in s.get_model() if x > 0)
    g = [[1 if v(r, c) in m else 0 for c in range(n)] for r in range(n)]
    return g, dt


if __name__ == '__main__':
    out = {}
    log = []
    for n in (14, 13):
        N = n * n
        target = N // 2
        g, dt = solve(n, ones=target)
        log.append(f"n={n} balanced ones={target}: {'SAT' if g else 'UNSAT'} in {dt:.2f}s")
        print(log[-1], flush=True)
        if g is None:
            g, dt = solve(n)
            log.append(f"n={n} unconstrained: {'SAT' if g else 'UNSAT'} in {dt:.2f}s")
        assert check(g)
        out[str(n)] = g
        if n == 14:
            gs, dt = solve(n, rot='anti90')
            log.append(f"n=14 rot90 anti-symmetry: {'SAT' if gs else 'UNSAT'} in {dt:.2f}s")
            print(log[-1], flush=True)
            if gs:
                assert check(gs)
                assert all(gs[c][n - 1 - r] == 1 - gs[r][c] for r in range(n) for c in range(n))
                out['14_sym'] = gs
                out['sym_type'] = 'rot90_antisymmetric: colour(rot90(p)) = 1 - colour(p)'
        if n == 13:
            # rot90 (anti)symmetry is impossible for 13 (centre fixed / centred squares mono)
            for rt in ('sym180',):
                gs, dt = solve(n, ones=N // 2, rot=rt)
                log.append(f"n=13 {rt} ones={N // 2}: {'SAT' if gs else 'UNSAT'} in {dt:.2f}s")
                print(log[-1], flush=True)
                if gs:
                    assert check(gs)
                    out['13_sym'] = gs
                    out['13_sym_type'] = 'rot180_symmetric: colour(rot180(p)) = colour(p)'
    for k in list(out):
        if isinstance(out[k], list):
            print(k, 'ones =', sum(map(sum, out[k])), 'verified', check(out[k]))
    out['log'] = log
    json.dump(out, open('squarefree.json', 'w'))
