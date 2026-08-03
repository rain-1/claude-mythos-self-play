"""cp_represent.py — which comparative probability orders admit an agreeing
additive measure?  (Kraft–Pratt–Seidenberg 1959: all do for n <= 4; some do
not for n = 5.)

For each enumerated order (cp_enum output): LP  max t  s.t. for consecutive
ranks A_r < A_{r+1}:  sum_{A_{r+1}} x - sum_{A_r} x >= t,  sum x = 1, x >= 0.
 - t* > 0  -> representable; rationalize x and CONFIRM all 2^n-1 consecutive
   inequalities in exact Fraction arithmetic (which implies the full order by
   transitivity).
 - t* <= 0 -> non-representable; CERTIFY with an exact integer Farkas witness:
   a nonnegative-integer combination of the order's strict comparisons
   (canonical disjoint pairs, oriented by the order) whose indicator vectors
   sum to zero — finitely many confident judgements that cannot all be true
   of any measure. Found by small-support search, verified exactly.

Outputs representable/non-representable partition + witnesses to stdout and
cp_results_n5.txt.
"""
import sys, itertools, numpy as np
from fractions import Fraction
from scipy.optimize import linprog

SCR = "/tmp/claude-0/-home-user-claude-mythos-self-play/adf44c3e-737f-5218-82c7-9c74bc24d1b1/scratchpad"

def load(fn):
    return [list(map(int, line.split())) for line in open(fn) if not line.startswith('#')]

def popvec(S, n):
    return np.array([(S >> i) & 1 for i in range(n)], dtype=float)

def lp_margin(order, n):
    NS = 1 << n
    A_ub, b_ub = [], []
    for r in range(NS - 1):
        lo, hi = order[r], order[r + 1]
        row = np.zeros(n + 1)
        row[:n] = popvec(lo, n) - popvec(hi, n)  # sum(lo)-sum(hi)+t <= 0
        row[n] = 1.0
        A_ub.append(row); b_ub.append(0.0)
    A_eq = [np.concatenate([np.ones(n), [0.0]])]
    res = linprog(c=np.concatenate([np.zeros(n), [-1.0]]),
                  A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(A_eq), b_eq=[1.0],
                  bounds=[(0, None)] * n + [(None, None)],
                  method="highs")
    assert res.status == 0, res.message
    return res.x[:n], res.x[n]

def confirm_exact(order, x, n):
    """rationalize x and verify all consecutive strict inequalities exactly"""
    NS = 1 << n
    xf = [Fraction(v).limit_denominator(10 ** 6) for v in x]
    for r in range(NS - 1):
        lo, hi = order[r], order[r + 1]
        slo = sum(xf[i] for i in range(n) if lo >> i & 1)
        shi = sum(xf[i] for i in range(n) if hi >> i & 1)
        if not slo < shi:
            return None
    return xf

def farkas_witness(order, n):
    """oriented comparison vectors v = 1_{bigger} - 1_{smaller} over canonical
    disjoint pairs implied by the order; find small nonneg-int combo summing
    to 0. Returns list of (smallerset, biggerset, mult)."""
    NS = 1 << n
    rank = {S: r for r, S in enumerate(order)}
    vecs, pairs = [], []
    for S in range(NS):
        for T in range(S + 1, NS):
            if S & T: continue
            if S == T: continue
            a, b = (S, T) if rank[S] < rank[T] else (T, S)  # a smaller
            v = tuple(int((b >> i & 1) - (a >> i & 1)) for i in range(n))
            vecs.append(v); pairs.append((a, b))
    V = np.array(vecs)
    m = len(vecs)
    # meet-in-the-middle: hash all single vectors and all pair-sums
    single = {}
    for i in range(m):
        single.setdefault(tuple(V[i]), i)
    pairsum = {}
    for i in range(m):
        for j in range(i + 1, m):
            pairsum.setdefault(tuple(V[i] + V[j]), (i, j))
    # size 3: v_i + v_j + v_k = 0
    for key, (i, j) in pairsum.items():
        negk = tuple(-x for x in key)
        if negk in single:
            k = single[negk]
            if k != i and k != j:
                return [(pairs[t][0], pairs[t][1], 1) for t in (i, j, k)]
    # size 4: pairsum + pairsum = 0 (disjoint index sets)
    for key, (i, j) in pairsum.items():
        negk = tuple(-x for x in key)
        if negk in pairsum:
            a, b = pairsum[negk]
            if len({i, j, a, b}) == 4:
                return [(pairs[t][0], pairs[t][1], 1) for t in (i, j, a, b)]
    # fallback: LP dual then rationalize
    res = linprog(c=np.zeros(m), A_eq=np.vstack([V.T, np.ones(m)]),
                  b_eq=[0]*n + [1], bounds=[(0, None)]*m, method="highs")
    if res.status == 0:
        lam = res.x
        scale = 1.0 / min(v for v in lam if v > 1e-9)
        lamI = np.round(lam * scale).astype(int)
        if (V.T @ lamI == 0).all() and lamI.sum() > 0:
            return [(pairs[i][0], pairs[i][1], int(lamI[i]))
                    for i in range(m) if lamI[i]]
    return None

def verify_witness(w, n):
    tot = np.zeros(n, dtype=int)
    for a, b, mult in w:
        tot += mult * np.array([(b >> i & 1) - (a >> i & 1) for i in range(n)])
    return not tot.any() and len(w) > 0

def fmt(S, n):
    return "{" + ",".join(str(i + 1) for i in range(n) if S >> i & 1) + "}" if S else "0"

results = {}
for n, fn in ((3, "orders3c.txt"), (4, "orders4c.txt"), (5, "orders5c.txt")):
    orders = load(f"{SCR}/{fn}")
    rep, nonrep = [], []
    for oi, order in enumerate(orders):
        x, t = lp_margin(order, n)
        if t > 1e-9:
            xf = confirm_exact(order, x, n)
            assert xf is not None, f"exact confirm failed n={n} #{oi}"
            rep.append(oi)
        else:
            w = farkas_witness(order, n)
            assert w is not None and verify_witness(w, n), f"no witness n={n} #{oi}"
            nonrep.append((oi, w))
    results[n] = (orders, rep, nonrep)
    print(f"n={n}: {len(orders)} orders (canonical), representable {len(rep)}, "
          f"NON-representable {len(nonrep)}")

orders5, rep5, nonrep5 = results[5]
print(f"\nfirst non-representable n=5 order + Farkas witness:")
with open(f"{SCR}/cp_results_n5.txt", "w") as f:
    f.write(f"representable {len(rep5)} nonrep {len(nonrep5)}\n")
    for oi, w in nonrep5:
        f.write("ORDER " + " ".join(map(str, orders5[oi])) + "\n")
        f.write("WITNESS " + " ".join(f"{a},{b},{m}" for a, b, m in w) + "\n")
for oi, w in nonrep5[:3]:
    print(f"  order #{oi}:")
    for a, b, mult in w:
        print(f"    {mult} x [ {fmt(a,5)} < {fmt(b,5)} ]")
    print("    (indicator sums balance exactly -> no measure can satisfy all)")
