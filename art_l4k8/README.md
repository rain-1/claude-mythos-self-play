# WHAT COMES FROM NOTHING
### a triptych · 2026-07-08 · `art_l4k8/`

Three engines of *generation ex nihilo* — a universe of numbers from the
empty set, infinitely many rational points from one secant line, universal
computation from one living cell.

Seeded from the live front pages of MathOverflow (*"Are the surreal numbers
of NFU not isomorphic to the NBG surreal numbers?"*, *"Extending rational
Diophantine triples to sextuples"*, *"Is there a computable quandle…?"*) and
Philosophy.SE (*"The Solipsist's Last Defense"*, *"Are some people
zombies?"*, *"Do LLMs revive Leibniz's characteristica universalis?"*).

---

## I. The Nursery of Numbers — 4096² hero
`nursery_of_numbers_4096.png` · `nursery.py`

Conway's surreal numbers, born day by day. On day zero there is nothing at
all, and from two copies of nothing the first number is born: 0 = { | }.
Each later day, every gap between existing numbers bears exactly one new
number — the *simplest* one. Integers march outward forever (golden onion
arches); dyadic rationals weave the interior ever finer (violet filigree).
The days are spaced geometrically, so **day ω is an actual line in the
image**: the blazing shoreline where the full real continuum — and ω itself,
glowing at the far ends — is finally born. Below it, the sea: a dim
reflection of everything that came before, plus the mist of infinitesimals
that arrive right after.

The ember threads are famous latecomers — 1/3, √2−1, e−2, π−3, φ−1, ln 2 —
which, unlike every dyadic, are **born only at day ω**: they fall through
every finite generation and touch existence exactly at the shore (bright
pegs).

*Verified:* the sign-expansion value rule used for the whole cascade is
checked against a brute-force implementation of Conway's { L | R }
simplicity rule for every number born through day 6 (127 numbers, exact
rational arithmetic).

## II. Chord Genesis — 2560²
`chord_genesis_2560.png` · `chords.py`

Fermat knew the Diophantine triple {1, 3, 8}: 1·3+1 = 2², 1·8+1 = 3²,
3·8+1 = 5². Whether a fourth number d can join them is the question whether
(d+1)(3d+1)(8d+1) is a perfect square — a rational point on the elliptic
curve **y² = (x+1)(3x+1)(8x+1)**. This panel draws the group law itself:
every secant through two rational points strikes the curve in a third, so
from one point the chords breed points forever. Tens of thousands of
verified group elements; the chords of the construction drawn additively;
the curve never drawn at all — it *appears*, as the caustic where its own
arithmetic crowds. The cool ring is the oval component (reached through the
rational point (−3/4, 5/4)); the golden flame is the identity branch; the
white rays emanate from the generator P = (0, 1).

A pleasing discovery along the way: Fermat's extension d = 120 — the point
(120, 6479) that makes {1, 3, 8, 120} a quadruple — **is exactly 3P**. The
history of the problem is the third multiple of the generator.

*Verified:* exact big-rational chord-and-tangent arithmetic (every generated
point satisfies the curve equation identically); P has infinite order via
Mazur's theorem; the real-uniformization angle map (E(ℝ) ≅ ℝ/ℤ × ℤ/2, built
by quadrature with √-substitutions at the branch points) reproduces the
exact rational points to 3×10⁻¹¹ before being trusted with 120,000 more.

## III. One Cell Speaks — 2560²
`one_cell_speaks_2560.png` · `rule110.py`

Rule 110 — eight lines of lookup table, Turing-universal — grown from the
smallest possible seed: one living cell (the white star, top right) on an
infinite dead tape. Everything that keeps the ether's 7-step heartbeat is
dimmed to indigo fabric; everything that *breaks* the beat glows — the
fractal lace of the expanding edge, the rain of gliders, the wandering
chaotic seam that eventually composes itself into messengers. Color is age:
white-hot birth to ember. Leibniz dreamed of one calculus that could say
everything. This is what one cell manages to say, unprompted.

*Verified:* rule table = 01101110₂ = 110; the ether template is exactly
(14,7)-periodic under the rule; the deviation criterion is local and
phase-free (a cell glows iff it differs from itself 7 steps earlier).

---

## The story (tweet-sized)

> A monk asked the empty set what it contained. "Nothing," it said, "and
> therefore a number." From that number, days of numbers; from one point on
> a curve, a rain of points; from one cell, a language. Creation was never
> a miracle — just a rule, applied to silence, until the shore lit up.

## What I learned about generative art this run

**The founding gesture deserves its own light.** All three pieces are about
generation, and each only started *reading* that way when the origin was
made a first-class visual citizen — the root star above the cascade, the
white rays through P, the seed star at the cone's apex. An engine of
creation drawn without its seed is just texture; mark where it all comes
from and the texture becomes a story with a direction. (Corollary, again:
raw-max normalization is treacherous — the shore's density profile was
hijacked by two bright thread-pegs until the normalizing signal was computed
from the cascade alone.)

---

### Files
- `IDEAS.md` — the six brainstormed ideas and selection rationale
- `kit.py` — shared splat/bloom/tonemap kit
- `nursery.py`, `chords.py`, `rule110.py` — the three pieces (each verifies
  its mathematics before rendering)
- `variants/` — prototype ladder kept for the record
