# Iterated differences of the primes — MO 515079 and Gilbreath's triangle

**The question (MathOverflow 515079, "Linear equations with consecutive primes").** For every n ≥ 1, is there
(are there infinitely many) j with Σ_{k=0}^{n} C(n,k)(−1)^k p_{j+k} = 0?  The sum is the signed n-th forward
difference D_n(j) of the prime sequence at j (p₁ = 2).  The poster's examples: n = 3: j = 7, 11, 13, 18, 22;
n = 5: 13, 17, 53, 87; n = 9: 43, 101, 250.  All three lists are reproduced exactly by the census below.

## Census (`primediff.py`, primes < 2·10⁹, J = 98,222,287 indices, all n ≤ 40)

n = 1 has no zero at all (consecutive primes differ), so the question starts at n = 2.

| n | least zero j_min | zeros with j ≤ 9.8·10⁷ | log₂ j_min − n |
|---|---|---|---|
| 2 | 2 | 311,444 (j ≤ 1.1·10⁷) | −1.0 |
| 3 | 7 | 445,615 (j ≤ 1.1·10⁷) | −0.2 |
| 4 | 69 | 165,404 (j ≤ 1.1·10⁷) | 2.1 |
| 5 | 13 | 107,863 (j ≤ 1.1·10⁷) | −1.3 |
| 6 | 47 | 30,692 (j ≤ 1.1·10⁷) | −0.5 |
| 7 | 58 | 25,255 (j ≤ 1.1·10⁷) | −1.1 |
| 8 | 9 | 11,109 (j ≤ 1.1·10⁷) | −4.8 |
| 9 | 43 | 8,823 (j ≤ 1.1·10⁷) | −3.6 |
| 10 | 3,553 | 2,868 (j ≤ 1.1·10⁷) | 1.8 |
| 11 | 100 | 1,735 (j ≤ 1.1·10⁷) | −4.4 |
| 12 | 7,019 | 1,009 (j ≤ 1.1·10⁷) | 0.8 |
| 13 | 14,082 | 393 (j ≤ 1.1·10⁷) | 0.8 |
| 14 | 68,097 | 219 (j ≤ 1.1·10⁷) | 2.1 |
| 15 | 14,526 | 93 (j ≤ 1.1·10⁷) | −1.2 |
| 16 | 149,677 | 411 | 1.2 |
| 17 | 2,697 | 211 | −5.6 |
| 18 | 481,054 | 81 | 0.9 |
| 19 | 979,719 | 59 | 0.9 |
| 20 | 631,894 | 28 | −0.7 |
| 21 | 29,811 | 14 | −6.1 |
| 22 | 25,340,978 | 5 | 2.6 |
| 23 | 50,574,254 | 2 | 2.6 |
| 24 | 7,510,843 | 5 | −1.2 |
| 25 | none yet (j ≤ 9.8·10⁷) | 0 | > 1.5 |
| 26 | 67,248,861 | 2 | 0.0 |
| 27–40 | none yet | 0 | |

(Rows n ≤ 15 list the counts from the first run, primes < 2·10⁸; rows n ≥ 16 from the second, primes < 2·10⁹.)

## Why 2ⁿ: the mechanism

D_n(p) at j is the (n−1)-th difference of the gap sequence g_j = p_{j+1} − p_j.  If the gaps were white noise
with variance s², Var D_n = C(2n−2, n−1)·s² ≈ 4^{n−1} s² /√(π(n−1)).  Measured (first 2·10⁶ indices, s² = 187.7,
mean gap 16.2): Var D_n / (C(2n,n) s²) = 0.275, 0.268, 0.266, 0.265 for n = 10, 20, 30, 40 — i.e. 1.07 × the
white prediction C(2n−2,n−1)/C(2n,n) → 1/4.  The gap autocorrelation at lag 1 is only −0.034, and the spectral
density of the gaps at the Nyquist frequency π (measured by alternating block sums: 196 vs variance 188) is white.
So the differencing acts as a narrow band-pass filter at ω = π with gain 2ⁿ, and

    σ_n ≈ 2^{n−1} · s · (π(n−1))^{−1/4} · 1.03,   with s ≈ the gap standard deviation (grows like log j).

D_n is always even (all primes odd for j ≥ 2), so a Gaussian local law gives P(D_n(j) = 0) ≈ 2/(σ_n √(2π)).
Check: predicted zero counts up to J = 9.8·10⁷: n = 16: 447 (measured 411); n = 20: 29.4 (measured 28);
n = 22: 7.3 (5); n = 24: 1.8 (5).  Predicted least zero E[j_min] ≈ 1.25 σ_n ≈ 8.6 · 2ⁿ · (πn)^{−1/4}:
n = 24: 4.9·10⁷ (observed 7.5·10⁶), n = 25: 9.7·10⁷ (nothing yet below 9.8·10⁷ — consistent), n = 26: 1.9·10⁸
(observed 6.7·10⁷, an early one).

## Conjectures (stated as such)

1. **For every n ≥ 2 there are infinitely many j with D_n(j) = 0.**  Heuristic count up to J:
   N_n(J) ≈ (2/√(2π)) Σ_{j≤J} 1/σ_n(j) ≍ J / (2ⁿ log J) → ∞.  (For n prime this gives the poster's corollary:
   infinitely many j with n | p_{n+j} − p_j.)  n = 1 is the only exception (no zeros).
2. **j_min(n) = 2^{n + O(1)}: the variable log₂ j_min(n) − n has a limiting distribution** (the log of a geometric
   waiting time, centred near 1.5 with an exponential left tail).  Measured over n = 2..26: mean −0.67,
   standard deviation 2.5, range [−6.1, 2.6].  The lucky early zeros (n = 8: j = 9; n = 17: 2,697; n = 21:
   29,811) are the left tail, not a second law.
3. What it would take to prove 1: nothing known — even D_2(j) = 0 (balanced primes, p_{j+1} = (p_j + p_{j+2})/2)
   is not known to happen infinitely often; it follows from prime k-tuples.  The 2ⁿ law is a statement about
   the prime gaps' spectrum at the Nyquist frequency being white, which is itself only heuristic (it is
   consistent with the Hardy–Littlewood pair correlation of gaps).

## Gilbreath's triangle (the picture)

Row 0 the primes, each row the absolute differences of the row above.  Gilbreath's conjecture (1958; Proth
1878): every row begins with 1.  Odlyzko checked 3.4·10¹¹ rows (1993).  Certificate in this run: the first
entry is 1 in every one of the first 3000 rows (`primediff.json`, `all_firsts_one`), and in every row of the
picture (`gilbreath_2560_cert.json`).

What the picture shows, measured: within the first 3000 columns the entries > 2 die out by row 50 (j₀ = 1),
row 80 (j₀ = 10⁵), row 62 (j₀ = 10⁷) — the crust depth grows only slowly with the gap size.  A value v > 2 sitting
in a sea of 0s and 2s survives one row with probability ~1/2 (|v − 0| or |v − 2|), always moving one column
left, hence the down-left stalactites of geometric length.  Below the crust the rule |a − b| on {0, 2} is XOR,
i.e. elementary cellular automaton Rule 90, so the sea is a Rule-90 evolution of the crust's last wild row and
carries Sierpiński holes.  Sea composition below row 100: 49.9 % twos, 50.0 % zeros.
