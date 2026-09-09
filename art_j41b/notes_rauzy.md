# Notes — *Three Letters, One Shadow* (the Rauzy fractal)

**Object.** σ: 1 → 12, 2 → 13, 3 → 1 (Tribonacci substitution), fixed point u = 1213121121312…
Incidence matrix M = [[1,1,1],[1,0,0],[0,1,0]], Perron root β = 1.839286755 (β³ = β² + β + 1), complex
conjugates α, ᾱ with |α|² = 1/β (certificate `beta_times_abs_alpha_sq = 1.0000000000000`: the product
of the three roots is 1, so β|α|² = 1 exactly). Left eigenvector v for α, gauge v₁ = 1:
v₂ = −1.41964 + 0.60629 i, v₃ = −0.77184 − 1.11514 i.

**Two constructions, one set (certificate 1).** The *walk* z_n = Σ_{k≤n} v[u_k] and the *digits*
z_n = Σ_j d_j α^j (n = Σ d_j T_j the greedy Tribonacci expansion, T = 1, 2, 4, 7, 13, …, no '111')
agree to 4.4·10⁻¹¹ over all n ≤ 200,000 (`rauzy.py certify`). Proof sketch: the prefix of length
n = Σ d_j T_j is the concatenation σ^{j₁}(1) σ^{j₂}(1)… (greedy, descending j), and
v · l(σ^j(1)) = v Mʲ e₁ = αʲ v₁. So the Rauzy fractal R = closure{z_n} is the set of values of all
admissible digit strings, and a digit string is an *address*: the first branch (d₀ = 0 / 10 / 110)
says which of the three subtiles R₁, R₂, R₃ the point lies in, the next branch says which
sub-subtile, and so on — the same three-way split at every scale, which is the whole picture.

**Letter rule (certificate 2).** u_{n+1} = 1 if d₀ = 0, 2 if (d₀,d₁) = (1,0), 3 if (d₀,d₁,d₂) = (1,1,0):
checked for all n ≤ 200,000. Counts of admissible strings of length k = T_k (1, 2, 4, 7, 13, 24, …) for
k ≤ 11 — the branching recursion is the Tribonacci recursion.

**Areas (certificate 3).** area(R₁) : area(R₂) : area(R₃) measured by pixel majority on the 1024
proto = 1 : 0.5440 : 0.2959; predicted 1 : 1/β : 1/β² = 1 : 0.5437 : 0.2956. (The subtiles are affine
copies: R₁ = αR, and each further branch contracts by α.) Points per pixel ≈ 19–20 on every sheet
(K = 27 digits at 1024, 30 at 2560: 15.9 M and 98.95 M points).

**Tiling (certificate 4).** Λ = ⟨v₁ − v₃, v₂ − v₃⟩ = π(ℤ³ ∩ {x₁+x₂+x₃ = 0}). R + Λ tiles the plane: the
twelve nearest translates overlap the central tile only along boundaries (overlap ≤ 0.20 % of the
area for the six touching neighbours ±(1,0), ±(0,1), ±(1,−1); zero for the rest), and the union of
the thirteen tiles covers 100.0 % of the central disc of radius 0.45 W. Six translates touch the tile
(within 2 px at 2048², `rauzy_extra.json`).

**Domain exchange (certificate 5).** E(z) = z + v_i on R_i is a bijection of R modulo boundaries: the
translated pieces R_i + v_i lie outside R by 0.047 %, 0.031 %, 0.008 % of their area (the coral outlines
in the picture are these three translates — they form the tile's second partition).

**Boundary.** Box-counting of the boundary at 2048² (scales 2–32 px) gives 1.025; the literature
value for the Hausdorff dimension of ∂R is 1.0933 (Ito–Kimura 1991, from the boundary's own
substitution). The grid is too coarse for a fair test — the boundary's structure below 2 px is lost —
so this is recorded as a limitation, not a discrepancy. A next run could use the boundary automaton.

**The philosophy seed.** *What is completeness?* (Phil.SE 141442). The walk visits countably many
points and never returns to one; its closure — the completion — is a compact tile with a fractal
rim that fills the plane by translation. What was a sequence of three letters becomes a shape only
when you add the points it never reaches.
