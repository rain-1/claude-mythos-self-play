# Sums of two numbers with the same totient (MO 515573) — notes, 2026-09-30

R(N) = #{a < b : a + b = N, φ(a) = φ(b)} (OEIS A362832). Is R(N) > 0 for all large N?

## Exact census (`totsum.c`, bucket numbers by φ, pairs inside each bucket in increasing order)
* **Up to 10⁸ there are exactly 435 N with R(N) = 0**; the largest is **413 759**, the next 245 771, 173 191, 165 746 …
  (full list: run `./totsum 100000000 out.bin`, 2 minutes).
* min R(N) over [10⁶, 10⁷) is 3, over [10⁷, 10⁸) is 8. Median R roughly doubles per decade (2, 4, 8, 17, 35, 71 on
  the decades from 10² to 10⁸), i.e. R(N) ≈ N^{0.3}.
* 188 of the 435 exceptions are prime, including the last two.

## Why primes are the hard case
Infinite families come from φ(ua) = φ(va) for a in a residue class: (1,2) a odd; (2,3) a even, 3 ∤ a;
(3,4) gcd(a,6) = 1; (4,5) a even, 5 ∤ a; (7,9) gcd(a,21) = 1; … They give N = (u+v)·a — always composite (a ≥ 2).
So a prime N is only ever reached by *sporadic* pairs, and "every large prime is a + b with φ(a) = φ(b)" is a
Goldbach-type statement. In the picture (x = (b−a)/(a+b), y = log N) the families are vertical threads at
x = (v−u)/(v+u); the strongest found by peak-matching are 1:2, 2:3, 3:4, 4:5, 7:9.
Median R in [10⁷, 10⁷+2·10⁵]: primes 28, composites 45.

## Conjecture
**R(N) ≥ 1 for every N > 413 759**, and in fact R(N) → ∞ (min over [10^e, 10^{e+1}) grows: 0, 0, 0, 0, 3, 8).
A heuristic: φ-fibres near x have size ~ x^{c} on average, so the expected number of sporadic pairs summing to N
grows like a power of N; a proof would need the φ-values of a and N − a to "collide", which is at least as hard as
Graham–Holt–Pomerance-type results for φ(n) = φ(n + k), here with k = N − 2a varying.
