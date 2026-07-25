"""
Independent, from-scratch, exact verification of the claimed counterexample to the
claw-free Schur-positivity conjecture (Gasharov/Stanley), as stated in MO question
513515 "Is this a counterexample to the claw-free Schur-positivity conjecture?".

Claim: H = 4-cycle abcd + triangles auv, cxy at opposite vertices a,c + pendants bl, dm.
G = L(H) (line graph, 12 vertices, claw-free).  Then [s_{(3,3,3,3)}] X_G = -64,
so X_G is NOT Schur-positive.

Everything here is built from first principles:
  * X_G p-expansion via signed edge-subset DFS with exact cycle-cancellation pruning
  * S_12 character table via Murnaghan-Nakayama on beta-sets (orthogonality-verified)
  * Schur coefficients via <X, s_mu> = sum_lam c_lam chi^mu(lam)/z_lam  (Fractions)
  * e-expansion via exact 77x77 Gaussian elimination over Q in p-coordinates
  * cross-checks: chromatic polynomial computed FOUR independent ways
    (p-specialization, Schur hook-content specialization, deletion-contraction,
     brute-force coloring counts for k=3,4)
No Sage, no sympy.  Pure python + fractions.
"""
import json, itertools, sys
from fractions import Fraction
from collections import defaultdict

# ---------------------------------------------------------------- the graph
H_edges = [('a','b'),('b','c'),('c','d'),('d','a'),
           ('a','u'),('a','v'),('u','v'),
           ('c','x'),('c','y'),('x','y'),
           ('b','l'),('d','m')]
assert len(H_edges) == 12 and len(set(map(frozenset,H_edges))) == 12

# G = L(H): vertices = edges of H, adjacency = sharing an endpoint
NV = 12
Gedges = []
for i in range(12):
    for j in range(i+1,12):
        if set(H_edges[i]) & set(H_edges[j]):
            Gedges.append((i,j))
NE = len(Gedges)
adj = [[False]*NV for _ in range(NV)]
for i,j in Gedges: adj[i][j]=adj[j][i]=True
print(f"G = L(H): {NV} vertices, {NE} edges")
assert NE == 22

# connectivity of G
seen={0}; st=[0]
while st:
    v=st.pop()
    for w in range(NV):
        if adj[v][w] and w not in seen: seen.add(w); st.append(w)
assert len(seen)==NV, "G must be connected"
print("G is connected: OK")

# ---------------------------------------------------------------- claw-free check
claws = 0
for c in range(NV):
    nb = [w for w in range(NV) if adj[c][w]]
    for t in itertools.combinations(nb,3):
        if not adj[t[0]][t[1]] and not adj[t[0]][t[2]] and not adj[t[1]][t[2]]:
            claws += 1
print(f"induced claws K_1,3 centered anywhere: {claws}")
assert claws == 0, "G is NOT claw-free!"
print("G is claw-free: OK")

# ---------------------------------------------------------------- p-expansion of X_G
# X_G = sum_{S subset E} (-1)^{|S|} p_{lambda(S)}   (lambda(S) = component sizes)
# DFS over edges; if the current edge's endpoints are already joined by chosen
# edges, the WHOLE subtree cancels in +/- pairs (S <-> S xor {e}) -> prune.
parent = list(range(NV)); size=[1]*NV
def find(x):
    while parent[x]!=x: x=parent[x]
    return x
c_p = defaultdict(int)          # partition (desc tuple) -> integer coefficient
sys.setrecursionlimit(100)
leaves = 0
def dfs(k, sign):
    global leaves
    if k == NE:
        roots = {}
        for v in range(NV):
            r = find(v)
            roots[r] = size[r]
        lam = tuple(sorted(roots.values(), reverse=True))
        c_p[lam] += sign
        leaves += 1
        return
    i,j = Gedges[k]
    ri, rj = find(i), find(j)
    if ri == rj:
        return                   # exact pairwise cancellation of entire subtree
    dfs(k+1, sign)               # exclude edge k
    # include edge k (a genuine merge)
    if size[ri] < size[rj]: ri, rj = rj, ri
    parent[rj] = ri; size[ri] += size[rj]
    dfs(k+1, -sign)
    parent[rj] = rj; size[ri] -= size[rj]   # rollback

dfs(0, 1)
c_p = {lam:v for lam,v in c_p.items() if v != 0}
print(f"p-expansion computed: {leaves} surviving leaves, {len(c_p)} nonzero p-coefficients")

# sanity: sign-alternation (Whitney/NBC): sign of c_lam must be (-1)^(12-len(lam))
for lam,v in c_p.items():
    assert v * (-1)**(12-len(lam)) > 0, (lam,v)
print("p-coefficients sign-alternate (-1)^(n-l(lam)): OK  (NBC theorem)")

# ---------------------------------------------------------------- partitions of 12
def partitions(n, maxp=None):
    if maxp is None: maxp = n
    if n == 0: yield (); return
    for p in range(min(n,maxp), 0, -1):
        for rest in partitions(n-p, p):
            yield (p,)+rest
