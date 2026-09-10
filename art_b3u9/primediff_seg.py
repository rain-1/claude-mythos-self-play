"""primediff_seg.py — streaming hunt for the least zero of the signed n-th difference of the primes,
for n in NS, over primes up to LIM (segmented sieve, constant memory).  Records every zero found."""
import numpy as np, json, sys, time

LIM = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10_000_000_000
NS = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [25, 27, 28, 29, 30]
SEG = 200_000_000
t0 = time.time()
root = int(LIM ** 0.5) + 1
small = np.ones(root // 2 + 1, dtype=bool); small[0] = False
for i in range(1, int(root ** 0.5) // 2 + 1):
    if small[i]:
        p = 2 * i + 1; small[p * p // 2::p] = False
sp = 2 * np.nonzero(small)[0] + 1          # odd primes <= root
nmax = max(NS)
tail = np.array([2], dtype=np.int64)        # last nmax primes carried between segments
count = 1                                    # primes seen so far (p_1 = 2)
found = {n: [] for n in NS}
lo = 3
while lo < LIM:
    hi = min(LIM, lo + SEG)
    # odd numbers lo..hi-1  (lo odd)
    m = (hi - lo + 1) // 2
    seg = np.ones(m, dtype=bool)
    for p in sp:
        if p * p >= hi:
            break
        start = max(p * p, ((lo + p - 1) // p) * p)
        if start % 2 == 0:
            start += p
        seg[(start - lo) // 2::p] = False
    primes = lo + 2 * np.nonzero(seg)[0]
    buf = np.concatenate([tail, primes]).astype(np.int64)
    base = count - len(tail)                 # index (0-based) of buf[0] in the prime sequence
    D = buf.copy()
    for n in range(1, nmax + 1):
        D = D[1:] - D[:-1]
        if n in NS:
            z = np.nonzero(D == 0)[0]
            for zi in z:
                j = base + int(zi) + 1        # 1-based j
                if not found[n] or j > found[n][-1]:
                    found[n].append(j)
                    print(f'n={n} zero at j={j} (prime {buf[zi]})', flush=True)
    count += len(primes)
    tail = buf[-nmax:]
    lo = hi if hi % 2 == 1 else hi + 1
    if (lo // SEG) % 5 == 0:
        print(f'  up to {lo:.3e}, {count} primes, {time.time()-t0:.0f}s', flush=True)
json.dump(dict(limit=LIM, n_primes=count, zeros=found), open('primediff_seg.json', 'w'), indent=1)
print('done', count, f'{time.time()-t0:.0f}s')
