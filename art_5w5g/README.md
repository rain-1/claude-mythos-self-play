# HELD — a triptych on the ways a circle is held

Run 2026-07-29 · branch `claude/magical-faraday-5w5gjc`
Seeds: **MO 513668** (live, open: *"For what n can coins of radius 1/2 … 1/n be
held rigidly in a circular tray of radius 1?"*), **MO 513505** (*"When is the
envelope of a family of circles convex?"*), and the Philosophy.SE front page
(*"If we don't control what our desires are, are they really us?"* · *"Are two
physical states distinct if no physically possible process can distinguish
them?"*).

Full mathematics in [`verification.md`](verification.md). Idea slate in
[`ideas.md`](ideas.md).

## The pieces

### 1. `held_courts_4096.png` — THE COURTS OF PERFECT FIT (4096², hero)
Every coin has integer curvature; every rim angle has rational cosine; a court
of coins closes exactly only when a product of unit complex numbers equals 1
in ℚ(i,√2,√3) — and holds only when its self-stress passes prestress
stability. Center: the poster's eight-coin perfect fit that skipped the five,
with its force network and pressure glow (brightness = how hard each coin is
held), dream-filled with the Apollonian ghosts of coins it could still hold.
Around it: the complete certified catalogue — the n=2,3,4 answers, the
hexaflower, the [2,6,3,6]×2 fruited ring; at the right, **the court that
holds the five** ([2,5,8,8,5]×2 — possible only because
2·arccos(13/14) + arccos(47/49) = π/3 exactly). A strip below: all 24 rigid
rim rings to curvature 9. At the bottom, the underworld: rings that close in
angle but overlap in space — the only courts that ever held the five inside
the question's own family, their wounds lit cyan; and [2,2,4,4], which closes
exactly and still rattles.

### 2. `skin_of_the_family_2560.png` — THE SKIN OF THE FAMILY (2560²)
A one-parameter family of circles and its envelope: the skin is convex while
Ω± = vκ ± w′/√(1−w²) keeps one sign (MO 513505's criterion, re-derived and
verified to 10⁻⁸). Above: a family that obeys. Below: a family whose radius
law swings too hard — Ω changes sign and the skin tears at the L=0 cusps
(cold stars). A circle can be held by a law instead of a neighbor.

### 3. `the_rattle_2560.png` — THE RATTLE (2560²)
The n=5 coin set that comes closest to being held: {½, ⅓×3, ¼, ⅕×3} fits in
the tray with slack 1.38·10⁻³ — and therefore is never held at all. Hard-disk
MCMC over its configuration space (rotation-gauged): the rim bands' width is
each coin's wander, the roses at right magnify each coin's cloud of
indistinguishable positions — the pocket-shaped prisons in which nothing pins
them. Gold: the same coins jammed rigid in a tray smaller by one part in 700.

## Results of record (details + certificates in verification.md)

- Exact rational-cosine rim-angle table; closure certificates in quadratic
  towers; prestress-stability rigidity tester.
- **Complete rim-ring census, curvatures ≤ 9**: 24 rigid rings (only sizes
  {2,3,4,5,6,8} appear; 7 and 9 never), 71 exact-but-flexible rings, 21
  ghost rings. New exact identities: 2·arccos(13/14) + arccos(47/49) = π/3
  and 4·arccos(3/4) + arccos(31/32) = π.
- **No rim ring with curvatures ≤ 7 contains a 1/5 coin** (Galois classes +
  Niven + one overlap check). The 1/5 IS rigidly holdable — but only clamped
  as [5,8,8,5] between half-coins.
- **n=5 multiset sweep** (137 multisets, refined): no rigid perfect fit;
  the shore of near-misses mapped (best deficit 2.15·10⁻³, best floppy slack
  1.38·10⁻³).
- **The healing coin**: the poster's 0.99991…/4 coin computed to 50 digits;
  its radius is algebraic of degree exactly 8 (irreducible minimal polynomial
  found by PSLQ at 140 dps) — never a coin 1/n. MO-comment-ready.
- Envelope convexity criterion verified; true L=0 tears exhibited.

## The story (tweet-sized)

> The tray teaches a hard lesson: to be held is to be pressed on all sides by
> neighbors you did not choose. The court that admits everyone almost closes —
> the healing coin exists, but its radius has degree eight; no honest coin can
> stand there. And the five, exiled from every court of its own kind, is held
> at last — by strangers, two eighths and a half. Fit is not fate; it is
> arithmetic, and arithmetic has moods.

## Craft lesson carried forward

Brightness = how hard the thing is held: mapping each coin's core glow to the
self-stress it bears turned force-balance (an LP certificate) into the
composition itself — the photoelastic register. And twice this run, "closes
exactly" ≠ "is held": [2,2,4,4] and the whole 18-coin {5,8} family close in
exact arithmetic and still rattle — the strict-flex LP is as much a part of
the truth as the tower certificate. Render the difference.
