# Undulations of the 3n−1 basin proportions: a renewal-equation explanation

(MathOverflow 516116. Map on odd n: T(n) = (3n−1)/2^v, where v = ν₂(3n−1). The three known cycles are {1}, {5,7} and {17,…,91}.)

## Summary

**Conjecture (heuristic, not proved).** Let θ = log₂3, m = 2−θ = 0.41504 and x = log₂n. For every integer q, the local
Fourier coefficient of the basin-j density at frequency q behaves like C_{j,q}·e^{−β_q x}. Here β_q is the root, near 0,
of

  e^{2πiqθ} · e^{β(1−θ)} = 2 − e^{β}            (Wald / renewal equation, ★)

So mode q oscillates at frequency q + f_q with f_q = −Im β_q/2π, and its amplitude decays at rate r_q = Re β_q per octave.
When ‖qθ‖ = ε is small, β_q ≈ −2πiε/m + 4π²ε²/m³. This is exactly exp(−2π²ε²·Var K) with Var K ≈ (2/m³)·x = 27.97x,
where K is the number of odd steps. The surviving modes are the q with ‖qθ‖ small: 12, 41, 53, 94, 106, 147, …, 306, 359,
665, …. The 12-mode (rate 0.105/octave) dominates the cumulative proportions p_j(n) up to n ≈ 2^37 ≈ 10^11. The 53-mode
(rate 0.0048/octave) takes over after that. The constants C_{j,q} (amplitudes and phases) depend on small-n data, and the
theory does not predict them.

**Evidence.**
- There are no free parameters. The predicted decay rates and frequency shifts match the exact data for n < 2^32 for
  about 40 modes. For example, q = 12 is predicted at 0.1046 and measured at 0.1029.
- The predicted phase drift (+11.76°/octave for q = 12, +2.57°/octave for q = 53) fits to within ±1° over 20 octaves.
- Out of sample, Monte Carlo at 2^40, 2^50 and 2^60 matches the amplitude **and phase** extrapolated from 2^30 (see the
  table in §2c).
- The asker's ratio "1.059" is 2^{1/(12+f_12)} = 2^{1/12.0327} = 1.05928. It is not exactly the semitone 2^{1/12} = 1.05946.

**What would decide it.**
- (a) A proof of the 3-adic equidistribution step H below. With H, (★) is just linear algebra.
- (b) A test of the q = 12 amplitude at 2^80 and beyond. The prediction is 1.4e-4 at 2^80, so about 10^8 samples are
  needed.
- (c) A check that no mode outside the small-‖qθ‖ set is sustained. This holds in the data, apart from a few residual
  anomalies at the 3e-4 level.

---

## 1. Heuristic derivation

**Exact preimage structure.** Fix k ≥ 1. The odd n with v(n) = k are exactly n = (2^k m + 1)/3, where m runs over the odd m
with m ≡ r_k (mod 3), and r_k = 1 for odd k, 2 for even k. Among the odd n in a window around 2^x, a fraction 2^{−k} has
v = k. Their images are all odd m ≡ r_k (mod 3) in the corresponding window around 2^{x+θ−k}, up to a relative error
O(1/n). Since basin(n) = basin(T(n)), this gives

  g(x) = Σ_{k≥1} 2^{−k} g^{(r_k)}(x + θ − k) + O(2^{−x}),

where g^{(r)} is the basin density among odd m ≡ r (mod 3). This statement is exact.

**Heuristic H.** g^{(1)} ≈ g^{(2)} ≈ g. In words, basin membership is asymptotically independent of the residue mod 3.
With H we get the **renewal equation**

  g(x) = Σ_k 2^{−k} g(x+θ−k),

which is equivalent to g(x) = E[G(X_τ)]. Here X is the random walk X → X + θ − v with P(v = k) = 2^{−k}, and τ is the
time at which the walk enters the "resolved" region of small n, where the basin is known.

