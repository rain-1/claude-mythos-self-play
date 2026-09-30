"""ferris.py — Ferris wheel numbers (MO 515611).

n is a Ferris wheel number if its k = tau(n) divisors can be hung at the k-th roots
of unity so that the centre of mass is the hub:  sum_j d_{pi(j)} zeta^j = 0.

Facts used here (see notes_ferris.md):
  * (de Bruijn / Redei–Schoenberg) an integer vector c on Z_k has sum c_j zeta^j = 0
    iff c = sum_{p | k prime} f_p with f_p periodic of period k/p.
  * LEMMA (this run): if k has at most two distinct prime factors, no n with tau(n)=k
    is a Ferris wheel number (the largest divisor n sits in a p x q 'sum block' whose
    neighbours would have to be divisors strictly between n/2 and n).
  * the same condition written over Q: the Ramanujan-sum 'trace' equations
      sum_j c_j R(j - r) = 0  for every r,   R(m) = mu(k/g)/phi(k/g), g = gcd(m,k)
    (Tao's answer uses r = position of n).  Rearrangement gives a cheap necessary test.
"""
import sys, math, itertools, time
import numpy as np
from sympy import divisors, factorint, totient, mobius, cyclotomic_poly, Poly, symbols


def R(m, k):
    g = math.gcd(m, k)
    q = k // g
    return int(mobius(q)) / int(totient(q))


def trace_slack(n, divs=None):
    """n minus the largest amount the other divisors can cancel in the trace equation
    centred on n.  > 0  ==>  n is certainly not a Ferris wheel number."""
    d = sorted(divs or divisors(n))
    k = len(d)
    coef = sorted(R(j, k) for j in range(1, k))          # most negative first
    rest = sorted(d[:-1], reverse=True)                     # largest first
    return n + sum(c * x for c, x in zip(coef, rest))


def primes_of(k):
    return sorted(factorint(k))


def cyclo_matrix(k):
    """(phi(k), k) integer matrix M with zeta^j = sum_i M[i,j] zeta^i (power basis)."""
    x = symbols('x')
    Phi = Poly(cyclotomic_poly(k, x), x)
    ph = Phi.degree()
    M = np.zeros((ph, k), dtype=np.int64)
    for j in range(k):
        r = Poly(x ** j, x).rem(Phi)
        for (e,), c in r.terms():
            M[e, j] = int(c)
    return M


def solve_ilp(n, time_limit=60, verbose=False):
    """exact: returns permutation (list of divisors by position) or None; 'timeout' if undecided"""
    from ortools.sat.python import cp_model
    d = sorted(divisors(n))
    k = len(d)
    M = cyclo_matrix(k)
    m = cp_model.CpModel()
    X = [[m.NewBoolVar(f'x{j}_{i}') for i in range(k)] for j in range(k)]
    for j in range(k):
        m.AddExactlyOne(X[j])
    for i in range(k):
        m.AddExactlyOne(X[j][i] for j in range(k))
    m.Add(X[0][k - 1] == 1)                       # n at position 0 (rotation)
    # reflection: position of n/2 ... skip; mirror j -> -j: ask d[k-2] at j <= k/2
    m.Add(sum(X[j][k - 2] for j in range(k // 2 + 1)) == 1)
    for row in M:
        m.Add(sum(int(row[j]) * d[i] * X[j][i] for j in range(k) for i in range(k) if row[j]) == 0)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = 4
    st = s.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        perm = [None] * k
        for j in range(k):
            for i in range(k):
                if s.Value(X[j][i]):
                    perm[j] = d[i]
        return perm
    if st == cp_model.INFEASIBLE:
        return None
    return 'timeout'


def solve_cp2(n, time_limit=60, workers=4, log=False):
    """de Bruijn model: c_j in divisors (all different), c_j = sum_p f_p[j mod k/p]."""
    from ortools.sat.python import cp_model
    d = sorted(divisors(n))
    k = len(d)
    ps = primes_of(k)
    m = cp_model.CpModel()
    dom = cp_model.Domain.FromValues(d)
    c = [m.NewIntVarFromDomain(dom, f'c{j}') for j in range(k)]
    m.AddAllDifferent(c)
    m.Add(c[0] == n)
    F = {p: [m.NewIntVar(-n, n, f'f{p}_{i}') for i in range(k // p)] for p in ps}
    # gauge: f_p for the largest p has zero mean on each class -- cheap symmetry cut: f_{p}[0]=0 for p != first
    for p in ps[1:]:
        m.Add(F[p][0] == 0)
    for j in range(k):
        m.Add(c[j] == sum(F[p][j % (k // p)] for p in ps))
    # mirror: largest proper divisor in the first half
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = workers
    s.parameters.log_search_progress = log
    st = s.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return [s.Value(x) for x in c]
    if st == cp_model.INFEASIBLE:
        return None
    return 'timeout'


def solve_set(d, time_limit=60, workers=4, hint=None):
    """EXACT: c_j in the set (all different), n pinned at 0, sum_j M[i,j] c_j = 0 for the
    power-basis reduction mod Phi_k.  INFEASIBLE is a proof; returns list / None / 'timeout'."""
    from ortools.sat.python import cp_model
    d = sorted(d)
    k = len(d)
    M = cyclo_matrix(k)
    m = cp_model.CpModel()
    dom = cp_model.Domain.FromValues(d)
    c = [m.NewIntVarFromDomain(dom, f'c{j}') for j in range(k)]
    m.AddAllDifferent(c)
    m.Add(c[0] == d[-1])
    for row in M:
        m.Add(sum(int(row[j]) * c[j] for j in range(k) if row[j]) == 0)
    if hint:
        for j, v in enumerate(hint):
            m.AddHint(c[j], v)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = workers
    st = s.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return [s.Value(x) for x in c]
    if st == cp_model.INFEASIBLE:
        return None
    return 'timeout'


def solve_n(n, time_limit=60, workers=4):
    return solve_set(divisors(n), time_limit, workers)


if __name__ == '__main__':
    for n in map(int, sys.argv[1:]):
        d = divisors(n)
        k = len(d)
        t0 = time.time()
        sl = trace_slack(n, d)
        r = solve_n(n, 120)
        print(n, 'k=', k, 'primes(k)=', primes_of(k), 'slack/n=%.4f' % (sl / n), '->', r, '%.1fs' % (time.time() - t0), flush=True)




def solve_set2(d, time_limit=60, workers=4, trace_rows=True):
    """solve_set + redundant trace equations (sum_j c_j R(j-r) = 0, scaled by lcm of phi's) for propagation."""
    from ortools.sat.python import cp_model
    d = sorted(d); k = len(d)
    M = cyclo_matrix(k)
    m = cp_model.CpModel()
    c = [m.NewIntVarFromDomain(cp_model.Domain.FromValues(d), f'c{j}') for j in range(k)]
    m.AddAllDifferent(c); m.Add(c[0] == d[-1])
    for row in M:
        m.Add(sum(int(row[j]) * c[j] for j in range(k) if row[j]) == 0)
    if trace_rows:
        L = 1
        for q in divisors(k):
            L = L * int(totient(q)) // math.gcd(L, int(totient(q)))
        co = [int(round(R(m_, k) * L)) for m_ in range(k)]
        for r in range(k):
            m.Add(sum(co[(j - r) % k] * c[j] for j in range(k) if co[(j - r) % k]) == 0)
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = time_limit; s.parameters.num_workers = workers
    st = s.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE): return [s.Value(x) for x in c]
    if st == cp_model.INFEASIBLE: return None
    return 'timeout'
