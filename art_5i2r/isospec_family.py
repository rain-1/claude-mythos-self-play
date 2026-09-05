"""Cayley–Hamilton families: if u X v ~ u' X v' and u X^2 v ~ u' X^2 v' (same char poly) then u X^k v ~ u' X^k v' for all k.
Proof: chi(u X^k v) = e1^T P_u P_X^k P_v e1, and P_X (2x2, det 1) satisfies P_X^2 = tr(P_X) P_X - I, so f(k) = chi(uX^kv)
and g(k) = chi(u'X^kv') both satisfy the same 2-term recurrence f(k+2) = tr(P_X) f(k+1) - f(k); equal for k=0,1 => equal for all k.
Check: the n=8 seed 00011011 ~ 00100111 with X=01 inserted: u=0001,v=1011 / u'=0010,v'=0111 (k=0 gives the n=8 pair; k=1 the n=10 pair).
Also test which n<=20 nontrivial classes are 'explained' by some (u,X,v),(u',X,v') decomposition with a shorter equal-chi pair at k-1 and k-2 (or k-1 trivially equal strings)."""
import numpy as np, json, sympy as sp
x = sp.symbols('x')
def chi(s):
    Km1, K0 = sp.Integer(0), sp.Integer(1)
    for ch in s:
        Km1, K0 = K0, sp.expand((x - int(ch)) * K0 - Km1)
    return K0
def same(a, b): return sp.expand(chi(a) - chi(b)) == 0
# family A: 0001 (01)^k 1011  ~  0010 (01)^k 0111
print('family A k=0..8:', [same('0001' + '01'*k + '1011', '0010' + '01'*k + '0111') for k in range(9)])
# family with X = '0': 0001 0^k 1011 ?
print('X=0 variant   :', [same('0001' + '0'*k + '1011', '0010' + '0'*k + '0111') for k in range(5)])
# the n=8 pair: is it uv~u'v' with X removed? i.e. k=0 of family A IS the n=8 pair -> the seed is the k=0 member; k=-1 impossible.
# general explanation test on the census: for each nontrivial pair (w,w') of length n, look for a common block X and positions with
# w = u X v, w' = u' X v', such that (u v, u' v') have equal chi and (u X X v, u' X X v') too? (then the recurrence explains the whole family)
cen = json.load(open('isospec_census.json'))
def explained(w, w2):
    n = len(w)
    for L in range(1, n - 1):
        for i in range(0, n - L + 1):
            X = w[i:i+L]
            for j in range(0, n - L + 1):
                if w2[j:j+L] != X: continue
                u, v = w[:i], w[i+L:]; u2, v2 = w2[:j], w2[j+L:]
                if (u + v) == (u2 + v2) or same(u + v, u2 + v2):
                    if same(u + X + X + v, u2 + X + X + v2):
                        return (u, X, v, u2, v2)
    return None
tot = 0; expl = 0; unexplained = []
for n in range(8, 15):
    for cl in cen[str(n)]['nontrivial']:
        # pick a non-reversal pair
        w = cl[0]; w2 = [s for s in cl[1:] if s != w[::-1]][0]
        tot += 1
        e = explained(w, w2)
        if e: expl += 1
        else: unexplained.append((n, w, w2))
    print(f'n={n}: explained so far {expl}/{tot}', flush=True)
print('unexplained:', unexplained[:20])
json.dump(dict(total=tot, explained=expl, unexplained=unexplained), open('isospec_family.json', 'w'), indent=1)
