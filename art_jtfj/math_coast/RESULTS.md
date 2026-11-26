# The straight coast — notes on MathOverflow 518177

Question (paraphrased). For a positive integer m and M = m·rad(m) put

    E(s) = M^(s−1) · Σ_{d|m} d^(−s),      D(s) = E(s) + E(1−s).

Numerically every zero of D lies on Re s = ½. (b) Is that a theorem? (a) If d^(−s) is replaced by a(d)·d^(−s),
which coefficients keep the zeros on the line? The asker's counterexample: the Epstein coefficients of x² + 5y²
on the divisors of 5040 give 13 zeros with ½ < Re s < 1 and 0 < Im s < 60.

Everything below was worked out in this run. Scripts: `check1.py`, `check2.py`, `check3.py`; logs beside them.
Nothing has been posted anywhere.

Notation: F(s) = E(s)/E(1−s). D(s) = 0 exactly when F(s) = −1. In the pictures h = log|F| is the height, the
set |F| = 1 is the shore, and a zero of D is a light.

## 1. Theorem (answers b, with room to spare)

**For every real M ≥ √m, all zeros of D lie on Re s = ½, and they are simple.**
M = m·rad(m) is far inside this range.

*Proof.* Write m = Π p^a and x = p^s. Then

    M^s · Σ_{d|m} d^(−s) = (M/m)^s · Π_p q_a(p^s),      q_a(x) = 1 + x + … + x^a,

so

    F(s) = (M²/m)^(s−½) · Π_p F_p(s),      F_p(s) = p^(−a(s−½)) · q_a(p^s) / q_a(p^(1−s)).

*Lemma (one root).* If |ρ| ≤ 1 < R and |x| > R, then
R²|x − ρ|² − |R² − ρ̄x|² = (|x|² − R²)(R² − |ρ|²) > 0. Dividing by |x|² and using |R² − ρ̄x| = |x|·|R²/x̄ − ρ|: With R = √p this says

    |x − ρ| / |p/x̄ − ρ|  >  |x| / √p        for |x| > √p.

The roots of q_a are roots of unity, so multiplying the lemma over the a roots gives
|q_a(x)| / |q_a(p/x̄)| > (|x|/√p)^a = p^(a(σ−½)) for σ > ½, and q_a has real coefficients, so |q_a(p/x̄)| = |q_a(p^(1−s))|.
Hence **|F_p(s)| > 1 for every prime and every Re s > ½**, and |F(s)| > (M²/m)^(σ−½) ≥ 1 when M ≥ √m.
By F(1−s̄) = 1/conj F(s), |F| < 1 on the left. So F = −1 only on the line. Simplicity: on the line
∂_t arg F = ∂_σ log|F| > 0 (the inequalities above are strict to first order), so arg F is strictly increasing. ∎

Checked numerically for m = 2, 6, 12, 30, 360, 1152, 5040, 9973 at 20,000 random points each (`check1.py`),
and by counting sign changes of the real function √M·D(½+it) against the total number of zeros
T·log M/π + O(1): m = 5040, M = m·rad m, 0 < t < 32: 141 crossings, 141.30 expected.

Consequences that fall out of the proof:

* **The count is exact:** N(T) = T·log M/π + O(1), one zero for each half-turn of arg E(½+it).
* **Interlacing:** the zeros of E(s) − E(1−s) are also all on the line and interlace with those of D.
* **Every high water is above mean level:** t ↦ √M·D(½+it) is a real trigonometric sum with only real zeros,
  so each local maximum is positive and each local minimum negative (0 wrong-sign extrema out of 141 in the
  check; the Epstein version has 3).
* **At M = √m the lights are in bijection with the zeros of Σ d^(−s).** The curve arg F = π leaving a zero
  ρ = it of σ₋ₛ(m) (a "pit" on Re s = 0) climbs monotonically, crosses the shore at a zero of D, and by the
  mirror symmetry ends at the pole 1 − ρ̄ (the "mountain" on Re s = 1). Counts for 0 < t < 300:
  m = 12: 118 pits, 118 lights; m = 5040: 407, 407; m = 720720: 643, 644. For M > √m the extra
  log(M²/m)/(2π) lights per unit height sit on threads that come in from infinity.

## 2. The threshold √m is sharp

For M < √m the far right is sea again (|F| → 0 as σ → +∞), so the land is only a strip around Re s = 1 and
has a second shore. Zeros appear there.

