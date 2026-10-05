# forward occupation probabilities of the K=3 piles walk from (n,n,n); saves visits[a,b,c]
import numpy as np, sys
n = int(sys.argv[1]); A = [int(v) for v in sys.argv[2].split(',')] if len(sys.argv) > 2 else [n, n, n]
M = max(A) + 1
p = np.zeros((M, M, M)); p[tuple(A)] = 1.0
vis = np.zeros_like(p); final = np.zeros((3, M))
for s in range(sum(A), 0, -1):
    # all states with a+b+c = s
    idx = [(a, b, s - a - b) for a in range(min(s, M - 1) + 1) for b in range(min(s - a, M - 1) + 1) if 0 <= s - a - b < M]
    for a, b, c in idx:
        q = p[a, b, c]
        if q == 0: continue
        vis[a, b, c] += q
        nz = [i for i, v in enumerate((a, b, c)) if v > 0]
        if len(nz) == 1:
            final[nz[0], (a, b, c)[nz[0]]] += q; continue
        for i in nz:
            t = [a, b, c]; t[i] -= 1; p[tuple(t)] += q / len(nz)
np.save(f'flow_{"_".join(map(str,A))}.npy', vis); np.save(f'final_{"_".join(map(str,A))}.npy', final)
print('E final', sum(final[i] @ np.arange(M) for i in range(3)), 'P(end) mass', final.sum())
