# Notes — What We Inherit and Whom We Forget (run of 2026-09-17)

## 1. The names that reach us (haploid Wright–Fisher, N = 1000)

**Model.** N individuals per generation; each child picks one parent uniformly at random. Generation 0 has N
distinct founders ("names"). A name is *forgotten* when its last carrier dies childless. The run ends the first
generation with a single name: the present descends entirely from one founder.

**Layout theorem (what makes the picture planar).** Sort each generation by the rank of its parent (stable).
Then (i) no lineage line between consecutive rows crosses another, and (ii) the descendants of any individual form
a contiguous block in every later generation (induction: the children of a contiguous block of parents are
contiguous). So every name is one block and the picture is a forest without crossings, by construction.

**The clock.** Forward in time the number of surviving names at generation t equals the number of ancestral
lineages of generation t's population at time 0, i.e. Kingman's coalescent count A_N(t/N) (Tavaré 1984), whose
large-t form is 2N/t. The last coalescence (the two-name era) has mean length N generations, the whole fixation
2N(1 − 1/N). Measured over 300 runs: `cert_names.json`.

**The pictured run** (seed 3): fixation at generation 1392, two names from 1172, names left at t = 1, 10, 100,
1000: 643, 160, 24, 3. The root (winner founder) is index 229 of 1000.

**Axis.** Two-sided logarithm, y ∝ log(t + 1) − log(G − t + 30): both ends expanded, since the forgetting happens
in the first hundred generations and the branching of the present's family tree in the last hundred.

## 2. A fraction of a fraction (Rogers–Ramanujan)

R(q) = q^{1/5} / (1 + q/(1 + q²/(1 + q³/…))) = q^{1/5} ∏ (1 − q^{5n−1})(1 − q^{5n−4}) / ((1 − q^{5n−2})(1 − q^{5n−3})).
On the disc of w = q^{1/5} it is single-valued with R(ζw) = ζR(w), ζ⁵ = 1, and R(w̄) = R(w)̄, so one tenth of the
disc is computed (2500 log-spaced radii to |w| = 0.9965 × 4096 angles, term count 40/(5(1 − r)) capped at 6000).
Certificate: R(e^{−2π/5}) = √((5 + √5)/2) − φ = 0.284079043840412 (Ramanujan's first letter to Hardy, 1913);
the product reproduces it to 2e-16 in double precision (`rr.py` prints it).
Two limits worth knowing: R → φ⁻¹ = 0.618… along the positive real ray (q → 1⁻) and R → φ·e^{iπ/5} along the ray
at angle π/5 (q → −1⁺); both are exact contour levels of φ^{k/2}, so the hairlines are drawn at φ^{k/2+1/4}.
Drawn with a log-radial warp (display radius ∝ −log(1 − |w|)), so each decade of 1 − |w| gets the same ring.

## 3. What the circle cannot see (Gauss's fragment)

Gauss (1834/1839, Werke X-1 pp. 311–320; Schwarz 1870): w = √k · sn((2K/π) arcsin z, k) maps the interior of the
ellipse with foci ±1 and semi-axes cosh c, sinh c onto the unit disc, where K'/K = 4c/π (nome q = e^{−4c} =
((a−b)/(a+b))²). Reason: arcsin takes the ellipse to the rectangle (−π/2, π/2) × (−c, c); scaling by 2K/π gives
(−K, K) × (−K'/2, K'/2); and |sn(u + iK'/2)| = 1/√k for real u.
Complex sn from the real Jacobi functions by the addition formula. Certificates (`cert_gauss_cr.json`): winding
number of w around the boundary = 1.000 for every ellipse (one zero, degree one ⇒ bijective), Cauchy–Riemann
residual ≤ 1e-8 (2.7e-6 for b/a = 0.15, where 1 − k² ≈ 1e-9), |w| = 1 on the boundary to 1e-15.

**Crowding, in numbers** (`cert_gauss.json`): the two tips beyond the foci hold this share of the ellipse's area,
and receive this share of the circle's rim (harmonic measure from the centre):

| b/a | area beyond the foci | share of the rim |
|---|---|---|
| 0.8 | 14 % | 23 % |
| 0.55 | 3.9 % | 4.9 % |
| 0.38 | 1.2 % | 0.59 % |
| 0.25 | 0.34 % | 0.018 % |
| 0.15 | 0.072 % | 0.000024 % |

The rim share falls like exp(−π a/(2b)) (a strip's harmonic measure), the area share only like (b/a)^{3}: what the
circle cannot see is exactly what a thin ellipse mostly is.
