# Verification — THE RANK AND THE WEIGHT (2026-08-03)

Triptych on *order vs magnitude*, seeded from the live MathOverflow and
Philosophy.SE front pages of 2026-08-03 ("Are ordinal probability rankings
more fundamental than cardinal probabilities?", MO 513791 on Scholz's
norm-of-units theorem, MO 513837 on a dyadic-layer formula for γ).

Everything below was computed from scratch in this repository; every claim
has a machine check in the listed scripts.

---

## 1. THE HALF-STEP (`half_step_4096.png`, hero)

**Object.** For every squarefree nonsquare d ≤ 10⁸ (60,792,693 values):
the continued fraction of √d — period P(d), regulator
R(d) = log ε_d = Σᵢ log((mᵢ+√d)/qᵢ) over one period — computed by
`pell_census.c` (OpenMP, ~8 min on 4 cores). Negative Pell
x² − dy² = −1 is solvable iff P(d) is odd, iff the fundamental unit of
ℤ[√d] has norm −1.

**Checks (`verify_pell.py`, all passed).**
- For all squarefree d ≤ 2000 and 4000 random d ≤ 10⁵ (later re-run with
  samples at 10⁸): recomputed the CF in exact bigint arithmetic, built the
  end-of-period convergent p/q, and confirmed **p² − dq² = (−1)^P exactly**,
  period match, regulator match vs mpmath log(p + q√d), and both sieve flags
  vs sympy factorization.
- OEIS A031396 (negative-Pell d) prefix reproduced below 300 with no
  discrepancy.
- Classic d = 61: period 11, fundamental solution 29718 + 3805√61 of norm −1.
- **Global theorem tripwire** over the full census (`pell_analyze.py`):
  no d with an odd period has a prime factor ≡ 3 (mod 4) — 0 violations in
  60.8M values (necessity of eligibility).

**Headline census numbers.**
- negative Pell solvable: 8,214,361 of 60,792,693 squarefree d (13.5%);
  among the 10,807,188 *eligible* d (no prime factor ≡ 3 mod 4): **0.76008**.
- The proven density limit (Stevenhagen's conjecture, Koymans–Pagano 2022,
  arXiv 2201.13424) is 1 − α = Π_{j odd}(1 − 2⁻ʲ) complement ≈ **0.58058**;
  the cumulative fraction crawls 0.847 → 0.760 from 10³ to 10⁸ — the
  celebrated log-slow convergence (cf. Bosma–Stevenhagen 1996 density
  computations, consistent with our curve). The horizon strip of the piece
  plots exactly this windowed fraction against the proven limit.
- Record regulators: absolute record d = 97,544,899 (P = 29,818,
  R = 35,048.6 → smallest Pell solution has 15,221 decimal digits, even
  period); gold record d = 99,890,389 (P = 28,965, R = 34,237.7 → 14,869
  digits, norm −1).
- Roads: Richaud–Degert d = m² + r with r | 4m have period ≤ 8 and
  R ≈ log 2m; height in the piece is log₁₀(R / ln 2√d), so they ride the
  horizon exactly.

## 2. THE LEDGER OF HALVES (`ledger_of_halves_2560.png`)

**Complete resolution of MO 513837.** With B_k = Σ 1/n over odd
n ∈ [2^(k−1), 2^k):

**Theorem (exact, finite, rational).**
  Σ_{k=1..N} (2 − 2^(k−N)) B_k = H_{2^N − 1}.

*Proof:* group H by odd part: n = 2ʲ·m, m odd in layer k contributes
2⁻ʲ/m, and n < 2^N ⇔ j ≤ N − k, so each 1/m receives weight
Σ_{j=0..N−k} 2⁻ʲ = 2 − 2^(k−N). ∎

