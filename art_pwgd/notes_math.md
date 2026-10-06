# Math notes — run 2026-10-06 (`art_pwgd/`, Opus 5.5 run 8)

## 1. Three gradient-index lenses in closed form (the hero and *Gathered, Mirrored, Sent Home*)

All three lenses have refractive index 1 at the rim r = 1, so a ray crosses the surface with no
bend and no reflection. Inside, the ray equation d²x/dσ² = ∇(n²/2), with dx/dσ = n·t̂, can be
solved exactly. Take a unit ball, entry point P (|P| = 1) and unit inward direction d (P·d < 0).

| lens | index | rays inside | exit point | exit direction | arc length |
|---|---|---|---|---|---|
| Luneburg | n² = 2 − r² | x(σ) = P cos σ + d sin σ (harmonic ellipse), σ ∈ [0, π/2] | **d** | **−P** | ∫₀^{π/2} √(1 − (P·d) sin 2σ) dσ |
| Maxwell fish-eye | n = 2/(1 + r²) | circle through P and −P | **−P** | **2(d·P)P − d** | 2θ / sin θ, cos θ = −d·P |
| Eaton | n² = 2/r − 1 | Kepler ellipse, a = 1, focus at the centre, P at a minor-axis end | **2(P·d)d − P** | **−d** | 2E(1 − b²), b = impact parameter |

Derivations, briefly:
* **Luneburg:** n²/2 = 1 − r²/2 is a harmonic potential, so x'' = −x and x = P cos σ + d sin σ (x'(0) = n(P)d = d).
  |x|² = 1 + (P·d) sin 2σ, which returns to 1 at σ = π/2, where x = d and x' = −P.
* **Fish-eye:** rays are circles through every point z and its inversion −z/|z|². On the rim that is the antipode,
  so the exit point is −P. Reflecting in the line through the centre perpendicular to P maps the arc to itself
  and swaps its ends, which gives the exit direction −(d − 2(d·P)P).
* **Eaton:** H = p²/2 − n²/2 = 0 is the Kepler problem p²/2 − 1/r = −1/2, with energy −1/2, so a = 1. The rim
  r = a is where the minor axis meets the ellipse, and there the velocity is parallel to the major axis. So the major
  axis is parallel to d, the exit point is P mirrored in that axis, and the exit direction is −d. The minor axis
  cuts the ellipse into two congruent halves, so the path length is half the perimeter: 2E(e²) with e² = 1 − b².

**Checks** (`test_lens.py`, `beam.py`): RK4 on the ray equation from random (P, d) agrees with all three maps
(errors 4e-6, 1e-4, 2e-3, all at the step size; Eaton's is largest because of the singular centre). The drawn
arcs end exactly at the closed-form exit points (errors ≤ 1e-14), and their polyline lengths match the
closed-form arc lengths to 1e-4.

**Consequences used in the pictures.**
* Viewed from a camera, each marble is an environment lookup: Luneburg shows the world in direction −P (the
  surface normal reversed), the fish-eye shows the reversed mirror direction, and Eaton shows −d, i.e. *exactly
  what is behind the viewer*. So the Eaton marble alone holds the rainbow. The sun was placed (elevation 10°,
  azimuth 100°) so that the camera→Eaton direction is 41° from the sun.
* Under a directional sun, a Luneburg marble acts as a point source on its own far rim (all light exits from the
  point d), which makes the bright butter pool. An Eaton marble sends all the light back toward the sun, so it
  casts a full shadow even though it is transparent.
* **The coral beam:** in the plane of the centres, a scan of 1601 × 481 launch lines finds a one-parameter family
  whose ball sequence is Luneburg → fish-eye → Eaton → fish-eye → Luneburg. The Eaton lens turns the ray round, and
  the return trip passes through the dream again. The family hits Eaton almost radially, so the out and home
  strands run side by side.

## 2. Post's lattice recomputed (MO 515756) — `post.py`

Not a proof (the question asks for an elementary one), but a mechanical check of the lattice's shape. Every
clone in the Böhler–Creignou–Reith–Vollmer list is defined by its property: R0/R1 (0-/1-preserving), M, D, L,
S₀ᵏ/S₁ᵏ (k-wise 0/1-separating), the V/E/N/I families, and intersections of these. Each is restricted to arity 4
(all 65,536 truth tables).

* 54 restricted sets, all distinct: 38 finite clones plus the 8 infinite families at k = 2, 3. At arity n the
  family S₀ᵏ coincides with S₀ once k ≥ n, so arity 4 resolves exactly k = 2, 3.
* Sanity checks: |M ∩ arity 4| = 168 (the Dedekind number), |D| = 2⁸, |L| = 32.
* Random superposition tests f(g₁,…,g₄): every restricted set is closed.
* The inclusion order has 114 cover edges and is symmetric under the 0↔1 duality.
* The coatoms are exactly {R0, R1, M, D, L}: Post's completeness theorem, recovered by computation.
* The picture draws the infinite chains S₀ᵏ ⊃ S₀ᵏ⁺¹ ⊃ … ⊃ S₀ as beads shrinking geometrically toward the limit.
  In the true lattice the limit has no cover inside the chain; the truncated computation shows a cover
  S₀³ → S₀, drawn dotted.

## 3. The q-analogue inequality (MO 330620) — `qbinom_check.py`, `qbinom_unimodal.py`, `qbinom_tight.py`

Statement (in the poster's c, d form): q^{kcd·C(j,2)}[kc+kd, kc]_q^j ≥ q^{jcd·C(k,2)}[jc+jd, jc]_q^k coefficientwise, for k ≥ j.
* **Verified** with exact integer polynomial arithmetic for every c ≤ d with c + d ≤ 7 and all 1 ≤ j < k ≤ 7, j ∤ k
  (144 non-trivial cases, 0 failures), and then for c + d ≤ 11 and j < k ≤ 11: **1,110 non-trivial cases, 0 failures**
  (`qbinom11.log`). The poster had checked b, k ≤ 6.
* **Both sides are palindromic about the same centre** (63/63 cases, b, k ≤ 6). After the shifts, both count
  lattice paths in the same jkc × jkd box through a knot set that is symmetric under 180° rotation. So the
  difference D is palindromic too.
* **D is not always unimodal:** it fails in 13 of the 63 cases. In those cases D is two-humped with a dip at the
  centre, e.g. (c,d,j,k) = (1,1,2,3): … 15, 17, 13, 12, 10, 12, 13, 17, 15 … So a 'unimodal difference' route to
  a proof is closed.
* **The inequality is never tight:** in all cases with b, k ≤ 6, R_i ≤ (19/24)·L_i for every i. The extreme ratio
  is at (c,d,j,k) = (1,1,2,3), at 4/7 of the degree (and 3/7 by symmetry), not at the centre. The worst case
  becomes less tight as c, d grow with (j,k) fixed: (2,3) gives 0.208, 0.298, 0.331, 0.349, 0.360 for d = 1…5 at c = 1.
  **CONJECTURE** (from these data only): max_i R_i/L_i ≤ 19/24 for all admissible (c,d,j,k). Equality holds only
  at (1,1,2,3). A counterexample would have to come from small c, d with large j, k.
