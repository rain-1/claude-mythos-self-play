# The sign of det A_n for the "i+j is a power of 2" matrix

**Setting** (MO question 513368). Let `A_n` be the n×n 0/1 matrix with
`A_n[i,j] = 1` iff `i+j` is a power of 2, for `1 ≤ i,j ≤ n`.  The accepted
answer (2026) shows `perm(A_n) = 1`: there is exactly one permutation π of
{1,…,n} with `i + π(i)` a power of 2 for all i, hence `det(A_n) = sgn(π) ∈
{−1, +1}`.  The value of the sign was left open.  It has a closed form.

**Theorem.** Let `r(n)` denote the number of maximal runs of equal bits in
the binary expansion of n (e.g. `r(2730) = r(101010101010₂) = 12`,
`r(2^k) = 2` for `k ≥ 1`, `r(2^k − 1) = 1`).  Then

    det(A_n) = (−1)^((n − r(n)) / 2).

**Proof.**  Write `2^k ≤ n < 2^{k+1}`.  As in the accepted answer, for every
`i` with `2^{k+1} − n ≤ i ≤ n` the unique permutation is forced to satisfy
`π(i) = 2^{k+1} − i` (for `i > 2^k − 1` no smaller power of 2 is reachable,
and taking inverses forces the rest of the interval); the remaining indices
`{1, …, m}` with

    m = 2^{k+1} − n − 1

carry a copy of the same problem, because for `i, j ≤ m` we have
`i + j ≤ 2(2^{k+1} − n − 1) < 2^{k+1}` (using `2^k ≤ n`), so only the smaller
powers of 2 are in play.  Hence π is the disjoint union of the interval
reversal of `I_1 = [2^{k+1}−n, n]` about its midpoint and the unique
permutation of `{1,…,m}`.

Two observations turn this recursion into the formula:

1. *Each stage contributes exactly one fixed point.*  The reversal
   `i ↦ 2^{k+1} − i` on `I_1` fixes exactly `i = 2^k`, and `2^k ∈ I_1`
   always (`2^k ≤ n` and `2^k ≥ 2^{k+1} − n` ⟺ `n ≥ 2^k`).  An interval
   involution with one fixed point on an interval of (odd) length `L` is a
   product of `(L−1)/2` transpositions.

2. *The recursion is bitwise complementation, so the number of stages is
   r(n).*  `m = 2^{k+1} − 1 − n` is the bitwise complement of n inside its
   k+1 binary digits.  Complementation turns the leading run of n into
   leading zeros (which vanish) and complements the remaining runs, so
   `r(m) = r(n) − 1`, and n reaches 0 after exactly `r(n)` stages.

Consequently π has exactly `r(n)` fixed points, and its transpositions
number `(n − r(n))/2`, giving `sgn(π) = (−1)^{(n − r(n))/2}`.  ∎

**Sanity notes.**  `n ≡ r(n) (mod 2)` automatically (every stage consumes an
interval of odd length).  Hand checks: `A_2 = I₂` (only 1+1 and 2+2 are
powers of 2), det = +1; formula: `(2 − r(10₂))/2 = 0` → +1. ✓
`A_3 = [[1,0,1],[0,1,0],[1,0,0]]`, det = −1; formula: `(3 − r(11₂))/2 =
(3−1)/2 = 1` → −1. ✓  `A_4`: rows 2 and 4 are unit vectors, leaving minor
`[[1,1],[1,0]]`, det = −1; formula: `(4 − r(100₂))/2 = 1` → −1. ✓
For `n = 2^a`, a ≥ 2: sign `(−1)^{2^{a−1}−1} = −1` (verified at 2048, 4096).

**Verification** (`verify_ledger.py` in this directory):
- all n ≤ 400: determinant computed exactly two independent ways
  (fraction-free elimination mod 2³¹−1 and mod 2³¹−19, plus exact
  `fractions.Fraction` elimination at n = 37, 100, 173, 256) equals the
  formula and equals the sign of the explicitly constructed permutation;
- 30 uniformly random n ∈ [401, 3000] and n = 1000, 2048, 2730, 3000, 4095,
  4096: same agreement.

**Corollary.**  det A_n depends on n only through n mod 4 and the run
count: among n ≤ 4096 the signs split 2015 (+) / 2081 (−) — the ledger is
signed almost fairly, and the sign sequence is 2-automatic (r(n) is
computable by a finite automaton reading n's bits).
