# Notes — WHAT MAKES IT THE SAME (run of 2026-09-19)

Three pictures about identity through change, seeded by the top question on Philosophy.SE this morning
(141876, *What makes a person the same person* — memories removed ten minutes at a time, a body whose cells are
all replaced) and three MathOverflow threads: 363950 *Curves on potatoes*, 515243 *partition a convex polygon into
the least number of mutually affine-equivalent pieces*, and (for the middle piece) the exact von Kármán street.

## 1. Curves on potatoes (MO 363950) — `potato.py`, `potato_census.py`, `render_potato.py`

Winkler's puzzle: *given two potatoes, draw a closed curve on each so that the two curves are identical as space
curves.* Solution: push one potato through the other; the two skins cross in a closed curve that lies on both.

**The two potatoes.** Star-shaped bodies |Mx| < ρ(Mx/|Mx|) with M = diag(1/a, 1/b, 1/c) and
ρ(u) = 1 + Σ ε_k exp(−(1 − u·d_k)/w_k) (four bumps for A, three for B; `make_bodies`). Convexity certificates
(`convexity.json`): every one of 40 000 Fibonacci-sphere surface samples is a vertex of its own convex hull
(hull deviation 0), and the Gaussian curvature on a 181×360 chart is positive everywhere
(A: K ∈ [0.195, 2.22]; B: K ∈ [0.258, 5.03]).

**The shared curves.** For a placement of B (translation τ, rotation R) the shared curves are the zero set of
g(u) = F_B(R^T(p_A(u) − τ)) on A's (θ, φ) chart (768×1536); `find_contours` gives the loops, and the number of
loops is the number of sign regions on the sphere minus one (union–find across the φ seam and the poles).
The hero moves B by **pure translation** around a tilted circle of radius 0.78 about A's centre (60 moments),
so every shared curve is a translate of itself: drawn on A and again on B in the same pigment, the two drawings
are exact translates on the page (orthographic camera). The coral loop is the pictured moment; B's silhouette
at that moment is the dashed ghost inside A. The film strip shows seven moments of the same passage.

