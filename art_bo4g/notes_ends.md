# Notes — WHERE ONE WORLD BECOMES TWO (run of 2026-09-16)

## 1. Ricci-flow neckpinch with surgery (`ricci.py`, `run_hero.py`, `sweep_a.py`)

**Model.** Rotationally symmetric metrics on S³, g = ds² + ψ(s,t)² g_{S²}, under Ricci flow (Angenent–Knopf 2004):
ψ_t = ψ_ss − (n−1)(1 − ψ_s²)/ψ with n = 2. Written in the square u = ψ² the equation for S³ is *linear*:
u_t = u_ss − 2 (the (n−2) u_s²/(2u) term vanishes exactly at n = 2), which is what made the solver stable at the
poles: u is smooth and even there (u ≈ s² − K s⁴/3). The arclength gauge is kept by moving every node with
V(s) = n ∫₀ˢ ψ_ss/ψ and re-interpolating (φ_t = n φ ψ_ss/ψ); at the poles ψ_ss/ψ → −K is taken from a
least-squares fit ψ = s − K s³/6 over 8 nodes, because the raw stencil amplifies a node-1 error by 1/ds² and
the resampling feeds it back with growth 1 + 2λ per step (found the hard way; see craft notes).

**Test on the round sphere** (N = 400): r(t) tracks √(1 − 4t) to 1e-4, the pole slope stays 1.0003, extinction at
t = 0.25 — the exact value (r² = r₀² − 2n t).

**Initial data.** A unit sphere squeezed at the equator: z = −cos θ, r = sin θ · (1 − a e^{−(z/w)²}); the
neck radius is 1 − a. The metric embeds in R⁴ (|ψ_s| ≤ 1 is preserved), so every picture is an honest
hypersurface of revolution with profile (z, ψ), dz/ds = √(1 − ψ_s²).

**Surgery.** When the neck radius falls below ε = 0.02, the neck is cut where ψ = 2.5ε on both sides and a
spherical cap is glued to each side; the two children flow on, each on its own grid, until its radius < ε.

**Certificates** (`cache/cert_*.json`, N = 1600 nodes, record every 0.0005):

| run | a | w | surgery at | children die at | d(ψ²_min)/dt before the pinch (window 0.02 / 0.01 / 0.005) | d(ψ²_max)/dt of a child near its end |
|---|---|---|---|---|---|---|
| a80w35 | 0.80 | 0.35 | 0.04728 | 0.11650 | −1.42 / −1.55 / −1.63 | −4.04 |
| a85w50 (hero) | 0.85 | 0.50 | 0.01965 | 0.08234 | −1.15 / −1.43 / −1.55 | −4.11 |

- Angenent–Knopf: ψ_min ≈ √(2(n−1)(T−t)) = √(2(T−t)) with logarithmic corrections, i.e. d(ψ²_min)/dt → −2
  *slowly*. The measured slope climbs toward −2 as the window shrinks (−1.42 → −1.55 → −1.63), which is the
  logarithmic approach the theorem predicts; the fitted pinch time T from the 0.005 window is within 0.0003 of the surgery time.
- A round S³ of radius r has r² = r₀² − 4t; the children's d(ψ²_max)/dt = −4.04 and −4.11 say that after
  the cut each half is a round sphere to 1–3 % long before it dies. Finite extinction, as in Perelman /
  Colding–Minicozzi / Morgan–Tian ch. 19 (the front-page question MO 515040 is about a claim in exactly that chapter).

**Sweep: does the neck pinch?** (N = 600, w = 0.35)

| a | 0.50 | 0.55 | 0.60 | 0.65 | 0.70 | 0.75 | 0.80 | 0.85 | 0.90 |
|---|---|---|---|---|---|---|---|---|---|
| initial neck radius 1 − a | 0.50 | 0.45 | 0.40 | 0.35 | 0.30 | 0.25 | 0.20 | 0.15 | 0.10 |
| fate | one sphere, dies 0.184 | one sphere, 0.174 | one sphere, 0.162 | **pinch 0.1395**, children die 0.1435 | pinch 0.109 | pinch 0.076 | pinch 0.047 | pinch 0.025 | pinch 0.010 |

So with these lobes the neck must start thinner than about 0.37 of the lobe radius to pinch (threshold between
a = 0.60 and 0.65); the a = 0.65 case pinches only 0.004 before its children would have died anyway —
a world that splits just before it ends. Not a theorem: a numerical threshold for this one-parameter family.

**Hypothesis (stated, not proved).** For the family r = sin θ (1 − a e^{−(z/w)²}) at fixed w, the pinch time
T(a) behaves like T ≈ c (1 − a)² near the pinching side (the neck closes at the cylinder rate ψ² ≈ 2(T − t), so
T ≈ ψ₀²/2 if the neck started as a cylinder): predicted T(0.90) = 0.005, T(0.85) = 0.011, T(0.80) = 0.020 against
measured 0.010, 0.025, 0.047 — the same ordering and roughly 2× slower, because the neck first has to become
cylindrical (its curvature in s is initially of the same order as 1/ψ). A better fit would take ψ_min(0) after the
initial transient; not pursued.

## 2. The microwave sky (`sky.py`, `render_sky.py`)

- C_ℓ^{TT} from CAMB 2.0.4 with Planck-2018-like parameters (H₀ = 67.36, Ω_b h² = 0.02237, Ω_c h² = 0.1200,
  τ = 0.0544, A_s = 2.1e-9, n_s = 0.9649, lensed). First acoustic peak at ℓ = 220, i.e. **0.82°** on the sky.
- One Gaussian realisation on a HEALPix sphere with N_side = 2048 (50M pixels), seed 5; rms 114.5 μK, range −571…+607 μK.
- Mollweide ellipse (own inverse projection, checked against the ellipse equation) and a 14° gnomonic window at
  (lon 40°, lat −20°); the coral circle in the window is the first peak's angular scale, the hairline circle on the
  ellipse is the window's footprint. This is a *statistical* sky (the true one has the same spectrum, different phases).

## 3. Craquelure (`craq.c`, `render_craq.py`)

- Triangular spring lattice (jittered ±0.25 so cracks are not forced along lattice lines), unit springs whose rest
  length shrinks as 1 − ε (drying), every node tied to its substrate by k_s = 0.004 (screening length 1/√k_s ≈ 16 cells),
  bond thresholds 0.03 × (1 ± 0.15) × (1 + 0.2 smooth field). Quasi-static: raise ε by 0.0005, relax (SOR to residual
  5e-6), break the most over-strained bond, relax a window of radius 23 around it, repeat until nothing is over threshold.
- Two bugs worth recording: (i) an unconverged relaxation (12 sweeps over a 16-cell screening length) produced a
  V-shaped shatter from the top edge that looked like physics; (ii) the reverse-bond parity was wrong for odd rows, so half
  the reaction forces were missing (Newton's third law broken) and the film sheared. With both fixed the mosaic has
  T-junctions and a spread of breaking strains (0.008–0.05 at 120², i.e. a hierarchy).
- Cells are components of the crack raster (with a morphological closing to seal the pinholes left by unstrained
  ligament bonds that never break, and the film's rim), tinted by the mean breaking strain of their walls.
