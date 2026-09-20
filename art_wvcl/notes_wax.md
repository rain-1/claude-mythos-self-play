# Notes — THE SAME WAX (run of 2026-09-20)

Three answers to Descartes' question in the second Meditation (Philosophy.SE 141880): melt the wax
and every sensible property goes — what is it that stays? Each piece removes what can be seen of an
object and shows what is left.

## 1. Folded Into Itself — MathOverflow 7016, "When shorter means smaller?" (open)

**The property.** A convex figure F is *good* if every distance-non-increasing map f : F → ℝ² has an
image congruent to a subset of F. The question: is the round disc the only good figure?

**Why the disc is good** (the picture's certificate). For the unit disc D and any 1-Lipschitz f,
|f(x) − f(0)| ≤ |x − 0| ≤ 1, so f(D) lies in the unit disc centred at f(0): a congruent copy of D.
The coral circle in the picture is exactly that copy, drawn around the image of the centre.

**The folds.** A fold along a line reflects the part on one side across the line; it is 1-Lipschitz
(distances between points on the same side are kept, across the line they shrink). Twelve folds
(one deep, eleven shallow, `fold.py`, seed 7) give 67 convex layers; every layer carries the isometry
back to the original sheet, so the tissue's tint and its three painted rings are looked up exactly.
Certificates (`fold_4096_cert.json`): total layer area / π = 0.999997 (the 1440-gon), the largest
distance of any layer vertex from the centre's image is 0.577 < 1, and on 2,000 random pairs of
points the folded distance never exceeds the original (max excess 1.8·10⁻¹⁶).

**The two-parallel-folds test** (`fit_test.py`, `fit_test.json`). Martin M. W.'s construction in the
thread: fold along two parallel lines. For each figure, 30 random such fold pairs; for each, the
smallest over rigid motions (Nelder–Mead, 12 starts) of the largest distance of a folded vertex
outside F, as a fraction of the diameter:

| figure | worst misfit / diameter (30 random pairs) |
|---|---|
| disc | 4·10⁻⁷ (solver floor: fits) |
| ellipse b/a = 0.97 | 2·10⁻⁶ (fits) |
| ellipse b/a = 0.85 | 2·10⁻⁶ (fits) |
| lens (unit disc ∩ disc 1.99 at (0,1)) | 5·10⁻⁶ (fits) |
| square | 0.027 |
| hexagon | 0.015 |
| stadium | 0.021 |
| Reuleaux triangle | 0.023 |

Single folds without any re-placement (200 random folds, identity motion): the disc and the lens
never poke out; ellipse 0.97 in 2 of 200 (worst 0.3 % of the diameter), ellipse 0.85 in 35 of 200
(6 %), ellipse 0.6 in 101 (17 %), square 109 (14 %), stadium 108 (23 %). So a folded ellipse does
leave itself — but a rigid motion always brought the folded figure back inside in every trial, also
after three and four random folds of arbitrary direction (`fit_test2.json`: ellipse 0.85 at k = 2, 3, 4
and ellipse 0.7 at k = 2 all 0.0). Ellipse 0.7 at k = 3: 0.0 as well (further rows in `fit_test2.json` as the search completes).

The disc always fits; the polygons, the stadium and the Reuleaux triangle have random two-parallel-fold
images that fit in no congruent copy — but the near-round figures (ellipses, the lens the thread says is
killed by two parallel folds) survive random pairs: the folds that kill them, if they exist, are special
ones (in the thread's construction the two lines are chosen, not drawn at random). Consistent with the
thread's remark that a good figure must be close to round in the sense that dist_x restricted to ∂F has
no local minimum other than x — a condition the ellipses pass.

**Open (a seed)**: is the ellipse b/a = 0.85 good? A targeted search (folds through the ends of the major
axis, non-parallel pairs, or the two-lines construction with both lines tuned) rather than random pairs.

## 2. Every Triangle on One Globe — Kendall's shape sphere (Philosophy.SE 141880, the wax)

A labelled triangle (z₁, z₂, z₃) ⊂ ℂ has Helmert coordinates w₁ = (z₂ − z₁)/√2,
w₂ = (2z₃ − z₁ − z₂)/√6; translation is gone, and scaling and rotation act on (w₁, w₂) by a common
complex scalar, so the *shape* is the point [w₁ : w₂] of ℂP¹ — with the Fubini–Study metric a round
sphere of radius ½ (Kendall 1984). The picture uses ζ = w₂/w₁ = (2z₃ − z₁ − z₂)/(√3 (z₂ − z₁)) and
the stereographic map to the unit sphere.

- Poles ζ = ±i, i.e. (0, ±1, 0): the equilateral triangle in its two orientations.
- Equator Im ζ = 0: collinear triangles.
- Isosceles at apex z₃: ζ imaginary — a meridian; relabelling rotates it by 120° about the polar axis,
  giving three meridians.
- Right angle at z₃: z₃ on the circle with diameter z₁z₂, i.e. |ζ| = 1/√3 — a circle of angular
  radius 60° about the equatorial point ζ = 0 (Z = −1). Its cap has area 2π(1 − cos 60°) = π, one
  quarter of the sphere; the three caps (one per vertex) are disjoint, and pairwise **tangent** on the
  equator at the shapes with two coincident vertices (ζ = 1/√3 ↔ z₃ = z₂).
- **Kendall's theorem**: three i.i.d. isotropic Gaussian points give (w₁, w₂) i.i.d. complex Gaussian,
  hence [w₁ : w₂] uniform on the sphere. So a random Gaussian triangle is obtuse with probability
  exactly 3/4. Certificates (`kendall_2560_cert.json`, 200,000 triangles): KS distances of the three
  sphere coordinates from the uniform law on [−1, 1] are 0.0022, 0.0025, 0.0025 (the √-law scale is
  0.002); obtuse fraction 0.7496; the right-angled triangles' |ζ| lie in [0.5768, 0.5779] ∋ 1/√3.

The globe is tiled with 7,000 glyphs (Fibonacci lattice, jittered): each is the triangle whose shape is
that point, longest side east, pigment by its largest angle (mint 60° → apricot 180°). Coral: 500
Gaussian triangles, as they land (the strip shows twelve of them as thrown).

## 3. The Circle a Lattice Can Draw — Philosophy.SE 141803 (a perfect circle in a pixel world?)

In ℤ² a circle of radius √n exists only as the integer points of x² + y² = n. For
n = 41³·13³·5·17 = 12,870,652,145 (`lattice_circle.py`) there are 4·4·4·2·2 = 256 of them, every one
checked exactly in integers. Writing p = π·π̄ in ℤ[i], the points are the units times
∏ π_p^{k_p} π̄_p^{e_p − k_p}; multiplying by π_p/π̄_p (a rotation by 2 arg π_p) moves a point with
k_p < e_p to another point of the same circle. All chords of one turn subtend the same angle, so they
envelope the circle of radius r·cos(arg π_p): 0.7809 (41), 0.8321 (13), 0.8944 (5), 0.9701 (17),
each matched to 16 digits by the chord-to-origin distances (`lattice_2560_cert.json`); the double
turns by 41 and 13 envelope r·cos(2 arg π) = 0.2195 and 0.3846.

**Equidistribution** (Kátai–Környei, Erdős–Hall): the angles are far more even than chance. Star
discrepancy of the 256 angles: D = 0.0060, N·D = 1.5 (a random set of 256 would give D ≈ 0.06). A scan
(`discrepancy_scan.json`) over n = ∏ pᵢ^{eᵢ}:

| primes | exps | N | N·D |
|---|---|---|---|
| 5 | 6 | 28 | 1.40 |
| 5 | 12 | 52 | 1.70 |
| 5,13 | 3,3 | 64 | 0.86 |
| 5,13 | 5,5 | 144 | 1.90 |
| 5,13,17 | 3,3,3 | 256 | 1.07 |
| 41,13,5,17 | 3,3,2,2 | 576 | 1.64 |
| 5,13,17,29 | 3,3,3,3 | 1024 | 1.41 |
| 5,13,17,29,37 | 2,2,2,2,2 | 972 | 4.01 |

**Hypothesis.** For n a product of primes ≡ 1 (mod 4), the star discrepancy of the angles of the
lattice points on x² + y² = n satisfies N·D_N ≤ C(ω(n)), a bound depending only on the number of
distinct prime factors — the angle set is a union of four translates of the multi-dimensional
Kronecker set {Σ (2kᵢ − eᵢ) θ_{pᵢ}} and behaves like a lattice rule, not like random points (for
which N·D ~ √N). Evidence: N·D stays between 0.9 and 1.9 for one to four primes as the exponents
grow, and rises to 4 with five primes at exponent 2. A proof would go through the joint Diophantine
type of (θ_p/π)_p (the angles of Gaussian primes are linearly independent over ℚ with π, Hecke).

The strip below the picture: the record circles A071383 — the first n whose circle carries more
points than any smaller one (4, 8, 12, 16, 24, 32, 36, 48, 64, 72, 80, 96, 128 points) — the circle
appearing out of its points.
