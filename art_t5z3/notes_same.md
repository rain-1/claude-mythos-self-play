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
(`cache/convexity.json`): every one of 40 000 Fibonacci-sphere surface samples is a vertex of its own convex hull
(hull deviation 0), and the Gaussian curvature on a 181×360 chart is positive everywhere
(A: K ∈ [0.195, 2.22]; B: K ∈ [0.258, 5.03]).

**The shared curves.** For a placement of B (translation τ, rotation R) the shared curves are the zero set of
g(u) = F_B(R^T(p_A(u) − τ)) on A's (θ, φ) chart (768×1536); `find_contours` gives the loops, and the number of
loops is the number of sign regions on the sphere minus one (union–find across the φ seam and the poles).
The hero moves B by **pure translation** around a tilted circle of radius 0.78 about A's centre (60 moments),
so every shared curve is a translate of itself: drawn on A and again on B in the same pigment, the two drawings
are exact translates on the page (orthographic camera). The coral loop is the pictured moment; B's silhouette
at that moment is the dashed ghost inside A. The film strip shows seven moments of the same passage.

**Census** (`cache/potato_census.json`). 800 random placements (uniform rotation, |τ| uniform in [0.15, 1.9]):
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

**Transversality certificate** (`cache/affine_cert.json`). At the regular pentagon's axis cut (m = 0, four-gons)
the residual map R(Q, cut, φ) ∈ ℝ⁸ over the 17 unknowns (10 polygon coordinates + 1 + 6) has Jacobian rank 8
(smallest singular value 0.89): the incidence variety is a smooth 9-manifold there, and its projection to the
10-dimensional space of pentagons has measure zero. (The m = 2, 4 "solutions" the search reported for the
regular pentagon are rank-deficient by exactly m: their breakpoints lie on the axis — the m = 0 cut in
disguise; a mirror-symmetric cut is necessarily straight, while a centrally symmetric one may zigzag.)
What is proved: the count and the type constraints; what is certified numerically: transversality at the
known solutions; what remains a HYPOTHESIS: that no component of the incidence variety is everywhere
rank-deficient in a way that projects onto an open set of pentagons — the search below is the evidence.

**Search** (`affine.py`, `cache/affine_search*.json`): all placements of p, q (corners or edges), m = 0…4,
all 2·n_v cyclic vertex correspondences, least-squares φ, Nelder–Mead over the cut with random restarts, then a
validity check (cut simple and interior). Residuals normalised by the polygon's diameter²:

RESULTS_TABLE

**HYPOTHESIS (least number of pieces).** For a generic convex n-gon the least number of mutually
affine-congruent pieces is n − 2 (the triangulation is optimal) — the same count for k pieces of v vertices
each gives 6(k − 1) + (cut parameters) − 2v(k − 1) freedoms, which is negative for every k < n − 2 in the
few types I counted (e.g. a hexagon into three quadrilaterals from an interior point: 14 − 16 = −2).
What it would take: enumerate the combinatorial types of k-piece dissections and check the count for each.
