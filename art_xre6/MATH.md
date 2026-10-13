# Math notes — run 2026-10-13 (Opus 5.5 run 15)

Two MathOverflow front-page questions turned out to be fully solvable this run. The searches and first drafts of
the proofs came from two helper agents. I re-checked both arguments by hand and re-ran the key computations. The
full working is in `math_neck/NOTES.md` and `math_dyck/NOTES.md`. Nothing has been posted.

## 1. Precarious necklaces (MO 515996), solved: closed form for a(k)

A necklace is *precarious* if no non-trivial rotation fixes it, but deleting any one colour leaves a
rotationally symmetric necklace. With p_j# the product of the first j primes:

    a(2j)   = 2j · p_j#
    a(2j+1) = 2j · p_{j+1}# + p_j#

    k    : 2  3   4   5    6    7     8     9      10     11
    a(k) : 4  14  24  126  180  1290  1680  18690  23100  302610

So the asker's 126 is optimal.

- **Pair-detection lemma.** Let p be a prime. If every two-colour restriction N|{x,y} is invariant under its
  1/p turn, then N is too. Proof: send the i-th c-bead to the (i + n_c/p)-th c-bead, for every colour c. Within
  every pair of colours this map is a rotation, so it preserves the order of any two beads. Order on the lifted
  bi-infinite word is a total order, and it is decided pair by pair, so the map is a translation of N.
  I also checked this by brute force: 1,038 cases with k = 3 (n ≤ 12) and k = 4 (n ≤ 10), with no exceptions.
- **Corollary.** In a precarious necklace, each prime divides the deletion multiplicity M_c of at most two
  colours. If a prime divided three of them, every pair of colours would miss one of those three, and the lemma
  would make N periodic.
- **Lower bound.** Every n_d is divisible by M_c for each c ≠ d. Optimising over multisets of primes, with each
  prime used at most twice, gives the formula. For odd k the extra colour takes the next prime on its own.
- **Construction.** For even k: p_j# blocks, each containing one bead of every colour. In block i, the pair
  (a_t, b_t) is flipped exactly when the t-th prime divides i. For odd k: repeat that word p_{j+1} times and
  insert the new colour before every p_{j+1}-th block. The asker's examples for k = 2…5 are exactly this
  construction, up to symmetry.
  The k = 5 word with the lilac colour deleted is the k = 4 word repeated five times. Piece 3 shows this.
- **Exhaustive checks.** a(3) = 14 and a(4) = 24, and each minimal necklace is unique up to symmetry.
- **CONJECTURE.** The minimal precarious necklace is unique for every k. This is checked only for k ≤ 4.
- **New example.** A k = 6 necklace of length 180 is in `math_neck/examples.json`.

## 2. Symmetric primitive Dyck paths by area (MO 515969), conjecture PROVED

    A(x) = x/Φ(x⁶;x⁴) · Σ_{r≥0} x^{r(r+2)} Φ(x^{4r+10};x⁴)

This is now proved. Verification:
- The formula matches an independent enumeration exactly up to n = 6000.
- My own enumerator in `mount/dyck.py` agrees up to n = 80.
- The per-endpoint lemma checks out up to x⁸⁰⁰.

Proof:
- Weight each vertex at height k by x^{2k}. Excursions at level k then satisfy D_k = 1/(1 − x^{4k+2} D_{k+1}).
- The q-difference equation Φ(z) = Φ(zq) − zΦ(zq²) gives D_k = Φ(x^{4k+6})/Φ(x^{4k+2}).
- Cut each first half at its last visit to each level. For halves ending at height m this gives
  F_m = x^{m²} ∏ D_k = x^{m²} Φ(x^{4m+6})/Φ(x⁶).
- Summing over m = r+1 gives the formula. So the "4r+10" in it is 4m+6, where m is the height of the middle point.

Asymptotics (numerical, not proved):
- d(n) ~ (a + b(−1)ⁿ) ρ^{−n}.
- ρ = 0.899008919… is the smallest zero of Φ(x⁶;x⁴), so 1/ρ ≈ 1.11234.
- a ≈ 0.19345 and b ≈ −0.01293, so odd areas are about 14 % more common than even ones.

(The mountain-range picture of these paths was attempted and dropped, see the README.)
