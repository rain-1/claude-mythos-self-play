# Randomized Pascal triangle (MO 479618): results

Model: X_{n,0}=X_{n,n}=1, and for interior entries X_{n,k} = X_{n-1,k-1}+X_{n-1,k} with prob. p,
or |X_{n-1,k-1}-X_{n-1,k}| with prob. 1-p. S_n = row sum. L_p = lim E[mean of rows 0..n].

## 0. Already known (MO 479618 + MSE 4972093)
* Rødland (MSE): parity is deterministic; E S_{n+1} >= 2p E S_n, so L_p = inf for p > 1/2.
  His long C runs (up to 1e6 x 1e6 in quadrant coordinates) blow up for p = 0.085 and 0.08, and he
  conjectures divergence for every p > 0, after a long waiting time ("spikes").
* MO answer: rigorous E S_n >= lambda^n with lambda = p^2 + sqrt(p^4+4p(1-p)) > 1 iff p > 1-1/sqrt2 ≈ 0.2929.
  A computer-assisted extension gives p >= 0.232. Nothing rigorous is known below 0.232.
* Srini (MSE): heuristics only. Nobody has given a value of L_p, or a finite L_p, for any 0<p<1.

## 1. Rigorous statements (proved here or elementary)
1. **Parity.** a+b ≡ |a-b| (mod 2), so X_{n,k} ≡ C(n,k) (mod 2) whatever the coins are. Row n has exactly
   2^{s_2(n)} odd entries, so S_n >= 2^{s_2(n)} surely. An entry can be 0 only where C(n,k) is even.
2. **Domination.** |a-b| <= a+b gives X_{n,k} <= C(n,k) by induction, so S_n <= 2^n.
3. **Homogeneity.** f(ca,cb) = c f(a,b). The triangle is the zero-padded process started from a single 1,
   with the edge 1's obeying the rule. A local value A in a background of much smaller values starts an
   A-scaled copy of the process, and values much larger than their neighbours spread at light speed
   (|A-ε| ≈ A+ε ≈ A). At p=0 the row maximum never increases, since |a-b| <= max(a,b).
4. **Second diagonal is exactly solvable.** Y_n := X_{n,1} = f(1, Y_{n-1}) is a ±1 random walk on {0,1,2,...}
   (+1 w.p. p, −1 w.p. 1−p, 0→1 surely). For p<1/2 it is positive recurrent with stationary law
   π_0 = (1−p)π_1, π_k = π_1 r^{k-1} (r = p/(1−p)), π_1 = (1−2p)/(2(1−p)^2). The Cesàro mean of E Y_n is
   **1/(2(1−2p))** (checked by simulation: 0.6249 / 1.2485 / 4.987 vs 0.625 / 1.25 / 5 at p = .1/.3/.45).
   For p > 1/2, Y_n ~ (2p−1)n; at p = 1/2, Y_n ~ sqrt(n). The X_{n,n-1} diagonal behaves the same way
   (a rigorous divergence of the diagonals for p ≥ 1/2, and a finite exact constant for p<1/2).

## 2. Numerics (numba, float64 with per-row log-rescaling; 1 core)
Validation: p=0 gives S_n = 2^{s_2(n)} exactly, and p=1 gives 2^n. On rings with integer data, float64 is
exact while values < 2^53. Once values grow past that, the trajectories separate from exact big-integer
runs, but the growth rates still agree within about 0.5% (p = .15, .3, W=1001, T=3000).

### 2a. Two phases
* **Low phase:** entries are small integers. About 40–50% are zeros, the row mean is O(1), S_n ≈ μ_p·n, and
  the maximum stays bounded (ring W=10007, 2e5 rows: max 16 at p=.005, 80 at p=.05, ~7000 at p=.08).
* **High phase:** values are spread over many scales, there are essentially no zeros, and
  ln S_n ≈ γ(p)·n with γ>0 (quenched Lyapunov exponent; max, sum and typical log value grow at the same rate).

Quenched growth rate γ(p) = lim (1/n) ln S_n. Triangle: N=2e4, 4 seeds, slope over rows 1e4–2e4, ± is the
std error. Near threshold: periodic rings.

