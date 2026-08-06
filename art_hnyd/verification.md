# Verification — WHAT THE REPLACEMENT KEEPS (`art_hnyd/`)

Triptych, 2026-08-06. Phil.SE seed: "Recurring Consciousness Replacement Theory"
(consciousness replaced each instant, inheriting all memories, keeping the illusion
of continuity). Three MO threads about what survives repeated replacement.

---

## Piece 1 (hero, 4096²): THE LAST TO SETTLE — MO 513971 (0 answers, fresh)

**Question.** A ∈ {0,1}^(n×n); alternately sort rows into lex order, then columns
(read top-down), starting with rows; T(A) = first t ≥ 1 with A^(t) fixed by both.
Poster: exact μ_n = E[T] for n ≤ 4, MC to n = 100, worst case max T = 2n − 3;
asks for asymptotics of μ_n.

**Our verification of the poster's data** (`exact_small.py`, exhaustive over all
2^(n²) matrices):
- μ₁ = 1, μ₂ = 21/16, μ₃ = 105/64, μ₄ = 125387/65536 — all EXACT MATCHES.
- max T = 3 (n=3), 5 (n=4) — matches 2n−3.
- poster's worst-case construction verified to give T = 2n−3 at
  n = 5, 8, 12, 20, 50, 120 (`mc_scale.py`).
- MC μ₉₆ = 4.6275 ± 0.0115 vs poster's μ₁₀₀ ≈ 4.63 — reproduction.

**New exact value** (exhaustive over all 2^25 five-by-five matrices):

    μ₅ = 36573599 / 2^25 = 2.179956376552582...   (poster had only MC ≈ 2.18)
    max T = 7 = 2n−3 now EXHAUSTIVELY confirmed for n = 3, 4, 5.

**New MC data far past the poster's n = 100** (`mc_scale.py` + `mc_topup.py`,
seeds 20260806 / 77000513971): μ_n measured to n = 8192; e.g.
μ₂₅₆ = 4.936 ± 0.019, μ₁₀₂₄ ≈ 5.11, μ₄₀₉₆ ≈ 5.3 (pooled), μ₈₁₉₂ ≈ 5.1–5.3.

**Law fit** (`analyze_sorting.py`, weighted LS on n ≥ 16): among
{lnln, (ln)^{1/2}, (ln)^{1/3}, ln, (lnln)²}, the iterated-log law wins by a
factor ≥ 2 in χ²/dof:

    μ_n ≈ 2.00 + 1.71 · ln ln n

**CONJECTURE (stated for the record).** T(A_n) / ln ln n → c in probability,
c ≈ 1.7–2; equivalently μ_n = a + b ln ln n + o(1)-corrections. Mechanism
(supported by the per-pass displacement cascade, e.g. n = 4096 hero trace:
row/col permutation displacement 5.65M → 5.60M → 36028 → 1640 → 44 → 0):
after the first two sorts, disorder survives only inside blocks of rows
(columns) that agree on the prefix of columns (rows) already effectively
frozen; each further alternation roughly SQUARES the rarity of surviving ties,
and a doubly-exponential contraction of the disorder scale needs Θ(log log n)
rounds. The final acts are adjacent swaps of near-identical lines: at n = 4096
the last sort performed exactly 22 adjacent column swaps (displacement 44).

Hero facts (seed rng 513971): T = 6; last-change strata populations
1.52M / 3.01M / 5.48M / 2.26M / 2.89M / 90462; 1423 rows still moving at pass
5, 44 columns (22 adjacent swaps) at pass 6; 129 cells changed in all 6 passes.

## Piece 2 (2560²): THE LEDGER OF SIGNS — MO 513954 (0 answers)

**Question.** D real diagonal (possibly singular), x with Δ = xᵀDx ≠ 0, w = Dx,
M = D − wwᵀ/Δ. Is inertia(M) = (n₊−1, n₋, n₀+1) for Δ > 0 and
(n₊, n₋−1, n₀+1) for Δ < 0, without assuming D invertible?

**Answer: YES.** One congruence suffices (no D⁻¹ anywhere). H = ker(wᵀ) has
dim n−1 and ℝⁿ = H ⊕ span{x} because wᵀx = Δ ≠ 0. Take P = [Z x], Z a basis
of H. Then (all by direct multiplication):
- ZᵀDx = Zᵀw = 0, so PᵀDP = diag(ZᵀDZ, Δ);
- ZᵀMx = Zᵀw − (Zᵀw)(wᵀx)/Δ = 0 and xᵀMx = Δ − Δ²/Δ = 0, and
  ZᵀMZ = ZᵀDZ − 0 (since Zᵀw = 0), so PᵀMP = diag(ZᵀDZ, 0).
Sylvester's law twice: inertia(D) = inertia(ZᵀDZ) + (1,0,0) or (0,1,0)
according to sign Δ; inertia(M) = inertia(ZᵀDZ) + (0,0,1). Subtract. ∎
(This also answers the "does Sylvester immediately establish it" sub-question:
yes — the poster's own congruence is complete; the only point to make explicit
is that Zᵀ(wwᵀ)Z = 0 kills the downdate term on H.)

The corollary as stated also holds: on a connected domain with Δ(y) ≠ 0 and
M(y) ⪰ 0, Δ has constant sign (continuous, nonvanishing, connected domain);
if negative, n₋(D(y)) ≡ 1, and the index of the unique negative diagonal entry
is locally constant (d_i(y) < 0 is an open condition and indices can only swap
through a point with n₋ ≠ 1), hence constant.

**Verification** (`inertia_verify.py`):
- (a) float: 2982 random diagonal cases n ≤ 40 with many exact zero diagonal
  entries + n = 200, 400 with n/3 zeros — 0 failures.
- (b) EXACT rational arithmetic: 380 random cases n ≤ 9 (Fractions,
  Schur-complement congruence with 1×1 and [[0,b],[b,0]] 2×2 pivots) — all pass.
- (c) iterated cascade M ← M − (Mx)(Mx)ᵀ/(xᵀMx) on GENERAL symmetric M
  (the same proof applies verbatim — D was never required to be diagonal, only
  symmetric): a random signature-(35,20,5) matrix (rank 55) died in EXACTLY 55
  replacements with the inertia law asserted at every step; final |M| < 2e-12.

Piece 2 renders a signature-(66,42,12) operator drained in exactly 108
replacements (`cascade_data.py`): eigenvalue magnitudes are wildly
non-conserved along the way (small-|Δ| replacements fling the survivors), yet
the inertia ledger ticks down one unit per step — Sylvester's law is the only
thing the replacement keeps.

## Piece 3 (2560²): ATLAS PIECE 41 — ℤ[√2] census to 10¹¹ (channel 17)

(filled in after the deep census lands — see `atlas41_notes.md`)

Rig: `sqrt2_deep41.c` = piece 40's segmented full-factorization sieve + fast
word-scan run pass. Recompiled from the previous branch and re-certified:
|S|(4×10⁹) = 601,376,078 = piece 39/40's value EXACTLY, per-gap run tables
byte-identical (`cert_4e9_rungap.txt`).
