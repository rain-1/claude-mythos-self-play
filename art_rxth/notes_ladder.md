# One curve beneath every ladder — the reciprocal-Pascal family collapses
### (MO 514552 one-parameter family; run 2026-08-24)

Family F(a,e), a>0, e>0: triangle A(n,0)=A(n,n)=e,
A(n,k) = a/A(n−1,k−1) + a/A(n−1,k) for 0<k<n.
Equal-parent map x ↦ 2a/x has fixed point s=√(2a), multiplier −1, so the
gauge d(n,k) = (−1)^n (A(n,k) − s) linearizes to plain averaging and the
2026-08-23 law d(n,k) ≈ M̄ · 2^(−n) C(n,k) holds with one constant
M̄(a,e) := lim_n ½(S_n + S_{n+1}), S_n = Σ_k (−1)^n (A(n,k) − s)
(the parity-average kills the alternating boundary-layer mass).

## Theorem 1 (reduction; proof = one line)
If B = A/λ then B satisfies the family rule with a/λ² and edge e/λ.
Taking λ = √(2a):    **M̄(a, e) = √(2a) · m(e/√(2a))**, where
m(ε) := M̄(1/2, ε) — the whole two-parameter family is ONE universal curve.
*Verified on 300 random members (a ∈ [0.05,20] log-uniform): max residual
3.0e−11 (`family_pts.json`). The 08-23 mother constant M̄(1,1) =
0.0654503304… is reproduced directly (0.06545033109, convergence err ~1e−9)
and through the reduction √2·m(1/√2) (agreement 3e−11).*

## Theorem 2 (the slope): m(1) = 0 and m′(1) = −1/2 exactly
m(1)=0: at (a,e)=(1/2,1) the triangle is identically 1.
Slope: the derivative triangle D = ∂A/∂e at e=1 satisfies D(n,0)=D(n,n)=1,
D' = −(D₁+D₂)/2; in the gauge E=(−1)^n D this is plain averaging with
forced edges (−1)^n. Row sums obey EXACTLY
   T_n = T_{n−1} + 3(−1)^n,  T_0 = 1   ⇒   T_n = 1 (n even), −2 (n odd),
because averaging preserves the row sum except for the two half-edge terms
lost at the rim (−(−1)^{n−1}) and the two new forced edges (+2(−1)^n).
Hence ½(T_n + T_{n+1}) = **−1/2 for every n** — no limit needed.
The nonlinear central difference confirms: −0.5000004 (h=1e−4, →−1/2 as h→0).
Corollary (chain rule): every family member leaves its fixed point with
∂M̄/∂e = −1/2 at e = √(2a) — a universal exit slope.

## New constant: the second zero
m crosses zero again at **e\* = 0.6119453567467…** (bisection, nrows=20000,
float64; ~11 digits). No match found against standard constants (mpmath
identify at this precision returns only overfit junk); we conjecture e\* is
a new constant. The curve's hump: max m = +0.0569117 at e = 0.7880085.
Sign structure: m < 0 on (0,e\*), m > 0 on (e\*,1), m < 0 on (1,∞).

## Asymptotics (honest status)
Deep runs (60000 rows, t=1 Richardson) still drift at the extremes:
- e→∞: |m| grows with log-log slope ≈ 1.16–1.26 (drifting down as depth
  grows); m/(e ln e) ∈ [−1.0, −0.7] unsettled. Best guess m ≍ −e^(1.2±0.1)
  or −C·e·ln e; open.
- e→0: log-log slope ≈ −1.34; m·e·ln(1/e) ≈ −0.32…−0.38 non-monotone; open.
The boundary tower L_k (settled layer) contracts at ratio −1/3 (verified;
the linear profile w_k = (−1/3)^k is exact in the derivative triangle).

## Files
`ladder.py` (curve + slope engine), `ladder2.py`/`ladder3.py` (refinements,
deep runs, e\*), `ladder_family.py` (300-member certificate),
`ladder_curve.json`, `family_pts.json`, art: `ladder_2560.png`.