**Why integer frequencies.** Insert a plane wave e^{(2πiξ − β)x}. The k-sum contributes the factor Σ_k 2^{−k}e^{−2πiξk},
which has modulus 1 only when ξ is an integer. So non-integer frequencies are killed geometrically: because v is an
integer, only period-1-compatible structure survives. For an integer q the v-part drops out entirely, and each odd step
only multiplies by the phase z = e^{2πiqθ}. Equivalently, X_τ = x + Kθ − V with V an integer, so
e^{2πiqX_τ} = e^{2πiqx}·z^K. The mode-q coefficient of g at x is then Ĥ_q·E[z^K]. Here Ĥ_q is the coefficient of the
boundary function folded mod 1. This step also assumes that the integer part of the landing point is approximately
independent of x + Kθ mod 1, which is again heuristic.

**Wald identity.** The process z^k e^{−β(X_k−x)} is a martingale when z·E[e^{−βΔ}] = 1, where
E[e^{−βΔ}] = e^{β(1−θ)}/(2−e^{β}). That is equation (★). It gives E[z^K] ≈ const·e^{−β_q x}, so for mode q:

- the amplitude decays as e^{−r_q x} with r_q = Re β_q;
- the local frequency is q + f_q with f_q = −Im β_q/2π (the oscillation is *not* exactly periodic in log₂n with period 1/q);
- the small-ε expansion, with ε = qθ − round(qθ), is β = −2πiε/m + 4π²ε²/m³ + O(ε³). This is the Gaussian law
  |E z^K| ≈ exp(−2π²ε² Var K) with E K ≈ x/m and Var K ≈ 2x/m³. The expansion parameter is 2π|ε|/m² = 2π|ε|/0.172. It is
  small for q = 53 (0.11) but **not** for q = 12 (0.71). For q = 12 the Gaussian law predicts 0.211/octave, while the exact
  root gives 0.1046 and the data give 0.103. So the exact root of (★) has to be used.

**Stopping-time constants, checked empirically** (`stoptime.c` → `stoptime.txt`; 2·10^5 samples per x, x = 12…60). Here
K₁₀ is the number of odd steps until n < 2^10.

| quantity | predicted | measured |
|---|---|---|
| slope of mean of K₁₀ per octave | 1/m = 2.409 | 2.396 (fit over x = 24…60) |
| slope of Var K₁₀ per octave | 2/m³ = 27.97 | 27.93 |

Hitting a cycle instead of the threshold 2^10 adds a constant to K but leaves the slopes unchanged.

**Predicted rates and frequency shifts** (`beta.py`). The last column is the cumulative-proportion damping factor
ln2/|ln2 + 2πiq| (see §2d).

| q | ε = ‖qθ‖ (signed) | r_q exact (/octave) | Gaussian 552ε² | f_q (cycles/octave) | cumulative factor |
|---|---|---|---|---|---|
| 5 | −0.0752 | 0.382 | 3.12 | −0.056 | 0.022 |
| 12 | +0.01955 | 0.1046 | 0.211 | +0.0327 | 0.0092 |
| 41 | −0.01654 | 0.0846 | 0.151 | −0.0295 | 0.0027 |
| 53 | +0.003013 | 0.00483 | 0.00501 | +0.00713 | 0.0021 |
| 94 | −0.01352 | 0.0644 | 0.101 | −0.0258 | |
| 106 | +0.006025 | 0.0176 | 0.0200 | +0.0136 | 0.0010 |
| 306 | −0.001475 | 0.00119 | 0.00120 | −0.0035 | |
| 359 | +0.001538 | 0.00129 | 0.00131 | +0.0037 | |
| 665 | +0.0000630 | 2.2e-6 | 2.2e-6 | +0.00015 | 1.7e-4 |

Generic q have r_q ≈ 0.3–0.93 per octave; the rate saturates near 0.93 for ε near 1/2.

## 2. Tests against the data (n < 2^32, plus Monte Carlo to 2^60)

### 2a. Amplitude decay

The data are the fine bin counts in `fine2048.u32` (2048 bins/octave), built by `fine.c`. The amplitude is
2|c_q| = 2|(1/N) Σ_n (1[basin(n)=1] − p̄) e^{−2πiq log₂n}| over 2-octave windows (`table.py`).

Each cell shows the measured value, with the prediction in parentheses. The prediction is anchored only at the last window
and extrapolated downward with e^{r_q Δx}.

