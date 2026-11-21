# The borrowed camel — what was computed (2026-11-21)

Seeds: MathOverflow 271608 ("17 camels trick"), 392723 (Weyl's cyclic identity for random walks in
the plane); the parking-function answer under 271608 (Pollak's circle).

## 1. Camel wills (`wills.py`, `camelnum.py`, `even.py`)

A **will** for k sons is a herd n and unit shares 1/a₁ > … > 1/a_k with every aᵢ dividing n+1 and
Σ 1/aᵢ = n/(n+1). Lend one camel, each son takes (n+1)/aᵢ whole camels, one camel is left over.
Equivalently N = n+1 and **N − 1 is a sum of k distinct proper divisors of N**.

| sons k | wills | distinct herds | smallest herd | largest herd |
|---|---|---|---|---|
| 1 | 1 | 1 | 1 | 1 |
| 2 | 2 | 2 | 3 | 5 |
| 3 | 7 | 6 | 7 | 41 |
| 4 | 52 | 32 | 15 | 1805 |
| 5 | 1043 | 453 | 23 | 3263441 |
| 6 | 60613 | 20173 | 35 | 10650056950805 |

* The seven three-son wills: 7 = 4+2+1, 11 = 6+4+1, 11 = 6+3+2, 17 = 9+6+2, 19 = 10+5+4,
  23 = 12+8+3, 41 = 21+14+6 (exhaustive search over Egyptian fractions; the classical list).
* The largest herd is Sylvester's sequence minus two (42−1, 1806−1, …), as Curtiss's theorem on
  unit fractions predicts. The counts 1, 2, 7, 52, 1043, 60613 returned nothing from an OEIS search
  on this date.
* Herds that work for *some* number of sons ("camel numbers") are OEIS A085493. Counted here to 10⁶:
  110,356 of them (4, 30, 207, 1595, 13045, 110356 at powers of ten); count·ln n / n drifts
  1.43 → 1.52, so they thin out like practical numbers do (every practical N gives one).
* Almost all are odd. The first **even** herd is **944** (N = 945, the smallest odd abundant number);
  there are 1,996 even ones below 10⁶. An even herd needs N odd with σ(N) ≥ 2N − 1.

## 2. Weyl's identity (`weyl.py`, `partition.py`)

Legs a₀…a_n in independent uniform directions, S their sum, E_j = { |S − z_j| < a_j }.
Weyl (1938): Σ P(E_j) = 1. Geometrically E_j says: *the circle the end of the journey draws when
leg j alone swings full circle encloses the start.* So the expected number of enclosing circles is 1.

* Checked for legs (4, 3, 2.4, 1.7, 1.1): Bessel quadrature gives
  0.52322 + 0.22235 + 0.15633 + 0.06923 + 0.02879 = 0.99993; 2·10⁷ random journeys give 0.99989.
  The count N of enclosing circles there is 0, 1, 2, 3, 4 with probability .325, .392, .243, .039, .001.
* **Three legs.** If the lengths make a triangle, P(E_j) = (angle opposite side a_j)/π — so the
  identity for three legs *is* the angle sum of a triangle. (|a₁ + a₂e^{iφ}| < a₀ ⇔ |φ| > π − A₀.)
  Check: legs 5, 4, 3 give .4997, .2949, .2051 against 1/2, .2952, .2048. If they make no
  triangle the longest leg gets probability 1.
  Here the events *can* be made disjoint: project the triangle on a line of random direction;
  exactly one vertex lands in the middle, and it is the vertex opposite a_j with probability A_j/π.
* **Four equal legs: never exactly one.** N is 0 or 2, each with probability 1/2.
  Proof. For unit a, b, c the sum a+b+c is the orthocentre of the triangle abc, and
  |a+b+c|² = 1 − 8 cos A cos B cos C, so |a+b+c| < 1 iff the triangle is acute iff it contains the
  centre. Four points on a circle lie in a half-circle with probability 4/2³ = 1/2 (then no
  triangle contains the centre); otherwise the centre is inside the quadrilateral and each of its
  two triangulations has exactly one triangle containing it. ∎  (Simulation: .5000, 0, .5000.)
* Equal legs, general n: P(E_j) = 1/n (Rayleigh–Kluyver); N = #{j : 2 U_j·S > |S|²}. P(N = 0) is
  1/3, 1/2, .503, …, .644 (n=8), .790 (n=16): mostly nobody, rarely almost half of everybody.
* **Still open (the question's second half):** a reading of the identity as n+1 disjoint, exhaustive
  events for four or more legs. Three natural selection rules (largest projection on S; smallest
  |S − z_j| − a_j; smallest |S − z_j|/a_j) all fail badly — they over-reward the longest leg
  (.72 against .52). The existing answer on MO gives the winding-number proof; nothing here was posted.

## 3. Pollak's circle (`../stalls.py`)

17 cars (camels) with wishes in ℤ₁₈ park on a ring of 18; one stall stays empty; adding t to every
wish moves the empty stall by t. The script asserts that the 18 turnings of its wish list have 18
different empty stalls, so exactly one is a parking function for a row of 17: 18¹⁷/18 = 18¹⁶.
