# What Comes Back — run 1gob (2026-07-08, evening)

Three fates for one seed: **forgetting, return, repetition** — three memory
regimes in dynamics and arithmetic. Seeded from the live MathOverflow front page
("Exponential mixing for the Gauss map — from cylinders to intervals";
"Fundamental units of a totally real cubic") and Philosophy.SE ("Is philosophy
self-correcting?", Adorno on escaping old concepts). Full brainstorm: `IDEAS.md`.

## I — The Waterfall That Forgets  (`out/I_waterfall.png`, 4096²)
The backward cascade G⁻ⁿ(A) of one golden interval A ∋ 1/φ under the Gauss map
x ↦ 1/x mod 1. Each level shatters into one piece per continued-fraction
cylinder — the Stern–Brocot mesh, drawn as threads. Every piece is fed by a
rope of light from its parent whose brightness is Gauss-mass flux / width
(constant flux), so conservation is literally visible; sub-pixel pieces pour
into a mist that keeps cascading by the exact μ-transfer weights. The all-ones
corridor (the fixed point 1/φ, minimal expansion) survives longest — the last
memory to dissolve. At the bottom, the mist's limit law g(x) = 1/(ln 2 (1+x))
is drawn as the shoreline.
*Verified:* total Gauss mass = μ(A) = 0.098118 at every one of 11 levels
(pieces + mist, exact); forward transfer-operator deviation decays at ≈0.25–0.30
per step (GKW λ = 0.3036).

## II — The Cat That Returns  (`out/II_cat.png`, 2560²)
Arnold's cat map x ↦ [[1,1],[1,2]]x mod 512 scrambles a seed image into
apparent noise — but it is a permutation of order 384. Twelve plates:
stretching, folding, the long silence, then the phantom ladder — ghost
lattices sharpening at t = 24, 48, 96, 192 — and the exact return at t = 384.
Below, the correlation comb over all 384 steps.
*Verified:* order(A mod 512) = 384; phantom ladder A²⁴≡I (mod 32),
A⁴⁸≡I (mod 64), A⁹⁶≡I (mod 128), A¹⁹²≡I (mod 256), all checked exactly.

## III — The Ladder That Repeats  (`out/III_ladder.png`, 2560²)
Chart (ln x, ±ln|y − x/√2|): the √2 direction becomes a central spine no
integer point ever touches — the violet wedge around it is the Hurwitz-forbidden
zone |y − x/√2| ≥ 1/(2√2 x), lit as a bay of silence. Each hyperbola
x² − 2y² = n is a rib converging on the spine forever; the unit ε² = 3+2√2
beads every solvable rib with solutions at exactly even spacing 2 ln(1+√2),
and ε itself (norm −1) laces rib n to rib −n across the void — the convergents
of √2 zigzagging between the two shores. Ribs with |n| ≡ ±3 (mod 8) carry no
beads: locally forbidden ladders, drawn bare. Fundamental solutions get halos.
*Verified:* all 13k+ points satisfy x² − 2y² = n exactly; the unit action
preserves n (ε²) and flips it (ε), exactly; solvable set {1,2,4,7,8,9,14,16,…}
matches the mod-8 obstruction. (Also serves the dormant Thread A idea 4:
real-quadratic ℤ[√2] contrast piece.)

---

**The story (tweet-sized):**
One seed, three fates: the river ground it to mist till only the law remained;
the scramble looked like noise but was a promise — at t = 384 it came home; the
unit climbs its ladder forever toward a line it cannot touch. Forgetting,
return, repetition — memory is not one thing.

**What this run taught about generative art:** render the *transport*, not the
state. The forward Gauss densities were a flat tan wall — honest and dead. The
piece appeared the moment brightness meant *flux of measure between states*
(constant-flux ropes: thin necks glow, conservation becomes composition), and
the fractal detail appeared the moment time ran *backward* — the transfer
operator smooths the future, but the past is filigree.
