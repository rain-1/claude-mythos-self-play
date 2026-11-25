# Earshot — the nonlocal Fisher–KPP equation and how full a land can be

Seed: MO 518158 (a Fisher–Kolmogorov equation with nonlocal competition). Model, with R = 1 and growth rate 1:

    u_t = D Δu + u (1 − φ*u),     φ = normalised indicator of the disc (interval) of radius R,     s = R²/D.

`φ*u` is the *dose*: the crowd a newcomer at x would compete with. "Density" below means mean of u, in units of
the uniform state u ≡ 1.

## Checked numerically (scripts in this folder and one level up)
1. **Threshold.** u ≡ 1 loses stability when −φ̂(q) > q²/s for some q: s* = 185.19 in the plane (q = 4.779,
   wavelength 1.315 R), s* = 84.20 on the line (wavelength 1.541 R). Runs at s = 100 (line) stay flat; s ≥ 250 pattern.
2. **What the land settles into (plane, random start, torus 12.8², t = 600):**

   | s = R²/D | 250 | 600 | 2000 | 10⁴ | 10⁵ | D = 0 (replicator, 24 starts) |
   |---|---|---|---|---|---|---|
   | density | 1.258 | 1.493 | 1.704 | 1.797 | 1.837 | 1.88 … 2.08, mean 1.97 |

3. **Behind a front on the line** (`sim1d.py`, growth cut off below 10⁻⁷):

   | s | 300 | 1000 | 3000 | 10⁴ | 3·10⁴ |
   |---|---|---|---|---|---|
   | tooth spacing / R | 1.47 | 1.425 | 1.345 | 1.275 | ≈1.24 (few teeth) |
   | people per tooth / R | 1.81 | 1.92 | 1.96 | 1.98 | 1.99 |
   | density | 1.23 | 1.35 | 1.46 | 1.55 | ≈1.6 |

4. With D = 0 a "village" from a random start is not a point: it is a constellation of points on which the dose is
   exactly 1 (stationary to 4 decimals, minimum dose 1.0000 everywhere).

## Proved (short)
Take D → 0 and call a measure μ **settled** if φ*μ = 1 on supp μ and φ*μ ≥ 1 everywhere (no empty site can be
invaded). Normalise so that φ*μ(x) = μ(B(x,R))/|B_R|.

* **Lemma 1 (never emptier).** Every settled μ has density ≥ 1, with equality only if φ*μ = 1 almost everywhere.
  *Proof.* Average φ*μ ≥ 1 over space; ∫φ = 1.
* **Lemma 2 (never more than 2^d).** Every stationary μ has density ≤ 2^d. *Proof.* A ball of radius R/2 that meets
  supp μ at x lies inside B(x,R), so it holds at most |B_R|; average over all positions of the small ball.
  On the line this is sharp: teeth of mass 2R at spacing R⁺ give 2.
* **Lemma 3 (the sphere-packing bound applies to measures).** Let f be a Cohn–Elkies function: f(0) = 1,
  f(x) ≤ 0 for |x| ≥ R, f̂ ≥ 0. Positive-definiteness gives f ≤ f(0) = 1, hence f ≤ 1_{B_R}. For periodic μ with
  total mass M on a torus of volume V (carrying capacity 1, so μ(B(x,R)) ≤ |B_R| on the support):
  |B_R|·M ≥ ∬ 1_{B_R}(x−y) dμ dμ ≥ ∬ f(x−y) dμ dμ ≥ f̂(0) M²/V,  so
  **density ≤ |B_R| / f̂(0)** — exactly the Cohn–Elkies linear-programming bound for packing balls of radius R/2,
  multiplied by 2^d. So a *weighted, smeared* population cannot beat the LP bound that point packings obey.
* **Corollary.** d = 1: max density 2. d = 8: max = 2⁸·π⁴/384 = 64.94, attained by villages on E₈ (Viazovska's
  function is sharp). d = 24: 2²⁴·π¹²/12! = 32,372.9, on the Leech lattice (CKMRV).

## Conjectures
* **(A) Weighted Thue.** In the plane the fullest settled land is the hexagonal one with villages just out of
  earshot, density 2π/√3 = 3.6276. Lemma 3 reduces this to the open question whether the Cohn–Elkies bound is
  sharp in dimension 2 (numerically it is, to many digits). Thue's theorem alone does not give it, because the
  measure need not be a packing: villages may hear each other and share the dose. No trial here exceeded 2.09.
* **(B) Fronts leave the land half full.** On the line the spacing left by a front decreases with s and the tooth
  mass → 2R; I guess spacing → R, density → 2 as s → ∞, but the data (1.47 → 1.24 over two decades) do not
  exclude a limit above R.
* **(C)** From a random start with D = 0 in the plane the density is 1.97 ± 0.06, about 54% of the maximum; is
  there a jamming constant here, as for random sequential adsorption?

Nothing was posted anywhere.
