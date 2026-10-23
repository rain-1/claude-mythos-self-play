# Fair 3-partitions (equal area and equal perimeter, convex pieces). MO 516282

All shapes are scaled to area π. "Y" means an interior junction p with three segments to the boundary (a T-junction is the case where one angle is 180°). "Chords" means two disjoint chords, giving cap / middle / cap.
Three convex pieces always meet in one of these two ways. Either two segments are disjoint or share a boundary endpoint (a "V"), or there is a single junction p. A junction on the boundary reduces to the V case.

## Q1: the unit disc. Answer: NO (computer-assisted proof)

**Reduction (Kepler).** Put p=(r,0) with 0≤r<1 and boundary points A_i=(cos t_i, sin t_i). By the shoelace formula, piece i has area
½[(t_{i+1}-t_i) + r(sin t_i - sin t_{i+1})].
So the pieces have equal area **iff the "mean anomalies" M_i = t_i - r sin t_i are equally spaced**, M_i = c + 2πi/3. Each t_i is then the Kepler inverse of M_i.
The equal-perimeter conditions become Q_0=Q_1=Q_2, where Q_i = u(t_{i+1}) + v(t_i), u = d + r sin t, v = d - r sin t and d = |p - A(t)|.
What remains is **2 equations G(r,c)=0 in 2 unknowns**. The fundamental domain is r∈[0,1] and c∈[0,π/3], because shifting c by 2π/3 only relabels the pieces and c→-c is the mirror image. The lines c=0 and c=π/3 are exactly the mirror-symmetric configurations.

**Theorem (computer-assisted).** Up to rotation and reflection, the disc has exactly two Y solutions:
1. the 120° partition (r=0), whose three pieces are congruent;
2. the mirror partition (r=r*, c=0), where pieces 0 and 2 are mirror images.

The mirror partition is the unique solution of
  t - r sin t = 2π/3,  √(1+r²-2r cos t) = 1 - r + 3 r sin t:
- r* = 0.60826002684141148833012449973881568919
- t₁ = 2.47194706162488913187213632975028330677
- arcs (t₁, 2π-2t₁, t₁) = (2.471947061624889…, 1.339291183929808213181014107058439…, 2.471947061624889…)
- segment lengths 1-r* = 0.391739973158588511669875500261 and d = 1.52439585085366943036099772295 (twice)
- common perimeter 4.38808288563714707390300955296; the 120° partition has perimeter 2+2π/3 = 4.0944
- angles at p: 155.9719990463° (twice) and 48.0560019073°, so all pieces are convex.

`mp.identify` found no closed form for r*, t₁, d or the perimeter (basis π, √3). **CONJ:** these numbers have no elementary closed form.

**Proof method** (`disc_certify.py`, runs in 0.3 s):
- Branch-and-bound with vectorised interval arithmetic (`iv.py`, outward rounding via nextafter) over r∈[0,1], c∈[-0.05, π/3+0.05].
- Kepler inverse: E(M,r) increases in M and is monotone in r for fixed M. The enclosure is built from the corner values and then checked by evaluating the Kepler residual's sign in interval arithmetic.
- Near r=0: G(0,c)≡0, so boxes touching r=0 use the mean-value form G/r ∈ ∂_rG([0,r_hi],c). This is nonzero because the leading term is r·Re[e^{ic}K ωⁱ] with K≠0, which holds since ω=e^{2πi/3}≠i. So no other solutions accumulate at the centre.
- Results: 6176 boxes were examined and 57 remain undecided. All 57 lie in a box of half-width 5e-3 around (r*,0). On that box a **Krawczyk test** succeeds (K(B)⊂int B), so the box contains exactly one zero, and it is the mirror solution on c=0.
- r=1 (junction on the boundary) is inside the domain and is excluded too.
- Degenerate cases, by hand:
  - two disjoint chords: the caps have equal area, so they have equal arcs and are congruent. In fact no fair chord pair exists at all: the cap arc α solves α - sin α = 2π/3 (α = 2.6053), giving cap perimeter 4.533 against middle-piece perimeter 4.929;
  - V (two chords from one boundary point): the same caps and the same mismatch, so no solution.

Status: rigorous up to trusting libm sin/cos/sqrt to a couple of ulp, which the code pads for. The code has not been independently checked. **I found no conceptual proof that every solution is mirror-symmetric.** The Kepler reduction above is the best structural handle I have.

## Q2: other convex regions. Answer: generically YES; the disc looks exceptional

**Why.** For a general region a Y partition has 5 unknowns (p and three boundary parameters) and 4 equations, so the fair Y partitions form **1-parameter families (closed curves)**.
For the disc each curve is just a rotation orbit, so the pieces never change shape. That is why the disc fails.
For any shape with only finitely many symmetries, moving along a curve really changes the pieces. Having a congruent pair is a codimension-1 event, so it happens only at isolated points of a curve.
There is one exception: a shape with 3-fold rotational symmetry has a whole family with p at the centre and endpoints 120° apart, in which all three pieces are congruent.
Fair chord pairs are isolated solutions (4 equations, 4 unknowns).

**Method** (`shapes.py`, `fair.py`, `run_all.py`, `analyze.py`):
- Boundaries are exact: polygons, circular arcs, and ellipses via `ellipeinc`.
- Solutions are found by multistart least squares and then traced by pseudo-arclength continuation. The Jacobian is one-sided at polygon vertices, and an explicit step crosses a vertex when an endpoint passes one.
- Chord pairs come from 300 random Newton starts.
- Congruence test: compare piece invariants (inertia eigenvalues, max distance from centroid, list of corner turning angles), with tolerance 1e-5. "Margin" is the smallest, over the three pairs, of the largest invariant difference.

