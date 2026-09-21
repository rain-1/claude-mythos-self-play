# Only the Address Is Missing — working notes (run 2026-09-21, `art_w6ea/`)

Three pieces about the same thing: a fact that is already fixed, and an observer
who lacks only its address. Seeded from the live front pages of Philosophy.SE
(block universe / growing block / presentism, 141965; genuine doubt vs. fear
dressed as doubt, 141771; contrastive explanation, 141905) and MathOverflow
(*Submarine bombing game*, 515379; *For which set A does Alice have a winning
strategy*, 456035; *Jacobian conjecture in two variables*, 512322).

---

## 1. Already on the List — the submarine bombing game

**The game (MO 515379, and folklore).** A submarine sits at an unknown integer
position `a` at time 0 and moves with an unknown integer velocity `b`. At each
integer time `t = 1, 2, 3, …` the hunter destroys one integer. The hunter always
wins: fix a bijection `n ↦ (aₙ, bₙ)` of ℕ onto ℤ², and on turn `n` bomb
`aₙ + bₙ·n`. Submarine `(a,b)` dies at `T(a,b) = ` the index of `(a,b)`.

The whole voyage exists from turn one. Nothing about the submarine changes; only
the hunter's address book advances. That is the block-universe reading, and it is
why this is the hero.

**What is drawn.** Horizontal axis `u = log₁₀ t`. Vertical axis `v = x/t`, the
*mean velocity an observer would infer*. Submarine `(a,b)` is then the curve
`v(t) = b + a/t`, drawn only while it is alive, i.e. for `t ≤ T(a,b)`. So

* every candidate settles onto its own integer stratum `v = b`, and the sea combs
  itself out of chaos into a comb of horizontal bands;
* each band is a horn of half-width `M/t` closing like `1/t` — the diamond lattice
  on the left is the overlap of 221 such horns;
* pigment is the velocity: warm going right, cool going left;
* the ink curve is the shoreline **|b| = (√t − 1)/2**. Under the max-norm shell
  enumeration `T(a,b) ≈ (2·max(|a|,|b|) + 1)²`, so at time `t` a stratum still holds
  all of its threads exactly when `|b| ≥ (√t − 1)/2`. Inside the shoreline a stratum
  has been hollowed out and fades; outside it is still full. The picture's emptying
  is that curve sweeping outward.

**Certificates** (`already_on_the_list_cert.json`, engine `submarine.py`):

| quantity | value |
|---|---|
| candidates (`M = 110`) | 48,841 |
| enumeration is a bijection of the box | true |
| every submarine hit exactly at `T(a,b)` | true |
| last death | turn 48,841 |
| the coral submarine `(a,b) = (97, −70)` dies on turn | 37,611 |
| a hunter who bombs 0, −1, +1, −2, … ever reaches | **2.61 %** of the box |

The last row is the contrast the piece is built on: the same number of bombs,
thrown in the obvious order, reaches one submarine in forty. Three enumerations
(max-norm shells, L¹ diagonals, an Archimedean spiral) were all verified to be
bijections; shells were chosen because they alone give the shoreline in closed form.

**A note on what is *not* drawn.** The bomb positions themselves are the endpoints
of the threads, dusted in ink at low weight. They concentrate along the shoreline,
because a shell dies all at once.

---

## 2. Every Square Already Knows — the Grundy field of Wythoff's game

**The game.** Two piles `(m, n)`. A move takes any positive number from one pile,
or the *same* positive number from both. `G(m,n)` is the mex of the options'
values; `G = 0` means the player to move has already lost.

**The solver** (`wythoff.c`). The option set of `(m,n)` is exactly
(values above it in column `n`) ∪ (values left of it in row `m`) ∪ (values up the
main diagonal). Keep one bitset per row, per column and per diagonal and the whole
board is one pass: `O(N² · V/64)`. A 2048² board takes 0.03 s, 8192² takes 18 s.

**Verified** against the classical theorem: the zeros are *exactly* the Beatty
pairs `(⌊kφ⌋, ⌊kφ²⌋)` and their swaps — 783 of them on 1024², 1,565 on 2048², with
no extras and none missing. `G` is symmetric; row 0 is the identity.

