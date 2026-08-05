#!/usr/bin/env python3
"""Independent verification of the necessity proof for MO 513606, via the
half-unit tau = (sqrt6+sqrt2)/2, tau^2 = omega = 2+sqrt3, N = 2^(n-1)+3 prime.

Chain (our proof, cleaner than the posted Chebyshev one):
  1. n>=4: N === 3 mod 8  =>  (2/N) = -1.
  2. n odd: N === 19 mod 24: (3/N) = -1, (6/N) = +1.
     Frobenius fixes sqrt6, negates sqrt2 => tau^N = tau'=(sqrt6-sqrt2)/2,
     tau^(N+1) = tau tau' = 1 = omega^((N+1)/2); (N+1)/2 = 2^(n-2)+2
     => omega^m = omega^(-2), s(n-2) = 14.       [m = 2^(n-2)]
  3. n even: N === 11 mod 24: (3/N) = +1, (6/N) = -1.
     Frobenius negates both => tau^N = -tau, omega^((N-1)/2) = tau^(N-1) = -1;
     (N-1)/2 = 2^(n-2)+1 => omega^m = -omega^(-1), s(n-2) = -(omega+1/omega) = -4.
We verify 1-3 plus the endpoint for every prime N = 2^(n-1)+3 with n <= 800,
doing GF(N^2) arithmetic from scratch (pairs (a,b) = a + b sqrt3)."""
import gmpy2
from gmpy2 import mpz, jacobi

def gf2_mul(x, y, N, D):  # elements a + b*sqrtD
    (a, b), (c, d) = x, y
    return ((a * c + D * b * d) % N, (a * d + b * c) % N)

def gf2_pow(x, e, N, D):
    r = (mpz(1), mpz(0))
    while e:
        if e & 1: r = gf2_mul(r, x, N, D)
        x = gf2_mul(x, x, N, D)
        e >>= 1
    return r

primes_checked = 0
for n in range(4, 801):
    N = (mpz(1) << (n - 1)) + 3
    if not gmpy2.is_prime(N): continue
    primes_checked += 1
    assert N % 8 == 3 and jacobi(2, N) == -1, n
    m = mpz(1) << (n - 2)
    omega = (mpz(2), mpz(1))
    if n % 2 == 1:
        assert N % 24 == 19 and jacobi(3, N) == -1 and jacobi(6, N) == 1, n
        t = gf2_pow(omega, (N + 1) // 2, N, 3)
        assert t == (1, 0), (n, "omega^((N+1)/2) != 1")
        w = gf2_pow(omega, m, N, 3)          # should be omega^(-2) = 7-4sqrt3
        assert w == (7 % N, (-4) % N), (n, "omega^m != omega^-2")
    else:
        assert N % 24 == 11 and jacobi(3, N) == 1 and jacobi(6, N) == -1, n
        t = gf2_pow(omega, (N - 1) // 2, N, 3)
        assert t == (N - 1, 0), (n, "omega^((N-1)/2) != -1")
        w = gf2_pow(omega, m, N, 3)          # should be -omega^(-1) = -2+sqrt3
        assert w == ((-2) % N, 1 % N), (n, "omega^m != -omega^-1")
    # endpoint: s(n-2) = trace(omega^m) = 2*first component
    s = (2 * w[0]) % N
    target = mpz(14) % N if n % 2 else (N - 4) % N
    assert s == target, (n, "endpoint mismatch")
print(f"necessity chain verified for all {primes_checked} primes N=2^(n-1)+3, n in [4,800]")
