"""Exact/analytic census for the Sunflower of Fifths: which family is nearest at each seed,
where the hand-overs happen (analytic vs KD-tree), and the musical name of each family.
Writes census_table.md"""
import math, numpy as np
from scipy.spatial import cKDTree
from sunflower import ALPHA, cf, convergents, intermediates, frac_dist

a = cf(ALPHA - 1, 16)
conv = [q for p, q in convergents(a)]
inter = intermediates(a)
cands = sorted(set([m for m in inter if m <= 40000]))
names = {1: 'fifth (3:2)', 2: 'whole tone 9:8', 3: '', 5: '5-tone (slendro-like)', 7: '7-tone', 12: '12-TET / Pythagorean comma',
         17: '17-TET', 29: '29-TET', 41: '41-TET', 53: '53-TET (Mercator)', 94: '94-TET', 147: '', 200: '', 253: '', 306: '306-TET',
         359: '', 665: '665-TET (Satanic comma)', 971: '', 15601: '15601-TET'}


def nn_analytic(k):
    best = None
    for m in cands:
        if m > k: break
        d2 = (2 * math.pi * math.sqrt(k) * frac_dist(m * ALPHA)) ** 2 + m * m / (4 * k)
        if best is None or d2 < best[0]:
            best = (d2, m)
    return best[1]


# analytic hand-over indices up to 2e6 (bisection on each pair transition is overkill: scan log-spaced then refine)
N_AN = 2_000_000
ks = np.unique(np.round(np.geomspace(2, N_AN, 4000)).astype(int))
fam = [nn_analytic(int(k)) for k in ks]
trans_an = []
for i in range(1, len(ks)):
    if fam[i] != fam[i - 1]:
        lo, hi = int(ks[i - 1]), int(ks[i])
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if nn_analytic(mid) == fam[i]: hi = mid
            else: lo = mid
        trans_an.append((hi, fam[i]))

# KD-tree measured hand-overs up to 3e5
N_M = 300_000
k = np.arange(N_M); th = 2 * np.pi * np.mod(k * ALPHA, 1.0); r = np.sqrt(k)
xy = np.c_[r * np.cos(th), r * np.sin(th)]
d, idx = cKDTree(xy).query(xy, k=3)
dk1 = np.abs(idx[:, 1] - k); dk2 = np.abs(idx[:, 2] - k)
# a hand-over = first k after which the new value holds for >= 90% of the next 300 seeds
trans_m = []
prev = None
for kk in range(2, N_M - 300):
    v = int(dk1[kk])
    if v != prev and np.mean(dk1[kk:kk + 300] == v) >= 0.9:
        trans_m.append((kk, v)); prev = v
# opposed families (second neighbour excluding multiples of the first) per nearest-family era
opp = {}
for (k0, v), (k1, _) in zip(trans_m, trans_m[1:] + [(N_M - 300, None)]):
    sl = slice(k0, k1)
    d2 = dk2[sl]; d1 = dk1[sl]
    m = (d2 % np.maximum(d1, 1)) != 0
    u, c = np.unique(d2[m], return_counts=True)
    top = [int(x) for x in u[np.argsort(-c)][:4]]
    opp[v] = top

lines = ['# Census — The Sunflower of Fifths', '',
         'alpha = log2(3) = %.12f; continued fraction of alpha-1: %s' % (ALPHA, a),
         '', 'convergent denominators: %s' % conv[:10], 'intermediate (semiconvergent) denominators: %s' % [m for m in inter if m < 20000], '',
         '## Fifth error of each family (1200*||m alpha|| cents = how far m fifths miss a whole number of octaves)', '',
         '| m | cents | record? | name |', '|---|---|---|---|']
best = 1.0
for m in cands:
    e = frac_dist(m * ALPHA)
    rec = e < best
    if rec: best = e
    lines.append('| %d | %.4f | %s | %s |' % (m, 1200 * e, 'yes' if rec else '', names.get(m, '')))
lines += ['', '## Nearest-family hand-overs: analytic minimiser of d(m,k)^2 = (2 pi sqrt(k) ||m alpha||)^2 + m^2/(4k)', '',
          '| takes over at seed k | family m | radius sqrt(k) |', '|---|---|---|']
for kk, v in trans_an:
    lines.append('| %d | %d | %.1f |' % (kk, v, math.sqrt(kk)))
lines += ['', '## Nearest-family hand-overs measured by KD-tree on %d seeds (first k where the new value holds for 90%% of the next 300 seeds)' % N_M, '',
          '| seed k | family m | radius | opposed families seen in this era (2nd neighbour, non-multiples) |', '|---|---|---|---|']
for kk, v in trans_m:
    lines.append('| %d | %d | %.1f | %s |' % (kk, v, math.sqrt(kk), opp.get(v)))
agree = all(any(abs(kk - ka) <= max(3, 0.02 * kk) and v == va for ka, va in trans_an) for kk, v in trans_m[1:])
lines += ['', 'analytic and measured hand-overs agree (within 2%% in k): **%s**' % agree]
open('census_table.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
