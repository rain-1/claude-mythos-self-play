# Good permutations (MO 514690): notes

A permutation a_1..a_n of {1..n} (n odd) is *good* if no proper consecutive block of length ≥2 has an integer average.
Below, "proved" means a complete argument is written here or in the MO thread. "Observed" means computed only.

## 0. What the MO thread already has (fetched via the SE API, saved in data/*.json)
- Comment (te4): a_{t+2^k} ≡ a_t (mod 2^k) for 2^k<n, and the first 2^k terms hit every residue mod 2^k.
- Answer 514702 (Bîsceanu) **proves n = 2^m − 1** (a good permutation forces the Mersenne form). Steps: sums of 2^k consecutive terms are odd multiples of 2^{k-1}, so the pairs {a_i, a_{i+q}} are {j, j+q} with q = 2^{m-1}. If n ≠ 2q−1, the middle segment then has average (n+1)/2.
- Answer 516078 (AI-assisted): the given permutation is good **iff n is prime**. Its only failures are prefixes/suffixes whose length is a proper divisor of n. Exhaustive search using the pair structure: counts 7→4, 15→0, 31→4, 63→0, with the 4 being one permutation and its images under reversal and complement. If only lengths coprime to n are checked, n=15 still allows 320 permutations.
- Comment: "k-good" permutations (only lengths ≤ k checked) exist well beyond Mersenne n.

So the **open part is primality**: are there no good permutations for composite 2^m − 1 (63, 255, 511, 1023, 2047, ...)?

## 1. Exact counts (observed, exhaustive)
`naive.c` is a plain DFS over all permutations. It uses incremental prefix sums and makes **no structural assumptions**.

| n | good perms | DFS nodes |
|---|---|---|
| 3 | 2 | 13 |
| 5,9,11,13 | 0 | ≤ 26,693 |
| 7 | **4** | 477 |
| 15,17,19,21,23 | 0 | ≤ 5.0 M |
| 25,27,29 | 0 | ≤ 74 M |
| 31 | **4** | 181.5 M |

n=7: `1 6 7 4 5 2 3`, `3 2 5 4 7 6 1`, `5 6 3 4 1 2 7`, `7 2 1 4 3 6 5`. These are the canonical permutation C, its complement (x→8−x), its reversal, and its reverse-complement (see good7.json).
n=31: likewise exactly the 4 images of C (good31.json).
This independently confirms the asker's data and the Mersenne-form theorem for n ≤ 31, without using any of the theory.

`mers2.c` is an exhaustive search that uses the structure in Section 2 and checks only odd lengths. It reproduces 7→4, 15→0, 31→4, and gives **63→0** (7.1 M nodes, 1.5 s), agreeing with 516078.

## 2. A clean reformulation (proved; it sharpens the MO arguments)
Let n = 2^m − 1, q = 2^{m-1}, and suppose a is good.

**Lemma A.** For every k ≤ m−1, the map σ_k : (t mod 2^k) ↦ (a_t mod 2^k) is well defined and a **bijection** of Z/2^k, with σ_k(0)=0. The σ_k are compatible (σ_k = σ_{k+1} mod 2^k). So σ := σ_{m-1} is an automorphism of the depth-(m−1) binary tree that fixes the leaf 0.
*Proof.* Well-definedness is te4's congruence, valid for all 2^k < n, i.e. k ≤ m−1. On positions 1..n, the class 0 mod 2^k has 2^{m-k}−1 members and every other class has 2^{m-k}. The values 1..n split the same way. If σ_k sent two classes to one value class s, that class would need at least 2(2^{m-k})−1 > 2^{m-k} values. ∎
Consequences: a_q = q; a_{2^k} ≡ 0 (mod 2^k); {a_t, a_{t+q}} = {j, j+q}.

**Lemma B (even lengths are automatic).** Take any arrangement satisfying Lemma A and a block of even length L = 2^k·u (u odd, 1 ≤ k ≤ m−1). The block's positions cover each class mod 2^k exactly u times. So its sum is ≡ u·Σ_{r mod 2^k} r = u·2^{k-1}(2^k−1) ≡ 2^{k-1} (mod 2^k), and L does not divide the sum. ∎

