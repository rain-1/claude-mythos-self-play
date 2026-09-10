# What the Definition Predicts — every Kepler orbit from one point at one speed

**Seed.** Philosophy.SE 141543 asks whether Newton's first and second laws are empirical laws or definitions.
The honest answer is: the second law alone defines force; it predicts nothing until a force law is added.  The
picture is what the definition predicts once the inverse-square law is added — and it is a prediction that could
have been false.

## The theorem drawn

Sun O at the origin, gravitational parameter μ = 1; launch point P at distance r₀ = 1; launch speed v with
v² < 2 (bound).  For any launch direction φ:

- energy E = v²/2 − 1 fixes the semi-major axis a = 1/(2 − v²) — **the same for every direction**;
- the second focus F satisfies |PO| + |PF| = 2a, so F lies on the circle |F − P| = 2a − r₀ around P (the dotted
  ink rings; one ink bead per orbit);
- a point X lies on some orbit iff |XO| + |XF| = 2a for some F on that circle, and by the triangle inequality
  this is possible iff |XO| + |XP| ≤ 4a − r₀: **the union of all orbits is the ellipse with foci O and P and
  major axis 4a − r₀** (the gravitational safety ellipse; for constant gravity it degenerates to the parabola of
  safety).  Every orbit touches the rim exactly once.

Three speeds v = 0.95, 1.12, 1.26 give a = 0.911, 1.343, 2.427 and envelope semi-axes A = (4a − 1)/2 =
1.322, 2.186, 4.354 with B = √(A² − 1/4).

## Certificates (`kepler_2560_cert.json`)

- Envelope from the field: 720 rays from the envelope centre, the union of 900 orbits measured against the
  exact ellipse — maximum relative overshoot 0.3 % (one pixel), median relative gap 0.2 %.  The coral rims
  were drawn after this check.
- Second foci computed from the eccentricity vector e = (v × L)/μ − r̂: F = P + (2a − r₀)(−ê).

## How it is drawn

Orbits are drawn **stroboscopically**: 900·(size scale) points per orbit at equal time intervals (Kepler's
equation solved by Newton for each point), so the pigment density is the time the planet spends there —
Kepler's second law as a density field: pale and beaded near periapsis, dark at apoapsis.  All orbits of one
speed share the period (same a), so equal points per orbit means equal time weight.  Pigment by speed
(lemon, apricot, orchid), lightness by |L| (radial launches pale, tangential dark).  Sun: ink dot with a lemon
halo; launch point: coral bead; rims: coral.
