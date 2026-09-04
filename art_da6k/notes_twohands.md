# Two hands on the circle — notes for MO 488999

**Question (Banakh–Karasová line, MO 488999).** Is the circle S¹ a *topological fractal with two
maps*: continuous f₁, f₂ : S¹ → S¹ with f₁(S¹) ∪ f₂(S¹) = S¹ and, for every ε > 0, some n with
diam(f_{i₁}∘…∘f_{i_n}(S¹)) < ε for ALL words of length n? Three maps suffice (three metric
contractions). Sub-question: find a pair for which some length-n compositions all have image
shorter than a quarter turn. On 2026-09-03 the poster added a ChatGPT-assisted "Theorem": for
every ε there are f, g = f + ½ (a fold with parameter L ≥ 3) and N with all length-N images < ε.

## 1. The fold, computed exactly (`twohands.py`)
T = ℝ/ℤ, δ = 1/(2L), r = (L−2)/(L−1); f is piecewise linear through
(0, ½−1/L), (δ, ½), (½, 1/L), (½+δ, 0), (1, ½−1/L); image [0, ½]; g = f + ½, image [½, 1]. All
2^k images computed as exact rational arcs (Fractions) for L ≤ 6, floats above.

Max diameter over all words of length k:

| L | k=1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | … | limit |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | .5000 | .3333 | .3333 | .3333 | .3333 | .3333 | .3333 | .3333 | … | **1/3** |
| 4 | .5000 | .2500 | .2500 | .2500 | .2500 | .2500 | .2500 | .2500 | … | **1/4** |
| 5 | .5000 | .3000 | .2250 | .2000 | .2000 | .2000 | .2000 | .2000 | … | **1/5** |
| 6 | .5000 | .3333 | .2667 | .2133 | .1707 | .1667 | .1667 | .1667 | … | **1/6** |
| 8 | .5000 | .3750 | .3214 | .2755 | .2362 | .2024 | .1735 | .1487 | … | **1/8** |
| 12 | .5000 | .4167 | .3788 | .3444 | .3130 | .2846 | .2587 | .2352 | … | 1/12 |

**The max diameter does not go to 0: it plateaus at exactly 1/L.** The culprit is the arc
J = [½, ½ + 1/L]: g maps the slope −2 piece [½, ½+δ] onto [0, 1/L] and then adds ½, so
g(J) ⊇ J — in fact g(J) = J (L = 4: g([½, ¾]) = [½, ¾] exactly). Hence gᵏ(T) ⊇ J for every k,
and so does f∘gᵏ⁻¹(T) ⊇ f(J) = [0, 1/L]. In every ring of the picture these are the two coral arcs.

So the added "Theorem" is true exactly as stated — *for every ε there is a pair* (take L > 1/ε) —
but it is the ε-dependent statement, not the fixed-pair one the question asks. It does settle
the sub-question: L = 5 gives every length-3 word an image shorter than ¼ (L = 4 gives ¼ exactly
and never less). The original question is still open.

## 2. A necessary condition
If some word w has an arc J with w(J) ⊇ J, then wᵐ(T) ⊇ J for all m and the pair fails. For
piecewise-smooth maps this happens at any fixed point of any word where |w′| > 1. Since every word
T → arc has degree 0 it has a fixed point (Lefschetz), so: **every word must have all its fixed
points non-expanding**, i.e. along every periodic orbit of the IFS the product of slopes is ≤ 1.
Yet a map of T onto an arc A of length |A| must sweep A twice from the complement (length
1 − |A|), so its average |slope| there is ≥ 2|A|/(1−|A|) > 1 as soon as |A| > 1/3 — and one of
the two arcs has length ≥ ½. The expanding sets of f and g each map onto (almost) all of the
other's domain; the question is whether the two expanding regions can avoid ever forming a cycle.

## 3. Search (`pairsearch.py`, `pairsearch2.py`)
Nelder–Mead over piecewise-linear degree-0 pairs (4–5 interior breakpoints each), objective
D₉ = max diameter over the 512 words of length 9.

- **Covering enforced by construction** (`pairsearch2.py`, A = [0,a], B = [b, 1+c] with b ≤ a, c ≥ 0
  so A ∪ B = T exactly): 11 trials, every local optimum is a rational plateau — D_k → 1/2, 1/3,
  0.3659, 0.2717, 0.2511, … — i.e. an invariant arc appears every time.
- **Covering only penalised** (`pairsearch.py`): the optimiser immediately opens a small gap
  (0.5 %–3 % of the circle uncovered) and then D_k → 0 geometrically. That is no surprise: with
  |A| + |B| < 1 two *metric* contractions (x ↦ λ·dist(x, x₀), λ = |A|+|B|) already do it. The
  exact-cover case is precisely where metric contraction is impossible (λ ≥ 1), and the search
  suggests topological contraction fails there too.

**Conjecture.** The circle is not a topological fractal with two maps: for any continuous f, g
with f(T) ∪ g(T) = T there is c > 0 and, for every n, a word of length n whose image has diameter
≥ c. (Evidence: the plateaus above; the necessary condition in §2. A proof would have to show
that the two expanding regions, each of which must cover the other's domain, always support a
cycle — a horseshoe-type argument on the pair.)

## 4. The picture
*Two Hands Cover the Clock* (2560², L = 5, 11 rings): ring k holds the 2^k images of the words of
length k, one hairline arc each; f·w and g·w share a sub-band (their arcs lie in opposite halves),
warm pigments for f-words, cool for g-words, the second and third letters choosing the pigment.
The coral arcs are gᵏ(T) and f gᵏ⁻¹(T), the arcs that never shrink. Centre: the graphs of f and g.
`twohands_2560_cert.json` records the max diameters per ring (0.5, 0.3, 0.225, 0.2, 0.2, …).
