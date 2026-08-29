#!/usr/bin/env python3
"""Exact certificates for MO 514744.

1. Exact T(m,n) for small m,n via integer resultant Res(q_m,f_n)/m
   (sympy, exact) -- cross-checks the mod-p engine and the identity itself.
2. Diagonal law: T(n,n)*n/2^(n-1) is a perfect square (exact isqrt) for all
   n<=NDIAG, and T(n,n) itself is square exactly at the magic n.
3. Desert ledger: sum over unchecked pairs of 1/sqrt(T) (squareness luck).
"""
import math, json
from math import isqrt
import sympy as sp

t = sp.symbols('t')

def qpoly(m):
    c0, c1 = sp.Integer(1), t - 1
    for k in range(2, m + 1):
        a = t - 1 if k == m else t - 2
        c0, c1 = c1, sp.expand(a * c1 - c0)
    q = sp.div(c1, t)[0]
    return sp.Poly(q, t)

def fpoly(n):
    e0, e1 = sp.Integer(1), t + 1
    for k in range(2, n):
        e0, e1 = e1, sp.expand((t + 2) * e1 - e0)
    return sp.Poly(sp.expand((t + 1) * e1 - e0), t)

def T_exact(m, n):
    return abs(sp.resultant(qpoly(m).as_expr(), fpoly(n).as_expr(), t)) // m

# --- 1. cross-check small values -------------------------------------------
known = {(2,2):4,(2,3):15,(2,4):56,(2,5):209,(3,3):192,(3,4):2415,
         (4,4):100352,(4,5):4140081,(5,5):557568000}
ok = True
for (m,n),v in known.items():
    got = T_exact(m,n)
    if got != v: print("MISMATCH",m,n,got,v); ok=False
print("small-value cross-check:", "ALL OK" if ok else "FAIL")

# squarefulness for all m<=n<=12 exact, to validate the witness engine
sqmap = {}
for m in range(2,13):
    for n in range(m,13):
        Tv = T_exact(m,n)
        s = isqrt(Tv)
        sqmap[(m,n)] = (s*s == Tv)
sq_pairs = sorted(k for k,v in sqmap.items() if v)
print("exact squares among m<=n<=12:", sq_pairs)   # expect [(2,2),(8,8),(9,9)]

# --- 2. diagonal law exact to NDIAG ----------------------------------------
NDIAG = 60
magic = []
law_ok = True
for n in range(2, NDIAG+1):
    Tv = T_exact(n, n)
    M = Tv * n
    d, r = divmod(M, 2**(n-1))
    if r: print("2-adic FAIL", n); law_ok=False; continue
    q = isqrt(d)
    if q*q != d:
        print("LAW FAIL: T*n/2^(n-1) not square at n =", n); law_ok=False
    s = isqrt(Tv)
    if s*s == Tv: magic.append(n)
print("diagonal law T(n,n)*n = 2^(n-1)*Q^2 exact for n<=%d:" % NDIAG,
      "HOLDS" if law_ok else "BROKEN")
print("exact diagonal squares n<=%d:" % NDIAG, magic)
pred = sorted([x*x for x in range(1,9,2) if x*x<=NDIAG] +
              [2*x*x for x in range(1,6) if 2*x*x<=NDIAG])
print("predicted:", [p for p in pred if p>=2])

# --- 3. desert ledger -------------------------------------------------------
# log T(m,n) by float eigenvalue product (numpy)
import numpy as np
NCAP = 300
evs = {m: 2-2*np.cos(np.pi*np.arange(1,m)/m) for m in range(2,NCAP+1)}
logs = {}
E_all = E_81 = E_200 = 0.0
for m in range(2, NCAP+1):
    mu = evs[m]
    for n in range(m+1, NCAP+1):
        lt = float(np.log(mu[:,None]+evs[n][None,:]).sum())
        w = math.exp(-lt/2)
        E_all += w
        if max(m,n) > 81: E_81 += w
        if max(m,n) > 200: E_200 += w
# tail beyond NCAP: log T >= 1.16*m*n nats; sum < 1e-8000, negligible
print("desert ledger  E[squares among m<n] if unbiased:")
print("  all pairs        : %.4f (dominated by tiny grids, all checked)" % E_all)
print("  beyond poster 81 : %.3e" % E_81)
print("  beyond ours 200  : %.3e" % E_200)
json.dump(dict(magic=magic, E_all=E_all, E_81=E_81, E_200=E_200),
          open("trees_verify.json","w"))
