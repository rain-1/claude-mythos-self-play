#!/usr/bin/env python3
"""Numerical checks for MathOverflow 516177 (interleaved boustrophedon triangles).

All arithmetic is exact (int / Fraction). Single-threaded.
Run:  python3 check.py   (writes triangles.json next to this file)
"""
import json, os, random
from fractions import Fraction
from math import factorial

NMAX = 60


# ---------------------------------------------------------------- triangles
def triangles(N, c=None, c0=1):
    """T1[n][k], T2[n][k] for 1<=k<=n<=N (1-based; index 0 unused).
    c: dict/list with c[n] for n>=1 (T1(n,1)=c(n)); default all 1.
    c0: value of T2(1,1) (=1 in the question).
    Also returns the computation order (same order as the PARI list3 code)."""
    if c is None:
        c = [1] * (N + 1)
    T1 = [[0] * (N + 2) for _ in range(N + 1)]
    T2 = [[0] * (N + 2) for _ in range(N + 1)]
    order = []
    T1[1][1] = c[1]; order.append(("T1", 1, 1))
    T2[1][1] = c0;   order.append(("T2", 1, 1))
    for n in range(2, N + 1):
        T2[n][n] = T1[n - 1][n - 1]; order.append(("T2", n, n))
        T1[n][1] = c[n];             order.append(("T1", n, 1))
        for k in range(2, n + 1):
            T1[n][k] = T1[n][k - 1] + T2[n - 1][k - 1]; order.append(("T1", n, k))
        for k in range(n - 1, 0, -1):
            T2[n][k] = T2[n][k + 1] + T1[n - 1][k]; order.append(("T2", n, k))
    return T1, T2, order


def list3(n):
    """Literal transcription of the PARI code in the question (1-based via padding)."""
    v1 = [0] * (n + 1); v1[1] = 1
    v2 = v1[:]; v3 = v1[:]; v4 = v1[:]
    for i in range(2, n + 1):
        v5 = v1[:]
        v1[1] = 1
        v2[i] = v5[i - 1]
        for j in range(2, i + 1):
            v1[j] = v1[j - 1] + v2[j - 1]
        for j in range(i - 1, 0, -1):
            v2[j] = v2[j + 1] + v5[j]
        v3[i] = v1[i]; v4[i] = v2[1]
    return v3[1:], v4[1:]


# ---------------------------------------------------------------- power series (EGF coefficient lists, exact)
def mul(a, b, M):
    return [sum(a[i] * b[m - i] for i in range(m + 1)) for m in range(M + 1)]


def inv(a, M):
    r = [Fraction(0)] * (M + 1); r[0] = Fraction(1) / a[0]
    for m in range(1, M + 1):
        r[m] = -sum(a[i] * r[m - i] for i in range(1, m + 1)) / a[0]
    return r


def deriv(a):
    return [a[i + 1] * (i + 1) for i in range(len(a) - 1)] + [Fraction(0)]


def integ(a):
    return [Fraction(0)] + [a[i] / (i + 1) for i in range(len(a) - 1)]


def even(a): return [x if i % 2 == 0 else 0 for i, x in enumerate(a)]
def odd(a):  return [x if i % 2 == 1 else 0 for i, x in enumerate(a)]


