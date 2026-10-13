# MO 515969: symmetric primitive Dyck paths by area

Notation: `Phi(z;q) = sum_{j>=0} (-1)^j q^{j(j-1)} z^j/(q;q)_j`, all series formal in `x`, `q = x^4`.

## 1. Verification (computational)

- `verify.py N`: transfer-matrix enumeration of first halves (P_0=0, P_1=1, P_j>=1, area
  `2*sum_{j<h}P_j + P_h`) vs. the conjectured formula, exact integer arithmetic.
  **Agreement for all n <= 6000** (54 s, one core). `d_upto_6000.json` holds d(0..6000).
- `make_paths.py`: brute-force DFS of all paths of area 1..40 (131 paths) -> `paths.json`
  (`{"n": [[P_0,...,P_2h], ...]}`, keys "1".."40", sorted by length then lexicographically);
  counts match d(n).
- `lemma_check.py`: checks the per-endpoint lemma below for every m with m^2 <= 800, up to x^800.

## 2. Proof — COMPLETE

**Step 1 (excursions = Rogers–Ramanujan type continued fraction).**
Give a vertex at height k the weight x^{2k}. Let `D_k` = GF of excursions that start and end at
height k and stay >= k, counting every vertex except the final one. First-return decomposition:
an excursion is a sequence of arches; an arch is (vertex at k) · up · (excursion at level k+1,
last vertex excluded) · (that last vertex at k+1) · down, of weight `x^{2k} D_{k+1} x^{2k+2}`. So

    D_k = 1 / (1 - x^{4k+2} D_{k+1}),   i.e.   D_k = 1/(1 - z q^k/(1 - z q^{k+1}/(1 - ...))),  z = x^2.

From the definition, `Phi(z) - Phi(zq) = sum_{j>=1} (-1)^j q^{j(j-1)} z^j/(q;q)_{j-1} = -z Phi(zq^2)`,
i.e. `Phi(z) = Phi(zq) - z Phi(zq^2)`. Hence `R_k := Phi(z q^{k+1})/Phi(z q^k)` satisfies the same
recursion `R_k = 1/(1 - z q^k R_{k+1})`. Both D_k and R_k are power series = 1 + O(x^{4k+2}); the
recursion determines the solution uniquely x-adically (D_k mod x^{L} is determined by D_{k+1} mod
x^{L-4k-2}), so

    D_k = Phi(x^{4k+6}; x^4) / Phi(x^{4k+2}; x^4).

**Step 2 (meanders by last passage).** A first half ending at height m >= 1 is
`0 -> 1`, then a path from 1 to m staying >= 1. Cutting at the last visit to each level
1,2,...,m gives a unique factorisation `E_1 · up · E_2 · up · ... · up · E_m`, with E_k an
excursion at level k. Weights: P_0 contributes x^0; the non-final vertices of E_k give D_k; the
final vertex of E_k (height k) gives x^{2k} for k < m, and the middle point P_h = m gives x^m.
Therefore

    F_m(x) = x^{m(m-1)} x^m prod_{k=1}^m D_k = x^{m^2} Phi(x^{4m+6}; x^4) / Phi(x^6; x^4)

(the product telescopes). **Lemma** (verified independently, `lemma_check.py`).

**Step 3.** Summing over m >= 1 and putting m = r+1 (so m^2 = r(r+2)+1, 4m+6 = 4r+10):

    A(x) = sum_m F_m = x/Phi(x^6;x^4) * sum_{r>=0} x^{r(r+2)} Phi(x^{4r+10}; x^4).   QED

So the "4r+10" is indeed the endpoint height (4m+6 with m = r+1), and the r-sum is a sum over
the height of the middle point. Equivalent continued-fraction form:
`A(x) = sum_{m>=1} x^{m^2} D_1 D_2 ... D_m`, `D_1 = 1/(1 - x^6/(1 - x^10/(1 - x^14/(1 - ...))))`.

## 3. Asymptotics (numerical, standard dominant-pole analysis)

Growth is **exponential**, not exp(c sqrt n). g(x) = Phi(x^6;x^4) is even in x and has its
smallest zeros at x = ±rho, rho = 0.8990089195827778728 (rho^2 = smallest positive zero of
Phi(y^3;y^2)). The numerator `sum_m x^{m^2} Phi(x^{4m+6};x^4)` is analytic in |x|<1, giving

    d(n) ~ (a + b(-1)^n) rho^{-n},  1/rho = 1.11233601604764,
    a = -N(rho)/(rho g'(rho)) = 0.1934474326535823,  b = -N(-rho)/(rho g'(rho)) = -0.0129281077813821.

Check (`asymptotics.py`): ratio d(n)/prediction = 0.99974 (n=100), 1 - 1.7e-14 (n=500), 1 to 25
digits for n = 1000..6000. The relative error decays like ~0.941^n, suggesting
(**observation, numerical**) the next singularities have modulus ≈ 0.955. The small parity
oscillation (b/a ≈ -0.067: even n get factor a+b, odd n get a-b, so odd areas are ~14% more
frequent asymptotically) comes from the pole at -rho.

## 4. Remarks / observations

- (Observation) The same argument gives the bivariate refinement by middle height:
  `sum_m u^m F_m = Phi(x^6;x^4)^{-1} sum_{m>=1} u^m x^{m^2} Phi(x^{4m+6};x^4)`. With t marking the
  semilength h (t per step of the half path), z = x^2 becomes t^2 x^2 and the m forced up-steps give
  t^m: `F_m(x,t) = t^m x^{m^2} Phi(t^2 x^{4m+6};x^4)/Phi(t^2 x^6;x^4)` (follows from the same proof;
  not separately machine-checked).
- The proof uses nothing beyond the Flajolet continued fraction for excursions and the
  three-term recurrence of Phi; nothing about the identity is special to symmetric paths except
  the half-weight x^m on the middle vertex, which is exactly what produces x^{m^2}.
