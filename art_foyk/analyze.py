import glob, re
from fractions import Fraction
from math import factorial
from collections import defaultdict

data = defaultdict(dict)   # (k,m) -> {nu: q}
for f in glob.glob('qdata/q_*.txt'):
    for line in open(f):
        parts = line.split()
        if len(parts) != 4: continue
        k, m = int(parts[0]), int(parts[1])
        nu = tuple(int(x) for x in parts[2].split(','))
        data[(k,m)][nu] = Fraction(parts[3])

def nperms(nu):
    from collections import Counter
    c = Counter(nu); r = factorial(len(nu))
    for v in c.values(): r //= factorial(v)
    return r

# (a) support: which cycle-counts c occur per (k,m)?
print("== cycle-count support ==")
for (k,m) in sorted(data):
    cs = sorted(set(len(nu) for nu in data[(k,m)]))
    print(f"k={k} m={m}: c in {cs}")

# (b) m=3 closed-form verification against ALL data
print("\n== m=3 law: q = 2*perms*(bc - t(t+1))/((k-1)^2(k-2)^2), t=max(0,k-2-a); Pr[c=1]=1/2 ==")
allok = True
for (k,m) in sorted(data):
    if m != 3: continue
    tab = data[(k,m)]
    N = 2*k-3
    # single cycle
    ok1 = tab.get((N,), 0) == Fraction(1,2)
    D = Fraction((k-1)**2 * (k-2)**2)
    bad = []
    tot = Fraction(0)
    for nu, q in tab.items():
        if len(nu) == 1: tot += q; continue
        a,b,c = nu
        t = max(0, k-2-a)
        pred = Fraction(2*nperms(nu)*(b*c - t*(t+1)), 1)/D
        tot += q
        if pred != q: bad.append((nu, q, pred))
    print(f"k={k}: single-cycle=1/2 {ok1}, c=3 mismatches: {len(bad)}, total={tot}")
    if bad: allok=False; print('   ', bad[:5])
print("M=3 LAW HOLDS FOR ALL k IN DATA:", allok)
