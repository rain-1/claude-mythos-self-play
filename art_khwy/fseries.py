"""MO 513816: F(x) = sum 3^-n sqrt(1 + x/4^n).  Verification suite.

Claims to certify numerically (proofs in verification.md):
 C1. Functional equation F(x) = sqrt(1+x) + F(x/4)/3          (exact identity)
 C2. Coefficient law  c_m = binom(1/2,m) / (1 - 4^-m/3)
 C3. Hadamard factor  L(x) = sum_m x^m/(1-4^-m/3) = sum_j 3^-j/(1-x/4^j)
     (poles at +4^j mirror F's branch points at -4^j)
 C4. Branch jump across the cut on (-4^(m+1), -4^m):
     Im F(x + i0) = sum_{j<=m} 3^-j sqrt(|1+x/4^j|)   (only first m+1 flip)
 C5. Asymptotics F(x) = (6/5) sqrt(x) + x^(-log_4 3) Phi(log_4 x) + O(1/sqrt x),
     Phi periodic with period 1  (log-periodic wobble, exponent log3/log4
     = the Cantor-ish exponent of the (3,4) system)
"""
import mpmath as mp
mp.mp.dps = 60

def F_direct(x, terms=220):
    return mp.fsum(mp.power(3, -n) * mp.sqrt(1 + x * mp.power(4, -n))
                   for n in range(terms))

def F_funceq(x, depth=100):
    """Continue via F(x) = sqrt(1+x) + F(x/4)/3 down to tiny argument."""
    s = mp.mpf(0); w = mp.mpf(1)
    for k in range(depth):
        s += w * mp.sqrt(1 + x / mp.power(4, k))
        w /= 3
    # remainder: F(x/4^depth) ~ 3/2 for tiny arg (F(0) = 3/2)
    s += w * mp.mpf(3) / 2 * 3  # w already divided; F(tiny)=3/2, factor w*3? no:
    return s

# --- C1: functional equation ---
for x in [mp.mpf('0.37'), mp.mpf('2.5'), mp.mpc(1, 2), mp.mpc(-0.4, 0.9)]:
    lhs = F_direct(x)
    rhs = mp.sqrt(1 + x) + F_direct(x / 4) / 3
    print("C1 residual", mp.nstr(abs(lhs - rhs), 3))

# --- C2: coefficients ---
import math
def coeff_num(m, dps=60):
    # m-th Taylor coefficient by high-order finite differences on a tiny circle
    mp.mp.dps = dps
    R = mp.mpf('0.25'); Npts = 64
    s = mp.mpf(0)
    vals = [F_direct(R * mp.expjpi(2 * mp.mpf(k) / Npts)) for k in range(Npts)]
    c = mp.fsum(vals[k] * mp.expjpi(-2 * mp.mpf(k * m) / Npts)
                for k in range(Npts)) / Npts / R**m
    return c

for m in [0, 1, 2, 5, 11]:
    pred = mp.binomial(mp.mpf(1)/2, m) / (1 - mp.power(4, -m)/3)
    got = coeff_num(m)
    print(f"C2 m={m}: |got-pred| =", mp.nstr(abs(got - pred), 3))

# --- C3: Hadamard partner: two representations of L ---
for x in [mp.mpf('0.7'), mp.mpc(0.3, 0.5), mp.mpf('-2.3')]:
    L1 = mp.fsum(x**m / (1 - mp.power(4, -m)/3) for m in range(400)) \
        if abs(x) < 1 else None
    L2 = mp.fsum(mp.power(3, -j) / (1 - x / mp.power(4, j)) for j in range(200))
    if L1 is not None:
        print("C3 residual", mp.nstr(abs(L1 - L2), 3))

# --- C4: branch jump on (-16, -4), i.e. m=1: first two terms flipped ---
for xr in ['-5.0', '-9.7', '-15.2']:
    x = mp.mpc(mp.mpf(xr), mp.mpf('1e-30'))
    jump = F_direct(x).imag
    pred = mp.fsum(mp.power(3, -j) * mp.sqrt(abs(1 + mp.mpf(xr) / 4**j))
                   for j in range(2))
    print(f"C4 x={xr}: Im F(x+i0) - pred =", mp.nstr(abs(jump - pred), 3))
# and on (-4,-1), m=0: only first term flipped
x = mp.mpc(mp.mpf('-2.5'), mp.mpf('1e-30'))
print("C4 x=-2.5:", mp.nstr(abs(F_direct(x).imag - mp.sqrt(mp.mpf('1.5'))), 3))

# --- C5: log-periodic wobble ---
print("C5: G(x) = (F(x) - (6/5)sqrt(x)) * x^(log_4 3); sample over 2 periods:")
lg3 = mp.log(3) / mp.log(4)
rows = []
for u in [mp.mpf(k) / 8 for k in range(17)]:   # u = log_4 x fractional part steps
    x = mp.power(4, 20 + u)                     # deep asymptotic regime
    G = (F_direct(x, terms=300) - mp.mpf(6)/5 * mp.sqrt(x)) * mp.power(x, lg3)
    rows.append((u, G))
for u, G in rows[:9]:
    print(f"  u={mp.nstr(u,3):6}  Phi={mp.nstr(G, 12)}")
# periodicity check: compare u and u+1 at x*4 (same fractional part)
x1 = mp.power(4, mp.mpf('20.3')); x2 = x1 * 4
G1 = (F_direct(x1, 300) - mp.mpf(6)/5*mp.sqrt(x1)) * mp.power(x1, lg3)
G2 = (F_direct(x2, 300) - mp.mpf(6)/5*mp.sqrt(x2)) * mp.power(x2, lg3)
print("C5 periodicity |Phi(u) - Phi(u+1)| =", mp.nstr(abs(G1 - G2), 3),
      " (should be ~ x^(lg3-1/2) correction size)")
