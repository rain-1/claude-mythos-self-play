"""erdos_sat.py — find a ±1 sequence x_1..x_N whose every homogeneous-progression ledger
S_d(k) = x_d + x_{2d} + ... + x_{kd} stays within [-C, C]  (the Erdős discrepancy problem).
Tao (2015): no infinite sequence does it for any C.  Konev–Lisitsa (2014): C = 2 is possible
for N = 1160 and impossible for N = 1161.

Encoding: one-hot ledger states p[d,k,s] with the parity reduction (S_d(k) ≡ k mod 2).
usage: python3 erdos_sat.py N C solver out.json [seed]
"""
import sys, json, time
from pysat.solvers import Solver

N = int(sys.argv[1]); C = int(sys.argv[2]); SOLVER = sys.argv[3]; OUT = sys.argv[4]
SEED = int(sys.argv[5]) if len(sys.argv) > 5 else 0
t0 = time.time()

nv = N  # x_1..x_N are variables 1..N (true = +1)
pid = {}
def P(d, k, s):
    global nv
    key = (d, k, s)
    if key not in pid:
        nv += 1; pid[key] = nv
    return pid[key]

clauses = []
for d in range(1, N + 1):
    K = N // d
    # start state: S_d(0) = 0
    clauses.append([P(d, 0, 0)])
    for k in range(1, K + 1):
        x = k * d
        for s in range(-C, C + 1):
            if (s - (k - 1)) % 2:      # parity: S_d(k-1) ≡ k-1 (mod 2)
                continue
            prev = P(d, k - 1, s)
            # x = +1
            if s + 1 <= C:
                clauses.append([-prev, -x, P(d, k, s + 1)])
            else:
                clauses.append([-prev, -x])
            # x = -1
            if s - 1 >= -C:
                clauses.append([-prev, x, P(d, k, s - 1)])
            else:
                clauses.append([-prev, x])
clauses.append([1])  # symmetry: x_1 = +1
if SEED:
    import random
    random.Random(SEED).shuffle(clauses)
print('N', N, 'C', C, 'vars', nv, 'clauses', len(clauses), 'build %.1fs' % (time.time() - t0), flush=True)

with Solver(name=SOLVER, bootstrap_with=clauses) as s:
    ok = s.solve()
    dt = time.time() - t0
    print('SAT' if ok else 'UNSAT', 'in %.1fs' % dt, flush=True)
    if ok:
        m = s.get_model()
        val = {abs(v): (v > 0) for v in m}
        x = [1 if val.get(i, False) else -1 for i in range(1, N + 1)]
        # verify every ledger
        worst = 0
        for d in range(1, N + 1):
            S = 0
            for k in range(1, N // d + 1):
                S += x[k * d - 1]
                worst = max(worst, abs(S))
        assert worst <= C, worst
        json.dump(dict(N=N, C=C, solver=SOLVER, seconds=dt, x=x, max_abs_ledger=worst), open(OUT, 'w'))
        print('verified: max |ledger| =', worst, 'saved', OUT, flush=True)
