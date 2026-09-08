# Bunimovich's mushroom — the trap theorem, and how long the free ones imitate the trapped

**Geometry** (`mushroom.py`). Cap: half-disc of radius R = 1 (y ≥ 0) centred at the origin. Stem:
rectangle |x| ≤ r = 1/2, −h ≤ y ≤ 0 with h = 1. Specular reflection, vectorised over thousands of
particles; the chord rasteriser is `rast.c` (bilinear splats along each chord, ~40 M samples/s).

## The trap theorem (Bunimovich 2001), as drawn
An orbit inside the cap has an invariant: the distance ρ = |p × v| of its current line from the cap's
centre (its caustic radius). Reflection off the arc preserves ρ (a disc billiard is integrable) and
reflection off the flat wall y = 0 preserves it too, because reflecting the half-disc in y = 0 gives the
full disc — the wall bounce is the unfolding. A chord at distance ρ from the origin crosses y = 0 at
|x| = ρ/|sin φ| ≥ ρ, so if **ρ ≥ r the chord never crosses the mouth**: the orbit stays in the cap forever
(integrable, "happy"). If ρ < r, the chords' feet on y = 0 are carried by the rotation of the unfolded disc
(angle 2·arccos(ρ/R) per bounce), which is dense for irrational rotation number, so the foot eventually
lands in |x| < r and the orbit falls into the stem: free — and chaotic thereafter.

*Certificates in the picture's JSON* (`mush_hero2_4096_cert.json`): all 16 trapped orbits (ρ from 0.502
to 0.996) stayed in the cap for all 600 chords; the invariant ρ drifted by < 3·10⁻¹⁴ over the run.

## Stickiness: free orbits that look trapped
Launch an orbit in the cap with ρ = r(1 − ε). It is free by the theorem, but it must wait for the
rotation to bring a chord's foot inside the mouth, and for ε small that takes ~1/ε bounces. The sheet's
warm orbits use ε = 3·10⁻³ … 0.25 (eight values, geometric); for each ε, 64 launch phases were tried
and the phase with the **longest first sojourn** kept — a designed demonstration, declared as such.
First sojourns of the eight (chords before the first fall): see the certificate; the ε = 3·10⁻³ orbit
circles for hundreds of chords, drawing an inner ring just inside the coral circle before it drops.

**Survival law** (`survival.py`, `survival.json`): 24,000 free orbits from the stem, 20,000 bounces each
(4.8·10⁸ chords), every completed cap-sojourn recorded: 86,256,663 sojourns, mean length 2.80,
longest 12,920 (in units of R).
Survival function P(τ > t) of the sojourn length τ (path length, R = 1):

| t | 2.6 | 6.9 | 18 | 47 | 123 | 323 | 845 | 2212 | 5792 |
|---|---|---|---|---|---|---|---|---|---|
| P(τ > t) | 0.48 | 2.4e−2 | 2.8e−3 | 5.1e−4 | 9.2e−5 | 1.5e−5 | 2.1e−6 | 2.4e−7 | 2.3e−8 |

Local log-log slope: −1.9 at t ≈ 18, −1.7 at 47, −1.8 at 123, −2.0 at 323, −2.1 at 845, −2.3 at 2212
(the last decade is starved: ~10 events). So **P(τ > t) ≈ C·t⁻²** over 20 < t < 1000 for r/R = 1/2.

Why not the textbook 1/t? A heuristic: entering orbits have ρ = |x cos θ| (foot x, angle θ from the
vertical); the flux measure cos θ dx dθ gives P(r − ρ < ε) ∝ ε^{3/2}, and the wait is ~1/ε, which would
predict P(τ > t) ∝ t^{−3/2}. The measured −2 is steeper. **Note the coincidence r/R = 1/2 = cos(π/3):**
the theorem's circle ρ = r is exactly the caustic of the inscribed equilateral triangle, a period-3
orbit of the disc, so near ρ = r the rotation number is 1/3 and the foot returns near the same three
places — the escape is governed by the slow drift of a nearly period-3 orbit, not by a generic rotation.
A control run with r/R = 0.45 (`survival_r045.json`, same budget) tests whether the exponent moves.

**Control result (r/R = 0.45, 83.1 M sojourns, same 4.8·10⁸ chords):** the tail is far lighter —
longest sojourn 1,627 (vs 12,920), P(τ > 43) = 2.0·10⁻⁴ (vs 5.1·10⁻⁴ at t = 47), P(τ > 193) = 1.6·10⁻⁶
(vs 1.5·10⁻⁵ at t = 323), local slopes −2.6 … −3.4 over 10 < t < 400 (vs −1.7 … −2.0). So moving the
mouth off the period-3 caustic makes the free orbits' imitation of trapped ones roughly one power of t
shorter-lived: **the trap's edge is stickiest when it coincides with a periodic caustic.** The
hypothesis above stands as a hypothesis (two points, r/R = 1/2 and 0.45); the next runs are
r/R = cos(π/4) = 0.7071, cos(π/5) = 0.8090 and a generic 0.6.

**Hypothesis to play with:** for r/R = cos(π/q) (q = 3, 4, 5, …) the mouth radius coincides with the
caustic of a period-q disc orbit; the survival exponent of cap sojourns then differs from the generic
value, and the generic value is 3/2 (from the flux measure) rather than 1. The engine can test q = 3, 4
and a generic r in an hour each.