*Proposition.* For m ≥ 3 and M slightly below √m, D has zeros near
s = σ* + i(2k+1)π / log(m/M²), σ* = log(m/M) / log(m/M²) > ½.
(Rouché: for large σ, D·M^s·m^(1−s) = (M²/m)^s·(m/M)(1+ε₁) + (1+ε₂) with ε = O(2^(−σ)), and σ* → ∞ as M ↑ √m.)

Numerics (`check2.log`, 0 < t < 300, m = 6, 12, 30, 360, 5040) say more: the line keeps T·log M/π zeros and
exactly the rest, T·log(m/M²)/(2π) pairs, leave it.

| m = 5040 | M/√m = 8 | 2 | 1 | 0.99 | 0.95 | 0.8 | 0.5 |
|---|---|---|---|---|---|---|---|
| zeros on the line | 606 | 473 | 407 | 406 | 402 | 386 | 341 |
| pairs off the line (total − on-line)/2 | 0 | 0 | 0 | 1.0 | 5.0 | 21.2 | 66.1 |
| predicted T·log(m/M²)/(2π) | – | – | 0 | 0.96 | 4.9 | 21.3 | 66.2 |

**Conjecture A.** For 1 < M < √m the off-line zeros of D number T·log(m/M²)/π + O(1) up to height T, and the
on-line ones T·log M/π + O(1). (I can prove "infinitely many off the line" only near the threshold. The obstacle
to a counting proof: on the line the phase need not be monotone, so on-line zeros are not bounded by its variation.)

## 3. General coefficients (question a)

Let A(s) = Σ a(d) d^(−s), real a, a(1) ≠ 0, and let m₊ be the largest d with a(d) ≠ 0.

* **Sufficient.** If A has no zero with Re s > ½ and M ≥ √m₊, all zeros of E + E(1−·) are on the line.
  (M^s·A(s) is then an exponential polynomial of Hermite–Biehler type about the line: Levin, *Distribution of
  zeros of entire functions*, ch. VII; the condition M ≥ √m₊ is the sign of the defect. I am citing this,
  not re-proving it; for products over primes the lemma above does it directly.) For multiplicative a
  this is a condition prime by prime: the polynomial Σ_j a(p^j) u^j has no root with |u| < p^(−½).
  Divisor sums satisfy it with a full half-plane to spare (roots on |u| = 1), which is why the result holds
  down to √m.
* **Nearly necessary for large M.** If A(ρ) = 0 with Re ρ > ½ then F = M^(2s−1)·A(s)/A(1−s) is tiny near ρ:
  there is a lake |F| < 1 around ρ of radius about M^(−(2 Re ρ − 1)), and arg F turns once round it, so
  F = −1 somewhere on its bank: a zero of D off the line within that distance of ρ — unless the lake reaches
  the line Re s = ½, in which case the −1 point may lie on the straight part of its bank.
* **Epstein, m = 5040, M = m·rad m, 0 < t < 60** (`check2.log`): A has 14 zeros right of the line; D has
  13 zeros right of the line (the asker's count), each next to one of them, at distances 5·10⁻⁶ … 3·10⁻²
  that track M^(−(2σ−1)); the fourteenth zero of A (0.533 + 38.388i) has a lake that touches the line and its
  light stayed on it. The on-line count is 238 = 264.9 − 26.9: the missing 27 are the 13 pairs.
* **What a lake looks like when it touches the line:** the line is always part of the shore (symmetry), so the
  lake is bounded by an arc and a stretch of the line itself; its mirror image is an island on the other side
  of the same stretch. Along that stretch the water is on the landward side. This is the picture
  *Where the Shore Turns Inside Out*.
* Changing M moves the near-line zeros on and off the line (`check3.log`): between M = √5040 and m·rad m the
  number of off-line pairs with 0 < t < 60 is 9, 10, 13, 11, 14, 11, 11, 14, 13, 13 — never more than 14.

**Conjecture B (a light for every lake, at most).** For M ≥ √m₊ and every T, the number of zeros of
E + E(1−·) with Re s > ½, 0 < t < T is at most the number of zeros of A there, plus O(1).
Sketch: each off-line zero lies on the bank of a lake; arg F is monotone along a bank and turns once for each
zero of A inside; so a lake with k zeros carries exactly k lights, some of which may sit on the line.
Missing: a proof that no lake is an unbounded channel.

## 4. What I did not settle

* Conjecture A away from the threshold; Conjecture B's channel gap.
* A converse to §3 "sufficient": the asker asks whether multiplicativity is necessary. It is not (any A with
  zeros left of the line works), and it is not sufficient either (a multiplicative a with a local root inside
  |u| < p^(−½) gives A a zero right of the line, hence, by the lake argument, off-line zeros for large M). The right condition is where the zeros of A are, not whether A factors.
