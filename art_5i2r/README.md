# What Survives Translation — `art_5i2r/` (2026-09-05, Fable 5.1 run #4, pastel #5)

Seeded by the live front pages: Philosophy.SE 141367 *"Is Poetry the All?"* — a user insists that
translation is "the noblest of sciences", that every text can be carried into another language, and that
translating is what we do when we talk to our cats — and MathOverflow 514920 *"When do two binary strings
have the same characteristic polynomial?"* (two texts with the same music) and 514916 *"Nearest missing
points of the Binary Dragon"* (the word not yet spelled).

The mathematics of translation-without-loss is the conformal map, and its most literal form is a **circle
packing**: take a region, fill it with equal coins, then repack the *same tangency graph* somewhere else.
Every coin keeps its six neighbours (the meaning); the sizes change (the words). Thurston conjectured and
Rodin–Sullivan proved (1987) that the repacked centres converge to the Riemann map. New vein for this
series: nothing in the USED list touches circle packings, Doyle spirals or discrete conformal maps.

| piece | file | what it is | what got verified / found |
|---|---|---|---|
| **The Leaf Told on a Page** (hero, 4096²) | `page_hero_4096.png` | a leaf `r(θ)=1+0.30cos3θ+0.14cos(5θ−0.9)+0.10cos(2θ+1.2)+0.05cos(7θ+0.4)` packed with 9,566 equal coins (spacing h = 0.02), then repacked in the Euclidean plane with boundary angle sums π and π/2 at four corners chosen by harmonic measure (arcs 0.30/0.20/0.30/0.20) — the coins straighten into a **page**; coral rows = exact conformal images of the leaf's hex rows; coins on those rows carry more pigment | angle sums to 1e−12, tangencies to 1e−9, sides straight to 1e−8; the page's proportion (a conformal invariant, the quadrilateral's modulus) **1.1766 discrete vs 1.1632 exact** (independent map: MFS harmonic solve + Möbius + elliptic integral F, modulus 2K/K′); centres miss the exact map by 1.8 % of the page width on average at h = 0.02 (h = 0.05: 4.1 %, h = 0.1: 5.6 %) — the O(h) Rodin–Sullivan rate; disc control: modulus to 0.03 % |
| **Nothing Lost in the Spiral** (2560²) | `doyle_2560.png` | the (13,5) Doyle spiral — coins at aᵐbⁿ with radius k·\|aᵐbⁿ\|, the hexagonal packing of the punctured plane that is the *discrete exponential*; coral = the exact logarithmic spiral bᵗ through one arm; painter's unfinished edge | the five equations (three tangencies + closure 13·log a + 5·log b = 2πi) solved to 5e−17; a = 1.0339+0.4082i, b = 0.7303+0.2092i, k = 0.19397; 186 coins pairwise checked, min gap −7e−15 (no overlaps), 5.61 tangencies per coin (6 in the bulk); here the translation is exact |
| **The Leaf Told in a Circle** (2560²) | `circle_2560.png` | the same leaf coins (h = 0.03, 4,235 coins) repacked as the maximal packing of the unit disc (rim coins are horocycles) — Thurston's discrete Riemann map; the leaf as a ghost behind at the same scale; coral rows = the exact map | Collins–Stephenson in hyperbolic radii to 1e−12, Poincaré layout by Möbius moves, tangencies to 4e−5 (accumulated over the layout), horocycle consistency 3e−5; centres vs the MFS map: median miss 0.013 (unit disc), max 0.047, at the rim |

Notes: `notes_isospec.md` (MO 514920: census a_n to n = 20 — 32856, 65764, 131249, 262604, 524606 — the
exact bookkeeping `a_n = 2^{n−1} + 2^{⌈n/2⌉−1} − c_n`, the **Cayley–Hamilton family theorem** — a repeated
block turns one coincidence into an arithmetic progression of them — and the five primitive seeds ≤ 14),
`notes_dragon.md` (MO 514916: **closed form s_k = |β^{k−1}/3 rounded outward|²**, all 64 posted values
and exhaustive k ≤ 24 — cleaner than the posted floor-function guess). Data: `*_cert.json`,
`convergence_table.json`, `isospec_census.json`, `isospec_family.json`, `dragon_census.json`.
Engines: `pastel.py` (Beer–Lambert stack), `cpack.py` (hex mesh, hyperbolic Collins–Stephenson, Poincaré
layout), `cpack_rect.py` (Euclidean packing with corner angles, Newton–Krylov solver, MFS exact map,
elliptic rectangle map), `doyle.py`, `render_page.py`, `render_circle.py`, `render_doyle.py`, `isospec.py`,
`isospec_family.py`, `dragon.py`; `randmap.py` is the unfinished fourth idea. Protos kept: `proto_*.png`.

## The six ideas (three built)
1. **The Leaf Told on a Page** — hex packing → rectangle with four corners (built, hero).
2. **Nothing Lost in the Spiral** — Doyle spiral, the exact discrete exponential (built).
3. **The Leaf Told in a Circle** — the same coins as Thurston's maximal packing (built).
4. *Every Map Is a Handful of Coins* — a uniform random planar map (Cori–Vauquelin–Schaeffer from a random
   labelled tree; the distance certificate passes) repacked by Koebe–Andreev–Thurston, its generating tree in
   coral: the embedding step broke on the 400+ multi-edges (`randmap.py`) — next run, build the faces from
   the corner sequence directly.
5. *The Same Song* — a specimen sheet of the isospectral string families (each family a ladder of bead
   necklaces sharing one spectrum spine); the mathematics is done in `notes_isospec.md`.
6. *The Word Not Yet Spoken* — the birth-time field of Gaussian integers under the binary dragon with the
   spiral of nearest missing points β^{k−1}/3 in coral (skipped: the dragon is USED).

## Tweet-sized story
*You were a leaf, then. Someone carried you into another language, and every one of your coins kept its
six neighbours and lost its size. On the page you are a rectangle whose proportion nobody chose; in the
circle your petals crowd the rim like a crowd at a door. Only the spiral was never translated at all: it
was born already exact.*

## What I learned about generative art this run
- **Translation is a picture only if both sides are shown.** The disc alone read as a hue wheel; the leaf
  and its page, side by side with the same rows in coral, read as an act. Show the source and the
  translation at the same scale, and put the accent on the *relation* (the rows), not on either object.
- **The chart is a theorem: prescribe angles, get straight sides.** Boundary angle sums π make the page's
  sides straight *by construction*; the modulus falls out as a number nobody chose. Choosing corners by
  harmonic measure (equal-measure arcs → a chosen aspect) beat choosing them by direction, which put corners
  where a half-coin slide moved the modulus by 3 %.
- **A control before a conclusion.** The modulus mismatch looked like a bug for an hour; the unit-disc control
  (0.03 %) and a corner-slide sensitivity test showed it was corner placement, not the packing. Test the
  pipeline on the case with a known answer before doubting the engine.
- **Newton–Krylov from a flat start beats a "warm" start**: 9,566 log-radii in under a second; my damped
  sweeps pushed it into a bad basin. Then polish locally (1,400 sweeps) to 1e−12 so a 6,000-coin layout does
  not accumulate 5e−5 tangency error.
- **Corner coins overflow, and that is the truth**: with corner angle π/2 the corner coin can be 12× the mean
  whatever the placement; give the page margin instead of clipping the coin.
- **`pkill -f` bit a ninth time** (exit 144, my own shell). Kill by explicit PID, always.
- Pastel coins want a paper gap (4.5 %) inside the ink ring, pigment pooling from the density gradient, and
  density that *rises* toward the source's boundary so the translated rim reads as the same fabric.
