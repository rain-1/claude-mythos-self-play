"""Construct + rigorously verify a nontrivial homometric pair (The Same Shadow).

A = U + V (Minkowski), B = U - V.  Since the autocorrelation of any set is
centrosymmetric, dA = dU * dV = dU * d(-V) = dB  -- same difference multiset,
same |F|^2: no diffraction/scattering experiment can distinguish A from B.
Nontrivial iff neither U nor V is centrosymmetric and A is not congruent to B.

All in integer coordinates => difference-multiset equality checked EXACTLY.
Non-congruence: exhaustive isometry search (every candidate rigid motion built
from anchor-pair correspondences, both orientations).
"""
import numpy as np
from collections import Counter
from itertools import product

# ---- design: U = asymmetric skeleton (6 sites), V = spiral-curl motif (7 pts)
U = np.array([(0, 0), (31, 7), (46, 33), (21, 52), (-13, 43), (-25, 14)])
V = np.array([(0, 0), (12, -3), (21, 4), (23, 16), (16, 26), (4, 27), (-4, 20)])


def minkowski(U, V, sign):
    P = np.array([(u[0] + sign * v[0], u[1] + sign * v[1]) for u in U for v in V])
    return P


def diffs(P):
    return Counter((int(a[0] - b[0]), int(a[1] - b[1]))
                   for a in P for b in P if not (a[0] == b[0] and a[1] == b[1]))


def centrosymmetric(P):
    c2 = P.sum(0) * 2 / len(P)  # 2*centroid
    S = set(map(tuple, P * 2))  # avoid halves: compare doubled coords
    return all((c2[0] * len(P) / len(P) * 1, ) is not None and
               (int(round(2 * c2[0] / 2 * 0)) or True) for _ in [0]) and \
        all(tuple((2 * np.array([c2[0], c2[1]]) / 1 - 2 * p).astype(int)) in
            set(map(tuple, (2 * P).astype(int))) for p in P) if np.allclose(c2, np.round(c2)) else \
        _centro_float(P)


def _centro_float(P):
    c = P.mean(0)
    S = set(map(tuple, np.round((P - c) * 2).astype(int)))
    return all((-x, -y) in S for (x, y) in S)


def congruent(P, Q, tol=1e-7):
    """Exhaustive: does any isometry map set P onto set Q?"""
    P = np.asarray(P, float); Q = np.asarray(Q, float)
    if len(P) != len(Q):
        return False
    # anchor: pair in P with the rarest distance
    dP = {}
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            d = round(float(np.sum((P[i] - P[j]) ** 2)), 6)
            dP.setdefault(d, []).append((i, j))
    d0, pairsP = min(dP.items(), key=lambda kv: len(kv[1]))
    i0, j0 = pairsP[0]
    a, b = P[i0], P[j0]
    Qset = set(map(tuple, np.round(Q * 4).astype(int)))  # quarter-integer grid
    for qi in range(len(Q)):
        for qj in range(len(Q)):
            if qi == qj:
                continue
            c, d = Q[qi], Q[qj]
            if abs(np.sum((c - d) ** 2) - d0) > 1e-5:
                continue
            for refl in (False, True):
                u = b - a
                v = d - c
                if refl:
                    u = np.array([u[0], -u[1]])
                nu = np.hypot(*u)
                nv = np.hypot(*v)
                if nu < 1e-12:
                    continue
                ct = (u @ v) / (nu * nv)
                st = (u[0] * v[1] - u[1] * v[0]) / (nu * nv)
                R = np.array([[ct, -st], [st, ct]])
                M = R @ np.diag([1, -1]) if refl else R
                img = (P - a) @ M.T + c
                key = np.round(img * 4).astype(int)
                if np.abs(img * 4 - key).max() < 0.02 and \
                   set(map(tuple, key)) == Qset:
                    return True
    return False


def build():
    A = minkowski(U, V, +1)
    B = minkowski(U, V, -1)
    assert len(set(map(tuple, A))) == len(U) * len(V), "sum collisions in A"
    assert len(set(map(tuple, B))) == len(U) * len(V), "sum collisions in B"
    dA, dB = diffs(A), diffs(B)
    assert dA == dB, "difference multisets differ!"
    assert not _centro_float(U) and not _centro_float(V)
    assert not congruent(A, B), "A congruent to B: homometry is trivial!"
    assert congruent(A, A.copy())            # sanity: detector works
    assert congruent(A, (-A) + np.array([3, 7]))  # detects point-inversion+shift
    # spectral check on a fine k-grid
    k = np.linspace(-np.pi, np.pi, 601)
    KX, KY = np.meshgrid(k, k)
    FA = np.zeros(KX.shape, complex)
    FB = np.zeros(KX.shape, complex)
    for (x, y) in A:
        FA += np.exp(1j * (KX * x + KY * y))
    for (x, y) in B:
        FB += np.exp(1j * (KX * x + KY * y))
    spec_err = np.abs(np.abs(FA) ** 2 - np.abs(FB) ** 2).max() / (np.abs(FA) ** 2).max()
    return A, B, dA, spec_err


if __name__ == "__main__":
    A, B, dA, spec_err = build()
    print(f"|A|=|B|={len(A)}  distinct differences: {len(dA)}")
    print(f"difference multisets: EXACTLY equal (integer arithmetic)")
    print(f"A congruent to B: False (exhaustive isometry search)")
    print(f"max relative |F_A|^2 - |F_B|^2 on 601^2 k-grid: {spec_err:.2e}")
