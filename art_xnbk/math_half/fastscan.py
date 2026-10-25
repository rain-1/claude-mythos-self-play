"""Fast check of (n+1)/2 in R(n) for all odd abundant n <= N.
Sufficient criterion (interval extension lemma): if the subset sums of d_1..d_i contain [a, S_i - a]
and d_{i+1} <= S_i - 2a + 1 then sums of d_1..d_{i+1} contain [a, S_{i+1} - a].
Exact bitset on a prefix (sum <= CAP), then the lemma; exact bitset fallback if the lemma breaks.
Usage: python3 fastscan.py N out.txt
"""
import sys, time, numpy as np
from scan import odd_sigma, spf_sieve, divisors
CAP = 4096

def check(n, ds):
    T = (n + 1) // 2
    b = 1; S = 0; i = 0; k = len(ds)
    while i < k and S + ds[i] <= CAP:
        b |= b << ds[i]; S += ds[i]; i += 1
    half = S // 2
    nb = ~b & ((1 << (half + 1)) - 1)
    a = nb.bit_length()  # largest nonrep <= S/2, plus 1
    while i < k:
        d = ds[i]
        if d <= S - 2 * a + 1: S += d; i += 1
        else: break
    if i == k and a <= T <= S - a:
        return 1, 0, a
    # fallback exact
    mask = (1 << (T + 1)) - 1; b = 1
    for d in ds:
        if d > T: break
        b |= (b << d) & mask
    return (b >> T) & 1, ds[i] if i < k else -1, a

def main():
    N = int(sys.argv[1]); out = sys.argv[2]; t0 = time.time()
    s = odd_sigma(N); spf = spf_sieve(N)
    odd = np.arange(1, N + 1, 2); ab = odd[s[odd] > 2 * odd]; del odd
    print('sieves', time.time() - t0, 'odd abundant', len(ab), flush=True)
    nfb = 0; bad = []
    with open(out, 'w') as f:
        for j, n in enumerate(ab):
            n = int(n); ds = divisors(n, spf)
            ok, brk, a = check(n, ds)
            if brk: nfb += 1; f.write(f'{n} ok={ok} break_at={brk} a={a}\n')
            if not ok: bad.append(n)
            if j % 50000 == 0: print(j, n, time.time() - t0, 'fallbacks', nfb, 'bad', len(bad), flush=True)
    print('done', time.time() - t0, 'count', len(ab), 'fallbacks', nfb, 'counterexamples', len(bad), flush=True)

if __name__ == '__main__':
    main()
