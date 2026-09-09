"""rauzy.py — the Rauzy fractal of the Tribonacci word, with its hierarchy.

sigma: 1 -> 12, 2 -> 13, 3 -> 1.  Incidence matrix M (M[i,j] = # of letter i in sigma(j)),
Pisot root beta = 1.8393, complex conjugate alpha with |alpha| = beta^(-1/2).

Two constructions that must agree (certificate 1):
  (walk)   z_n = sum_{k<=n} v[u_k], v = left eigenvector of M for alpha (v M = alpha v)
  (digits) z_n = v_1 * sum_j d_j alpha^j, n = sum_j d_j T_j the greedy Tribonacci expansion
           (T = 1, 2, 4, 7, 13, ...; no three consecutive 1s)
The letter u_{n+1} is read off the low digits (certificate 2): d_0 = 0 -> 1, (1,0) -> 2, (1,1,0) -> 3.
So the fractal is the set of values of admissible digit strings, and the digit string IS the
address of a point in the hierarchy: level-1 subtile from (d_0, d_1), level-2 from the next
branch, and so on — the same three-way split at every scale.
"""
import numpy as np, time, json, sys

M = np.array([[1, 1, 1], [1, 0, 0], [0, 1, 0]], float)
IMG = {1: [1, 2], 2: [1, 3], 3: [1]}


def eig():
    w, V = np.linalg.eig(M.T)           # left eigenvectors of M = right eigenvectors of M^T
    ib = np.argmax(w.real)
    beta = w[ib].real
    ia = [i for i in range(3) if i != ib and w[i].imag > 0][0]
    alpha = w[ia]
    v = V[:, ia]
    v = v / v[0]                        # gauge: v_1 = 1, so digit-values and walk agree exactly
    return beta, alpha, v


def tribonacci(K):
    T = [1, 2, 4]
    while len(T) < K:
        T.append(T[-1] + T[-2] + T[-3])
    return np.array(T[:K], np.int64)


def word(n):
    """first n letters of the fixed point sigma^inf(1) (int8, letters 1..3)"""
    w = np.array([1], np.int8)
    lens = np.array([0, 2, 2, 1])
    img = np.array([[0, 0], [1, 2], [1, 3], [1, 0]], np.int8)
    while len(w) < n:
        L = lens[w]
        starts = np.concatenate([[0], np.cumsum(L)[:-1]])
        tot = int(L.sum())
        idx = np.repeat(np.arange(len(w)), L)
        pos = np.arange(tot) - starts[idx]
        w = img[w[idx], pos]
    return w[:n]


def digits_of(n, T):
    """greedy Tribonacci digits (low first) of integers n (array)"""
    n = np.array(n, np.int64)
    K = len(T)
    d = np.zeros((len(n), K), np.int8)
    r = n.copy()
    for j in range(K - 1, -1, -1):
        m = r >= T[j]
        d[m, j] = 1
        r[m] -= T[j]
    assert (r == 0).all()
    return d


def admissible_strings(k):
    """all digit strings of length k with no '111' as an (N,k) int8 array, low digit first"""
    if k == 0:
        return np.zeros((1, 0), np.int8)
    S = [np.zeros((1, 0), np.int8), np.array([[0], [1]], np.int8), np.array([[0, 0], [1, 0], [0, 1], [1, 1]], np.int8)]
    while len(S) <= k:
        a, b, c = S[-1], S[-2], S[-3]
        A = np.concatenate([np.zeros((len(a), 1), np.int8), a], 1)
        B = np.concatenate([np.tile([1, 0], (len(b), 1)).astype(np.int8), b], 1)
        C = np.concatenate([np.tile([1, 1, 0], (len(c), 1)).astype(np.int8), c], 1)
        S.append(np.concatenate([A, B, C], 0))
    return S[k]


def letter_of_digits(d):
    """level-1 branch (= next letter u_{n+1}) from low digits: 1 if d0=0, 2 if d0=1,d1=0, 3 if d0=d1=1"""
    return np.where(d[:, 0] == 0, 1, np.where(d[:, 1] == 0, 2, 3)).astype(np.int8)


def branch_address(d, levels):
    """the hierarchy address: successive branches of the digit string (each consumes 1, 2 or 3 digits)"""
    n = len(d); out = np.zeros((n, levels), np.int8)
    pos = np.zeros(n, np.int64)
    K = d.shape[1]
    ar = np.arange(n)
    for L in range(levels):
        d0 = d[ar, np.minimum(pos, K - 1)] * (pos < K)
        d1 = d[ar, np.minimum(pos + 1, K - 1)] * (pos + 1 < K)
        b = np.where(d0 == 0, 1, np.where(d1 == 0, 2, 3))
        out[:, L] = b
        pos = pos + np.where(b == 1, 1, np.where(b == 2, 2, 3))
    return out


def certify(n_check=200000):
    beta, alpha, v = eig()
    T = tribonacci(40)
    u = word(n_check + 2)
    walk = np.concatenate([[0], np.cumsum(v[u[:n_check] - 1])])       # z_0..z_n
    d = digits_of(np.arange(n_check + 1), T)
    dig = (d.astype(float) @ alpha ** np.arange(len(T)))
    err = np.abs(walk - dig).max()
    lett = letter_of_digits(d[1:])                                     # letter u_{n+1} for n>=1 ... d of n
    lett0 = letter_of_digits(d)                                        # n = 0..: u_{n+1}
    ok_letter = (lett0 == u[:n_check + 1]).all()
    return dict(beta=float(beta), alpha=[float(alpha.real), float(alpha.imag)], abs_alpha=float(abs(alpha)),
                beta_times_abs_alpha_sq=float(beta * abs(alpha) ** 2), v=[[float(x.real), float(x.imag)] for x in v],
                walk_vs_digits_max_err=float(err), n_checked=n_check, letter_rule_holds=bool(ok_letter))


if __name__ == '__main__':
    c = certify()
    print(json.dumps(c, indent=1))
    for k in range(1, 12):
        print(k, len(admissible_strings(k)), tribonacci(12)[k - 1])