Hence the poster's γ-limit is the classical H_M − ln M → γ along M = 2^N in
disguise; equivalently S_N − γ = ψ(2^N) − N ln 2 **exactly**, with pure
Euler–Maclaurin error −2^{−N−1} − 4^{−N}/12 + 16^{−N}/120 − … (Bernoulli;
no odd-order terms beyond the first) — 0.301 decimal digits per layer.
Not competitive as a γ algorithm (layer k holds 2^{k−2} terms; computing
B_k by ψ is circular). Same proof gives the base-b generalization
H_{b^N−1} = Σ (b − b^{k−N})/(b−1) · B_k^{(b)}.

**Checks (`gamma_layers.py`, all passed).**
- T1: identity verified EXACTLY in ℚ (Fraction arithmetic) for N ≤ 12.
- T2: per-odd-part weight bookkeeping recounted exactly at N = 10.
- T3: S_N − γ = ψ(2^N) − N ln 2 to ~4·10⁻⁴²⁰ at N = 10, 50, 200, 400.
- T4: error-law coefficients −1/2, −1/12, +1/120 confirmed at N = 60, 100.
- T5: base-3 version exact in ℚ at N = 8.
- Plus a float64-only direct summation of all 2³⁰ terms (no CAS, no ψ, no
  γ in the pipeline) landing within 5·10⁻¹⁰ of γ at N = 30, as the
  error law predicts.

## 3. THE FIFTH ATOM (`fifth_atom_2560.png`)

**Object.** Comparative probability orders on n atoms: strict total orders
on 2^[n] with ∅ first and de Finetti additivity
(A < B ⇔ A∪C < B∪C, C disjoint). Enumerated completely by `cp_enum.c`
(orientation-consistency DFS over canonical disjoint pairs):

- n = 3: **2** canonical orders (12 labeled) — matches Fine–Gill/Maclagan.
- n = 4: **14** canonical (336 labeled) — matches literature.
- n = 5: **546** canonical — matches literature.

**Representability census (`cp_represent.py`, all certified).**
- n ≤ 4: every order admits an agreeing measure — each verified by an
  exact rational weight vector (LP solution rationalized, then all 2^n − 1
  consecutive strict inequalities re-checked in Fraction arithmetic).
- n = 5: **516 representable / 30 non-representable** (the
  Kraft–Pratt–Seidenberg 1959 phenomenon). Every representable order has
  an exact rational measure; every non-representable order has an **exact
  integer Farkas witness**: 4 comparisons asserted by the order whose two
  sides are equal as multisets of atoms — e.g.
  {1,2} < {3}, {2,3} < {1,4}, {5} < {1,2,3}, {1,3,4} < {2,5}
  (each side sums to the multiset {1²,2²,3²,4,5}) — so no measure can
  satisfy all four, verified by integer arithmetic.
- **Structure of the flip graph** (verified in-render): the graph of
  single-adjacent-swap moves between the 546 orders is a **perfect
  matching**: every order has exactly one axiom-free adjacent swap, always
  at the central ranks 15|16, and the central pair is always complementary
  {A, Ā} (checked: XOR = 31 in all 546). Moreover **all 30 landless orders
  are matched to representable twins** (0 ice–ice pairs): every order that
  owns no measure is one central swap away from one that does.
- Defiance (inversions vs cardinality) of the 30 landless orders spans
  6–44 of the full 0–55 range: landlessness is not extremism.

## Reproduce

    gcc -O3 -march=native -fopenmp -o pell_census pell_census.c -lm
    ./pell_census 100000000 <outdir> 4
    python3 verify_pell.py <outdir> 100000000   # sample verification
    python3 pell_analyze.py                     # tripwires + statistics
    python3 gamma_layers.py                     # T1..T5 all-exact suite
    gcc -O3 -o cp_enum cp_enum.c && ./cp_enum 5 -c > orders5c.txt
    python3 cp_represent.py                     # LP + exact certificates
    python3 render_hero.py 4096 ; python3 render_gamma.py ; python3 render_kps.py