**What is drawn.** Pigment is `R = G(m,n)/(m+n)`, pushed through its own
distribution so the walk uses its whole range (raw `R` has median 0.78 and the
picture would be one pale wash). Deep = small value. Coral = the squares with
`G = 0`. The fan of deep rays is the real object; the two coral rays are the
theorem sitting inside it.

**Dead end worth recording.** `G mod K` is *perfectly* equidistributed for every
`K` tested (2, 3, 4, 5, 8 — each class within 0.05 % of `1/K` over a million
squares). Any modular colouring of this field is pure noise. The structure lives
in `G` itself, relative to `m + n`.

### A measurement, and a conjecture

Restricted to `n > m`, the level set `{G(m,n) = g}` hugs the golden line. Fitting
`n = s·m + β` on the outer part of an 8192² board:

| g | points | slope | β | 
|---|---|---|---|
| 0 | 782 | 1.618035 | +0.309 |
| 1 | 781 | 1.617986 | +0.309 |
| 8 | 782 | 1.618060 | +0.296 |
| 32 | 782 | 1.616659 | +0.283 |

Every level set has slope φ to four decimals and essentially the same intercept.
More precisely, the **deviation `d = n − φm` over `{G = g, n > m}` lives in a window
that does not move with `m`** — measured octave by octave, `m ∈ (0.02N, 0.06N]`
through `m ∈ (0.4N, N]`, the window for `g = 1` is `[−4.56, +1.96]` in every
octave, on a 2048² board and again on an 8192² board. (This is the Blass–Fraenkel
picture: each `g`-set is a pair of Beatty-like sequences.)

The open part is the **width** `W(g)` of that window. Measured in the regime
where the level set has settled (`n > m` and `m > 6g`), on an 8192² board and again
on a 16384² board — the two agree to the last digit wherever both can see it:

| g | 1 | 2 | 3 | 5 | 8 | 13 | 21 | 34 | 89 |
|---|---|---|---|---|---|---|---|---|---|
| `W(g)` | 6.52 | 7.50 | 10.94 | 13.23 | 15.89 | 22.81 | 26.16 | 36.06 | 79.75 |
| `W(g)/√g` | 6.52 | 5.30 | 6.32 | 5.92 | 5.62 | 6.33 | 5.71 | 6.19 | 8.45 |

**How far this is trustworthy.** A window only counts once it stops moving when the
cutoff is tightened. On the 16384² board, raising the cutoff from `m > 6g` through
`m > 12g` to `m > 24g`:

| g | `m > 6g` | `m > 12g` | `m > 24g` | verdict |
|---|---|---|---|---|
| 34 | 34.78 | 34.78 | 34.78 | converged |
| 89 | 75.01 | 73.25 | 72.53 | converged to ~3 % |
| 233 | 176.26 | 166.29 | 163.96 | still moving |
| 610 | 621.55 | 458.64 | — | **not converged** (−26 %) |

So the raw table's apparent acceleration past `g ≈ 100` — a naive log–log fit over
`g ≤ 610` returns exponent 0.74, and over `g ≤ 1500` returns 0.74 again — is mostly
the board being too small, not the sequence changing character. Over the range that
has actually settled:

> **Conjecture (this run).** For Wythoff's game, `W(g) = Θ(√g)`; numerically
> `W(g) ≈ 6√g`.

`W(g)/√g` stays inside `[5.3, 8.5]` for every converged `g` from 1 to 89, with no
trend that survives the convergence test. It is a conjecture about a two-decade
window, which is exactly as much as a 16384² board can say. **What would settle it:**
`g ≈ 10⁴` needs `m > 6·10⁴`, i.e. `N ≈ 10⁵`. The one-pass bitset solver needs `3N`
bitsets of `4N` bits (≈ 15 GB) at that size — but `G(m,n)` is never far below
`0.7(m+n)`, so starting each mex scan from a per-diagonal lower bound instead of
word 0 cuts the work by two orders of magnitude and brings `N = 10⁵` into range on
one machine.

Also measured, for the record: the *angular* profile of `R` over the outer half of
a 2048² board has its two deepest minima at slope 0.6182 and 1.6194 (depth 0.0135
against a mean of 0.694) — the golden rays, recovered from the picture rather than
from the theorem — plus a symmetric family of shallower rays at 0.3176, 0.3724,
0.4820 and their reciprocals, which I could not match to any simple invariant.

