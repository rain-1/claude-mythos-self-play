# Two theorems on the Fibonacci-sum matrix (MO 513340)

**Setting.** Let q₁ = 1, q₂ = 2, q₃ = 3, q₄ = 5, … be the distinct Fibonacci
numbers (qₜ₊₁ = qₜ + qₜ₋₁), and set q₀ := 1 where it appears as a bound. Let
Q = {1, 2, 3, 5, 8, …} and let Mₙ be the n×n matrix with (Mₙ)ᵢⱼ = 1 iff
i + j ∈ Q (only qₜ with t ≥ 2 can occur, since i + j ≥ 2). A *Fibonacci
permutation* of [1, n] is a permutation π with i + π(i) ∈ Q for all i;
per(Mₙ) counts them. Blocks: for n ∈ [q_K, q_{K+1}) write m = n − q_K.

These notes prove, for the two laws found empirically on 2026-08-01:

* **Theorem 1 (golden dead zone).** det Mₙ = 0 whenever
  m ∈ [0, q_{K−5} − 1] or m ∈ [q_{K−3}, q_{K−1} − 1] (K ≥ 7; blocks K ≤ 6
  verified directly). Hence all n with det Mₙ ≠ 0 satisfy
  m ∈ [q_{K−5}, q_{K−3} − 1] — asymptotically the golden window
  [1/φ⁴, 1/φ²] of each block.

* **Theorem 2 (lone voice).** Let u₁, u₂, u₃, u₄ = 1, 2, 3, 5 and
  u_k = q_k + u_{k−4} (Zeckendorf `1(0001)*`). Then per(M_{u_K}) = 1: the
  unique Fibonacci permutation is the involution π*_K that reflects each
  segment (u_{j−2}, u_j] across q_{j+1} (j = K, K−2, K−4, …). Consequently
  det M_{u_K} = sign(π*_K) ∈ {+1, −1} ≠ 0.

Every lemma and inequality below is additionally machine-checked by
`verify_proofs.py` (all checks pass for K ≤ 18, windows t ≤ 21, plus spot
checks of dead-zone determinants and independent DP verification of
per(M_{u_K}) = 1 for K ≤ 19).

---

## 1. The dead zone

**Lemma 1 (three-term Fibonacci identity).** Let t ≥ 2 and
q_{t−2} < s < 2q_{t+1}. Then

  𝟙_Q(s) = 𝟙_Q(s + qₜ) + 𝟙_Q(s + q_{t+1}).

*Proof.* Write W = (q_{t−2}, 2q_{t+1}). Three enumerations:

1. **Q ∩ W = {q_{t−1}, qₜ, q_{t+1}, q_{t+2}} ∩ W.** Indeed
   q_{t+3} = q_{t+2} + q_{t+1} = 2q_{t+1} + qₜ > 2q_{t+1}, so no larger
   Fibonacci number lies below 2q_{t+1}; and none other lies above q_{t−2}.
2. **{s ∈ W : s + qₜ ∈ Q} = {q_{t−1}, q_{t+1}} ∩ W.** Here
   s + qₜ ∈ (qₜ + q_{t−2}, 2q_{t+1} + qₜ) = (qₜ + q_{t−2}, q_{t+3}); since
   q_{t+1} = qₜ + q_{t−1} > qₜ + q_{t−2}, the Fibonacci numbers in that
   range are exactly q_{t+1} and q_{t+2}, giving s = q_{t+1} − qₜ = q_{t−1}
   or s = q_{t+2} − qₜ = q_{t+1}.
3. **{s ∈ W : s + q_{t+1} ∈ Q} = {qₜ, q_{t+2}} ∩ W.** Similarly
   s + q_{t+1} ∈ (q_{t+1} + q_{t−2}, 3q_{t+1}), and
   3q_{t+1} < q_{t+4} = 3q_{t+1} + 2qₜ, so the Fibonacci values available
   are exactly q_{t+2} and q_{t+3}, giving s = qₜ or s = q_{t+2}.

The sets in (2) and (3) are disjoint and their union is the set in (1).
Hence both sides of the identity are the indicator function of the same
subset of W. ∎

**Lemma 2 (kernel vectors).** Let t ≥ 2, a ≥ q_{t−2},
a + q_{t+1} ≤ n ≤ 2q_{t+1} − a − 1. Then
x = −e_a + e_{a+qₜ} + e_{a+q_{t+1}} ∈ ker Mₙ, so det Mₙ = 0.

*Proof.* (Mₙx)ᵢ = −𝟙_Q(i+a) + 𝟙_Q(i+a+qₜ) + 𝟙_Q(i+a+q_{t+1}) for
1 ≤ i ≤ n. Since s = i + a ranges over [a+1, a+n] ⊆ (q_{t−2}, 2q_{t+1}),
each entry vanishes by Lemma 1. x ≠ 0, so Mₙ is singular. ∎

**Theorem 1.** For K ≥ 7:
det Mₙ = 0 for every n ∈ [q_K, q_K + q_{K−5} − 1] ∪ [q_K + q_{K−3}, q_{K+1} − 1].

