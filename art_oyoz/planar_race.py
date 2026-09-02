"""planar_race.py — exact count of n <= N whose proper-divisor divisibility graph is planar.

Planar  <=>  exponent signature in {p, p^2, p^3, p^4, pq, p^2 q, p^3 q, pqr}  (+ n = 1, empty graph).
Non-planar minimal signatures: p^5, p^2 q^2, p^4 q, p^2 q r, pqrs (K5 / K33-type subgraphs).

Counting with a Lucy_Hedgehog prime-count table pi(N//k) for every k:
  P(N) = 1 + pi(N) + pi(N^(1/2)) + pi(N^(1/3)) + pi(N^(1/4))
       + sum_{p<=sqrt N} [pi(N//p) - pi(p)]                       (pq, p<q)
       + sum_{p} [pi(N//p^2) - [p^3<=N]]                           (p^2 q, q != p)
       + sum_{p} [pi(N//p^3) - [p^4<=N]]                           (p^3 q, q != p)
       + sum_{p<q, p q^2 < N} [pi(N//(pq)) - pi(q)]                (pqr, p<q<r)
Every argument N//m is in the Lucy table.  Cross-checked against a brute-force sieve for small N.
"""
import numpy as np, sys, time
from math import isqrt

def lucy(N):
    """Return (V, S) with S[i] = pi(V[i]); V = all distinct floor(N/k) descending... (standard)."""
    r = isqrt(N)
    V = [N // i for i in range(1, r + 1)]
    V += list(range(V[-1] - 1, 0, -1))
    V = np.array(V, dtype=np.int64)
    S = V - 1  # count of integers 2..v
    S = S.astype(np.int64)
    # index helper: value v -> position. For v > r: pos = N//v - 1 ; for v <= r: pos = len(V) - v
    L = len(V)
    def idx(v):
        return np.where(v > r, N // v - 1, L - v)
    for p in range(2, r + 1):
        sp = S[L - p + 1]       # pi(p-1) = number of primes below p
        if S[L - p] == sp:      # p not prime (count did not step)
            continue
        p2 = p * p
        k = np.searchsorted(-V, -p2, side='right')  # V descending; positions with V >= p2
        Vk = V[:k]
        S[:k] -= S[idx(Vk // p)] - sp
    return V, S, idx

def count_planar(N, verbose=False):
    t0 = time.time()
    V, S, idx = lucy(N)
    L = len(V); r = isqrt(N)
    def pi(x):
        x = np.asarray(x, dtype=np.int64)
        out = np.zeros_like(x)
        m = x >= 1
        out[m] = S[idx(x[m])]
        return out
    # primes up to sqrt(N)
    sieve = np.ones(r + 1, bool); sieve[:2] = False
    for i in range(2, isqrt(r) + 1):
        if sieve[i]:
            sieve[i * i::i] = False
    primes = np.nonzero(sieve)[0].astype(np.int64)
    pip = pi(primes)  # pi(p) for each p
    total = 1  # n = 1
    c1 = int(S[0]); total += c1                           # primes
    c2 = int(pi(isqrt(N))); c3 = int(pi(icbrt(N))); c4 = int(pi(isqrt(isqrt(N))))
    total += c2 + c3 + c4
    # pq
    cpq = int(np.sum(pi(N // primes) - pip))
    # p^2 q
    p2 = primes[primes * primes <= N]
    cp2q = int(np.sum(pi(N // (p2 * p2)) - (p2 ** 3 <= N)))
    # p^3 q
    p3 = primes[primes ** 3 <= N]
    cp3q = int(np.sum(pi(N // (p3 ** 3)) - (p3 ** 4 <= N)))
    # pqr: p<q, p*q*q < N
    cpqr = 0
    pmax = icbrt(N)
    for i, p in enumerate(primes[primes <= pmax]):
        qmax = isqrt(N // p)
        qs = primes[(primes > p) & (primes <= qmax)]
        if len(qs) == 0:
            continue
        # need r > q with p q r <= N => pi(N//(pq)) - pi(q)
        cpqr += int(np.sum(pi(N // (p * qs)) - pi(qs)))
    total += cpq + cp2q + cp3q + cpqr
    if verbose:
        print(f'N={N}: planar={total} ({total / N:.5f})  [p:{c1} p2:{c2} p3:{c3} p4:{c4} pq:{cpq} p2q:{cp2q} p3q:{cp3q} pqr:{cpqr}]  {time.time() - t0:.1f}s', flush=True)
    return total, dict(p=c1, p2=c2, p3=c3, p4=c4, pq=cpq, p2q=cp2q, p3q=cp3q, pqr=cpqr)

def icbrt(N):
    c = int(round(N ** (1 / 3)))
    while c ** 3 > N: c -= 1
    while (c + 1) ** 3 <= N: c += 1
    return c

PLANAR_SIGS = {(1,), (2,), (3,), (4,), (1, 1), (2, 1), (3, 1), (1, 1, 1)}

def brute(N):
    """Sieve signatures for all n <= N (small N) — cross-check."""
    spf = np.zeros(N + 1, np.int64)
    for i in range(2, N + 1):
        if spf[i] == 0:
            spf[i::i][spf[i::i] == 0] = i
    cnt = 1
    for n in range(2, N + 1):
        m = n; sig = []
        while m > 1:
            p = spf[m]; e = 0
            while m % p == 0:
                m //= p; e += 1
            sig.append(e)
        if tuple(sorted(sig, reverse=True)) in PLANAR_SIGS:
            cnt += 1
    return cnt

if __name__ == '__main__':
    if sys.argv[1] == 'check':
        for N in [100, 1000, 5000, 20000, 100000]:
            a = count_planar(N)[0]; b = brute(N)
            print(N, a, b, 'OK' if a == b else 'MISMATCH')
    else:
        for arg in sys.argv[1:]:
            N = int(float(arg))
            count_planar(N, verbose=True)