**Census** (`potato_census.json`). 800 random placements (uniform rotation, |τ| uniform in [0.15, 1.9]):
669 cross; **668 of them share exactly one closed curve, one shares two.** Along the hero's arc the count is
1 at all 720 fine steps (no tangency: the loop stays one loop for the whole circuit — it is always "the same
curve"). Along a straight push (direction (1, 0.35, 0.55), 3.4 units) the count is 1 → 0 → 1: B is entirely
inside A for t ∈ (0.438, 0.560), 12 % of the passage, so the loop dies at a tangency and is reborn at another —
the line sweep's two families of loops (entry cap, exit cap) are the two lives of the curve.

*Remark.* Two convex surfaces can share many loops (a needle through a ball shares two; a ball through a
cube-with-rounded-corners shares six), so "one curve" is a property of these two potatoes' proportions, not a
theorem; with B nearly fitting inside A the second loop needs B to poke out of A on two sides at once.

## 2. The vortex street — `street.py`, `render_street.py`

The exact staggered two-row point-vortex street (rows y = ±h/2, spacing a, circulations ∓Γ, stagger a/2) at
von Kármán's stable ratio h/a = arccosh(√2)/π = 0.28055, regularised with Krasny's δ = 0.16 a:
for one periodic row, (u, v) = (Γ/2a)(−sinh κy′, sin κx′)/(cosh κy′ − cos κx′ + δ²), κ = 2π/a.
**Certificate**: the velocity induced at a top-row vortex by the whole bottom row is −0.3513 (predicted
−(Γ/2a) tanh(κh/2) = −0.3536; the 0.6 % gap is the δ-core), and its transverse component is 10⁻¹⁷: the street
translates rigidly at U_v = U − U_s = 0.646 U through a free stream U. Dye is released every 2 steps
(dt = 0.004) at 30 fixed points x = −1.6 (heights ∝ sign·|u|^{1.5}, denser near the axis) and every particle is
advected with RK4 in the lab frame until T = 11 (93 534 particles): the streaklines. Ink: the streamlines of
the street's own frame (ψ = U_s y − Σ ±(Γ/4π) log(cosh − cos + δ²)), through the nine stagnation points found
as minima of the street-frame speed, plus four inner loops per eye. Coral: the vortex centres.

## 3. Two pieces, one shape (MO 515243) — `affine.py`, `affine_cert.py`, `render_affine.py`

The question hopes that every convex polygon may be cut into **two** mutually affine-congruent pieces once the
pieces may be non-convex. It cannot, generically:

**Proposition (type constraints).** Let a convex n-gon Q be cut by a simple polygonal arc γ from boundary point
p to boundary point q with m genuine breakpoints (turning angle ≠ 0) into pieces P₁ and P₂ = φ(P₁), φ affine.
Then m is even, and the numbers k₁, k₂ of corners of Q strictly inside the two boundary arcs are equal — so
n is even if p, q are both corners or both interior to edges, and n is odd if exactly one of them is a corner.
*Proof.* Convexity/reflexivity of a vertex is affine-invariant. Each breakpoint of γ is convex in one piece and
reflex in the other; corners of Q, and p, q, are convex in every piece containing them. φ maps vertices to
vertices preserving type, so #reflex(P₁) = c = m − c = #reflex(P₂) gives m = 2c, and
#convex(P₁) = k₁ + 2 + c = k₂ + 2 + (m − c) gives k₁ = k₂. ∎

**Dimension count.** Unknowns: the cut (1 for each of p, q interior to an edge, 0 at a corner; 2 per breakpoint)
plus the six entries of φ; equations: two per vertex of P₁, i.e. 2(k₁ + 2 + m). In all three cases
unknowns − equations = **4 − n**. So triangles have a one-parameter family (every cevian: two triangles are
always affine twins), quadrilaterals finitely many (the diagonals; and edge-to-edge cuts into two
quadrilaterals), and for n ≥ 5 each combinatorial type imposes n − 4 ≥ 1 more conditions than it has freedoms:
**a generic convex n-gon, n ≥ 5, has no two-piece affine dissection, so its least number of mutually
affine-congruent pieces is ≥ 3 — and = 3 = n − 2 for a generic pentagon (the triangulation).** This answers
the thread's "I don't know if there can be convex n-gons for which n − 2 is the least possible": yes, every
generic pentagon. The exceptions are the polygons with an affine symmetry (mirror-symmetric, centrally
symmetric, and their affine images — a family of codimension 2 among pentagons).

**Transversality certificate** (`affine_cert.json`). At the regular pentagon's axis cut (m = 0, four-gons)
the residual map R(Q, cut, φ) ∈ ℝ⁸ over the 17 unknowns (10 polygon coordinates + 1 + 6) has Jacobian rank 8
(smallest singular value 0.89): the incidence variety is a smooth 9-manifold there, and its projection to the
10-dimensional space of pentagons has measure zero. (The m = 2, 4 "solutions" the search reported for the
regular pentagon are rank-deficient by exactly m: their breakpoints lie on the axis — the m = 0 cut in
disguise; a mirror-symmetric cut is necessarily straight, while a centrally symmetric one may zigzag.)
What is proved: the count and the type constraints; what is certified numerically: transversality at the
known solutions; what remains a HYPOTHESIS: that no component of the incidence variety is everywhere
rank-deficient in a way that projects onto an open set of pentagons — the search below is the evidence.

**Search** (`affine.py`, `affine_search.json`): all placements of p, q (corners or edges), m = 0…4,
all 2·n_v cyclic vertex correspondences, least-squares φ, Nelder–Mead over the cut with random restarts, then a
validity check (cut simple and interior). Residuals normalised by the polygon's diameter²:

| polygon | m = 0 | m = 2 | m = 4 |
|---|---|---|---|
| regular pentagon | 2.8e-32 (0.00 %) | 4.3e-22 (0.00 %) | 9.1e-21 (0.00 %) |
| affine regular pentagon | 2.6e-32 (0.00 %) | 4.2e-22 (0.00 %) | 1.4e-22 (0.00 %) |
| random pentagon | 1.6e-06 (0.13 %) | 3.0e-05 (0.55 %) | 2.5e-04 (1.57 %) |
| random pentagon 2 | 1.2e-05 (0.35 %) | 2.6e-04 (1.62 %) | 2.7e-04 (1.63 %) |
| random hexagon | 5.2e-03 (7.21 %) | 4.6e-03 (6.76 %) | 6.1e-03 (7.84 %) |

(cells: least residual / diameter², and √ of it as a percentage of the diameter — the r.m.s. vertex miss. Odd m were also run for the regular pentagons and gave 10⁻²⁵: a straight-angle breakpoint, i.e. the m = 0 cut.) For the generic pentagons the m = 0 problem is one-dimensional (the position of q on the edge opposite the chosen corner), so the floor was **certified by an exact scan**: a 999-point grid and a bounded refinement agree to three digits for every corner (random pentagon: 2.8e-6, 3.9e-5, 2.2e-4, 2.0e-3, 2.9e-3 for its five corners; the second: 1.2e-5 … 4.0e-3). The misses are small because the affine group is large (six parameters against eight equations leaves one scalar condition), but they are positive minima, not unconverged zeros. As area: the symmetric difference between the image of piece 1 and piece 2 at the best cut is 0.13 % and 0.29 % of the pentagon’s area (the two generic pentagons) and 4.6 % for the generic hexagon (count 4 − n = −2: two conditions short instead of one).

**HYPOTHESIS (least number of pieces).** For a generic convex n-gon the least number of mutually
affine-congruent pieces is n − 2 (the triangulation is optimal) — the same count for k pieces of v vertices
each gives 6(k − 1) + (cut parameters) − 2v(k − 1) freedoms, which is negative for every k < n − 2 in the
few types I counted (e.g. a hexagon into three quadrilaterals from an interior point: 14 − 16 = −2).
What it would take: enumerate the combinatorial types of k-piece dissections and check the count for each.

## 4. The sorites as Morse theory — `render_sorites.py`

The straight push (direction −(1, 0.35, 0.55)/|·|, 3.4 units, 72 moments). The shared loop is one loop at every moment before
t = 0.4407 and after t = 0.5627 (bisection to 1e-12 on 'the chart field changes sign'), and no loop between: the smaller body is
entirely inside the larger. The death point is where the smaller body's trailing surface is tangent to the larger from inside
(argmin |g| at the tangency moment): (0.99, 0.17, 0.25), on the visible face; the rebirth point (−0.86, −0.45, −0.13) is on the far
side. Between two tangencies the loop's isotopy class never changes (a regular value of a smooth family), so 'the same curve' has a
precise meaning and a precise end.

## 5. The mirage as a fold — `mirage.py`, `render_mirage.py`, `mirage_cert.json`

Index n(z) = 1 + ε(1 − e^{−z/h}), ε = 0.05, h = 0.30 (a real inferior mirage has ε ~ 10⁻⁴ over a few metres; the geometry is
identical after rescaling x by ε^{−1/2}). Rays by RK4 on dr/ds = p, dp/ds = n∇n (|p| = n), ds = 0.01, absorbed at the ground.
From the tower's top (height 1.62) 260 rays with launch angles in [−0.40, 0.16]: 51 turn, 23 strike the ground. The envelope of
the turned family is the fold; its first point (first crossing of neighbouring rays) is at x = 7.13, and the eye at (12, 1.1)
lies inside the fold. The view: for every tower height, all rays arriving at the eye (sign changes of z(L) − z_eye across the
launch angle, 1400 angles): tower points above 0.771 arrive twice (erect and inverted), below it never — the fold height by
bisection. The two images join at the fold line, where the images pile up (a fold caustic is bright), and beneath the inverted
top there is only sky.
