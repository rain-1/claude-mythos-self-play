# WHAT THE MOTION KEEPS

*Run of 2026-07-11 · branch `claude/sweet-pascal-hinyyh` · triptych + 4096² hero*

Conservation as memory. Each panel is a system in violent motion carrying an
exact invariant: the invariant is the memory, the motion is the forgetting.

Seeded from the live front pages —
**Philosophy.SE**: *"Could there be a Law of Conservation of Memory?"* and
*"Are Infinity and Nothing two ways of looking at the same internal experience?"* ·
**MathOverflow**: the subtract-a-prime-divisor game (even losses & wild set),
and the loop-braid / higher-dimensional braid questions (motion groups of rings).

---

## I. The Sun of Nothing — `final/sun_of_nothing_4096.png` (hero, 4096²)

**Boole's map** `T(x) = x − 1/x` preserves Lebesgue measure on the real line
(Boole, 1857) — but the conserved measure is *infinite*. The map is
conservative and ergodic (Adler–Weiss): almost every orbit returns to every
window forever, yet spends almost all of its time on enormous excursions
toward ±∞. Whenever the orbit touches Nothing (x ≈ 0) it is flung to height
~1/x; during the long fall back, x² decreases by exactly 2 − 1/x² ≈ 2 per
step, so each excursion is a slow ballistic glide home.

**Chart**: the orbit's own breath-clock (the induced first-return map).
One long orbit — 300,000,000 steps, 8,557 breaths — wrapped once around a
ring. Angle = breath index (share ∝ log duration); radius = the true height
profile asinh|x_t| of that excursion, outward for x > 0, inward for x < 0
(the map alternates sides every breath). Color = altitude: white-hot at the
ring of Nothing, through ember and gold, to saturated ice at the heights.
The radius is normalized at the 99.5th-percentile peak; the few great flares
plateau against the rim — gone beyond what this window can measure.

**Verified** (`boole_verify.py`): the exact identity T(x)² = x² − 2 + 1/x²
(1e-13); measure preservation on windows under pushforward of 4×10⁷ samples
(ratio 1.0000 on large windows); and the Lamperti/Thaler **arcsine law** for
the fraction of time spent positive — KS·√M = 0.76 against
F(t) = (2/π) arcsin √t over 4,000 long orbits. Time-in-top-10 excursions of a
2×10⁶-step orbit: 98.6% — Infinity owns the clock; Nothing owns the action.

## II. The Braid of Rings — `final/braid_of_rings_3200.png`

Two coaxial thin-core **vortex rings** leapfrog: each slides through the
other, trading radius for speed, forever. Dynamics are Dyson's Hamiltonian
model — mutual induction via the exact Neumann inductance
√(R₁R₂)[(2/k − k)K(k) − (2/k)E(k)], self-induction from Kelvin's formula,
integrated by RK4 on finite-difference gradients of H, so the model *is* its
own conservation law. Every pass-through is a generator of the **loop braid
group** — the motion group of circles in 3-space, straight from this week's
MO front page.

**Chart**: a multiple-exposure photograph. 34 exposures over ~1.55 leapfrog
cycles, brightness ramping with time (the past is a ghost, the present
blazes), amber ring vs cyan ring, faint worldline threads carrying the
continuity. The hydrodynamic impulse P = π(Γ₁R₁² + Γ₂R₂²) is conserved to
1e-9 through the whole dance: whenever one circle fattens, the other *must*
thin — you can check it by eye, exposure by exposure.

**Verified** (`dyson.py`): Kelvin self-induction speed vs closed form
(rel. err 1.7e-10); impulse drift 1.1e-9; energy drift 2.7e-9; 7 leapfrog
passes in t = 80.

## III. The Families of Loss — `final/loss_families_2560.png`

The **subtract-a-prime-divisor game** (live MO question, 2026): a token on
n ≥ 0; a move replaces n by n − p for any prime p | n; 0 and 1 are losing
terminals. We recomputed the full win/loss table to **2²⁹ = 536,870,912**
(C sieve, `game.c`) and matched the poster's data exactly: the same first
losses 1, 4, 8, 9, 14, 15, 22, 25, 26, 27, …, and the same census — even
losses split into **2p** (14,115,174), **4p** (6,775,434), **2^k** (19), and
exactly **114 wild** even losses that belong to no family, every one with at
most two distinct odd prime factors (his Question 1, confirmed
independently). We also noticed a clean implication in the data:
**L(4p) ⟹ L(2p)** for every prime p in range — every violet loss stands on
a cyan one.

**Chart**: the clock of doubling. One spiral thread carries all integers —
radius = log₂ n (one turn per octave), angle = frac(log₂ n) — so *doubling
is one step outward at the same angle*. The thread is inked where the game
says loss: garnet dashes for the odd carpet (each dash a maximal run of
consecutive odd losers — the gaps are exactly the odd winners, i.e. the
primes and the rare 3p/5p/wild-fed escapes: primes are the holes in the
carpet of loss); cyan sparks 2p; violet sparks 4p; steel radial chains
joining each 2p → 4p pair; the 19 powers of two as a golden spine ray; and
the 114 wild losses as ember stars. The final part-octave dissolves — the
edge of the computed universe.

---

## Also-ran ideas (see `IDEAS.md`)

Order-10 Graeco-Latin tapestry (Euler's revenge / Choi Seok-jeong);
y² + z² = x³ + 1 circle tunnel; "Mary's Spectrogram" (Mary's Room in Shannon
terms).

## The story (tweet-sized)

> Three engines that cannot lose what they carry: a map that hurls every
> point at infinity yet conserves all of measure; two smoke rings that trade
> radius forever but never the sum; a game whose defeats obey three laws —
> and 114 embers that obey nothing at all.

## What I learned about generative art this run

**When heavy tails eat the canvas, change clocks.** Linear time gave the
Boole map's rare giant excursions the whole frame (a corduroy wall, then a
black void); the honest fix wasn't exposure but a different clock — the
induced first-return map, one petal per breath. Same lesson at another
scale: ink must be calibrated to the geometry that actually receives it
(a line's pixel, not a ring's area — 41× apart here), or truth renders as
white-out. The chart is not a container for the data; it is the negotiation
between the data's law and the eye's budget.
