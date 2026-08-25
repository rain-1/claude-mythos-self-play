#!/usr/bin/env python3
"""Structure of det D_pi: border decomposition + Minkowski route + ladder families.

|det D| = 2^(n-1) det(Ftilde) * (s + q),  Ftilde = -(1/2) Q^T D Q on 1-perp,
s = 1^T D 1 / n, q = (1/2) h^T Ftilde^{-1} h, h = Q^T D 1 / sqrt(n).

Checks: (1) identity of the decomposition; (2) Minkowski det Ftilde_pi >= 2^{n-1} det FA;
(3) the candidate lemma q_pi >= q_id; (4) which perms give the second-smallest value;
(5) gcd of all det values per n.
"""
import numpy as np, itertools, math
from math import gcd
from functools import reduce

def Qbasis(n):
    # orthonormal basis of 1-perp via QR of centering
    M = np.eye(n) - np.ones((n,n))/n
    q, r = np.linalg.qr(M)
    return q[:, :n-1]

def decomp(n, perm, Q, A):
    p = np.asarray(perm)
    D = A + np.abs(np.subtract.outer(p, p))
    C = Q.T @ D @ Q
    Ft = -0.5 * C
    s = D.sum() / n
    h = Q.T @ D.sum(axis=1) / math.sqrt(n)
    q = 0.5 * h @ np.linalg.solve(Ft, h)
    detFt = np.linalg.det(Ft)
    return D, detFt, s, q

def run(n, exhaustive):
    A = np.abs(np.subtract.outer(np.arange(n), np.arange(n))).astype(float)
    Q = Qbasis(n)
    # base (pi = id): D = 2A, Ftilde_id = 2 FA
    _, detFt_id, s, q_id = decomp(n, range(n), Q, A)
    detFA = detFt_id / 2**(n-1)
    perms = itertools.permutations(range(n)) if exhaustive else \
            (tuple(np.random.permutation(n)) for _ in range(3000))
    bad_ident = bad_mink = bad_q = 0
    worst_q = np.inf; worst_qp = None
    second = {}   # value -> example perm (integer dets)
    gall = 0
    for pm in perms:
        D, detFt, s2, qq = decomp(n, pm, Q, A)
        det = np.linalg.det(D)
        # (1) identity check
        pred = 2**(n-1) * detFt * (s2 + qq)
        if abs(abs(det) - pred) > 1e-6 * abs(det): bad_ident += 1
        # (2) Minkowski
        if detFt < 2**(n-1) * detFA * (1 - 1e-9): bad_mink += 1
        # (3) q lemma
        if qq < q_id - 1e-9: bad_q += 1
        if qq - q_id < worst_q: worst_q = qq - q_id; worst_qp = pm
        v = int(round(abs(det)))
        gall = gcd(gall, v)
        if len(second) < 400000: second.setdefault(v, pm)
    vals = sorted(second)
    t = (n-1)*4**(n-1); t2 = (n-2)*4**(n-2) if n >= 2 else 0
    print(f"n={n} ident_bad={bad_ident} mink_bad={bad_mink} q_bad={bad_q} "
          f"worst(q-q_id)={worst_q:.6f} at {worst_qp}")
    print(f"   gcd(all dets)={gall}  bottom={vals[:8]}")
    if len(vals) > 1:
        print(f"   2nd = floor + {vals[1]-t} (= {(vals[1]-t)/t2:.4f} * (n-2)4^(n-2)); "
              f"2nd argmin ex: {second[vals[1]]}")
        for v in vals[1:6]:
            print(f"     val {v} = floor + {(v-t)/t2:.4f} u   ex {second[v]}")

if __name__ == "__main__":
    np.random.seed(1)
    for n in range(4, 9): run(n, True)
    for n in (12, 16, 24): run(n, False)
