"""bandsfine files for small n (brute) + convert existing RLE -> bandsfine format."""
import numpy as np, re
from math import lcm
BPD = 28

def write_bands(fn, n, L, cnt, tot):
    with open(fn, 'w') as f:
        f.write(f"# n={n} L={L} bpd={BPD}\n")
        for j in range(len(cnt)):
            f.write(f"{j} {int(cnt[j])} {int(tot[j])}\n")

# small n brute
for n in (4, 6, 8):
    L = lcm(*range(1, n+1))
    reach = np.zeros(L, dtype=bool); reach[0] = True
    for k in range(2, n+1):
        w = L//k
        for i in range(w, L):
            if reach[i-w]: reach[i] = True
    d = np.arange(1, L)
    rb = reach[L-d]
    nb = int(np.log10(L)*BPD) + 2
    j = np.minimum((np.log10(d)*BPD).astype(int), nb-1)
    cnt = np.bincount(j[rb], minlength=nb)
    tot = np.bincount(j, minlength=nb)
    write_bands(f'shore/bandsfine_{n}.txt', n, L, cnt, tot)
    print("brute bands", n)

# convert RLE
for n in (9, 12, 14, 16, 18, 20, 22):
    lines = open(f'shore/rle_{n}.txt').read().split('\n')
    m = re.match(r'# lo=(\d+) L=(\d+)', lines[0])
    lo, L = int(m.group(1)), int(m.group(2))
    start = int(lines[1].split()[1])
    runs = np.array([int(x) for x in lines[2:] if x.strip()], dtype=np.int64)
    ends = np.cumsum(runs); starts = ends - runs
    bits = (np.arange(len(runs)) % 2 == 0) if start == 1 else (np.arange(len(runs)) % 2 == 1)
    rs_, re_ = starts[bits], ends[bits]
    d_hi = (L - (lo + rs_)).astype(np.float64)
    d_lo = (L - (lo + re_) + 1).astype(np.float64)
    nb = int(np.log10(L)*BPD) + 2
    cnt = np.zeros(nb); tot = np.zeros(nb)
    edges = 10**(np.arange(nb+1)/BPD)
    span_max = L - lo
    for j in range(nb):
        a, b = edges[j], min(edges[j+1]-1, span_max)
        if a > span_max: break
        ov = np.maximum(0, np.minimum(d_hi, b) - np.maximum(d_lo, a) + 1)
        cnt[j] = ov.sum()
        tot[j] = max(int(b) - int(a) + 1, 1)
    write_bands(f'shore/bandsfine_{n}.txt', n, L, cnt, tot)
    print("rle bands", n)
