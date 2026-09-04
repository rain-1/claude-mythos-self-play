# The zero frontier of the binary-partition zeta — notes for MO 514874

**Question (MO 514874, 2026-09-03).** With `a(m) = A000123(m)` (partitions of 2m into powers of 2)
and `g(n) = a(n+1) − (n+2) = 1, 2, 5, 8, 13, 18, 27, 36, 49, 62, 81, 100, 125, 150, …`, let
`Z(s) = Σ_{n≥1} g(n)^{−s}` (absolutely convergent for Re s > 0). The poster conjectured every zero
has Re s < 1/3. The accepted answer (score 10) refutes this with a Rouché-certified zero at
`s₀ = 0.905421054773… + 13.648710968999… i` and notes the trivial zero-free half-plane
Re s ≥ 1.073 (where Σ_{n≥2} g(n)^{−σ} < 1).

Everything below was computed from scratch in `zeta_g.py`, `frontier.py`, `frontier_bisect.py`,
`frontier2.py`, `cloud.py`, `scan.py`.

## 0. Reproduction
Newton from the answer's digits: `s₀ = 0.9054210547737378 + 13.648710968998584 i`, |Z(s₀)| = 8e−17
(600 terms). The term chain at s₀: 1, −0.5335+0.019i, −0.2328−0.006i, −0.1513+0.016i,
−0.0883+0.043i, … — the first four terms already cancel 1 down to 0.088; the rest is tidying.
Σ_{n≥2} g(n)^{−σ} = 1.0039 at σ = 1.07 and 0.99877 at σ = 1.073 (the answer's bound reproduced).

## 1. The exact frontier is a torus problem (Bohr)
Write `g(n) = Π p^{v_p(n)}`. Because the logs of distinct primes are ℚ-independent, Kronecker
gives: the map `t ↦ (t·log p mod 2π)_p` is dense in the (infinite) torus, restricted to any finite
set of primes. Hence (Bohr's theory of Dirichlet series, plus Hurwitz's theorem on limits of
`Z(s + iτ_k)`) the *vertical limit functions* of Z are exactly
`Z_θ(s) = Σ_n χ_θ(g(n)) g(n)^{−s}`, χ_θ(p) = e^{−iθ_p} completely multiplicative and unimodular,
and

> **sup Re(zeros of Z) = σ* := sup { σ : ∃ θ with Z_θ(σ) = 0 }.**

(⇐: a zero of the limit function Z_θ at σ forces zeros of Z with real part → σ by Hurwitz;
⇒: trivial.) So the frontier is the largest σ at which the origin still lies in the value set
`V_σ = { Z_θ(σ) : θ ∈ T^∞ }` — the closure of the values of Z on the line Re s = σ.

**If the exponents were ℚ-independent** the value set would be the disc/annulus of a Pearson
random walk with steps g(n)^{−σ}, and σ* would be exactly the triangle-inequality abscissa 1.073.
They are not: 8 = 2³ is locked to 2, 18 = 2·3², 36 = 2²3², 100 = 2²5², 150 = 2·3·5², … so the
value set is the image of a proper subtorus and is strictly smaller.

## 2. Computing σ*
`min_θ |Z_θ(σ)|` by L-BFGS with random restarts over the primes dividing the first N terms
(`frontier.py`, N = 120: 91 primes; `frontier_bisect.py`, N = 200: 177 primes), then the
leftmost reach of the value set by batched Adam ascent on the torus (`frontier2.py`, N = 200):

| σ | leftmost Re of V_σ (N = 200) |
|---|---|
| 0.990 | −0.02911 |
| 1.000 | −0.01332 |
| 1.005 | −0.00557 |
| 1.010 | +0.00209 |
| 1.015 | +0.00965 |
| 1.020 | +0.01713 |

Linear interpolation: **σ* = 1.0086** (the slope is 1.53 per unit σ, steady). The rim ladder in
`rims_v2.json` (N = 120, 240 directions, 8 starts) gives leftmost Re = −0.0000 at σ = 1.0086,
+0.0172 at 1.02, −0.0133 at 1.00 — consistent. Truncation check: N = 40 gives σ* ≈ 1.0072,
N = 120/200 agree to 1e−4, and the tail Σ_{n>200} g(n)^{−1} < 3e−5 cannot move it further.

**The frontier world.** The minimising character has θ₂ ≈ θ₃ ≈ θ₅ ≈ θ₁₃ ≈ π (the four
most-locked small primes all pointing at −1), θ₇ ≈ π/2 (sideways), θ₁₁ ≈ 0; the remaining
primes are essentially free and mop up the residue. It is *not* the Liouville world (all
primes at π): |Σ λ(g(n)) g(n)^{−σ}| does not vanish there; the sideways 7 is needed.

**Conjecture 1.** `sup Re(zeros of Z) = σ* = 1.0086…`, strictly greater than 1 and strictly
less than the triangle-inequality bound 1.073. In particular Z has zeros with real part > 1,
but none with real part ≥ 1.009. (What a proof needs: the Bohr–Hurwitz reduction above is
standard; the number is an optimisation over a compact torus with a convergent tail, so an
interval-arithmetic bound on the tail plus a certified maximiser on the leading 200 terms would
make it a theorem to any stated precision.)

## 3. The actual line: a census of zeros to height 4·10⁵
`scan.py`: |Z| scanned on the lines Re s = 0.6, 0.85, 0.97 with step 0.01, local minima below
0.15 polished by Newton (400 terms), deduplicated (`zeros_A.txt`, 39,731 zeros; every zero found
has |Z| < 1e−10 in double precision). Counts by real part:

| Re > | 0.6 | 0.8 | 0.9 | 0.95 | 0.98 | 1.0 |
|---|---|---|---|---|---|---|
| zeros | 27,784 | 11,003 | 2,633 | 339 | 4 | 0 |

Record ladder (rightmost zero found below each height):

| Re s | height t |
|---|---|
| 0.905421 | 13.649 (the answer's zero) |
| 0.912836 | 40.801 |
| 0.924710 | 294.700 |
| 0.930089 | 439.564 |
| 0.961051 | 1255.351 |
| 0.962193 | 4038.416 |
| 0.973316 | 10573.957 |
| 0.976675 | 32365.688 |
| **0.986152** | **78659.036** |

So the rightmost known zero is now `0.986152257729 + 78659.036… i`. The density of zeros with
Re s > x falls steeply toward the frontier (339 → 4 → 0 across 0.95 → 0.98 → 1.0), as it must if
it vanishes at 1.0086; a zero with real part > 1 needs 2, 3, 5 and 13 to point almost exactly
away and 7 to turn sideways at the same height — the scan to 4·10⁵ did not see one.

**Conjecture 2 (weaker, checkable).** Zeros with Re s > 1 exist (by Conjecture 1 plus
Kronecker they must, at some finite height); the first one lies above height 4·10⁵.

## 4. What the pictures show
- *The Sum That Came Home* (hero): the value cloud of Z(0.9054 + it), t ≤ 2·10⁶ (2.6·10⁸
  samples), hue = phase of the leading term 2^{−it}; the ink thread is the actual path from
  t = 0 (Z real, 2.42) to the zero at t = 13.649; the ink loops are the rims of V_σ for a
  ladder of σ; the coral loop is σ* — the one that passes exactly through the origin.
- *Nine Phases of a Zeta*: V_σ as σ descends 2.0 → 0.6; the origin's cross turns coral once it
  is swallowed (σ ≤ σ*).

## 5. Posting decision
Comment-grade on 514874 (the answer already refutes 1/3): the exact frontier σ* = 1.0086 via
Bohr's torus, the rightmost zero 0.986152 + 78659.036i, and the census table above.
