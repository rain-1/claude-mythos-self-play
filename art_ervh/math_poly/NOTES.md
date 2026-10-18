# Unit-side simple polygons in the unit square (MO 481323)

Method: vertices are parametrised by a start point and n edge angles, so every side is exactly 1
by construction. Closure, box and simplicity are enforced by a least-squares solve (scipy TRF)
with residuals: closure gap; box excess; (margin - signed distance between non-adjacent edges)+,
where the sign is negative if the edges cross; and (fold - |v_{k+1}-v_{k-1}|)+. Starts: random
walks, random turn sequences, random vertex loops, and zigzags (including "raised" ones). Then
an MCMC-like exploration: angle noise, swapping or reversing edge blocks (closure is kept under
edge permutation), rotating or reflecting blocks, each followed by a re-solve. Each kept polygon
passes `exact_check` in float64: |side-1| < 1e-9, box excess < 1e-9, no crossings, and a
recorded positive clearance. One core.

## Gallery (gallery.json, preview: gallery_preview.png)
There are 12 polygons for each n = 3,5,...,21. They were picked by farthest-point sampling,
using a shape distance that ignores the 8 square symmetries and cyclic relabelling. All 120
re-verified: max side error 4e-10, max box excess 9.5e-10.

| n | valid found | turn word classes (cyclic/reversal canonical) | reflex vertices | gallery min clearance |
|---|---|---|---|---|
| 3 | 1095 | LLL | 0 | (no non-adjacent edges) |
| 5 | 846 | LLLLR | 1 | 0.0060 |
| 7 | 535 | LLLLRLR | 2 | 0.0060 |
| 9 | 637 | LLLLRLRLR | 3 | 0.0060 |
| 11 | 333 | LLLLRLRLRLR | 4 | 0.0060 |
| 13 | 428 | LLLL(RL)^4R | 5 | 0.00174 |
| 15 | 265 | LLLL(RL)^5R | 6 | 0.00128 |
| 17 | 275 | LLLL(RL)^6R | 7 | 0.00098 |
| 19 | 270 | LLLL(RL)^7R | 8 | 0.00077 |
| 21 | 171 | LLLL(RL)^8R | 9 | 0.00063 |

(L = convex, R = reflex, with the polygon oriented CCW.) The clearance target was 0.006. For
n ≥ 13 I lowered it to 0.25/(n-1)^2, because a margin of 0.006 is impossible there (see obs. 3).

## Observations
1. **Only one combinatorial type was found.** Every one of the 4,855 valid odd polygons has the
   turn word LLLL(RL)^k R, with n = 2k+5 (plus LLL for n = 3). This is a "comb or zigzag": one
   run of 4 convex vertices, then alternating vertices. So there are always (n-3)/2 reflex
   vertices. The search moves (edge swaps, block reversals and reflections) never produced
   another word. Shape variety comes only from continuous freedom: unequal tooth widths, tilt,
   which square side holds the base, and spike thickness.
2. Interior angles are always ≤ 90° or ≥ 270°, as expected: u_k·u_{k+1} ≤ 0 because
   |v_{k+1}-v_{k-1}| ≤ √2. In every pool the maximum convex angle is exactly 90°. The two base
   corners sit at corners of the square, so the base edge is a full side of the square in
   essentially all examples.
3. **Clearance decays like 1/n².** The teeth must be nearly vertical, with horizontal parts
   ≈ 1/(n-1). The vertical rise of a tooth edge is then ≈ 1 - 1/(2(n-1)²), so the reflex
   vertices sit at most ≈ 1/(2(n-1)²) above the base edge. The largest clearance found is about
   0.25–0.4/(n-1)².
4. **Alternating-sign reformulation (proof idea).** Let w_k = (-1)^k u_k. Then
   w_k·w_{k+1} ≥ 0, so each step of the w-sequence turns by at most 90°, and it closes with
   w_n = (-1)^n w_0. Its total rotation is therefore an integer number of turns when n is even
   and a half-integer when n is odd. Every valid odd polygon found has w-rotation exactly ±1/2.
   The best even near-misses have w-rotation 0 or ±1. Conjecture B below would imply that a
   rotation of 0 or ±1 is impossible, which is exactly the parity claim. Two heuristics: with
   rotation ±1, the unit edges point in all directions like spikes around a small core, which
   needs diameter about 2. With rotation 0, all teeth point roughly the same way, which looks
   like it forces the two chains of alternate vertices, v_even and v_even + w, to cross.

## Even search (near_misses.json)
Sides are exactly 1. The violation is the max of: closure gap, box excess,
(δ - clearance)+ and (δ - fold)+, with δ = 0.005. For n = 4, square-like configurations are
excluded. Total CPU was about 13 min, short of the ~40 min asked for: the budget went to the
gallery first.

| n | starts + basin hops | best violation | best near-miss turn word | w-rotation |
|---|---|---|---|---|
| 4 | 2058 | 4.4e-3 | LLLR (folded rhombus) | 0 |
| 6 | 1942 | 1.4e-3 | LLLLLR | ±1 |
| 8 | 2190 | 1.6e-3 | LLLRLLLR | ±1 |
| 10 | 3263 | 2.2e-3 | LLLRLLLRLR | ±1 |
| 12 | 3580 | 2.6e-3 | LLLRLRLLLRLR | ±1 |

No even polygon was found. The best violations are a fixed fraction (0.3–0.9) of δ, and they
are bounded away from 0 at this δ. The near-misses use the slack to pinch: they have tiny
clearance or a near-180° fold, sit just outside the box, and leave a closure gap of about
1e-3. This suggests they are degenerate configurations that tend to 0 as δ → 0, not true
solutions. The evidence is consistent with the conjecture, though it is not strong at fixed δ.
n = 6 is a sanity check: it is known to be impossible, and it behaves the same way as 8, 10
and 12. For n = 4 the result is a theorem: a unit rhombus with angle α < 90° has a diagonal
2cos(α/2) > √2, so only the square fits.

## Conjectures (numerical evidence only)
- **Conjecture A (rigidity of type).** Every simple unit-side polygon in [0,1]² other than the
  square has turn word LLLL(RL)^k R, or LLL. Evidence: 4,855 verified examples for
  n = 3,…,21, all of this type, and no other type found despite moves designed to change it.
  A implies the MO conjecture, since the word length 2k+5 is odd.
- **Conjecture B.** The w-sequence above always rotates by exactly ±1/2 turn. Equivalently, the
  "anti-alternating" edge sequence sweeps a half-turn exactly once.
- **Conjecture C.** The largest possible clearance is Θ(1/n²).

## Files
poly.py (core: parametrisation, numba residual, exact check, turn words), search.py
(multi-start), explore.py (seeded exploration), gallery.py (selection, gallery.json,
gallery_stats.json, gallery_preview.png), even.py (even search), analyze.py (statistics:
analysis.json, near_misses.json), runs/ (raw pools g*.json, even*.json, logs).