M = NMAX + 3
COS = [Fraction((-1) ** (m // 2), factorial(m)) if m % 2 == 0 else Fraction(0) for m in range(M + 1)]
SIN = [Fraction((-1) ** (m // 2), factorial(m)) if m % 2 == 1 else Fraction(0) for m in range(M + 1)]
EXP = [Fraction(1, factorial(m)) for m in range(M + 1)]
SEC = inv(COS, M)
TAN = mul(SIN, SEC, M)
SPT = [s + t for s, t in zip(SEC, TAN)]


def egf_to_seq(a):  # n! [x^n]
    out = [x * factorial(i) for i, x in enumerate(a)]
    assert all(x.denominator == 1 for x in out)
    return [int(x) for x in out]


def seq_to_egf(s):
    return [Fraction(x, factorial(i)) for i, x in enumerate(s)]


# ---------------------------------------------------------------- standard boustrophedon (Millar-Sloane-Young)
def boustro(a):
    """T(N,0)=a_N, T(N,k)=T(N,k-1)+T(N-1,N-k); returns rows and b_N=T(N,N)."""
    rows = []
    for N in range(len(a)):
        r = [a[N]]
        for k in range(1, N + 1):
            r.append(r[k - 1] + rows[N - 1][N - k])
        rows.append(r)
    return rows, [r[-1] for r in rows]


def main():
    ok = True
    def check(cond, msg):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + msg)
        ok &= bool(cond)

    # 1. reproduce the question with c=1
    T1, T2, order = triangles(NMAX)
    v3, v4 = list3(NMAX)
    check(v3 == [T1[n][n] for n in range(1, NMAX + 1)] and v4 == [T2[n][1] for n in range(1, NMAX + 1)],
          "Python triangles agree with literal PARI list3, n<=%d" % NMAX)
    A003701 = egf_to_seq(mul(EXP, SEC, M))   # index 0..M
    A009739 = egf_to_seq(mul(EXP, TAN, M))
    check(all(T1[n][n] == A003701[n] for n in range(1, NMAX + 1)), "T1(n,n) = n![x^n] e^x sec x, 1<=n<=%d" % NMAX)
    check(all(T2[n][1] == A009739[n] for n in range(1, NMAX + 1)), "T2(n,1) = n![x^n] e^x tan x, 1<=n<=%d" % NMAX)
    print("   a(1..10) =", A003701[1:11]); print("   b(1..10) =", A009739[1:11])

    # 2. generalised version, random c (incl. negative), and random c0 = T2(1,1)
    rng = random.Random(516177)
    for trial in range(6):
        c0 = 1 if trial < 3 else rng.randint(-50, 50)
        c = [c0] + [rng.randint(-10 ** 6, 10 ** 6) for _ in range(NMAX + 3)]
        T1, T2, _ = triangles(NMAX, c, c0)
        C = seq_to_egf(c[:M + 1])
        a = egf_to_seq(mul(C, SEC, M)); b = egf_to_seq(mul(C, TAN, M))
        check(all(T1[n][n] == a[n] for n in range(1, NMAX + 1)) and all(T2[n][1] == b[n] for n in range(1, NMAX + 1)),
              "random c trial %d (c0=%d): T1(n,n)=n![x^n]C sec, T2(n,1)=n![x^n]C tan, n<=%d" % (trial, c0, NMAX))

    # 3. intermediate identities of the proof
    # 3a. Millar-Sloane-Young: B = (sec+tan) A for random a
    a = [rng.randint(-1000, 1000) for _ in range(M + 1)]
    _, bb = boustro(a)
    check(bb == egf_to_seq(mul(SPT, seq_to_egf(a), M)), "MSY boustrophedon theorem B=(sec+tan)A, N<=%d" % M)
    # 3b. bivariate EGF G(x,y)=sum T(i+j,i) x^i y^j/(i!j!) equals P(x+y)(cos((x-y)/2)+sin((x-y)/2)),
    #     P = A/(cos(y/2)-sin(y/2)), checked coefficientwise via T(N,k) = sum_m binom-convolution
    D = 14
    rows, _ = boustro(a[:D + 1])
    half = [Fraction(1, 2 ** m) for m in range(D + 1)]
    ch = [x * h for x, h in zip(COS[:D + 1], half)]; sh = [x * h for x, h in zip(SIN[:D + 1], half)]
    P = mul(seq_to_egf(a[:D + 1]), inv([u - v for u, v in zip(ch, sh)], D), D)   # P(s) EGF-type ordinary coeffs
    # coefficient of x^i y^j in P(x+y) f(x-y), with f = ch+sh (ordinary coefficients):
    from math import comb
    f = [u + v for u, v in zip(ch, sh)]
    def coef(i, j):
        tot = Fraction(0)
        for p in range(i + j + 1):
            q = i + j - p
            # P_p (x+y)^p * f_q (x-y)^q
            s = Fraction(0)
            for r in range(0, i + 1):           # r from (x+y)^p, i-r from (x-y)^q
                if r <= p and i - r <= q:
                    s += comb(p, r) * comb(q, i - r) * (-1) ** (q - (i - r))
            tot += P[p] * f[q] * s
        return tot
    good = all(coef(i, j) * factorial(i) * factorial(j) == rows[i + j][i]
               for i in range(D + 1) for j in range(D + 1 - i))
    check(good, "bivariate closed form of boustrophedon triangle, total degree <=%d" % D)

    # 3c. chain decomposition: each chain is a standard boustrophedon with a_N as in PROOF.md
    for trial in range(2):
        c = [1] + [rng.randint(-999, 999) for _ in range(NMAX + 3)]
        T1, T2, _ = triangles(NMAX, c, 1)
        for name, t1par in (("P", 1), ("Q", 0)):      # chain P: T1 rows with n odd; Q: n even
            rowsC = []
            for n in range(1, NMAX + 1):
                N = n - 1
                if n % 2 == t1par:
                    rowsC.append([T1[n][i + 1] for i in range(n)])
                else:
                    rowsC.append([T2[n][n - i] for i in range(n)])
            aC = [r[0] for r in rowsC]
            rowsS, bS = boustro(aC)
            same = rowsS == rowsC
            # a_N formula
            af = []
            for N in range(NMAX):
                n = N + 1
                if n % 2 == t1par: af.append(c[n])
                elif N == 0: af.append(1)
                else: af.append(bS[N - 1])
            Cpar = odd(seq_to_egf(c[:M + 1])) if name == "P" else even(seq_to_egf(c[:M + 1]))
            Fpred = egf_to_seq(deriv(mul(Cpar, SPT, M)))[:NMAX]
            Apred = egf_to_seq([u + v for u, v in zip(deriv(Cpar), mul(Cpar, SEC, M))])[:NMAX]
            check(same and af == aC and bS == Fpred and aC == Apred,
                  "chain %s (trial %d): standard boustrophedon, a_N rule, F=(C_par(sec+tan))', A=C_par'+C_par sec" % (name, trial))

    # 3d. the key series identity (sec+tan)(C' + C sec) = (C (sec+tan))' for random C
    C = seq_to_egf([rng.randint(-99, 99) for _ in range(M + 1)])
    lhs = mul(SPT, [u + v for u, v in zip(deriv(C), mul(C, SEC, M))], M)
    rhs = deriv(mul(C, SPT, M))
    check(lhs[:M - 1] == rhs[:M - 1], "identity (sec+tan)(C'+C sec) = (C(sec+tan))'")

    # 4. export for art
    T1, T2, order = triangles(16)
    out = {
        "T1": [[T1[n][k] for k in range(1, n + 1)] for n in range(1, 17)],
        "T2": [[T2[n][k] for k in range(1, n + 1)] for n in range(1, 17)],
        "order": [list(t) for t in order],
        "order_note": "computation order (triangle, n, k), 1-based, as in the PARI list3 code: "
                      "row n: T2(n,n)=T1(n-1,n-1), then T1(n,1..n) left->right, then T2(n,n-1..1) right->left",
        "chain_note": "chain P = T1 rows with n odd + T2 rows with n even; chain Q = the rest. "
                      "Each chain read along the arrows (T1 left->right, T2 right->left) is a Seidel boustrophedon.",
    }
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "triangles.json")
    with open(path, "w") as fh:
        json.dump(out, fh)
    print("wrote", path, "(", len(order), "entries in order )")
    print("ALL PASS" if ok else "SOME FAILURES")


if __name__ == "__main__":
    main()