*Proof.* Two instances of Lemma 2.

*Head.* Take t = K−2, a = q_{K−4} (= q_{t−2}). Lower bound:
a + q_{t+1} = q_{K−4} + q_{K−1} < q_{K−2} + q_{K−1} = q_K ≤ n. Upper bound:
using 2q_{K−1} = q_K + q_{K−3},
n ≤ 2q_{K−1} − q_{K−4} − 1 = q_K + (q_{K−3} − q_{K−4}) − 1 = q_K + q_{K−5} − 1.

*Tail.* Take t = K−1, a = q_{K−3} (= q_{t−2}). Lower bound:
a + q_{t+1} = q_{K−3} + q_K, exactly the start of the tail zone. Upper
bound: using 2q_K = q_{K+1} + q_{K−2},
2q_K − q_{K−3} − 1 = q_{K+1} + (q_{K−2} − q_{K−3}) − 1 = q_{K+1} + q_{K−4} − 1
≥ q_{K+1} − 1, covering the rest of the block. ∎

**Remark.** The bound is exact: the census (n ≤ 75,024) shows det ≠ 0 *at*
m = q_{K−5} and *at* m = q_{K−3} − 1 = q_{K−4} + q_{K−6} + ⋯ for every
block 8 ≤ K ≤ 23. Proving that these endpoints are always attained (i.e.
per(Mₙ) is odd there) remains open; Theorem 2 proves it for the
`1(0001)*` positions inside the window.

---

## 2. The lone voice

Recall u₁, …, u₄ = 1, 2, 3, 5, u_k = q_k + u_{k−4}, and set u₀ = u₋₁ = 0.

**Lemma 3 (u-arithmetic).** For all j ≥ 2:
(a) u_j + u_{j−2} = q_{j+1} − 1;
(b) u_{j−1} ≤ u_j < q_{j+1};
(c) 2u_j ≤ q_{j+2} − 1.

*Proof.* (a) With the convention u_j = 0 for j ≤ 0, the recursion
u_j = q_j + u_{j−4} holds for every j ≥ 1 (bases included). Let
v_j = u_j + u_{j−2}. For j ≥ 3,
v_j − v_{j−4} = (u_j − u_{j−4}) + (u_{j−2} − u_{j−6}) = q_j + q_{j−2}
             = q_{j+1} − q_{j−3},
so v_j − (q_{j+1} − 1) satisfies the same recursion with zero increments;
the base values v₂, v₃, v₄, v₅ = 2, 4, 7, 12 equal q₃−1, q₄−1, q₅−1, q₆−1,
and v_j = q_{j+1} − 1 follows for all j ≥ 2. 
(b) Monotonicity is immediate from the recursion; u_j < q_{j+1} follows by
induction: u_j = q_j + u_{j−4} < q_j + q_{j−3} < q_j + q_{j−1} = q_{j+1}.
(c) By (a) and (b): 2u_j = (u_j + u_{j−2}) + (u_j − u_{j−2}), and
u_j − u_{j−2} = q_j − (u_{j−2} − u_{j−4}) ≤ q_j by monotonicity, so
2u_j ≤ (q_{j+1} − 1) + q_j = q_{j+2} − 1. ∎

Fix K ≥ 7 and n = u_K. Let π be **any** Fibonacci permutation of [1, n].

**Lemma 4 (top forcing).** π(i) = q_{K+1} − i for every
i ∈ [q_K, u_K] ∪ [u_{K−2} + 1, q_{K−1}]; in particular these two intervals
are matched to each other bijectively by the reflection across q_{K+1}.

*Proof.* First, no pair of π sums to q_{K+2} or beyond: for any i, j ≤ n,
i + j ≤ 2u_K ≤ q_{K+2} − 1 by Lemma 3(c). Now let i ∈ [q_K, u_K] (as a
row). Any q ∈ Q with 1 ≤ q − i ≤ n satisfies q > i ≥ q_K and
q ≤ i + n < q_{K+2}, hence q = q_{K+1}: the move is forced, and
π(i) = q_{K+1} − i ∈ [q_{K+1} − u_K, q_{K−1}] = [u_{K−2} + 1, q_{K−1}]
(the identity q_{K+1} − u_K = u_{K−2} + 1 is Lemma 3(a)). The same
argument applied to columns j ∈ [q_K, u_K] (Mₙ is symmetric) forces
π(q_{K+1} − j) = j. These constraints are consistent and pair the two
intervals by the stated reflection. ∎

After Lemma 4 the surviving rows and columns are
V = B ∪ S, B = [1, u_{K−2}], S = (q_{K−1}, q_K).

**Lemma 5 (trichotomy).** Every admissible pair (i, j) ∈ V × V (i.e.
i + j ∈ Q) is of exactly one of three kinds:
(i) *B-internal*: i, j ∈ B; then i + j ≤ 2u_{K−2} < q_K (Lemma 3(c) one
    index down: 2u_{K−2} ≤ q_K − 1), so admissibility in B coincides with
    admissibility in the standalone problem M_{u_{K−2}};
