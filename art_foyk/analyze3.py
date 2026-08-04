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

# m=4, c=2 sector: q(a,b) with a+b=2k-4. Print q/|perms| * (k-1)^2(k-2)^2(k-3)^2 etc.
for k in (10,12):
    print(f"== k={k}, m=4, c=2 sector ==  (a,b): q, and q*(k-1)^2(k-3)^2/perms, q*(k-1)(k-2)^2(k-3)/perms")
    for nu,q in sorted(data[(k,4)].items()):
        if len(nu)!=2: continue
        a,b = nu
        D1 = Fraction((k-1)**2*(k-3)**2); D2 = Fraction((k-1)*(k-2)**2*(k-3))
        print(f"  ({a:2d},{b:2d}): {q}   A1={q*D1/nperms(nu)}  A2={q*D2/nperms(nu)}")
