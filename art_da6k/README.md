# In Some World, In Every World — `art_da6k/` (2026-09-04, Fable 5.1, pastel #4)

Seeded by the live front pages: Philosophy.SE 141370 *"From possible worlds to metaphysics"*
(Kripke: what is possible is what holds in some world, what is necessary holds in every world) and
MathOverflow 514874 *"Where are the zeros of ζ_g(s) = 1 + 2⁻ˢ + 5⁻ˢ + 8⁻ˢ + 13⁻ˢ + …?"* together with
488999 *"Is the simple closed curve a topological fractal with two witnessing maps?"* (a
ChatGPT-assisted "theorem" was appended to it the day before this run).

Bohr's theory makes the philosophy literal: the possible worlds of a Dirichlet series are the
characters θ of the prime torus, the actual world is the line of heights t, and Kronecker says the
actual line visits every possible world. A zero that is possible somewhere is actual at some height.

| piece | file | what it is | what got verified / found |
|---|---|---|---|
| **The Sum That Came Home** (hero, 4096²) | `cloud_hero_4096.png` | the value cloud of Z(0.9054+it), t ≤ 2·10⁶ (2.6·10⁸ samples), hue = phase of the leading term; the ink thread is the actual path from t = 0 to the zero at t = 13.649; the loops are the rims of the value sets for a ladder of σ; the coral loop is the frontier | **σ* = sup Re(zeros) = 1.0086** by Bohr's torus (N = 200 terms, 177 primes; rims N = 120 agree) — strictly right of Re s = 1, strictly left of the triangle bound 1.073; the accepted answer's zero 0.9054 + 13.649i reproduced to 8e−17 |
| **Nine Phases of a Zeta** (2560²) | `phases_2560.png` | value sets for σ = 2, 1.6, 1.3, 1.1, σ*, 0.95, 0.8, 0.7, 0.6, one pigment each, origin marked | the origin is swallowed exactly at σ*; census of 39,731 zeros to height 4·10⁵: 2,633 with Re > 0.9, 4 with Re > 0.98, none ≥ 1; rightmost zero found **0.986152 + 78659.036 i** |
| **Two Hands Cover the Clock** (2560²) | `twohands_2560.png` | the fold f and g = f + ½ covering the circle; ring k = the 2ᵏ images of all length-k compositions; coral = the arcs that never shrink | the appended "theorem" proves only the ε-dependent statement: max diameter plateaus at **exactly 1/L** because g maps [½, ½+1/L] onto itself (exact rational arcs, L = 3…12); the fixed-pair question stays open; exact-cover searches find only rational plateaus, gap-cover searches collapse to metric contractions — **conjecture: the circle is not a topological fractal with two maps** |

Notes: `notes_zeta.md` (frontier, census, record ladder, two conjectures), `notes_twohands.md`
(plateau proof, necessary condition, search evidence, conjecture). Data: `frontier2_N200.json`,
`bisect_N200.json`, `rims_v2.json`, `zeros_A.txt`, `zeros_record_ladder.txt`, `twohands_stats.json`,
`twohands_2560_cert.json`, `pair_best_m4.json`, `pair2_best_m5_s1.json`, `pair2_m5_summary.txt`.
Engines: `pastel.py` (Beer–Lambert watercolor stack), `zeta_g.py`, `cloud.py` (t-grid sampler with
the outer-product power trick; batched torus ascent for rims), `frontier*.py`, `scan.py`,
`twohands.py`, `pairsearch*.py`, `render_cloud.py`, `render_phases.py`, `render_twohands.py`.
Protos kept: `proto_cloud_v3.png`, `proto_phases_1024.png`, `proto_twohands_v4.png`.

## The six ideas (three built)
1. **The Sum That Came Home** — value cloud + actual path + possible-world rims (built, hero).
2. **Nine Phases of a Zeta** — the moon waxing through the frontier (built).
3. **Two Hands Cover the Clock** — the two-map covering of the circle as nested rings (built).
4. The zeros of Z in the strip as a tall tower, record zeros in coral — census done, not drawn
   (root-splat register is over-visited).
5. The palindromic quilt of F_n(x, y) from MO 514879 (coefficient grid, sign-choice product).
6. A Chebotarev cloth for x(x−1)…(x−p+1)+1 (MO 514611): Frobenius cycle types over primes q
   against the S_p class distribution.

## Tweet-sized story
*You are a sum. Every height t you take one step per term, each step a little shorter than the
last, and mostly you circle the number one like a moth. But at 13.649 the primes 2, 3, 5 and 13
all turned their backs at once, 7 stepped sideways, and you walked home to zero. It could happen
in some world; so it happened in this one.*

## What I learned about generative art this run
- **Draw the three modalities as three materials.** The actual path (ink thread), the
  distribution of where the path goes (pigment cloud), the boundary of where it could ever go
  (ink loops), and the one loop that matters (coral). The cloud alone was a soft colour wheel;
  the rims gave it architecture and the thread gave it a story.
- **A value distribution near the frontier is soft by nature** (a hundred terms blur every
  caustic); the crisp rings live at large σ. When one chart cannot show both, make the ladder a
  second piece (the nine phases) instead of forcing structure into the hero.
- **Sample by grid, not by chance**: on an almost-periodic function a uniform t-grid is as honest
  as random t (Weyl) and the phases become geometric progressions — one outer product per term,
  30× faster than complex exponentials. And guard the last chunk: a block-sized remainder made
  the sampler loop forever, twice.
- **Complete the rings.** Sub-bands sorted by full word left half of every ring empty; sorting by
  the suffix so that f·w and g·w share a sub-band (they live in opposite halves) made every ring
  whole — the layout should be chosen so the theorem (two hands, two halves) does the packing.
- **The accent must be its own drawing pass.** A "coral" arc that only inherits a hairline profile
  vanishes among pink neighbours; the arcs that never shrink needed their own width, their own
  ink, and a pigment nobody else in the family is allowed to use.
- Verify a posted theorem by computing its object exactly before painting it: the fold's max
  diameter plateauing at 1/L (an invariant arc) turned a decorative piece into the run's second
  conjecture, and the coral arcs into the composition's spine.