| p | γ(p) | source |
|---|---|---|
| 0.95 | 0.6493 ± 0.0002 | triangle |
| 0.90 | 0.6102 ± 0.0002 | triangle |
| 0.80 | 0.5370 ± 0.0002 | triangle |
| 0.70 | 0.4677 ± 0.0001 | triangle |
| 0.60 | 0.3980 ± 0.0003 | triangle |
| 0.50 | 0.3263 ± 0.0002 | triangle (rigorous lower bound for ln E: 0.2475) |
| 0.40 | 0.2513 ± 0.0004 | triangle |
| 0.30 | 0.1707 ± 0.0005 | triangle (rigorous bound: 0.0109) |
| 0.25 | 0.1284 ± 0.0003 | triangle |
| 0.20 | 0.0848 ± 0.0004 | triangle; ring 0.0845 |
| 0.15 | 0.0404 ± 0.0003 | triangle; ring 0.0403 |
| 0.12 | 0.0161 ± 0.0003 | triangle; ring 0.0155 |
| 0.11 | 0.0087 ± 0.0002 | ring W=1e4, 3e5 rows, 2 inits |
| 0.10 | 0.0032 ± 0.0002 | triangle 0.0033, ring 0.0031–0.0033 |
| 0.095 | 0.0015 ± 0.0001 | ring W=1e4, 1e6 rows |
| 0.09 | 0.0005 ± 0.0001 | ring W=1e4, 1e6 rows |
| 0.085 | 0.0002 ± 0.0001 | ring W=1e4, 1e6 rows |
| 0.0825 | ≈1.5e-4 | ring W=1e5, high-phase start, 4e5 rows |
| 0.08 | ≈1.3e-4 (float); exact-integer run grows too (mean ln 7→31 in 3e5 rows) | ring W=1e5 |
| 0.075 | ≈0.6e-4 | ring W=1e5, float |
| 0.07 | +0.2e-4 ± 0.3e-4 (no clear growth) | ring W=1e5, float |
| 0.065 | ≤ 0: exact-integer run, max e^27.6 → e^21 | ring W=1e5 |
| 0.06 | −0.4e-5 ± 3e-5 (float); stuck/decaying | ring W=1e5 |
| 0.05 | −2.7e-5 (float); exact-integer run decays e^27.6 → e^17.5 | ring W=1e5 |

The high phase also has a finite-size effect. On W=1e4 rings at p=0.08, a high-phase start collapses
into the low phase and an all-ones start never leaves it in 1e6 rows. With W=1e5 the high phase survives
and grows. The same thing explains why the triangle runs in (2b) show no blow-up at p≤0.08 by n=2e4.

### 2b. Behaviour of the row mean vs n (one realisation is typical; 4–8 seeds)
* p ≥ 0.12: the row mean grows like e^{γ n} from n of a few hundred onwards. ln(A(2e4)), the log of the mean of the
  first 2e4 rows, is 301 / 792 / 1672 / 3398 / 6504 / 12967 at p = .12/.15/.2/.3/.5/.95.
* p = 0.10: blow-up starts after about 1–3e3 rows, and ln A(2e4) ≈ 58.
* p ≤ 0.08: no blow-up by n = 2e4. A(n) rises slowly towards the bulk low-phase density μ_p (table 2d).
  At p=0.08 a blow-up still happens eventually: the high phase is stable there and is nucleated
  (Rødland saw it at ~1e5–1e6 rows).

### 2c. Annealed rate (what the question asks: E S_n)
Population-dynamics (cloning) estimate of ln E S_n. Results are independent of population size
(P = 500 vs 4000 agree within 2%), and the p=1 check gives exactly ln 2.
Rate = d ln E S_n / dn over n ∈ [1500, 3000]:

| p | 0.5 | 0.3 | 0.2 | 0.15 | 0.12 | 0.10 | 0.09 | ≤0.08 (0.04, .06, .07, .08) |
|---|---|---|---|---|---|---|---|---|
| rate | 0.3316 | 0.1774 | 0.0908 | 0.0460 | 0.0200 | 0.0059 | 0.0014 | E S_n ∝ n (log-slope = 1/n exactly) |

