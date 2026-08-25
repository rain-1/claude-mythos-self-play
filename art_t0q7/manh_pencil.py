#!/usr/bin/env python3
"""Reality lemma test: generalized eigenvalues of the pencil (A, P A P^T).

If all mu_i real > 0, then |det(A + PAP^T)| = |det A| prod(1+mu_i) and
prod(1+mu_i) >= 2^n by AM-GM given prod mu_i = 1 -- proving MO 514626.
Also test reciprocal symmetry mu -> 1/mu, and the general Lorentzian version.
"""
import numpy as np, itertools
from scipy.linalg import eig

def pencil_test(n, exhaustive, trials=4000, seed=0):
    rng = np.random.default_rng(seed)
    A = np.abs(np.subtract.outer(np.arange(n), np.arange(n))).astype(float)
    detA = np.linalg.det(A)
    perms = itertools.permutations(range(n)) if exhaustive else \
            (rng.permutation(n) for _ in range(trials))
    bad_real = bad_pos = bad_recip = bad_prod = 0
    worst_im = 0.0
    minprod = np.inf
    for pm in perms:
        p = np.asarray(pm)
        B = np.abs(np.subtract.outer(p, p)).astype(float)
        mu = eig(A, B, right=False)          # generalized eigenvalues A u = mu B u
        im = np.max(np.abs(mu.imag) / np.maximum(np.abs(mu), 1e-12))
        worst_im = max(worst_im, im)
        if im > 1e-7: bad_real += 1; continue
        m = np.sort(mu.real)
        if m[0] <= 0: bad_pos += 1
        # reciprocal symmetry
        if np.max(np.abs(np.log(m) + np.log(m[::-1]))) > 1e-6: bad_recip += 1
        pr = np.prod(1 + m)
        minprod = min(minprod, pr)
        # identity check: |det(A+B)| = |det A| * prod(1+mu)
        d = abs(np.linalg.det(A + B))
        if abs(d - abs(detA) * pr) > 1e-6 * d: bad_prod += 1
    print(f"n={n} bad_real={bad_real} bad_pos={bad_pos} bad_recip={bad_recip} "
          f"bad_prod={bad_prod} worst_rel_im={worst_im:.2e} min prod(1+mu)={minprod:.3f} "
          f"(2^n={2**n})")

def lorentzian_general(n, trials=20000, seed=1):
    """General version: X, Y random with signature (1,n-1), sharing timelike vector?
    Construct: X = R^T J R, Y = S^T J S with J=diag(1,-1,..). Check when pencil real."""
    rng = np.random.default_rng(seed)
    J = np.diag([1.0] + [-1.0]*(n-1))
    bad = 0; badshare = 0; share_ct = 0
    for _ in range(trials):
        R = rng.standard_normal((n, n)); S = rng.standard_normal((n, n))
        X = R.T @ J @ R; Y = S.T @ J @ S
        mu = eig(X, Y, right=False)
        real = np.max(np.abs(mu.imag)/np.maximum(np.abs(mu),1e-12)) < 1e-7
        # shared timelike vector? check if exists v: v^TXv>0 and v^TYv>0.
        # cheap sufficient probe: top eigvec of X, of Y, and of X+Y
        share = False
        for M in (X, Y, X + Y):
            w, V = np.linalg.eigh(M)
            v = V[:, -1]
            if v @ X @ v > 0 and v @ Y @ v > 0: share = True; break
        if share: share_ct += 1
        if not real:
            bad += 1
            if share: badshare += 1
    print(f"general n={n}: nonreal {bad}/{trials}; among shared-timelike: "
          f"nonreal {badshare}/{share_ct}")

def commonH_general(n, trials=20000, seed=2):
    """Both ND on a COMMON hyperplane H=v-perp, signature (1,n-1). Pencil real?"""
    rng = np.random.default_rng(seed)
    bad = 0
    for _ in range(trials):
        # build X: ND on H=e0-perp... general v: use basis where H = span(e1..e{n-1})
        def mk():
            G = rng.standard_normal((n-1, n-1)); G = G @ G.T + 1e-3*np.eye(n-1)  # PD
            b = rng.standard_normal(n-1); a = rng.standard_normal()**2 + b @ np.linalg.solve(G, b)
            # X = [[a, b],[b^T, -G]]: Schur a + b G^{-1} b^T > 0 ensures sig (1, n-1)
            X = np.empty((n, n)); X[0,0] = a; X[0,1:] = b; X[1:,0] = b; X[1:,1:] = -G
            return X
        X = mk(); Y = mk()
        mu = eig(X, Y, right=False)
        if np.max(np.abs(mu.imag)/np.maximum(np.abs(mu),1e-12)) > 1e-7: bad += 1
    print(f"commonH n={n}: nonreal {bad}/{trials}")

if __name__ == "__main__":
    for n in range(3, 8): pencil_test(n, True)
    for n in (10, 16, 30, 64): pencil_test(n, False, trials=1500, seed=n)
    for n in (3, 5, 8): lorentzian_general(n, 5000)
    for n in (3, 5, 8): commonH_general(n, 5000)
