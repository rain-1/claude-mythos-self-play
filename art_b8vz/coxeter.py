"""coxeter.py — the permutohedron of n runners, projected to its Coxeter plane.

A vertex is a finishing order: runner k finishes in place x_k.  It is drawn at Σ x_k ω^k,
ω = e^{2πi/n} (each runner pulls in its own direction, harder the later it finishes).
A 2-face is an ordered partition with n−2 blocks: a three-way tie (hexagon) or two two-way
ties (square).  All 2-faces are laid on the sheet as glazes (Beer–Lambert sums), so the
picture is a stack of translucent tiles whose overlaps darken like layered tissue.
"""
import itertools, numpy as np
from math import factorial


def faces2(n):
    """yield (kind, tied_blocks, start_positions, polygon vertices as rank vectors)"""
    runners = range(n)
    out = []
    # hexagons: one block of 3 at positions p..p+2
    for p in range(n - 2):
        for T in itertools.combinations(runners, 3):
            rest = [r for r in runners if r not in T]
            for perm in itertools.permutations(rest):
                # perm fills positions 0..p-1 and p+3..n-1 in order
                base = np.zeros(n)
                pos = [q for q in range(n) if not (p <= q < p + 3)]
                for r, q in zip(perm, pos):
                    base[r] = q
                # hexagon cycle: orders of T through adjacent transpositions
                a, b, c = T
                cyc = [(a, b, c), (b, a, c), (b, c, a), (c, b, a), (c, a, b), (a, c, b)]
                poly = []
                for o in cyc:
                    v = base.copy()
                    for i, r in enumerate(o):
                        v[r] = p + i
                    poly.append(v)
                out.append(('hex', (T,), (p,), poly))
    # squares: two blocks of 2 at positions p, q (q >= p+2)
    for p in range(n - 1):
        for q in range(p + 2, n - 1):
            for T1 in itertools.combinations(runners, 2):
                rest1 = [r for r in runners if r not in T1]
                for T2 in itertools.combinations(rest1, 2):
                    rest = [r for r in rest1 if r not in T2]
                    pos = [s for s in range(n) if s not in (p, p + 1, q, q + 1)]
                    for perm in itertools.permutations(rest):
                        base = np.zeros(n)
                        for r, s in zip(perm, pos):
                            base[r] = s
                        poly = []
                        for o1, o2 in [((0, 1), (0, 1)), ((1, 0), (0, 1)), ((1, 0), (1, 0)), ((0, 1), (1, 0))]:
                            v = base.copy()
                            v[T1[o1[0]]], v[T1[o1[1]]] = p, p + 1
                            v[T2[o2[0]]], v[T2[o2[1]]] = q, q + 1
                            poly.append(v)
                        out.append(('sq', (T1, T2), (p, q), poly))
    return out


def project(V, n, phase=0.0):
    w = np.exp(2j * np.pi * (np.arange(n) / n) + 1j * phase)
    z = np.asarray(V) @ w
    return z


if __name__ == '__main__':
    for n in (4, 5, 6, 7):
        F = faces2(n)
        h = sum(1 for f in F if f[0] == 'hex'); s = len(F) - h
        from sympy.functions.combinatorial.numbers import stirling
        print(n, 'hex', h, 'sq', s, 'total', len(F), 'k!S(n,k) k=n-2:', factorial(n - 2) * stirling(n, n - 2))
