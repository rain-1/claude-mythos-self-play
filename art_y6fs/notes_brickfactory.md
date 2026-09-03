# Notes — The Brick Factory (MO 514851, Turán's brick factory)

**Object.** Zarankiewicz's drawing of K_{n,m}: the n vertices of one side on the x-axis
(half on each side of the origin), the m of the other on the y-axis, every edge a straight
segment. Its crossing count is exactly
Z(n,m) = ⌊n/2⌋⌊(n−1)/2⌋⌊m/2⌋⌊(m−1)/2⌋; Zarankiewicz's conjecture says no drawing does
better, and this is proved for min(n,m) ≤ 6 (Kleitman 1970) and for K_{7,7}…K_{7,10}
(Woodall 1993). The drawn K_{16,16} has 256 edges and 3136 crossings, counted exactly by
segment intersection tests, equal to Z(16,16).

**The (3,3)-even relaxation (the MO question).** A function g on the C(n,2)·C(m,2)
"quadrilaterals" X = {a,a'}∪{b,b'} is (3,3)-even if its sum over the 9 X inside any
A₁∪B₁ (|A₁|=|B₁|=3) vanishes mod 2. R(n,m) = min #zeros. The poster shows R ≤ Z (the
drawing supplies a g with a zero exactly at each crossing) and R ≥ n(n−1)m(m−1)/36;
an answer improved the lower bound to 1/24. Asked: the asymptotics.

**Structure.** Write g as a C(n,2)×C(m,2) matrix M over GF(2). The condition is
T_n M T_mᵀ = 0 where T_k is the triple-contains-pair incidence matrix, and ker T_k is the
cut space of K_k (dimension k−1: a pair-function is even on every triangle iff it is a cut).
Hence the solution space is {A + B : columns of A are cuts of K_n, rows of B are cuts of K_m},
of dimension C(n,2)C(m,2) − (C(n,2)−n+1)(C(m,2)−m+1), and

    max weight = max over B  Σ_columns f  max over cuts c of K_n  popcount(B[:,f] ⊕ c),

which needs only (2^{m−1})^{C(n,2)} choices of B with the inner maximum precomputed
(`even33.py`). Exhaustive Gray-code enumeration of the full code (`brickfactory.py`,
R_exact) agrees on (3,3), (3,4), (3,5), (4,4).

**Result: R(n,m) = Z(n,m) in every case computed.**

| n,m | |F| | max weight | R(n,m) | Z(n,m) |
|---|---|---|---|---|
| 3,3 | 9 | 8 | 1 | 1 |
| 3,4 | 18 | 16 | 2 | 2 |
| 3,5 | 30 | 26 | 4 | 4 |
| 3,6 | 45 | 39 | 6 | 6 |
| 3,7 | 63 | 54 | 9 | 9 |
| 3,8 | 84 | 72 | 12 | 12 |
| 3,9 | 108 | 92 | 16 | 16 |
| 4,4 | 36 | 32 | 4 | 4 |
| 4,5 | 60 | 52 | 8 | 8 |
| 4,6 | 90 | 78 | 12 | 12 |
| 4,7 | 126 | 108 | 18 | 18 |

(4,6) took 72 s and (4,7) 103 min on the 64⁶ row choices; (5,5) would be 16¹⁰ and (4,8)
128⁶ — the next step needs the K_n cut symmetry or a MaxSAT solver, not enumeration.

**Conjecture.** R(n,m) = Z(n,m) for all n, m — the parity relaxation is tight. Since
R(n,m) ≤ cr(K_{n,m}) ≤ Z(n,m) (any good drawing yields a (3,3)-even g with a zero at each
crossing), this conjecture is *stronger* than Zarankiewicz's conjecture, and it answers the
poster's asymptotic question with n²m²/16. What it would take: the first open crossing case
is K_{7,11} (Z = 225); R(7,11) is a maximum-weight-codeword problem in a 480-dimensional
binary code of length 1155 — out of reach of enumeration, but a SAT/ILP attack on the
product structure (rows-in-cuts-of-K₁₁ plus column-wise best cut of K₇) is conceivable; a
proof would presumably go through the same counting as Kleitman's, with the (3,3)-even
condition replacing planarity of K_{3,3}.

**The picture.** Edges tinted by quadrant (apricot / aqua / lavender / pistachio, one
per pair of half-axes), thin ink over them, every crossing a coral bead whose size grows
with the crossing load of its two edges, the 32 vertices as ink dots on the two axes.
