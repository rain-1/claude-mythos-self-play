# MO-ready drafts (not posted; for the repo owner to use or ignore)

## Draft comment for MO 513971 (alternating lexicographic sorting)

Some computational data extending yours, plus a conjecture. (i) Exhaustive
enumeration over all 2^25 matrices gives the exact value
**μ₅ = 36573599/2^25 = 2.17995637...** (your MC said ≈2.18), and confirms
max T = 7 = 2n−3 exhaustively for n = 5 (it also reconfirms your exact
μ₁..μ₄ and your worst-case construction for several larger n). (ii) MC far
past n = 100 (≥ 10^4 trials per point up to n = 512, hundreds beyond,
n up to 8192): μ₂₅₆ ≈ 4.936(19), μ₁₀₂₄ ≈ 5.11(3), μ₂₀₄₈ ≈ 5.27(5),
μ₄₀₉₆ ≈ 5.3(1). Among two-parameter laws a + b·f(n) with
f ∈ {ln ln n, (ln n)^{1/2}, (ln n)^{1/3}, ln n, (ln ln n)²}, weighted least
squares on n ≥ 16 prefers **μ_n ≈ 2.0 + 1.7 ln ln n** by a factor > 2 in
χ²/dof over every rival. (iii) Mechanism data: the total displacement of the
sorting permutation collapses super-exponentially along a run — e.g. one
n = 4096 sample gave 5.65×10^6, 5.60×10^6, 36028, 1640, 44, 0 across its six
passes; the late passes are entirely adjacent transpositions of
near-identical lines (the final pass was exactly 22 adjacent column swaps).
Notably the tie DEPTH of swapped pairs does not grow with the pass
(it stays ≈ log₂ n throughout); what decays is the population of unstable
deep-tied pairs. The endgame is a dependency chain through the deciding
prefix: in that sample, all 22 final column swaps first differed at row 16,
and all were triggered by one 3-cycle of rows 16-18 in the previous pass —
row order among the first ~log₂ n rows decides column order, which decides
row order, and so on. **Conjecture: T(A_n)/ln ln n → c in probability
(c ≈ 1.7–2), i.e. μ_n = Θ(log log n).**

## Draft answer for MO 513954 (inertia of the structured downdate)

**Yes — and your congruence is already the whole proof; no invertibility of D
is used anywhere.** Let w = Dx, Δ = xᵀDx ≠ 0, M = D − wwᵀ/Δ. Since
wᵀx = Δ ≠ 0, the hyperplane H = ker wᵀ satisfies ℝⁿ = H ⊕ span{x}. Choose Z
with columns a basis of H and set P = [Z x] (invertible). Then:

* ZᵀDx = Zᵀw = 0, so PᵀDP = diag(ZᵀDZ, Δ);
* ZᵀMZ = ZᵀDZ − (Zᵀw)(wᵀZ)/Δ = ZᵀDZ, ZᵀMx = Zᵀw − (Zᵀw)(wᵀx)/Δ = 0,
  xᵀMx = Δ − Δ²/Δ = 0, so PᵀMP = diag(ZᵀDZ, 0).

By Sylvester's law applied twice,
inertia(D) = inertia(ZᵀDZ) + (𝟙{Δ>0}, 𝟙{Δ<0}, 0) and
inertia(M) = inertia(ZᵀDZ) + (0, 0, 1); subtracting gives exactly your
formula, singular D included. (The only point worth making explicit beyond
your sketch is that the downdate term dies on H because Zᵀw = 0 — that is
what makes the (1,1) blocks of PᵀDP and PᵀMP literally equal.)

Note D need not be diagonal: the argument uses only symmetry, so for any
symmetric A with Δ = xᵀAx ≠ 0, A − (Ax)(Ax)ᵀ/Δ loses exactly one sign-unit
(of sign Δ) to the kernel. Iterating with fresh x therefore kills a rank-r
symmetric matrix in exactly r steps — a rank-revealing "inertia peeling".
Corollary (your connectedness statement): on a connected domain where
Δ(y) ≠ 0 and M(y) ⪰ 0, Δ has constant sign; when Δ < 0, n₋(D(y)) ≡ 1 and
{y : d_i(y) < 0} is open for each i, so the negative index is locally
constant, hence constant. (All of this verified numerically: 3000 float
trials with very singular D up to n = 400, and 380 trials in exact rational
arithmetic; code in the linked repo.)
