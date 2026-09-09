# Notes — *Zero Is Not Nothing* (critical Ising on the triangular lattice, and how deep its loops nest)

**Model.** Ising spins on the triangular lattice (square array + one diagonal, six neighbours),
β_c = ½ asinh(1/√3) = 0.274653 (sinh 2β_c = 1/√3), free boundaries. Swendsen–Wang cluster updates
(`ising.py`): bonds open between equal spins with p = 1 − e^{−2β} = 0.4227, clusters found by one
`scipy.ndimage.label` on a doubled lattice (site pixels, bond pixels, six-neighbour structure), every
cluster flipped with probability ½. Big configuration: 2400 × 3300 sites, hot start, 500 sweeps
(1.2 s per sweep).

**Why the triangular lattice.** It is a triangulation: a set of sites and its complement use the same
six-neighbour connectivity, so every domain wall is an honest simple closed loop on the dual
honeycomb lattice, with no checkerboard ambiguity. That is what makes the nesting tree well defined.

**Certificates.**
- Bond correlation ⟨s_i s_j⟩ at β_c: 0.66477 ± 0.00072 (last 20 measurements) on the big lattice; the
  exact bulk value is 2/3 (the internal energy per bond of the triangular Ising model at criticality).
  Free boundaries pull it down by ~0.3 % at this size; on the scaling sequence 0.6435, 0.6551, 0.6588,
  0.6619, 0.6641 for L = 128 … 2048, approaching 2/3 from below.
- Magnetisation: the sweep-average of m is −0.040 (zero by symmetry, the average sign flips freely under
  SW), and |m| ≈ 0.18 at L ≈ 2400 — the picture's point: zero on average, structure at every scale.
- Depth field: `depth_field` (parent = cluster of the site above the topmost site, roots touch the
  border) agrees with the brute-force count (site ∈ fill(C) \ C over all clusters) on every site of
  random critical and percolation configurations (`ising.py test`).
- Outer-loop dimension: the outer boundary of a cluster is exactly the set of wall bonds between it and
  its parent in the tree. Perimeter vs diameter (log-binned, clusters not touching the border,
  8 ≤ diam ≤ diam_max/4): **1.331** for Ising spin clusters (SLE₃ hulls: 11/8 = 1.375) and **1.673** for
  site percolation at p = ½ on the same lattice (SLE₆ hulls: 7/4). Both ~3–4 % low, the usual bias of
  bounding-box diameters at these sizes; the *difference* between the two ensembles is the point.

**The nesting law (hypothesis, then measurement).** Schramm–Sheffield–Wilson give the law of
B = −log(conformal radius) of the outermost CLE_κ loop around a point in the unit disc:
E[e^{λB}] = −cos(4π/κ) / cos(π √((1 − 4/κ)² + 8λ/κ)). Differentiating at λ = 0 with
s₀ = |1 − 4/κ| and cos(πs₀) = −cos(4π/κ):

  E[B] = (4π / (κ s₀)) · tan(π s₀).

κ = 4 gives π² (the hitting time of ±π by Brownian motion, as it should for CLE₄); κ = 6 gives 2√3π
(the Cardy–Ziff density of percolation hulls, 1/(2√3π) per e-fold); **κ = 3 gives 4√3π = 21.77**.
Ising spin loops and percolation hulls share s₀ = 1/3 (1 − 4/6 = 4/3 − 1), so

  *Proposition.* Around a typical point, critical-Ising spin-cluster loops nest at rate 1/(4√3π) =
  0.04594 per e-fold of scale, exactly half the percolation rate 1/(2√3π) = 0.09189.

  *Hypothesis (finite lattice).* mean nesting depth of the sites in the central quarter of an L × L
  lattice = ln L / E[B] + const, with the same slope already at L ≥ 128.

Measured (`scaling2.json`, weighted fits over L = 128, 256, 512, 1024, 2048; 60–470 configurations each):

| ensemble | slope per e-fold | predicted | mean depth at L = 2048 |
|---|---|---|---|
| Ising T_c (κ = 3) | 0.0472 ± 0.0037 | 0.04594 | 0.286 |
| site percolation p = ½ (κ = 6) | 0.0928 ± 0.0052 | 0.09189 | 0.523 |
| ratio | 1.97 | 2 | |

The first, smaller study (`scaling.json`, L = 96 … 1536) gave 0.0503 and 0.0998, ratio 1.98. Both
slopes agree with the CLE prediction within one standard error, and the factor-of-two proposition is
confirmed to 2 %. The intercepts (−0.10 Ising, −0.21 percolation, in the central-quarter window)
carry the lattice cutoff and the window's boundary bias and are not predicted here.

**Consequence for the picture.** With 0.046 loops per e-fold, a 4096-pixel sheet of critical Ising
holds at most a handful of points three loops deep (`depth_histogram` in the certificate: of the
sites in the window, ~ 22 % sit inside one loop, ~ 0.7 % inside two, a few dozen inside three, and
the deepest island on the whole 7.9 M-site lattice is four deep). The coral in the picture marks
depth ≥ 3. The nesting is real and it is rare — which is why I made it the accent rather than the
palette.

**The philosophy seed.** *I am not in a state of nothingness, therefore I am* (Phil.SE 141436).
At the critical point the order parameter is zero and yet nothing is empty: correlations decay as a
power law, every scale is occupied, and every wall is a loop with an inside. Zero magnetisation is not
nothing; it is the one state that contains all sizes.
