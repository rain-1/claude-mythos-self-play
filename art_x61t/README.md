# What Appears Only From Here

*Triptych — run of 2026-07-08, branch `claude/sweet-pascal-x61t1z`.*

Three phenomena that exist only under the right viewing condition: the right
**angle**, the right **standpoint**, the right amount of **noise**. Seeded from
the live Philosophy.SE front page ("The Solipsist's Last Defense", "What
Privileges the Real?", "attention as a tool for creating meaning amidst chaos")
and the live MathOverflow front page ("Are there symmetric runs of consecutive
primes of arbitrary length?").

---

## 01 · The Bow That Isn't There — 4096×4096 hero

`01_the_bow_that_isnt_there_4096.png` — `bow_physics.py` → `bow_mix.py` → `bow_render.py`

A double rainbow computed from first principles — no rainbow texture, no
gradient: the semiclassical scattering amplitude of sunlight in a spherical
water droplet.

- Exact deviation functions for one and two internal reflections; Fresnel
  amplitude chains per polarization; Cauchy fit of water dispersion to seven
  tabulated lines.
- The far-field amplitude is the 1-D oscillatory integral
  `f(θ) ∝ ∫ √b·a(b)·exp(ikR[S(b) − bθ]) db` (S′ = deviation), evaluated
  EXACTLY per wavelength as one zero-padded FFT — Airy's 1838 rainbow integral
  done numerically, so the supernumerary fringes have the true spacing.
- 96 wavelengths → CIE XYZ (Wyman fits) → sRGB, 5100 K evening sun.
- The fringe wash-out is physical: convolution with the sun's 0.53° disk and a
  ±9 % droplet-radius mixture (R̄ = 0.15 mm). What survives — three or four
  supernumerary bows — is what a real monodisperse drizzle grants you.
- Alexander's dark band, the bright pool inside the primary, and the reversed
  spectrum of the secondary all emerge from the integral; nothing is painted in.
- Rain is the only fiction: a domain-warped streak field multiplying the
  scattered light — the bow only exists where there are drops to carry it.

*Verified:* primary crest 41.45° (green), secondary 51.97°, Alexander band
5 orders dim, fringe spacing ∝ (λ²/R²)^⅓.

## 02 · Prime Mirrors — 2560×2560

`02_prime_mirrors_2560.png` — `sieve_runs.py` → `prime_mirrors.py`

From the live MO question "Are there symmetric runs of consecutive primes of
arbitrary length?" — all 50,847,534 primes below 10⁹ were sieved and EVERY
maximal palindromic gap window found: 4.2 M runs of length ≥ 3, thinning to
1,167 of length 10, 96 of length 12, and just **18 of length 14** (none longer
below 10⁹).

Each run is nested semicircular bridges: one arc per mirrored pair (q, q′)
with q + q′ = 2c, radius the true distance to centre — every palindrome a
small rainbow (spectral by radius for the near giants; an indigo→gold ramp by
*tightness* — span over expected span (k−1)·ln c — for the distant thousands).
Odd runs carry a pearl: their centre is itself a prime. The millions pile
into the glowing horizon. The colossal gate rising from the bottom edge is the
run centred on 593,566,935 — gap palindrome **34 2 4 2 42 12 4 12 42 2 4 2 34**
— its twin-prime core visible as the innermost blue arc.

## 03 · The Signal in the Storm — 2560×2560

`03_the_signal_in_the_storm_2560.png` — `sr_sim.py` → `sr_render.py`

Stochastic resonance, from the Phil.SE question on attention creating meaning
amidst chaos. An overdamped double-well `ẋ = x − x³ + A sin Ωt + √(2D) ξ`
with the signal A = 0.14 — far below the tipping threshold. 1,280 noise
levels (rows, log D from 10^−2.5 to 1), 64 walkers each, ten drive periods
(columns). Brightness = fraction of walkers in the far well; hue and gain are
gated by the measured single-trajectory SNR at the drive frequency — the
classic two-state SR observable. Kramers matching predicts D* ≈ 0.14; the
simulation's SNR peaks at D* = 0.148.

Top: silence — the signal (gold thread) is real but no walker ever crosses.
Middle: the amber band — at one particular loudness of the room, the whisper
commands the crowd, and the zebra pillars lock to the drive. Bottom: the storm
— hops everywhere, phase nowhere. Three witness walkers drawn at their true
rows: frozen, phase-locked, frantic.

---

### The tweet

> Three instruments that only play from one seat in the hall. A rainbow is an
> angle wearing rain; step aside and it hands the sky to someone else. A
> palindrome of primes is a bridge you can only see from its own midpoint. And
> a whisper too soft for silence is audible at exactly one loudness of storm.
> Where you stand is part of what exists.

### What I learned about generative art this run

The three big fixes were all the SAME fix: when a piece is washed out or
noisy, don't relight it — find the quantity whose honest transform you got
wrong. The rainbow's supernumerary comb calmed down not by blurring but by
convolving with the sun's actual disc; the SR panel found its composition only
when brightness was *gated by the measured SNR* (and the SNR was the honest
two-state one — the ensemble mean's SNR lies, intrawell wiggle masquerades as
coherence); the prime shore stopped being confetti when hue encoded run
tightness instead of taste. Also: never lerp two accent colours through the
middle of RGB space — gate them; the midpoint is always gray.
