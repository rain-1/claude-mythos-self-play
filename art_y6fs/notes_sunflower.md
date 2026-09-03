# Notes — The Sunflower of Fifths

**Object.** A Vogel spiral whose divergence angle is a perfect fifth instead of the golden
angle: seed *k* sits at angle 2π·{kα} and radius √k, with α = log₂3 = 1.5849625…
(a fifth is 3:2; reducing to the octave means taking the fractional part of k·log₂3).
Seed k is the pitch reached after k fifths.

**Why the visible spirals are tunings.** Seeds k and k+m are at squared distance

    d(m,k)² = (2π√k·‖mα‖)² + m²/(4k)      (‖x‖ = distance to the nearest integer)

so the family m that is *nearest* at seed k is the m minimising this — small ‖mα‖ (m fifths
close a whole number of octaves: an equal temperament with a good fifth) against small m.
The hand-over indices where the nearest family changes are the roots of d(m,k)=d(m',k).

## Theorem (nearest family = convergent)
On a Vogel spiral with divergence α, the nearest-neighbour family at any seed is a convergent
denominator q_n of α. *Proof.* Let m be any step and q_n the largest convergent denominator
≤ m. By Lagrange's best-approximation theorem, ‖q_nα‖ ≤ ‖mα‖ for all 1 ≤ m < q_{n+1}, with
equality only at m = q_n. Then q_n ≤ m and ‖q_nα‖ ≤ ‖mα‖, so both terms of d² are no larger
for q_n: a non-convergent m never strictly minimises. ∎
Intermediate fractions (semiconvergents) *can* be the second-nearest (the opposed family), and
are: 7, 17, 29, 41, 359 are seen as opposed families in the census.

## Which convergents are realised (hypothesis + sketch)
For log₂3 the nearest families are 5, 12, 53, 306, 665 — the convergent **41 is skipped**.
Across seven angles (log₂3, golden, √2, e, π, √3, ln2) every skipped convergent q_n has
next partial quotient a_{n+1} = 1 (41 for log₂3; 106 for π; 10 for ln 2; 11, 41, 153, 571,
2131 for √3), and every convergent with a_{n+1} ≥ 2 was realised.

Sketch: q_n is realised iff it beats q_{n−1} before q_{n+1} does, i.e.
(q_n²−q_{n−1}²)/(e_{n−1}²−e_n²) < (q_{n+1}²−q_{n−1}²)/(e_{n−1}²−e_{n+1}²) with e_j = ‖q_jα‖.
With the crude e_j ≈ 1/q_{j+1}, x = q_{n−1}/q_n and A = a_{n+2}: if a_{n+1} ≥ 2 the right side
is ≥ 3 while the left is ≤ 1 (always realised); if a_{n+1} = 1 the condition becomes
(1−x²)(1−(A(1+x)+1)⁻²) < (1+2x)(1−(1+x)⁻²), roughly x ≳ 0.4 — golden (x = 0.618) passes at
every step, log₂3's 41 (x = 12/41 = 0.29, A = 5) fails, √3's convergents alternate.
**Conjecture:** a convergent followed by partial quotient ≥ 2 is always a nearest family; one
followed by 1 is a nearest family iff the displayed inequality holds with the exact e_j.
(What it would take: replace the crude e_j by e_j = 1/(q_{j+1}+q_jθ_{j+2}) and check the sign
of the difference is monotone in θ — a page of algebra, not done here.)

## Census (analytic vs measured)
Continued fraction of log₂3 − 1: [0; 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, …].
Convergent denominators 1, 2, 5, 12, 41, 53, 306, 665, 15601, 31867 …

| family m | cents the fifth misses | record | name |
|---|---|---|---|
| 5 | 90.2 | yes | 5-tone |
| 7 | 114 | | 7-tone |
| 12 | 23.46 | yes | 12-TET (the Pythagorean comma) |
| 17 | 66.8 | | 17-TET |
| 29 | 27.4 | | 29-TET |
| 41 | 19.8 | yes | 41-TET |
| 53 | 3.615 | yes | 53-TET (Mercator's comma) |
| 306 | 1.77 | yes | 306-TET |
| 665 | 0.0755 | yes | 665-TET (the "satanic comma") |
| 15601 | 0.0315 | yes | |

Nearest-family hand-overs (analytic minimiser, then KD-tree on 300 000 seeds; the measured
row is the first seed after which the new family holds for 90 % of the next 300 seeds):

| family | analytic k | measured k | radius √k | opposed families in that era |
|---|---|---|---|---|
| 5 | 5 | — | 2.2 | 2, 12 |
| 12 | 12 | 11 | 3.5 | 5, 17, 41, 53 |
| 53 | 213 | 204 | 14.6 | 41, 306, 12 |
| 306 | 9130 | 9094 | 95.6 | 359, 665, 53 |
| 665 | 31888 | 31734 | 178.6 | 306 |

Analytic and measured agree within 2 % in k at every hand-over. The full table with all
intermediates is in `census_table.md` (`census_extra.py`); the per-band census of the hero is
in `sunflower_4096_census.json`.

**The picture.** 48 000 seeds (a 60 000-seed first render had sub-pixel threads at 4096²).
Nearest-family threads in ink, opposed-family threads in the ring's pigment, florets as pale
underpainting dense at the heart and thinning to the rim, pigment blending across each
hand-over (coral 12 → apricot 53 → aqua 306 → cornflower 665), a coral bloom at seed 0.
Bead size breathes with the seed's distance from its nearest 12-TET note, so the comma
drift is a slow 12-armed pinwheel of bead sizes near the centre. Labels at the hand-over
radii: 12, 53, 306, 665. Where two rings meet the weave changes direction — that seam is
the hand-over of the nearest family, i.e. the moment one temperament stops being the best
way to count the seeds.

**Seed.** MO 509849 (adjacent ratios of p^n q^m and a subtractive-Euclid recursion; already
proved by an answerer) pointed at the log-lattice of 2^n 3^m; the fifth's continued fraction
is the same object seen one-dimensionally. Phil.SE 141195 ("models of reality outside the
big four"): this is the *automatic* picture — one rule turning, no maker, and the tunings
are its by-product.
