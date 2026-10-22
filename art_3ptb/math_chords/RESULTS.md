# Right triangles whose sides are unit-circle polygon edges (MO 153761)

Side of {n/k} inscribed in the unit circle: 2 sin(πr), r = k/n ∈ (0, 1/2] (r = 1/2 is the diameter, "digon" {2}).
Problem: find all rationals r1 ≤ r2, r3 in (0,1/2] with sin²πr1 + sin²πr2 = sin²πr3.

## Answer (proved, modulo Conway–Jones Thm 7)

**One infinite family, degenerate (Thales):** r1 + r2 = 1/2, r3 = 1/2. Legs 2 sin πr, 2 cos πr, hypotenuse 2 (diameter).
In polygon terms {n/k}, {2n/(n−2k)} (reduced), {2}. Examples: {4},{4},{2}; {6},{3},{2}; {10},{5/2},{2}; {8},{8/3},{2}; {12},{12/5},{2}.

**Non-degenerate: exactly 5 triangles, no infinite families.**

| # | legs | hypotenuse | side lengths | identity | Galois orbit |
|---|------|-----------|--------------|----------|------|
| 1 | {10}, {6} | {5} | 0.6180340, 1, 1.1755705 | 1/φ² + 1 = (5−√5)/2 (Euclid XIII.10) | A |
| 2 | {6}, {10/3} | {5/2} | 1, 1.6180340, 1.9021130 | 1 + φ² = (5+√5)/2 | A |
| 3 | {10}, {10/3} | {3} | 0.6180340, 1.6180340, 1.7320508 | 1/φ² + φ² = 3 | B (self-conjugate; σ swaps legs) |
| 4 | {6}, {6} | {4} | 1, 1, 1.4142136 | 1 + 1 = 2 | C (rational) |
| 5 | {6}, {4} | {3} | 1, 1.4142136, 1.7320508 | 1 + 2 = 3 | D (rational) |

(Orbits A, B, C, D = `orbit` ids 0, 1, 2, 3 in sporadic.json. φ = golden ratio; squared lengths 4 sin²πr live in Q(√5); the Galois action ζ→ζ^j, j coprime to N = lcm of denominators,
is the swap √5 ↔ −√5, i.e. {10}↔{10/3}, {5}↔{5/2}, {6},{3},{4} fixed.) Orbit A is Euclid's triangle and its conjugate
(hexagon, decagram, pentagram). Orbit B is a third golden triangle: decagon + decagram legs, triangle hypotenuse.
Orbits C, D are the "rational" ones (half-square, and the 30-60-90 shape built from hexagon/square/triangle).

## Reduction (Task 1)

sin²x = (1−cos2x)/2 turns the equation into  cos X + cos Y − cos Z = 1, X = 2πr1, Y = 2πr2, Z = 2πr3 ∈ (0, π].
Equivalently ζ^a+ζ^−a+ζ^b+ζ^−b−ζ^c−ζ^−c−1−1 = 0: a vanishing sum of 8 roots of unity (signs absorbed), so the
relevant tool is Conway–Jones (1976), Theorem 7: classification of minimal rational linear relations
Σ c_i cos θ_i ∈ Q with ≤ 4 distinct θ_i ∈ (0, π/2) ∩ πQ. The ones with ≤ 3 angles are:
- (φ-family) −cos φ + cos(π/3−φ) + cos(π/3+φ) = 0, 0 < φ < π/6;
- cos π/5 − cos 2π/5 = 1/2;
- cos π/7 − cos 2π/7 + cos 3π/7 = 1/2;
- cos π/5 − cos π/15 + cos 4π/15 = 1/2;  −cos 2π/5 + cos 2π/15 − cos 7π/15 = 1/2
(plus cos π/3 = 1/2; the remaining four list items have 4 angles). Numerically re-checked at 50 digits.

## Proof sketch of completeness

Write each cos X as a rational (X ∈ {π/3, π/2, 2π/3, π}, i.e. r ∈ {1/6, 1/4, 1/3, 1/2}) or ±cos θ, θ ∈ (0,π/2)\{π/3}.
Collect equal θ's: we get Σ_{θ∈S} c_θ cos θ = q, |S| ≤ 3, c_θ ∈ {±1, ±2} (0 removed). View the cos θ in the Q-space R/Q:
the space of relations is spanned by circuits (minimal relations), so every θ ∈ S lies in a CJ circuit contained in S.
1. **S = ∅** (all irrational parts cancel). Cancellation of two cosines forces X+Y = π (cos X = −cos Y) or X = Z / Y = Z.
   X+Y = π leaves −cos Z = 1, Z = π: the **Thales family**. X = Z leaves cos Y = 1, Y = 0: excluded. Otherwise all
   three are rational-valued: finite check → triangles 4, 5 (and Thales members {4}{4}{2}, {6}{3}{2}).
2. **|S| = 3, all of X,Y,Z irrational, so q = 1 and all |c| = 1.** If the relation is itself a 3-term circuit: the four
   sporadic 3-term circuits have constant ±|c|/2 = ±1/2 ≠ 1, and the φ-family has constant 0 ≠ 1. Impossible.
   If not a circuit, S contains a smaller circuit; the only ≤2-term circuit is {π/5, 2π/5}, and no 3-term circuit or
   φ-triple contains both π/5 and 2π/5 (checked: φ-triple pair sums/differences are π/3, 2π/3), so the third
   coefficient would be 0. Impossible.
3. **|S| = 2.** S must be the circuit {π/5, 2π/5} with coefficients ∝ (1,−1) (a coefficient 2 from merging cannot be
   proportional), the third side rational-valued. Finite check → triangles 1, 2, 3.
4. **|S| = 1:** no 1-term circuit (π/3 excluded). Impossible.

Consequently every non-Thales solution has all r with denominators dividing 4, 6 or 10, hence it is found by any search
with denominators ≥ 10. (Heptagon/π/15/π/21 relations cannot occur: wrong constant or too many terms.)
**Status:** complete classification is *proved* conditional only on Conway–Jones Thm 7 (published, standard).
The case analysis above is mine (not taken from the MO thread); the brute force below independently confirms it.

## Brute force (Task 2)

`brute.py D`: all 26 828 rationals in (0,1/2] with denominator ≤ 420 (single core, numpy, ~12 s search, ~15 s total); for each pair r1 ≤ r2
the nearest sin²πr3 via searchsorted, tolerance 1e-12. 6 719 candidates; each then checked at 60 digits (|res| > 1e-40
⇒ certified nonzero) and the survivors verified **exactly** as 2(cos X + cos Y − cos Z − 1) ≡ 0 mod Φ_N(x) over Z
(N = lcm of denominators, own exact cyclotomic polynomial routine).
- 6 712 exact hits = 6 707 Thales (r1 + r2 = r3 = 1/2; equals the independently counted number of such pairs
  with both denominators ≤ 420, so none missed) + the 5 sporadic triangles above.
- 7 near misses with float residual ~1e-13 (e.g. 22/285, 81/340, 68/265: 1.07e-13), all certified nonzero at 60 digits.
- D = 60 gives the same 5 sporadics (plus 139 Thales).

## Files
- `brute.py` – search + exact verification; `classify.py` – families, sporadics, Galois orbits, JSON output.
- `sporadic.json` – {"legs":[[n,k],[n,k]],"hyp":[n,k],"lengths":[...],"orbit":id} (+ r, names, 60-digit residual).
- `families.json` – Thales family with samples; records that no non-degenerate family exists.
- `hits_60.json`, `hits_420.json`, `brute_420.log` – raw verified hits and log.
