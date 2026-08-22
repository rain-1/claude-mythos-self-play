"""Fiber analysis for the K3 surface x^4+y^4+z^4 = 51 t^4 (MO 514531).

Fiber at z/t = p/q (primitive, M = 51 q^4 - p^4 > 0):
  rational point on surface with z/t=p/q  <=>  rational point on the genus-3
  plane quartic  C_M : X^4 + Y^4 = M Z^4   (x = X/(Z q), y = Y/(Z q)).
C_M has quotients:
  conic  Q_M : r^2 + s^2 = M u^2          (r=X^2,s=Y^2,u=Z^2)
  genus-1 D_M : a^2 = M - v^4             (v = Y/Z, a = X^2/Z^2)
and a point of C_M is exactly a point (v,a) of D_M with a a rational SQUARE.

Local solubility of D_M over Q_p — closed-form criteria (derived this run,
validated by brute force in validate_local()):
  * p == 1 mod 4 (and p odd): always soluble (points near v-infinity).
  * p == 3 mod 4, m = v_p(M), M' = M/p^m:
      m odd                -> insoluble
      m == 2 mod 4         -> soluble iff chi_p(M') = 1
      m == 0 mod 4         -> soluble iff chi_p(M')=1 or exists unit r mod p
                              with M'-r^4 == 0 mod p or chi_p(M'-r^4)=1
  * p == 2, m = v_2(M), M' = M/2^m:
      soluble iff (m==1 mod 4 and M'==1 mod 4)
               or (m even and M'==1 mod 8)
               or (m==2 mod 4 and M'==5 mod 8)
               or (m==0 mod 4 and M'==5 mod 16)
  * real place: M > 0.
Conic Q_M soluble <=> for all p==3 mod 4, v_p(M) even  (sum of two squares).
"""
from sympy import factorint
import math

def chi(a, p):
    """Legendre symbol a/p for odd prime p, a not divisible by p -> +-1."""
    r = pow(a % p, (p - 1) // 2, p)
    return 1 if r == 1 else -1

def vp(n, p):
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v, n

def d_local_odd3(M, p):
    """Local solubility of a^2 = M - v^4 over Q_p, p == 3 mod 4 odd."""
    m, Mp = vp(M, p)
    if m % 2 == 1:
        return False
    if m % 4 == 2:
        return chi(Mp, p) == 1
    # m == 0 mod 4
    if chi(Mp, p) == 1:
        return True
    for r in range(1, p):
        w = (Mp - pow(r, 4, p)) % p
        if w == 0 or chi(w, p) == 1:
            return True
    return False

def d_local_2(M):
    m, Mp = vp(M, 2)
    if m % 4 == 1 and Mp % 4 == 1: return True
    if m % 2 == 0 and Mp % 8 == 1: return True
    if m % 4 == 2 and Mp % 8 == 5: return True
    if m % 4 == 0 and Mp % 16 == 5: return True
    return False

def d_locally_soluble(M, fac=None):
    """(soluble?, obstruction_witness) for D_M over all completions."""
    if M <= 0:
        return False, 'real'
    if not d_local_2(M):
        return False, 2
    if fac is None:
        fac = factorint(M)
    for p in fac:
        if p % 4 == 3 and not d_local_odd3(M, p):
            return False, p
    return True, None

def conic_soluble(M, fac=None):
    """r^2+s^2 = M u^2 soluble <=> M>0 and no p==3 mod 4 to odd order."""
    if M <= 0:
        return False, 'real'
    if fac is None:
        fac = factorint(M)
    for p, e in fac.items():
        if p % 4 == 3 and e % 2 == 1:
            return False, p
    return True, None

# ---------- brute-force validators ----------
def brute_qp_soluble(M, p, kmax=None):
    """Brute-force: does a^2 = M - v^4 have a Q_p-point?  Checks integral v
    (mod p^k lifting with Hensel certificate) and the v=1/w chart
    b^2 = M w^4 - 1 with w in pZ_p."""
    def f1(x): return M - x**4          # chart 1, v integral
    def f2(x): return M * x**4 - 1      # chart 2, w = 1/v in pZp

    def zp_sol(f, p, only_multiples_of_p=False):
        # BFS on x mod p^k; a branch survives if y^2 == f(x) mod p^k might
        # still have solutions; certify solubility via Hensel: exists x0 with
        # val = v_p(f(x0)) even and finite, unit part square mod p (p odd) or
        # mod 8 (p=2), and the value stable on the whole branch
        # (k - val >= 3 for p=2, >= 1 for odd p).
        frontier = [(0, 0)] if not only_multiples_of_p else [(0, 1)]
        for depth in range(40):
            newf = []
            for (x0, k) in frontier:
                pk = p ** k
                step = p ** (k + 1)
                for r in range(p):
                    x = x0 + r * pk if k > 0 or not only_multiples_of_p else (x0 + r * pk)
                    fx = f(x)
                    if fx == 0:
                        return True
                    v = 0
                    t = fx
                    while t % p == 0:
                        t //= p
                        v += 1
                    # value determined mod p^(4?)... conservative margin:
                    margin = (k + 1) * 1 - v  # digits of f known beyond val:
                    # f(x + p^(k+1) s) = f(x) + f'(x) p^(k+1) s + ...
                    # so f known mod p^(k+1) at least (f' integral)
                    if margin >= (3 if p == 2 else 1):
                        # valuation exact and unit part determined enough
                        if v % 2 == 0:
                            if p == 2:
                                if margin >= 3 and t % 8 == 1:
                                    return True
                            else:
                                if chi(t, p) == 1:
                                    return True
                        # else: this x needs deeper look only if f can still
                        # change class -> no: val exact, class exact -> dead
                        # branch for this x, but other lifts x+p^(k+1)s share
                        # the SAME f-class up to margin -> whole sub-branch
                        # dead; do not re-add.
                        continue
                    newf.append((x, k + 1))
            frontier = newf
            if not frontier:
                return False
        raise RuntimeError(f'ambiguous at M={M} p={p}')
    if p == 2:
        return zp_sol(f1, 2) or zp_sol(f2, 2, True)
    return zp_sol(f1, p) or zp_sol(f2, p, True)

def validate_local(pmax=23, Mmax=400):
    """Compare closed-form criteria against brute force."""
    bad = []
    for p in [2] + [q for q in range(3, pmax) if all(q % r for r in range(2, q)) and q % 4 == 3]:
        for M in range(1, Mmax):
            closed = d_local_2(M) if p == 2 else d_local_odd3(M, p)
            brute = brute_qp_soluble(M, p)
            if closed != brute:
                bad.append((p, M, closed, brute))
    return bad
