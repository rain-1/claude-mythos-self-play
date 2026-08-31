# THREE FATES OF A WANDERER — a second trio (same day)

The first triptych of this run leaned on sequels; the user asked for new
ground, so: three subjects this practice has never touched — dynamical
knots, exact planar dynamics, prime-constellation geography. Return knotted;
drift unbounded; stranded by water.

## 1. WHAT THE STORM KEEPS TIED — `lorenz_4096.png` (4096², hero)

The certified periodic skeleton of the Lorenz attractor: 53 unstable
periodic orbits of symbol length ≤ 8 (complete through length 5; the
one-lobe loops L and R do not exist at ρ=28 — they died in the subcritical
Hopf at ρ≈24.74), found by close-return harvest + Newton shooting on the
z-max section, residuals < 1e-10. T(LR) = 1.558652 and T(LLR) = 2.305907
match Viswanath's published periods to the digit. The flow's mirror symmetry
appears as exact period degeneracy of mirror words. All 1378 pairwise
linking numbers computed by signed crossings with two-projection integer
agreement: min 1, max 16, every one positive — Birman–Williams' "Lorenz
links are positive," verified in the data. Rotation number orders the
orbits radially: the shells of the butterfly are the words.

## 2. THE ORBIT THAT WOULD NOT SETTLE — `outer_2560.png` (2560²)

Outer billiards around the golden kite, every orbit in exact (1/16)ℤ[√5]
integer arithmetic (the map is subtraction-only). Fates are certificates:
207/305 seeds provably periodic (exact state recurrence; periods 3 to
53,622), 23 wanderers with no repeated state in 60,000 steps — the farthest
carried to |P| = 239 — and 75 seeds that struck a singular ray exactly
(vanishing integer cross product). Schwartz's Moser–Neumann theorem (2007)
says irrational kites shed unbounded orbits; here is the kingdom of the
settled and the ice-trails of those who left.

## 3. THE WIDENING WATER — `moats_2560.png` (2560²)

The Gaussian moat problem, walked: sieve of 33M quadrant Gaussian primes to
|z| = 25,000 (C engine, verified against an independent full-plane BFS,
exact agreement). From 1+i, the step-√2 walker strands on 27 stones at
|z| ≤ 11.7; step 2 dies at 45.3; step 2√2 at 93.5; step 4 exhausts a
complete 695,275-stone continent ending at |z| = 4,312.6; the step-√26
walker crosses our whole horizon still going. Log-radius geography: the
golden filigree of the first islands, the ember continent with its fringed
coast, the teal open water, four ice moat-rings at the exact death radii.

## The story (tweet-sized)

One traveler came home and found his footprints had tied a knot that can
never be untied kindly. One circled a golden kite ten thousand times,
politely, exactly — and was never seen again. One hopped stone to stone
until the stones gave out, and stood there, counting the water.

## Craft carried forward

An exact-arithmetic dynamical census turns "looks periodic" into theorems —
integer subtraction maps (outer billiards in a quadratic field) give free
certificates for every fate, including the map's own singularities. And a
weak hash on symmetric integer states WILL collide on the symmetry orbit
(negated states): add a mixing finalizer and verify candidate periods by
shift-consistency before believing them.
