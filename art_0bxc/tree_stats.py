"""tree_stats.py — statistics of the merger tree of shocks (the picture's genealogy).
Mergers: an interval of stuck particles at row r that contains >= 2 intervals of row r-1.
Mass ratio of a merger: smaller / larger of the two heaviest parents."""
import numpy as np, json, sys
from burgers import velocity_field, hull_row

def march(n=4096, seed=1, T=60.0, t_min=0.004, rows=3000, amp=0.018, n_index=0.0):
    margin = n // 4
    u, phi = velocity_field(n, seed, n_index, None, amp=amp)
    idx = np.arange(-margin, n + margin); q = idx / n; PH = phi[idx % n]
    ts = np.geomspace(t_min, T, rows)
    prev = []   # list of (a,b) intervals
    mergers = []; births = 0
    counts = []
    for t in ts:
        v = hull_row(q, PH, t)
        a, b = v[:-1], v[1:]; g = (b - a) > 1; a, b = a[g], b[g]
        ins = (q[a] >= 0) & (q[b] <= 1)
        cur = list(zip(a[ins], b[ins]))
        counts.append((t, len(cur)))
        if prev:
            pa = np.array([p[0] for p in prev]); pb = np.array([p[1] for p in prev])
            for (x, y) in cur:
                inside = (pa >= x) & (pb <= y)
                k = inside.sum()
                if k >= 2:
                    ms = np.sort(pb[inside] - pa[inside])[::-1]
                    mergers.append((t, float(ms[1] / ms[0]), int(k), int(y - x)))
                elif k == 0:
                    births += 1
        prev = cur
    return np.array(counts), np.array(mergers), births

if __name__ == '__main__':
    out = {}
    allr = []
    for seed in [1, 2, 3, 4]:
        counts, mg, births = march(seed=seed)
        r = mg[:, 1]
        allr.append(mg)
        print(f'seed {seed}: mergers {len(mg)} births {births}  median ratio {np.median(r):.3f}  mean {r.mean():.3f}  P(r<0.1)={np.mean(r<0.1):.3f}  P(r>0.5)={np.mean(r>0.5):.3f}')
    mg = np.concatenate(allr)
    r = mg[:, 1]; t = mg[:, 0]
    # self-similarity: ratio distribution by time decade
    for lo, hi in [(0.01, 0.1), (0.1, 1), (1, 10), (10, 60)]:
        s = (t >= lo) & (t < hi)
        if s.sum() > 20:
            print(f't in [{lo},{hi}): n={s.sum()} median r={np.median(r[s]):.3f} mean={r[s].mean():.3f} P(r<0.1)={np.mean(r[s]<0.1):.3f}')
    h, e = np.histogram(r, bins=np.linspace(0, 1, 11))
    print('histogram of r (10 bins):', h.tolist())
    # cumulative test against P(r) = c r^-1/2 (i.e. F(r) = sqrt(r)) and uniform
    rs = np.sort(r); F = np.arange(1, len(rs) + 1) / len(rs)
    for name, Fth in [('sqrt', np.sqrt(rs)), ('uniform', rs), ('r^0.3', rs ** 0.3)]:
        print(name, 'KS distance', float(np.max(np.abs(F - Fth))))
    json.dump(dict(n_mergers=int(len(r)), median=float(np.median(r)), mean=float(r.mean()), hist=h.tolist(),
                   frac_multi=float(np.mean(mg[:, 2] > 2))), open('tree_stats.json', 'w'), indent=1)