| window | q=5 | q=12 | q=17 | q=41 | q=53 | q=65 | q=94 | q=106 | q=306 | q=359 | q=665 | q=971 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r_q pred | 0.3816 | 0.1046 | 0.3008 | 0.0846 | 0.0048 | 0.1240 | 0.0644 | 0.0176 | 0.0012 | 0.0013 | 0.0000 | 0.0011 |
| 2^10–2^12 | 0.0220 (0.5453) | 0.1971 (0.1814) | 0.0419 (0.0942) | 0.0738 (0.0543) | 0.0641 (0.0617) | 0.0625 (0.0966) | 0.0465 (0.0662) | 0.1257 (0.0993) | 0.0332 (0.0198) | 0.0288 (0.0316) | 0.0217 (0.0091) | 0.0151 (0.0515) |
| 2^14–2^16 | 0.0138 (0.1185) | 0.1204 (0.1194) | 0.0150 (0.0283) | 0.0406 (0.0387) | 0.0589 (0.0605) | 0.0598 (0.0588) | 0.0462 (0.0512) | 0.0895 (0.0925) | 0.0189 (0.0197) | 0.0334 (0.0314) | 0.0112 (0.0091) | 0.0291 (0.0513) |
| 2^18–2^20 | 0.0036 (0.0258) | 0.0782 (0.0786) | 0.0034 (0.0085) | 0.0269 (0.0276) | 0.0594 (0.0594) | 0.0328 (0.0358) | 0.0377 (0.0395) | 0.0873 (0.0862) | 0.0212 (0.0196) | 0.0282 (0.0313) | 0.0109 (0.0091) | 0.0378 (0.0510) |
| 2^22–2^24 | 0.0001 (0.0056) | 0.0513 (0.0517) | 0.0028 (0.0025) | 0.0187 (0.0197) | 0.0578 (0.0582) | 0.0218 (0.0218) | 0.0304 (0.0306) | 0.0804 (0.0804) | 0.0194 (0.0195) | 0.0301 (0.0311) | 0.0093 (0.0091) | 0.0434 (0.0508) |
| 2^26–2^28 | 0.0004 (0.0012) | 0.0340 (0.0340) | 0.0008 (0.0008) | 0.0135 (0.0140) | 0.0570 (0.0571) | 0.0134 (0.0133) | 0.0235 (0.0236) | 0.0750 (0.0749) | 0.0194 (0.0195) | 0.0307 (0.0310) | 0.0089 (0.0091) | 0.0478 (0.0506) |
| 2^29–2^31 | 0.0004 | 0.0249 | 0.0003 | 0.0109 | 0.0563 | 0.0092 | 0.0195 | 0.0711 | 0.0194 | 0.0308 | 0.0091 | 0.0504 |

How the modes behave:

- **q = 12** follows e^{−0.1046x} over 20 octaves, from 0.197 down to 0.025.
- **q = 53** decays only from 0.064 to 0.056.
- **Generic modes** (q = 5, 17) die quickly, down to a floor of about 3e-4.
- **Fit quality.** `test_rates.py` fits all q ≤ 1023 between 2^21 and 2^29. Among modes above 30σ, measured and predicted
  rates correlate at 0.94–0.96 for all three basins, with a median error of 0.006/octave.
- **Exceptions** are a few high-q modes (q = 718, 865, 971) whose amplitude does not yet decay as predicted. They may
  still be transients, or show a breakdown of H or of the O(q/n) phase error at small n. I am labelling this an open
  discrepancy.

**Where the oscillation power sits.** The local density is rough at fine scales: more than 5000 modes with q < 32768 lie
above 10σ at 2^30 (`hispec.py`). They all sit at small ‖qθ‖: q = 1024, 1077, 1636, 1689, 1995 (ε = 1.9e-4), 3325,
15601, …. In the octave 2^30–2^31, the 327 values of q < 32768 with ‖qθ‖ < 0.005 carry 43% of the oscillation power.

At 2^30 the strongest local modes are q = 106 (0.071), then 53 (0.056), 971 (0.050) and 465 (0.047). The earlier finding
that "53 dominates" comes from the 240-bins/octave FFT, which suppresses high q. Also, 665 aliases to 55 at 240 bins.

### 2b. Phase stability (`phases.py`)

The phase of c_{1,q} in window [a, a+2] should drift as 360°·f_q·(a+1).

