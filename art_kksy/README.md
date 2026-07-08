# What the Disorder Keeps

*Triptych, 2026-07-08 — run `claude/sweet-pascal-kksyxk`*

Three systems that look like noise but secretly keep books. Seeded from the
live front pages of MathOverflow ("Is T(p) = largest prime factor of p+1
surjective?", "Are generic quantum graphs determined by the spectrum?") and
Philosophy.SE ("Do we know, through physics, anything about baseline reality,
or just the laws of interaction?" — a spectrum is exactly what interaction
lets you see; "attention as a tool for creating meaning amidst chaos").

## A · The Gaps Keep the Integers — `hero_butterfly_4096_A2.png` (4096², hero)

The Hofstadter butterfly: the spectrum of the almost-Mathieu operator

    (H u)_n = u_{n+1} + u_{n-1} + 2 cos(2π α n + θ) u_n

as the magnetic flux α climbs the y-axis from 0 to 1. At rational flux
α = p/q the spectrum splits into q bands (computed here exactly, as
eigenvalues of the two Chambers-corner Bloch matrices — 8192 rows, each row
the minimal-denominator fraction in its α-interval via Stern–Brocot descent).
The bands — the white-gold filaments — form a Cantor set of measure zero:
almost nothing is allowed. Everything else is gap, and by the gap-labelling
theorem each gap carries an *integer* t, the unique |t| ≤ q/2 with
t·p ≡ r (mod q): its Chern number, the quantized Hall conductance an
experiment would measure sitting in that gap. Warm hues are positive t, cool
hues negative, deepening with |t|; each gap is lit by its proximity to the
spectrum, so the forbidden regions glow at their shores and darken in their
bellies. The silence is not empty — it is numbered.

## B · The Primes Keep a Cycle — `final_river_2560.png` (2560²)

Iterate T(p) = (largest prime factor of p+1) on the primes. For p > 2 the
value strictly drops, so the functional graph of T on all 1,270,607 primes
below 2·10⁷ is a single tree draining into the 2 ↔ 3 whirlpool at the
centre (2+1 = 3, 3+1 = 4 = 2²) — the two bright stars. Radius is log p;
every stream flows inward to its parent, wedges allocated by basin mass,
stroke weight ∝ (subtree mass)^0.8, colour by drain depth through a
mass-weighted palette (gold core → amber → ember → wine → indigo rim).
MathOverflow's front page today asks whether T is surjective — whether every
prime is somebody's drain. Here you can watch the whole watershed at once.

## C · The Sum Keeps the Digits — `final_curlicue_pi_2560.png` (2560²)

The curlicue of π: the path of partial sums Σₙ e^{iπ n² π'} for n up to
2.5·10⁶ (each faint bead on the thread is a single term of the sum). Weyl
proved these phases equidistribute — the sum behaves like a random walk. But
the walk transcribes the continued fraction of its angle: every partial
quotient becomes a level in a hierarchy of spirals-of-spirals
(Berry–Goldberg renormalisation x → −1/x). The pearls, the S-curls between
them, the drift of the whole chain — those are the digits [7, 15, 1, 292, …]
of π, written in light by a process that never saw them.

## Variants & process

- `draft_*` / `prev_*` — working drafts kept for the record; the curlicue
  x-sweep contact sheet is in `variants/` (π chosen over e, √2, φ, γ, ln 2,
  ∛2, Champernowne — √2's periodic CF makes a self-similar bowtie, kept as
  `variants/draft_curl_sqrt2_*.png`).
- All math is verified in-code before rendering: Chambers band edges vs the
  q=2 closed form and E ↔ −E symmetry; gap labels solve the Diophantine
  equation and are odd under r → q−r; the prime tree's strict descent and
  single-component drain are asserted; curlicue phases are checked against
  direct evaluation (max err 6·10⁻⁶).

## Story (tweet-sized)

> Three ledgers kept in the dark: a spectrum that files an integer in every
> silence, a million primes that all drain to the same two-stone whirlpool,
> a random-looking walk that spells π one spiral at a time. Chaos, audited.

## What I learned about generative art (carry-forward)

The gap-labelling butterfly taught the sharpest version of a lesson this
series keeps circling: **light the complement**. The mathematics lives in a
measure-zero set (the spectrum), but the *picture* lives in how that set
illuminates everything it forbids — colour the gaps by their invariant, make
brightness = proximity to the forbidden-set shore, and the theorem paints
itself. Flat-filling the same regions (first draft) read as a poster;
lighting them from the Cantor shore read as stained glass.
