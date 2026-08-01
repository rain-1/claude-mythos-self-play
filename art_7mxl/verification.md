# Verification notes — run 2026-08-01 (`art_7mxl`)

Triptych **THE CASTING VOTE** — what survives massive cancellation.
Seeds: LIVE MathOverflow front page (513340 Fibonacci-sum determinant 35↑,
513787 two-squares APs, 41939 balls-and-colours 25↑) + Phil.SE front page
("Why is it rational to assert X without a rebuttal for every argument
ending therefore not-X?", "Can idealism/solipsism be dismissed…?").

All computations from scratch in this repo; no CAS, no external tables.

---

## 1. The Fibonacci-sum determinant (MO 513340) — hero

`(M_n)_{ij} = 1  iff  i+j ∈ {1,2,3,5,8,13,…}`, conjecture `det M_n ∈ {−1,0,1}`.

**Engines.**
- `detlib.py` — exact integer sparse Gaussian elimination, min-degree
  pivoting, sign tracked by Fenwick-rank parity. A **total-unimodularity
  tripwire** asserts every intermediate entry stays in {−1,0,1}
  (Schur entries of a TU matrix are minors up to sign). The tripwire never
  fired across every determinant computed this run —
  **live TU verification over ~110,000 eliminations** (census to 75,024 +
  spot checks), consistent with the TU theorem claimed in the answer.
- `permlib.py` — exact permanent (= number of Fibonacci permutations) via
  min-degree chordal completion → elimination-forest DP over separator
  tables. Elimination width comes out **2** at every n tried (the
  bipartite Fibonacci-sum graph is treewidth-2 in practice, matching the
  outerplanarity of the Arman–Gunderson–Li Fibonacci-sum graph).
  n=1000 permanent (~10^107) in 40 ms.

**Cross-checks.**
- census reproduces the poster's nonzero list n ≤ 120 and the first
  answer's full table to n = 1219 **exactly**;
- per(33) = 10800 = poster's value, split 5400/5400 even/odd (det 0 ⇔ tie);
- parity tripwire per(n) ≡ det(n) (mod 2) on 25 random n — two independent
  engines agree;
- n = 104: permanent = 1 and the DP-sampled unique permutation is odd,
  matching det = −1 exactly.

**Census results (n ≤ 75,024 = F₂₄−1, exact).**
- det M_n ∈ {−1,0,1} everywhere (no counterexample; TU tripwire silent).
- Nonzero-det positions: 859 up to 28,656; **the sequence is not in OEIS**
  (checked 2026-08-01, both the set and its difference sequence).

**New empirical laws** (all exact statements about the computed censuses):

1. **Golden window.** Within each Fibonacci block [F_k, F_{k+1}):
   - the FIRST n with det ≠ 0 is exactly `n = F_k + F_{k−5}`
     (Zeckendorf `100001 0…0`), verified k = 8..21;
   - the LAST n with det ≠ 0 is the Zeckendorf word `1000(10)*`
     (n = F_k + F_{k−4} + F_{k−6} + F_{k−8} + ⋯), verified k = 8..21;
   - hence the nonzero set lives in the window
     [F_k + F_{k−5},  F_k + F_{k−4} + F_{k−6} + ⋯], whose relative
     position inside the block converges to **[1/φ⁴, 1/φ²]** — verdicts
     only in the golden window; the last 1−1/φ² ≈ 61.8% of every block is
     entirely det = 0.

2. **Lone voices.** per(M_n) = 1 (a UNIQUE Fibonacci permutation) exactly at
   n = 1, 2, 3, 5, 9, 15, 24, 39, 64, 104, 168, 272, 441, 714, 1155
   (all n ≤ 1597), satisfying the recursion **u_k = F_k + u_{k−4}** —
   Zeckendorf pattern `1(0001)*`. All of these have det ≠ 0.

3. **Massive cancellation quantified.** n = 97: 333,973,125 permutations,
   166,986,563 even vs 166,986,562 odd (det = +1 — "carried by one vote");
   n = 100: 10,562,500 permutations split exactly 5,281,250 : 5,281,250
   (det = 0). At n = 987 the permanent is ~10^105.6 while det = 0.

**Automaton.** The msd-first Zeckendorf prefix-signature method finds a
deterministic Moore machine consistent with the census (zero transition
conflicts at every signature depth tried), but the state count is still
growing with available prefix depth (155 states at k*=5 on the 28k census)
— the minimal automaton, if finite, needs a deeper census than depth ~21
words to close. Signature machines trained at depth ≤ 16 mispredict some
held-out values, so we do NOT claim a finite characterization; the exact
window laws above are the safe, fully verified statements.
(See §1a addendum below for the final census status.)

## 2. APs of consecutive sums of two squares (MO 513787) — piece 37

S = {x²+y² : x,y ∈ ℤ≥0} sieved exactly to 10⁹ (block marking; membership
independently re-verified by trial-division factorization on all reported
witnesses — a number is in S iff every prime ≡ 3 (mod 4) divides it to an
even power).

**(a) equal-gap runs of CONSECUTIVE elements of S** — first occurrences:

| l | first run | gap |
|---|---|---|
| 3 | 0, 1, 2 | 1 |
| 4 | 757, 761, 765, 769 | 4 |
| 5 | 2989 … 3005 | 4 |
| 6 | 28,059,605 … 28,059,665 | 12 |

No run of length 7 below 10⁹. The length-6 run was re-verified by
factorization: all six terms in S, no other member of S between them, and
it extends in neither direction.

**(b) smallest k with 1, 1+k, …, 1+(l−1)k ∈ S:**
k(2)=1, k(3..5)=4, k(6..11)=12, k(12..16)=336; no k < 2×10⁶ reaches l=17
(within terms < 10⁹). Note 4 = 2², 12 = 2²·3, 336 = 2⁴·3·7.

**2-adic good-step law** (Thread A's unified law at the ramified prime 2):
sums of two squares avoid {3, 6, 7} mod 8; an AP of length ≥ 4 inside S is
forced into k ≡ 0 (mod 4), and all record gaps/steps found are 2-adically
good (1; 4; 4; 12 ≡ 4 mod 8; k = 4, 12, 336 ≡ 0 mod 4). This revives the
AP-obstruction atlas as **piece 37**.

## 3. Balls-and-colours (MO 41939)

Process: pick an ordered pair of distinct balls uniformly, paint the second
with the first's colour. E[T to monochrome] = (n−1)².

- **Exact**: linear solve on colour-count-partition Markov chains gives
  E[T] = 1, 4, 9, 16, 25, 36, 49 for n = 2..8 — exactly (n−1)², to
  1e-12 numerically.
- **Ensembles**: n=32: 969.3 ± 8.7 (target 961); n=128: 16,295 ± 224
  (target 16,129).
- **Proof sketch rendered in the piece** (folklore, via duality): tracing
  ancestries backward, k surviving lineages coalesce at rate
  k(k−1)/(n(n−1)) per step, so
  E[T] = n(n−1) · Σ_{k=2}^{n} 1/(k(k−1)) = n(n−1)(1 − 1/n) = (n−1)².
- The rendered run (n=512): T = 329,889 (mean 261,121; the distribution is
  heavy-tailed). The extinction-frontier in the image is overlaid with the
  mean-field block-counting curve k(t) = [1−(1−1/n)e^{−t/(n(n−1))}]⁻¹.

## Pieces

- `hero2_4096.png` — **The Casting Vote** (4096²)
- `twosq_2560.png` — **The Ladders in the Thin Set** (2560², atlas piece 37)
- `colors_2560.png` — **The Last Colour** (2560²)
