"""Scan odd abundant n <= N: subset sums of divisors via Python big-int bitsets.
Usage: python3 scan.py N out.csv
For each odd abundant n computes bitset of subset sums up to floor(sigma/2) (enough by symmetry
x -> sigma-x), then:
  half_ok : (n+1)/2 representable
  L, U    : largest non-representable < n/2, smallest non-representable > n/2
  h       : max h with all integers in [(n-1)/2-h, (n+1)/2+h] representable (-1 if (n+1)/2 or (n-1)/2 fails)
  nonrep  : number of non-representable integers in [0, sigma]
"""
import sys, time, numpy as np, numba

@numba.njit(cache=True)
def odd_sigma(N):
    s = np.zeros(N+1, np.int64)
    for d in range(1, N+1, 2):
        for m in range(d, N+1, 2*d):
            s[m] += d
    return s

@numba.njit(cache=True)
def spf_sieve(N):
    spf = np.zeros(N+1, np.int32)
    for i in range(2, N+1):
        if spf[i] == 0:
            for j in range(i, N+1, i):
                if spf[j] == 0: spf[j] = i
    return spf

def divisors(n, spf):
    ds = [1]
    while n > 1:
        p = int(spf[n]); e = 0
        while n % p == 0: n //= p; e += 1
        ds = [d * p**k for d in ds for k in range(e+1)]
    return sorted(ds)

def analyse(n, ds, sig):
    M = sig // 2
    mask = (1 << (M+1)) - 1
    b = 1
    for d in ds:
        b |= (b << d) & mask
    # complement bits in [0,M]
    nb = (~b) & mask
    cnt_low = bin(nb).count('1')
    # nonrep in [0,sigma]: values x in [0,M] and sigma-x; if sigma even, x=M=sigma/2 counted once
    nonrep = 2*cnt_low - (1 if (sig % 2 == 0 and (nb >> M) & 1) else 0)
    lo = (n-1)//2; hi = (n+1)//2   # n/2 sits between lo and hi
    # L: highest set bit of nb restricted to [0,lo]
    low = nb & ((1 << (lo+1)) - 1)
    L = low.bit_length() - 1
    up = nb >> hi
    if up:
        U = hi + ((up & -up).bit_length() - 1)
    else:
        U = None  # no non-rep in [hi,M]; use symmetry: smallest nonrep > M is sigma - (largest nonrep <= sigma-M-1)
        t = sig - M - 1
        seg = nb & ((1 << (t+1)) - 1)
        U = sig - (seg.bit_length() - 1)
    h = min(lo - L, U - hi) - 1
    half_ok = (b >> hi) & 1
    return half_ok, L, U, h, nonrep

def main():
    N = int(sys.argv[1]); out = sys.argv[2]
    t0 = time.time()
    s = odd_sigma(N); spf = spf_sieve(N)
    print('sieves', time.time()-t0, flush=True)
    odd = np.arange(1, N+1, 2)
    ab = odd[s[odd] > 2*odd]
    print('odd abundant count', len(ab), flush=True)
    bad = []
    with open(out, 'w') as f:
        f.write('n,sigma,ndiv,half_ok,L,U,h,nonrep\n')
        for i, n in enumerate(ab):
            n = int(n); sig = int(s[n]); ds = divisors(n, spf)
            half_ok, L, U, h, nonrep = analyse(n, ds, sig)
            if not half_ok:
                bad.append(n); print('COUNTEREXAMPLE', n, flush=True)
            f.write(f'{n},{sig},{len(ds)},{half_ok},{L},{U},{h},{nonrep}\n')
            if i % 20000 == 0: print(i, n, time.time()-t0, flush=True)
    print('done', time.time()-t0, 'counterexamples', len(bad), bad[:50])

if __name__ == '__main__':
    main()