**Basin 1 after subtracting the predicted drift:**
- q = 12: −120.0° ± 0.7° for every window from 2^11 to 2^32. The raw phase moves by 240°.
- q = 53: 39.0° ± 0.4° from 2^18 to 2^32 (transient below 2^16).
- q = 106: 96.5° ± 0.5°.

So the oscillation is a stable, quasi-periodic function of log₂n with frequency 12.0327 (respectively 53.0071, 106.0136)
cycles per octave, not exactly 12 or 53. The peak spacing of the low-passed cumulative p₁ is 0.0831 octaves, a ratio of
1.0593 (`cumul.py`). The prediction is 1.05928, against the semitone 1.05946.

**Relative phases of the three basins.** Since g₁+g₅+g₁₇ = 1, the coefficients satisfy c₁ + c₅ + c₁₇ = 0 exactly. They form
a closed triangle, and its angles are fixed by the three amplitudes. They are **not** a symmetric 120° three-phase pattern.

| mode | relative phases (basin 1 → 5 → 17 → 1) | amplitudes (basins 1, 5, 17) | stable over |
|---|---|---|---|
| q = 12 | 130°, 134°, 96° | 0.025, 0.034, 0.026 at 2^30 | 2^13–2^32 |
| q = 53 | 137.5°, 130°, 92.4° | | |
| q = 106 | 187°, 346°, 187° | | |

At q = 106, basins 5 and 17 oscillate nearly in phase (−14°), and basin 1 is in antiphase with both.

### 2c. Out-of-sample Monte Carlo far beyond 2^32 (`mcfar.c`, `mcfar_cmp.py`)

Setup: 4·10^6 random odd n per octave with log₂n uniform in [a, a+1); the basin is found by direct iteration. The
prediction is c(a) = c_exact(2^30)·e^{−β_q(a−30)} with the complex β_q, so both amplitude and phase are extrapolated. The
noise in 2|c| is about 3e-4.

Results for basin 1:

| q | octave | MC 2\|c\| | predicted 2\|c\| | MC phase | predicted phase |
|---|---|---|---|---|---|
| 12 | 2^40 | 0.0083 | 0.0085 | −4.9° | −6.5° |
| 12 | 2^50 | 0.0033 | 0.0030 | 118.5° | 111.1° |
| 12 | 2^60 | 0.0011 | 0.0011 | −142° | −131° (phase noise ≈ 15°) |
| 53 | 2^40 | 0.0527 | 0.0531 | 141.3° | 141.5° |
| 53 | 2^50 | 0.0503 | 0.0505 | 167.2° | 167.1° |
| 53 | 2^60 | 0.0482 | 0.0482 | −167.1° | −167.2° |
| 106 | 2^60 | 0.0422 | 0.0417 | 30.1° | 30.6° |

Basins 5 and 17 agree equally well. The full table is printed by `mcfar_cmp.py`. As a side result, the proportions at
2^60 are (0.3268, 0.3251, 0.3481), the same as at 2^30.

### 2d. Which mode dominates, and when does 665 overtake 53? (`extrap.py`)

**Extrapolation rule.** I extrapolate every mode above 10σ at 2^30 (about 5000 modes, q < 32768) with its predicted rate.
This assumes the constants C_{j,q} are already established, which is a heuristic assumption.

