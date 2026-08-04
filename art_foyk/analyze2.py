import glob
from fractions import Fraction
from math import factorial
from collections import defaultdict, Counter

data = defaultdict(dict)
for f in glob.glob('qdata/q_*.txt'):
    for line in open(f):
        p = line.split()
        if len(p)!=4: continue
        data[(int(p[0]),int(p[1]))][tuple(int(x) for x in p[2].split(','))] = Fraction(p[3])

def nperms(nu):
    c = Counter(nu); r = factorial(len(nu))
    for v in c.values(): r //= factorial(v)
    return r

print("== Pr[c cycles] by (k,m) ==")
for (k,m) in sorted(data):
    if m > 6: continue
    byc = defaultdict(Fraction)
    for nu,q in data[(k,m)].items(): byc[len(nu)] += q
    print(f"k={k:2d} m={m}: " + "  ".join(f"c={c}:{byc[c]}" for c in sorted(byc)))
