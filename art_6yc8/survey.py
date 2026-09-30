"""survey.py N — decide every n <= N with omega(tau(n)) >= 3 (the only open case)."""
import sys, time, numpy as np
from sympy import factorint, divisors
from ferris import solve_set, trace_slack
N = int(sys.argv[1]); lo = int(sys.argv[2]) if len(sys.argv) > 2 else 2
shard, nsh = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 1)
tau = np.zeros(N + 1, np.int32)
for d in range(1, N + 1):
    tau[d::d] += 1
ks = np.unique(tau[lo:])
good = [int(k) for k in ks if len(factorint(int(k))) >= 3]
cand = np.nonzero(np.isin(tau, good))[0]
cand = cand[cand >= lo][shard::nsh]
if len(sys.argv) > 6 and sys.argv[6] == "rev": cand = cand[::-1]
print('N', N, 'k values', good, 'candidates', len(cand), flush=True)
if len(sys.argv) > 3 and sys.argv[3] == 'count': sys.exit()
t0 = time.time(); stats = {}
for i, n in enumerate(cand):
    n = int(n); d = divisors(n); sl = trace_slack(n, d)
    if sl > 1e-9:
        stats['trace'] = stats.get('trace', 0) + 1
        if i % 1000 == 0: print(i, n, stats, '%.0fs' % (time.time() - t0), flush=True)
        continue
    r = solve_set(d, 900, 1)
    key = 'cp_none' if r is None else ('TIMEOUT' if r == 'timeout' else 'FOUND')
    stats[key] = stats.get(key, 0) + 1
    if key != 'cp_none':
        print('!!', n, len(d), key, r, flush=True)
    if i % 100 == 0:
        print(i, n, stats, '%.0fs' % (time.time() - t0), flush=True)
print('DONE', N, 'shard', shard, stats, '%.0fs' % (time.time() - t0), flush=True)
