"""survival.py — the sticky law of the mushroom: survival function of cap sojourns of free orbits."""
import numpy as np, json, time, sys
sys.path.insert(0, '.')
import mushroom as mb
rng = np.random.default_rng(7)
n, nb = int(sys.argv[1]), int(sys.argv[2])
rr = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
out = sys.argv[5] if len(sys.argv) > 5 else 'survival.json'
allL = []
t0 = time.time()
for chunk in range(int(sys.argv[3])):
    P = np.stack([rng.uniform(-rr, rr, n), rng.uniform(-1.0, 0.0, n)], 1)
    a = rng.uniform(0, 2 * np.pi, n); V = np.stack([np.cos(a), np.sin(a)], 1)
    segs, incap = mb.propagate(P, V, nb, 1.0, rr, 1.0)
    L = np.hypot(segs[..., 2] - segs[..., 0], segs[..., 3] - segs[..., 1])
    allL.append(mb.sojourn_lengths_fast(incap, L))
    print(chunk, time.time() - t0, flush=True)
L = np.concatenate(allL); L.sort()
qs = np.geomspace(1, L.max(), 60)
surv = [(float(q), float((L > q).mean())) for q in qs]
json.dump(dict(n_sojourns=int(len(L)), mean=float(L.mean()), max=float(L.max()), survival=surv, total_time=float(nb * n * int(sys.argv[3])), r=rr), open(out, 'w'), indent=1)
for q, s in surv[::6]:
    print(f'{q:9.2f} {s:.3e}')
# local slopes
lq = np.log([q for q, s in surv if s > 0]); ls = np.log([s for q, s in surv if s > 0])
for i in range(6, len(lq) - 6, 6):
    sl = np.polyfit(lq[i - 6:i + 6], ls[i - 6:i + 6], 1)[0]
    print(f'slope near t={np.exp(lq[i]):.1f}: {sl:.2f}')