P12 = sorted(partitions(12), reverse=True)
NP = len(P12)
print(f"partitions of 12: {NP}")
assert NP == 77
pidx = {lam:i for i,lam in enumerate(P12)}

def zlam(lam):
    z = 1
    mult = defaultdict(int)
    for p in lam: mult[p]+=1
    for p,m in mult.items():
        z *= p**m
        for t in range(1,m+1): z *= t
    return z
Z = {lam: zlam(lam) for lam in P12}

# ---------------------------------------------------------------- Murnaghan-Nakayama
L = 14   # beta-set length
memo = {}
def chi(mu, rho):
    """character chi^mu(rho), mu partition, rho cycle type (tuples)"""
    if not rho: return 1
    key = (mu, rho)
    if key in memo: return memo[key]
    r = rho[0]; rest = rho[1:]
    beta = set(mu[i] + (L-1-i) if i < len(mu) else (L-1-i) for i in range(L))
    total = 0
    for b in beta:
        if b - r >= 0 and (b-r) not in beta:
            nb = set(beta); nb.remove(b); nb.add(b-r)
            ht = sum(1 for x in beta if b-r < x < b)   # beta numbers strictly between
            snb = sorted(nb, reverse=True)
            nmu = tuple(x - (L-1-i) for i,x in enumerate(snb))
            nmu = tuple(x for x in nmu if x > 0)
            total += (-1)**ht * chi(nmu, rest)
    memo[key] = total
    return total

# verify: dims and full orthogonality
import math
fdim = {mu: chi(mu, tuple([1]*12)) for mu in P12}
assert sum(f*f for f in fdim.values()) == math.factorial(12)
assert all(chi((12,), lam) == 1 for lam in P12)
assert all(chi(tuple([1]*12), lam) == (-1)**(12-len(lam)) for lam in P12)
# row orthogonality (all 77*78/2 pairs, exact)
for a in range(NP):
    for b in range(a, NP):
        s = sum(Fraction(chi(P12[a],lam)*chi(P12[b],lam), Z[lam]) for lam in P12)
        assert s == (1 if a==b else 0), (P12[a],P12[b],s)
print("S_12 character table: dimensions + FULL row orthogonality verified exactly")

# ---------------------------------------------------------------- Schur expansion
# <p_lam, s_mu> = chi^mu(lam)  (s_mu = sum_rho chi^mu(rho)/z_rho p_rho, <p,p>=z),
# so [s_mu] X_G = <X_G, s_mu> = sum_lam c_lam chi^mu(lam)  -- an integer sum.
a_s = {}
for mu in P12:
    a_s[mu] = sum(v * chi(mu, lam) for lam,v in c_p.items())

target = a_s[(3,3,3,3)]
print(f"\n[s_(3,3,3,3)] X_G = {target}")
negs = {mu:v for mu,v in a_s.items() if v < 0}
print(f"negative Schur coefficients: {negs}")
print(f"claim [s_3333] = -64: {'CONFIRMED' if target == -64 else 'REFUTED'}")

# ---------------------------------------------------------------- e-expansion
# e_k in p-basis; e_mu by convolution; solve 77x77 over Q
def e_in_p(k):
    d = {}
    for lam in partitions(k):
        d[lam] = Fraction((-1)**(k-len(lam)), zlam(lam))
    return d
ek = {k: e_in_p(k) for k in range(1,13)}
def conv(d1, d2):
    out = defaultdict(Fraction)
    for l1,v1 in d1.items():
        for l2,v2 in d2.items():
            out[tuple(sorted(l1+l2, reverse=True))] += v1*v2
    return dict(out)
e_mu_p = {}
for mu in P12:
    d = {(): Fraction(1)}
    for part in mu: d = conv(d, ek[part])
    e_mu_p[mu] = d
# matrix M[lam][mu], solve M d = c
M = [[e_mu_p[mu].get(lam, Fraction(0)) for mu in P12] for lam in P12]
cvec = [Fraction(c_p.get(lam,0)) for lam in P12]
n = NP
for col in range(n):
    piv = next(r for r in range(col,n) if M[r][col] != 0)
    M[col],M[piv] = M[piv],M[col]; cvec[col],cvec[piv] = cvec[piv],cvec[col]
    inv = 1/M[col][col]
    M[col] = [x*inv for x in M[col]]; cvec[col] *= inv
    for r in range(n):
        if r != col and M[r][col] != 0:
            f = M[r][col]
            M[r] = [xr - f*xc for xr,xc in zip(M[r],M[col])]
            cvec[r] -= f*cvec[col]
a_e = {}
for i,mu in enumerate(P12):
    assert cvec[i].denominator == 1
    a_e[mu] = int(cvec[i])
# verify e-expansion reproduces p-expansion
chk = defaultdict(Fraction)
for mu,v in a_e.items():
    for lam,w in e_mu_p[mu].items(): chk[lam] += v*w
for lam in P12:
    assert chk[lam] == c_p.get(lam,0)
