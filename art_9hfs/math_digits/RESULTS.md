# Digits on a board — notes on MO 516966 (2026-11-20)

**Question (A. Della Corte / R. Piergallini, MO 516966).** Remove the four central squares of a
chessboard. Can a digit be put in each of the 60 remaining squares so that the 100 pairs of
adjacent squares (read left→right and top→down) show each of 00…99 exactly once?
**Yes** — a solution was posted by MO user OscarTheGrumpyGrouch (answer 516967; `../mo_answer.json`,
re-verified here: 100 distinct pairs). The hero picture uses that arrangement. I did **not**
find a second solution of my own (see "What failed").

General problem: a *board* is a finite set of cells of the square grid (or of a torus) with exactly
b² adjacencies; a *solution in base b* labels the cells with 0…b−1 so that the b² ordered pairs
are all different. Everything below was checked by `sat.py` / `cp.py` (exhaustive when it says
"impossible").

## 1. Degree identity (proved, one line)
In a solution, digit d is the first member of exactly b pairs and the second of exactly b. So

> for every digit d:  Σ over cells holding d of (number of neighbours of the cell) = 2b,

and separately the right+down neighbours sum to b and the left+up neighbours sum to b.
Adding these as redundant constraints took CP-SAT from 17 s to 1 s on the 5×6 board.

## 2. Ladders never work (THEOREM)
A 2×n board has 3n−2 adjacencies, so b² = 3n−2. All cells have 3 neighbours except the four
corners, which have 2. By §1, 3·n_d − c_d = 2b, where c_d = number of corners holding d, hence
c_d ≡ b (mod 3) for **every** digit. If b ≡ 2 (mod 3) each of the b digits needs at least two
of the four corners: b ≤ 2. If b ≡ 1 (mod 3) each needs at least one: b ≤ 4. The two survivors,
2×2 (b=2) and 2×6 (b=4), are impossible by exhaustive search. **No ladder has a solution.**
Best possible number of distinct pairs: b²−1 for b = 4, 5, 7 (examples found by annealing;
2×9 in base 5 is the ladder in the picture). For b = 8, 10, 11 short runs reached b²−2, b²−2, b²−3
— unknown whether b²−1 is always attainable.

## 3. Which rectangles and which holed squares can even try
* m×n rectangle: 2mn−m−n = b² ⇔ **(2m−1)(2n−1) = 2b²+1**. Squares need the Pell equation
  x²−2b²=1: 2×2 (b=2, impossible), **9×9 in base 12**, 50×50 in base 70. Near-squares m×(m+1)
  need 2m²−b²=1: **5×6 in base 7 (solved)**, 29×30 in base 41. There is no 3×n board at all
  (5 ∤ 2b²+1), and no rectangle for b = 3, 6, 8, 9, 10 other than the path / the dead ladder.
* N×N with a centred h×h hole: 2N(N−1) − 2h(h+1) = b². Piergallini's board is the case h=2 of
  an infinite family **N = 3h+2, b = 4h+2** (identity: 2(3h+2)(3h+1) − 2h(h+1) = (4h+2)²):
  2×2 base 2 (impossible), **5×5 minus the centre in base 6 (solved)**, the chessboard in base
  10 (solved on MO), 11×11 minus 3×3 in base 14, 14×14 minus 4×4 in base 18, …
  **CONJECTURE A.** Every member with h ≥ 1 has a solution.
* m×n torus: 2mn = b². Solved: 2×4 (base 4), 3×6 (base 6).
* Small pretty boards solved for the stamp sheet: 1×5 (b=2), a 3×3 ring on a stem (b=3),
  a 4×4 cross (b=4), a 4×4 house with a chimney (b=5).

## 4. A solution of the chessboard has almost no symmetry (proved) — and probably none
Suppose a symmetry s of the holed chessboard maps a solution to itself up to renaming the digits
by a permutation σ. All digits occur, so σ has the order of s.
* **Half turn.** The pair (x,y) on a horizontal edge e reappears on s(e) as (σy,σx). Pairs and
  edges are in bijection, so (x,y) ↦ (σy,σx) may have no fixed pair unless s(e)=e; no edge is
  fixed (the centre is missing). But σ²=1, so (x,σx) is a fixed pair. Impossible.
* **Quarter turn.** Its square is a half turn. Impossible.
* **Anti-diagonal reflection.** Horizontal edges go to vertical ones, again with (x,y) ↦ (σy,σx).
  Impossible for the same reason.
* **Main-diagonal reflection.** Pairs transform as (x,y) ↦ (σx,σy), which must be fixed-point
  free, so σ has no fixed digit; but a cell on the diagonal holds a fixed digit. Impossible.
* **Mirror in the vertical (or horizontal) mid-line.** Not excluded by this argument. It forces:
  σ is a product of five disjoint transpositions; the six doors across the fold read (x,σx);
  and — since the vertical pairs are closed under (x,y)↦(σx,σy) and the horizontal ones under
  (x,y)↦(σy,σx) — **the set of horizontal pairs is closed under reversal** ("37" horizontal ⇒
  "73" horizontal), and likewise the vertical set.
  Exhaustive search says a mirror solution is impossible on every smaller symmetric board I
  tried: 5×6 base 7, the 4×4 cross base 4, a 6-wide base-6 board, and the 2×4, 3×6 and 4×8 tori.
  For the chessboard itself the search (30 free cells) did not finish.
  **CONJECTURE B.** No solution on any board is mirror-symmetric up to renaming digits; hence
  solutions of the holed chessboard have trivial symmetry group. (I could not find the counting
  argument that the small cases suggest; the reversal-closure lemma is the natural start.)

## What failed (so the next run does not repeat it)
* Plain simulated annealing on the 60-cell board (`dig.cpp`, single-cell moves, cost = missing
  pairs) reaches 1–2 missing pairs in seconds and then never closes, at any temperature tried.
* SAT (`sat.py`: direct encoding, sequential-counter or pairwise exactly-one; CaDiCaL, Glucose,
  MapleChrono) and CP-SAT (`cp.py`, AllDifferent on b·x_u+x_v, with degree and inverse
  constraints) solve b ≤ 7 in a second and do not solve b = 10 in 7–10 minutes on 2–4 cores.
* Anneal-then-repair (`lns.py`: free a disc of cells, SAT the rest) never repaired a near-solution.
* NOTE on this environment: background jobs only advance while a tool call is running, so "leave
  it running while I draw" does not work; long searches need explicit waits.

## Files
`sat.py` (board(), solve(), check(); modes rect / holed / holeH / torus / mask:…), `cp.py`
(CP-SAT; flags m, deg, inv, t=, w=), `dig.cpp` (annealer), `lns.py`, `sol_*.json` (verified grids).
