# The Mian–Chowla sequence, its differences, and the number 33

Seed: MathOverflow 518238, *Is the difference set of the Mian–Chowla sequence expected to have
density zero?* (Erdős problem #340; the smallest integer not known to be a difference is 33.)

`A = 1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, …` — each term is the least integer that keeps all
pairwise differences distinct. Data: the 10,000 terms of the OEIS b-file A005282
(`b005282.txt`, a₁₀₀₀₀ = 9,369,171,844). Nothing here is a theorem; it is a heuristic, three
conjectures it produces, and the numerical checks. Nothing was posted.

## 1. The forbidden places are (nearly) Poisson — and that fixes the growth rate

A place x > aₙ is forbidden exactly when x = aᵢ + aⱼ − aₖ with k ∉ {i, j}. Call the number of such
representations the *dose* of x. The next term is the first place with dose 0.

Write aₙ = n³/L (L varies slowly). Treating A as a continuum of density ρ(t) = (L^{1/3}/3)·t^{−2/3},
the mean dose just above aₙ is

    λ = ½ ∬ ρ(u)ρ(v)ρ(u+v−aₙ) du dv = (I/54)·L,
    I = ∬_{u,v ≤ 1 ≤ u+v} (u·v·(u+v−1))^{−2/3} du dv = 7.1906834142706573…

If doses were Poisson, a place would be free with probability e^{−λ}, so the mean gap is e^{λ}.
Checked directly (`an3.py`: all triples landing within three mean gaps above aₙ):

| n | L = n³/aₙ | (I/54)·L | measured λ | log(mean gap) | variance/mean of dose |
|---|---|---|---|---|---|
| 100 | 36.74 | 4.89 | 5.01 | 6.53 | 0.65 |
| 200 | 46.26 | 6.16 | 6.12 | 7.77 | 0.75 |
| 400 | 55.94 | 7.45 | 7.39 | 8.93 | 0.85 |
| 800 | 67.36 | 8.97 | 9.01 | 10.21 | 0.89 |
| 1600 | 79.04 | 10.53 | 10.76 | 11.43 | 0.93 |
| 3200 | 89.64 | 11.94 | 12.21 | 12.69 | 0.96 |
| 6400 | 99.92 | 13.31 | 13.72 | 13.98 | 0.98 |
| 9500 | 105.74 | 14.08 | 14.37 | 14.71 | 0.98 |

Two things happen. The continuum formula gives the measured intensity to 2–3 %. And the doses,
sub-Poissonian for small n (the sums are spread *too* evenly, so free places are rarer and gaps
longer than e^{λ}), approach Poisson: variance/mean → 1 and log(gap) − λ falls from 1.5 to 0.3.

Self-consistency, gap = daₙ/dn ≈ 3n²/L = e^{λ}, then gives (I/54)·L ≈ 2 log n, i.e.

> **Conjecture A.** aₙ ~ c · n³ / log n with c = I/108 = 0.066580…

The OEIS entry records the guess aₙ ~ n³/log² n. On the data, aₙ·log n/n³ falls slowly
(0.125, 0.109, 0.097, 0.090, 0.086 at n = 100, 300, 1000, 3000, 10000) and aₙ·log² n/n³ rises without
levelling (0.58, 0.62, 0.67, 0.72, 0.79). The local exponent d log a/d log n ≈ 2.84 at n ≈ 9000
lies between 3 − 1/log n = 2.89 and 3 − 2/log n = 2.78; the corrections to A are of relative size
(log log n)/(log n), so the data cannot decide — the table above is the evidence, not the fit.

## 2. The difference set has density zero, at a definite rate

Every difference occurs once, so |(A−A) ∩ [1, X]| is the number of pairs at distance ≤ X:
∫ρ(t)·(n(t) − n(t−X)) dt = J·(L·X)^{2/3} with

    J = ⅓ ∫₀^∞ τ^{−2/3} (τ^{1/3} − (τ−1)₊^{1/3}) dτ = B(⅓,⅓)/6 = Γ(⅓)²/(6Γ(⅔)) = 0.8833193751…

(the closed form was found numerically and agrees to 25 digits). With Conjecture A, L ≈ (36/I)·log X:

> **Conjecture B.** |(A−A) ∩ [1, X]| ~ C · (X log X)^{2/3}, C = J·(36/I)^{2/3} = 2.5851…,
> so the density of A−A in [X, 2X] decays like X^{−1/3}(log X)^{2/3}.

Check (`an4.py`), using the measured L at each scale rather than its asymptotic form:

| X | 2¹⁰ | 2¹⁴ | 2¹⁸ | 2²² | 2²⁶ |
|---|---|---|---|---|---|
| \|D ∩ [1,X]\| / X^{2/3} | 7.13 | 10.44 | 13.26 | 15.32 | 16.42 |
| J·L^{2/3} | 6.85 | 9.14 | 11.72 | 14.24 | 16.49 |

Per octave the observed density is 1.0–1.2 × the prediction from 2⁷ to 2²³, the ratio drifting to 1.
The asker's "factor 0.81 per doubling" is 2^{−1/3 + (2/3)/log X} = 0.81 at X = 2³⁰. So: yes,
density zero is what the heuristic says, and the whole question is equivalent to the growth of aₙ.

## 3. An absent difference stays absent with a computable probability

By the Sidon property a gap aₙ₊₁ − aₙ can only be a number that is *not yet* a difference; and since
small numbers are almost all differences already, a small open d (like 33) can only ever appear as
a gap. At step n that has probability ≈ e^{−λₙ} ≈ 1/(mean gap). So an open d ≪ gap closes later with
probability T(N) = Σ_{n>N} 1/gapₙ ≈ L_N/(3N) → (12/I)·log N / N.

Check: of the d that are open after N terms, the fraction that close by n = 10,000:

| N | d ≤ | open | closed later | fraction | T(N) |
|---|---|---|---|---|---|
| 60 | 200 | 33 | 10 | 0.303 | 0.264 |
| 100 | 400 | 100 | 16 | 0.160 | 0.187 |
| 200 | 1500 | 580 | 71 | 0.122 | 0.112 |
| 400 | 5000 | 2522 | 156 | 0.062 | 0.065 |
| 800 | 20000 | 12576 | 428 | 0.034 | 0.037 |

The model also explains the one late surprise: 216 became a difference only at n = 3875
(a gap of 216 where the mean gap is 6·10⁵). And the gap distribution is exponential except at the
short end, where it is thinned by exactly the share of numbers already used
(P(gap < 0.01·mean) = 0.0059, not 0.0100).

> **Conjecture C.** Each integer that is not a difference of the first N terms becomes one later
> with probability (1 + o(1))·(12/I)·log N / N. In particular T(10⁴) = 0.0038, T(10⁵) ≈ 0.0005:
> **33 is never a difference, with probability about 0.9995** given that it is absent from the
> first 10⁵ terms (as the question reports).

The philosophical sting (Philosophy.SE 144664, *Can "nothing" be "absent"?*; 144713, *Is "nothing"
"thinkable"?*): if B is right, almost every positive integer is absent from A−A — and not one
absence is known. A presence is certified by two terms; an absence needs every future step. The
set of absent distances has density one and no known member.

## What I did not do
- No proof of anything. A rigorous version would need to control the Sidon set's triple sums near
  the frontier; even aₙ ≫ n^{2+ε} is open.
- I did not integrate the full mean-field equation a′(n) = exp(λ[a]) with the sub-Poisson
  correction; that would give a parameter-free prediction for a₁₀₀₀₀ and is the next thing to do.
- I could not identify I in closed form (PSLQ against Γ(⅓)³, π, √3 combinations found nothing).

## Files
- `an1.py` growth, absent differences ≤ 256 (33, 88, 98, 99, 105, 106, 112, 126, 130, …), late closers
- `an2.py`, `an3.py` (+ `an3.log`) dose statistics above aₙ; the constant I
- `an4.py` (+ `an4.log`) Sidon check of all differences ≤ 2²⁷, octave densities, gap statistics, T(N)
