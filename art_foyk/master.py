"""Master formula: q_{k,m}(nu) = sum_lam q_{m,m}(lam) * sum_{distinct perms n of nu}
   [ sum_{G: 0<=G_i<=n_i-a_i, sum G = k-m} prod_i C(G_i+a_i-1,a_i-1)*C(n_i-a_i-G_i+a_i-1,a_i-1) ] / C(k-1,m-1)^2 """
import glob, itertools
from fractions import Fraction
from math import comb, factorial
from collections import defaultdict

data = defaultdict(dict)
for f in glob.glob('qdata/q_*.txt'):
    for line in open(f):
        p = line.split()
        if len(p)!=4: continue
        data[(int(p[0]),int(p[1]))][tuple(int(x) for x in p[2].split(','))] = Fraction(p[3])
# add tiny-m base cases from python brute (m=2..6 exist at k=m in data? need q_{m,m})
import subprocess
for m in (2,3,4,5,6):
    if (m,m) not in data:
        out = subprocess.run(['python3','wheels_brute.py',str(m),str(m)],capture_output=True,text=True)
        for line in out.stdout.strip().split('\n'):
            m2 = __import__("re").match(r"(\d+) (\d+) \(([^)]*)\,?\) (\S+)", line)
            nu = tuple(int(x) for x in m2.group(3).replace(" ","").split(",") if x)
            data[(m,m)][nu] = Fraction(m2.group(4))

def gap_weight_sum(avec, nvec, total):
    """sum over G_i in [0, n_i-a_i], sum G = total of prod C(G_i+a_i-1,a_i-1)C(n_i-G_i-a_i+a_i-1,a_i-1)."""
    # DP over cycles
    dp = {0: Fraction(1)}
    for a, n in zip(avec, nvec):
        nd = defaultdict(Fraction)
        for s, w in dp.items():
            for G in range(0, n-a+1):
                H = n-a-G
                nd[s+G] += w * comb(G+a-1, a-1) * comb(H+a-1, a-1)
        dp = nd
    return dp.get(total, Fraction(0))

def master_q(k, m, nu):
    pm = data[(m,m)]
    denom = Fraction(comb(k-1, m-1))**2
    tot = Fraction(0)
    for lam, plam in pm.items():
        if len(lam) != len(nu): continue
        avec = list(lam)
        for n in set(itertools.permutations(nu)):
            if any(nn < aa for nn, aa in zip(n, avec)): continue
            tot += plam * gap_weight_sum(avec, n, k-m) / denom
    return tot

# verify against everything with m<=6, all k in data
bad = 0; tested = 0
for (k,m) in sorted(data):
    if m > 6 or k == m: continue
    for nu, q in data[(k,m)].items():
        pred = master_q(k, m, nu)
        tested += 1
        if pred != q:
            bad += 1
            if bad < 8: print("MISMATCH", k, m, nu, q, pred)
print(f"tested {tested} values (m<=6, k up to 12): mismatches = {bad}")
