"""Goldbach comet data: r(2n) for all 2n <= LIM via one FFT, plus the
Hardy-Littlewood singular series 3S(n) by sieve.  Verification:
  * per-stratum empirical/HL ratio -> 1
  * no even number in range without a representation (Goldbach verified here)
  * r matches direct counting at small n
Cache: comet.npz
"""
import numpy as np, os, time

LIM = 1 << 23          # count r(2n) for 2n up to ~8.4M
C2 = 0.6601618158468695739278121100145557784326  # twin prime constant


def primes_upto(N):
    s = np.ones(N + 1, dtype=bool)
    s[:2] = False
    for p in range(2, int(N ** 0.5) + 1):
        if s[p]:
            s[p * p:: p] = False
    return np.nonzero(s)[0]


def build():
    if os.path.exists("comet.npz"):
        return np.load("comet.npz")
    t0 = time.time()
    P = primes_upto(LIM)
    Podd = P[P > 2]
    f = np.zeros(LIM + 1, dtype=np.float64)
    f[Podd] = 1.0
    # ordered pairs of odd primes p+q = m, all m at once
    F = np.fft.rfft(f, 2 * len(f))
    conv = np.fft.irfft(F * F, 2 * len(f))
    m = np.arange(0, LIM + 1, 2)
    r = np.rint(conv[: LIM + 1: 2]).astype(np.int64)   # r(2n), ordered pairs
    # exact spot-check vs direct counting
    Pset = np.zeros(LIM + 1, dtype=bool)
    Pset[Podd] = True
    for m0 in [10, 100, 1000, 9998, 123456]:
        direct = int(sum(1 for p in Podd[Podd < m0] if m0 - p <= LIM and Pset[m0 - p]))
        assert direct == r[m0 // 2], (m0, direct, r[m0 // 2])
    # singular series S(n) = prod_{p | n, p odd} (p-1)/(p-2) over odd primes
    n = np.arange(LIM // 2 + 1)
    S = np.ones(LIM // 2 + 1, dtype=np.float64)
    for p in Podd[Podd <= LIM // 2]:
        S[p:: p] *= (p - 1.0) / (p - 2.0)
    print(f"built in {time.time()-t0:.0f}s")
    np.savez_compressed("comet.npz", r=r, S=S)
    return dict(r=r, S=S)


if __name__ == "__main__":
    d = build()
    r, S = d["r"], d["S"]
    m = np.arange(0, LIM + 1, 2)
    # Goldbach holds in range?
    bad = np.nonzero(r[3:] == 0)[0]
    print(f"even numbers 6..{LIM} without representation: {len(bad)}")
    # HL band verification: r(2n) ~ 2*C2*S(n)*2n/ln^2(2n) (ordered pairs)
    sel = m >= 1 << 20
    ml = m[sel].astype(np.float64)
    hl = 2 * C2 * S[sel.nonzero()[0]] * ml / np.log(ml) ** 2
    ratio = r[sel] / hl
    print(f"global mean r/HL (2n>1M): {ratio.mean():.4f}")
    for lo, hi, name in [(1.0, 1.01, "S=1 (2^k or p^j)"), (1.9, 2.1, "3|n band"),
                         (1.32, 1.34, "5|n band"), (2.6, 2.7, "15|n band")]:
        b = (S[sel.nonzero()[0]] >= lo) & (S[sel.nonzero()[0]] < hi)
        if b.sum():
            print(f"  band {name}: mean ratio {ratio[b].mean():.4f}  n={b.sum()}")
