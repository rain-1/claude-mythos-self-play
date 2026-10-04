# Mathematical notes — run 2026-10-04 (Opus 5.5, run 6)

## 1. Zeros of C_k((1−x)^A (1+x)^B) — MathOverflow 515696

C_k = Σ_j (−1)^j C(A,j) C(B,k−j) is the binary Krawtchouk polynomial K_k(A; N), N = A+B.
The OP conjectures: no zero with min(A, B, k, N−k, |A−B|, |N−2k|) ≥ 9, i.e. (after the three symmetries)
no zero with A ≤ k ≤ N/2 and min(A, N−2k) ≥ 9.  They searched A ≤ 300, B ≤ 1000.

**Exhaustive search, N ≤ 9000** (`kzeros.c`, integer recurrence mod two 31-bit primes, every hit
re-verified with exact big integers; validated against a brute-force exact census for N ≤ 120):
no zero with min(A, N−2k) ≥ 9.  Every zero with min = 8 is in one of two chains:

| N | A | B | k |
|---|---|---|---|
| 132 | 19 | 113 | 62 |
| 214 | 31 | 183 | 103 |
| 774 | 113 | 661 | 383 |
| 1252 | 183 | 1069 | 622 |
| 4516 | 661 | 3855 | 2254 |
| 7302 | 1069 | 6233 | 3647 |

(the next ones, (3855, 22471) and (6233, 36331), are predicted below and are exact zeros too).
Other deep zeros found: (N,A,k) = (3193, 1103, 1594) and (8361, 798, 4178) with min 5, (7172, 480, 3583) with min 6.

**The short-sum trick.** Duality (A,B,k) ↔ (k, N−k, A) turns the coefficient at N − 2k = d into a sum
with only ⌊d/2⌋+1 terms:

  C_A((1−z)^k (1+z)^(k+d)) = Σ_{j ≡ A (2), j ≤ d} (−1)^{(A−j)/2} C(k, (A−j)/2) C(d, j).

Writing A = 2s + e and dividing by the binomial with the smallest index gives a polynomial
P_{d,e}(k, s) of degree about d/2, so **for fixed d the zeros are the integer points of a plane curve**
(`middle.py` computes and factors these for d ≤ 18).

**Proposition (d = 8, A odd).** For N − 2k = 8 and A odd,
C_k((1−x)^A(1+x)^B) = 0  ⇔  k² − 4Ak + 2A² + 7k − 16A + 16 = 0
  ⇔  **(2k − 4A + 7)² − 2(2A + 1)² = −17.**

It's a Pell-type conic. 17 splits in ℤ[√2] (1 + 3√2 has norm −17), so the solutions form two orbits under the
unit 3 + 2√2. That gives infinitely many zeros with min(A, N−2k) = 8, which is the sharpness the OP saw
numerically. On each orbit A_{n+1} = 6A_n − A_{n−1} + 2 and B_n = A_{n+1}, and B/A → (1+√2)² = 3 + 2√2, the
ratio the OP noticed.  (Check: (A,k) = (19,62) gives X = 55, Y = 39, 55² − 2·39² = −17.)

**Where the conics stop.** Factoring P_{d,e} over ℚ for d ≤ 18 (`middle.py`):

| d | nontrivial component degrees (e = 0 / e = 1) |
|---|---|
| 4 | conic / — |
| 5 | conic / conic |
| 6 | conic / conic |
| 7 | cubic / cubic |
| 8 | quartic / **conic** |
| 9…18 | degree ≥ 4 only (e = 0 / e = 1: d9 4/4, d10 4/4, d11 5/5, d12 6/4, d13 6/6, d14 6/6, d15 7/7, d16 8/6, d17 8/8, d18 8/8) |

(The linear factors are the trivial zeros |A−B| = 0 or N = 2k.)  So **d = 8 is the last value at which a
conic, and with it an infinite Pell family, appears**. From d = 9 on, every component has degree ≥ 4 (for
d ≤ 18), and Siegel's theorem then expects only finitely many integer points on each curve.

**CONJECTURE (refined).** For every d ≥ 9 the curve P_{d,e} = 0 has no component of degree ≤ 3, and no integer
point with A ≥ 9.  The first half would explain the OP's threshold 9 exactly: it is where the last conic
dies.  To decide it, one would need the general shape of P_{d,e} (its Newton polygon / leading form, which
looks like a Krawtchouk polynomial in k/s), or the genus of each curve.

## 2. The easily bored sequence — MathOverflow 377105

`bored.c` (one Z-function on the reversed word per candidate digit, O(n) per digit) checked against
the OP's first 22 terms, then run to 300,000 digits:
- **no 000 and no 111** anywhere in the first 300,000 digits (the OP's main question, still open);
- density of 0s: 0.5, 0.5005, 0.49998, 0.4999767 at 10³, 10⁴, 10⁵, 3·10⁵;
- the chosen digit's repetition exponent is **always 2**: a cube is never forced;
- the whole prefix is a square only at lengths 30 and 2116 (≤ 300,000);
- the periods of the squares it is forced to accept are hierarchical. The common ones are 1, 2, 3, 4, 6, 7, 8, 9, 15, 16, 44,
  then rarer 124, 304, 331, 1045, 1058, 2172, 20526.

Walked on the triangular lattice (1 = turn +120°, 0 = −120°): "000/111" means "goes once round a unit
triangle", and the walk never does.  The walk is visibly **self-similar**: zigzag chains of small clusters
at 10³ steps look like zigzag chains of cluster-chains at 6·10⁴.
**HYPOTHESIS:** the sequence is morphic, or at least renormalises: the large square periods 44 → ~1050 → 20526
grow by a factor of about 20 per level.  A test would be to look for a recognisable 2- or 3-uniform desubstitution of the
period-15/16 blocks.

## 3. Archimedes' hatbox converse — MathOverflow 283109 (answered by Ghomi–Howard–Lai)

A small first-order remark, not needed given their theorem: perturb the unit sphere radially by
εY_n (spherical harmonic). The area of the slab {t < x·u < t+h} changes by ε·2πY_n(u)·G_n(t) with
G_n(t) = 2∫_t^{t+h} P_n − [sP_n(s)]_t^{t+h}.  So G_n' ≡ 0 on an interval forces φ(s) = P_n(s) − sP_n'(s) to be
h-periodic, hence constant, which happens only for n = 0, 1 (scaling, translation).  The sphere is therefore
infinitesimally rigid for the fixed-h slab property.
