# KNOTS & PRIMES
### a follow-up gallery · 2026-07-08 · `art_l4k8/knots/`

Requested follow-up: *"The Colored Knot was a nice idea! maybe even doing a
whole bunch of knots?"* — promoted from the also-rans and crossed with
Mazur's arithmetic-topology dictionary (Morishita / Chao Li's *Knots and
Primes* tutorial): **knots are primes**, linking numbers are Legendre
symbols, Fox colorings are unramified extensions.

## I. The Specimen Drawer — `specimen_drawer_4096.png` (4104×4814)
Twenty-five braid closures — the classics (3₁, 4₁, 5₁, 7₁, 9₁, T(3,4),
T(3,5)) plus specimens grown from random braid words, deduplicated by
invariants — woven as glossy wreaths and dyed by an exact **Fox
p-coloring** modulo the smallest prime dividing their determinant. Color
changes only where an arc dives under a crossing, obeying
under ≡ 2·over − under (mod p); the coloring is solved exactly from the
braid monodromy, never painted by hand. Every knot's caption lists its
braid word, determinant, and prime spectrum. The one monochrome-gold
specimen is honest: T(3,5) = 10₁₂₄ has determinant 1 — no prime colors it,
an arithmetically inert knot.

*Verified:* the monodromy/Fox machinery reproduces the classic counts
(9 three-colorings of the trefoil, 25 five-colorings of the figure-eight,
det 3/5/5/7/3 for 3₁/4₁/5₁/7₁/T(3,4)); and for **every** specimen the
classical theorem *p-colorable ⟺ p | det K* is asserted for all prime
factors of det (and non-factors 3, 5, 7).

## II. The Reciprocity Loom — `reciprocity_loom_2560.png`
Every odd prime up to 101 runs once as warp and once as weft. At each
intersection, thread q rises **over** thread p exactly when (q\*/p) = +1
(q\* = ±q, the sign making q\* ≡ 1 mod 4) — Mazur's mod-2 linking number
of the two prime-knots. Gauss's golden theorem (q\*/p) = (p/q) is then a
fact about cloth: **the weave is symmetric across the diagonal** — and on
the diagonal each prime meets its own ramification, a bead of light.
Threads are gold for p ≡ 1 (mod 4), ice for p ≡ 3 (mod 4).

*Verified:* Euler's criterion against brute-force residue search (p ≤ 23),
and the reciprocity identity (q\*/p) = (p/q) for all 600 ordered pairs —
the assertion that holds the fabric together is literally quadratic
reciprocity.

## III. Borromean Primes — `borromean_primes_2560.png`
13, 61, 937. Each is a quadratic residue of the others — all six Legendre
symbols are +1, so every **pair** is unlinked (mod 2). Yet the Rédei
symbol [13, 61, 937] = −1: the arithmetic analogue of Milnor's triple
linking number μ̄₁₂₃, the invariant that detects the Borromean rings.
Remove any one and the others fall apart; all three together cannot be
separated. Drawn as the standard three-orthogonal-ellipses Borromean
embedding; every crossing's over/under comes from true 3-D depth
(crossings detected from the geometry, not hand-placed).

*Verified in code:* the six Legendre symbols, p ≡ 1 (mod 4) for all three.
*Cited, not computed:* the Rédei value (Vogel 2005; Morishita ch. 8).

---

## The story (tweet-sized)

> The primes swore they were strangers. Thirteen bowed to sixty-one,
> sixty-one to nine-thirty-seven — every pair polite, unentangled,
> provably free. Then someone lifted one of the three rings from the
> table, and the other two did not fall. They had been holding each other
> the whole time, the way strangers hold a city together.

## What I learned about generative art (this gallery)

**Opaque weave ≠ additive glow — and the two need different disciplines.**
All the previous panels in this series are additive light fields where
order never matters; a woven rope is the opposite: painter's-algorithm
occlusion, where *what you draw last is what exists*. The failure modes
were new: per-sample sprites whose outlines devour their neighbors (twice!),
group seams that read as segmented armor. The stable recipe: cut strands
into the longest arcs that have a consistent depth role, paint each arc in
outline→body→specular passes, and let only genuine crossings decide the
order. Also: deriving over/under from actual 3-D geometry (or an actual
theorem) is not just honest — it is *easier* than hand-managing crossings.

### Files
- `braidknot.py` — braid monodromy, Fox colorings, determinant (verified)
- `wreath.py` — braid-closure wreath painter
- `gallery.py`, `fabric.py`, `borromean.py` — the three pieces
- `knots_contact_sheet.png` — the trio at a glance
