# Mathematics of this run (pastel #38, FROM THE EVIDENT TO THE HIDDEN)

Seeds (live front pages, 2026-10-15): MathOverflow **516050** (Cayley's formula from the exponential formula),
**516046** (ℤ×ℤ-scrambling); Philosophy.SE **142598** (Epicurus: how can the Canon justify atoms and void, which no one
perceives?) and **142593** (Wright's *Orrery* read as Plato's cave).

## 1. MO 516050 — n^{n−2} out of log(1 + Σ xⁿ/n! (1+y)^{C(n,2)})  (`math_cayley/`)
The coefficient extraction is an alternating sum over set partitions,
A(n) = Σ_π (−1)^{|π|−1}(|π|−1)! · binom(Σ_{B∈π} C(|B|,2), n−1), checked exactly = n^{n−2} for n ≤ 14
(and the unicyclic coefficient = A057500 for n ≤ 14). No involution evaluates it directly; instead:

* **G = Σ xⁿ/n! (1+y)^{C(n,2)} solves a heat equation**: (1+y)G_y = (x²/2)G_xx (because C(n,2)xⁿ = (x²/2)(xⁿ)'').
* So C = log G solves (1+y)C_y = (x²/2)(C_xx + C_x²). Comparing coefficients gives a recurrence that, from c_{n,0} = [n=1]
  alone, forces c_{n,e} = 0 for e < n−1 and, at e = n−2, the tree recurrence (n−1)t_n = ½ Σ C(n,k) k t_k (n−k) t_{n−k}.
* That recurrence is uT' − T = (u²/2)T'²; with R = uT' it becomes R' = R/(u(1−R)), i.e. R = u e^R, so r_n = n^{n−1} and
  t_n = n^{n−2} by Lagrange. (Higher powers of y give Wright's excess hierarchy; Rényi's unicyclic formula checks out.)
* **By-product (a vanishing identity, which is just "connected ⇒ ≥ n−1 edges" seen from the right-hand side):**
  for every m < n−1, Σ_π (−1)^{|π|−1}(|π|−1)! · binom(Σ_B C(|B|,2), m) = 0. The PDE proves it without graphs.

## 2. MO 516046 — ℤ×ℤ-scrambling  (`math_scramble/`)
**Yes**, and explicitly: **f(x,y) = x + g(y)** with the period-5 map (y = 5t + r)

| r | g(y) | y + g(y) |
|---|---|---|
| 0 | 4t | 9t |
| 1 | 4t+2 | 9t+3 |
| 2 | −8t+5 | −3t+7 |
| 3 | 4t+3 | 9t+6 |
| 4 | −8t+1 | −3t+5 |

Rows are translations; columns are bijections because the images of g are the exact cover {0,2,3 mod 4} ∪ {1,5 mod 8};
diagonals x−y=k are bijections because the images of y+g(y) are the exact cover {0,3,6 mod 9} ∪ {1,2 mod 3}.
(I re-checked injectivity and coverage numerically on |y| ≤ 20000.) No such piecewise-affine g exists with period ≤ 4 (search).
A back-and-forth argument gives existence for any finite set of directions (anti-diagonals too).

Observations (spiral-greedy fills, 'smallest unused |v|'):
* rows+cols+diagonals greedy is **not** a scrambling: every 0 sits on the anti-diagonal x+y=0 (|y| ≤ 1500), so odd diagonals never get a 0.
* rows+cols greedy: max|f| on ring r is exactly 2^{⌊log₂ r⌋+1}; on the same-sign quadrants f is a nim-like function of (x−1) xor (y−1). **CONJ**: this holds everywhere.
* OPEN: a *strong* complete mapping of ℤ (g, g+id, g−id all bijections) that is piecewise affine — none with period ≤ 4.

## 3. The Perrin plate's physics (`perrin/`)
2-D WCA gas, 20,000 atoms (area fraction 0.4) + 12 grains, velocity Verlet, T = 1600. Grain mean-square displacement gives a
time-dependent D(t) = MSD/4t: 0.11 (t=50), 0.18 (200), 0.24 (500), 0.29 (1000) — still rising, roughly linearly in log t.
That is the Alder–Wainwright long-time tail: in two dimensions the velocity autocorrelation decays like 1/t and the
diffusion constant does not exist (D(t) ~ log t). **HYPOTHESIS (testable with this code)**: D(t) ≈ a + b log t with b
independent of the grain radius and mass, set by the gas alone (its density and kinematic viscosity, as the mode-coupling
theory of the 1/t tail suggests). Decide it by fitting b per grain size over a longer run; here the 12 grains are too few.
Epicurus would have liked it: the invisible gas leaves a signature that never settles.

## 4. The orrery's sky
Heliocentric longitudes for 2026-10-15 00:00 UT from J2000 mean elements + Kepler's equation (≈ 1° accuracy):
Mercury −51°, Venus 16°, Earth 21°, Mars 92°, Jupiter 132°, Saturn 11°. Venus and Earth are within 6° of each other —
an inferior conjunction of Venus is close (Venus is between Earth and Sun around now), which is why their glass balls
nearly touch in the picture.
