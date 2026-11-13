# MO 516862 — "Recurrence that produces primes in most cases"

    T(n,k) = T(n,k−1) + gcd( T(n,k−1), (n+1)(k−1)+1 ),   T(n,0) = 1,
    a(n)   = (n+1)·T(n,n−1) − n².

The poster asks why composite a(n) are so rare (n = 4, 12, 172, 2420, 4114, 13176, 19490, 22703, …)
and whether the recurrence can be rewritten to explain it. Below: a rewriting, a lemma that proves
primality of a(n) for 99.9 % of n, and data to n = 5·10⁶. Nothing here has been posted.

Write m = n+1 and fix n.

## 1. The rewriting

Put **c_k = T_k − k** (the *offset*; c_0 = 1, non-decreasing) and **N_k = m·c_k − 1**.

Since m·k + 1 = m·(T_k − c_k) + 1 ≡ −(m·c_k − 1) (mod T_k),

    gcd(T_k, m k + 1) = gcd(T_k, N_k).                                   (1)

And the output is the last N:

    a(n) = m(n−1+c_{n−1}) − (m−1)² = m·c_{n−1} − 1 = N_{n−1}.            (2)

So the recurrence is this procedure. Keep a candidate N = m·c − 1 (initially c = 1, N = n) and a
counter T that walks upward through the integers one at a time (initially T = 1).

* As long as gcd(T, N) = 1, nothing happens: T ← T+1, c and N unchanged.
* The first time T shares a factor g > 1 with N ("a firing"), the candidate is discarded:
  c ← c + g − 1, N ← N + m(g−1), and T ← T + g.
* Stop after n−1 steps and output the current candidate N.

It is **trial division along the progression m·c − 1**: T finds a factor of the candidate (almost
always its smallest prime factor, because the multiples of a small prime come round soonest), the
candidate is replaced, and the search goes on until a candidate survives to the end.

## 2. The window lemma

Let ℓ be the index of the last firing (ℓ = −1 if there is none) and W = n − 2 − ℓ the number of
quiet steps after it. During those steps c is constant, so T runs through the **W consecutive
integers** ℓ+1+c, …, n−2+c, and by (1) and (2) each of them is coprime to a(n).

> **Lemma.** Every prime factor of a(n) is greater than W. In particular, if (W+1)² > a(n) then
> a(n) is prime.

*Proof.* Any W consecutive integers contain a multiple of every p ≤ W. ∎

Two immediate cases:

* **n prime ⇒ a(n) = n.** Nothing fires (T ≤ n−1 < n = N), c stays 1.
* **n composite with least prime factor p**: the first firing is at T = p, with g = p, so c jumps
  to p and the candidate becomes (n+1)p − 1.

Example n = 100: firings at k = 1, 4, 9, 14, 16 (g = 2, 3, 13, 5, 3), c ends at 22,
a(100) = 101·22 − 1 = 2221. After k = 16 there are W = 82 quiet steps, T runs through 39…120,
and 83² > 2221, so 2221 is prime — proved by the recurrence itself.

## 3. How often the lemma decides (computed, `fast.py`, `stats2.py`)

| n in | n | a(n) composite | not decided by the lemma | fraction |
|---|---|---|---|---|
| [10², 10³) | 900 | 1 | 38 | 4.2 % |
| [10³, 10⁴) | 9 000 | 2 | 93 | 1.03 % |
| [10⁴, 10⁵) | 90 000 | 5 | 314 | 0.35 % |
| [10⁵, 10⁶) | 900 000 | 11 | 949 | 0.105 % |
| [10⁶, 2·10⁶) | 1 000 000 | 4 | 619 | 0.062 % |
| [2·10⁶, 5·10⁶) | 3 000 000 | 14 | 1 341 | 0.045 % |

So for n up to 5·10⁶ the lemma alone proves a(n) prime for all but 3 365 values of n; of those, 39
are composite. The undecided n are exactly the ones whose offset ran away: in every undecided case
with 10⁵ < n ≤ 5·10⁶, c > 0.40·n (median 0.74·n) and a single firing with g ≈ c/2 did most of it. In the
census picture they sit above a sharp line.

Why a threshold near 0.4·n: the time used up to the last firing is at least about c (T has to walk
past c), so W ≲ n − c, and the lemma fails only if (n−c)² ≲ n·c, i.e. c/n ≳ (3−√5)/2 = 0.382.

