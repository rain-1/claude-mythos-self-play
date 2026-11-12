# A proof of the closed form for the Binary Dragon (MO 514916)

`β = 1+i`, `D_0 = {0}`, `D_{k+1} = βD_k ∪ (1−βD_k)`, `M_k = Z[i] \ D_k`,
`s_k = min{|z|² : z ∈ M_k}`.

**Theorem.** Let `u_j = (2^(2j+1)+1)/3` (so `u_0 = 1`, `u_{j+1} = 4u_j − 1`). For every `j ≥ 0`

    s_{4j+2} = (u_j²+1)/2,    s_{4j+3} = u_j²,    s_{4j+4} = 2u_j²,    s_{4j+5} = 4u_j²,

and `s_1 = 1`. Consequently `s_k = 2^k/18 + Θ(2^{k/2})`, in particular `s_k ~ 2^k/18`.

Everything below is elementary; the finite checks are in `verify_proof.py`.

## 0. Notation: steps as affine maps

Write `f_0(w) = βw`, `f_1(w) = 1 − βw`. `f_0` is a bijection `Z[i] → βZ[i]` (the "even"
Gaussian integers) and `f_1` is a bijection onto the odd ones. Since
`D_{k+1} = f_0(D_k) ⊔ f_1(D_k)`, taking complements coset by coset gives

    M_{k+1} = f_0(M_k) ⊔ f_1(M_k).                                   (1)

Composing n steps, `z = f_{d_1}(f_{d_2}(… f_{d_n}(w)))  =  c + E β^n w`, where, with `ε_i = 1 − 2d_i`,

    c = d_1 + ε_1 β d_2 + ε_1ε_2 β² d_3 + … ,       E = ε_1 ε_2 ⋯ ε_n = ±1.

So `M_{k+n}` is the union of the images of `M_k` under the `2^n` maps `w ↦ c + Eβ^n w`.
The tables (`β² = 2i`, `β³ = −2+2i`, `β⁴ = −4`):

| n | `(c, E)` |
|---|---|
| 1 | `(0,+)`, `(1,−)` |
| 2 | `(0,+)`, `(−i,+)`, `(1,−)`, `(1+i,−)` |
| 3 | `E=+`: `0, −i, 1−2i, 1−i`;  `E=−`: `1, 1+i, 2i, i` |
| 4 | `E=+`: `0, −i, 1−2i, 1−i, 2, 2−i, 3−i, 3−2i`;  `E=−`: `1, 1+i, i, 2i, −1, −1+i, −2+i, −2+2i` |

Two facts about the last row carry the whole proof:

* (F1) every `E=+` map has `Re c ≥ 0`;
* (F2) the only `E=−` maps with `Re c > 0` are `c = 1` and `c = 1+i`; and all `|c| ≤ √13 < 4`.

Let `Y = {0, 1, 4, 5, 16, 17, 20, 21, …}` be the non-negative integers whose base-4 digits are
all 0 or 1 (the Moser–de Bruijn sequence). It satisfies `Y = 4Y ⊔ (4Y+1)`.

## 1. Theorem A: the missing points just outside the disc lie on one line

**Theorem A.** For `j ≥ 1` and `u = u_j`: every `z ∈ M_{4j+3}` with `|z| < u + 1` has the form
`z = −u + iy` with `y ∈ Y`. Moreover `−u ∈ M_{4j+3}`.

*Proof.* Induction on `j`.

*Base `j = 1`* (`k = 7`, `u = 3`): the missing points of `D_7` with `|z| < 4` are exactly `−3` and
`−3+i` (direct enumeration of the 128 points of `D_7`).

*Step.* Assume the statement for `j`, put `u = u_j`, `u' = u_{j+1} = 4u − 1`, and let
`z ∈ M_{4j+7}` with `|z| < u' + 1 = 4u`. By §0, `z = c − 4Ew` for one of the sixteen pairs
`(c,E)` and some `w ∈ M_{4j+3}`. Then `|w| = |z − c|/4 < (4u + √13)/4 < u + 1`, so by the
induction hypothesis `w = −u + iy` with `y ∈ Y`, and

    z = (Re c + 4Eu) + i(Im c − 4Ey).

If `E = +`, then `Re z = 4u + Re c ≥ 4u` by (F1), contradicting `|z| < 4u`.
If `E = −`, then `|z| ≥ |Re z| = 4u − Re c`, which is `≥ 4u` unless `Re c > 0`; by (F2) that leaves
`c = 1` or `c = 1+i`, and then

    z = −(4u−1) + i(4y)      or      z = −(4u−1) + i(4y+1),

