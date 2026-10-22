# Cover time of the unit disk by disks of area π/n (MO 458793): simulation results

Setup: the bottom set is the closed disk D_R (R = 1 is the actual problem). The top disks are open, B_n has radius r_n = n^{-1/2}, and the centres are i.i.d. uniform in the unit disk. The cover time is T = min{N : D_R ⊂ B_1 ∪ … ∪ B_N}. Each run is followed up to N_max = 2^52 ≈ 4.5e15 (2^48 for R = 1.05). All runs used one core.

## Method (`sim.py`)
- **Uncovered set.** It is stored as leaves of quadtrees. Each live leaf carries two things:
  - a *witness* point in leaf ∩ D_R that is certified uncovered by every disk so far. Candidates are the centre, the radial projection onto the rim, the corners and the edge midpoints.
  - the *complete* list (at most 8) of disks that partially overlap the leaf.
- **When a disk arrives.**
  - A leaf entirely inside one disk is deleted. A leaf entirely outside D_R is never kept.
  - If a disk partially overlaps a leaf and the leaf is larger than r_n/4, or the list is full, or no witness survives, the leaf is split recursively. The children inherit the filtered lists.
  - So a cell covered only by a *union* of disks keeps splitting until each piece lies inside a single disk. This terminates by the Lebesgue-number argument (open cover of a compact set).
  - Every surviving leaf therefore has a genuinely uncovered point. "No live leaf" is equivalent to "covered", so T is exact.
