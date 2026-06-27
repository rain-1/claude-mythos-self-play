"""Bhargava cubes -> three binary quadratic forms -> Gauss composition = identity.

A 2x2x2 integer cube A_{ijk} can be sliced three ways into a pair of 2x2
matrices (M,N); each pair gives a binary quadratic form Q(x,y) = -det(Mx+Ny).
Bhargava (2004): the three forms share one discriminant and compose to the
identity in the form class group, [Q1][Q2][Q3] = 1.

We verify both facts directly: equal discriminant, and Gauss/Dirichlet
composition (via coprime representation + CRT) landing on the principal form.
"""
from math import gcd


def xgcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x, y = xgcd(b, a % b)
    return (g, y, x - (a // b) * y)


def cube_forms(cube):
    """cube = (a,b,c,d,e,f,g,h) -> the three forms (A,B,C), each = -det(Mx+Ny)."""
    a, b, c, d, e, f, g, h = cube
    A = {(0, 0, 0): a, (0, 0, 1): b, (0, 1, 0): c, (0, 1, 1): d,
         (1, 0, 0): e, (1, 0, 1): f, (1, 1, 0): g, (1, 1, 1): h}

    def form(M, N):
        (m11, m12), (m21, m22) = M
        (n11, n12), (n21, n22) = N
        # det(Mx+Ny) = (detM)x^2 + (mixed)xy + (detN)y^2 ; Q = -det
        a2 = -(m11 * m22 - m12 * m21)
        b2 = -(m11 * n22 + n11 * m22 - m12 * n21 - n12 * m21)
        c2 = -(n11 * n22 - n12 * n21)
        return (a2, b2, c2)

    # slice on first index i
    M1 = ((A[0, 0, 0], A[0, 0, 1]), (A[0, 1, 0], A[0, 1, 1]))
    N1 = ((A[1, 0, 0], A[1, 0, 1]), (A[1, 1, 0], A[1, 1, 1]))
    # slice on second index j
    M2 = ((A[0, 0, 0], A[0, 0, 1]), (A[1, 0, 0], A[1, 0, 1]))
    N2 = ((A[0, 1, 0], A[0, 1, 1]), (A[1, 1, 0], A[1, 1, 1]))
    # slice on third index k
    M3 = ((A[0, 0, 0], A[0, 1, 0]), (A[1, 0, 0], A[1, 1, 0]))
    N3 = ((A[0, 0, 1], A[0, 1, 1]), (A[1, 0, 1], A[1, 1, 1]))
    return [form(M1, N1), form(M2, N2), form(M3, N3)]


def disc(f):
    a, b, c = f
    return b * b - 4 * a * c


def reduce_def(f):
    """Reduce a positive-definite form (D<0) to -a<b<=a<=c (b>=0 if a==c)."""
    a, b, c = f
    D = disc(f)
    if a < 0:
        a, b, c = -a, -b, -c
    for _ in range(100000):
        if c < a or (a == c and b < 0):
            a, b, c = c, -b, a                      # swap step
        elif b > a or b <= -a:
            t = (a - b) // (2 * a)                  # bring b into (-a, a]
            b = b + 2 * a * t
            c = (b * b - D) // (4 * a)
        else:
            break
    return (a, b, c)


def transform(f, x, z, y, w):
    """Apply M=[[x,z],[y,w]] (det 1): new form g with g(s,t)=f(xs+zt, ys+wt)."""
    a, b, c = f
    A = a * x * x + b * x * y + c * y * y
    C = a * z * z + b * z * w + c * w * w
    B = 2 * a * x * z + b * (x * w + z * y) + 2 * c * y * w
    return (A, B, C)


def represent_coprime(f, k):
    """Return a form equivalent to f whose leading coeff a' is coprime to k."""
    a, b, c = f
    if gcd(a, k) == 1:
        return f
    if gcd(c, k) == 1:
        return transform(f, 0, -1, 1, 0)   # swap variables: a'<-c
    # search small (x,y) coprime with gcd(f(x,y),k)=1, complete to SL2 basis
    for s in range(1, 40):
        for x in range(-s, s + 1):
            for y in range(-s, s + 1):
                if gcd(x, y) != 1:
                    continue
                val = a * x * x + b * x * y + c * y * y
                if gcd(val, k) == 1:
                    g, w, z = xgcd(x, y)       # x*w + y*z = 1
                    # basis [[x, -z],[y, w]] has det x*w + z*y = 1
                    return transform(f, x, -z, y, w)
    raise RuntimeError("no coprime representative found")


def compose(f1, f2):
    """Dirichlet/Gauss composition of two primitive forms of the same disc."""
    D = disc(f1)
    assert disc(f2) == D, "forms must share a discriminant"
    f2 = represent_coprime(f2, f1[0])
    a1, b1, _ = f1
    a2, b2, _ = f2
    assert gcd(a1, a2) == 1
    # CRT: B ≡ b1 (mod 2a1), B ≡ b2 (mod 2a2)
    g, p, q = xgcd(2 * a1, 2 * a2)            # = 2 gcd(a1,a2) = 2
    # b1 ≡ b2 mod 2 (same disc parity) so solvable
    m1, m2 = 2 * a1, 2 * a2
    L = m1 * m2 // g                          # lcm
    B = (b1 + m1 * ((b2 - b1) // g) * p) % L
    a3 = a1 * a2
    # make B the right residue mod 2a3 with B^2 ≡ D (mod 4a3)
    while (B * B - D) % (4 * a3) != 0:
        B += L
    c3 = (B * B - D) // (4 * a3)
    return reduce_def((a3, B, c3))


def compose_list(forms):
    r = reduce_def(forms[0])
    for f in forms[1:]:
        r = compose(r, reduce_def(f))
    return r


if __name__ == "__main__":
    # --- test composition on D=-23 (class group C3): g=(2,1,3), g^3=1 ---
    g = (2, 1, 3); one = (1, 1, 6)
    print("D(-23) g =", g, "disc", disc(g))
    g2 = compose(g, g); print("g*g =", g2, "(expect (2,-1,3))")
    g3 = compose(g2, g); print("g*g*g =", g3, "(expect principal (1,1,6))")
    print("principal*g =", compose(one, g), "(expect g)")

    # --- a Bhargava cube ---
    for cube in [(0, 1, 1, 1, 1, 0, 0, 1), (1, 0, 0, 1, 0, 1, 1, 0),
                 (0, 1, 1, 0, 1, 0, 0, 2), (1, 1, 0, 1, 0, 1, 2, 0)]:
        F = cube_forms(cube)
        Ds = [disc(f) for f in F]
        if len(set(Ds)) == 1 and Ds[0] < 0 and all(f[0] != 0 for f in F):
            red = [reduce_def(f) for f in F]
            comp = compose_list(F)
            print("\ncube", cube, " disc", Ds[0])
            print("  forms        ", F)
            print("  reduced      ", red)
            print("  composition  ", comp, "  identity?", comp == reduce_def((1, Ds[0] % 2, (Ds[0] % 2 - Ds[0]) // 4)))
