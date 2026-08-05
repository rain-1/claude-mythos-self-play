#!/usr/bin/env python3
"""Piece 40: singular series R(g) for l-term gap-g AP patterns in S (Z[sqrt2] norms).
S at one integer: odd part === +-1 mod 8, and v_p even for every bad prime p===3,5 mod 8.

R(g) = [d2(g,l)/(1/2)^l] * prod_{bad p} [dp(g,l)/(p/(p+1))^l]

d2: exact bracket by enumeration mod 2^K (undetermined classes give lo/up).
dp: for p !| g and p > l: CLOSED FORM  dp = 1 - l/(p+1)
    (at most one post hits 0 mod p; conditional even-valuation measure = 1/(p+1));
    for p <= l or p | g: numeric bracket mod p^J.
Tail p in (P0, inf): log fp ~ -C(l)/p^2, negligible beyond 1e5."""
import numpy as np
from sympy import primerange

def d2_bracket(g, l, K):
    M = 1 << K
    n = np.arange(M, dtype=np.int64)
    good = np.ones(M, bool); bad = np.zeros(M, bool); undet = np.zeros(M, bool)
    lim = 1 << (K - 3)
    for k in range(l):
        t = (n + k * g) % M
        low = (t & (-t)).astype(np.int64)
        det = (t != 0) & (low <= lim)
        odd = np.ones_like(t)
        nz = t != 0
        odd[nz] = t[nz] // low[nz]
        r8 = odd % 8
        good &= det & ((r8 == 1) | (r8 == 7))
        bad |= det & ((r8 == 3) | (r8 == 5))
        undet |= ~det
    lo = good.mean()
    up = (good | (undet & ~bad)).mean()
    return lo, up

def dp_bracket(g, l, p, J):
    M = p ** J
    n = np.arange(M, dtype=np.int64)
    good = np.ones(M, bool); bad = np.zeros(M, bool); undet = np.zeros(M, bool)
    for k in range(l):
        t = (n + k * g) % M
        v = np.zeros_like(t); tt = t.copy()
        act = tt != 0
        while True:
            div = act & (tt % p == 0)
            if not div.any(): break
            v[div] += 1; tt[div] //= p
            act = div
        det = t != 0
        even = (v % 2) == 0
        good &= det & even
        bad |= det & ~even
        undet |= ~det
    return good.mean(), (good | (undet & ~bad)).mean()

def R_factor(g, l=5, K=22, P0=100000):
    lo2, up2 = d2_bracket(g, l, K)
    d2 = 0.5 * (lo2 + up2)
    logf = np.log(max(d2 / 0.5 ** l, 1e-300))
    special = {3, 5} | {p for p in (3, 5, 11, 13, 19, 29, 37, 43, 53, 59, 61) if g % p == 0}
    for p in sorted(special):
        if p % 8 not in (3, 5): continue
        J = max(4, int(np.ceil(16 / np.log2(p))) )
        lop, upp = dp_bracket(g, l, p, J)
        fp = 0.5 * (lop + upp) / (p / (p + 1.0)) ** l
        if fp <= 0: return 0.0, (lo2, up2)
        logf += np.log(fp)
    for p in primerange(7, P0):
        if p % 8 not in (3, 5) or g % p == 0 or p in special: continue
        fp = (1 - l / (p + 1.0)) / (p / (p + 1.0)) ** l
        logf += np.log(fp)
    return float(np.exp(logf)), (lo2, up2)

if __name__ == "__main__":
    K = 22
    print("g    R(g)        d2_lo      d2_up")
    for g in [1, 2, 4, 7, 8, 9, 14, 15, 16, 17, 18, 24]:
        R, (lo2, up2) = R_factor(g, 5, K)
        print(f"{g:3d} {R:11.4g}  {lo2:.6f}  {up2:.6f}", flush=True)
