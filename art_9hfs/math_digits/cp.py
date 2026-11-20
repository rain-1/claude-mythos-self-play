"""cp.py R C b mode [m] [t=seconds] [w=workers] — digit boards by OR-tools CP-SAT:
x_cell in 0..b-1, pair value b*x_u + x_v on every directed edge, AllDifferent over the b^2 edges."""
import sys, json, time
from ortools.sat.python import cp_model
from sat import board, check
R, C, b = map(int, sys.argv[1:4]); mode = sys.argv[4]; rest = sys.argv[5:]
mirror = 'm' in rest
tl = float([a[2:] for a in rest if a.startswith('t=')][0]) if any(a.startswith('t=') for a in rest) else 300
nw = int([a[2:] for a in rest if a.startswith('w=')][0]) if any(a.startswith('w=') for a in rest) else 4
cells, E = board(R, C, mode); assert len(E) == b*b, (len(E), b*b)
M = cp_model.CpModel(); x = {}
for (i, j) in cells:
    if mirror and j > C-1-j: continue
    x[i, j] = M.NewIntVar(0, b-1, 'x%d_%d' % (i, j))
if mirror:
    h = b//2
    for (i, j) in cells:
        if j > C-1-j:
            v = M.NewIntVar(0, b-1, 'y%d_%d' % (i, j))
            sig = [(d + h) % b for d in range(b)] if b % 2 == 0 else [0] + [((d - 1 + h) % (b - 1)) + 1 for d in range(1, b)]
            M.AddElement(x[i, C-1-j], sig, v); x[i, j] = v
ps = []
for (u, v) in E:
    p = M.NewIntVar(0, b*b-1, 'p'); M.Add(p == b*x[u] + x[v]); ps.append(p)
M.AddAllDifferent(ps)
if not mirror: M.Add(x[cells[0]] == 0)
# redundant: each digit is the first member of exactly b pairs and the second of exactly b
if 'deg' in rest:
    outd = {c: 0 for c in cells}; ind = {c: 0 for c in cells}
    for (u, v) in E: outd[u] += 1; ind[v] += 1
    B = {}
    for c in cells:
        for d in range(b):
            B[c, d] = M.NewBoolVar('b'); M.Add(x[c] == d).OnlyEnforceIf(B[c, d]); M.Add(x[c] != d).OnlyEnforceIf(B[c, d].Not())
        M.AddExactlyOne([B[c, d] for d in range(b)])
    for d in range(b):
        M.Add(sum(outd[c]*B[c, d] for c in cells) == b); M.Add(sum(ind[c]*B[c, d] for c in cells) == b)
if 'inv' in rest:
    pos = [M.NewIntVar(0, b*b-1, 'q') for _ in range(b*b)]
    M.AddInverse(ps, pos)
S = cp_model.CpSolver(); S.parameters.max_time_in_seconds = tl; S.parameters.num_workers = nw
if any(a.startswith('seed=') for a in rest): S.parameters.random_seed = int([a[5:] for a in rest if a.startswith('seed=')][0])
t0 = time.time(); st = S.Solve(M)
name = S.StatusName(st)
print(name, R, C, b, mode, 'mirror' if mirror else '', '%.0fs' % (time.time()-t0), flush=True)
if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    g = [[None]*C for _ in range(R)]
    for c in cells: g[c[0]][c[1]] = S.Value(x[c])
    assert check(g, R, C, b, mode)
    D = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for r in g: print(' '.join('.' if v is None else D[v] for v in r))
    json.dump(g, open('sol_%d_%d_%d_%s%s.json' % (R, C, b, mode.replace(':', '_').replace('/', '-').replace('#', 'x').replace('.', 'o'), '_m' if mirror else ''), 'w'))
