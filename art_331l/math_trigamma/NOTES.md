# MO 516002: S = sum_{n>=1} [psi'(1-in) - psi'(1+in) - 2i/n]

## Result (numerically certain to ~95 digits)
S = i*T,
T = -0.48197675632314710911170383198462159135973534627147351787027133860811921057804351843257443137939329739...

T computed two independent ways (agree to 95 digits between N=300 and N=500 runs, `compute2.py`):
direct sum for n<N, with the tail summed from the asymptotic expansion
psi'(1-in)-psi'(1+in) - 2i/n ~ 2i sum_k (-1)^k B_{2k} / n^{2k+1}  (summed with Hurwitz zeta(2k+1, N)).

## Closed form?
No elementary closed form found. PSLQ at 95-98 digits (`ident2.py`, `ident3.py`, `verify.py`) found no relation
with coefficients up to about 10^3 to 10^4 over bases built from {1, pi, 1/pi, pi^2} x {1, gamma, log2, log pi, log Gamma(1/4), log A},
plus Catalan G, G/pi, zeta(3)/pi^k, sqrt2, log(1+sqrt2). The analysis below suggests why: T is the "odd" (imaginary) part of a
quadrant lattice sum, which symmetry does not fix. (The real part is fixed: it is equivalent to E_2(i) = 3/pi.)

## Derivation of the best reduction
1. psi'(1+z) = sum_{m>=1} (m+z)^{-2}, and Im (m+in)^{-2} = -2mn/(m^2+n^2)^2, so
   psi'(1-in)-psi'(1+in) = -2i Im psi'(1+in) and T = -2 sum_n [Im psi'(1+in) + 1/n] = "sum_{m,n>=1} 4mn/(m^2+n^2)^2" (rows regularised).
2. Laplace transform along the ray t = w u with w = e^{-i pi/4}: Re(w(m+in)) = (m+n)/sqrt2 > 0, so no poles lie on the ray, and
   sum_{m,n>=1} e^{-(m w + n wbar) u} = 1/|e^{wu}-1|^2  (because wbar/w = i).
   Hence Q := sum_{m,n>=1}(m+in)^{-2} = -i * int_0^inf u du/|e^{wu}-1|^2, which is formally purely imaginary.
   Matching the row cutoff to the u-cutoff gives (checked to 49 digits in `ray.py`, then to 61 digits):
   T = 2 lim_{d->0} [ int_d^inf u du/|e^{wu}-1|^2 + log d ].
3. Rescale u = sqrt2 x and use Frullani to get the fast, exponentially convergent integral

   **T = 2 int_0^inf [ 2x/(e^{2x} - 2e^x cos x + 1) - e^{-x}/x ] dx + log 2 - 2 gamma**   (verified to 61 digits, `verify.py`)

4. Mellin form: int_0^inf u^{s-1} u/|e^{wu}-1|^2 du = Gamma(s+1) w^{-s-1} Z(s+1), where Z(w) = sum_{m,n>=1}(m+in)^{-w} = zeta_2(w; 1+i | 1, i)
   is a Barnes double zeta (checked at s=2 to 30 digits). Write Z(w) = -i/(w-2) + Z0 + O(w-2). Taking the constant term at w=2 gives:
   - Re Z0 = -pi/4. This is the real-part identity, equivalent to sum k/(e^{2 pi k}-1) = 1/24 - 1/(8 pi).
   - T = 2(1 - gamma - Im Z0).
   Because d_a^2 zeta_2'(0,a) = CT_{s=2} zeta_2(s,a) + Res, we get Z0 = (log Gamma_2)''(1+i | 1, i) + i. So
   **T = -2 gamma - 2 Im (log Gamma_2)''(1+i | 1, i)**  (Barnes double gamma, periods 1, i, standard zeta_2 normalisation).
   This is the double-gamma analogue of Im psi'(1+i), which also has no known elementary form.

## Files
compute2.py (high-precision sum), ray.py / verify.py (integral representations, Mellin check, PSLQ), ident2.py / ident3.py (PSLQ).
