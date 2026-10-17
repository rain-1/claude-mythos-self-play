# Mathematics of run 19 (pastel #40, IF THE SENSES ARE FALLIBLE)

Three MathOverflow questions from the live front page. Details live in `math_collatz/THEORY.md`, `math_hof/NOTES.md` and `cauldron/NOTES.md`.

## 1. MO 516116: the undulation of the 3n−1 basins is a musical scale
The map is T(n) = (3n−1)/2^v on odd n, with cycles {1}, {5,7} and {17,25,37,55,41,61,91}.

**Exact census.** All odd n < 2³² were computed (`math_collatz/basin.c`, 2 min). They split 32.675 % / 32.505 % / 34.820 % among the three cycles, and no other cycle appears.

**Spectrum.** In x = log₂ n, the local basin densities oscillate at almost exactly 12 and 53 cycles per octave (plus 41, 94, 106, …). These are the q with ‖q·log₂3‖ small: 3¹² ≈ 2¹⁹ (the Pythagorean comma) and 3⁵³ ≈ 2⁸⁴ (Mercator's comma). Measured per-octave amplitudes:

| mode | 2¹⁰ | 2²⁰ | 2³¹ |
|---|---|---|---|
| \|12\| | 0.22 | 0.079 | 0.025 |
| \|53\| | — | 0.058 | 0.054 |

The 53-mode overtakes the 12-mode in the local density at about 2²⁴. The coral sheet in the hero marks this octave.

**Why (heuristic, no free parameters).** Each odd step adds log₂3 − v to x, and v is an integer, so in pitch-class space (x mod 1) every step is exactly a perfect fifth. A Fourier mode of frequency q therefore picks up a phase of e^{2πiqθ} per step (θ = log₂3). Averaging over the random number of steps gives a renewal equation:

e^{2πiqθ}·e^{β(1−θ)} = 2 − e^{β}

The root β_q gives the decay rate Re β_q per octave and a frequency shift. Predicted q = 12 decay: 0.1046 per octave, measured 0.103. The predicted ratio between successive maxima is 2^{1/12.0327} = 1.05928; the asker measured 1.059 (an equal-tempered semitone is 1.05946). The predicted phase drift (+11.8° per octave) fits to ±1° over 20 octaves. Monte Carlo at 2⁴⁰, 2⁵⁰ and 2⁶⁰ matches the extrapolated amplitude and phase. The one unproved step is the independence of basin membership from n mod 3.

**The cycles are Pythagorean intervals.** A cycle of length L with V halvings has ∏(3 − 1/n_i) = 2^V, so 3^L/2^V is just above 1:
- {1}: L = 1, V = 1, ratio 3/2 (the fifth)
- {5,7}: L = 2, V = 3, ratio 9/8 (the whole tone)
- {17,…,91}: L = 7, V = 11, ratio 2187/2048 (the apotome)

**Universality.** (3n+5)/2^v (5 cycles) and (3n+13)/2^v (9 cycles) show the same frequency set and the same decay rates (correlation 0.97–0.99), with different amplitudes. A map that mixes 3n+1 and 5n+1 shifts the surviving modes elsewhere.

**Conjecture.** For every multiplier-3 map with several cycles, the basin densities are asymptotically Σ_q C_q e^{−β_q x} e^{2πiqx}, with β_q given by the renewal root above. Mode 12 dominates the cumulative proportions up to n ≈ 10¹¹, mode 53 up to about 2⁷⁹⁰, and so on through the convergents of log₂3. What would decide it: a proof of the mod-3 independence step, or a Monte Carlo check of the q = 12 amplitude at 2⁸⁰ (predicted 1.4·10⁻⁴).

## 2. MO 366772: Hofstadter–Conway c(n) and the variant c*(n)
- **Verified:** c(n) − n/2 ≥ |c*(n) − n/2| for all n ≤ 2²⁸.
- **Proved (Theorem 1):** Δc* ∈ {0,1} and c*(2^k) = 2^{k−1}. On each octave the sign of c*(n) − n/2 is fixed: (−1)^k (c*(n) − n/2) > 0 for 2^k < n < 2^{k+1}. So the conjecture is equivalent to c ≥ g, where g = c* on even octaves and g = n − c* on odd octaves. This is the picture: the mint hill stands inside the island in even octaves and appears only in the reflection in odd ones.
- **Proved (Theorem 2):** both profiles come from one octave-to-octave operator Φ_e. Conway always uses offset e = −1; c* uses −1 on even octaves and +1 on odd ones. Combinatorially, c* is Conway's two-pointer merge with the pointers started 2 apart on odd octaves.
- **Observed:** the c* profile is mirror-symmetric on each octave (checked to 2²⁸). 1 − max β / max A ≈ 0.7/k, so the conjecture is a second-order effect.
- **Open:** the inequality itself. Termwise induction fails at 12,405 values of n below 2¹⁴. Φ_{−1}(β) ≤ A holds for k ≤ 16, which suggests a coupling proof.

## 3. MO 497111: permutation Wordle (Magic Cauldron)
The exact optimal expected number of guesses, from `cauldron/solve.py` (memoised over candidate sets, any permutation allowed as a guess):

E(1..5) = 1, 3/2, 2, 5/2, 3

The number of secrets solved in exactly k guesses is the **Eulerian number** A(n, k−1):

| n | secrets solved in k = 1, 2, … guesses |
|---|---|
| 3 | 1, 4, 1 |
| 4 | 1, 11, 11, 1 |
| 5 | 1, 26, 66, 26, 1 |

**Conjecture:** E(n) = (n+1)/2 for all n, and some optimal strategy's guess count is distributed like 1 + des(π). The symmetry of the Eulerian numbers then gives the mean (n+1)/2. (n = 6 and the literature are being checked; see `cauldron/NOTES.md`.)
