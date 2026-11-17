# Sharing 1ᵏ, 2ᵏ, …, nᵏ between two pans — what was computed and proved

Seed: MathOverflow 296667, *Alternating sum of powers*: for fixed k and all large n, are there signs with
±1ᵏ ± 2ᵏ ± … ± nᵏ equal to the forced parity value (0 when n ≡ 0, 3 mod 4, else ±1)?

Write m(k, n) for the minimum of |±1ᵏ ± … ± nᵏ| and call n *balanced* when m(k, n) ≤ 1.
Let a(k) be the last n that is not balanced.

## 1. Exact values

`ss.cpp` computes m(k, n) exactly (Schroeppel–Shamir: four lists, two heaps, 128-bit integers) and
prints a sign vector that attains it. `small.py` is an independent big-integer bitset check for k ≤ 5.

| k | unbalanced n (m(k, n) in brackets for the late ones) | a(k) | status |
|---|---|---|---|
| 1 | none | 0 | classical |
| 2 | 2–5 | 5 | proved |
| 3 | 2–9, 11 (12) | 11 | proved |
| 4 | 2–15, 18 (13), 21 (9), 26 (5), 29 (5) | 29 | proved |
| 5 | 2–23, 26 (3), 27 (2) | 27 | proved |
| 6 | 2–30, 35 (2) | 35 | proved |
| 7 | 2–36, 38 (5) | 38 | proved |
| 8 | 2–40, 42–44, 51, 52, 59 (14), 60 (10), 67 (6), 68 (6) | 68 | see §4 |
| 9 | 2–43, 45–48, 50–55, 57 (9), 62 (3) … | ≥ 62 | exact search through n = 62, 63 balanced, beyond that open |

"Proved" means: every failure is an exhaustive search, and every n in the window
(a(k), a(k) + 2^(k+1)] has an explicit sign vector in `out/k*.txt`. That window suffices because of
the Prouhet–Thue–Morse identity: with Thue–Morse signs, any 2^(k+1) consecutive k-th powers sum to 0,
so if n is balanced then so is n + 2^(k+1).

So the answer to the question is yes for k ≤ 7, with the thresholds above (this much is surely known
in some form; I did not find the sequence 0, 5, 11, 29, 27, 35, 38 in the OEIS by a direct search).

The sequence is not monotone: a(4) = 29 > a(5) = 27, and a(8) = 68 is far above a(9)'s
neighbourhood. That is the interesting part.

## 2. Two different reasons to fail

**Shortage.** There are 2ⁿ sign choices and the sums spread over a range of order n^(k+1). The
local-limit heuristic gives about 2^(n+1) / sqrt(2π n^(2k+1)/(2k+1)) representations of a central
value; this crosses 1 at n\*(k) = 12, 18, 24, 31, 38, 45, 53 for k = 3 … 9, and 110, 258 for k = 16, 32. For k = 3, 5, 6, 7
the last failure (11, 27, 35, 38) is within four steps of that.

**The lock.** For k = 4 and k = 8 failures continue long after there are plenty of sign choices.
They are arithmetic.

## 3. Theorem (the 2-adic lock)

Let k ≡ 0 (mod 4), k ≥ 8, and r = v₂(k). Put M = 2^(r+3).

* For odd i: i^k ≡ 1 (mod M) if i ≡ ±1 (mod 8), and i^k ≡ 1 + M/2 (mod M) if i ≡ ±3 (mod 8).
  (Lifting the exponent: v₂(i^k − 1) = v₂(i² − 1) + r − 1, and v₂(i² − 1) = 3 exactly when i ≡ ±3 mod 8.)
* For even i: i^k ≡ 0 (mod M), because k ≥ r + 3.

Hence for any signs, with m the number of odd i ≤ n, J the number of odd i carrying a minus sign and
u the number of i ≤ n with i ≡ ±3 (mod 8),

  S ≡ m − 2J + (M/2)·u (mod M).

If n = 8q + 3 or 8q + 4 then m = 4q + 2, u = 2q + 1 is odd and the target is S = 0, so
J ≡ 2q + 1 + M/4 (mod M/2). Since 0 ≤ J ≤ 4q + 2 this needs 2q + 1 ≥ M/4, i.e. q ≥ 2^r.

