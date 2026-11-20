"""sat.py — digit boards (MO 516966, generalised) by SAT.
board(R,C,mode) -> cells, directed edges; solve(R,C,b,mode,mirror,...) -> grid or None (UNSAT).
mode: rect | holed (centre 2x2 removed) | torus.  mirror: left-right mirror with sigma(d)=d+b/2."""
import sys, time, json, itertools
from pysat.solvers import Cadical153, Glucose4
from pysat.card import CardEnc, EncType

def board(R, C, mode):
    alive = [[True]*C for _ in range(R)]
    if mode.startswith('hole'):          # 'holed' = centre 2x2; 'hole3' = centre 3x3, ...
        h = 2 if mode == 'holed' else int(mode[4:])
        for i in range((R-h)//2, (R-h)//2+h):
            for j in range((C-h)//2, (C-h)//2+h): alive[i][j] = False
    if mode.startswith('mask:'):
        rows = mode[5:].split('/'); assert len(rows) == R and all(len(r) == C for r in rows)
        alive = [[ch == '#' for ch in r] for r in rows]
    tor = mode == 'torus'
    cells = [(i, j) for i in range(R) for j in range(C) if alive[i][j]]
    E = []
    for (i, j) in cells:
        if j+1 < C or (tor and C > 1):
            k = (i, (j+1) % C)
            if alive[k[0]][k[1]]: E.append(((i, j), k))
        if i+1 < R or (tor and R > 1):
            k = ((i+1) % R, j)
            if alive[k[0]][k[1]]: E.append(((i, j), k))
    return cells, E

def solve(R, C, b, mode='rect', mirror=False, fix=True, solver=Cadical153, block=None, extra=None, enc='seq', swapclosed=False):
    cells, E = board(R, C, mode)
    assert len(E) == b*b, (len(E), b*b)
    idx = {c: n for n, c in enumerate(cells)}
    X = lambda c, d: idx[c]*b + d + 1
    top = len(cells)*b
    cl = []
    for c in cells:
        cl.append([X(c, d) for d in range(b)])
        for d in range(b):
            for d2 in range(d+1, b): cl.append([-X(c, d), -X(c, d2)])
    if mirror:
        h = b//2
        for (i, j) in cells:
            m = (i, C-1-j)
            if j < C-1-j:
                for d in range(b):
                    cl.append([-X((i, j), d), X(m, (d+h) % b)])
    # z[e][p] <- x&x ; exactly one edge per pair
    Z = {}
    for n, (u, v) in enumerate(E):
        for k in range(b):
            for l in range(b):
                top += 1; Z[n, k, l] = top
                cl.append([-X(u, k), -X(v, l), top])
                cl.append([-top, X(u, k)]); cl.append([-top, X(v, l)])
    for k in range(b):
        for l in range(b):
            lits = [Z[n, k, l] for n in range(len(E))]
            if enc == 'seq':
                e_ = CardEnc.equals(lits=lits, bound=1, top_id=top, encoding=EncType.seqcounter)
                top = max(top, e_.nv); cl += e_.clauses
            else:
                cl.append(lits)
                for a in range(len(lits)):
                    for c_ in range(a+1, len(lits)): cl.append([-lits[a], -lits[c_]])
    if mirror and swapclosed:
        # LEMMA (see RESULTS.md): in a mirror-symmetric solution the set of horizontal pairs is
        # closed under (k,l)->(l,k), and so is the set of vertical pairs. Redundant but helpful.
        Hs = [n for n, (u, v) in enumerate(E) if u[0] == v[0]]; Vs = [n for n, (u, v) in enumerate(E) if u[0] != v[0]]
        for grp in (Hs, Vs):
            for k in range(b):
                for l in range(b):
                    if k == l: continue
                    big = [Z[n2, l, k] for n2 in grp]
                    for n in grp: cl.append([-Z[n, k, l]] + big)
    if fix and not mirror:   # symmetry breaking: first cell holds 0
        cl.append([X(cells[0], 0)])
    if fix and mirror:
        cl.append([X(cells[0], 0)])
    if extra: cl += extra(X, cells)
    s = solver(bootstrap_with=cl)
    return s, X, cells

def grid_of(model, X, cells, R, C, b):
    ms = set(l for l in model if l > 0)
    g = [[None]*C for _ in range(R)]
    for c in cells:
        for d in range(b):
            if X(c, d) in ms: g[c[0]][c[1]] = d
    return g

def check(g, R, C, b, mode):
    cells, E = board(R, C, mode)
    P = set((g[u[0]][u[1]], g[v[0]][v[1]]) for u, v in E)
    return len(P) == b*b == len(E)

if __name__ == '__main__':
    R, C, b = map(int, sys.argv[1:4]); mode = sys.argv[4]; mirror = len(sys.argv) > 5 and sys.argv[5] == 'm'
    t = time.time()
    from pysat.solvers import Solver
    sname = [a for a in sys.argv[5:] if a.startswith('s=')]
    enc = 'pair' if 'pair' in sys.argv[5:] else 'seq'
    s, X, cells = solve(R, C, b, mode, mirror, enc=enc, swapclosed='swap' in sys.argv[5:], solver=(lambda bootstrap_with: Solver(name=sname[0][2:], bootstrap_with=bootstrap_with)) if sname else Cadical153)
    ok = s.solve()
    if not ok: print('UNSAT', R, C, b, mode, mirror, '%.1fs' % (time.time()-t)); sys.exit()
    g = grid_of(s.get_model(), X, cells, R, C, b)
    assert check(g, R, C, b, mode)
    print('SAT', R, C, b, mode, 'mirror' if mirror else '', '%.1fs' % (time.time()-t))
    D = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for r in g: print(' '.join('.' if x is None else D[x] for x in r))
    json.dump(g, open('sol_%d_%d_%d_%s%s.json' % (R, C, b, mode, '_m' if mirror else ''), 'w'))