**Corollary.** The good permutations of 2^m−1 are exactly these: choose a tree automorphism σ of Z/2^{m-1} fixing 0, and choose for each of the q−1 pairs which of j, j+q comes first (2^{q-1} ways). Then require **only the odd block lengths 3 ≤ L ≤ n−2** to be non-integer. For n=15 there are 2^4·2^7 = 2048 candidates and none survives. For n=63 the search space is 2^{26}·2^{31}.
Since gcd(L, 2) = 1 for every remaining constraint, the 2-adic structure is used up. Any proof of primality has to use odd-modulus information that interacts with the pairing a_t + a_{t+q} = 2(a_t mod q) + q (note 2q ≡ 1 mod every odd d | n).

## 3. Experiments on the primality question (observed)
- **Relaxed problem** (lengths dividing n are not checked):
  - n=15: 320 survivors (same number as 516078's "coprime lengths" count). **Every one of them has a failing block of length 3.**
  - Skipping only length 3 leaves 8 survivors. Skipping only length 5 leaves 0.
  - Checking only lengths {3,5} (plus the structure) leaves 8.
  - n=63, relaxed, 10-minute partial run: ≥1255 survivors, and **again every one fails at length 3**. The failing length sets seen are {3}, {3,7}, {3,9}, {3,7,9}, {3,7,21}, {3,7,9,21}.
  - This suggests that when 3 | n (m even), length-3 blocks are the robust obstruction. It is not proved: the structure plus length-3 checks alone allow 28 permutations for n=15.
- **Affine family** a_t ≡ α t + β_{t mod 2} (mod 2^m), searched over all α, β_0, β_1. Good members exist for m=3, 5, 7 (only the 4 images of C) and there are 0 for m=4, 6, 8 (n=15, 63, 255).
- **Canonical σ fixed** (σ(t) = −t + 2[t odd] mod q, which is the σ of C), searching all 2^{q−1} orderings of the pairs: exactly 1 good permutation (C itself) for n=31 and 127; **0 for n=15, 63, 255, 511, 1023, 2047**.
  - With divisor lengths skipped, there is exactly 1 for n=63, 255 and 511 (C again, failing only at divisor-length prefixes), and 39 for n=15.
- **n=127**: C is good (verified directly; data/good127_canon.txt). A full count is **not** feasible within the budget: a Knuth random-probe estimate puts the structured search tree at ~6·10^9 surviving nodes, several CPU-hours. A randomized restart DFS (200 M nodes) found nothing, which says little because solutions are extremely sparse. So uniqueness up to symmetry for 127 is **open/unverified**.
- **n=63**: exhaustively 0, so the composite Mersenne 63 has no good permutation (confirming 516078).

## 4. Status and conjecture
Proved (MO thread + Lemma A/B here):
- good ⇒ n = 2^m − 1;
- n Mersenne prime ⇒ good permutation exists;
- the problem reduces to odd lengths on the tree-automorphism-and-pair-choice space.

Verified (exhaustive): no good permutation for n = 15, 63. For n = 7, 31, exactly 4.

**Conjecture 1 (asker's).** A good permutation exists iff n is a Mersenne prime.
**Conjecture 2 (stronger, rigidity).** For a Mersenne prime n the good permutations are exactly the 4 images of C under the Klein group ⟨reversal, complement⟩. Verified for n = 3 (2 images, since they coincide), 7, 31. Since C fails exactly at prefixes of length d | n, Conjecture 2 together with a "near-rigidity" statement for composite 2^m−1 would imply Conjecture 1.
**Conjecture 3 (heuristic, from the data).** If 3 | n (m even), every arrangement satisfying the structure of Section 2 and all non-divisor lengths has a block of length 3 with sum ≡ 0 (mod 3).

**Not proved:** that composite 2^m − 1 admits no good permutation. I did not find a proof. Odd m (e.g. 2047 = 23·89, or 2^9−1 = 7·73) would need a different obstruction anyway.

## Files
- `naive.c`: unstructured exhaustive DFS.
- `mers2.c`: structured exhaustive search.
  - `mers3.c`: randomized restarts.
  - `mers4.c`: Knuth tree-size estimate.
  - `mers5.c`: canonical-σ-fixed search.
  - `mers.c`: first structured version.
- `affine.c`: affine-family scan.
- `good7.json`, `good31.json`: all good permutations for n = 7, 31.
- `data/`: raw outputs (lists of perms; m2r_* = relaxed survivors) and the MO JSON.