- **Rim.** The rim of D_R needs no special case: leaves are clipped to D_R and witnesses may lie on the circle. The circle |x| = R is also tracked exactly as 1-D arc intervals, which gives T_rim.
- **Depth cap.** Splitting stops at 1e-6·r_n, and such leaves are marked "ambiguous". These leaves can only be deleted by single-disk containment, so they can delay T but never fake coverage. In validation they never changed T.
- **Thinning (exact).** In epoch [N, 2N), only disks whose centre lies in E matter. E is the union of grid squares of side N^{-1/2} that touch the s-neighbourhood of some live leaf.
  - The number of relevant disks is Binomial(N, |E|/π). Their indices are a uniform random subset of the epoch, and their centres are uniform in E, rejected if outside the unit disk.
  - This makes the cost per epoch O(#holes), so N = 2^52 is reachable. A typical run takes about 0.15–0.3 s.
- **Hole counts at N = 2^k.** Grid cells of side ≤ r_N/16 that contain a certified-uncovered sample point are grouped into 8-connected components. Each component is binned by its depth δ = R − |x| (bin 0: δ < r_N; bin j: δ ∈ r_N·[2^{j−1}, 2^j)).

## Validation (`validate.py`, `validation.json`)
- **Exact T versus brute force.** 24 runs (R = 1 and R = 0.95, every disk generated, no thinning) were checked against a brute-force raster: 2001² globally plus an 801² zoom at the last hole.
  - The zoomed brute force gives exactly T in 24/24 runs.
  - The coarse global raster sometimes gives a smaller T (12200 vs 16227, 39274 vs 59280), because it misses sub-pixel holes.
  - The last-hole witness is exactly uncovered by disks < T and covered by disk T in 24/24 runs.
  - T_rim agrees with a 2·10^5-point rim raster in 24/24 runs.
- **Hole counts versus raster labelling.** Compared with scipy labelling on a 3001² raster at N = 64…2048 (86 cases): 78% match exactly, and the totals are 389 vs 409. The counter therefore runs about 5% low (thin slivers).
- **Thinning.** min(T, 2^17) from thinned runs and from runs with every disk generated (300 runs each) agree: KS p = 0.72.

## Results, R = 1 (6050 runs)
**Quantiles of T:**
- q10 = 8.2e3, q25 = 8.5e7; the median is above 2^52 (60% of runs are still uncovered at 4.5e15).
- T_rim: q10 = 1.3e3, q25 = 3.4e5, median 6.4e10.

| N | P(T>N) | P(T_rim>N) | E[#holes] | E[#holes \| uncovered] | E[#rim holes] |
|---|---|---|---|---|---|
| 2^10 | 0.943 | 0.910 | 5.1 | 5.4 | 3.10 |
| 2^16 | 0.864 | 0.789 | 8.7 | 10.1 | 3.79 |
| 2^20 | 0.813 | 0.720 | 10.7 | 13.1 | 3.60 |
| 2^24 | 0.772 | 0.649 | 12.6 | 16.3 | 3.49 |
| 2^30 | 0.721 | 0.568 | 15.7 | 21.8 | 3.50 |
| 2^36 | 0.680 | 0.499 | 19.1 | 28.0 | 3.56 |
| 2^40 | 0.653 | 0.462 | 21.3 | 32.6 | 3.57 |
| 2^44 | 0.631 | 0.433 | 23.4 | 37.1 | 3.47 |
| 2^50 | 0.604 | 0.393 | 26.9 | 44.6 | 3.67 |

The full tables, including hole counts by depth bin, are in `analysis_R1.00.md`. The plot is `tail_and_holes.png`.

**Tail laws.**
- A power law P(T > N) ~ cN^{-a} does not fit: the fitted a drifts from 0.017 to 0.014.
- A fit c(log N)^{-a} has an effective exponent that *rises* with the fitting window: a = 0.21 on [2^6, 2^52], 0.27 on [2^10, 2^52], 0.33 on [2^20, 2^52].
- S(N)·log N keeps growing (9.6 → 20.5 between k = 16 and 48), so the tail is not c/log N.
- S(N)·√log N = 2.88, 3.15, 3.33, 3.44, 3.55 at k = 16, 24, 32, 40, 48. It is still rising, but the increments shrink.
- For the rim, the effective exponent of P(T_rim > N) rises 0.36 → 0.50 → 0.66.

**Hole counts.**
- E[#holes at N] grows *linearly in log N*: about 0.54 per doubling of N, i.e. about 0.78·ln N.
- The rim holes (depth < r_N) stay constant at about 3.5.
- Each fixed depth window r_N·[2^a, 2^b] holds a constant number of holes once N is large enough (about 2.6, 4.1, 4.2 for the bins 1–4, 5–8, 9–12). New depth bins keep switching on as r_N shrinks.
- So E[#holes] is O(1) *per dyadic depth shell* δ ∈ (r_N, 1), which gives about log N in total. This matches the first-moment computation: a point at depth δ is uncovered at time N with probability about 1/(δN), and holes have area about r_N².

**Where the last hole is** (2432 covered runs):
- Last hole exactly on the circle (T = T_rim): 43% overall. By range of T: 82% for T ≤ 10^3, 57% for (10^3, 10^6], 37% for (10^6, 10^9], 18% for (10^9, 10^12], and 9% above 10^12.
- Depth < 0.05 in 73% of covered runs, against an area share of 9.8%; depth < 0.2 in 86%, against 36%. The last hole is strongly concentrated near the rim, but for large T it sits *off* the circle at depth ≫ r_T. The median of log2(depth/r_T) for non-rim last holes rises 2 → 4 → 7.6 → 10 → 15 across the T ranges.
- **Mechanism check** (1391 runs with T_rim < T). Define the birth generation of the last hole as g_b = log2(depth^{-2}), and the rim's death generation as g_r = log2 T_rim. In 99.8% of these runs g_b ≤ g_r + 2. That is, the last interior hole always sits at a depth the rim could still "reach" when it was last uncovered.
- Spearman rank correlations: ρ(g_r, log T) = 0.75 and ρ(g_b, g_r) = 0.75.

## Contrast runs
**R = 0.95 (11550 runs).** Here the rim is inside the centre region, so only the interior criticality remains.
- E[#holes at N] = 2.78 ± 0.02, flat from N = 2^10 to 2^50. This is exactly the classical "O(1) holes at criticality".
- **P(T > N)·log N = 6.11, 6.10, 6.12, 5.99, 5.94 at k = 16, 24, 32, 40, 48**, so the tail is clean c/log N with c ≈ 6.0. The fitted exponent on [2^20, 2^52] is 1.04.
- The median T is 2.2e5, q75 is 4e10, and 17% of runs are still uncovered at 1.1e15.
- The last hole lies on the circle |x| = 0.95 in 71% of runs with T ≤ 10^3 and 0% of runs with T > 10^9.

**R = 1.05 (16700 runs).** Coverage fails with a certificate in 99.70% of runs. The certificate is a witness point at distance ≥ r_n outside the unit disk, which no later disk can reach; every failure was detected by N = 2^12. The remaining 0.30% (50 runs) were covered, almost all with T < 10^3, so P(cover) ≈ 0.003.

## Conjectures (heuristic; supported by the numbers above, not proved)
**Conjecture A (holes).** For R = 1, E[#holes at N] ~ α log N (empirically α ≈ 0.78), whereas for R < 1, E[#holes] → const. The rim contributes O(1) holes, and each dyadic depth shell r_N ≪ δ ≪ 1 contributes O(1) more.

**Conjecture B (tail).** For R < 1, P(T > N) ~ c/log N; for R = 0.95, c ≈ 6.0. For R = 1:
- P(T_rim > N) ≍ 1/log N, and
- **P(T > N) ≍ (log N)^{-1/2}.**

So T has an extremely heavy tail: E[(log T)^{1/2−ε}] < ∞ but E[(log T)^{1/2}] = ∞. The data are compatible with this but not conclusive: the effective exponent rises 0.21 → 0.33 and S·√log N creeps up 2.9 → 3.55. Convergence is slow because the branching variance is small.

**Heuristic for B.** Work in generations k = log2 N.
- The rim gaps form a scale-invariant critical branching process (mean offspring 1; E[#rim holes] ≈ 3.5 is constant). Its survival probability is about c/k.
- While the rim is uncovered at generation k, each rim gap leaves behind, with probability bounded below, interior "holes" at depth δ ≈ r_{2^k}. After that time those points see hit probability 1/n, i.e. they enter the interior critical regime. Each one starts an independent critical family, which survives m more generations with probability about 1/m.
- Conditioned on the rim living τ generations, the total progeny is about τ², so about τ² families are born. About τ²/L of them survive to generation L.
- Hence P(T > 2^L) ≈ P(τ ≳ √L) ≍ L^{-1/2}. The mean number of holes is ∑_k O(1) = O(L), which is Conjecture A.
- The same picture predicts that the last hole is "born" before T_rim (seen in 99.8% of runs) and that P(T = T_rim | T > N) → 0 (seen: 82% falls to 9%).
- For R < 1 there is no rim source, so the process is a single critical family, giving c/log N and O(1) holes.

**Conjecture C (location).** For R = 1, P(last hole lies on ∂D | T > N) → 0. The last hole lies at depth δ with δ → 0 but δ/r_T → ∞; the heuristic gives log(1/δ) ≍ √log T. The overall probability P(T = T_rim) is a constant, about 0.43 at the N_max used here.

## Extra: the artwork disc sequence (`seed9.py`, `seed9.json`)
The sequence is rng = default_rng(9), u = rng.random(1e6), th = rng.random(1e6)·2π, disc k with centre √u_{k−1}·(cos, sin)th_{k−1} and radius k^{−1/2}.
- **Exact T = 74195.** The last point is (−0.25891, 0.15723), at radius 0.3029.
  - It is certified uncovered by discs 1…74194 and covered by disc 74195.
  - A zoomed brute-force raster and a global 2501² raster both also give T = 74195.
  - The earlier raster bracket of 30727–38406 missed the sub-pixel hole.
- **When holes closed.** The circle was covered at N = 1786. The number of components dropped at N = 1786, 2859, 8291, 16953, 34963 and 74195.
  - At 34963 the last-but-one fragment, at (−0.2606, 0.1613), closed. This is next to the final hole, which survived alone for about 39000 more discs.

## Files
- `sim.py`: the simulator.
- `validate.py`, `validation.json`, `validate.log`: the validation checks.
- `run_main.py`: the production runs.
- `analyze.py`: produces `analysis_R*.md`.
- `plot.py`: produces `tail_and_holes.png`.
- `per_seed.json`: compact per-seed records (T, T_rim, failure time, last-hole x, y).
- `runs_R*.json`: full per-run data, including hole counts per N = 2^k.
- `seed9.json`: the artwork sequence result.
