"""Exact enumeration of E[T] for n=1..5 and worst-case max T; verify poster's values."""
import numpy as np, json
from fractions import Fraction
from sort_lib import batch_T

results = {}
for n in range(1, 5):
    NN = n * n
    codes = np.arange(1 << NN, dtype=np.uint64)
    T = batch_T(codes, n)
    s = int(T.sum())
    mu = Fraction(s, 1 << NN)
    results[n] = dict(sum=s, denom=1 << NN, mu=str(mu), mu_f=float(mu),
                      maxT=int(T.max()),
                      dist={int(t): int((T == t).sum()) for t in np.unique(T)})
    print(n, mu, float(mu), "maxT", T.max())

# poster's claims
assert results[1]['mu'] == '1'
assert results[2]['mu'] == '21/16'
assert results[3]['mu'] == '105/64'
assert results[4]['mu'] == '125387/65536'
assert results[3]['maxT'] == 3 and results[4]['maxT'] == 5   # 2n-3
print("POSTER VALUES n=1..4 VERIFIED; worst case 2n-3 verified n=3,4")

# n=5 exhaustive in chunks (2^25 = 33.5M)
n = 5
NN = 25
tot = 0
maxT = 0
dist = {}
CH = 1 << 21
for lo in range(0, 1 << NN, CH):
    codes = np.arange(lo, lo + CH, dtype=np.uint64)
    T = batch_T(codes, n)
    tot += int(T.sum())
    maxT = max(maxT, int(T.max()))
    for t in np.unique(T):
        dist[int(t)] = dist.get(int(t), 0) + int((T == t).sum())
    print("chunk", lo >> 21, "/16 done", flush=True)
mu5 = Fraction(tot, 1 << NN)
results[5] = dict(sum=tot, denom=1 << NN, mu=str(mu5), mu_f=float(mu5), maxT=maxT, dist=dist)
print("n=5 EXACT mu =", mu5, "=", float(mu5), " maxT =", maxT, " (2n-3 =", 2 * n - 3, ")")
json.dump(results, open("exact_small.json", "w"), indent=1)
