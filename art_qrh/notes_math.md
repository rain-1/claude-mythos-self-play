# Notes — the quasi-Riemann hypothesis series (art_qrh)

Everything here is computed from scratch; nothing is taken from the openai/math repository except the
statements being illustrated (family 003: *The Quasi-Riemann Hypothesis*, 199 pp; the 49-page 11/12 paper;
*Uniform exclusion of Landau–Siegel zeros*, 9 pp).

## What the claim is
- A fixed σ₀ < 1 such that ζ(s), every Dirichlet L(s, χ) and every finite-order Hecke L-function over
  F = Q(√−3) has no zero with Re s > σ₀. Part I gives σ₀ = 11/12, Part II gives σ₀ = 7/8. Lean (Comparator
  challenge `QuasiRiemannHypothesis.lean`) states the ζ case against Mathlib's `riemannZeta`; the docs say the
  paper's later applications are not formalized.
- The classical regions are not of this form: de la Vallée Poussin's σ > 1 − 1/(5.573412 log t)
  (Mossinghoff–Trudgian constant) and Vinogradov–Korobov's σ > 1 − 1/(57.54 (log t)^{2/3} (log log t)^{1/3})
  (Ford's constant) both narrow to nothing as t → ∞; for Dirichlet L-functions Kadiri's
  σ > 1 − 1/(6.4355 log q) allows one real exception (the Landau–Siegel zero). The paper's second
  theorem claims (1 − β) log q ≥ c for every such real zero, with no value of c given.

## The mechanism (as drawn)
1. **Möbius sums** (Section 3 of the 11/12 paper): a power saving A₁(D) = Σ μ(n) ν(n) W(N n / D) ≪ D^{1−δ}
   gives the zero-free half-plane, by Littlewood's classical equivalence, in Hecke form.
2. **The family** A_u(D) = Σ μ(n) ν(n) χ_n(u) W(N n/D), χ_n(u) = (u/n)₆ the sextic residue symbol over
   Z[ω], n primary (≡ 1 mod 3). The rows u = p⁶ copy the target: χ_n(p⁶) = 1 unless p | n.
   Claimed (Prop. 3.1): Σ_{N u ≤ H} |A_u|² ≪ D^{1+ε} H — square-root cancellation on average over rows.
3. **Poisson summation in u** turns the sextic twists into Gauss sums; the Gauss–Jacobi identity absorbs μ(n)
   and leaves the cubic Gauss sum γ₂(n), which is a Fourier coefficient of Kubota's cubic theta function
   (Patterson). The automorphy of θ reflects the sums; the quadratic large sieve (Goldmakher–Louvel) bounds
   the reflected rows; Möbius inversion removes the cube factors.
4. **Transfer**: a Dirichlet character composed with the norm is a Hecke character over F; its L-function
   factors as L(s, χ) L(s, χχ₋₃) up to finitely many Euler factors, so a Hecke half-plane is a Dirichlet one.

## What was computed and checked here
- `eis.py`: Eisenstein-integer arithmetic (primary associates, factorisation over Z[ω], sextic symbols at
  split and inert primes, normalised Gauss sums γ_j(π) with the paper's additive character
  e(z) = exp(4πi Im z/√3)).
  - **Lemma 4.2 verified numerically**: |γ₂(π)| = 1 and γ₂(π)³ = −π/|π| to 1e−15 for every one of the
    18,020 primary primes of norm ≤ 200,000 (`gauss_sweep.py`, `gauss_200000.npy`).
  - Conjugate primes have conjugate Gauss sums (3,000 pairs checked, no violation).
- `tables.py`: all 10,811 primary n with N n ≤ 30,000 (9,468 squarefree), their factorisations, μ(n), and
  the symbol table (u/p)₆ for every prime and 458 rows u. Hand check: M_F(7) = −2 (ideals (1), (2), two of
  norm 7).
- **Square-root cancellation on average** (the content of (2.3)): over the 210 rows with N u ≤ 60,
  root-mean-square |A_u(30,000)| = 94.7, against √9,468 = 97.3. The target row u = 1 ends at −14 and its
  walk stays within [−118, 20]. (This is a consistency check of the claim's shape at one scale, nothing more.)
- **Kummer's problem**: over split primes of norm ≤ 200,000 the three cube roots are chosen
  6,996 / 5,490 / 5,490 times (34.6 % / 27.7 % / 27.7 %); the strawberry road's excess shrinks shell by
  shell. The running sum Σ_{N π ≤ x} γ₂(π) is real to rounding (conjugate symmetry) and
  |S(x)| / x^{5/6} ≈ 0.079, 0.076, 0.068, 0.061 at x = 10⁴, 5·10⁴, 10⁵, 2·10⁵ — consistent with the
  Heath-Brown–Patterson main term of order x^{5/6}.
- `zeta.py`: ζ on the strip by Euler–Maclaurin (N = 120, 12 Bernoulli terms), checked against mpmath to
  1e−14 for |t| ≤ 140; the first 120 zeros from mpmath, 2,469 zeros to t = 3000 by Riemann–Siegel.

## Honest limits
- The pictures illustrate the *objects* the proof manipulates. They cannot test a zero-free half-plane:
  no zero off the line has ever been computed, and none ever will be if RH is true. The walks picture tests
  only that the family behaves at D = 30,000 the way the claimed estimate says it should on average.
- The claimed cut (1 − β) log q ≥ c is drawn with c = 1 because the paper gives no constant.
