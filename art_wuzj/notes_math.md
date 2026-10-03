# Notes — the Pythagorean beanstalk (MO 515674) and the zero-sum quilt (MO 515677)

## 1. The beanstalk

**Definition (MO 515674).** B_n = the closure of {1, …, n} under "x, y ∈ B and x² + y² = z² ⇒ z ∈ B";
a(n) = max B_n. The OP asks whether a(n) is polynomially bounded and reports a(192) = 457,
a(9 624 384) = 136 979 809, a(95 703 552) = 2 231 317 337.

**Engine (`beanstalk.c`).** B_n ⊆ B_{n+1}, so the closure is grown once, incrementally in n.
When a new member w arrives, every triple with leg w is (w, x, z) with d | w², d < w,
d ≡ w²/d (mod 2), x = (w²/d − d)/2, z = (w²/d + d)/2 — so only the divisors of w² are scanned
(no quadratic pair loop). 10⁵ in 0.2 s; 1.5·10⁸ in ~25 min.
Reproduces the OP's whole table for n ≤ 64, a(192) = 457 with exactly the 52 listed extra
elements, a(9 624 384) = 136 979 809 and a(95 703 552) = 2 231 317 337.
*Bug caught mid-run:* w² overflows u64 once members pass 2³² (n ≈ 1.6·10⁸); the first run
(`rec_3e8.txt`) is only trusted while a(n) < 2³²; `beanstalk2` (= current `beanstalk.c`, 128-bit
w²) re-runs to 2.1·10⁸ (`rec_2e8_fixed.txt`).

### Lemma (scaling by a Pythagorean triple)
For every primitive triple p² + q² = r² (p < q) and every m:  **a(q·m) ≥ r · a(m).**

*Proof.* Scaling is a closure homomorphism: k·B_m ⊆ B_{km} (induct on the derivation of each
element). Since p·m ≤ q·m, both p·B_m ⊆ B_{pm} ⊆ B_{qm} and q·B_m ⊆ B_{qm}. For b ∈ B_m,
(pb)² + (qb)² = (rb)², so rb ∈ B_{qm}. Take b = a(m). ∎

With (3, 4, 5): **a(4m) ≥ 5·a(m)**, hence along every chain m, 4m, 16m, … the exponent
log a / log n tends to at least log 5 / log 4 = 1.160964… . (3,4,5) is the best single triple:
log r / log q is 1.161 for (3,4,5), 1.106 for (20,21,29), 1.046 for (8,15,17), 1.032 for (5,12,13).

**Data.** For all m < 2·10⁶: a(4m) = 5a(m) exactly for 1 125 569 values of m, a(4m) > 5a(m)
for 874 430, never less (as the lemma demands). The OP's own a(192·4ᵏ) = 457·5ᵏ for k = 0…4
(192, 768, 3072, 12 288, 49 152 → 457, 2285, 11 425, 57 125, 285 625).
a(1536) = 4570 = 10·457 and a(6144) = 22 850 = 50·457 (the hero's coral ring).
Records of a(n) occur only at n with a large 3-smooth part (e.g. 107 495 424 = 2¹⁴·3⁸,
130 056 192 = 2¹⁵·3⁴·7²).

### Conjecture
**a(n) = n^{log 5 / log 4 + o(1)}**, i.e. the asymptotic beanstalk exponent is log₄5 ≈ 1.16096,
and the OP's constant γ = sup_n log a(n)/log n is attained at some finite n (γ ≥ 1.171363 from
n = 95 703 552). Evidence: the running maximum of a(n)/n^{log₄5} is 1.021 (n < 10⁴), 1.043
(< 10⁶), 1.070 (< 10⁷), 1.211 (< 10⁸, at n = 95 703 552), 1.187 (on [10⁸, 1.5·10⁸]) — it creeps,
consistent with a sub-polynomial correction but not with a larger exponent. What would decide
it: an upper bound. A plausible route: every member > n has a derivation tree whose leaves are
seeds; bound the height of a tree by the product of the triples' r/q ratios along its spine.

## 2. The zero-sum quilt (MO 515677)

A bijection φ: ℤ² → ℤ with every 2×2 window summing to 0 exists (answers on MO). The explicit
one drawn here: x_i = the i-th positive integer whose balanced-ternary digits vanish in odd
positions, x_{−i} = −x_i, y_j = 3x_j, φ(i, j) = (−1)^j x_i + (−1)^i y_j. The quilt makes the
proof visible: the even ternary digits of φ(i, j) are ±(digits of x_i) — they run down the
column as **warp threads** — and the odd digits are ±(digits of x_j), running along the row as
**weft**; the sign flips with parity, so warm and cool swap patch by patch and every tie closes a
window of ±x_i ± y_j that cancels. Checked: all 400 windows of the 21×21 patch sum to 0, all 441
values distinct, and the patch contains every integer with |v| < 59.
