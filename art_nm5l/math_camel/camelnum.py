"""n is a CAMEL NUMBER if n is a sum of distinct proper divisors of n+1 (some number of sons)."""
import sys
M = int(sys.argv[1])
divs = [[] for _ in range(M + 2)]
for d in range(1, (M + 1) // 2 + 1):
    for m in range(2 * d, M + 2, d): divs[m].append(d)
cnt = 0; non = []; marks = {10**j for j in range(1, 8)}
bykmin = {}
for N in range(2, M + 2):
    t = N - 1; ds = divs[N]
    if sum(ds) < t: ok = False
    else:
        bits = 1
        for d in ds: bits |= bits << d
        ok = (bits >> t) & 1
    if ok: cnt += 1
    if (N - 1) in marks: print(N - 1, cnt, cnt / (N - 1), flush=True)
print('first camel numbers', [N-1 for N in range(2, 80) if (lambda ds,t: (__import__("functools").reduce(lambda b,d: b|(b<<d), ds, 1)>>t)&1)(divs[N], N-1)])
