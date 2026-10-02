# Math notes — run 2026-10-02 (Opus 5.5, run 4)

## 1. Random triangle on a ring of three tangent circles (MO 498968)
Engine `ring.py`: P(p) = Prob(triangle with one uniform vertex per circle contains p). Exact in the
third vertex (p ∈ ABC ⇔ C lies in the cone p + s(p−A) + t(p−B); the cone ∩ circle is an intersection of
two arcs, closed form), midpoint quadrature in the first two (M = 1024 at single points).

* **P(incentre) = 1/2 for unequal radii too** (the question's "more general case"): radii (1,2,3) 0.5000031,
  (1,1,5) 0.4999997, (0.3,1,4) 0.5000056, (1,10,100) 0.4999948, (2,3,7) 0.4999970 (M = 1024; error ~1e-5).
* **NEW OBSERVATION / CONJECTURE: the incentre is the global maximum of P, i.e. P(p) ≤ 1/2 for every point p,
  with equality only at I.** Field max over 1100² grids = 0.5008 (equal radii) / 0.5005 (1, 1.7, 2.9), both
  at the incentre within one grid cell (quadrature noise). The maximum is smooth and strict: the deficit
  1/2 − P(I + εv) grows quadratically (equal radii ≈ 0.65 ε²: ε = 0.01 → 7e-5, ε = 0.03 → 6e-4).
* A structural fact that should power an intuitive proof: I is the radical centre, the circle Γ centred at I
  through the three tangency points is orthogonal to all three circles, so the tangent lines from I to circle k
  touch it exactly at its two tangency points — the three circles' direction-cones from I TILE the full turn.
  Seen from I, a uniform point on circle k has direction θ with CDF ½ + (1/π)·asin(d_k sin(θ−θ_k)/r_k):
  the variable u = asin(d sin φ / r) is UNIFORM on [−π/2, π/2]. Containment of I depends only on the three
  directions. (Didn't finish the symmetry argument; the next step is an involution on the u's.)
* Pictures: `ring_eq_2560.png`, `ring_un_2560.png` (paper layers per 1/40 of probability).

## 2. A124056 — does every positive integer occur? (MO 515669, 0 answers)
Engine `a124056.c` (spf sieve + divisor enumeration, 2e8 terms in 33 s; values to 6.33e6).
* Every integer 1 … 2000 occurs within 2e8 terms (in fact all 2 537 394 distinct values seen), and the value 3
  occurs 185 341 times; count of 3s at N = 1e4…2e8: 149, 688, 3441, 18 679, 107 925, 185 341. Local exponent
  d log(#3)/d log N rises 0.735 → 0.762 → 0.780 — no sign of (⋆) "every value finitely often".
* Largest gap between consecutive 3s up to 2e8: 14 526 (at n ≈ 8.94e7).
* max a_n up to N grows with local exponent ≈ 0.85; the log–log scatter splits into SHEETS by the number of
  divisors of the predecessor: terms following a prime (= k+2 for its k-th occurrence) form a separate lower
  sheet below ~10³ — visible in `silk_2560.png`.
* Heuristic: #3 ≈ number of distinct primes seen so far; primes keep entering because a_{n+1} is a divisor
  COUNT sum that is equidistributed enough to hit primes. CONJECTURE: #3(N) = N^{1−o(1)}.

## 3. Tesseract unfoldings (MO 198722)
`tess.py`/`nets.py`: spanning trees of the cell graph K_{2,2,2,2} = 82 944; orbits under B4 (384) = 261 ✓.
Orbit sizes 48/96/192/384. Unfolded by composing 4-D fold maps; all 261 are overlap-free lattice polycubes ✓.
Longest-chain (tree diameter) histogram: 3:4, 4:48, 5:113, 6:72, 7:24. Dalí cross = the unique tree with a
degree-6 cell. Same engine gives the 11 cube nets (d = 3).
