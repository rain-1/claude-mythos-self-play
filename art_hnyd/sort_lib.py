"""MO 513971: alternating lexicographic row/column sorting of binary matrices.

R(A): rows -> increasing lex order.  C(A): columns -> increasing lex order
(each column read top to bottom).  Start with R.  T(A) = min t>=1 such that
A^(t) is fixed by BOTH R and C (each sort = one step).

Key representation: rows packed to bytes (bitorder 'big'), viewed as
big-endian uint64 words -> lexicographic comparison of the word tuple ==
lexicographic comparison of the 0/1 row.
"""
import numpy as np


def _row_keys(A):
    """(n,n) uint8 0/1 -> (n, ceil(n/64)) uint64 whose tuple-lex order == row lex order."""
    P = np.packbits(A, axis=1)                     # (n, ceil(n/8)) big-bit-first
    pad = (-P.shape[1]) % 8
    if pad:
        P = np.hstack([P, np.zeros((P.shape[0], pad), np.uint8)])
    P = np.ascontiguousarray(P)
    return P.view('>u8').astype(np.uint64)         # big-endian words


def _lex_argsort(K):
    """argsort of rows of K (uint64 words, most significant first), stable."""
    return np.lexsort(tuple(K[:, j] for j in range(K.shape[1] - 1, -1, -1)))


def _is_sorted(K):
    """rows of K non-decreasing in tuple lex order?"""
    a, b = K[:-1], K[1:]
    for j in range(K.shape[1]):
        lt = a[:, j] < b[:, j]
        gt = a[:, j] > b[:, j]
        # row pair decided at first differing word
        if j == 0:
            bad = gt
            und = ~(lt | gt)
        else:
            bad |= und & gt
            und &= ~(lt | gt)
    return not bad.any()


def sort_rows(A):
    K = _row_keys(A)
    return A[_lex_argsort(K)]


def rows_sorted(A):
    return _is_sorted(_row_keys(A))


def T_of(A, tmax=10_000, trace=None):
    """number of sorts until doubly sorted; A modified copy.
    trace: optional list collecting (pass_index, n_changed_cells)."""
    A = A.copy()
    t = 0
    while t < tmax:
        t += 1
        if t % 2 == 1:                      # R
            B = sort_rows(A)
        else:                               # C
            B = sort_rows(A.T).T
        if trace is not None:
            trace.append((t, int((A != B).sum())))
        A = B
        if rows_sorted(A) and rows_sorted(A.T):
            return t, A
    raise RuntimeError("no convergence")


# ---------- batched exhaustive engine for small n (matrices as n*n-bit ints) ----------

def batch_T(codes, n):
    """codes: uint64 array of matrix codes (bit (i*n+j) = A[i,j], bit 0 = A[0,0],
    reading row-major, MOST significant position = A[0,0]... we define:
    code = sum A[i,j] << (n*n-1 - (i*n+j)), so lex order of full read == integer order.
    Returns T for each code. Vectorized over the batch."""
    NN = n * n
    # extract row keys: row i = bits [NN-1-i*n .. NN-n-i*n]  (n bits)
    def rowkeys(c):
        ks = np.empty((c.shape[0], n), np.uint32)
        for i in range(n):
            shift = NN - n * (i + 1)
            ks[:, i] = ((c >> np.uint64(shift)) & np.uint64((1 << n) - 1)).astype(np.uint32)
        return ks

    def build(ks):
        c = np.zeros(ks.shape[0], np.uint64)
        for i in range(n):
            shift = NN - n * (i + 1)
            c |= ks[:, i].astype(np.uint64) << np.uint64(shift)
        return c

    def transpose_code(c):
        ks = rowkeys(c)
        # bit j of row-key i (from msb: col j) -> bit i of new row j
        tk = np.zeros((ks.shape[0], n), np.uint32)
        for i in range(n):
            for j in range(n):
                bit = (ks[:, i] >> np.uint32(n - 1 - j)) & np.uint32(1)
                tk[:, j] |= bit << np.uint32(n - 1 - i)
        return build(tk)

    def rsort(c):
        ks = rowkeys(c)
        ks.sort(axis=1)
        return build(ks)

    T = np.zeros(codes.shape[0], np.int32)
    active = np.arange(codes.shape[0])
    c = codes.copy()
    t = 0
    while active.size:
        t += 1
        if t % 2 == 1:
            c2 = rsort(c)
        else:
            c2 = transpose_code(rsort(transpose_code(c)))
        c = c2
        # doubly sorted?
        ks = rowkeys(c)
        rs = np.all(ks[:, :-1] <= ks[:, 1:], axis=1) if n > 1 else np.ones(c.shape[0], bool)
        ct = transpose_code(c)
        kt = rowkeys(ct)
        cs = np.all(kt[:, :-1] <= kt[:, 1:], axis=1) if n > 1 else np.ones(c.shape[0], bool)
        done = rs & cs
        T[active[done]] = t
        active = active[~done]
        c = c[~done]
        if t > 4 * n:
            raise RuntimeError("no convergence in batch")
    return T
