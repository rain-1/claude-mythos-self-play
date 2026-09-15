# Notes — What Can Be Said (run 2026-09-15)

Three small pieces of mathematics behind the three pictures, with certificates.

## 1. The Longest Honest Answer — Erdős discrepancy, C = 2, N = 1160

**Problem (Erdős, 1932).** Is there a ±1 sequence x₁, x₂, … and a bound C such that every homogeneous
progression ledger S_d(k) = x_d + x_{2d} + … + x_{kd} stays within [−C, C]?  **Tao (2015): no** — every ±1
sequence has unbounded discrepancy.  For C = 2 the exact threshold is known: **Konev–Lisitsa (2014)** found a
sequence of length 1160 and proved by SAT that 1161 is impossible.

**What was computed here.** `erdos_sat.py` encodes the ledgers as one-hot automaton states p[d,k,s] with the
parity reduction S_d(k) ≡ k (mod 2) (≈ 29k variables, 61k clauses at N = 1160) and hands the instance to
CaDiCaL 1.9.5 through python-sat.  Times on one core:

| N | 300 | 600 | 800 | 1000 | 1100 | 1160 (clauses in build order) | 1160 (clauses shuffled, seed 3) |
|---|---|---|---|---|---|---|---|
| seconds | 0.0 | 2.1 | 15.1 | 9.6 | 59.7 | > 13 min, killed | **77.9** |

Every solution is re-verified by summing all ⌊N/d⌋ ledgers for every d (`max_abs_ledger = 2` in each cert JSON).
The hero draws `cache/erdos_1160_s3.json`.  Shuffling the clause order matters enormously (a
factor > 10 in either direction between seeds): this is a hard, luck-sensitive instance, as Konev and Lisitsa
reported.

**Structure of the sequences (`analyze_erdos.py`, `erdos_analysis.json`).**  Two statistics per solution:
the *multiplicativity defect* (fraction of pairs a, b ≥ 2 with ab ≤ N and x_{ab} ≠ x_a x_b) and the agreement
with the Dirichlet character mod 3 on the n not divisible by 3 (up to a global sign).

| N | 300 | 600 | 800 | 1000 | 1100 | 1160 (s3) |
|---|---|---|---|---|---|---|
| mult. defect | 0.451 | 0.686 | 0.454 | 0.596 | 0.440 | **0.126** |
| χ₃ agreement | 0.575 | 0.522 | 0.562 | 0.855 | 0.737 | **0.806** |
| fraction of ledger cells at ±2 ("the brink") | 0.167 | 0.163 | 0.150 | 0.113 | 0.149 | 0.107 |

The short sequences are essentially arbitrary (a random sequence has defect 0.5); the sequence of maximal
length is *forced* toward multiplicativity: only 12.6 % of its multiplicative relations fail, and it follows
the character mod 3 on four fifths of the non-multiples of 3.  (A completely multiplicative discrepancy-2
sequence has maximal length 246; the length-1160 record is bought exactly by the freedom to break
multiplicativity in one place in eight.)

**Three independent solutions at N = 1160** (clause-shuffle seeds 3, 10, 11; 78 s, 403 s, 412 s):

| seed | mult. defect | χ₃ agreement | x_{3m} = x_m | cells at ±2 |
|---|---|---|---|---|
| 3 | 0.126 | 0.806 | 0.337 | 0.107 |
| 10 | 0.139 | 0.813 | 0.313 | 0.106 |
| 11 | 0.130 | 0.817 | 0.337 | 0.106 |

The three sequences agree with one another on 93.6–94.7 % of positions: the solver, started three different ways,
lands on essentially one object.

**HYPOTHESIS (holds on 3 of 3 solutions found).**  *Every* ±1 sequence
of length 1160 with discrepancy 2 has multiplicativity defect below 0.2 and agrees with χ₃ (up to sign) on more
than 70 % of its non-multiples of 3 — i.e. near the wall, honesty forces near-multiplicativity.  What it would
take to prove: enumerate the solutions at 1160 (blocking clauses, or a #SAT run — the 94 % pairwise agreement
says the solution set is a small cluster) and check the two statistics on each; then the statement is a finite fact,
and the interesting question becomes *why* the wall is multiplicative (Tao's proof goes through the
Elliott conjecture for multiplicative functions — the hypothesis says the extremal sequences already know that).

## 2. The Meaning of a Number Is a Tree — Matula–Goebel

Every rooted tree is a number: 1 is the single node; if n = p_{k₁} p_{k₂} ⋯ (p_k the k-th prime) then the
tree of n is a root whose children are the trees of k₁, k₂, ….  This is a bijection ℕ ↔ rooted trees.
Facts drawn on the sheet: the *bamboo* (a single stalk of h nodes) is the primeth recurrence
1, 2, 3, 5, 11, 31, 127, 709, … (a(h) = p_{a(h−1)}); the *stars* (root with k leaves) are 2^k; the tree of a
prime p_k is the tree of k on a stem.  `garden_2560_cert.json` lists size, height and root degree of each of
the first 120 trees.

## 3. The Order You Tell It In — Steinitz and Banaszczyk

**Steinitz lemma (plane, sharp form — Banaszczyk 1987).**  If v₁, …, v_n ∈ ℝ² have ‖v_i‖ ≤ 1 and Σ v_i = 0,
some ordering keeps every partial sum inside the disc of radius √5/2 ≈ 1.118, and √5/2 cannot be improved.

What the picture certifies (`orders_2560_cert.json`): n = 720 vectors with equidistributed angles, mean removed,
max norm 1.  Angle order: max |partial sum| = 211.5 (a circle of radius ≈ n/2π = 114.6 reaching 2r).
m interleaved angle blocks, each block started 2πj/m further round: m circles of radius ≈ n/(2πm) through the
origin (max |S| = 106.2, 70.8, 53.1, … for m = 2, 3, 4, …).  Random order: 24.7 (a Brownian loop, ~√n).
Greedy (choose the remaining vector that brings the partial sum nearest the origin) then 40,000 random
swaps accepted when not worse: **0.995 < √5/2**.  So the picture's balanced order beats the sharp bound for
this particular polygon — as it must for most polygons; the extremal ones are rare.

*Small lemma behind the roses.*  If the angles are equidistributed and the vectors are ordered by angle, the
partial-sum path is a discrete circle of radius n/2π; taking every m-th vector gives the same circle at
radius n/(2πm), and starting block j a fraction j/m further along the cycle rotates its circle by 2πj/m about
the origin — hence a rose of m circles, all through the origin.
