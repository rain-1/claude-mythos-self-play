# MO 516332: d(n²+m²) = 2·b(n,m)

**Notation.** N = n²+m², a = d(N). b = #{(x,y) ∈ Z², x,y ≥ 0 : n² − 4y(y+m) = x²}. c = A004613. r₂(N) = #{(u,v) ∈ Z² : u²+v² = N}.

**Theorem (the conjecture is true, and floor(m²/2) is the exact threshold).** Let m ∈ c and n > floor(m²/2). Then d(n²+m²) = 2b(n,m). For every m ∈ c with m > 1, the value n = floor(m²/2) = (m²−1)/2 fails: there b = (a+1)/2.

**More general theorem.** Take any m ≥ 1 and any n > m²/4 − 1 such that N is not a perfect square. Then a(n,m) = 2b(n,m) **iff gcd(n,m) ∈ c**. When n > floor(m²/2), N is never a square, so for such n the identity holds exactly when gcd(n,m) ∈ c. In particular, for m ∉ c it fails for infinitely many n: for example, all n divisible by a prime p ≡ 3 (mod 4) that divides m, or all even n when m is even.

## Proof
1. **Translate b.** Put z = 2y+m. The equation becomes x² + z² = N. So b counts the pairs (x,z) with x ≥ 0, z ≥ m, z ≡ m (mod 2) and x²+z² = N. Reducing mod 8 (z² ≡ m²) gives x ≡ n (mod 2).
2. **Remove the condition z ≥ m when n > m²/4 − 1.** Suppose a solution has 0 < z < m. Then x² = n² + (m² − z²) > n², and x ≡ n (mod 2), so x ≥ n+2. That gives m² > m² − z² = x² − n² ≥ 4n+4, which is impossible. Solutions with z ≤ 0 are excluded anyway because z ≥ m > 0. So b = #{x ≥ 0, z > 0, z ≡ m (mod 2), x²+z² = N}.
3. **Count with r₂.** Write N = 2^e·P·Q, where every prime of P is ≡ 1 (mod 4) and every prime of Q is ≡ 3 (mod 4). Then r₂(N) = 4·d(P)·[Q is a square]. The quadrant {x ≥ 0, z > 0} holds exactly r₂/4 of the representations.
   * **n ≢ m (mod 2):** N is odd and exactly one of x, z is odd. The parity condition picks out half of the representations, and the sign symmetry x ↦ −x pairs them up except when x = 0, which happens iff N is a square. So b = (r₂(N)/4 + [N = □])/2.
   * **n, m both odd:** N ≡ 2 (mod 4), x and z are both odd, and the parity condition holds automatically. So b = r₂(N)/4.
   * **n, m both even:** x and z are both even, so b = r₂(N/4)/4.
4. **Compare with d(N) = (e+1)·d(P)·d(Q).** A prime p ≡ 3 (mod 4) divides n²+m² iff p | gcd(n,m). So Q = 1 iff gcd(n,m) has no prime ≡ 3 (mod 4).
   * If n, m are not both even, then e ≤ 1 and, for N not a square, 2b = (e+1)·d(P)·[Q = □]. This equals d(N) iff Q = 1, that is, iff gcd(n,m) ∈ c.
   * If both are even, then e ≥ 2 and 2b ≤ 2·d(P) < 3·d(P) ≤ d(N), so the identity fails. (Here gcd(n,m) is even, so it is not in c.)
5. **Squares.** If n²+m² = k², then (k−n)(k+n) = m² with k−n ≥ 1, so n ≤ (m²−1)/2. Hence N is not a square once n > floor(m²/2). Conversely, for odd m, n = (m²−1)/2 gives N = ((m²+1)/2)². This n is even, so we are in the first case of step 3 and get 2b = a+1. ∎

**Remarks.** Below the threshold, the failures for m ∈ c come from two sources: N being a square, or a solution with z < m (the latter only when n ≤ m²/4 − 1). The exact formula for b in step 3 holds for every m and every n > m²/4 − 1.

## Verification (scripts `verify.py`, `formula.py`; brute force over z, divisor counts from sympy)
* **m ∈ c, m ≤ 100, 1 ≤ n ≤ floor(m²/2) + 3000:** no failure above the threshold, and the largest failing n is exactly floor(m²/2) for every m ∈ c with 5 ≤ m ≤ 97. For m = 1 there is no failure with n ≥ 1.
* **All m ≤ 100, n in (floor(m²/2), floor(m²/2) + 300]** (and + 3000 for m ∈ c), 70,500 cases: "a = 2b ⇔ gcd(n,m) ∈ c" holds with 0 mismatches.
* **All m ≤ 60, ceil(m²/4) ≤ n ≤ floor(m²/2) + 1000**, 78,475 cases: the exact formula for b in step 3 and the iff criterion (including the square exception) hold with 0 mismatches.
