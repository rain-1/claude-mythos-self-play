# Verification ledger — run 2026-08-07 (`art_71k0/`)

Everything drawn is computed from scratch in this directory; every claim below
names its certificate. (Numbers marked ⏳ are finalized at the end of the run.)

## Piece 1 — THE SYNTHESIS (MO 513971, alternating lexicographic sorting)

**Object.** A ∈ {0,1}^{n×n}; R sorts rows lexicographically, C sorts columns
(read top-to-bottom); A⁽¹⁾=R(A), A⁽²⁾=C(A⁽¹⁾), …; T(A) = min{t ≥ 1 :
A⁽ᵗ⁾ row- and column-sorted}. μ_n = E[T] under iid Bernoulli(1/2).

**Reduction (new, trivial but load-bearing).** A⁽¹⁾ = R(A) depends only on the
*multiset* of rows, hence so does T. So the exact μ_n needs
C(2ⁿ+n−1, n) multiset evaluations instead of 2^{n²}:
n=6: 1.2×10⁸ (5 s), n=7: 9.36×10¹⁰ (~1 core-day, ran here in ~2 h wall).

**Certificates.**
- `sort_brute.py` (straight from the definition, all 2^{n²} matrices, n ≤ 4)
  reproduces the poster's exact values μ₁=1, μ₂=21/16, μ₃=105/64,
  μ₄=125387/65536 — and `sort_exact.c` (multiset path) matches it exactly for
  n = 2, 3, 4. Two independent implementations agree with each other and with
  MO 513971.
- Worst case: max T = 2n−3 attained at every n ∈ {3,…,7} by exhaustive census
  (witness row-multisets printed in `exact*.txt`), matching the poster's
  theorem max T = 2n−3.
- **New exact values** (`exact5.txt`, `exact6.txt`, `exact7.txt`):
  - μ₅ = 36 573 599 / 2²⁴ ≈ 2.179 956 377
  - μ₆ = 168 401 367 693 / 2³⁶ ≈ 2.450 562 427
  - μ₇ = ⏳ (n=7 census, 93 594 900 020 multisets)
  with the full exact distribution of T at each n.
