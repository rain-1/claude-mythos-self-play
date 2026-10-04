# Zeros of C_k((1-x)^A(1+x)^B) with N-2k = d (MO 515696).
# Duality (A,B,k)<->(k,N-k,A) turns the coefficient into a SHORT sum:
#     C_A((1-z)^k (1+z)^(k+d)) = sum_{j=A mod 2, j<=d} (-1)^((A-j)/2) C(k,(A-j)/2) C(d,j)
# Write A = 2s+e, divide by the binomial of the smallest index -> polynomial P_{d,e}(k,s) of degree ~d/2.
import sympy as sp
k, s = sp.symbols('k s')
def P(d, e):
    jmax = d if (d - e) % 2 == 0 else d - 1
    i0 = s - (jmax - e) // 2                      # smallest i = (A - jmax)/2
    tot = 0
    for j in range(e, jmax + 1, 2):
        m = (jmax - j) // 2                       # i = i0 + m
        r = sp.Integer(1)
        for t in range(m):
            r *= (k - (i0 + t)) / (i0 + t + 1)
        tot += (-1) ** ((j - e) // 2) * sp.binomial(d, j) * r
    return sp.factor(sp.numer(sp.together(tot)))
if __name__ == '__main__':
    for d in range(1, 19):
        for e in (0, 1):
            f = P(d, e)
            facs = sp.factor_list(f)[1]
            print(d, e, [(sp.Poly(g, k, s).total_degree(), mult) for g, mult in facs],
                  [g for g, _ in facs if sp.Poly(g, k, s).total_degree() == 2])
