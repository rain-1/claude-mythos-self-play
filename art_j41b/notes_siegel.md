# Notes — *What Zero Draws* (the golden-mean Siegel disk)

**Map.** f(z) = z² + c with c = λ/2 − λ²/4, λ = e^{2πiθ}, θ = (√5 − 1)/2 = 0.6180339887.
Then z₀ = λ/2 = −0.36868 − 0.33775 i is a fixed point (f(z₀) − z₀ = 0 exactly in floating point) with
multiplier f′(z₀) = 2z₀ = λ, |λ| = 1. c = −0.39054 − 0.58679 i.

**What is known (and what the picture certifies).**
- *Siegel (1942)*: θ is Diophantine (it is the golden mean, the worst-approximable number), so f is
  analytically linearisable near z₀: there is a disk Δ ∋ z₀ on which f is conjugate to the rotation
  w ↦ λw. Every orbit inside Δ lies on a closed analytic curve (the image of a circle |w| = r).
  Certificate in `siegel_hero_4096_cert.json`: the 34 orbits started on the segment from z₀ toward 0
  stay bounded for 240,000 iterates, and their maximal distances from z₀ are strictly increasing in the
  starting parameter (`curves_nested: true`) — the curves are nested and never cross.
- *Douady–Ghys–Herman–Świątek*: for a rotation number of bounded type the boundary of the Siegel disk
  is a quasicircle **passing through the critical point 0**. So ∂Δ is the closure of the orbit of 0.
  Certificate: the orbit of 0 (4,000 iterates, drawn as coral beads) stays bounded, |f^n(0)| ≤ 0.838,
  and its closest approach to z₀ is exactly 0.25 = |0 − z₀|… the beads fill a curve just outside the
  outermost drawn invariant curve (max distance from z₀: 0.4945 for the last drawn curve, and the
  boundary reaches 0.25 at its nearest point — the disk is far from round: its conformal radius is not
  its Euclidean radius).
- *Böttcher / Douady–Hubbard*: outside the filled Julia set K the Green's function G(z) = lim 2^{−n} log|f^n(z)|
  is harmonic, and the external rays (gradient lines of G, labelled by the angle at infinity) are
  drawn by Newton continuation along the Böttcher coordinate: for potential level r and angle t the
  point solves f^k(z) = r^{2^k} e^{2πi 2^k t}. 64 rays at angles (j + ½)/64, 40 halvings of the
  potential each (final G = 6·10⁻¹² ≈ the Julia set), 6 sub-steps per halving; **no ray jumped a
  branch** (`rays_with_late_jumps: 0`, tested as no step > 0.05 over the last 60 substeps).

**How the satellites were drawn.** Every point of K that is not in Δ eventually maps into Δ (K is
the union of all preimages of the disk — for this c there is no other Fatou component type; the Julia
set has measure zero so this is a statement about all of K's interior). Each drawn curve was pulled
back through the two branches ±√(z − c), nine levels deep, with the point set subsampled by 2 per
level so that every level carries the same total pigment as the disk itself. The measure is therefore
the pull-back of the same measure, and the small satellites go darker because the same mass lands on
a smaller area: brightness *is* a measure here, and it is the invariant one.

**The philosophy seed.** *Does One contemplate Zero?* (Phil.SE 141404). In the quadratic family
everything contemplates zero: the fate of the critical point decides the whole dynamics (Fatou,
Julia), and here it does so literally — the disk on which the map is a pure rotation is rimmed by the
orbit of 0. The fixed point (ink dot) is the One; the rim is what Zero draws around it.
