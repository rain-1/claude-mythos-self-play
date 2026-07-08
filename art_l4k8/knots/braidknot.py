"""Braid-closure knot engine with Fox p-colorings.

A braid word on n strands closes into a link; it is a KNOT iff the braid's
permutation is an n-cycle. Fox p-colorings of the closure are computed
exactly: each crossing acts on the strand-label vector by an integer
matrix (under-strand label -> 2*over - under), and colorings of the
closure are the fixed vectors mod p of the total monodromy A. The knot
determinant is |det| of a first minor of (A - I), which equals
|Delta_K(-1)| (verified against the classics below).

VERIFIED here:
  trefoil  sigma_1^3            : det 3,  9 Fox 3-colorings
  figure-8 (s1 s2^-1)^2         : det 5, 25 Fox 5-colorings
  cinquefoil sigma_1^5          : det 5
  6_1 = s1 s1 s2 s2^-1... use granny/square checks instead:
  granny = s1^3 then closure with... (skipped; classics above suffice)
  T(3,4) = (s1 s2)^4            : det 3
"""
import numpy as np
from fractions import Fraction


def perm_of_word(n, word):
    p = list(range(n))
    for i, s in word:
        p[i], p[i + 1] = p[i + 1], p[i]
    return p


def is_knot(n, word):
    """Closure is a knot iff the braid permutation is a single n-cycle."""
    p = perm_of_word(n, word)
    seen = set()
    j = 0
    for _ in range(n):
        if j in seen:
            return False
        seen.add(j)
        j = p[j]
    return len(seen) == n


def monodromy(n, word):
    """Integer matrix A: label vector (by slot) after one trip through the
    braid, reading crossings bottom to top. sigma_i^+ : slot i passes OVER
    slot i+1."""
    A = np.eye(n, dtype=object)

    def apply(M, i, s):
        M = M.copy()
        row_i = M[i].copy()
        row_j = M[i + 1].copy()
        if s > 0:
            # over = slot i (o), under = slot i+1 (u); after: slot i holds
            # the under strand with label 2o-u; slot i+1 holds o
            M[i] = 2 * row_i - row_j
            M[i + 1] = row_i
        else:
            # over = slot i+1, under = slot i
            M[i] = row_j
            M[i + 1] = 2 * row_j - row_i
        return M

    for i, s in word:
        A = apply(A, i, s)
    return A


def fox_colorings(n, word, p):
    """Kernel dimension of (A - I) mod p (>=1; dim>1 means nontrivial
    colorings exist). Returns (dim, basis) with basis vectors mod p."""
    A = monodromy(n, word)
    M = (np.array(A, dtype=object) - np.eye(n, dtype=object)).astype(object)
    Mp = np.array([[int(x) % p for x in row] for row in M], dtype=np.int64)
    # gaussian elimination mod p
    Mp = Mp.copy()
    rows, cols = Mp.shape
    pivots = []
    r = 0
    for c in range(cols):
        piv = None
        for rr in range(r, rows):
            if Mp[rr, c] % p:
                piv = rr
                break
        if piv is None:
            continue
        Mp[[r, piv]] = Mp[[piv, r]]
        inv = pow(int(Mp[r, c]), p - 2, p)
        Mp[r] = (Mp[r] * inv) % p
        for rr in range(rows):
            if rr != r and Mp[rr, c] % p:
                Mp[rr] = (Mp[rr] - Mp[rr, c] * Mp[r]) % p
        pivots.append(c)
        r += 1
    free = [c for c in range(cols) if c not in pivots]
    basis = []
    for fc in free:
        v = np.zeros(cols, dtype=np.int64)
        v[fc] = 1
        for ri, pc in enumerate(pivots):
            v[pc] = (-Mp[ri, fc]) % p
        basis.append(v % p)
    return len(free), basis


def determinant(n, word):
    """|Delta_K(-1)| via first minor of (A - I) over the integers."""
    A = monodromy(n, word)
    M = np.array(A, dtype=object) - np.eye(n, dtype=object)
    M = M[:-1, :-1]
    return abs(_int_det(M))


def _int_det(M):
    """Fraction-free-ish determinant of an object (python int) matrix."""
    from fractions import Fraction
    m = [[Fraction(int(x)) for x in row] for row in M]
    n = len(m)
    det = Fraction(1)
    for c in range(n):
        piv = None
        for r in range(c, n):
            if m[r][c] != 0:
                piv = r
                break
        if piv is None:
            return 0
        if piv != c:
            m[c], m[piv] = m[piv], m[c]
            det = -det
        det *= m[c][c]
        inv = m[c][c]
        for r in range(c + 1, n):
            f = m[r][c] / inv
            if f:
                for cc in range(c, n):
                    m[r][cc] -= f * m[c][cc]
    assert det.denominator == 1
    return int(det)


def verify():
    trefoil = (2, [(0, 1)] * 3)
    fig8 = (3, [(0, 1), (1, -1), (0, 1), (1, -1)])
    cinq = (2, [(0, 1)] * 5)
    t34 = (3, [(0, 1), (1, 1)] * 4)
    assert is_knot(*trefoil) and is_knot(*fig8) and is_knot(*cinq) and is_knot(*t34)
    assert determinant(*trefoil) == 3
    assert determinant(*fig8) == 5
    assert determinant(*cinq) == 5
    assert determinant(*t34) == 3
    d3, _ = fox_colorings(*trefoil, 3)
    assert 3 ** (d3) == 9, d3          # 9 colorings incl. trivial
    d5, _ = fox_colorings(*fig8, 5)
    assert 5 ** (d5) == 25, d5
    d5t, _ = fox_colorings(*trefoil, 5)
    assert d5t == 1                    # only trivial 5-colorings of 3_1
    print("VERIFIED: trefoil det 3 (9 three-colorings), figure-eight det 5 "
          "(25 five-colorings), 5_1 det 5, T(3,4) det 3; monodromy/Fox "
          "machinery consistent")


if __name__ == "__main__":
    verify()