| shape | Y families (closed, % convex) | chord-pair solutions | non-congruent fair partition? | best example (angles at p; margin) |
|---|---|---|---|---|
| disc | 2: centre orbit and mirror orbit, every point has a congruent pair | 0 | **no (proved)** | none |
| square | 2 (60%, 100%) | 2 (three strips: all congruent) | **yes** | p=(0.223893316962, 1.264936959538); 39.2/172.3/148.5°; 0.097 |
| rect 1.5:1 | at least 2 traced curves (tracing did not close); convex arcs are short | 2 (strips) | **yes** | 180.0/26.5/153.6°; 0.053 |
| rect 2:1 | at least 4 (not closed); convex arcs tiny | 2 (strips) | **yes** | 19.3/161.3/179.4°; 0.023 |
| rect 3:1 | several; about 1% convex | 2 (strips) | **yes** (nearly a T) | 174.0/12.9/173.1°; 0.0021 (corner sets clearly differ) |
| equilateral triangle | 4: one all-congruent centre family + 3 equivalent ones (20% convex) | 3 (caps congruent) | **yes** | 164.2/147.7/48.1°; 0.069 |
| regular pentagon | 2 (100%, 100%) | 0 | **yes** | 41.5/158.4/160.2°; 0.034 |
| regular hexagon | 2: one non-congruent, one all-congruent centre family | 0 | **yes** | 45.1/172.2/142.7°; 0.068 |
| ellipse b/a=0.95 | 2 (100%), deformations of the disc's two orbits | 0 | **yes** | 148.5/48.0/163.4°; 0.0071 |
| ellipse b/a=0.8 | 2 (52%) | 0 | **yes** | 0.028 |
| ellipse b/a=0.5 | 2 physical (7%) | 0 | **yes** | 0.011 |
| stadium (square with two half-discs) | 3 (0–7%) | 0 | **yes** | 21.7/158.3/180.0°; 0.055 |
| Reuleaux triangle | 2: one all-congruent centre family + one with 43% convex | 0 | **yes** | 35.3/150.4/174.3°; 0.079 |
| half-disc | 1 (13% convex) | 2: one mirror-symmetric, **one pairwise non-congruent** | **yes** (both Y and chords) | see below |

**Cleanest example: the half-disc, using only two chords.** Take the unit half-disc y≥0. Cut the right piece with the chord from (a,0) to e^{iθ₁}, and the left piece with the chord from (b,0) to e^{iθ₂}. Solved with mpmath (`halfdisc_mp.py`, residual 1e-41):
- a = 0.043297629742660482938990943395
- b = -0.316872145386923825510361874410
- θ₁ = 1.085495811744436781645044930612
- θ₂ = 1.784747780810107883537809560881
- each piece has area π/6 and perimeter 3.022749165199282417778408487

Each piece contains exactly one unit-radius arc, of lengths 1.08550, 0.69925 and 1.35684. These differ, so the three pieces are **pairwise non-congruent**; this argument is rigorous. Pieces from two chords are automatically convex.

**Square, rigorous by corner data.** The best square example (`best_noncongruent_Y` in the JSON) has pieces with 4, 5 and 4 corners. The two quadrilaterals have different interior angles: the turning angle sets are {46.57, 82.66, 90, 140.76} and {31.53, 90, 105.05, 133.43}. So no two pieces are congruent.

Observations:
- Elongated shapes (rectangles at 1.5:1 and beyond, ellipse 0.5, stadium) still have convex non-congruent fair Y partitions, but only near T-junctions. Most of each traced curve is non-convex there.
- For every 3-fold symmetric shape, the all-congruent centre family exists and has convex fraction 100%.

**CONJ:** among convex regions, the disc is the only one with no fair convex 3-partition into pairwise non-congruent pieces. Evidence: every one of the 13 other test shapes has one, including the ellipse b/a=0.95, so arbitrarily small deformations of the disc already break it.

**What is certified and what is numerical:**
- Q1 (disc): computer-assisted interval proof.
- Half-disc chord example: 40-digit Newton, plus a rigorous non-congruence argument (unit-arc lengths).
- Square example: Newton residual 2e-15 (well conditioned), with non-congruence from corner counts and angles.
- Everything else in Q2 is numerical.
- **"All solutions" for Q2 is not certified.** Families were found by multistart (≥150 starts) and continuation. For the 1.5:1 and 2:1 rectangles the traced curves wind repeatedly in the boundary parameter without closing within 5000 steps, so the list of families there may be incomplete or duplicated.
- Counts of congruent-pair points along curves come from sign changes of an inertia difference and are approximate.

## Files
- `disc_certify.py` + `iv.py`: the disc proof.
- `disc_mp.py`: 40-digit mirror solution.
- `disc_kepler.py`: the reduced equations.
- `halfdisc_mp.py`: the half-disc non-congruent chord partition.
- `shapes.py`, `fair.py`, `run_all.py`, `analyze.py`, `make_json.py`: the Q2 pipeline. Raw traces are in `raw_all.pkl`; logs in `run_all2.log` and `analyze.log`.
- `partitions.json`: per shape, the boundary (400 points), the traced Y families (junction path plus representative solutions, including congruent-pair points), chord solutions and `best_noncongruent_Y`. Each solution gives junction and endpoints (≥13 digits), angles, areas, perimeters, piece polygons, `congruent_pairs`, `pairwise_noncongruent` and invariants. `disc.certified_Y_solutions` holds the two disc solutions to 20–35 digits.
