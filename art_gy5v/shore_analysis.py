"""Parse RLE shore dumps -> per-n log-band densities; verify champions exactly."""
import numpy as np, re, os
from fractions import Fraction as F
from math import lcm

champions = {
 9:  [5,6,7,7,8,9,9],
 12: [5,5,8,9,11,11,11,11],
 14: [7,8,9,9,11,11,11,12,13,13],
 16: [4,9,9,11,13,13,13,13,15,16],
 18: [4,5,9,11,11,13,16,17,17],
 20: [11,11,11,11,13,14,15,18,19,19,19,19,19,19,20],
 22: [5,11,11,13,13,13,14,17,17,19,19,21,22],
 24: [5,11,16,17,17,17,17,17,17,17,19,21,21,23,23],
 25: [9,10,11,13,13,13,19,19,19,21,21,22,23,23,24,25],
 28: [9,10,11,13,13,13,19,19,19,21,21,22,23,23,24,25],
}
gaps = {9:1, 12:7, 14:5, 16:7, 18:7, 20:68, 22:48, 24:39, 25:34, 28:102}
for n, ch in champions.items():
    L = lcm(*range(1, n+1))
    s = sum(F(1, k) for k in ch)
    gap = 1 - s
    assert gap == F(gaps[n], L), (n, gap, F(gaps[n], L))
    print(f"n={n:2d} gap = {gap} = 1/{float(1/gap):.6g}  champion 1-sum verified exactly")

# full record table (brute small n + DP)
records = {2:(2,1),3:(6,1),4:(12,1),5:(60,1),6:(60,1),7:(420,2),8:(840,4),9:(2520,1),10:(2520,1),
           11:(27720,7),12:(27720,7),13:(360360,5),14:(360360,5),15:(360360,5),16:(720720,7),
           17:(12252240,7),18:(12252240,7),19:(232792560,110),20:(232792560,68),21:(232792560,68),
           22:(232792560,48),23:(5354228880,39),24:(5354228880,39),25:(26771144400,34),
           26:(26771144400,34),27:(80313433200,102),28:(80313433200,102)}
print("\nn, gap g(n), -log10 g(n), -log10(1/lcm)")
tab = []
for n,(L,g) in records.items():
    tab.append((n, np.log10(L/g), np.log10(L)))
    print(n, f"{g}/{L}", f"{np.log10(L/g):.3f}", f"{np.log10(L):.3f}")
np.save('shore_records.npy', np.array(tab))

# band densities from RLE
for n in (9, 12, 14, 16, 18, 20, 22, 24):
    fn = f'shore/rle_{n}.txt'
    lines = open(fn).read().split('\n')
    m = re.match(r'# lo=(\d+) L=(\d+)', lines[0])
    lo, L = int(m.group(1)), int(m.group(2))
    start = int(lines[1].split()[1])
    runs = np.array([int(x) for x in lines[2:] if x.strip()], dtype=np.int64)
    # values: bit b at positions [lo + cum, ...) alternating starting with `start`
    ends = np.cumsum(runs)
    starts = ends - runs
    bits = (np.arange(len(runs)) % 2 == 0) if start == 1 else (np.arange(len(runs)) % 2 == 1)
    # distance to L: d = L - i for i in [lo+starts, lo+ends)
    # reachable runs only
    rs, re_ = starts[bits], ends[bits]
    d_hi = L - (lo + rs)      # farthest distance in run (exclusive of...)
    d_lo = L - (lo + re_) + 1 # nearest distance
    # log10 band counts: band j = d in [10^j, 10^(j+1))
    NB = 12
    cnt = np.zeros(NB)
    for j in range(NB):
        a, b = 10.0**j, 10.0**(j+1)
        ov = np.maximum(0, np.minimum(d_hi, b-1) - np.maximum(d_lo, a) + 1)
        cnt[j] = ov.sum()
    tot = np.array([min(10.0**(j+1)-1, L-lo) - 10.0**j + 1 if 10.0**j <= L-lo else 0 for j in range(NB)])
    with np.errstate(divide='ignore', invalid='ignore'):
        frac = np.where(tot > 0, cnt/np.maximum(tot, 1), np.nan)
    print(n, "band fill fraction (d=1..):", np.array2string(frac[:10], precision=4))
    np.save(f'shore/bands_{n}.npy', np.stack([cnt, tot]))
