# MO 516229 — two quadratic families, which integers are missed

f(n,m) = n²+2n+(2n+1)m,  g(n,m) = n²+3n+(2n+1)m,  n ≥ 1, m ≥ 0.

Put d = 2n+1 (odd, ≥ 3). Then 4(n²+2n) = d²+2d−3 and 4(n²+3n) = d²+4d−5, so

* N is hit by f  ⇔  some odd d ≥ 3 divides 4N+3 with d(d+2) ≤ 4N+3,
* N is hit by g  ⇔  some odd d ≥ 3 divides 4N+5 with d(d+4) ≤ 4N+5.

Writing M = d·e (e odd): for f, d(d+2) ≤ M ⇔ e ≥ d+2 ⇔ e > d (both odd). For g we need
e ≥ d+4, but e = d+2 is impossible there: d(d+2) = (d+1)²−1 ≡ 3 (mod 4) while 4N+5 ≡ 1 (mod 4).
So in both cases a usable split exists iff M is composite and not the square of a prime.

**Theorem (checked to N = 2·10⁶, 0 mismatches).** N is missed by both families
⇔ 4N+3 and 4N+5 are each a prime or the square of a prime.

So the missed set is {twin primes (q, q+2) with q ≡ 3 (mod 4)} ∪ {primes p²−2, p prime}
(p²+2 is ≡ 0 mod 3 unless p = 3, giving only N = 1). Up to 2·10⁶: 24,479 missed N,
of which 24,372 are twin-prime pairs and 107 are p²−2 cases (N = 1, 5, 11, 41, 89, 209, …).

Consequence: "finitely many missed" would imply only finitely many twin primes ≡ 3 mod 4
AND only finitely many primes of the form p²−2 — both contradict standard conjectures
(Hardy–Littlewood, Bunyakovsky). Expected answer: infinitely many, but proving it is as hard
as the twin prime conjecture (any one of the two infinitude statements suffices).
Script: `check.py`.
