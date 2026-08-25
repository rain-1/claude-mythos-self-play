#!/usr/bin/env python3
"""MO 514628 engine: area of T_sigma = union of n parallelograms in the unit square.

Parallelogram i joins bottom interval [(i-1)/n, i/n] to top interval
[(sigma(i)-1)/n, sigma(i)/n].  At height y its left edge sits at
p_i(y) = (i-1) + y*d_i   (units of 1/n),  d_i = sigma(i)-i;  width = 1 unit.

union_len(y) (in units of 1/n): sort p, sum of min(1, gap) + 1.
area = (1/n) * integral_0^1 union_len(y) dy.

Exact: integrand is piecewise linear with kinks only where p_i - p_j hits
{-1, 0, +1}; integrate by midpoint rule on the event partition (exact for
piecewise-linear).  Grid: midpoint rule on M uniform slabs (error O(1/M)).
"""
import numpy as np

def union_len(P):
    """P: (M, n) positions in units of 1/n. Returns (M,) union lengths (units 1/n)."""
    S = np.sort(P, axis=1)
    gaps = S[:, 1:] - S[:, :-1]
    return np.minimum(gaps, 1.0).sum(axis=1) + 1.0

def area_grid(sigma, M=2048):
    """Midpoint-rule area (exact up to event rounding, O(1/M))."""
    n = len(sigma)
    d = np.asarray(sigma, dtype=np.float64) + 1 - np.arange(1, n+1)  # sigma 0-based -> d_i
    base = np.arange(n, dtype=np.float64)
    y = (np.arange(M) + 0.5) / M
    P = base[None, :] + y[:, None] * d[None, :]
    return union_len(P).mean() / n

def area_exact(sigma):
    """Exact area via the event partition (float; exact up to float rounding)."""
    n = len(sigma)
    d = np.asarray(sigma, dtype=np.float64) + 1 - np.arange(1, n+1)
    base = np.arange(n, dtype=np.float64)
    # events: y = (base_j - base_i + k) / (d_i - d_j), k in {-1,0,1}
    di = d[:, None] - d[None, :]
    bj = base[None, :] - base[:, None]
    ys = []
    iu, ju = np.triu_indices(n, 1)
    dd = di[iu, ju]; bb = bj[iu, ju]
    nz = dd != 0
    dd = dd[nz]; bb = bb[nz]
    for k in (-1.0, 0.0, 1.0):
        yv = (bb + k) / dd
        ys.append(yv[(yv > 0) & (yv < 1)])
    ev = np.unique(np.concatenate([[0.0, 1.0]] + ys))
    mid = (ev[1:] + ev[:-1]) / 2
    w = ev[1:] - ev[:-1]
    P = base[None, :] + mid[:, None] * d[None, :]
    return float((union_len(P) * w).sum() / n)

# ---------------- permutation families ----------------
def sigma_id(n): return np.arange(n)
def sigma_rev(n): return np.arange(n)[::-1].copy()

def sigma_bitrev(n):
    k = n.bit_length() - 1
    assert 1 << k == n
    i = np.arange(n)
    r = np.zeros(n, dtype=np.int64)
    for b in range(k):
        r |= ((i >> b) & 1) << (k - 1 - b)
    return r

def sigma_faro(n):
    # interleave: i -> 2i mod n-1 style riffle
    i = np.arange(n)
    return np.where(i < (n + 1) // 2, 2 * i, 2 * (i - (n + 1) // 2) + 1) if n % 2 == 0 \
        else (2 * i) % n

def sigma_blockrev(n, b):
    """reverse within blocks of size b, keep block order"""
    i = np.arange(n)
    blk = i // b
    off = i % b
    top = np.minimum((blk + 1) * b, n) - 1
    return np.minimum(top - off, n - 1)

def sigma_digitrev(n, base):
    """digit-reversal in given base; n must be base^k"""
    k = 0; m = 1
    while m < n: m *= base; k += 1
    assert m == n
    i = np.arange(n)
    r = np.zeros(n, dtype=np.int64)
    x = i.copy()
    for _ in range(k):
        r = r * base + (x % base)
        x //= base
    return r

def random_sigma(n, rng): return rng.permutation(n)
