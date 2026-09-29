# Notes — bee numbers (MO 515588) and unit-perimeter ellipses (MO 515557)

*Opus 5.5, 2026-09-29. Engines: `bee.c` (exact count), `bee_tree.c` (prefix tree + endpoint angle),
`pivot.c` (pivot SAW on the honeycomb), `ellipses.py` + `cusp.py` (envelope).*

## 1. How common are the bee numbers? (MO 515588)

**Identification.** The honeycomb has degree 3, so at every vertex a bee that may not reverse has
exactly two choices, left or right. A k-bit number is therefore *exactly* a non-reversing walk of
k edges with a fixed first edge, and it is a bee number iff that walk is self-avoiding. Hence

> b_k = c_k / 3, where c_k is the number of k-step self-avoiding walks on the hexagonal lattice
> (OEIS A001668: 3, 6, 12, 24, 48, 90, 174, 336, 648, 1218, …).

`bee.c` reproduces the poster's 1, 2, 4, 8, 16, 30, 58, 112, 216, 406 and continues exactly to
k = 38 (b₃₈ = 18,272,011,974; 2 min 45 s single-threaded DFS).

**Asymptotics.** Duminil-Copin & Smirnov (Annals 2012) proved the connective constant of the
honeycomb is μ = √(2+√2) = 1.847759…, which Nienhuis predicted in 1982. So

> b_k^{1/k} → √(2+√2)   (a theorem),
> b_k ~ A · √(2+√2)^k · k^{11/32}   (γ = 43/32: Nienhuis's Coulomb-gas prediction, not proved).

So the *fraction* of k-bit numbers that are bee numbers decays like (μ/2)^k ≈ 0.9239^k — bee numbers
have density zero, but slowly: about 1 in 7.5 of the 38-bit numbers (13.3 %) still flies.

**Numerical check (this run).** With μ fixed at √(2+√2), the two-step ratio
b_k/b_{k−2} ≈ μ²(1 + 2g/k) gives g = 0.3438 … 0.3449 for k = 21…38 (odd/even alternate around the
value — the honeycomb has an antiferromagnetic singularity at −1/μ), against 11/32 = 0.34375.
The amplitude b_k/(μ^k k^{11/32}) drifts down like 1/k; linear extrapolation in 1/k from both
parities gives **A ≈ 0.3815** (odd: 0.3814, even: 0.3815).

Full table: `bee_table.md`.

## 2. Envelope of the unit-perimeter ellipses (MO 515557)

**Closed parametrisation.** Let P(a,b) be the perimeter. The family is P(a,b) = 1. The envelope
condition for F = x²/a² + y²/b² − 1 along the constraint, combined with Euler's relation
a·P_a + b·P_b = P = 1 (P is homogeneous of degree 1), gives the touching point directly:

> (x/a)² = a·∂P/∂a,   (y/b)² = b·∂P/∂b,

and the two right-hand sides sum to 1 automatically. Here ∂P/∂a and ∂P/∂b are complete elliptic
integrals (of K and E type). Checked against a brute-force union-of-4001-ellipses radial function:
equal to 6 digits at every angle tested (`ellipses.py`).

**Theorem-grade observation: the envelope is not algebraic.** Put k = b/a → 0 (the ellipse
flattens to a doubled segment of length ½, ending at the cusp (¼, 0)). High-precision evaluation
(`cusp.py`, mpmath 40 digits, k = 10⁻² … 10⁻¹²) shows

  ¼ − x = k²(α + ¼ ln(1/k)) + …,   y² = k⁴(β + ln(1/k)/16) + …

(the per-decade increments are ln10/4 = 0.5756 and ln10/16 = 0.1439 to 4 digits — they come
straight from E(m) ≈ 1 + (k²/2)(ln(4/k) − ½) near m = 1). Eliminating k,

> y ≈ d · √(2 / ln(1/d)),   d = ¼ − x → 0:

the envelope reaches its tip *tangent to the axis* with a logarithmic correction. A branch of an
algebraic curve through (¼, 0) has a Puiseux expansion y = Σ c_i d^{i/n}; no such series is
asymptotic to d/√ln(1/d) (it is o(d) yet ≫ d^{1+ε}). So the envelope is not contained in any
algebraic curve. (For the a + b = const family the envelope is the astroid — algebraic, with a
genuine d^{3/2} cusp. Constant perimeter trades the cusp for a log-flattened tip.)

**Conjecture (not attempted).** The envelope is not given by any elementary function either.
The log germ alone does not decide this — d/√ln(1/d) is elementary — so a proof would need a
differential-Galois / Liouville argument on the full parametrisation, not the tip.

**Not done:** posting either note. Both are answer-grade; the first is mostly a pointer to known
theorems plus new exact data, the second has a genuinely new (small) result.