- MC (`sortmc.py`, `mc_mu.json` + `mc_mu2.json`): ~390k matrices across
  n = 8 … 16384. At overlapping n the MC brackets the exact values
  (e.g. exact μ₅ = 2.17996 vs poster's MC 2.18).
- Law: the local slope dμ/d(ln ln n) FALLS through the data: ≈2.4 (n≈10),
  ≈1.5 (n≈64), ≈1.1 ± 0.15 (n ≈ 2×10³…8×10³). Weighted fit on n ≥ 512:
  μ = 3.05 + 1.07·ln ln n (χ²/dof = 1.05); a holdout fit on n ≤ 2048
  overpredicts n = 3072…6144 by 2–3σ (slope still softening).
  **Data-led conjecture: μ_n = ln ln n + C + o(1)** (slope → 1); the
  poster's small-n range slope ≈ 2 is a finite-size effect; log₂log₂
  (slope 1.44) not yet excluded, slope 2 is.
  Mechanism instrument (`hero_experiments.py` + inline runs): the leading-block
  agreement depth with the final fixed point roughly doubles per round
  (e.g. n=4096: 8 → 13 → 21 → 1918 → 4096), and the final sort snaps the
  whole matrix at once; target depth ~2·log₂ n ties T to log₂ log₂ n.
- Inversion symmetry: starting with C instead of R gives the same law
  (transpose bijection) — verified μ_R ≈ μ_C within SE at n=64, 256 — while
  the two fixed points differ on ~1.6% of entries (260k pixels at n=4096,
  c=32; 1.95M at c=256) and T_R ≠ T_C on ~57–60% of matrices with
  corr(T_R, T_C) ≈ −0.02.
- Sparse fixed points (`hero_gen.py`, `hero_c*.npz`): the doubly-sorted
  Bernoulli(c/n) matrix is structureless away from its leading coastline
  (the log-curve of first-1 positions); rendered previews kept as documentation
  (`hero_c32_prev.png` etc.), which motivated the chart-based hero.

## Piece 2 — THE HOLDOUT (atlas piece 41, ℤ[√2] channel 17)

**Object.** S = {n : v_p(n) even for every prime p ≡ 3,5 (mod 8)} (absolute
norms of ℤ[√2]). A gap-g length-5 *fence* = 5 consecutive members of S in
arithmetic progression with gap g. Piece 40: channel 17 expected ≈5–6 fences
below 3.2×10¹⁰ under its model, observed 0, P < 1%.

**Rig certificates.**
- `hunt17` (windowed, orderly segmented full-factorization sieve, no global
  bitmap, range-resumable): on [0, 4×10⁹] reproduces |S| = 601 376 078
  EXACTLY (pieces 39/40), all 77 first-occurrence entries of the run tables,
  and the l=5 gap set {1,2,4,7,8,9,15,16,18} with per-gap counts
  40629/9723/772/1499/4785/1064/104/13/1 — identical to piece 39.
  On restart it re-found channel 14's first fence at n = 5 341 738 436
  (piece 40's discovery) from its own sieve.
- `diag17` (bitmap census at 4×10⁹ + window instrumentation): W5 fence counts
  match piece 39/40 exactly per gap; C5 pattern counts:
  **C5(17) = 40 647 vs C5(1) = 40 629 and C5(14) = 22 445 vs C5(2) = 22 009**
  — the gap-scaling theorem R(u·g)=R(g) confirmed at the raw pattern-count
  level (0.04% and 2%).

**New results (the anomaly dissected).**
1. **Rigidity lemma (PROVED by finite check + census confirmation).** Every
   gap-17 5-post pattern in S has n ≡ 14 (mod 16) and n ≡ 2 (mod 9).
   Proof: enumerate residues r mod 2^k (k = 4…8); a post m with v₂(m) = v ≤
   k−3 has its odd part determined mod 8, which must be ≡ ±1 (mod 8); the
   surviving residues project mod 16 onto exactly {14} at every level.
   Mod 27: posts with v₃ = 1 exactly are excluded; survivors are {2,11,20},
   projecting mod 9 onto {2}. (`rigidity_proof.py`; census: all 40 647
   patterns comply, mod 32 splitting into {14, 30}.) Consequence: **no
   residue-class mixture exists** for g=17 — the mixture explanation of
   fence deficits cannot apply to this channel.
2. **Frozen slots and informers.** Given the posts, 26 of the 64 window slots
   have conditional occupancy EXACTLY 0 (2-adically frozen); the hot slots
   (q ≈ 0.40) are ≡ 1, 3 (mod 8). Full profiles: `diag17_prof_g*.txt`.
3. **The conspiracy (negative association).** Window occupancy is
   *underdispersed*: var 5.08 vs Poisson-binomial (same marginals) 6.03.
   The empty class is suppressed ~5× relative to independence — measured on
   the speaking channels: g=15 observed 104 vs 542 expected (×5.2),
   g=16: 13 vs 65 (×5.0), g=18: 1 vs 2.6. Residue-class refinement (mod
   8…1440) recovers at most a factor ~2 for g=15 and nothing for g=17
   (`mask_models.json`) — the rest is genuine inter-slot correlation.
   **Shuffle control:** independently permuting each slot's column across the
   1.32M g=15 patterns (exact marginals kept, dependence destroyed) restores
   the zero class to 560 ≈ the Poisson-binomial 542.5 — vs 104 in the real
   data. The deficit is entirely in the dependence structure.
4. **The camps (measured, then PROVED).** The strongest slot correlations
   form a clique on the slots ≡ 6 (mod 8) — exactly those with v₂(n+j) = 2 —
   split into two anti-correlated camps {14,54} vs {6,30,38,62}
   (corr ≈ +0.2 within, −0.22 across; `g17_pairs.json`). Proof of the camps:
   write n = 16t+14 and c = ((j+14)/4) mod 8 for j ≡ 6 (mod 8); the slot's
   2-part passes iff 4t + c ≡ ±1 (mod 8), i.e. iff (t even & c ∈ {1,7}) or
   (t odd & c ∈ {3,5}) — so slots split by n mod 32 into camp-even
   {14,22,46,54} and camp-odd {6,30,38,62}; slots 22 and 46 are killed
   separately by v₃(n+j) = 1 (n+22 ≡ 6, n+46 ≡ 3 mod 9), leaving the
   measured camps exactly. One camp's silence is the other's speech: joint
   emptiness across both camps is what independence overprices.
5. **Corrected forecast.** With the measured deficit f ≈ 5:
   E₁₇(3.2×10¹⁰) ≈ 1.4 ⇒ P(silence) ≈ 25% — **piece 40's P<1% anomaly
   dissolves**; the deficit was in the model, not the channel. Corrected
   first-fence median depth ≈ 4–7×10¹⁰. Growth law X/(ln X)^{5/2} verified
   against the g=1 counts at 4×10⁹ → 3.2×10¹⁰ (constant A to 3%).
6. **Deep verdict: CHANNEL 17 SPEAKS.** First gap-17 fence at
   **n = 33 099 743 774** — only 1.03× past piece 40's 3.2×10¹⁰ shoreline,
   exactly where the conspiracy-corrected model put it (corrected
   E(3.3×10¹⁰) ≈ 1.4; the uncorrected model had already "expected" 5–6 and
   panicked). Independently certified by sympy factorization
   (`certify_fence.py 33099743774 17`): posts
   2·16549871887, 33099743791 (prime), 2⁶·3²·23·103·127·191,
   5²·41·71·454823, 2·11²·8999·15199 — all bad-prime valuations even, all 64
   windows non-members. The witness obeys the rigidity lemma:
   n ≡ 14 (mod 16), n ≡ 2 (mod 9), and sits in the mod-32 class 30 (camp
   {6,30,38,62} alive). The atlas's second predicted-then-heard channel —
   this time the prediction needed the conspiracy correction to be right.
7. **Final hunt tables ([2×10¹⁰, 1.6×10¹¹], `hunt_rungap_*.txt`).**
   Fence counts: g=14: 132 · g=15: 7590 · g=16: 689 · **g=17: 13** ·
   g=18: 20 · g=23: 1 · g=24: 10 · g=25: 0. **l = 6: ZERO at every gap**
   (the 24|g theorem and the >10¹³ first-fence estimate stand).
   THREE silent channels opened this run, all sympy-certified:
   - **17** at 33 099 743 774 (the riddle resolved);
   - **24** at 52 909 727 729 — its first three posts 52909727729,
     52909727753, 52909727777 are all PRIME (a prime 3-AP heads the fence);
   - **23** at 158 783 559 650 (99.2% of the way to the horizon — posts
     2·5²·3175671193, prime, 2⁴·3²·6703·164503, prime, 2·79391779871).
   Only channel 25 of piece 40's five silent channels remains silent.
   Count-vs-model honesty: with the depth drift of P0 priced (q_j fall as
   density thins ⇒ P0 rises ≈ ×1.7/decade), the in-range counts give
   gap-dependent deficit factors: ~1 (g=14), ~3–4 (g=17), ~5 (g=15, 16, 18).
   The qualitative resolution stands — channel 17 was never specially
   obstructed — and the gap-dependence of the conspiracy factor plus the
   drift-aware Poisson-binomial model is piece 42's opening question.

## Piece 3 — THE ROADS HOME (MO 513995, trinomial root roads)

- Symbolic (sympy, `trinomial_verify.py`): the poster's real-root formula
  d = (sinh 5θ − 5 sinh 3θ − 6 sinh θ)/16 is exact (sinh⁵ identity residual 0);
  the complex-root d-formula follows from Im/Re split:
  d = R sin 4ψ / sin 5ψ with R⁴ = sin ψ / sin 5ψ — our two-line derivation in
  the file header.
- Numeric: 60-digit certificates at the poster's own test values d = √3, 2, 10
  (max residual ≤ 3×10⁻⁵⁹ over all five roots each) and for the
  generalization R^{n−1} = sin ψ / sin nψ for n = 3…12 (max ~2×10⁻⁵⁸).
- Collisions: d* = (4/5)·5^{−1/4} = (256/3125)^{1/4} — double-root points
  x = ±5^{−1/4}; two independent expressions agree to 30 digits.
- Literature verdict (the MO question's actual ask): the R–ψ relation **is
  known** — P. Bohl (1908) characterized moduli of trinomial roots;
  Theobald–de Wolff, *Norms of roots of trinomials*, Math. Ann. (2016)
  (hypotrochoid geometry); and the exact sine-ratio form appears in
  Čermák–Fedorková–Jánský, *On moduli and arguments of roots of complex
  trinomials*, Pacific J. Math. 332 (2024). Comment-grade answer ready.
- Render certificate: every milestone root (np.roots at d = 0, ±¼, ±d*, ±1,
  ±2, all panels n=3…9) sits on the sampled road curve within 2.3×10⁻⁴
  (assert in `piece3_roads.py`, printed per panel).

## Environment / reproduction

gcc -O3 -march=native -fopenmp; python3 + numpy/scipy/Pillow/sympy/mpmath.
All heavy passes are single files: `sort_exact.c`, `hunt17.c`, `diag17.c`,
`diag2.c`. Seeds fixed in render scripts.
