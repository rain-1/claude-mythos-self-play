# Notes — MathOverflow 515908, "Pizza slices on a plate"

**Question.** Cut a unit-radius pizza into 2N congruent sectors (angle π/N). The plate has
radius 1 − ε. What fraction P(N) of the slices fits, and what happens as N → ∞ (to leading
order in ε)? Posted so far: Jonathan Love's cross of rectangles, (2√3 − 1)/π − (8/π√3)ε ≈ 0.784,
and a hexagon of three rhombi, 3√3/2π + O(ε) ≈ 0.827.

## 1. A 5/6 construction (new here, as far as I can tell)

Put r = 1 − ε and d = √(1 − r²) ≈ √(2ε).

* **Half-pizza fan F.** Apex P = (d, 0), leaves (slices) in the directions π ± W with
  cos W = d. A leaf from P in direction π + t ends at distance² = d² + 1 − 2d cos t from O,
  which is ≤ r² exactly when cos t ≥ d. So W = arccos d = π/2 − d + O(d³), and F has area W.
  Every point of F has x ≤ d.
* **Two side fans.** Apex on the rim at (d, √(r² − d²)), first leaf straight down (x = d), the
  others rotated toward +x. A leaf from a rim point stays on the plate iff it is within
  arccos(1/(2r)) of the inward radius; the apex's radius is tilted by arcsin(d/r), so the fan
  spans T = arccos(1/(2r)) − arcsin(d/r) = π/3 − d − ε/√3 + …  Its mirror image hangs from
  the bottom. Both lie in x ≥ d, so they miss F; they meet each other only near (d, 0).

Area: F has area W, each side fan spans the angle T and has area T/2, so in the limit of thin slices

  **P∞(ε) ≥ [arccos d + arccos(1/(2r)) − arcsin(d/r)] / π = 5/6 − (2√2/π)·√ε + O(ε).**

| ε | fans (limit) | cross (limit) | hexagon (limit) |
|---|---|---|---|
| 1e-2 | 0.7409 | 0.7696 | ≈0.827 − O(ε) |
| 1e-3 | 0.8047 | 0.7829 | |
| 1e-4 | 0.8243 | 0.7842 | |
| 1e-5 | 0.8305 | 0.7843 | |
| 1e-6 | 0.8324 | 0.7843 | |

So the answer to "leading order in ε" is not a Taylor series: this construction loses √ε.
The hexagon is better for ε ≳ 5·10⁻⁵; the fans win below that, and **lim_{ε→0} P∞ ≥ 5/6**.

Finite N (`pizza.py`, every packing re-checked: polygon overlap area via shapely + sampled
penetration depth ≤ 1e-15 + exact max-radius per sector):

| N (2N slices) | ε | fans | cross |
|---|---|---|---|
| 40 (80) | 0.1 | 28 | **47** |
| 40 (80) | 0.01 | 52 | **58** |
| 40 (80) | 0.001 | **60** | 59 |
| 40 (80) | 1e-5 | **65** | 59 |

## 2. Why the obvious improvements fail (evidence for a conjecture)

* Two near-centre half-fans facing opposite ways must have their apexes on opposite sides of O
  (a fan's apex offset has to point away from its leaves), so their leaves cross: at most one
  "big" fan per plate.
* The right half-disc R holds a 120° fan from (1, 0) **or** two 60° fans from (0, ±1): area π/3
  either way. The 120° fan's arc passes through O, so it cannot coexist with F; mixing a narrow
  (1,0)-fan of half-width w with the side fans costs them ≈ √(2w) of angle for a gain of w.
* Sliding F's apex further right (d → larger) shrinks F by arcsin(d/2) and the side fans by
  2·arcsin(d/2) each: total area 5π/6 − 3·arcsin(d/2). So d → 0 is best.
* Rectangles / rhombi in R hold at most √3/2 < π/3.

**Conjecture (weak evidence, from these families only).** lim_{ε→0} lim_{N→∞} P(N, ε) = 5/6.
What would decide it: an upper bound for "disjoint unit segments in a disc of radius < 1" that
sees the centre (every leaf through the centre region must come from one fan), or a foliation
of the right half-disc beating π/3.

## 3. Small M (M slices of angle 2π/M), plate radius 0.999

`search2.py`: squared penetration of sampled boundary + interior points, L-BFGS from random
starts, each hit re-checked (shapely area + sampled depth + exact radius). "Best found", not proved.

| M | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| slices that fit | 1 | 1 | 3 | **4** | 5 | 6 | 6 | 6 | 7 | 7 | 8 | 10 |

* **M = 6: four of six fit**, so P(3) ≥ 2/3, not the 1/2 the question guessed (verified: shapely overlap area 0
  at 4000 arc points, sampled penetration depth ≤ 2·10⁻⁸ at 40 000 samples per piece, every sector's farthest
  point ≤ 0.99880 < 0.999). The four 60° slices point in four directions; their tips sit within 0.37 of the centre
  and are nudged apart, each one pulled back opposite its own direction. M = 4 (quarters): one, matching the question.
* M = 8: six of eight (3/4).
* Lesson for the limit: several fans whose apexes sit *near* the centre can coexist when each apex is offset
  backwards from its own leaves; "one big fan" is not a law. A seeded optimiser starting from the M = 6 pinwheel
  plus extra thin fans reached ≈ 0.82 with small residual overlaps and nothing valid above 5/6, so the conjecture
  above stands, with that caveat.


Also: there is always at least one slice left over, since the slices' total area π exceeds the
plate's π(1 − ε)². (The Phil.SE question beside this one — "a set is consistent iff there is a
sentence it fails to prove" — is the same shape: a plate is honest because something is left over.)
