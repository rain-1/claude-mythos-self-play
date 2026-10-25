# MO 516346: are odd abundant numbers "half-representable"?

Question (G. Melfi): for every odd abundant n, is (n+1)/2 a sum of distinct divisors of n?
Notation: R(n) is the set of subset sums of the divisors of n. It lies inside [0, σ(n)] and is symmetric under x ↦ σ(n) − x.

## Headline

1. **The answer is no.** The smallest counterexample is **n = 3,635,415 = 945·3847 = 3³·5·7·3847**. This agrees with JoshuaZ's MO answer (score 4), and our exhaustive search shows nothing smaller exists.
2. **Exhaustive counts.**
   - Up to **10⁷**: 20,661 odd abundant n, of which **758** are counterexamples. They are exactly the numbers 945·p with p prime and 3847 ≤ p ≤ 10567 (every prime in that range).
   - Up to **10⁸**: 205,366 odd abundant n, of which **23,275 are counterexamples (11.3%)**.
3. **Every counterexample up to 10⁸ is explained by one exact rule.** The digit criterion below predicts the 23,275 counterexamples exactly: no misses and no false positives (`predict_1e8.txt`). Every one has the form n = A·p where:
   - A is odd abundant,
   - p is a prime with p > σ(A),
   - (p+1)/2 ∉ R(A).

   In practice this means p ≥ 2σ(A)+1. Two sporadic "window" cases also occur, where p < 2σ(A) but (p+1)/2 = σ(A) − 2, which is never in R(A):
   - 2205·8887 = 19,595,835
   - 4095·17467 = 71,527,365

   | A | σ(A) | counterexamples ≤ 10⁸ (primes p) |
   |---|---|---|
   | 945 | 1920 | 9559 (p in 3847…105817) |
   | 1575 | 3224 | 5527 (p in 6449…63487) |
   | 2205 | 4446 | 3600 (p in 8887…45343; includes window prime 8887) |
   | 2835 | 5808 | 2361 (p in 11617…35267) |
   | 3465 | 7488 | 1389 (p in 14983…28859) |
   | 4095 | 8736 | 703 (p in 17467…24419; includes window prime 17467) |
   | 4725 | 9920 | 136 (p in 19841…21163) |

4. **The "large interval" behaviour has a sharp dichotomy (checked exhaustively to 10⁷).** Let ρ(n) = max over prime powers p^k ‖ n of p / σ(n/p^k), and let h be the largest h such that every integer in [(n−1)/2 − h, (n+1)/2 + h] is in R(n).
   - **ρ(n) ≤ 1** (19,282 numbers): h/n ≥ **0.4963**. The minimum is at n = 945, where h = 469. The median of h/n is 0.5000. Here R(n) misses only a handful of values near 0 and σ, so essentially all of [3, σ−3] is representable.
   - **ρ(n) > 1** (1,379 numbers): h/n ≤ **0.00052**. Of these, 758 are counterexamples (h = −1) and 621 still pass but only through a narrow window.

   So Melfi's stronger suspicion holds exactly when n has no "isolated large prime". When n does have one, the interval around n/2 has width less than σ(A), and it vanishes once p ≥ 2σ(A).

## Why the counterexamples exist (complete proof)

Let n = A·p^k with p prime, p ∤ A, and p > σ(A). Every divisor of n is d·p^j with d | A, so R(n) = { a₀ + a₁p + … + a_k p^k : a_j ∈ R(A) }. Each a_j ≤ σ(A) < p, so this base-p expansion is unique. The target has base-p digits

  T = (n+1)/2 = (p+1)/2 + (p−1)/2·(p + … + p^{k−1}) + (A−1)/2·p^k.

So T ∈ R(n) if and only if (p+1)/2, (p−1)/2 (when k ≥ 2) and (A−1)/2 all lie in R(A).

- If p ≥ 2σ(A)+1, the digit (p+1)/2 exceeds σ(A), so **n = A·p^k is a counterexample for every odd abundant A, prime p ≥ 2σ(A)+1 and k ≥ 1**. That gives infinitely many counterexamples, and also covers JoshuaZ's A·p^k suspicion.
- n is abundant automatically, since σ(n)/n > σ(A)/A > 2.
- A must be non-deficient. If A were deficient, then σ(n) > 2n would force p < σ(A)/(2A − σ(A)) ≤ σ(A).
- This is consistent with JoshuaZ's guess that primitive non-deficient numbers are fine: every counterexample found has the abundant proper divisor A.

The 945·p family shows the transition clearly (from `scan_1e7.csv`):

| p | regime | h | h/n | share of [0, σ] not in R(n) |
|---|---|---|---|---|
| 1009 | p < σ(945) = 1920 | 473722 | 0.4968 | ≈ 0 (gaps only near the ends, below 3p) |
| 1931 | p just above σ | 951 | 0.0005 | 0.7% |
| 3001 | | 416 | | 36% |
| 3833 | | 0 | | 50% |
| 3847 | p ≥ 2σ+1 = 3841 | −1 (fails) | | |

