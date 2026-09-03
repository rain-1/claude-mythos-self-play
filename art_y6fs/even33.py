"""Exact R(n,m) = min #zeros of a (3,3)-even function (MO 514851) by the product structure.
A (3,3)-even g is a C(n,2) x C(m,2) matrix M over GF(2) with T_n M T_m^T = 0, where T_k is the
triple/pair incidence matrix; ker T_k = cut space of K_k (dim k-1). The solution space is
  {A + B : columns of A in ker T_n, rows of B in ker T_m}
so max weight = max over B (2^{(m-1) C(n,2)} choices) of  sum over columns f of
  max over cuts c of K_n of  popcount(B[:,f] + c).
usage: python3 even33.py n m
"""
import sys, itertools, math, time
import numpy as np


def cuts(k):
    """all 2^{k-1} cut vectors of K_k as bitmasks over pairs (pair index = position in combinations)"""
    pairs = list(itertools.combinations(range(k), 2))
    out = []
    for S in range(1 << (k - 1)):
        v = 0
        for idx, (a, b) in enumerate(pairs):
            if ((S >> a) & 1) != ((S >> b) & 1) if a < k - 1 and b < k - 1 else (((S >> a) & 1) if b == k - 1 else 0) != 0:
                pass
        # simpler: vertex k-1 is always outside S
        mem = [(S >> a) & 1 if a < k - 1 else 0 for a in range(k)]
        for idx, (a, b) in enumerate(pairs):
            if mem[a] != mem[b]:
                v |= 1 << idx
        out.append(v)
    return sorted(set(out)), pairs


def R(n, m, verbose=True):
    cn, pa = cuts(n); cm, pb = cuts(m)
    PA, PB = len(pa), len(pb)
    # B: each of the PA rows is a cut vector of K_m (bitmask over PB positions). Enumerate all cm^PA
    # combinations; for each, per column f: bit f of each row -> a PA-bit column vector; contribution =
    # max over c in cn of popcount(col ^ c).
    # Precompute best[colvec] for all 2^PA column vectors.
    cn_arr = np.array(cn, np.int64)
    allcols = np.arange(1 << PA, dtype=np.int64)
    pc = np.array([bin(x).count('1') for x in range(1 << PA)], np.int64)
    best = np.max(pc[(allcols[:, None] ^ cn_arr[None, :])], axis=1)   # (2^PA,)
    # enumerate B row choices: rows r_0..r_{PA-1} each in cm (2^{m-1} options)
    K = len(cm)
    total = K ** PA
    if verbose:
        print('R(%d,%d): enumerating %d^%d = %.3g row choices' % (n, m, K, PA, total))
    # column vectors: colvec_f = sum_i bit_f(r_i) << i. Build incrementally with numpy over the last rows.
    cm_arr = np.array(cm, np.int64)
    # bits table: bitf[r, f] = (cm[r] >> f) & 1
    bitf = ((cm_arr[:, None] >> np.arange(PB)[None, :]) & 1).astype(np.int64)   # (K, PB)
    # split rows: first PA-2 rows enumerated in python (K^(PA-2)), last 2 rows vectorised (K^2)
    lastk = min(PA, 3) if K ** 3 <= 40000 else 2
    pre_rows = PA - lastk
    idx_last = np.array(list(itertools.product(range(K), repeat=lastk)), np.int64)   # (K^lastk, lastk)
    colvec_last = np.zeros((len(idx_last), PB), np.int64)
    for j in range(lastk):
        colvec_last |= bitf[idx_last[:, j]] << (pre_rows + j)
    bestw = 0
    t0 = time.time()
    for pre in itertools.product(range(K), repeat=pre_rows):
        base = np.zeros(PB, np.int64)
        for i, r in enumerate(pre):
            base |= bitf[r] << i
        cv = colvec_last | base[None, :]
        w = best[cv].sum(axis=1).max()
        if w > bestw:
            bestw = int(w)
    Rval = PA * PB - bestw
    if verbose:
        print('R(%d,%d) = %d  (|F| = %d, max weight %d)  %.1fs' % (n, m, Rval, PA * PB, bestw, time.time() - t0))
    return Rval


def zar(n, m):
    return (n // 2) * ((n - 1) // 2) * (m // 2) * ((m - 1) // 2)


if __name__ == '__main__':
    n, m = int(sys.argv[1]), int(sys.argv[2])
    if (m - 1) * (n * (n - 1) // 2) > (n - 1) * (m * (m - 1) // 2):
        n, m = m, n
    r = R(n, m)
    print('Z(%d,%d) = %d   equal: %s' % (n, m, zar(n, m), r == zar(n, m)))