i.e. `z = −u' + iy'` with `y' ∈ 4Y ∪ (4Y+1) = Y`.
Finally `−u' = 1 − 4u` is the image of `−u ∈ M_{4j+3}` under the map `(c,E) = (1,−)`, so
`−u' ∈ M_{4j+7}`. ∎

**Corollary.** `s_{4j+3} = u_j²` for `j ≥ 1` (every missing point within `u+1` of the origin has
real part `−u`, and `−u` itself is missing).

## 2. The other three residues

Fix `j ≥ 1`, `u = u_j`, and let `w` range over `M_{4j+3}`. In each case below a missing point `z`
of norm below the claimed value has a parent `w` with `|w| < u+1`, so `w = −u+iy`, `y ∈ Y`
(in particular `y ≥ 0`) by Theorem A.

**k = 4j+4, claim `s = 2u²`.** If `|z|² < 2u²`, then `z = f_d(w)` with
`|w| ≤ (|z|+1)/√2 < u + 0.71`. Now
`f_0(w) = (−u−y) + i(y−u)` has norm² `2u² + 2y²`, and
`f_1(w) = (1+u+y) + i(u−y)` has norm² `2u² + 2y² + 2u + 2y + 1`.
Both are `≥ 2u²`: contradiction. Equality: `f_0(−u) = −u − ui`.

**k = 4j+5, claim `s = 4u²`.** If `|z|² < 4u²`, then `z = c + E·2i·w` (row n=2), with
`|w| < (2u + √2)/2 < u + 0.71`. Here `2i·w = −2y − 2ui`, so the four images are

    (−2y, −2u),   (−2y, −2u−1),   (2y+1, 2u),   (2y+1, 2u+1),

all of norm² `≥ 4u²`: contradiction. Equality: `−2ui`.

**k = 4j+6, claim `s = (u'²+1)/2 = 8u² − 4u + 1`, `u' = 4u−1`.** If `|z|² < 8u²−4u+1`, then
`z = c + Eβ³w` (row n=3) with `|w| < (√(8u²−4u+1) + √5)/(2√2) < u + 1`.
Here `β³w = (2u−2y) + i(−2u−2y)`, of norm² `8u² + 8y²`, and
`|z|² = 8u² + 8y² + |c|² + 2E·[Re c·(2u−2y) − Im c·(2u+2y)]`:

| `(c,E)` | `|z|² − (8u² + 8y²)` |
|---|---|
| `(0,+)` | `0` |
| `(−i,+)` | `1 + 4u + 4y` |
| `(1−2i,+)` | `5 + 12u + 4y` |
| `(1−i,+)` | `2 + 8u` |
| `(1,−)` | `1 − 4u + 4y` |
| `(1+i,−)` | `2 + 8y` |
| `(2i,−)` | `4 + 8u + 8y` |
| `(i,−)` | `1 + 4u + 4y` |

Every entry is `≥ 1 − 4u`, so `|z|² ≥ 8u² − 4u + 1`: contradiction. Equality only for
`(1,−)`, `y = 0`: `z = −(2u−1) + 2ui = −(u'−1)/2 + i(u'+1)/2`.

In each case the extremal point is the image of `−u ∈ M_{4j+3}`, hence really missing, so the
three values are attained. This proves the theorem for all `k ≥ 7` (`k = 4j+3, …, 4j+6`, `j ≥ 1`).
The values `s_1, …, s_6 = 1, 1, 1, 2, 4, 5` are checked directly. ∎

## 3. Remarks

* For `k ≥ 7` the nearest missing point is unique; the four of them,
  `−u, −u−ui, −2ui, −(2u−1)+2ui`, are one backward orbit (multiply by β three times, then apply
  `z ↦ 1−βz`).
* The points `−u + iy`, `y ∈ Y`, are all missing (same induction, using both `c = 1` and
  `c = 1+i`): the fjord that comes closest to the origin meets the tangent line `x = −u` in a
  Cantor-like set, the Moser–de Bruijn numbers. That is the whole reason the induction closes:
  `Y = 4Y ⊔ (4Y+1)` matches the two maps of (F2).
* The base case cannot be `j = 0`: `D_3` also misses `−1−i`, which is not of the form `−1+iy`,
  `y ∈ Y`.
* Asymptotics: `s_{4j+2} = 2^k/18 + 2^{k/2}/9 + 5/9`, `s_{4j+3} = 2^k/18 + (2^{(k+1)/2}+1)/9`,
  and the next two are 2 and 4 times `s_{4j+3}`.
