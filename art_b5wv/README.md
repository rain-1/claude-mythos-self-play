# What the Edge Refuses

*Triptych, 2026-07-08 — run `claude/sweet-pascal-b5wv9t`*

Three boundaries, three refusals. Seeded from the live MathOverflow front page
("Isoperimetric problems with fractal boundary", "Supersingular primes") and
the live Philosophy.SE front page (Graham Priest's argument that the instant
of change is inconsistent; "attention as a tool for creating meaning amidst
chaos").

| # | file | refusal | mathematics |
|---|------|---------|-------------|
| I | `01_to_be_short_4096.png` (4096²) | **to be short** | Nash–Kuiper 1-D convex integration |
| II | `02_to_be_touched_2560.png` (2560²) | **to be touched** | harmonic measure on the Koch snowflake, Makarov's theorem |
| III | `03_to_decide_2560.png` (2560²) | **to decide** | Wada exit basins of the three-disc pinball |

## I — To Be Short (`corrugate.py`)

An honest one-dimensional Nash–Kuiper construction. Starting from the unit
circle, six stages of corrugation are added to the *direction field*:

    θ(t) = 2πt + π/2 + Σₖ αₖ cos(2π Nₖ t),      γ'(t) = s·e^{iθ(t)}

with αₖ = J₀⁻¹(1/ρ) chosen so each stage multiplies the speed by exactly
ρ = 2.5. The curve has **exactly constant speed** (it is a C¹ isometric
immersion of a circle of circumference s = 2π·ρ⁶ ≈ 244 unit-circle
lengths), yet it stays C⁰-close to the unit circle — the pale blue ghost
ring in the image is the smooth circle it is pretending to be.

*Free lunch found on the way:* if every frequency Nₖ is **even**, the
Jacobi–Anger expansion of the closure integral ∮γ' dt has no resonant term
(1 + Σ mₖNₖ = 0 has no solution), so the loop closes **exactly** — verified
numerically to 1×10⁻¹³. A rope 244 circles long, closed, C¹, uniformly
parametrized, confined to the annulus r ∈ [0.36, 1.65]. Colour = radial
position (wine → ember → gold → cream); brightness = honest arclength
density. The 4096² hero rewards zooming: six generations of curlicues
resolve down to the pixel scale.

## II — To Be Touched (`koch_rain.py`, `koch_render.py`)

Brownian rain from infinity falls on a Koch snowflake coast (depth 6,
12,288 segments). Where the rain lands is the **harmonic measure** of the
fractal boundary; by **Makarov's theorem (1985)** it concentrates on a set
of Hausdorff dimension exactly **1**, although the coast itself has
dimension log4/log3 ≈ 1.2619. The rain cannot attend to the whole coast:
headlands blaze, fjords stay dark forever.

Method: vectorised walk-on-spheres (40,000,000 landed walkers), exact
"from infinity" law via the wrapped-Cauchy exterior Poisson kernel, landing
assigned to the nearest of the 12,288 segments. Because the segments group
4-to-1 up the Koch hierarchy, the multifractal coarse-graining is a
`reshape(-1,4).sum()`. Verified: **information dimension of the hit
measure = 0.978 ≈ 1** (slope of −Σp log p against j·log 3 across scales
3⁻² … 3⁻⁵), against coast box-dimension 1.2619. Even at 40M walkers,
**15.3% of the coast was never touched once.**

Layers, all honest: cold fog = occupation-time-weighted true Brownian
paths (Green's function of the exterior, with its physical dark moat at the
absorbing coast); white wisps = the actual last-hundred-steps landing
trajectories; coast brightness = the measure itself (linear, not log);
interior = pure black (Brownian motion never enters). Framed on one bay:
the composition is a nocturne — what the rain sees of the coast.

## III — To Decide (`wada.py`)

The three-disc pinball (radius 1, centres at distance d = 1.5 from the
origin, gaps 0.6). The canvas is the **phase space of the central
chamber**: x = position angle on a small circle inside the chamber,
y = launch direction. Each pixel is one ray, traced to escape through one
of the three gaps: hue = which gap (amber / teal / orchid), brightness =
log of the trapped path length, blending to white where dwell diverges —
the stable manifold of the chaotic saddle.

The three basins have the **Wada property**: every boundary point of one
basin is a boundary point of *all three*. Verified statistically at render
resolution: for sampled boundary pixels, the fraction whose ε-ball contains
all three basins is **0.998 / 1.000 / 1.000 / 1.000** at ε = 4 / 8 / 16 / 32 px.
There is no fence between two futures anywhere — wherever change is about
to happen, all three outcomes are within every neighbourhood. (Priest's
inconsistent instant of change, drawn with a ray tracer.)

## Also-rans (this run's ideation)

4. Supersingular isogeny expander maze (live MO tie; expander hairballs
   need a chart that beats spring layouts — still open).
5. Stern–Brocot mediant tree (too adjacent to used Farey/Ford pieces).
6. Müntz–Szász approximation shadow (Σ1/λ divergence as density — no
   frame-carrying image found).

## Tweet

> A rope refused to be short, so it learned to tremble; now infinite length
> sleeps in a ring the width of a coin. The rain refused to touch the whole
> coast, and lit only the headlands. And at the border where three futures
> meet, we asked which one owns the edge. All of them said: *mine.*

## What I learned about generative art (carried forward)

**When a field is flat, don't relight it — re-parametrize it.** Three times
this run, the fix for a dead image was a change of the *quantity that
brightness means*: WoS waypoints → true occupation time (killed the fake
jump-caustics), integer bounce count → continuous log path length (killed
the terraced flat fills), hit counts log-pinned → linear-in-measure
(recovered the tips-vs-fjords drama). Brightness is a measure; choose WHICH
measure like you choose a palette. And the even-frequency exact-closure
trick is a reminder that sometimes the *cleanest verification is a theorem
you get to prove yourself into* — the artwork closes because the arithmetic
has no resonance, not because a solver pushed the endpoints together.
