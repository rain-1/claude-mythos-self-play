"""post.py — Post's lattice of Boolean clones, recomputed from the definitions (MO 515756).

Each clone is defined by a property (Böhler–Creignou–Reith–Vollmer names). We restrict to the
65,536 functions of arity n = 4 (truth tables as 16-bit ints), test every property exactly, and
read the inclusion order off the restricted sets.  With n = 4 the infinite families S_0^k ... are
resolved for k = 2, 3 (S_0^k at arity n coincides with S_0 once k ≥ n), so the computed poset is
Post's lattice truncated to those k.  We then check: lattice size, covering graph, duality symmetry.
"""
import numpy as np, itertools, json

n = 4
N = 1 << n                     # 16 input vectors
F = np.arange(1 << N, dtype=np.int64)          # all truth tables
bit = lambda f, x: (f >> x) & 1                 # f(x) for input vector index x (bit i of x = x_i)

def tt_var(i):
    return sum(1 << x for x in range(N) if (x >> i) & 1)
VARS = [tt_var(i) for i in range(n)]
FULL = (1 << N) - 1

R0 = bit(F, 0) == 0
R1 = bit(F, N - 1) == 1
# monotone: f(x) <= f(x | 1<<i)
M = np.ones(len(F), bool)
for x in range(N):
    for i in range(n):
        if not (x >> i) & 1:
            M &= bit(F, x) <= bit(F, x | (1 << i))
# self-dual: f(~x) = ~f(x)
D = np.ones(len(F), bool)
for x in range(N):
    D &= bit(F, x) != bit(F, (N - 1) ^ x)
# affine: ANF of degree <= 1  (Möbius transform over GF(2))
anf = F.copy()
for i in range(n):
    for x in range(N):
        if (x >> i) & 1:
            anf ^= ((anf >> (x ^ (1 << i))) & 1) << x
deg_ok = np.ones(len(F), bool)
for x in range(N):
    if bin(x).count('1') >= 2:
        deg_ok &= ((anf >> x) & 1) == 0
L = deg_ok

def separating(ones_side, k):
    """ones_side=False: S0^k (zeros of f: any k share a common 0 coordinate, i.e. OR != all-ones)
       ones_side=True : S1^k (ones of f: any k share a common 1 coordinate, i.e. AND != 0)"""
    Zmask = (~F & FULL) if not ones_side else F
    ok = np.ones(len(F), bool)
    for T in itertools.combinations_with_replacement(range(N), k):
        acc = 0 if not ones_side else N - 1
        for t in T:
            acc = (acc | t) if not ones_side else (acc & t)
        bad = (acc == N - 1) if not ones_side else (acc == 0)
        if bad:
            m = 0
            for t in set(T): m |= 1 << t
            ok &= (Zmask & m) != m
    return ok

S0k = {k: separating(False, k) for k in (1, 2, 3, 4)}
S1k = {k: separating(True, k) for k in (1, 2, 3, 4)}
S0, S1 = S0k[4], S1k[4]          # at arity 4, degree 4 = all of them

consts = (F == 0) | (F == FULL)
projs = np.isin(F, VARS)
negs = np.isin(F, [FULL ^ v for v in VARS])
ORs = np.isin(F, [int(np.bitwise_or.reduce([VARS[i] for i in s])) for r in range(1, n + 1) for s in itertools.combinations(range(n), r)])
ANDs = np.isin(F, [int(np.bitwise_and.reduce([VARS[i] for i in s])) for r in range(1, n + 1) for s in itertools.combinations(range(n), r)])
c0, c1 = F == 0, F == FULL

C = {}
C['BF'] = np.ones(len(F), bool)
C['R0'], C['R1'], C['R2'] = R0, R1, R0 & R1
C['M'], C['M0'], C['M1'], C['M2'] = M, M & R0, M & R1, M & R0 & R1
for tag, S, Sk in (('0', S0, S0k), ('1', S1, S1k)):
    for k in (2, 3):
        C[f'S{tag}^{k}'] = Sk[k]; C[f'S{tag}2^{k}'] = Sk[k] & R0 & R1
        C[f'S{tag}1^{k}'] = Sk[k] & M; C[f'S{tag}0^{k}'] = Sk[k] & R0 & R1 & M
    C[f'S{tag}'] = S; C[f'S{tag}2'] = S & R0 & R1; C[f'S{tag}1'] = S & M; C[f'S{tag}0'] = S & R0 & R1 & M
C['D'], C['D1'], C['D2'] = D, D & R0 & R1, D & M
C['L'], C['L0'], C['L1'], C['L2'], C['L3'] = L, L & R0, L & R1, L & R0 & R1, L & D
C['V'], C['V0'], C['V1'], C['V2'] = ORs | consts, ORs | c0, ORs | c1, ORs
C['E'], C['E0'], C['E1'], C['E2'] = ANDs | consts, ANDs | c0, ANDs | c1, ANDs
C['N'], C['N2'] = projs | negs | consts, projs | negs
C['I'], C['I0'], C['I1'], C['I2'] = projs | consts, projs | c0, projs | c1, projs

names = list(C)
sets = {k: frozenset(np.nonzero(v)[0].tolist()) for k, v in C.items()}
# distinctness
by = {}
for k in names: by.setdefault(sets[k], []).append(k)
dups = [v for v in by.values() if len(v) > 1]
print('clones listed', len(names), 'distinct restrictions', len(by), 'collisions', dups)

# closure check: is each restricted set closed under superposition f(g1..g4)?  (spot check, random)
rng = np.random.default_rng(0)
def compose(f, gs):
    out = 0
    for x in range(N):
        y = 0
        for i, g in enumerate(gs):
            y |= ((g >> x) & 1) << i
        out |= ((f >> y) & 1) << x
    return out
bad = []
for k in names:
    S = np.array(sorted(sets[k]))
    for _ in range(300):
        f = int(rng.choice(S)); gs = [int(rng.choice(S)) for _ in range(n)]
        if compose(f, gs) not in sets[k]:
            bad.append(k); break
print('closure failures (random superpositions):', bad)

# covering relation
less = {(a, b) for a in names for b in names if a != b and sets[a] < sets[b]}
cover = [(a, b) for (a, b) in less if not any((a, c) in less and (c, b) in less for c in names)]
print('cover edges', len(cover))
# duality: swap 0<->1 in names
def dual(nm):
    tr = {'R0': 'R1', 'R1': 'R0', 'M0': 'M1', 'M1': 'M0', 'L0': 'L1', 'L1': 'L0', 'V': 'E', 'E': 'V',
          'V0': 'E1', 'E1': 'V0', 'V1': 'E0', 'E0': 'V1', 'V2': 'E2', 'E2': 'V2', 'I0': 'I1', 'I1': 'I0'}
    if nm in tr: return tr[nm]
    if nm.startswith('S0'): return 'S1' + nm[2:]
    if nm.startswith('S1'): return 'S0' + nm[2:]
    return nm
cs = set(cover)
print('duality symmetric:', all((dual(a), dual(b)) in cs for a, b in cover))
# Post's five maximal clones = coatoms; membership code of each clone
coatoms = sorted(a for a, b in cover if b == 'BF')
print('coatoms', coatoms)
code = {k: [int(sets[k] <= sets[m]) for m in ('R0', 'R1', 'M', 'D', 'L')] for k in names}
json.dump(dict(names=names, cover=cover, code=code, size={k: len(sets[k]) for k in names}), open('post_lattice.json', 'w'), indent=0)
for a, b in sorted(cover, key=lambda e: e[1]): pass
print({k: len(sets[k]) for k in names})