(ii) *S-internal*: i, j ∈ S; then i + j ∈ (2q_{K−1}, 2q_K), and since
    2q_{K−1} = q_K + q_{K−3} > q_K and 2q_K = q_{K+1} + q_{K−2} < q_{K+2},
    the only Fibonacci value available is q_{K+1}: j = ρ(i) where
    ρ(i) := q_{K+1} − i, an involution of S onto itself;
(iii) *crossing*: one index in S, the other in B; then
    i + j ∈ (q_{K−1} + 1, q_K + u_{K−2}) ⊂ (q_{K−1}, q_{K+1}), so the only
    Fibonacci value is q_K: the pair is (i, q_K − i). ∎

**Theorem 2.** per(M_{u_K}) = 1 for all K ≥ 1; the unique Fibonacci
permutation is π*_K (segment (u_{j−2}, u_j] reflected across q_{j+1} for
j = K, K−2, …), and every pair-sum of π*_K is a q_j with
**j ≡ K + 1 (mod 2)**.

*Proof.* Strong induction on K with the displayed statement as the
hypothesis H(K). For K ≤ 6 all claims are verified directly by
enumeration (per(M_n) computed independently; `verify_proofs.py`).

Let K ≥ 7 and let π be a Fibonacci permutation of [1, u_K]. Apply
Lemmas 4–5. Let X = {i ∈ S : π(i) ∈ B} (the *crossing rows*; by
Lemma 5(iii), π(i) = q_K − i for i ∈ X, and π(i) = ρ(i) for i ∈ S ∖ X).

Suppose X ≠ ∅. The columns of S covered from S are ρ(S ∖ X), so the
columns ρ(X) must be covered from B, and by Lemma 5(iii) the only
possible source of column ρ(i) is the row q_K − ρ(i) = i − q_{K−1} ∈ B.
For each i ∈ X put rᵢ = i − q_{K−1} and cᵢ = q_K − i, so that B loses the
rows {rᵢ} (they map into S) and the columns {cᵢ} (consumed from S), with

  rᵢ + cᵢ = q_{K−2},  rᵢ, cᵢ ∈ (0, q_{K−2}),

and the rᵢ (resp. cᵢ) pairwise distinct. All other rows of B map inside
B. Therefore

  σ := π|_{B ∖ {rᵢ}} ∪ {(rᵢ ↦ cᵢ) : i ∈ X}

is a Fibonacci permutation of [1, u_{K−2}] (each added pair sums to
q_{K−2} ∈ Q). By H(K−2), σ = π*_{K−2}, all of whose pair-sums are q_j
with j ≡ K − 1 (mod 2). But σ contains a pair summing to q_{K−2}, whose
index K − 2 ≢ K − 1 (mod 2) — a contradiction. Hence **X = ∅**.

With X = ∅, every i ∈ S satisfies π(i) = ρ(i) (Lemma 5(ii) is the only
remaining option), and B is π-invariant with π|_B a Fibonacci permutation
of [1, u_{K−2}]; by H(K−2), π|_B = π*_{K−2}. Together with Lemma 4, π is
the reflection across q_{K+1} on the whole segment
(u_{K−2}, u_K] = [u_{K−2}+1, q_{K−1}] ∪ S ∪ [q_K, u_K], and equals
π*_{K−2} below: that is exactly π*_K, and it is indeed a valid Fibonacci
permutation (its top pairs sum to q_{K+1}). Its pair-sums are q_{K+1}
(index K+1) and, inductively, q_j with j ≡ K − 1 ≡ K + 1 (mod 2). H(K)
holds. ∎

**Corollary 1.** det M_{u_K} = sign(π*_K) ∈ {+1, −1}; explicitly
sign(π*_K) = ∏_j (−1)^{⌊(u_j − u_{j−2})/2⌋} over the segments
(j = K, K−2, … ≥ 1). Machine-checked against the census for all
u_K ≤ 75,024 (18 values).

**Corollary 2.** The lone-voice positions lie inside the golden window of
Theorem 1: u_K − q_K = u_{K−4} ∈ [q_{K−5}, q_{K−3} − 1] by Lemma 3(b).

---

## 3. What remains open

1. **Endpoint attainment**: det ≠ 0 at m = q_{K−5} and m = q_{K−3} − 1
   for every K (equivalently per(Mₙ) odd there). Verified for all
   8 ≤ K ≤ 23. A route: after Lemma-4-type peeling, the crossing-set
   expansion gives per(Mₙ) ≡ #{Fibonacci matchings of the reduced
   two-interval problem avoiding all q_{K−2}-reflection pairs} (mod 2);
   the parity bookkeeping through the zipper is unfinished.
2. **Full characterization** of {n : det Mₙ ≠ 0} inside the window (859
   values ≤ 28,656, not in OEIS). The prefix-signature analysis suggests
   it is *not* recognized by a small Zeckendorf DFA.
3. The determinant **sign** law inside the window.
