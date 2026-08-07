"""Independent brute force over ALL 2^(n^2) matrices for n<=4, straight from the
MO 513971 definition (no multiset trick) — validates sort_exact.c."""
from fractions import Fraction
from itertools import product

def R(A):  return tuple(sorted(A))
def cols(A): return tuple(tuple(row[j] for row in A) for j in range(len(A[0])))
def C(A):  return tuple(zip(*sorted(cols(A))))

def T(A):
    A = R(A); t = 1
    while True:
        if t % 2 == 1:                       # row-sorted; done iff col-sorted
            if C(A) == A: return t
            A = C(A)
        else:
            if R(A) == A: return t
            A = R(A)
        t += 1

for n in range(1, 5):
    tot, mx = 0, 0
    for bits in product((0, 1), repeat=n * n):
        A = tuple(bits[i * n:(i + 1) * n] for i in range(n))
        t = T(A); tot += t; mx = max(mx, t)
    mu = Fraction(tot, 2 ** (n * n))
    print(f"n={n}  mu={mu} = {float(mu):.9f}   maxT={mx}  (2n-3={2*n-3})")
