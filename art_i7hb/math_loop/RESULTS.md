# Unique Hamiltonian cycles in grids with holes (MO 516913) — what I found

M(m,n) = the fewest vertices to delete from the m × n grid graph so that exactly one Hamiltonian
cycle is left. The question conjectures that sup_n M(m,n) is finite exactly when m = 2 or 4 | m,
and asks for a proof that M(m,n) → ∞ when m ≥ 3 and 4 ∤ m.

## 1. The window lemma (computer-assisted) — settles m = 3, 5, 6, 7, 9

A *window* is L consecutive columns with no deleted vertex. A Hamiltonian cycle meets it in a
*path system*: disjoint paths covering all mL vertices, each end leaving through the left or right
side. Outside the window the cycle joins the left exits among themselves by a non-crossing perfect
matching τ_L and the right exits by τ_R (nothing outside can pass from one side to the other).

If the cycle is the only one, then the path system is the only one that, together with (τ_L, τ_R),
closes up into a single cycle: any other could be swapped in.

Call a window *possibly unique* if some exit sets and some (τ_L, τ_R) admit exactly one such path
system. `window.py` enumerates all path systems of an m × L window by their interface (exits and
which exit is joined to which) with a frontier DP, then tries every pair of non-crossing matchings.

| m | L=1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | first L with none |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 6 | 8 | **0** | 0 | 0 | 0 | 0 | 0 | 3 |
| 4 | 19 | 41 | 10 | 2 | 2 | 2 | 2 | 2 | never (to L = 8) |
| 5 | 56 | 143 | 16 | **0** | 0 | 0 | 0 | 0 | 4 |
| 6 | 171 | 593 | 84 | 10 | **0** | 0 | 0 | 0 | 5 |
| 7 | 520 | 2389 | 124 | 46 | **0** | 0 | 0 | 0 | 5 |
| 8 | 1581 | 9773 | 806 | 45 | 6 | 2 | | | never (to L = 6) |
| 9 | 4792 | 40979 | 1408 | 166 | **0** | | | | 5 |

(entries: number of possibly-unique interfaces; logs in `win_*.log`.) A longer window contains a
shorter one, so zero at L₀ means zero for all L ≥ L₀.

**Theorem 1.** For m = 3, 5, 6, 7, 9 put L₀ = 3, 4, 5, 5, 5. If a vertex-deleted m × n grid
(n > L₀) has exactly one Hamiltonian cycle, every L₀ consecutive columns contain a deleted vertex.
Hence M(m,n) ≥ ⌊n/L₀⌋, and M(m,n) → ∞ for these five widths.

(The window may touch an end of the grid: empty exit sets on one side are included.)

For m = 4 and m = 8 the survivors at large L are the square waves — exits on alternate rows,
(0,1,0,2) → (0,1,0,2) or its mirror — which is the bounded construction of the question.

Independent check (`check_lemma.py`, log in `check_lemma.log`): `hc search` lists every
unique-cycle deletion set by brute force for 3×11, 3×12, 3×13, 5×8, 5×9, 5×10, 6×9, 7×8, 7×10, 9×6 (1,874 sets) and every
one of them has a deletion in every L₀ columns. `hc` itself reproduces 6, 1072, 4638576,
1076226888605605706 for the 4×4 … 12×12 grids and the m = 3 row of the question's table.

## 2. Width 3 exactly

**Theorem 2.** M(3,n) = ⌊n/3⌋ + [n ≡ 1 (mod 3)] for every n ≥ 3.

*Lower bound.* Theorem 1 gives ⌊n/3⌋. A cycle has even length, so 3n − d is even; when
n = 3k + 1 this excludes d = k.

*Upper bound.* Delete one end vertex (top or bottom, never the middle) of columns 3, 6, 9, …:
(EE X)^k EE for n = 3k+2, (EE X)^k for n = 3k, and (EE B)^k B for n = 3k+1. `periodic.py` sweeps
the strip keeping min(count, 2) for every frontier state; under the letters EET, EEB only three
capped vectors are ever reached, and each of them finishes with exactly one cycle. So the count
is 1 for every k and every choice of top/bottom.

This matches the question's table for 3 ≤ n ≤ 16 and extends it to all n.

*Remark.* For n = 3k + 2 the lemma forces the k deletions into columns 3, 6, …, 3k, so the
minimisers are at most 3^k; brute force finds exactly the 2^k top/bottom choices (n ≤ 14).

## 3. Conjectures

* **A.** For every m ≥ 3 with 4 ∤ m some L₀(m) exists (no possibly-unique clear window). Known:
  L₀ = 3, 4, 5, 5, 5 for m = 3, 5, 6, 7, 9. This would prove the question's conjecture.
  m = 10 is the next case (even, 2 mod 4): Python needs a C++ port of `window.py`.
* **B.** For 4 | m the only possibly-unique interfaces at large L are the two alternate-row
  square waves (seen for m = 4 to L = 8 and m = 8 to L = 6).
* **C.** Theorem 1 is far from sharp for m ≥ 5 (the table has M(5,n) ≈ n/2 against my n/4).
  Windows that contain one deletion should give the right constant.

## 4. Other numbers

* 8 × 8: exactly 192 four-vertex deletion sets leave a unique cycle (`s88.txt`).
* 12 × 12 with 6 deletions: annealing (`hc anneal`) finds unique-cycle sets in a few hundred
  moves (seven are listed in `hero.py`). With 4 deletions: none found in ~19,000 moves (the
  count stays near e^22), so M(12,12) ∈ {4, 6} stays open here.
* `hc sample` draws exactly uniform Hamiltonian cycles (edge by edge, forced/forbidden edges
  in the DP).

Not posted to MathOverflow.
