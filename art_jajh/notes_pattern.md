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

Certificates for the piece (n = 2048, κ = 1.5625e-5): two initial inks (sin x stripes; one blob) after 45 blocks —
**cross-ink correlation 0.99934**, decay ×0.589 per block for both inks (consecutive-block correlation 0.9996
for the stripes, 0.9992 for the blob — a faint slower-converging component remains at this κ); at n = 512,
κ = 2.5e-4 they were 0.9999998 and ×0.522 per block; at 30 blocks and n = 2048 the correlation was 0.9956,
hence 45 blocks for the final. The decay per block is nearly κ-independent (0.522 → 0.589 as κ falls 16×;
see the sweep table below).

Decay rate vs κ (`sweeps.json`, same protocol, n ∝ κ^(-1/2), 40 blocks from the stripes):

| n | κ | ratio per block | rate per period |
|---|---|---|---|
| 256 | 1.00e-03 | 0.4818 | 0.2434 |
| 512 | 2.50e-04 | 0.5219 | 0.2167 |
| 1024 | 6.25e-05 | 0.5569 | 0.1951 |
| 2048 | 1.56e-05 | 0.5891 | 0.1764 |

The rate falls by a nearly constant 0.022 per halving of κ^(1/2) (0.243 → 0.217 → 0.195 → 0.176): on this
range it looks like rate ≈ a + b·log κ rather than a plateau. **Hypothesis (stated, not proven):** the decay
rate of this protocol keeps falling logarithmically in κ down to the resolution tested and has *not* reached
the κ-independent "global" strange-eigenmode limit of Haynes–Vanneste; either the limit lies at much smaller
κ, or the block protocol sits in the "local" regime where the decay is set by the slowest stretching region
and depends on κ through the diffusive cutoff. A test would be n = 4096, 8192 at κ ∝ 1/n² (memory: fine;
time: ~1 h each) and a fit of rate against log κ versus rate against κ^(1/2).

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
Coefficient c(χ) in σ² ≈ cR from the sweep (N = 1,500, six radii 1…8, 6,000 windows each; intercepts ≈ 0):

| χ | K | c |
|---|---|---|
| 0.100 | 2.254 | 0.964 |
| 0.200 | 3.150 | 0.726 |
| 0.300 | 3.897 | 0.578 |
| 0.401 | 4.487 | 0.490 |
| 0.450 | 4.738 | 0.477 |

c·K is 2.17, 2.29, 2.25, 2.20, 2.26 — constant to ±3 %. **Hypothesis:** for 2-D stealthy ground states
σ²(R) ≈ (c₀/K)·R with c₀ ≈ 2.2 independent of χ in the disordered range χ ≤ 0.45, i.e. the perimeter
coefficient is set only by the radius of the stealthy hole (the smallest wavelength the pattern still
carries), not by how many degrees of freedom were constrained. For a surface-area-scaling pattern the
coefficient is ∝ ∫ S(k)/k · dk near the hole edge; with S jumping from 0 to O(1) at K this gives ∝ 1/K,
consistent with the measurement; the numerical prefactor is the thing to derive.

Hero-size ground state (`far_cert.json`): N = 5,000, 4:1 box, χ = 0.40, K = 6.074, L-BFGS 2,321 iterations,
Φ/N = 4.7e-23 (99 min under CPU contention). Number variance at R = 0.5…8:
stealthy 0.35, 0.54, 0.88, 1.20, 1.71, 2.31, 2.93, 3.43, 4.62 vs Poisson
0.8, 3.1, 7.1, 12.5, 28.0, 49.2, 77.8, 114.5, 209.3 — stealthy σ²/R ≈ 0.58 (c·K = 3.5 here; the 4:1 box
and χ = 0.40 at this N sit close to the wavy-crystalline threshold: the pattern shows stripe domains, and its
Voronoi degrees are 5: 1,290, 6: 2,297, 7: 1,074 vs Poisson 5: 1,236, 6: 1,505, 7: 978 — narrower, as
hyperuniformity demands, but the stripe order raises c·K above the square-box value; worth a check). A Gaussian smoothing of width σ leaves variance
∝ ∫S(k)e^{−k²σ²}d²k: for the stealthy pattern this is ≲ e^{−K²σ²} — already 10⁻⁴ at σ = 0.5 — while for
Poisson it is 1/(4πσ²). That is the whole picture: at the left both bands are disorder, at the right one is
paper-flat and the other is weather. The coral circles (R = 2.5, expected count 19.6) are the certificate:
the upper band's counts on the sheet are 20, 19, 19, 18, 19; the lower band's 14 … 27.

Reading of 141658: here the pattern really IS a property of the observation scale — but of the scale of the
WINDOW, and the system chooses at which scale the observer will find it (2π/K).

## Side result — MO 342405 (triangle arrangements, average contact degree)
Not built this run; one line worth recording: a side of a triangle can share finite-length boundary with at
most 2 non-overlapping congruent copies on the other side of its line (three unit segments meeting a unit
segment in positive length must overlap), so the contact degree of any triangle is ≤ 6 with equality iff
every side is straddled by two neighbours — the same bound as the planar-graph bound, reached by a
different route.
