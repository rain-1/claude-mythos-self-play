# How many pieces does a rolling-shutter needle break into?

**Setting.** A thin radial needle of length R spins about its hub at k turns per frame. A rolling shutter reads
row y (measured from the hub row) at a time proportional to y, so row y sees the needle at angle
θ(y) = M + c·y, where c = 2πk/H and M is the phase. Scale so that R = 1 and put **e = c·R** (the "eccentricity"
at the tip). Row y meets the needle segment {(r cos θ, r sin θ) : 0 ≤ r ≤ 1} iff r = y / sin θ(y) ∈ [0, 1].
So the rows that show the needle form the set

  S = { y ∈ [−1, 1] : 0 ≤ y / sin(M + e y) ≤ 1 },  with y = 0 (the hub) always in S.

On S the image point x = y·cot θ(y) is continuous, and different components of S occupy disjoint, separated
bands of rows. So **pieces = number of connected components of S**.

**Theorem.** Let M be uniform mod 2π and e ≥ π. Then

  E[pieces] = e/π + ½ + B(e),  with  1/(2πe) ≤ B(e) ≤ π/(8e).

In particular E[pieces] = e/π + ½ + O(1/e), which proves the conjecture. Numerically e·B(e) ≈ 1/(2π) ≈ 0.159.

## Proof

**1. Split at the hub.** For y > 0 the condition reads sin θ(y) ≥ y. For y < 0, writing y = −s, it reads
sin(e s − M) ≥ s. Define

  S₊(M) = { y ∈ (0, 1] : sin(M + e y) ≥ y },  S₋(M) = S₊(−M) (reflected).

Then S = S₋ ∪ {0} ∪ S₊. Almost surely sin M ≠ 0. If sin M > 0, then S₊ contains (0, ε) and S₋ stays away
from 0; if sin M < 0 it is the other way round. So exactly one side merges with the hub, and

  pieces = 1 + A₊ + A₋,

where A± counts the components of S± that do not reach y = 0.

**2. One positive hump, at most one piece.** Put θ = M + e y. The positive humps of the sine are the intervals
H_m = [2πm, 2πm + π]. Points of S₊ need sin θ ≥ y > 0, so they lie inside humps, and two humps are separated by
rows where sin θ ≤ 0 < y. On one hump, h(y) = sin(M + e y) − y is concave (a concave function of an affine
argument, minus a linear term). So {h ≥ 0} ∩ H_m is an interval. **Each hump contributes at most one component of S₊.**

**3. Which humps contribute.**
- *A hump whose peak θ = π/2 + 2πm lies in (M, M + e]* contributes exactly one component: at the peak,
  sin θ = 1 ≥ y. The exception is the hump that contains θ = M with sin M > 0; it is the piece glued to the hub.
  Its peak lies in (M, M + e] exactly when M mod 2π ∈ [0, π/2); this needs e ≥ π/2.
- *A hump with no peak in (M, M + e]* is either the hub hump with M mod 2π ∈ (π/2, π), or the last, partial
  hump at the top end y = 1. Its peak lies just beyond, at θ = M + e + δ with δ ∈ (0, π/2).
  It contributes iff some x ∈ [δ, π/2] has cos x ≥ 1 − (x − δ)/e. This is the inequality sin θ ≥ y rewritten
  with x = peak − θ and u = 1 − y = (x − δ)/e. Call this event the **end bonus**.

So, with P₊ the number of peaks π/2 + 2πm in (M, M + e],

  A₊ = P₊ − [M mod 2π ∈ [0, π/2)] + bonus₊,

and the same holds for A₋ with M replaced by −M. The indicator for −M is [M mod 2π ∈ (3π/2, 2π)], and the two
indicators together give [cos M > 0]. Hence, for every M (e ≥ π):

  **pieces = 1 + P₊ + P₋ − [cos M > 0] + bonus₊ + bonus₋.**

**4. Average over M.** A fixed lattice π/2 + 2πℤ falls into a window of length e with uniform offset, so
E[P±] = e/2π exactly. Also P(cos M > 0) = ½. Therefore

  E[pieces] = 1 + e/π − ½ + B(e) = e/π + ½ + B(e),  B(e) = P(bonus₊) + P(bonus₋) ≥ 0.

**5. The bonus is O(1/e).** δ is uniform on an interval of length 2π, independent of everything that matters here.
- *Upper bound.* On |x| ≤ π/2, 1 − cos x = 2 sin²(x/2) ≥ 2x²/π². So a bonus needs 2x²/π² − x/e + δ/e ≤ 0
  for some x. Such an x exists only if the discriminant is ≥ 0, i.e. δ ≤ π²/(8e). Hence P(bonus±) ≤ π/(16e).
- *Lower bound.* 1 − cos x ≤ x²/2. If δ ≤ 1/(2e), then x = 1/e satisfies x²/2 ≤ (x − δ)/e (the discriminant of
  x²/2 − x/e + δ/e is 1/e² − 2δ/e ≥ 0), and x ∈ [δ, π/2] for e ≥ π. Hence P(bonus±) ≥ 1/(4πe).

Adding the two sides gives 1/(2πe) ≤ B(e) ≤ π/(8e). ∎

**Remark (sharp constant).** The lower-bound argument is asymptotically tight, because near the peak
1 − cos x = x²/2 + O(x⁴). So B(e) = 1/(2πe) + O(e⁻²).

## Numerical check (`pieces_proof_check.py`)
The proof's per-hump count agrees with direct pixel counting, which also double-checks the identity in step 3.
Means over 200 000 random phases:

| e | E[pieces] | e/π + ½ | B(e) | e·B(e) |
|---|---|---|---|---|
| 3 | 1.5079 | 1.4549 | +0.0530 | 0.159 |
| 7 | 2.7501 | 2.7282 | +0.0220 | 0.154 |
| 20 | 6.8754 | 6.8662 | +0.0092 | 0.185 |
| 40 | 13.2369 | 13.2324 | +0.0045 | 0.180 |
| 80 | 25.9675 | 25.9648 | +0.0027 | 0.217 |

Standard errors are about 0.001 in E, i.e. about ±0.08 in e·B at e = 80. All values lie inside [1/2π, π/8] = [0.159, 0.393]
and are consistent with e·B → 1/(2π). (The earlier 400-sample estimates in `pieces.py` that fell below e/π + ½ were
sampling noise.)

## Reading it back into the picture
Each turn of the needle per half frame height adds one new piece above the hub and one below: P₊ and P₋, one per
peak of the sine. The hub keeps one piece on whichever side the needle points at the start (the "+1 − ½"). Very
rarely, a sliver catches the top or bottom row just before its peak (the 1/(2πe) correction).
