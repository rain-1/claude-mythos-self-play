# MO 514920 — when do two binary strings have the same characteristic polynomial?

`H_b` = tridiagonal with the string `b ∈ {0,1}^n` on the diagonal and 1's off it;
`χ_b(x) = det(xI − H_b)` is the continuant `K(x−b_1, …, x−b_n)`, i.e. the (1,1) entry of the
transfer product `P_b = M_{b_1} ⋯ M_{b_n}`, `M_c = [[x−c, −1],[1, 0]]`, `det M_c = 1`.
Engines: `isospec.py` (all 2^n polynomials at once as exact int64 coefficient rows, grouped by
`np.unique`), `isospec_family.py` (sympy checks). Data: `isospec_census.json`, `isospec_family.json`.

## Census (reproduces the poster's 15 terms, extends to n = 20)

| n | a_n | 2^n | class sizes | exceptional classes |
|---|---|---|---|---|
| 1..7 | 2,3,6,10,20,36,72 | | {1,2} only | 0 |
| 8 | 134 | 256 | 16×1, 116×2, 2×4 | 2 |
| 9 | 270 | 512 | 32×1, 236×2, 2×4 | 2 |
| 10 | 526 | 1024 | 2×4 | 2 |
| 11 | 1052 | 2048 | 4×4 | 4 |
| 12 | 2072 | 4096 | 8×4 | 8 |
| 13 | 4154 | 8192 | 6×4 | 6 |
| 14 | 8231 | 16384 | 25×4 | 25 |
| 15 | 16504 | 32768 | 8×4 | 8 |
| 16 | **32856** | 65536 | 40×4 | 40 |
| 17 | **65764** | 131072 | 28×4 | 28 |
| 18 | **131249** | 262144 | 77×4, **1×6** | 78 |
| 19 | **262604** | 524288 | 52×4 | 52 |
| 20 | **524606** | 1048576 | | |

Singletons are exactly the palindromes (2^{⌈n/2⌉}); every other class is {b, rev b} except the
exceptional ones, which are unions of 2 (once 3, at n = 18) reversal pairs. Hence the exact bookkeeping

**a_n = 2^{n−1} + 2^{⌈n/2⌉−1} − c_n**, with c_n = number of excess merges =
0 (n ≤ 7), 2, 2, 2, 4, 8, 6, 25, 8, 40, 28, 79, 52, … (n = 8…19).
So a_n ~ 2^{n−1}: the exceptional coincidences are a vanishing fraction (c_n ≤ 79 for n ≤ 19,
non-monotone, even n richer than odd). The first size-6 class (three reversal pairs sharing one
polynomial) appears at n = 18: `000001001100001101 ~ 000001100001001101 ~ 101100001100100000` (+ reversals).

## Theorem (Cayley–Hamilton families)

Let `w_k = u X^k v` and `w'_k = u' X^k v'` for fixed blocks `u, X, v, u', v'` with `|u|+|v| = |u'|+|v'|`.
Then `χ(w_k) = e_1^T P_u P_X^k P_v e_1`. Since `P_X` is 2×2 with `det P_X = 1`, Cayley–Hamilton gives
`P_X^{k+2} = tr(P_X)·P_X^{k+1} − P_X^k`, so both sequences `f(k) = χ(w_k)`, `g(k) = χ(w'_k)` satisfy the
same two-term recurrence over ℤ[x]. **If χ(w_0) = χ(w'_0) and χ(w_1) = χ(w'_1) then χ(w_k) = χ(w'_k) for all k ≥ 0.**

The poster's n = 8 pair is the k = 0 member of such a family with `X = 01`:
`0001 (01)^k 1011 ~ 0010 (01)^k 0111` — verified k = 0…8 (n = 8, 10, …, 24); this is why the even-n
counts are richer (every family with |X| = 2 contributes to one parity only). Replacing X by `0` breaks
it (k ≥ 1 fails), as the theorem predicts: the recurrence needs the SAME block.

**Seeds are trivial coincidences.** Searching all decompositions `w = uXv, w' = u'Xv'` and asking that
the k = 0 members be equal-χ (in every found case they are *reversals of each other or identical
strings*) and that the k = 2 members agree: this explains 2/2, 2/4, 4/6, 8/10, 16/18, 20/24, 44/49 of
the exceptional classes at n = 8, …, 14. The five primitive pairs at n ≤ 14 not generated this way:

- n = 9: `000101011 ~ 011001001`, `001010111 ~ 011011001`
- n = 13: `0000101010011 ~ 0110001001001`, `0011010101111 ~ 0110110111001`
- n = 14: `01010110110001 ~ 01110010010101`

(The two n = 9 pairs are complements of each other up to reversal; complementing `b ↦ 1−b` sends
`χ_b(x)` to `(−1)^n χ_{1−b}(1−x)`… i.e. `x ↦ 1 − x`, so exceptional pairs come in complement pairs —
visible throughout the census.)

## Answer to the two questions, as far as the census goes
1. Formula: `a_n = 2^{n−1} + 2^{⌈n/2⌉−1} − c_n`, c_n small and erratic, asymptotically `a_n ~ 2^{n−1}`;
   c_n has no closed form yet — it counts family members alive at length n plus primitive seeds.
2. Mechanism beyond reversal: two-term recurrences from a repeated block (Cayley–Hamilton on the 2×2
   transfer matrix) turn one coincidence into an infinite arithmetic progression of coincidences; up to
   n = 14 all but five arise this way from trivial (reversal) seeds. **Conjecture:** the primitive pairs
   are themselves members of families with a *non-repeated* structure `u X^k v Y^k t` (two blocks growing
   together), which the same argument handles only when the two transfer matrices commute — testing this
   is the next step; the complement symmetry `x ↦ 1−x` halves the search.

POST decision: comment-grade (the theorem + the corrected/extended a_n table); the primitive seeds
are the open part.
