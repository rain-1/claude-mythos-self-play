# A perfect shuffle on ℕ (MO 453577) — what I checked and what I guess

**The question.** Cards come in pairs. Is there a way to lay all of ℕ in a row so that for every
n ≥ 1 exactly one pair of twins lies n apart?

## 1. The greedy shuffle is the Wythoff pairing (known mathematics, re-checked)
Put the k-th pair on the first free place a_k and on a_k + k. Then a_k = ⌊kφ⌋, b_k = ⌊kφ²⌋
(the P-positions of Wythoff's game; Beatty's theorem with 1/φ + 1/φ² = 1 gives the partition).
`shuffle.py line` checks greedy = ⌊kφ⌋, ⌊kφ²⌋ for k ≤ 10⁶. So the answer to the question is yes,
and nobody has to choose anything.

## 2. Lemma: where the twins sit on a sunflower (proved; three lines)
Place seed n at angle n/φ turns (the golden angle) and radius √n. Write t = {kφ}.
* a_k = kφ − t, so a_k/φ = k − t/φ: the first twin sits at angle **−t/φ** turns.
* b_k = a_k + k = kφ² − t, so b_k/φ = kφ − t/φ = a_k + t − t/φ = a_k + t/φ²: the second twin sits
  at angle **+t/φ²** turns.

Hence every second twin lies in one wedge of 1/φ² turns = 137.5° (the golden angle itself), every
first twin in the remaining 222.5°, and the pairing is one geometric map: reflect in the seam,
divide the angle by φ, multiply the radius by √φ (since b_k/a_k → φ). Checked numerically for
k < 10⁶ (`sunflower.py … check`), and as counts: every colour band of the picture holds exactly as
many seeds inside the wedge as twins outside it (asserted in `build`).
Honest remark: the bands are not clean circles. One seed-width of radius holds about 2πr seeds,
so a cut "n < n₀" follows the parastichies and comes out as a ragged star. That is in the picture.

## 3. How rare is a good shuffle of a finite deck? (numerics + a conjecture)
G(n) = number of ways to pair up 1..2n with all n differences distinct.
`shuffle.py count 12` gives 1, 1, 5, 29, 145, 957, 8397, 85169, 944221, 11639417, 160699437,
2430145085 (n = 1..12; 13 CPU-minutes for n = 12), with the perfect ones (differences exactly 1..n,
Skolem sequences) 1, 0, 0, 6, 10, 0, 0, 504, 2656, 0, 0, 455936. This is OEIS A060963, which lists
terms to n = 19; my twelve agree.

Fraction of all (2n−1)!! pairings that are good, and its successive ratios (OEIS terms):

| n | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |
|---|---|---|---|---|---|---|---|---|
| ratio f(n)/f(n−1) | .65749 | .65472 | .65474 | .65562 | .65566 | .65535 | .65535 | .65546 |

**Conjecture.** G(n)/(2n−1)!! ~ C·ρⁿ with ρ ≈ 0.6554 (the ratios settle in pairs, a damped
period-2 wobble, the same parity that kills Skolem sequences for n ≡ 2, 3 mod 4).

Two heuristics, neither of which hits it:
* differences independent, collisions Poisson: ρ = e^(−1/3) = 0.7165 (too crude);
* choose n distinct differences with weights (2n − d) and ignore overlaps: the saddle point gives
  ρ = e^(w−2)/w with w = 2 ln(1 + w), w = 2.5129, i.e. **ρ = 0.6646**.
The second is 1.4 % above the numerics. I do not know the true constant; the gap is the
correlation between "differences distinct" and "places disjoint".

## 4. The same greedy on the plane (numerics + a conjecture)
Cells of ℤ² in square-spiral order; steps = vectors up to sign, ordered by length then angle.
Each first free cell takes the shortest unused step that lands (±) on a free cell.
`shuffle.py plane 400`: 641,601 cells opened, 491,618 pairs.
* 96.56 % of pairs use the very shortest unused step; the step used is never more than **5**
  places down the list (4 for the first 10⁵ pairs). At the end the shortest unused step has rank
  491,617 of 491,618: nothing is left behind.
* pairs/cells opened → 0.766 (0.7676 at radius 60, 0.7662 at radius 400); on the line the
  analogous number is 1/φ = 0.618.

**Conjecture.** The plane greedy uses every step exactly once (so it is a perfect shuffle of ℤ²),
and the lag behind the list is bounded (or at worst grows like log). I have no proof and no closed
form: as a picture the pairing is noise with a faint drift, nothing like the sunflower.

## 5. Perfect Memory boards (a small new toy, with a theorem and a conjecture)
An n×n board holds n²/2 pairs. Call it *perfect* if the n²/2 steps between twins are exactly the
n²/2 shortest vectors of ℤ² up to sign. That needs a circle to cut the list of vectors at n²/2
("a cut"): n = 2, 6, 10, 12, 14, 18, 20, 24, 30, 42, 48, 50, 54, 58, … — not 4, 8, 16, 22, ….

**Proposition (parity, after Skolem).** If a perfect n×n board exists, the number of its steps
with odd x-component is even (and likewise for y).
*Proof.* Sum the x-coordinates of all cells: n·n(n−1)/2, which is even for even n. Each pair
contributes x_a + x_b ≡ dx (mod 2). So Σ dx ≡ 0. ∎

| n | 2 | 6 | 10 | 12 | 14 | 18 | 20 | 24 | 30 | 42 | 48 | 50 | 54 | 58 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| steps with odd dx | 1 | 10 | 25 | 35 | 50 | 81 | 100 | 145 | 223 | even | even | even | odd | even |
| perfect board | no | **yes** | no | no | **yes** | no | **yes** | no | no | **yes** | **yes** | **yes** | no | **yes** |

Every "yes" is an explicit board in `board_n.json`, found by `board_find.py` (most-constrained
branching; 0.3 s for n = 14, two minutes for n = 58) and verified by an independent check in the
same script (all cells covered once, the step set equal to the list).

**Conjecture.** A perfect n×n board exists exactly when the cut exists and the parity condition
holds. (True for all n ≤ 58.) So 6×6 is the only perfect board smaller than 14×14.

How many 6×6 boards: a Knuth random-probe estimate of the search tree gives about 1.3·10⁹
(2·10¹¹ nodes). The exact count (`board_nb.py 6`) had not finished when this was written.
