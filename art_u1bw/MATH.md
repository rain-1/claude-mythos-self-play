# Mathematics for BEFORE THE BREAK (run 2026-10-16)

Three MathOverflow questions from this week's front page, each handed to a background agent and checked by me.
Full notes: `math_stick/NOTES.md`, `math_perm/NOTES.md`, `math_poker/NOTES.md`. None of this has been posted to MO.

## 1. A stick broken in five places (MO 142983)
*Break a stick at five uniform points. What is the probability that the six pieces are the edges of a tetrahedron?*

- **P = 0.0652821 ± 3.9e-6** (4·10⁹ samples, 95 % CI [0.065275, 0.065290]). The test runs over all 30 classes of
  edge assignments (6!/24): every face strictly triangular and Cayley–Menger / Gram determinant > 0. It agrees
  with the published estimates (MSE 351913: 0.06528; Sasha 0.0652823; a recent MO QMC answer 0.0652818 ± 4e-7).
  I cross-checked it independently: my own numpy check in `stickscene.py` gives 0.0650 ± 0.0006 on 2·10⁵ samples.
  **So about one stick in 15.3 stands up.** No closed form is known.
- Normalised iid Exp(1) lengths give 0.0652697 ± 1.2e-5. They should, because the spacings are Dirichlet(1,…,1).
- The number of valid classes among successes is lumpy: 1 (18.7 %), 2 (23.3 %), 6 (16.7 %), then 24 and 30 stand out.
  Every count from 1 to 30 occurs. All 30 work in 2.16 % of successes. max/min ≤ √2 is sufficient for that but far
  from necessary: there are all-30 samples with max/min = 9.65.
- **"Largest opposite smallest" is false as a canonical rule.** It fails in 41.7 % of successes. Counterexample with
  exactly one valid class: (.02488, .14545, .15573, .18522, .20283, .28589).
- **Seven-class conjecture** (also observed by leonbloy on MSE): if any assignment works, one of 7 specific classes
  works, and each of the 7 is sometimes the only one. No other class was needed in 3·10⁸ samples.
- The tray picture uses the sample (1.52, 3.52, 2.67, 4.53, 3.43, 2.33) on a stick of 18. Exactly **12 of its 30**
  assignments close.

## 2. Good permutations and Mersenne primes (MO 514690)
*A permutation of 1..n (n odd) is good if no proper consecutive block of length ≥ 2 has an integer average.
Is there one iff n is a Mersenne prime?*

- From the MO thread: good ⇒ n = 2^m − 1 (answer 514702). The canonical permutation 1, n−1, n, n−3, n−2, …, 2, 3
  is good iff n is prime (answer 516078). n = 63 has none (exhaustive).
- **Exhaustive counts with an unstructured DFS:** 3 → 2, 7 → 4, 31 → 4 (181.5 M nodes). Every other odd n ≤ 29 → 0.
  For 7 and 31 the four are the canonical permutation and its images under reversal and complement x ↦ n+1−x.
- **Lemma A (proved):** position mod 2^k determines value mod 2^k, through a binary-tree automorphism fixing 0.
  **Lemma B (proved):** given Lemma A, every even block length passes automatically. Only odd lengths 3 … n−2 can fail.
  So the question reduces to (tree automorphism) × (order inside each pair {j, j+2^{m−1}}).
- **Observed:** for n = 15, and in a partial run for 63, every arrangement that passes all non-divisor lengths still
  fails at length 3. Fixing the canonical residue map leaves exactly 1 good permutation for 31 and 127, and 0 for
  15, 63, 255, 511, 1023, 2047.
- **Conjecture (rigidity):** for a Mersenne prime n, the good permutations are exactly the 4 Klein-group images
  of the canonical one. This is verified for n = 3, 7, 31. Not proved: no good permutation exists for composite 2^m − 1.
- The third picture is built from this: each pyramid is the triangle of all block averages of the canonical
  permutation, one glass bead per block. **No bead is an integer except the coral apex, the whole row.** The
  pyramids 3, 7, 31, 127 are present; 15 and 63 are empty coral rings.

## 3. Reverse poker (MO 516074), math only (no picture this run)
- Three players each see the other two cards but not their own. Symmetric equilibria were computed on 64/128/256
  grids by smoothed best response plus Newton–Krylov, from many starting points.
- **Only one equilibrium was found at every λ ∈ [0.003, 3]**, so there is no sign of a discrete bifurcation cascade.
- The structure does change at **λ_c ≈ 0.65 ± 0.05**. Below it, the payoff Jacobian on the large mixed region is
  nearly singular (condition number 10³–3·10⁵, 40–140 near-zero directions), which points to a near-flat family of
  mixed equilibria. Above it the equilibrium is rigid (condition number 20–90).
- The call region is the square [0, a(λ)]² plus a band along the diagonal x ≈ y, which pinches off into a corner
  blob at λ ≈ 0.6–0.7.
- **Conjecture:** the asker's "multiple equilibria below λ_c" is a continuum of mixed equilibria on the
  indifference set, not a cascade.