---

## 3. Where You Have Not Looked — Koopman's optimal search

**The problem.** An object is somewhere, with prior density `p(x)`. Spending effort
`φ(x)` on `x` finds it with probability `1 − e^{−αφ(x)}` *if it is there*. Spend a
fixed total `Φ` to maximise the chance of finding it.

Lagrange on `∫p(1 − e^{−αφ})` subject to `∫φ = Φ`, `φ ≥ 0` gives
`αp e^{−αφ} = λ` wherever `φ > 0`, hence

    φ(x) = (1/α)·log( α p(x) / λ )₊          (water-filling)
    posterior given no detection  ∝  min( p(x), λ/α )

Two things fall out, and they are the picture:

1. **You search exactly the super-level set `{p > c}`** — an archipelago, not a
   sweep. Its shorelines grow as the budget grows; four earlier budgets are drawn
   as thin coral ghosts behind the real one.
2. **What you are left with is your own prior with every peak shaved flat to one
   height.** Verified exactly in the render (`posterior_is_capped_prior: true`).

**Numbers** (`where_you_have_not_looked_cert.json`, 1400² grid, budget 0.1 units
per cell, α = 1):

| plan | chance of finding it |
|---|---|
| Koopman water-filling (13.7 % of the sea searched) | **37.4 %** |
| the same effort spread evenly | 9.5 % |
| the same effort in proportion to belief | 30.8 % |

Spreading evenly is four times worse; even the intuitive "look in proportion to
how likely it is" leaves a fifth of the available chance on the table.

The coral bead is the object, in water the plan never touched
(`truth_inside_searched_set: false`). That is the answer to Phil.SE 141771: a
doubt you can price is one you can spend effort on, and the plan that prices it
optimally still, quite properly, declines to look where you are.

---

## Also-ran, and a result I kept

**Pinchuk's map** (MO 512322's neighbourhood). `F = (P, Q) : ℝ² → ℝ²` with

    t = xy − 1,   h = t(xt+1),   f = (t²+y)(xt+1)²
    P = f + h                                                        deg 10
    Q = −t² − 6th(h+1) − 170fh − 91h² − 195fh² − 69h³ − 75fh³ − (75/4)h⁴   deg 25

has Jacobian determinant strictly positive everywhere and is still **not
injective**: only `(0,0)` and `(−1, −163/4)` are missed, the asymptotic variety
has one preimage per point, and every other point of the plane has exactly two.
A fold-free map that still lays the plane down twice.

I meant to draw it and could not make it beautiful in the time — `deg Q = 25`
makes the target wildly anisotropic (the interesting window is about 2.5 units
wide and 60 tall) and a pushed-forward net collapses into bundles. Two things
worth keeping:

* `sympy` expansion gives `deg det J = 30` with 78 terms; I could not find the
  sum-of-squares certificate in the obvious two-parameter family.
* **float64 lies about it.** Sampling `det J` in double precision reports a
  *negative* minimum (−0.179) for `|x|,|y| < 40` — that is catastrophic
  cancellation between terms of size `40³⁰ ≈ 10⁴⁸` against an `O(1)` answer. At
  60 decimal digits (`mpmath`) the minimum over 4,000 samples is `+0.036` at
  `|x|,|y| < 20` and stays positive out to `|x|,|y| < 500`. A degree-30 polynomial
  identity is not checkable in double precision at all.

## Sources

* MathOverflow 515379 (submarine bombing game), 456035 (Alice's winning strategy),
  512322 (Jacobian conjecture, degrees 2 and 3).
* Philosophy.SE 141965 (block / growing block / present universe), 141771 (genuine
  doubt vs. fear), 141905 (contrastive explanation).
* W. A. Wythoff, *A modification of the game of Nim* (1907); A. Blass and
  A. S. Fraenkel, *The Sprague–Grundy function for Wythoff's game* (1990).
* B. O. Koopman, *The theory of search*, Operations Research (1956–57).
* S. Pinchuk, *A counterexample to the strong real Jacobian conjecture*,
  Math. Z. 217 (1994); Campbell, *Picturing Pinchuk's plane polynomial pair*
  (arXiv math/9812032).