Once p > σ, R(n) breaks into disjoint blocks pb + R(A). The block that holds n/2 is b = 472, which covers 472p + [3, 1917], so h = min(p/2 − 3, 1917 − p/2) roughly. That reaches 0 at p ≈ 3840.

## Positive direction: a proof idea

**Interval-extension lemma.** Suppose the subset sums of d₁…d_i contain the interval [a, S_i − a], where S_i = d₁ + … + d_i. If d_{i+1} ≤ S_i − 2a + 1, then the subset sums of d₁…d_{i+1} contain [a, S_{i+1} − a].

With a = 0 this is the usual practical-number criterion. Odd n are never practical, because 2 ∉ R(n). The lemma with a small seed a replaces practicality.

**945, explicitly.** R(945) = [0, 1920] \ {2, 1918}. Only two values are missing, and 2 and 1918 are swapped by the symmetry.
- Proof: the subset sums of 1, 3, 5, 7 contain [3, 13] (S = 16, a = 3).
- Each later divisor satisfies d_{i+1} ≤ S_i − 5: 9 ≤ 11, 15 ≤ 20, 21 ≤ 35, 27 ≤ 56, 35 ≤ 83, 45 ≤ 118, 63 ≤ 163, 105 ≤ 226, 135 ≤ 331, 189 ≤ 466, 315 ≤ 655, 945 ≤ 970.
- Hence R ⊇ [3, 1917].
- Typical missing sets for other odd abundant n are similar: {2, σ−2}, or a few small values such as 2, 7, 11, 14, 17 or 22 together with their mirror images.

The smallest missing value is always 2, and by symmetry the largest is always σ(n) − 2. The interesting gaps are those near n/2.

**Scope of the lemma.** The lemma alone certifies (n+1)/2 ∈ R(n) for about 90% of odd abundant n up to 10⁷. It is applied as an exact bitset on divisors with prefix sum ≤ 4096, then the lemma (`fastscan.py`). It fails for 2,060 numbers; 1,302 of those still pass on exact check, all of the form A·p with p near σ(A).

**Conjecture (supported to 10⁷ by the dichotomy, and to 10⁸ for the half-target).** If n is odd abundant and every prime power p^k ‖ n satisfies p ≤ σ(n/p^k), then R(n) ⊇ [c, σ(n) − c] with c ≪ n (observed c ≤ 3·(largest prime) in the worst case). In particular (n+1)/2 ∈ R(n) with h > 0.49n.

**Proof route.** Induct on the prime powers in increasing order. If R(A) ⊇ [c, σ(A) − c] and p ≤ σ(A) − 2c + 1, then the translates R(A) + p·j overlap, so R(Ap) contains a long interval. Iterate over k for p^k.

## Data for 945 (`945.json`)

- **Divisors (16):** 1, 3, 5, 7, 9, 15, 21, 27, 35, 45, 63, 105, 135, 189, 315, 945. σ = 1920.
- **`counts[x]`, x = 0…1920 (length 1921):** the number of subsets of all 16 divisors with sum x. The counts are symmetric and total 2¹⁶ = 65536. counts is 0 only at x = 2 and x = 1918. The maximum count is 65, reached at x ∈ {396, 411, 564, 579, 1341, 1356, 1509, 1524}.
- **Subsets with sum 473: 49.** These are listed in `subsets_473`.
  - None can use 945. There are 15 proper divisors; the brief said 14, but 945 has 15 proper divisors.
  - By size: 8 subsets of 5 divisors, 23 of 7, 17 of 9, and 1 of 11. Every subset has an odd number of divisors, since all divisors are odd and 473 is odd.
  - 28 of the 49 avoid the divisor 1.
  - The example 315+105+35+15+3 is one of the 8 five-element subsets.

## Files (all in this folder)

- **Scripts:**
  - `scan.py` computes full R(n) up to σ/2 for every odd abundant n ≤ N and outputs h, L, U and the missing-value count. It produced `scan_1e5/1e6/1e7.csv`. Runs to 10⁷ in 60 s on one core.
  - `fastscan.py` is the lemma-plus-fallback check of the half-target only. It produced `fast_1e7.txt` and `fast_1e8.txt` (cases where the lemma broke, with ok flag). Runs to 10⁸ in 12 min.
  - `predict.py` runs the digit criterion against the fastscan output and produced `predict_1e8.txt`.
  - `analyse.py` produces the summary statistics.
  - `make945.py` builds `945.json`.
  - `util.py` holds helpers.
- **CSV columns:**
  - L / U are the largest / smallest missing values below / above n/2.
  - `nonrep` is the number of missing values in [0, σ].
- **MO thread:** `mo_question.json`, `mo_answers.json`, `mo_comments.json`. There is one answer, JoshuaZ's 945·3847, plus a comment pointing to Zumkeller numbers.
- Everything ran pinned to one core with `taskset -c 0`.
