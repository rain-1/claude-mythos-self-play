# PASSING — three studies of the gap between passing the test and having the property

Run 2026-07-31 · branch `claude/magical-faraday-mt4zvc` · seeded from the live
MathOverflow + Philosophy.SE front pages ("Are some people zombies?" — the
behaviorally-perfect impostor; "epistemic humility").

Every picture is computed from scratch and certified; see `verification.md`.

## The pieces

### 1. `hero_final_s42_d0.70.png` — **The Republic of Rest** (4096²)
MO 513737 *"A Level (not wobbly) table theorem?"* (live, unanswered).
One smooth floor on the unit disk, h = 0 at the shore.  The wobbly-table
theorem seats a four-legged square table *everywhere* — all four feet
touching — but almost never level: that is the violet atmosphere (brightness
= how level the best balanced rest gets).  A three-legged table rests level
along **19 closed curves** in (position × angle)-space — the teal rivers,
drawn by 21,406 traced placements with all foot-heights equal to 1e-10.
A four-legged square stands truly level at **exactly 4 isolated placements**
— the gold squares.  Touching is a surface, resting level is a curve,
standing true is a point.

### 2. `seams_final.png` — **The Seams to the Horizon** (2560²)
MO 122539 *"The unreasonable effectiveness of Padé approximation"* (69 pts).
f(z) = (1−z³)^(−1/2) has three branch points on the unit circle and a fourth
at infinity.  The Taylor polynomial of degree 291 (cold pupil) dies exactly
at |z| = 1.  The [144/144] Padé approximant built from the *same* 97
coefficients illuminates the whole plane (warm field; its exact error law
2|φ(z³)|⁹⁷ verified to 0.012 digits at 400-digit precision).  A rational
function has no branch cuts, so the impostor sews seams of alternating
pole-zero stitches along the three rays — every pole real to 220 digits,
interlacing, exactly as Markov's theory demands — and because infinity is
itself a branch point, the seams run off the edge of the map.
At z = 1.7+0.4i: Taylor error 3e+68, Padé error 3e-14.

### 3. `polya_final.png` — **The Nine Hundred Million Winters** (2560²)
Pólya's conjecture (1919): L(x) = Σ λ(n) never goes positive after x = 1.
λ sieved from scratch for every n ≤ 2³⁰ (own segmented C sieve, ~3 min).
The coastline is L(x)/√x, linear in x; the gold line is the law.  It holds
for 906,150,254 consecutive integers and breaks at **x = 906,150,257**
(Tanaka 1980, reproduced exactly), an archipelago of 136 positive islands
totalling 305,426 integers, peak **L = +829 at x = 906,316,571**, closed
again by 906,488,079 — magnified in the inset.  The sea looked like a law
for forty years.

## Code
- `table_lib.py`, `hero_table.py`, `sweep.py` — level-table machinery
  (analytic terrain, Newton continuation, curve tracing, tilt field)
- `pade_lib.py`, `pade_render.py` — exact-rational Padé + mpmath certificates
- `liouville.c` / `liouville2.c`, `polya_render.py` — Liouville sieve + render
- `rkit.py` — shared render kit
- `verification.md` — all certificates and the two little lemmas
  (square-coplanarity ⟺ diagonal sums; the 120°-rotation monodromy of a
  tripod's height differences)
