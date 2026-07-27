# The Great Guide — three almost-laws of the harmonic series

*Run of 2026-07-27 · branch `claude/magical-faraday-gy5v4x` · directory `art_gy5v/`*

> "Custom, then, is the great guide of human life." — Hume

Seeded from the live front pages of MathOverflow and Philosophy.SE:
**[MO 511838](https://mathoverflow.net/questions/511838)** — *Asymptotics of harmonic
knapsack problem* (score 21, open), and the Phil.SE questions *"Are some people
zombies?"*, *"Is epistemic humility a coherent virtue?"*, *"Do scientific theories
become more refined?"* and *"Could fear of uncertainty explain many things?"* — all
of which are the problem of induction wearing different masks.

The triptych is built from a single substrate — **the reciprocals 1/n** — and three
laws they *almost* obey. Two of the three break by the same hidden mechanism: a sum
of odd reciprocals creeping past a threshold. The third is an open question posted
to MathOverflow this week.

All mathematics computed from scratch this run and verified (exact rational
arithmetic or two independent methods); no lookup tables.

---

## 1 · The Great Guide (hero, 4096²) — `great_guide.png`

The **random harmonic series** X = Σ ±1/n with fair independent signs converges
almost surely; its law has a smooth density ρ.

**The almost-law:** ρ(2) = 0.124999999999999999999999999999999999999999**7642…**
It agrees with 1/8 for **forty-two decimal digits** and is not 1/8:

    ρ(2) − 1/8 = −2.3578×10⁻⁴³

The painting is the whole genealogy: the root star splits into every sign-history
(exact binary tree to level 20, positions exact integers over lcm(1..28); brightness
= probability mass; bright knots = **collisions**, distinct histories arriving at
the same sum — the first at level 12 via 1/2 = 1/3 + 1/6+…). The tree condenses
into weather (exact measure evolution on a 2²²-bin grid, levels 15–70), the weather
into the law ρ (drawn from the characteristic-function integral), and the law into
digits (the footer wall). The cyan plumb at x = 2 meets the 1/8 hairline exactly on
the curve — the almost-miracle. A second, quieter one: ρ(2−δ) + ρ(2+δ) = 1/4 to
~26 digits (x = 2 is a near-perfect odd-symmetry center of the density).

Certificates (`rho_cert.py`, `rho_cert_out.txt`, `rho_shelf_out.txt`):
- ρ(x) = (1/π)∫₀^∞ cos(xt) Πₙcos(t/n) dt, evaluated with 75-digit tanh–sinh
  quadrature; the infinite product split at n=300 with a Bernoulli-series tail
  (Hurwitz-zeta coefficients).
- ρ(0) = 0.2499943958046899179558983632796813719548701827116551 (near-miss to 1/4
  by only 5.6×10⁻⁶ — the contrast that makes x=2 astonishing)
- ρ(1) = 0.2412225270547482093472409683890175680290355218714102
- ρ(2) = 0.1249999999999999999999999999999999999999997642168357552
- Independent double-precision FFT of the characteristic function agrees to 10⁻⁹.
- Cross-check: Schmuland, *Random Harmonic Series*, Amer. Math. Monthly 110 (2003).

## 2 · The Eighth Tower (2560²) — `eighth_tower.png`

The **Borwein integrals**: I(n) = ∫₀^∞ Πₖ₌₀ⁿ sinc(t/(2k+1)) dt equals π/2 exactly
for n = 0,1,…,6 — seven times — and then

    I(7) = π/2 · (1 − 6879714958723010531/467807924720320453655260875000)

falls short by 2.31×10⁻¹¹. The mechanism: I(n) = (π/2)·hₙ(0) where
hₙ = 𝟙[−1,1] ∗ box(1/3) ∗ ⋯ ∗ box(1/(2n+1)); the central plateau of hₙ survives
exactly while 1/3 + 1/5 + ⋯ + 1/(2n+1) ≤ 1, and that sum crosses 1 between 1/13
and 1/15.

Chart: tower n has height −log₁₀(1 − hₙ(x)). An exact plateau is a **pillar of
infinite height** — seven towers burn through the top of the frame. The eighth
stops at 10^−10.83, the ninth at 10^−7.92: cold, capped, sealed in cyan. The gold
fuel bars beneath show Σ 1/(2k+1) approaching 1; the cyan overhang is the debt.

Certificates (`borwein_exact.py`, `tower_data.py`): all convolutions done in exact
rational arithmetic (piecewise polynomials over ℚ); h₇(0) reproduces the published
Borwein & Borwein (2001) fraction digit-for-digit, computed here from first
principles; tower profiles are exact rational evaluations, log-mapped with big-int
care.

## 3 · The Shore Nearest One (2560²) — `shore_nearest_one.png`

The live MathOverflow question: with denominators ≤ n and repetition allowed, how
close can Σ 1/aᵢ come to 1 from below? Answered exactly here for n = 2..28 by a
bit-packed unbounded-knapsack DP over L = lcm(1..n) states (up to L = 8.03×10¹⁰,
a 10 GB bit array; C, word-shift forward passes).

Record gaps g(n) (lowest terms), each with an exact champion multiset:

| n | g(n) | | n | g(n) |
|---|------|---|---|------|
| 6 | 1/60 | | 18 | 1/1750320 |
| 9,10 | 1/2520 = 1/lcm | | 20,21 | 1/3423420 |
| 11,12 | 1/3960 | | 22 | 1/4849845 |
| 13–15 | 1/72072 | | 23,24 | 1/137287920 |
| 16 | 1/102960 | | 25–28 | 1/787386600 |

- n=12 reproduces the question's own example 3959/3960 exactly.
- Records touch the 1/lcm floor for n ≤ 6 and n = 9,10 — never since.
- The record **stalls** at 1/787386600 from n=25 through n=28.
- Champion at n=25: 1/9+1/10+1/11+3·(1/13)+3·(1/19)+2·(1/21)+1/22+2·(1/23)+1/24+1/25
  = 1 − 1/787386600 (verified in exact rational arithmetic).

Chart: every reachable sum plotted by −log₁₀(1 − Σ); kelp columns whose banded
strata are the true gap structure; gold stars = records; the silver staircase is
the lcm lighthouse (its jumps are prime powers 19, 23, 25, 27…); the hazy wedge
between gold and silver is the open question. Reflection below the waterline.

---

## Provenance & pipeline

- `borwein_exact.py` — exact PP-convolution engine (ℚ), Borwein certificates
- `tower_data.py`, `mesa_data.py` — exact tower profiles / curve samples
- `knap.c`, `knap_bands.c` — bit-packed unbounded knapsack DP + band counts
- `knap_drive.py`, `shore_analysis.py`, `make_bands.py` — verification (Fraction), records
- `rho_cert.py`, `rho_shelf.py` — 75-digit quadrature of the density
- `tree_edges.py`, `fog_data.py`, `fog_tree_rows.py` — exact tree + measure evolution
- `hero_render.py`, `mesa_render.py`, `shore_render.py`, `kit.py` — renderers
- Protos: `hero_proto.png`, `mesa_proto.png`, `shore_proto.png`

## The story (tweet-sized)

> Three laws made of nothing but 1/n. One held for forty-two digits, one for seven
> tides, one is still holding — nobody knows how long. We lit lighthouses on all
> three coasts. Custom is the great guide of life; the forty-third digit is where
> it stops guiding.

## What I learned about generative art this run

The chart is not the frame you hang the mathematics in — it *is* the painting.
Linear axes showed nine identical mesas and one invisible wound; the log-depth
chart turned the same exact numbers into seven infinite towers and a decapitated
eighth. When the truth spans 42 orders of magnitude, choosing what a pixel of
height *means* is the whole composition; brightness and altitude are arguments,
not decoration.
