# MO 394427 — equal sticks (a small reproduction, nothing new)

Question: is the fewest number of *equal-length* sticks needed to build a knot always the same as
the fewest sticks of any lengths? Open; per the answer on MO every knot with stick number ≤ 9 is now
known to have an equilateral realisation with that many sticks (8₁₉ with 8 equal sticks is Millett's).

What `alex.py` does: random equilateral n-gons in space by crankshaft folds (rotate an arc about the
chord joining two vertices — edge lengths never change), knot type from the Alexander polynomial
(Wirtinger/Fox matrix of a projection, evaluated at t = −1, i, e^{2πi/3}; tested on torus knots
T(2,3), T(2,5), T(3,4), T(2,7), T(3,5)). `prep.py` then fattens one representative per type by
annealing the smallest distance between non-adjacent sticks, re-derives the **full** Alexander
polynomial in five random projections by interpolation at 64 roots of unity, and checks that all
edge lengths equal 1 to 1e-9.

| knot | sticks | found in unconfined random polygons | found with a compaction weight exp(−λ·n·Rg²) |
|---|---|---|---|
| 3₁ | 6 | 264 in 2·10⁶ hexagons (1.3·10⁻⁴, the known value) | |
| 4₁ | 7 | 248 in 10⁷ heptagons | |
| 5₂ | 8 | 20 in 10⁷ octagons | 406 in 2·10⁷ (λ=1) · 16 297 (λ=5) |
| 5₁ | 8 | 8 in 10⁷ | 136 · 5 518 |
| 6₂ | 8 | 5 in 10⁷ | 86 · 3 386 |
| 6₃ | 8 | 5 in 10⁷ | 74 · 3 880 |
| 6₁ | 8 | 2 in 10⁷ | 20 · 1 031 |
| Δ = (t²−t+1)² (granny, square or 8₂₀ — Alexander cannot tell) | 8 | 1 in 10⁷ | 16 · 871 |
| 8₁₉ | 8 | 0 in 10⁷ | 0 (λ=1), 0 (λ=2.5), **2 in 2·10⁷ (λ=5)** |

Identification by Alexander polynomial alone is legitimate here only because the list of knots with
stick number ≤ 8 is known (Calvo's list, as I recall it — I did not re-check the paper) and their polynomials are distinct except for the three in the
second-last row.

A false start worth recording: hard confinement in a ball (reject any fold that leaves it) froze the
chain at the starting regular octagon — 9·10⁷ samples, zero knots, not even a trefoil. A zero count
from a sampler is a statement about the sampler first.