print("e-expansion solved and re-verified against p-expansion exactly")
e_negs = sum(1 for v in a_e.values() if v < 0)
print(f"e-expansion: {sum(1 for v in a_e.values() if v>0)} positive, {e_negs} negative, "
      f"{sum(1 for v in a_e.values() if v==0)} zero coefficients")

# ---------------------------------------------------------------- chromatic polynomial, four ways
# (1) from p-expansion: chi_G(k) = sum c_lam k^{l(lam)}
def chrom_p(k):
    return sum(v * k**len(lam) for lam,v in c_p.items())
# (2) from Schur expansion: s_mu(1^k) = prod (k + j - i)/hook  (hook content formula)
def s_at_ones(mu, k):
    val = Fraction(1)
    mu_conj = [sum(1 for p in mu if p > j) for j in range(mu[0])] if mu else []
    for i,row in enumerate(mu):
        for j in range(row):
            hook = row - j + mu_conj[j] - i - 1
            val *= Fraction(k + j - i, hook)
    return val
def chrom_s(k):
    s = sum(v * s_at_ones(mu,k) for mu,v in a_s.items())
    assert s.denominator == 1
    return int(s)
# (3) deletion-contraction (memoized, independent code path)
from functools import lru_cache
def canon(edges):
    return tuple(sorted(edges))
dcmemo = {}
def chrom_dc(vs, edges):
    """returns coefficient list of chromatic polynomial in k, index = power"""
    key = (vs, edges)
    if key in dcmemo: return dcmemo[key]
    if not edges:
        out = [0]*vs + [1]     # k^vs
        dcmemo[key] = out
        return out
    e = edges[0]
    rest = edges[1:]
    d = chrom_dc(vs, rest)                      # delete
    # contract: merge e[1] into e[0]
    m = {}
    for (x,y) in rest:
        x2 = e[0] if x==e[1] else x
        y2 = e[0] if y==e[1] else y
        if x2 != y2: m[frozenset((x2,y2))] = None
    cont_edges = canon(tuple(tuple(sorted(fs)) for fs in m))
    c = chrom_dc(vs-1, cont_edges)              # contract
    out = [ (d[i] if i<len(d) else 0) - (c[i] if i<len(c) else 0) for i in range(max(len(d),len(c))) ]
    dcmemo[key] = out
    return out
# relabel-free: vertices as ints, contraction keeps labels -> memo keyed by edge structure
poly = chrom_dc(NV, canon(Gedges))
def chrom_dc_eval(k): return sum(cf * k**i for i,cf in enumerate(poly))
# (4) brute force count for k=3 and k=4
import numpy as np
def brute(k):
    tot = 0
    B = 12
    # enumerate colorings in chunks via mixed radix
    Nc = k**B
    chunk = 1<<20
    ecols = np.array(Gedges)
    for start in range(0, Nc, chunk):
        idx = np.arange(start, min(start+chunk, Nc), dtype=np.int64)
        cols = np.empty((len(idx), B), dtype=np.int8)
        t = idx.copy()
        for b in range(B):
            cols[:,b] = t % k; t //= k
        ok = np.ones(len(idx), dtype=bool)
        for i,j in Gedges:
            ok &= cols[:,i] != cols[:,j]
        tot += int(ok.sum())
    return tot

print("\nchromatic polynomial cross-checks:")
for k in range(0, 9):
    v1, v2, v3 = chrom_p(k), chrom_s(k), chrom_dc_eval(k)
    assert v1 == v2 == v3, (k,v1,v2,v3)
    print(f"  chi_G({k}) = {v1}   (p-exp == schur-exp == deletion-contraction)")
b3, b4 = brute(3), brute(4)
assert b3 == chrom_p(3) and b4 == chrom_p(4)
print(f"  brute-force proper colorings: chi_G(3) = {b3}, chi_G(4) = {b4}  MATCH")

# ---------------------------------------------------------------- degree/sanity extras
# X_G is homogeneous of degree 12; coefficient of s_(1^12): = number of acyclic
# orientation related?  Also: [s_(12)] should equal 0 unless G has no edges? print a few.
print(f"\n[s_(12)] = {a_s[(12,)]},  [s_(1^12)] = {a_s[tuple([1]*12)]}")
stotal = sum(1 for v in a_s.values() if v != 0)
print(f"Schur support: {stotal} of 77 partitions; negatives: {len(negs)}")

# ---------------------------------------------------------------- dump results
out = {
 "H_edges": H_edges, "G_edges": Gedges,
 "c_p": {" ".join(map(str,l)): v for l,v in sorted(c_p.items(), reverse=True)},
 "a_s": {" ".join(map(str,l)): v for l,v in sorted(a_s.items(), reverse=True)},
 "a_e": {" ".join(map(str,l)): v for l,v in sorted(a_e.items(), reverse=True)},
 "chromatic_poly_coeffs": poly,
 "claw_count": claws,
 "target_s3333": target,
}
with open("art_q2mb/results.json","w") as f:
    json.dump(out, f, indent=1)
print("\nresults written to art_q2mb/results.json")
