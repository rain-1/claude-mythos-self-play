# MO 514916 — nearest missing point of the Binary Dragon

`β = 1+i`, `D_0 = {0}`, `D_{k+1} = βD_k ∪ (1 − βD_k)`, `s_k = min{|z|² : z ∈ Z[i] \ D_k}`.

## 1. The complement obeys the same recursion (proved)

`z ↦ βz` is a bijection of `Z[i]` onto the even coset `βZ[i]` (x+y even) and `z ↦ 1−βz` is a
bijection onto the odd coset. `D_{k+1}` is the union of the two images of `D_k`, one in each
coset, so for the missing set `M_k = Z[i] \ D_k`

    M_{k+1} = βM_k ⊔ (1 − βM_k),        M_0 = Z[i] \ {0}.

Equivalently, with the "digit shift" `T(z) = z/β` (z even), `T(z) = (1−z)/β` (z odd):
`z ∈ D_k ⇔ T^k(z) = 0`. Since `T(0)=0`, the dragons are nested, `D_k ⊂ D_{k+1}`, and `s_k` is
the smallest norm of a point whose `T`-orbit needs more than `k` steps to reach 0.

Immediate consequences:

    s_{k+1} = min( 2 s_k ,  min_{z ∈ M_k} |1 − βz|² ),      |1−βz|² = 2|z|² − 2(x−y) + 1
    (√(2 s_k) − 1)²  ≤  s_{k+1}  ≤  2 s_k .

## 2. Closed form (conjecture; verified exactly for k ≤ 160)

Let `u_j = (2^(2j+1) + 1)/3` = 1, 3, 11, 43, 171, … (Jacobsthal numbers of odd index). Then

| k      | s_k          | a nearest missing point          |
|--------|--------------|----------------------------------|
| 4j+2   | (u_j² + 1)/2 | −(u_j−1)/2 + (u_j+1)/2 · i       |
| 4j+3   | u_j²         | −u_j                             |
| 4j+4   | 2 u_j²       | −u_j − u_j i                     |
| 4j+5   | 4 u_j²       | −2 u_j i                         |

The four points form one backward orbit of `T`: multiply by β three times, then apply
`z ↦ 1−βz` (and `u_{j+1} = 4u_j − 1`). Because `T` of each is the previous one, each needs
exactly one more step than its predecessor to reach 0, which **proves the upper bound**
`s_k ≤` (table) for every k. In particular `s_k ≤ 2^k/18 · (1 + O(2^{-k/2}))`.

The table reproduces all 64 values in the question (e.g. `s_64 = 2·715827883² =
1024819116160523378`). So, if the conjecture holds:

* **Q1.** Yes: `s_k ~ 2^k/18`; more precisely `s_k − 2^k/18 = Θ(2^{k/2})` and is positive
  (e.g. `s_{4j+2} = 2^k/18 + 2^{k/2}/9 + 5/9`).
* **Q2.** Yes: the table above.

## 3. How the check was done

* `dragon.py` — brute force, all `2^k` points, k ≤ 24: the formula and the listed point are exact
  (for k ≥ 4 the nearest missing point is unique).
* `annulus.py` — exact, no enumeration of the dragon. By §1 a missing point of `M_{k+1}` within
  `√s_{k+1} + 3` of 0 has its parent within `√s_k + 3` of 0 (since `|child| ≥ √2·|parent| − 1` and
  `s_{k+1} ≤ 2 s_k`), so the annulus `A_k = {z ∈ M_k : |z| ≤ √s_k + 3}` is computed from
  `A_{k−1}` alone, with Python integers. Started from brute force at k = 10 and run to k = 160:
  the formula holds at every step. `|A_k|` grows only like `2^{k/8}` (25 points at k=10,
  8.9 million at k=160).
* The second-nearest missing point is at a bounded squared distance beyond the first,
  with period 4: gaps `12, 1, 2, 1` for k ≡ 2, 3, 0, 1 (mod 4) — the "fjord" that reaches
  closest to 0 has the same local shape every four steps (β⁴ = −4). This is what a proof of the
  lower bound should exploit: `T⁴(z) = ±(z − c)/4` with `c` depending only on `z mod 4`, so
  the near-minimal configuration is a fixed point of a finite local rule.

## 4. In the picture

`the_moon_the_dragon_keeps.png` draws `D_22` with one pixel per Gaussian integer
(4,194,304 pixels), the disc of radius `√233245` about 0 — the largest it contains — and the
missing point `−341 + 342i` as the vermilion dot on its rim. Inside the moon: the discs of
orders 21, 20, 19, … and their own nearest missing points (all long since swallowed).
The eight inks are the first three digits of each point.
