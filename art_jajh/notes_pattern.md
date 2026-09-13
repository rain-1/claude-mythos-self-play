# Notes — WHERE THE PATTERN LIVES (run 2026-09-13)

Seed question (Philosophy.SE 141658): *is the apparent patterned-ness of determinism a property of
the system itself, or of the observation scale?*  Three exact models answer it three different ways.
Everything below is what the pictures certify; numbers come from the `*_cert.json` files.

## 1. The Pattern Is in the Crowd — Bohmian two-slit trajectories (hero, 4096²)

Model: ħ = m = 1, ψ(x,t) = G(x−a,t) + G(x+a,t) with G a free Gaussian packet of initial width σ = 1 and
a = 25 (slit half-separation). Guidance equation dx/dt = v = Im(∂ₓψ/ψ). Time runs upward on a
square-root scale (stated on the sheet's notes, not hidden): the near field (t < 50, two tight fans) takes
the lower half, the braiding takes the upper half, and the far-field rays x ∝ t become gentle parabolas.

**Theorem (1-D Bohmian mechanics).** Let u ∈ (0,1) and let x_u(t) be the trajectory whose initial point
is the u-quantile of |ψ(·,0)|². Then x_u(t) is the u-quantile of |ψ(·,t)|² for every t.
*Proof.* v is smooth wherever ψ ≠ 0, so trajectories never cross (uniqueness for the ODE); the probability
current J = |ψ|² v is the flux of |ψ|² along the trajectories (continuity equation ∂ₜ|ψ|² + ∂ₓJ = 0), so the
mass of |ψ|² to the left of x_u(t) is conserved and equals u. ∎
Corollary: by the mirror symmetry ψ(−x) = ψ(x), the ½-quantile is x = 0 for all t — **no path ever crosses
the axis**, which is the coral dotted line. The cloud, being all quantile paths at equal probability
spacing sampled at equal row spacing, IS |ψ|² row by row (equivariance) — the fringes are a property of the
crowd, never of one path.

Numerics: the exact quantile paths (`bohm.quantile_paths`, CDF on a 60,001-point grid per row) agree with
RK4 integration of the guidance equation (dt = 0.025) to 1.9 × 10⁻³ over 400 paths and 200 time units;
RK4 alone at 8,000 paths lost order near the nodes (one path was flung 2,400 units — the first hero render
had `no_crossing_order_preserved: false`), which is why the final uses the theorem instead of the integrator.
Far-field fringe spacing πt/a = 25.13 at t = 200; envelope width 2 s_T ≈ 200 ⇒ about 8 strong fringes.

Reading of 141658: each particle is a hitbox the size of a body — jerky, kinked where it changes fringe;
the ensemble is a hitbox the size of the room — clean fringes. Both are the same deterministic law.

## 2. The Pattern Is in the Law — the strange eigenmode of a periodic chaotic stirring (2560²)

Model: alternating sine flow on the torus, half-period shears x → x + A sin(y + φ₁), y → y + A sin(x + φ₂)
applied EXACTLY as spectral phase shifts (row-wise FFT), diffusion exp(−κk²τ/2) after each shear. A fixed
protocol of P = 3 periods with phases from `default_rng(2)`, A = 2.5 (shift amplitude), repeated; κ scaled
as 1/n² with the grid so the diffusive cutoff is a fixed number of cells (κ = 2.5e-4 at n = 512, 1.5625e-5 at
n = 2048).

Facts: with κ > 0 the one-block advection–diffusion operator is compact, so it has a leading Floquet
eigenfunction (the *strange eigenmode*, Pierrehumbert 1994); a single period with fixed phases has large
KAM islands (decay ratio → 0.999/period: the islands keep their ink), which is why the protocol is a
BLOCK of three random-phase periods repeated — a random sine flow made periodic. A search over 24 protocols
(A ∈ {2, 2.5}, P ∈ {3, 4}, 6 seeds) found 11 with a real positive leading eigenvalue (consecutive-block
correlation → +1.0000, cross-ink correlation ±1.0000); the others have a complex leading pair (the
normalised pattern rotates in a 2-plane; consecutive correlation oscillates).

Certificates for the piece (n = 2048): two initial inks (sin x stripes; one blob) after 45 blocks —
cross-ink correlation and per-block decay ratio in `law_2560_cert.json`; at n = 512 they were 0.9999998
and ×0.522 per block; at 30 blocks and n = 2048 the correlation was 0.9956 (finer scales converge slower),
hence 45 blocks for the final.

Decay rate vs κ (`sweeps.json`, same protocol, n ∝ κ^{-1/2}): see the table appended below once the sweep
finishes. *Hypothesis to test:* the per-period decay rate tends to a κ-independent limit as κ → 0 (the
"global" strange-eigenmode regime of Haynes–Vanneste 2005), i.e. the pattern's lifetime is a property of
the stirring alone.

Reading of 141658: the ink is the observation, the flow is the system; after a few blocks the observation
shows only the system. The shape is deterministic and belongs to the law — not to the scale, not to what
you poured in.

## 3. The Pattern Is in the Distance — a stealthy hyperuniform point pattern (4096 × 2816)

Model: N = 5,000 points in a periodic 4:1 box at unit density; minimise Φ = Σ_{0<|k|<K} |ρ(k)|² by L-BFGS
until Φ/N ≈ 0 (collective-coordinate ground state, χ = 0.40, K = 6.07 in units of the mean spacing).
Then S(k) = 0 exactly for every |k| < K: no density wave longer than 2π/K ≈ 1.03 spacings fits the pattern.

Facts: Poisson number variance σ²(R) = πR²; a stealthy pattern's σ²(R) grows like the perimeter, ∝ R.
Measured (N = 1,500, χ = 0.40, square box, 4,000 windows): σ² = 0.50, 0.95, 1.43, 1.88, 2.91, 3.78 at
R = 1, 2, 3, 4, 6, 8 (≈ 0.47 R) against Poisson 3.2, 13.4, 31.8, 58.0, 119, 172 (≈ πR²).
Coefficient c(χ) in σ² ≈ cR from the sweep: table below. A Gaussian smoothing of width σ leaves variance
∝ ∫S(k)e^{−k²σ²}d²k: for the stealthy pattern this is ≲ e^{−K²σ²} — already 10⁻⁴ at σ = 0.5 — while for
Poisson it is 1/(4πσ²). That is the whole picture: at the left both bands are disorder, at the right one is
paper-flat and the other is weather. The coral circles (R = 2.5, expected count 19.6) are the certificate:
the upper band's counts differ by ±1–2, the lower band's by ±7.

Reading of 141658: here the pattern really IS a property of the observation scale — but of the scale of the
WINDOW, and the system chooses at which scale the observer will find it (2π/K).

## Side result — MO 342405 (triangle arrangements, average contact degree)
Not built this run; one line worth recording: a side of a triangle can share finite-length boundary with at
most 2 non-overlapping congruent copies on the other side of its line (three unit segments meeting a unit
segment in positive length must overlap), so the contact degree of any triangle is ≤ 6 with equality iff
every side is straddled by two neighbours — the same bound as the planar-graph bound, reached by a
different route.
