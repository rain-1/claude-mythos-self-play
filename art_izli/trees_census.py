"""Census of polynomial dessins (bicolored plane trees) with n edges.

Model: edges = {0..n-1}; sigma0 = rotation around black vertices, sigma1
around white; polynomial dessin <=> sigma0*sigma1 = c (one face), tree <=>
c(sigma0)+c(sigma1) = n+1.  Fix c = (0 1 ... n-1); classes up to conjugation
by the centralizer of c, which is <c>.  Passport = (black cycle type, white
cycle type).
"""
import itertools, json
from collections import defaultdict

def cycles(p):
    n = len(p); seen = [False]*n; out = []
    for i in range(n):
        if not seen[i]:
            cyc = []; j = i
            while not seen[j]:
                seen[j] = True; cyc.append(j); j = p[j]
            out.append(tuple(cyc))
    return out

def compose(p, q):          # (p*q)(i) = p[q[i]]
    return tuple(p[q[i]] for i in range(len(p)))

def conj_by_ck(p, k, n):    # c^k p c^-k  where c(i) = i+1 mod n
    return tuple(((p[(i - k) % n]) + k) % n for i in range(n))

def census(n):
    c = tuple((i + 1) % n for i in range(n))
    cinv = tuple((i - 1) % n for i in range(n))
    reps = {}
    for perm in itertools.permutations(range(n)):
        s0 = perm
        s1 = compose(cinv, s0)          # wait: need s0*s1 = c  => s1 = s0^-1 * c
        # invert s0
        inv = [0]*n
        for i, v in enumerate(s0): inv[v] = i
        s1 = compose(tuple(inv), c)
        c0 = cycles(s0); c1 = cycles(s1)
        if len(c0) + len(c1) != n + 1:
            continue
        # canonical form under conjugation by c^k
        can = min((conj_by_ck(s0, k, n), conj_by_ck(s1, k, n)) for k in range(n))
        if can in reps: continue
        lam = tuple(sorted((len(x) for x in c0), reverse=True))
        mu  = tuple(sorted((len(x) for x in c1), reverse=True))
        reps[can] = dict(sigma0=s0, sigma1=s1, passport=(lam, mu))
    return reps

if __name__ == '__main__':
    allreps = {}
    for n in range(1, 8):
        reps = census(n)
        bypass = defaultdict(int)
        for v in reps.values():
            bypass[v['passport']] += 1
        print(f"n={n}: {len(reps)} dessins, {len(bypass)} passports")
        for p, k in sorted(bypass.items()):
            print(f"   {p[0]} | {p[1]} : {k}")
        allreps[n] = [dict(sigma0=list(v['sigma0']), sigma1=list(v['sigma1']),
                           passport=[list(v['passport'][0]), list(v['passport'][1])])
                      for v in reps.values()]
    json.dump(allreps, open('trees_census.json', 'w'))
