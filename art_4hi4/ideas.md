# Four Crossings — the 2026 Fields Medals suite

**Occasion (special instruction this run):** the 2026 Fields Medals were awarded
yesterday (2026-07-23) at ICM Philadelphia to **Yu Deng** (Chicago), **John
Pardon** (Stony Brook), **Jacob Tsimerman** (Toronto), **Hong Wang** (NYU/IHES).
This run departs from the usual triptych format *deliberately* (noted for the
run log): one substantial piece per medalist, each verified from scratch,
under one suite title.

**Unifying theme — a crossing between two worlds that shouldn't touch:**
- Deng: reversible micro-dynamics → irreversible macro-law (Boltzmann from hard spheres)
- Pardon: two utterly different curve-counts → one number (GW = DT, the MNOP conjecture)
- Tsimerman: tame logic (o-minimality) → wild arithmetic (special points, André–Oort)
- Wang: measure zero → full dimension (Kakeya in ℝ³; shadows, projections, Furstenberg)

**Live seeds folded in** (fetched 2026-07-24):
- Phil.SE front page: *"Is there a single comprehensible sentence explaining how
  the mental can arise from the physical?"* (emergence — Deng's whole citation);
  *"Although only half of a dish is red, can I call it 'red dish'?"* (predication
  with partial presence — a Kakeya set owns every direction yet has no volume);
  *"Does an external world exist?"* (the shadow vs the thing — projections).
- MO front page: "When is the envelope of a family of circles convex?", "Proper
  ways to measure circularness" (still open in memory), "Consequences of the
  disproof of the Jacobian conjecture" (ties to the 2026-07-21 run).

## The eight ideas (2 per medalist; ★ = executed)

1. ★ **WANG — "The Estate of Shadows"** (4096² hero). Point–line duality: each
   grain (a,b) of the four-corner Cantor set fires the line y=ax+b. Top: the
   dust (the "deed", dimension 1, Favard length → 0 — *it casts no shadow*).
   Below: the blazing union-of-lines furnace (the "estate": every slice an
   affine copy of a projection of the dust). Verified: exact generation-n
   projection lengths at all angles (interval-union), Favard decay, the
   slice⇄projection duality identity checked numerically, self-similarity.
   Kakeya annotation: Wang–Zahl 2025 — in ℝ³ a needle in every direction
   forces dimension 3.
2. **WANG alt — Wolff's hairbrush** in 3D additive render (the dim ≥ 5/2
   classical bound Wang–Zahl surpassed). Passed over: volumetric tube render
   is heavy and hard to verify honestly.
3. ★ **DENG — "The River That Flowed Uphill"** (2560²). Event-driven hard-disk
   gas, space-time carpet (x vs t, threads = particles). At t=T all velocities
   reversed: the lower half of the river is the exact mirror of the upper —
   Loschmidt's demon made visible; Boltzmann's H(t) descends, climbs back up
   the whole mountain, then descends again. Collision genealogy of one tagged
   particle in ember (the Lanford / Deng–Hani–Ma collision tree; recollision
   fraction measured = propagation of chaos). Verified: exact time-symmetry of
   the echo (max |x(2T)−x(0)|), energy conservation, Maxwell–Boltzmann fit.
4. **DENG alt — wave-kinetic cascade** (NLS with random phases → wave kinetic
   equation). Passed over: honest statistical verification needs ensembles ≫
   art budget.
5. ★ **TSIMERMAN — "The Ceiling of Small Primes"** (2560²). Gross–Zagier on
   singular moduli: for CM discriminants D₁≠D₂ the huge integer
   Res(H_{D₁},H_{D₂}) = ∏(j(τ₁)−j(τ₂)) factors ENTIRELY into primes
   p ≤ D₁D₂/4. Every pair of special points is a chord of prime stars; the
   diagonal ceiling blazes; above it, void — the theorem is the empty sky.
   (André–Oort, Tsimerman's medal territory: what special points may do is
   tamed.) Verified: Hilbert class polynomials computed from scratch at high
   precision and rounded to exact integers (integrality check), exact big-int
   resultants, complete factorization by primes ≤ D₁D₂/4 with cofactor ±1
   REQUIRED, class numbers vs table. Closes the old "singular moduli mod p" seed.
6. **TSIMERMAN alt — Duke equidistribution cascade** (Heegner points for
   growing |D| equidistribute in the fundamental domain). Passed over: chart
   is the over-visited Poincaré-disk family.
7. ★ **PARDON — "The Crystal That Counts Curves"** (2560²–4096²). DT theory of
   ℂ³ IS the MacMahon count of plane partitions (topological vertex); Pardon
   proved the MNOP conjecture (GW=DT) in vast generality. Sample the q^volume
   random plane partition (melting corner crystal) by checkerboard Metropolis,
   render as a true 3D cube crystal (three lozenge face-tints, faceting by
   orientation), brightness = local disorder (the melt glows, facets stay dark).
   Arctic boundary vs the amoeba of 1+z+w (e^{-x}+e^{-y}=1) overlaid. Verified:
   exact MacMahon DP count vs ∏(1−q^k)^{-k}, detailed balance, limit-shape fit.
   Closes the old "cube grove" seed.
8. **PARDON alt — torus-knot distortion heat** (Gromov's distortion problem,
   solved by Pardon). Passed over: the honest computation (geodesic vs chordal
   ratio on fattening torus knots) reads as a thin diagnostic curve, not a field.

## Format decision
Hero = Wang at 4096² (the medal's headline theorem). Deng, Tsimerman, Pardon
at 2560²+ with full verification bundles. Suite README carries the story.