> **Theorem.** If 4 | k, k ≥ 8, r = v₂(k), n ≡ 3 or 4 (mod 8) and n < 2^(r+3), then 1ᵏ, …, nᵏ cannot
> be balanced; in fact m(k, n) ≥ 2^(r+2) − ⌈n/2⌉.
>
> **Corollary.** a(2^r) ≥ 2^(r+3) − 4 for r ≥ 3: a(8) ≥ 60, a(16) ≥ 124, a(32) ≥ 252.

Checks: `cong.py` (reachable residues modulo 2¹², 3⁶, 5⁴, …) lists exactly these n for
k = 8, 16, 32 and for k = 12, 20, 24, 28, 36, 40 (where the bound 2^(r+3) is small); the exact values
m(8, 59) = 14 ≥ 2 and m(8, 60) = 10 ≥ 2 respect the bound. For k = 4 the same idea works modulo 32
with one change (2⁴j⁴ ≡ 16 for odd j), and gives exactly n = 18, 21, 26, 29.

All other residues of n mod 8 are free modulo M, and odd primes only lock small n (for instance k = 9
modulo 27 up to n = 40, below the shortage threshold).

## 4. The lock outlives its modulus (k = 8)

For n = 8q + 3 or 8q + 4 with q ≥ 2^r the congruence no longer forbids a balance, but it dictates its
shape: the number of odd weights on the minority pan must be J ≡ 2(q − 2^r) + 1 (mod 2^(r+1)).
For k = 8:

| n | odd weights | forced split of the odd weights | result |
|---|---|---|---|
| 67, 68 | 34 | 33 against 1 | impossible, m = 6 (`lock.cpp`, exhaustive over the 34 choices × all even signs, and over J ≤ 4 to certify the 6) |
| 75, 76 | 38 | 35 against 3 | possible (`balance75.json`: 13, 35, 73 apart; each pan 4426102656785155) |
| 83, 84 | 42 | 37 against 5 | possible |

So a(8) ≥ 68, twenty-three steps past the shortage threshold. (k = 9 shows a milder cousin: failures at 57 and 62 with minima 9 and 3, powers of 3; i⁹ is 0 or ±1 modulo 27. Not analysed.) Certificates exist for every n from 69 to 230,
and for every n ≤ 580 outside the two locked classes; the locked classes n ≡ 3, 4 (mod 8) between 231 and 580
were still being certified when the run ended (see the note at the end of this file). a(8) = 68 is proved once those are in. `table.py` prints what is missing.

## 5. Conjectures

1. **a(8) = 68** (only the certificates of §4 are missing).
2. **For k = 16 the lock wins by a wide margin.** The theorem gives a(16) ≥ 124 while n\*(16) ≈ 110.
   Beyond 124 the forced splits are 65 against 1 (n = 131, 132), 67 against 3 (139, 140), 5 (147, 148),
   7 (155, 156), 9 (163, 164) …; counting sign choices with the same local-limit heuristic that
   predicted k = 8 (slightly pessimistically: it gave 0.03 expected solutions at n = 75, where one exists),
   the first of these with a real chance is the 7- or 9-split. **Conjecture: 148 ≤ a(16) ≤ 164.**
3. **Powers of two are the only exponents where the lock decides a(k)**, and only up to k = 32:
   2^(r+3) = 8k grows linearly while n\*(k) grows like k·log₂k, and they cross near k = 32
   (lock bound 252, n\*(32) ≈ 258). For every other k, a(k) = n\*(k) + O(log k).
4. For k not a power of two, the answer to MO 296667 has no surprises: a(k) is finite for every k
   (this is what the question asks, and Prouhet's identity plus one window of successes proves it for
   each k separately; a uniform proof is the open part).

## Files

* `ss.cpp` — exact minimum and certificates; `ss k n1 n2 [n0 [M]]`. With n0 the top terms are signed
  greedily and only the lowest n0 are searched (a certificate when it succeeds, never a proof of failure).
* `lock.cpp` — exact search under the lock for 8 | k; `lock k n W` exhaustive, `lock k n W R` random.
* `cong.py` — residues reachable modulo prime powers. `small.py` — bitset cross-check.
* `dist.py` — exact distributions of the signed sums (used by the first picture).
* `solve75.py` — recovers the full sign vector of the n = 75 balance.
* `out/` — every line is `k n parity min mode signs`. `table.json` — the consolidated failures.