**Composite a(n), n ≤ 5·10⁶** (the first eight are the poster's):

| n | a(n) | factorisation |
|---|---|---|
| 4 | 9 | 3^2 |
| 12 | 493 | 17 · 29 |
| 172 | 56743 | 179 · 317 |
| 2420 | 7989299 | 37 · 215927 |
| 4114 | 45273229 | 947 · 47807 |
| 13176 | 335776313 | 10739 · 31267 |
| 19490 | 589290893 | 20963 · 28111 |
| 22703 | 621294959 | 17581 · 35339 |
| 65891 | 5234921723 | 30197 · 173359 |
| 74144 | 6380177249 | 26701 · 238949 |
| 109926 | 20307254417 | 82657 · 245681 |
| 115715 | 13760599571 | 82613 · 166567 |
| 130075 | 46687788451 | 128923 · 362137 |
| 146863 | 34092274639 | 45491 · 749429 |
| 205685 | 68589493361 | 197699 · 346939 |
| 221808 | 83866426517 | 87743 · 955819 |
| 227590 | 60740396443 | 172093 · 352951 |
| 327914 | 147474524609 | 34327 · 4296167 |
| 703638 | 587164229051 | 559277 · 1049863 |
| 725970 | 1602791514089 | 776233 · 2064833 |
| 787661 | 762397741349 | 198301 · 3844649 |
| 1157151 | 1959647326367 | 211291 · 9274637 |
| 1199815 | 1722063509767 | 244733 · 7036499 |
| 1267379 | 2628187451459 | 170389 · 15424631 |
| 1279402 | 1781363973019 | 782659 · 2276041 |
| 2246048 | 6039625760999 | 2182997 · 2766667 |
| 2342538 | 8273683770269 | 2286443 · 3618583 |
| 2739711 | 14743099857407 | 1428949 · 10317443 |
| 2936912 | 11656836776213 | 2507737 · 4648349 |
| 3434461 | 15763833699337 | 366433 · 43019689 |
| 3575801 | 25326794103857 | 4072427 · 6219091 |
| 3831359 | 20787231416639 | 3440243 · 6042373 |
| 4347879 | 14043187176839 | 2754889 · 5097551 |
| 4492369 | 42658777324729 | 3969071 · 10747799 |
| 4653227 | 46617159531947 | 4012369 · 11618363 |
| 4784263 | 28095336774007 | 1407293 · 19964099 |
| 4787851 | 33086398579627 | 4953931 · 6678817 |
| 4799818 | 31461133608349 | 3405979 · 9237031 |
| 4882569 | 41448493157609 | 4602347 · 9005947 |

(39 values of n up to 5·10⁶.)

All of them are products of two primes, except a(4) = 9 = 3².

## 4. What I believe but have not proved

* **Conjecture A.** The number of n ≤ x that the window lemma does not decide grows like x^θ with
  θ between 0.5 and 0.6.
  (Counts per decade 38, 93, 314, 949: ratios ≈ √10; then 619 on [10⁶,2·10⁶) and 1 341 on
  [2·10⁶,5·10⁶), where 1.39·Δ√x would give 575 and 1 143 — so the exponent may be a little above 1/2. I do not
  have a derivation; the naive "one unlucky large factor" heuristic predicts slower decay.)
* **Conjecture B.** a(n) is composite for infinitely many n, but for a set of density zero; the
  count up to x is a slowly shrinking share of the undecided ones (about 1–2 % so far: 39 of 3 365).
* **Conjecture C.** log c / log n has a limiting distribution on [0,1] as n → ∞ (through composite
  n). Measured: P(c > n^0.5) = 0.314, 0.306, 0.301 and P(c > n^0.7) = 0.098, 0.086, 0.082 on
  [10⁴,10⁵), [10⁵,10⁶), [10⁶,2·10⁶) — nearly stationary, drifting slowly down. In the census
  picture this is the statement that the gold cloud stops changing from left to right.

## 5. Files

* `rec.py` — the recurrence as stated (brute force), `trace.py n` prints the firings.
* `fast.py lo hi` — the rewriting of §1 with early-exit trial division; agrees with brute force for
  every n ≤ 6000 (`check_fast.py`); 2·10⁶ values of n in about three minutes on 4 cores.
  (The `.npz` outputs are not committed; they regenerate in minutes.)
* `stats2.py file.npz` — the table above.
