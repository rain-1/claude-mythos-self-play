# What Greed Builds — three lenses on Conway's nimbers

*2026-07-20 · branch `claude/laughing-davinci-gvjez4` · seeded from the live
MathOverflow front page ("When is Conway's nim-multiplication table singular",
MO 513363) and the live Philosophy.SE front page ("Why are we able to
contemplate abstractions at all?").*

Conway's nimbers are what pure greed builds. Define, on the natural numbers,

- nim-addition `a ⊕ b` = XOR, and
- nim-multiplication `a ⊗ b = mex { a'⊗b ⊕ a⊗b' ⊕ a'⊗b' : a'<a, b'<b }`,

where **mex** is the *minimal excludant* — the smallest number not yet refused.
Every entry of both tables is the least value consistent with what came before:
the greedy choice, made forever. The astonishing theorem (Conway, *On Numbers
and Games*) is that this pure parsimony builds **fields**: the nimbers below
`2^(2^k)` form the finite field `GF(2^(2^k))`, and the whole tower is the
quadratic closure of GF(2). Nobody asked for associativity; greed produced it.
That felt like an answer to the Philosophy.SE question about why abstraction
is possible at all: you contemplate the abstraction by refusing, at every
step, everything you have already seen.

One object, three lenses.

## 1. `hero_4096.png` — The Times Table of the Simplest Field (4096²)

The nim-multiplication table itself: cell `(i,j)` = `i ⊗ j` for `i,j < 1024`,
one exact product per 4×4-px cell. Color = `0.45·log₂(1+v)/16 + 0.55·ECDF(v)`
through a dusk ramp (the log part is scale-equivariant, so every nested
subfield block re-uses its parent's ramp — self-similar coloring for a
self-similar object). The golden block is `GF(256)²` — products of two small
nimbers stay small: a closed subworld. The icy stars inside it are the 255
solutions of `i ⊗ j = 1`: every element paired with its multiplicative
inverse. The gold thread on the diagonal is the Frobenius square `i ⊗ i`.
Illumination is anchored at the origin, where the mex genesis begins.

## 2. `tower_2560.png` — The Rose of 65535 (2560²)

All 65535 nonzero nimbers of `GF(2^16)` on one circle: **angle** = discrete
logarithm base g = 258 (the multiplicative group is cyclic of order
65535 = 3·5·17·257 — the product of the four Fermat primes, which is exactly
why the regular 65535-gon is compass-constructible), **radius** = log₂ of the
integer value. The steel curtain is the single orbit g^k → g^(k+1) walking the
whole field once. The golden needles are its dives into the subfield: the
integers below 256 sit at *exactly* the 255 evenly spaced angles (multiples of
257 in dlog) — being a small integer and being a deep harmonic are the same
thing here (verified). Once per cycle the orbit falls all the way to the
identity at the center. The teal chords connect each subfield element `x` to
its Frobenius square `x⊗x` — squaring doubles the discrete log, so the chords
envelope a cardioid. White beads: the four Fermat-prime subgroups C₃, C₅,
C₁₇, C₂₅₇ (the "gears" that mesh into the cyclic group).

## 3. `collapse_2560.png` — The Silence Before the Fourth Mountain (2560²)

The live MO question: treat the n×n nim times-table `M_n = [i⊗j]` as an
integer matrix — for which n is `det M_n = 0` over ℚ?  Horizontal axis:
log₂ n. Above the horizon, gold aurora: `log|det M_n| / n` (bits of memory
per row), breached exactly where the determinant dies. Below the horizon,
cyan stalactites: the corank profile `log₂(1+corank)`, **independently
recomputed here for every n ≤ 1300 modulo two ~2^20 primes**. Our singular
set matches the poster's exactly:

    [19,28] ∪ {43,44} ∪ {55} ∪ [259,508] ∪ [517,764] ∪ [773,1018] ∪ [1035,1161]

with corank peaks 3 (at n=23) and 63 (at n=383), as claimed. The crystal
ticks inside each mountain are the actual **free columns** of the collapse
(kernel support). New observation from this computation: on the rising flank
of each range the free columns are **exactly the odd integers from q+3
to n** (q = 16 or 256) — e.g. at the peak n=383 they are 259, 261, …, 383,
giving corank = (n−q−1)/2 there and explaining the poster's peak rule
corank(3q/2−1) = q/4−1; on the falling flanks they reorganize into
arithmetic progressions of step 4 and then dyadic combs (step 16/32) before
the range dies. Gold beads beyond the mountains: float `log|det|` samples
continuing past the poster's n ≤ 2048 scan, deep into the conjectured
silence (n up to ~21000). The great violet phantom at far right is the
poster's conjectured fourth range `[q₄+3, 2q₄−4] = [65539, 131068]` with
peak corank q₄/4−1 = 16383 at n = 98303 — drawn only as mist, because it is
a conjecture.

## Verification (`nim.py`, `singular.py`, `freecols.py`, `collapse_data.py`)

- 256×256 table built **from the raw mex definition** (no field shortcuts),
  then extended by the Fermat-power decomposition; row 2 and 3 match the
  classical table (OEIS A051775).
- Field axioms: associativity, commutativity, distributivity over ⊕ verified
  on 20000 random triples in GF(2^16); Latin-square rows; subfield closure
  GF(2), GF(4), GF(16), GF(256); Fermat rule F⊗F = 3F/2.
- g = 258 verified to have exact order 65535; dlog table covers every nonzero
  element exactly once.
- The jewel fact: the order-m subgroup (m = 3, 15, 255) is exactly the
  integers 1..m — set equality verified.
- Corank profile: two independent primes (1048573, 1048583) agree; singular
  intervals and both peaks match MO 513363's reported data exactly.
- Kernel at n=383: 63 vectors verified `M·K^T ≡ 0 mod p`, max residue 0;
  free columns = odd integers in [259,383].
