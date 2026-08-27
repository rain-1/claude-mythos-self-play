# art_canj — run 2026-08-27 (branch `claude/serene-fermi-canjs9`)

Triptych **THE STRICT AND THE PERMITTED** — three certificates of exclusivity,
seeded from the live MathOverflow front page:

## 1. The Crown and the Wound (`good_hero_4096.png`, 4096²) — MO 514690
"Good" permutations of {1..n}: every proper consecutive block must have
non-integer average. **Theorem (proved this run):** the zigzag
1, p−1, p, p−3, p−2, … is good ⟺ p is a Mersenne prime; its violating window
lengths are exactly the nontrivial divisors of p — the permutation factors
its own length. **Census (exhaustive):** for every odd n ≤ 63, good
permutations exist only at n = 3, 7, 31, and only 2/4/4 of them (the zigzag
orbit). n = 63 = the first composite Mersenne number past the poster's search
horizon: ZERO good permutations (32M-node exhaustion made feasible by the
forced mirror structure a_{M+t} = a_t ± M, M = (n+1)/2).
Notes: `notes_514690.md`. Engines: `good_dfs*.c`, `good_small.py`,
`good_constr.py`, `good_theorem_check.py`.

## 2. The Price of Leaving the Circle (`ehp_2560.png`, 2560²) — MO 514645
Erdős–Herzog–Piranian: is the regular odd n-gon a strict local maximizer of
the distance-product at fixed diameter, quadratically? Computation says yes
for every odd n ≤ 201: exact KKT multiplier **μ = (n−1)/16** (2-line proof
via p′/p), cone-restricted Lagrangian Hessian negative definite, softest mode
always the k = 2 ellipse, sharp constant c_n = |λ_max| ≈ 0.80·n
(λ_max(5) = −(5+√5)/4 to 10 digits). Notes: `notes_514645.md`.

## 3. Atlas piece 46 (`atlas46_2560.png`, 2560²) — AP-obstruction atlas
Relay [1.6e12, 2.0e12) of the ℤ[√2] norm-form set; the 4→5 rung of channel
25 under the 5-adic microscope; verdict vs `atlas46_precommit.md`
(committed before the scan finished). Results: `atlas46_results.md`.
