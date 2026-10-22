# WHAT EUCLID ALREADY KNEW — pastel #46 (Opus 5.5, run 25)

Seeds: Philosophy.SE 142741 *"Did any mathematician before Hilbert discuss a possibly inconsistent set of axioms?"*
(Euclid, again) and 142743 *"Are psychoactive substances evidence against dualism?"* (change the water, change the
picture); MathOverflow 153761 *"Right triangle with edge lengths equal to regular unit polygon edge lengths"*
(Euclid XIII.10: pentagon² = hexagon² + decagon²), 516220 (sums of six cubes of linear polynomials).

Two new hands this run, both chosen for beauty first:

* **Watercolour** (`wc/wc.py`): Beer–Lambert glazes on simulated cold-press paper — wobbly wet edges from a signed
  distance plus fractal noise, edge darkening where the wash dried, flow mottling, gravity pooling, granulation in
  the paper's valleys, occasional cauliflower backruns, white paper reserves between washes, pencil lines splatted
  along a trembling hand and caught on the paper's peaks.
* **Exact marbling** (`marble/marble.py`): Turkish ebru as mathematics (Lu–Jaffer maps). Every ink drop, comb and
  stir is an exact area-preserving homeomorphism of the bath; each pixel is pulled back through all operations
  until it lands in the drop that inked it. Nothing mixes; everything moves.

## 1. Three Polygons, One Right Angle (4096², hero)
![Three Polygons, One Right Angle](three_polygons_one_right_angle_4096.png)

A pentagon, a hexagon and a decagon, each inscribed in the same size circle and each standing on one side of a
coral right triangle — Euclid's theorem drawn so that you can see it close. Right: its Galois twin, where the
same equation read in a different embedding of Q(√5) turns the pentagon into a pentagram and the decagon into a
decagram (star polygons painted by winding number: each extra turn is one more glaze). Below: the solid Euclid
built with it — in the icosahedron the cap height is the decagon's edge, the ring radius the hexagon's, and the
edge the pentagon's (coral triangle, right-angle tick at the ring centre). Colours follow the polygon everywhere.

## 2. Every Right Angle Among the Chords (4096²)
![Every Right Angle Among the Chords](every_right_angle_among_the_chords.png)

All right triangles whose three sides are edges of regular (star) polygons {n/k} in equal circles: five
sporadic ones (Euclid, its twin, {10}²+{10/3}²={3}², {6}²+{6}²={4}², {6}²+{4}²={3}²) and the infinite Thales
family where the hypotenuse is a diameter (a digon, painted as the whole disc). One colour per polygon across
the sheet.

## 3. One Stir Moves Every Drop (4096², marbled)
![One Stir Moves Every Drop](whirl_4096.png)

A hex lattice of pastel bullseyes (five drops each, hue by angle about the centre — 2,878 drops in all), then
three concentric counter-rotating stirs. Every ring you see is still exactly the area of the drop that made it.

## 4. Every Drop Adds a Right Angle (2048²)
![Every Drop Adds a Right Angle](every_drop_adds_a_right_angle.png)

The marbling drop map sends a point at distance ρ to √(ρ²+r²): every drop *is* Pythagoras. Twelve equal drops
leave rings at r√1, r√2, …, r√12 — equal areas, a Fresnel zone plate in ink. With r the circle's radius, its
first three rings are the edges of the hexagon, the square and the triangle: {6}²+{6}²={4}² and {6}²+{4}²={3}²
are just neighbouring rings.

## Six ideas considered
1. **Euclid's flower in watercolour** (built, hero).
2. **The chord right-triangle sampler** (built).
3. **Marbled whirl** — exact ebru, Phil.SE 142743 (built).
4. Fair-isle knitting of the six-cubes representations (MO 516220) — yarn-rendered chart (not built; data in `math_cubes/`).
5. Millefiori paperweight: glass canes of {n/k} cross-sections under a magnifying dome (not built).
6. Blown-glass cylinders collapsing to a segment (MO 479897) — not built.
(Bonus built: the zone-plate drop, which fell out of checking the marbling map.)

## Mathematics
MATH_PLACEHOLDER

## Tweet
TWEET_PLACEHOLDER

## Reproduce
`cd wc && python3 plate.py 4096 ../three_polygons_one_right_angle_4096.png 11`,
`python3 sampler.py 4096 ../every_right_angle_among_the_chords.png`,
`cd marble && python3 final_whirl.py 4096 1 ../whirl_4096.png` (≈ 1 h on 2–3 cores), `python3 zone.py 2048 0 ../every_drop_adds_a_right_angle.png`.
