"""tide_data.py — shares of each planar signature among n <= N on a log grid (for the tide chart)."""
import json, numpy as np, time
from planar_race import count_planar
rows = []
t0 = time.time()
for k in range(24, 24 * 12 + 1, 2):   # 10^(k/24), k step 2 -> 12 per decade
    N = int(round(10 ** (k / 24)))
    P, comp = count_planar(N)
    rows.append(dict(N=N, P=P, **comp))
    print(f'{N} P/N={P / N:.5f} ({time.time() - t0:.0f}s)', flush=True)
    json.dump(rows, open('tide_data.json', 'w'))