**Cumulative proportion.** For p_j(n) = (1/#{odd ≤ n})·Σ_{odd ≤ n}, mode q is damped by ln2/|ln2 + 2πiq| ≈ 0.11/q. This
is why the asker sees the semitone: q = 12 is the smallest q with a slow decay. In the measured cumulative p₁ at 2^25–2^31,
2|c| is 2.8e-4 for q = 12 against 1.2e-4 for q = 53.

Extrapolated dominant mode of the cumulative p₁:

| range of n | dominant mode |
|---|---|
| up to n ≈ 2^37 ≈ 10^11 | 12 |
| 2^37 to about 2^790 ≈ 10^238 | 53 |
| about 2^790 to 2^1320 | 359 |
| beyond that | 1995 (= 3·665) |

In the cumulative proportion, **q = 665 overtakes q = 53 only at n ≈ 2^950 ≈ 10^286.**

**Local density (no 1/q damping).** In g, 106 leads up to 2^49 ≈ 10^15, then 53 leads, then 1995 from about 2^176
(10^53). There, 665 passes 53 at n ≈ 2^425 ≈ 10^128.

**Caveats.**
- The local-density ranking depends on resolution, because modes q > 32768 with even smaller ‖qθ‖ (multiples of 15601,
  …) are not measured.
- Every mode decays, so the conjecture implies p_j(n) → π_j. With slowest-rate exponents of order 10^{-3}–10^{-6} per
  octave, the convergence is extraordinarily slow. For example, the 53-mode decays like n^{−0.0070}.

## 3. Analog maps (n < 2^26; `gen.c`, `gen_modes.py`, `mix35.c`, `mix_modes.py`)

**(3n+d)/2^v for d = 5 and d = 13.** These have the same multiplier but different cycles: d = 5 has 5 cycles (minima 1,
19, 23, 187, 347) and d = 13 has 9. For d = 7 I found only the cycle {5, 11}, so it has no basin structure.

- The surviving modes are again the small-‖qθ‖ ones: 12, 41, 53, 94, 106, 147, 200, 253, 359, 412, 665, ….
- d = 5, largest basin at 2^24: top modes are 53 (0.059), 200, 253, 147, 359, 106.
- For q with ‖qθ‖ < 0.01 the median amplitude is 0.012, against 0.00035 (near noise) for ‖qθ‖ > 0.05.
- Measured rates match the *same* Wald rates, with correlation 0.97–0.99. Which mode is largest at small n differs by
  basin and by d (for d = 13 it is 41 or 106), because the C_{j,q} come from the boundary data.
- **Conclusion:** the frequency set is universal for multiplier 3, and the amplitudes are not.

**Control with a different multiplier.** T(n) = (3n+1)/2^v if n ≡ 1 (mod 4), and (5n+1)/2^v if n ≡ 3 (mod 4); v ≥ 2
always. It has two cycles (minima 1 and 7).

- The random-walk model now predicts per-step phases e^{2πiq log₂3} or e^{2πiq log₂5} with probability 1/2 each. Surviving
  modes therefore need both ‖q log₂3‖ and ‖q log₂5‖ to be small.
- Observed top modes: 53, 441, 205, 935, 65, 612, 118, 323, …. Most of their rates match the generalized (★) root,
  for example q = 441 (0.036 measured, 0.033 predicted) and q = 205 (0.063, 0.073).
- q = 12 and 53 are still visible at 2^24 but now decay fast. The predicted rates are 0.197 and 0.060, and 53 was
  measured at 0.066.
- So the selected frequencies move with the multiplier, as the theory says.
- One anomaly: q = 995 has amplitude 0.018 and essentially no decay, against a predicted rate of 0.5. This is unexplained.
  It may be a structural artifact of the mod-4 rule.

## 4. Honest status

- **Exact:** the preimage identity in §1, and (★) as the plane-wave condition of the renewal equation.
- **Heuristic:**
  - H, independence of the basin from the residue mod 3;
  - independence of the landing point's integer part from its fractional part;
  - the assumption that the C_{j,q} are already settled by 2^30 for the extrapolations in §2d.
- **Strongly supported numerically:**
  - rates and frequency shifts with no free parameters, for about 40 modes over 20 octaves;
  - out-of-sample amplitude and phase agreement up to 2^60.
- **Not explained:** the values of C_{j,q}, the residual 3e-4 floor at generic q, and a few high-q anomalies.

## Files (all in this directory)

- `beta.py` — roots of (★)
- `stoptime.c` / `stoptime.txt` — odd-step statistics
- `fine.c` / `fine2048.u32` — 2048 bins/octave counts
- `fineoct.c` / `oct{22,30}_65536.u32` — 65536 bins/octave counts for single octaves
- `modes.py`, `modes2.py`, `table.py`, `test_rates.py` — mode amplitudes and rate tests
- `phases.py` — phase stability
- `hispec.py` — high-resolution spectrum
- `cumul.py` — cumulative proportions
- `extrap.py` — crossover extrapolation
- `mcfar.c` / `mcfar.txt` / `mcfar_cmp.py` — Monte Carlo test to 2^60
- `gen.c`, `gen_modes.py` — (3n+d)/2^v analogs
- `mix35.c`, `mix_modes.py` — the 3/5 multiplier control
