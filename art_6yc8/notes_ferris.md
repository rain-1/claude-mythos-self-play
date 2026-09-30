# Ferris wheel numbers (MO 515611) — notes, 2026-09-30

**Question.** n > 1 is a *Ferris wheel number* if its k = τ(n) divisors can be hung at the k-th roots of unity with
centre of mass at the hub: Σ_j d_{π(j)} ζ^j = 0 for some permutation π. Do any exist?

**Equivalent picture.** Σ c_j ζ^j = 0 says the *equiangular* k-gon whose sides, in order, are c_0, c_1, …
(each side turning by 2π/k) closes up. So: *is there an equiangular polygon whose side lengths are exactly the
divisors of n?*

## Tools
* **de Bruijn / Rédei–Schoenberg.** An integer vector c on ℤ_k has Σ c_j ζ^j = 0 iff c = Σ_{p | k prime} f_p with
  f_p periodic of period k/p (real-valued is enough for what follows).
* Over ℚ the condition is φ(k) linear equations: reduce ζ^j modulo the cyclotomic polynomial Φ_k.
  Equivalently the Ramanujan-sum "trace" equations Σ_j c_j R(j − r) = 0 for every r, R(m) = μ(k/g)/φ(k/g),
  g = gcd(m, k) (Tao's answer uses the one centred on n).

## Lemma (proved here): if τ(n) has at most two distinct prime factors, n is not a Ferris wheel number.
*Proof.* If k = p^a, c = f_p is periodic with period k/p, so two positions carry equal values — impossible for
distinct divisors (k ≥ 2).
If k = p^a q^b with p ≠ q, write c = f + g, f of period s = k/p, g of period t = k/q, and rotate so c(0) = n.
Then
  c(0) = f(0) + g(0),  c(s) = f(0) + g(s),  c(t) = f(t) + g(0),  c(s+t) = f(t) + g(s),
so **n + c(s+t) = c(s) + c(t)**. The positions 0, s, t, s+t are distinct mod k (s + t ≡ 0 would need pq | p + q).
But c(s), c(t) are two *distinct proper* divisors of n, so c(s) + c(t) ≤ n/2 + n/3 < n < n + c(s+t). ∎

So the smallest open case is τ(n) = 30 (n = 720 is the smallest such n), and in general τ(n) must be divisible by
three distinct primes. With three primes the same argument gives only the 2×2×2 "cube" identity
n + c(s₁+s₂) + c(s₁+s₃) + c(s₂+s₃) = c(s₁) + c(s₂) + c(s₃) + c(s₁+s₂+s₃), which has room — that is where the problem lives.

## Exact search (`ferris.py`, `survey.py`)
* Filter 1 (Tao's trace, centred on n, by rearrangement): kills ≈ 92 % of the candidates with ω(τ(n)) ≥ 3.
  Centring the trace at every other r (rearrangement bound each) killed nothing extra up to 3·10⁵ (`filt.py`).
* Filter 2 (exact): CP-SAT model — position values c_j with domain = the divisors, AllDifferent, n pinned at 0, and the
  φ(k) integer equations from Φ_k. INFEASIBLE is a proof. Validated on planted solutions (k = 6 and k = 30 sets built
  as f₂ + f₃ + f₅ are found). Proves infeasibility for 720 720 (k = 240) in 45 s.
* **Result:** all 16 001 candidates n ≤ 1 945 152 with ω(τ(n)) ≥ 3 are proved not Ferris, except five undecided
  (900 s each): 907 200, 1 270 080, 1 425 600, 1 684 800 (τ = 210) and 1 940 400 (τ = 270); 907 200 also survived 90 min
  with 2 workers. Also proved: 720 720 (τ = 240) and 55 440 (τ = 120). Beyond: 2 041 200, 9 937 200, 9 979 200 undecided.

## Near misses (`anneal.c`)
Best hangings found by annealing miss the hub by |Σ c_j ζ^j| ≈ 0.0006 (n = 720, relative 8·10⁻⁷), 0.0022 (n = 5040),
0.0021 (n = 55 440). The miss does not grow with n: the number of hangings (k−1)! swamps the area they spread over,
so arbitrarily good near-misses exist and the obstruction is purely arithmetic.

## Conjecture
**There are no Ferris wheel numbers.** A route: for three primes, the de Bruijn pieces f_p restricted to one coset
of the order-pqr subgroup form a p×q×r array with vanishing third mixed difference; the largest divisor n has to be
paid for by the four "odd" corners of a cube, whose values are at most n/2 + n/3 + n/5 + n/7-ish … but the other
three "even" corners also enter with a plus sign, so a size argument alone will not do; one needs the multiplicative
structure (every divisor d of n comes with n/d).
