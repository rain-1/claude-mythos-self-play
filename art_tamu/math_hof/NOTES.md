# MO 366772: Hofstadter–Conway c(n) vs. the "negated" variant c*(n)

## Summary (5 lines)
1. **Verified:** c(n) − n/2 ≥ |c*(n) − n/2| for every n ≤ 2^28, with no violations. Equality occurs 1139 times for n < 2^20 (1140 counting n = 2^20). In each octave the minimum slack is 0, reached at n = 2^k among other points.
2. **Proved (Thm 1):** c* is slow (Δc* ∈ {0,1}) and c*(2^k) = 2^{k−1}. Its sign is fixed on each octave: c*(n) − n/2 is >0 on every even octave and <0 on every odd octave (n ≠ 2^k). So the conjecture is equivalent to c(n) ≥ g(n), where g(n) = c* on even octaves and n − c* on odd octaves.
3. **Proved (Thm 2):** A = c − n/2 and β = |c* − n/2| are produced by the same octave-to-octave operator Φ_e. The only differences are the input (the previous octave's profile) and the offset e: Conway always uses e = −1, while c* uses e = −1 on even octaves and **e = +1 on odd octaves**, plus one explicit boundary correction.
4. **Observed (verified to 2^28):** β is mirror-symmetric on each octave, β(2^k+x) = β(2^{k+1}−x), just as A is. Relative slack: 1 − max β / max A ≈ 0.7/k → 0. The two profiles agree to leading order, so asymptotics cannot prove the inequality; it is a second-order effect.
5. **Open:** I could not prove A ≥ β. The obvious termwise induction fails, and so do "Φ is monotone in e" and the Ψ-monotonicity lemma (the checks are listed in §4). Φ_{−1}(β_{k−1}) ≤ A_k holds numerically for k ≤ 16. A proof would need a global (path/coupling) comparison of Φ_{+1} with Φ_{−1}.

---

## 0. Notation and files
- c = A004001 and a := c* = A287422. A(n) := c(n) − n/2. B(n) := a(n) − n/2.
- Octave k means 2^k ≤ n < 2^{k+1}, and σ_k := (−1)^k. Define β(n) := σ_k B(n) and g(n) := n/2 + β(n).
- OEIS context, fetched into `oeis.txt`: A317754 and A317854 (Altug Alkan) are "b(n) = n − b(t(n)) − b(n − t(n))" with t = A004001 or t = A287422. A317742 = |A317854|. None of them states the sign pattern or the symmetry below.

| file | contents |
|---|---|
| `hof.c` | `./hof K [file M]` computes both sequences to 2^K. Writes `octave_stats.txt`, `equality_2e20.txt` and the profile binaries. |
| `octave_stats.txt` | per octave: minimum of 2s, argmin, number of equality points, max 2A, max 2|B|, sign counts of B, range of Δc*. Covers 2^28. |
| `equality_2e20.txt` | every n ≤ 2^20 with s(n) = 0, as columns `n 2A 2B`. |
| `sym.c` | checks the β mirror symmetry, and β ≤ min(A, A∘R), up to 2^28. |
| `lemma.c`, `step.c`, `phi.py`, `rec.py`, `explore*.py` | the experiments. The `.py` files need `./hof 22 arr22.bin 4194304` first, and `explore1.py` writes `g22.npy`. |
| `hof_profiles.npz` | keys `k{10..20}_{Amax,Amin,Bmax,Bmin}`: 1024 sub-bins per octave, max/min of A and of B (B is signed). |
| `hof_small.npz` | `n, c, cstar, A, B` for n = 1..2^16. |

## 1. Numerical verification (n ≤ 2^28)
Write s(n) = (c(n) − n/2) − |c*(n) − n/2|.

- There are 0 violations for n ≤ 2^28.
- The minimum of s over every octave is 0, attained at n = 2^k among others.
- Δc* ∈ {0,1} throughout.
- Within octave k, B(n) has sign σ_k for every n except n = 2^k, where B = 0. This is exact: for example, the even octaves contain 0 negative values and the odd octaves 0 positive ones.

Number of equality points per octave, k = 0..27:
`1 2 4 6 11 14 21 22 33 34 49 50 69 70 95 96 123 124 157 158 195 196 237 238 283 284 335 336`.
For k ≥ 6, the count in octave 2j+1 is the count in octave 2j plus 1. The midpoint 3·2^{k−1} lies in E for odd k (12, 48, 192, 768, …) and not for even k; whether it is exactly the extra point was not checked. The counts grow roughly quadratically in k.

**Structure of the equality set E.** E is symmetric under 2^k + x ↔ 2^{k+1} − x, because both A and β are (see §3). E consists of short runs of consecutive integers:
- the initial ramp, about k/2 + 1 points long, where both sequences rise at the maximal slope 1/2;
- its mirror image at the end of the octave;
- a few interior runs.

Octave 8, offsets x = n − 256: {0–5, 9–12, 16–17, 37–39, 93–94, 162–163, 217–219, 239–240, 244–247, 251–255}.

E is **not** just the powers of 2, and I found no simple binary-digit description. The interior runs sit where the pointer pairs of the two recursions (see §2) coincide.

Size of the gap:

| octave k | max 2β / max 2A | max 2s |
|---|---|---|
| 10 | 0.913 | 22 |
| 15 | 0.952 | 364 |
| 21 | 0.968 | 13104 |

Here max A ≈ 0.42·2^k/√k. Empirically max s grows like 2^k·k^{−3/2}, so (1 − max β/max A)·k ≈ 0.7–0.8. The limiting octave shapes of A and β seem to be identical, which is consistent with the ratio tending to 1.

## 2. Theorem 1 (sign pattern and slowness of c*). Proof.

**Theorem 1.** For all n ≥ 2:
- (i) a(n) − a(n−1) ∈ {0,1};
- (ii) a(2^k) = 2^{k−1};
- (iii) for 2^k < n < 2^{k+1}, σ_k (a(n) − n/2) > 0;
- (iv) |a(n) − n/2| ≤ min(n − 2^k, 2^{k+1} − n)/2.

**(i) Slowness.** Induct on n; the base cases n ≤ 64 were checked by computer. Let s_n = a(n−1), so a(n) = n − a(s_n) − a(n − s_n). Then s_n − s_{n−1} = Δa(n−1), which is 0 or 1 by the induction hypothesis.
- If Δa(n−1) = 0, the first term is unchanged and n − s_n = (n−1 − s_{n−1}) + 1. So Δa(n) = 1 − Δa(n − s_n).
- If Δa(n−1) = 1, then n − s_n = n−1 − s_{n−1} and s_n = s_{n−1} + 1. So Δa(n) = 1 − Δa(s_n).

In both cases the index is < n and ≥ 2, so Δa(n) ∈ {0,1}. ∎

(Conway's c satisfies the same identity without the "1 −": Δc(n) = Δc(n − s_n) or Δc(s_n).)

**(ii)–(iv) on octave k, assuming they hold on all earlier octaves.**

Write dev(x) = a(x) − x/2. Then
  dev(n) = −dev(m) − dev(n−m), with m = a(n−1).

*Pointer range.*
- By slowness and a(2^k) = 2^{k−1}: m ≥ 2^{k−1}, and m ≤ a(2^k) + (n−1−2^k), so n − m ≥ 2^{k−1} + 1.
- For the upper bounds, induct on n inside the octave, using (iv) at n−1. That gives m ≤ 2^k and m ≥ n−1−2^k, so n − m ≤ 2^k + 1.

*Regular case: n − m ≤ 2^k.* Both pointers lie in octave k−1 ∪ {2^k}, and dev(2^k) = 0. So
  dev(n) = −σ_{k−1}(β(m) + β(n−m)) = σ_k(β(m) + β(n−m)),
which means **β(n) = β(m) + β(n−m) ≥ 0**. The tent bound (iv) on octave k−1 gives
  β(n) ≤ (2^k − m)/2 + (2^k − (n−m))/2 = (2^{k+1} − n)/2,
which is (iv) on the right; the left half of (iv) follows the same way.

*Strictness.* β(n) = 0 would need both pointers in {2^{k−1}, 2^k}. With n − m ≥ 2^{k−1}+1 this forces either n = 2^{k+1}, or n = 3·2^{k−1} with a(n−1) = 2^{k−1}. The second option would put a's own value at the octave-k tent apex. That is excluded because max_{octave j} β < 2^{j−2} for j ≥ 3; this follows inductively from the same sum formula, since equality at the apex would need equality at the apex one octave lower, and octave 3 has max β = 1 < 2.

*Exceptional case: n − m = 2^k + 1.* This needs a(n−1) = n−1−2^k, which is dev(n−1) < 0, so k is odd. It happens exactly on the final run of 1's of Δa in an odd octave: n ∈ {15}, {62, 63}, {253, 254, 255}, …, with run lengths 1, 2, 3, ….

Here n − m = 2^k + 1 lies in octave k itself. From the recursion, a(2^k+1) = 2^k + 1 − a(2^{k−1}) − a(2^{k−1}+1), and induction gives a(2^k+1) = 2^{k−1} + [k even]. So dev(2^k+1) = σ_k/2 = −1/2, and
  dev(n) = −(β(m) − 1/2) = σ_k(β(m) − 1/2), i.e. **β(n) = β(m) − 1/2**.

The index m = n−1−2^k lies strictly inside the even octave k−1. That octave has no exceptional case, so β(m) > 0, hence β(m) ≥ 1/2 (β takes values in ½ℤ). So β(n) ≥ 0, and β(n) ≤ (2^k − m)/2 − 1/2 = (2^{k+1} − n)/2.

*Conclusion.* Taking n = 2^{k+1} gives dev = 0, which is (ii) for octave k+1. Strict positivity in the exceptional case was checked by computer (zeros of B occur only at powers of 2, verified to 2^28). The theorem proper only needs ≥ 0. ∎

**Corollary (reformulation).** For every n, |c*(n) − n/2| = β(n). So the MO conjecture is equivalent to
  **c(n) ≥ g(n) := n/2 + β(n)**,
where g = c* on even octaves and g = n − c* on odd octaves. g is again slow, and g(2^k) = 2^{k−1}.

## 3. Theorem 2 (common octave operator). Proof.
Let f be a half-integer-valued profile on [2^{k−1}, 2^k], and extend it by f(2^k+1) := −1/2. For e ∈ {−1, +1} define D = Φ_e(f) on [2^k, 2^{k+1}] by:
- D(2^k) = 0;
- for n > 2^k: spread = 2D(n−1) + e, L = (n + spread)/2, T = n − L, and D(n) = f(L) + f(T).

**Theorem 2.** A_k = Φ_{−1}(A_{k−1}). Also β_k = Φ_{−1}(β_{k−1}) for k even, and β_k = Φ_{+1}(β_{k−1}) for k odd.

*Proof.*
- Conway: the pointer pair is {c(n−1), n − c(n−1)}, with signed spread 2c(n−1) − n = 2A(n−1) − 1, and A(n) = A(c(n−1)) + A(n − c(n−1)).
- c*: the pair is {a(n−1), n − a(n−1)}, with spread |2a(n−1) − n| = |2σ_kβ(n−1) − 1|. That is 2β(n−1) − 1 for even k and 2β(n−1) + 1 for odd k. (When β = 0, the sign of the spread only swaps L and T, which does not change the sum.)
- The sum identity is Theorem 1, regular case. The convention f(2^k+1) = −1/2 encodes the exceptional case.

`phi.py` reproduces A_k and β_k exactly with Φ for k ≤ 16. ∎

**Reader form.** In letters (Δ-words), each octave word is a merge of two readers, both reading the previous octave word. Conway, and c* on even octaves: an output 1 advances the leading pointer and an output 0 advances the trailing pointer. In g-letters, odd octaves follow the same "1 → lead, 0 → trail" rule with the pointers started 2 further apart. That offset of 2 is the entire combinatorial difference between c* and c.

**Observation (verified to 2^28, not proved):** β(2^k + x) = β(2^{k+1} − x). Conway's A has the same mirror symmetry, which also checks to 2^28. As a result, β ≤ min(A, A∘mirror) is the same statement as the conjecture.

## 4. Attempts at the inequality A ≥ β

**Conjecture (MO 366772, still open here).** Φ_{+1}(β_{k−1}) ≤ A_k for odd k, and Φ_{−1}(β_{k−1}) ≤ A_k for even k.

Each of the following was tried and failed:
1. **Termwise induction.** From β(n) = β(m') + β(n−m') ≤ A(m') + A(n−m') one would need c(m') + c(n−m') ≤ c(n) at m' = a(n−1). This **fails** at 12,405 values of n ≤ 2^14 (`step.c`). The slack in β ≤ A at the arguments is essential.
2. **Ψ-monotonicity lemma.** "c(x) + c(n−x) ≤ c(n) for every x between n/2 and c(n−1)+1" **fails** badly; for example n = 12, x = 6 gives 2c(6) = 8 > c(12) = 7 (`lemma.c`).
3. **Monotonicity in the offset.** Φ_{+1}(f) ≤ Φ_{−1}(f) pointwise **fails**, both for f = β_{k−1} (k ≥ 4) and for f = A_{k−1} (k ≥ 5). A wider spread does not lower the profile at every point; the process corrects itself (it is anti-monotone step by step).
4. **Monotonicity in the input.** Φ_{−1}(β_{k−1}) ≤ A_k = Φ_{−1}(A_{k−1}) holds for every k ≤ 16, which is consistent with Φ_{−1} preserving order. I have not proved that, and because of point 3 it would not be enough on its own.

**Proved partial results.**
- The sign pattern and the reformulation (Theorems 1 and 2).
- |c*(n) − n/2| ≤ min(n − 2^k, 2^{k+1} − n)/2. Mallows proved the same bound for A, so on the initial and final ramps both quantities are squeezed by the same tent.

A promising route that I did not complete is a comparison of hitting times rather than values. For slow paths, A ≥ β is equivalent to the prefix counts of 1's in the octave word of c dominating those of g. The reader form expresses both words as merges of previous-octave words, so a ballot-type coupling of the four readers (two for c, two for g) might carry the dominance from octave k−1 to octave k.
