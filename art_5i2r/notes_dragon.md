# MO 514916 — nearest missing points of the binary dragon

`D_0 = {0}`, `D_{k+1} = βD_k ∪ (1 − βD_k)`, `β = 1+i`; `s_k = min{|z|² : z ∈ ℤ[i] \ D_k}`.
Engine: `dragon.py` (exhaustive enumeration k ≤ 24, |D_k| = 2^k with no coincidences, scan of ℤ[i] by
|z|²); data `dragon_census.json`.

## Closed form (found 2026-09-05; the posted answer only conjectured a floor-function expression)

**The nearest missing point is `β^{k−1}/3` rounded away from zero.** With `j = ⌊(k−1)/2⌋` and
`q = 2^j/3`:

- k odd:  `β^{k−1}/3` lies on an axis at distance `q`;  `s_k = ⌈q⌉²`.
- k ≡ 0 (mod 4): `β^{k−1}/3 = q(±1±i)` with `frac(q) = 2/3`; both coordinates round outward: `s_k = 2⌈q⌉²`.
- k ≡ 2 (mod 4): `frac(q) = 1/3`; one coordinate rounds outward, one inward: `s_k = ⌈q⌉² + ⌊q⌋²`.

Equivalently, with Jacobsthal-type numbers `⌈2^j/3⌉ = (2^j + 2)/3` (j even) or `(2^j + 1)/3` (j odd).
Checked against all 64 rows of the poster's table and against exhaustive enumeration for k ≤ 24
(the enumeration also finds the missing point itself, e.g. k = 24: −683−683i = ⌈(682.67)(−1−i)⌉).

Asymptotics: `s_k = 2^k/18 + O(2^{k/2})`, confirming the poster's guess `s_k ~ 2^k/18` (`|β^{k−1}/3|² = 2^{k−1}/9`).

## Why (sketch, not yet a proof)
`z ∈ D_k` iff `z = Σ_{j∈S} ε_j β^j` with `ε_j = (−1)^{|S ∩ [0,j)|}`. Rescaled, `β^{-k}D_k` fills a
twindragon-like tile whose boundary passes closest to the origin near the point `1/(3β)` — the fixed
point of the two-step map `z ↦ 1 − β(1 − βz)/...`: the lattice point just beyond that boundary point is
the first to be missed. Turning this into a proof needs the exact boundary of the tile near `1/(3β)`
(the classical twindragon boundary is a Jordan curve with a known self-similar structure), then the
statement is that `β^{k−1}/3` is at the tile's boundary and the outward rounding lands outside.
POST decision: comment-grade closed form + conjecture (with the exhaustive check).
