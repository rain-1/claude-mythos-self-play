"""gaps.py — consecutive prime gaps to N: the pair field (g_n, g_{n+1}), the lag-one correlation, the conditional
mean E[g_{n+1} | g_n], and a test of MO 515297's 'adaptive window' bound for EVERY integer x <= N:
    g_x <= ceil(2 e^{-gamma} [ (ln(x/d_x))^2 + 2 ]),  d_x = x - p_n (largest prime below x), g_x = p_{n+1} - x.
    python3 gaps.py N
"""
import sys, json, time, numpy as np
N = int(float(sys.argv[1]))
t0 = time.time()
# odd-only sieve
M = (N - 1) // 2 + 1                      # index i <-> number 2i+1
s = np.ones(M, dtype=bool); s[0] = False   # 1 is not prime
r = int(N ** 0.5)
for p in range(3, r + 1, 2):
    if s[(p - 1) // 2]:
        s[(p * p - 1) // 2::p] = False
primes = np.concatenate(([2], 2 * np.nonzero(s)[0].astype(np.int64) + 1))
del s
print('primes', len(primes), f'{time.time()-t0:.0f}s', flush=True)
g = np.diff(primes).astype(np.int32)      # g[n] = p_{n+1} - p_n
G = int(g.max())
# pair histogram (g_n, g_{n+1})
K = G + 1
pair = np.bincount(g[:-1].astype(np.int64) * K + g[1:], minlength=K * K).reshape(K, K)
marg = np.bincount(g, minlength=K)
a, b = g[:-1].astype(np.float64), g[1:].astype(np.float64)
corr = float(np.corrcoef(a, b)[0, 1])
# conditional mean of the next gap given this one
cm = np.where(pair.sum(1) > 0, (pair * np.arange(K)[None, :]).sum(1) / np.maximum(pair.sum(1), 1), np.nan)
print('max gap', G, 'corr', corr, 'mean gap', g.mean(), f'{time.time()-t0:.0f}s', flush=True)
np.savez_compressed('cache/gaps_pairs.npz', pair=pair, marg=marg, cm=cm, corr=corr, N=N, nprimes=len(primes))
# ---- MO 515297 bound for every x: loop over d = x - p_n (1..gap-1) and x = p_{n+1} (d = gap, g_x = 0 trivially)
gam = 0.5772156649015329
c = 2 * np.exp(-gam)
worst = (1e9, None)          # min slack (bound - g_x)
viol = []
for d in range(1, G):
    sel = np.nonzero(g > d)[0]
    if len(sel) == 0: break
    x = primes[sel] + d
    gx = g[sel] - d
    bound = np.ceil(c * (np.log(x / d) ** 2 + 2))
    slack = bound - gx
    j = int(np.argmin(slack))
    if slack[j] < worst[0]:
        worst = (float(slack[j]), dict(x=int(x[j]), p=int(primes[sel[j]]), d=d, g=int(gx[j]), bound=float(bound[j])))
    bad = np.nonzero(slack < 0)[0]
    for k in bad[:5]:
        viol.append(dict(x=int(x[k]), p=int(primes[sel[k]]), d=d, g=int(gx[k]), bound=float(bound[k])))
    if d % 50 == 0: print('d', d, 'tested', len(sel), 'min slack so far', worst[0], f'{time.time()-t0:.0f}s', flush=True)
res = dict(N=N, nprimes=int(len(primes)), max_gap=G, corr_lag1=corr, mean_gap=float(g.mean()), min_slack=worst[0], min_slack_at=worst[1],
           violations=viol[:50], n_violations=len(viol),
           cond_mean=[dict(g=int(k), E_next=float(cm[k]), count=int(pair.sum(1)[k])) for k in range(1, K) if pair.sum(1)[k] >= 1000])
json.dump(res, open('cert_gaps.json', 'w'), indent=1)
print('done', json.dumps({k: v for k, v in res.items() if k not in ('cond_mean', 'violations')}), f'{time.time()-t0:.0f}s')
