"""MO 513787: arithmetic progressions of consecutive sums of two squares.

Block-sieve S = {x^2+y^2} up to LIMIT, then:
  (a) among consecutive elements s_n < s_{n+1} < ... find equal-gap runs
      (vectorized RLE); first occurrence per length + overall record.
  (b) for each l, smallest k with 1, 1+k, ..., 1+(l-1)k all in S.
"""
import numpy as np
import pickle
import sys
import time

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 10**9
BLOCK = 1 << 27
CARRY = 256

t0 = time.time()


def mark_block(lo, hi):
    arr = np.zeros(hi - lo, dtype=np.uint8)
    xmax = int(np.sqrt(hi / 2)) + 2
    for x in range(0, xmax + 1):
        x2 = x * x
        if 2 * x2 >= hi:
            break
        ylo = x
        if lo > 2 * x2:
            ylo = max(x, int(np.sqrt(max(lo - x2, 0))) - 2)
        yhi = int(np.sqrt(hi - 1 - x2))
        if yhi < ylo:
            continue
        y = np.arange(ylo, yhi + 1, dtype=np.int64)
        pos = x2 + y * y
        sel = (pos >= lo) & (pos < hi)
        arr[pos[sel] - lo] = 1
    return arr


first_by_len = {}   # run length L (>=3) -> (start_value, gap)
best_len = 0
best_at = None
carry = np.empty(0, dtype=np.int64)
packed = np.zeros((LIMIT + 7) // 8, dtype=np.uint8)

lo = 0
while lo < LIMIT:
    hi = min(lo + BLOCK, LIMIT)
    arr = mark_block(lo, hi)
    pb = np.packbits(arr, bitorder='little')
    packed[lo // 8: lo // 8 + len(pb)] |= pb
    vals = np.flatnonzero(arr).astype(np.int64) + lo
    del arr, pb
    ncarry = len(carry)
    v = np.concatenate([carry, vals]) if ncarry else vals
    if len(v) >= 3:
        d = np.diff(v)                       # gaps
        e = d[1:] == d[:-1]                  # equal consecutive gaps
        # RLE of e
        if len(e):
            change = np.flatnonzero(e[1:] != e[:-1]) + 1
            starts = np.concatenate([[0], change])
            ends = np.concatenate([change, [len(e)]])
            for s, epos in zip(starts.tolist(), ends.tolist()):
                if not e[s]:
                    continue
                L = (epos - s) + 2           # elements in the run
                run_end_idx = epos + 1       # index in v of last element
                if run_end_idx < ncarry:     # fully inside carry: counted
                    continue
                start_val = int(v[s])
                gap = int(d[s])
                if L > 190:
                    raise RuntimeError("increase CARRY")
                if L > best_len:
                    best_len = L
                    best_at = (start_val, gap)
                for LL in range(3, L + 1):
                    if LL not in first_by_len:
                        # start of the length-LL prefix run is start_val
                        first_by_len[LL] = (start_val, gap)
    carry = v[-CARRY:].copy()
    lo = hi
    if (lo // BLOCK) % 2 == 0 or lo >= LIMIT:
        print(f"to {hi:,}: best {best_len} at {best_at}, "
              f"{time.time()-t0:.0f}s", flush=True)

print("first occurrence by length (start, gap):")
for L in sorted(first_by_len):
    print(L, first_by_len[L])


def in_S(n):
    return (packed[n >> 3] >> (n & 7)) & 1


krec = {}
for k in range(1, 2 * 10**6):
    l = 1
    while True:
        t = 1 + l * k
        if t >= LIMIT or not in_S(t):
            break
        l += 1
    for LL in range(2, l + 1):
        if LL not in krec:
            krec[LL] = k
print("part (b) smallest k per l:")
for LL in sorted(krec):
    print(LL, krec[LL])

pickle.dump({"first_by_len": first_by_len, "best": (best_len, best_at),
             "krec": krec, "limit": LIMIT},
            open("twosq_results.pkl", "wb"))
print("total", time.time() - t0)