The annealed rate lies just above γ(p) (Jensen), and both curves vanish together. Within these
windows (n ≤ 3000), E S_n is linear in n for p ≤ 0.08. That window is too short to see the slow
nucleation at p = 0.08.

### 2d. Estimate of p_c, and L_p below it
* **Conjecture (numerical): there is a threshold p_c ≈ 0.072 ± 0.006.** Above it the growing (high) phase is
  self-sustaining in large systems, so L_p = ∞ and the triangle eventually blows up almost surely.
  Below it, high-phase configurations do not grow (exact-integer runs at 0.05 and 0.065 decay), so the low
  phase is the attractor. γ(p) vanishes extremely steeply as p ↓ p_c: it is about 1e-4 at p = 0.08, while
  the e-folding time 1/γ near 0.075 already exceeds 1e4 rows. This report cannot rule out a tiny
  γ > 0 below 0.07, as in Rødland's scenario. What it does show is that γ ≤ 3e-5 there, if positive at all.
  For the expectation, p_c^{E} <= p_c is expected, and they are numerically indistinguishable.
* For p < p_c the conjectured limit is L_p = μ_p, the bulk stationary mean of the low phase. It is
  measured on integer rings (W=10007, time-averaged over 1.5e5 rows, 3 seeds; errors ≤ 0.002 except
  p = .08: ±0.016). The triangle's running mean A(n) converges to it slowly, roughly like (const)/log n.
  The triangle's mean over rows 1.5e4–2e4 is shown for comparison.

| p | 0.005 | 0.01 | 0.02 | 0.03 | 0.04 | 0.05 | 0.06 | 0.07 | (0.08, metastable) |
|---|---|---|---|---|---|---|---|---|---|
| μ_p (ring) | 0.992 | 1.032 | 1.082 | 1.135 | 1.198 | 1.279 | 1.389 | 1.552 | 1.91 |
| triangle row mean n∈[1.5e4,2e4] | 0.365 | 0.561 | 0.797 | 0.951 | 1.071 | 1.185 | 1.317 | 1.495 | – |
| A(2e4) (± ≤0.002) | 0.497 | 0.691 | 0.889 | 1.013 | 1.115 | 1.219 | 1.341 | 1.512 | – |
| zero fraction (ring) | 0.51 | 0.50 | 0.48 | 0.47 | 0.46 | 0.44 | 0.43 | 0.41 | 0.38 |

  **Conjecture:** lim_{p→0+} L_p ≈ 0.97 ± 0.03, while L_0 = 0. So L_p is discontinuous at p = 0. Any
  noise destroys the Sierpinski sparsity, and the bulk becomes a dense random pattern of mean about 1.
  The trouble is crossover time: at p=0.005 the triangle needs far more than 2e4 rows to approach μ_p.

## 3. Files
* `sim.py`: numba kernels. `run` is the triangle with log-rescaling, `ring`/`ring_from`/`ring_from2` are
  periodic strips, `cloning` estimates the annealed rate, `triangle`/`triangle_int` produce samples.
* Drivers and outputs: `scan1.py` / `scan1.npy`, `ring1-6.py` / `ring*.out` / `ring*.npy`, `clone1-2.py` /
  `clone2.out` / `clone2.npy`, `lowphase.py` / `lowphase_tri.npy`, `exactcheck.py`.
* Samples: 512×512 arrays with entry (n,k) for k≤n and −1 elsewhere. Seed 2026.
  * `tri_p030.npy` (float64, p=0.30, max ≈ 1.09e39; exact only while values < 2^53) and `coins_p030.npy`.
  * `tri_pc.npy` (int64, exact, p=0.08 ≈ just above p_c, max 88; still in the low phase at 512 rows) and
    `coins_pc.npy`.
  * Coins are uint8, 1 = sum and 0 = difference. They are defined only for interior cells
    (1≤k≤n−1); edges and the upper part are 0. Parity was checked against Lucas' theorem.
* `dl/`: the fetched question and answer JSON.
