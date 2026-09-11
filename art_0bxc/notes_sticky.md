# Notes — sticky dust, three ways (adhesion model, Burgers tree, Schwarzschild lens)

## 1. The adhesion model as one convex hull (`adhesion.py`, `render_web.py`)

Zel'dovich dust: initial velocity u₀ = −∇φ₀, straight-line flight x = q + t·u₀(q). The adhesion
model (Gurbatov–Saichev–Shandarin 1989) is the zero-viscosity limit of Burgers' equation: when streams
cross they stick. Its exact solution is the Hopf–Lax formula, which in Lagrangian form reads

    ψ_t(q) = |q|²/(2t) − φ₀(q),     x(q) = t · ∇(conv ψ_t)(q),

where conv ψ_t is the lower convex envelope. A particle q is still free exactly when q is a **vertex** of
the lower convex hull of the lifted points (q, ψ_t(q)); every point lying above the hull has been
swallowed. Each hull **facet** (triangle q₁q₂q₃, supporting plane with gradient g) is a lump: all the
Lagrangian area inside the triangle now sits at the single Eulerian point x = t·g. Chains of thin
facets are filaments; big facets are knots; the tiny facets of a still-convex region are the voids'
thinning mist. So the whole web — knots, filaments, voids — is one Qhull call.

*Field.* Gaussian random density contrast δ with P(k) ∝ k^{−1}·exp(−(k/k_cut)²) on a periodic N² grid,
k_cut = N/6 (in units of 2π/L), φ₀ from ∇²φ₀ = δ, normalised to rms|∇φ₀| = 0.08 L. Periodic extension by a
margin of N/8 cells before the hull (the hull of the tiled field is exact for the central box as long
as t·max|u₀| < margin).

*Hero* (`web_hero_4096.png`, 4096², 2048² particles, t = 1.0): collapse epoch of every particle from a
ladder of 14 hulls at t = 0.12 … 1.0 (geometric); pigment of a knot = mass-weighted percentile of the
mean collapse time of the dust it holds (apricot = the oldest, orchid = the youngest); density = √mass;
filaments = the hull edges between adjacent structure facets drawn as segments (width by mass class);
halos on knots heavier than 30 cells (radius ∝ √mass); ink beads on the 60 heaviest knots; coral = the
heaviest knot and the thin circle whose area equals the Lagrangian area it swallowed.  Voids are paper.
Window: 0.72 of the box, the heaviest knot at (0.38, 0.66). Numbers in `web_hero_4096_cert.json`.

*Sky* (`web_sky_2048.png`): the whole periodic box at 1024² particles, no caption, no fade — the
seamless texture behind the lens.

*Mass scaling, measured* (512² particles, same spectrum, t = 0.35 … 2.0): the mass-weighted mean knot
mass grows as t^{3.0} and the top-ten mean as t^{2.3}; the Press–Schechter self-similar exponent for
this spectrum would be 4/(n+2) = 4 in two dimensions. The shortfall is the cutoff k_cut (the spectrum
is not scale-free at the first crossings) and the finite box at late times — an honest measurement,
not a law.

## 2. The tree of shocks (`burgers.py`, `tree_stats.py`)

One dimension, same construction: the free particles at time t are the vertices of the lower convex
hull of (q, q²/2t − φ₀(q)); every gap between consecutive vertices [q_a, q_b] is a shock. From the hull
edge's slope,

    x_s(t) = (q_a + q_b)/2 + t · ū,   ū = −(φ₀(q_b) − φ₀(q_a))/(q_b − q_a) = mean of u₀ on [q_a, q_b]:

**every lump moves with the mean initial velocity of everything it has eaten** (momentum conservation,
read off the hull). Between mergers every branch of the tree is a straight line in (x, t); on the
sheet time runs up on a logarithmic axis (t = 0.004 … 60), so the branches are exponentials.

*Field.* 4096 particles, u₀ with a white energy spectrum up to k_cut = 512 (Gaussian cutoff), rms 0.018.
Warm ribbons: lumps moving right; cool: moving left; lighter when slow; the free flight of each particle
is a thread of the same family; coral = every birth of a shock (an interval whose interior was all free
one row earlier: 579 births in 8192 rows); ink spine width ∝ √(mass fraction).

*Kida's law, measured.* For a white velocity spectrum Kida (1979) predicts the number of shocks
N(t) ∝ t^{−2/3} and the energy E(t) ∝ t^{−2/3}. Fitted over t = 0.3 … 40: N ∝ t^{−0.61}, E ∝ t^{−0.82}
(the energy is still leaving the cutoff scale). Shock count 310 (t = 0.024) → 387 (t = 0.15, births
still outpacing mergers) → 156 (t = 0.9) → 52 (t = 5.4) → 16 (t = 33) → 14 (t = 60).

*The merger law (new measurement, four seeds, 2,244 mergers).* At each merger take the two heaviest
parents and r = smaller/larger.

| t | mergers | median r | mean r | P(r < 0.1) |
|---|---|---|---|---|
| 0.01–0.1 | 496 | 0.57 | 0.59 | 0.000 |
| 0.1–1 | 1231 | 0.47 | 0.49 | 0.029 |
| 1–10 | 444 | 0.36 | 0.41 | 0.153 |
| 10–60 | 73 | 0.25 | 0.30 | 0.274 |

Pooled, r is close to uniform on [0, 1] (Kolmogorov distance 0.07 to the uniform law, 0.30 to √r), but
it is not stationary: the first mergers are between equals (cutoff-scale shocks are all alike) and the
late ones are increasingly lopsided (a trunk eating twigs). **Hypothesis:** in the genuinely
self-similar regime of Burgers turbulence with a scale-free spectrum the merger-ratio law is
time-independent and *not* uniform — the drift seen here is the memory of the cutoff, and the
limiting law should be the one the 1–10 decade is approaching (median ≈ 0.35, a fifth of mergers with
r < 0.1). What it would take: a spectrum E(k) ∝ k^n without cutoff (Brownian-type initial data,
n = 0 needs n = −2 in this convention for Sinai's dense shocks), 10⁶ particles, and mergers binned by
the running shock spacing instead of by t. Not done this run.

## 3. The web behind a black hole (`lens.py`)

Schwarzschild null geodesics, G = c = M = 1, u = 1/r: the azimuth swept by a photon of impact parameter
b is ∫ du / √(1/b² − u² + 2u³). For b < b_c = 3√3 there is no turning point (the shadow). The observer
stands at r_o = 30; a pixel at angle θ from the hole (gnomonic, half-field 0.5 rad) has b = r_o sin θ /
√(1 − 2/r_o) and sees the sky point in the direction −cos Δφ·f + sin Δφ·e_b, with Δφ = 2∫₀^{u_max} −
∫₀^{1/r_o}. The sky is the seamless web tiled six times around the equator (equirectangular), and the
picture is a pure lookup of its pigment density — surface brightness is conserved along rays
(Liouville), so nothing is brightened. The shadow is left as paper; the coral circle is b = b_c.

*Certificates.* Weak field: α(50) = 0.085083 vs 4/b + 15π/(4b²) = 0.084712; α(200) = 0.020300 vs 0.020295;
α(1000) = 0.004012 vs 0.004012. Strong field (Bozza 2002): α + ln(b/b_c − 1) → ln(216(7 − 4√3)) − π =
−0.40023; measured −0.39711, −0.40019, −0.40023, −0.40022 at b/b_c − 1 = 10⁻³, 10⁻⁵, 10⁻⁷, 10⁻⁹. The
quadrature is exact to the last printed digit.

## 4. Why these three are one piece

Each is the same theorem in a different dimension: **a convex hull decides what sticks**. In 2-D the
hull's facets are the knots of a web that looks, to the eye on Philosophy.SE, like a neuron. In 1-D the
hull's edges are a merger tree that looks like a dendrite. And the black hole — the poster's "synapse" —
is a lookup through the one law that does not stick but bends: the same sky, wrapped in rings.
