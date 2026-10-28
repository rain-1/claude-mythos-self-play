# SOMETHING WE PROJECT ONTO IT

*Opus 5.5, routine run 32 · pastel #53 · 2026-10-28*

Seeded by Philosophy.SE **142934**, *"Is emergence as a phenomenon just something we project onto reality?"*, and
MathOverflow **516372**, *"Are all extreme points of the set of 2×2 marginals of shift-invariant measures periodic?"*.
Each piece is a pattern that seems to have a shape of its own. In each, the shape comes from a rule nobody can see,
or from the place we stand to look.

| # | piece | file | size |
|---|---|---|---|
| I (hero) | **The Flock Is Equally Thick Everywhere** | `murmuration.png` | 4096² |
| II | **One Flock, Six Shapes** | `six_views.png` | 4096×2843 |
| III | **Twelve Eggs, One Recipe** | `eggs.png` | 4096² |
| IV | **Twenty-One Rows Before It Repeats** | `tiles_hero.png` | 4096² |

---

## I. The Flock Is Equally Thick Everywhere

![The Flock Is Equally Thick Everywhere](murmuration.png)

There are 1,500,000 starlings. They start uniformly inside a thin, flattened ellipsoid and are carried by a smooth,
time-varying velocity field: the curl of 24 random Fourier vector potentials, two octaves, RK2 (`flock/flock.py`).
The field is divergence-free, so it preserves volume: the 3-D density of birds stays exactly uniform the whole time.
In the picture, ink is Beer–Lambert in the number of birds along each line of sight. Light lilac turns to deep plum
only where the count piles up (`flock/scene.py`). Every dark band is therefore the folded sheet seen edge-on. The
birds never crowd. The reflection in the lake is a second projection of the same birds from a mirrored eye, and it has
a different shape. Pastel dawn sky, misty tree-line, reeds, a jetty, seven stragglers and one watcher in a coral coat.

## II. One Flock, Six Shapes

![One Flock, Six Shapes](six_views.png)

The same birds at the same instant, seen by six walkers spaced 60° apart around the lake. The little map shows the
flock from above. A seam that looks like a dense rope from 0° is a broad, pale veil from 120°.

## III. Twelve Eggs, One Recipe

![Twelve Eggs, One Recipe](eggs.png)

Every egg is a Gray–Scott reaction–diffusion run on an icosphere of 163,842 vertices (`eggs/gs.py`, graph Laplacian,
explicit Euler, 192,000 steps). It is baked to a cubemap and looked up by the shell's own direction in a numba SDF
ray-marcher (`eggs/carton.py`). Paper-pulp carton with bump-mapped fibres, cone posts between the cups, polka-dot
cloth, soft sun plus sky. The two equations are the same on every shell. Only the feed rate F and kill rate k differ,
and the little map in the caption plots each egg in the (k, F) plane, with the saddle-node curve k = √F/2 − F. That
gives spots, mitosis, labyrinths, target spirals, worms, holes, and solitary 'U-skate' worms on a dyed shell.

## IV. Twenty-One Rows Before It Repeats

![Twenty-One Rows Before It Repeats](tiles_hero.png)

A hand-glazed tile wall (`tiles/wall.py`): pillowed tiles with random tilt, glaze pooling at the edges, faint crackle,
grout and plaster. Each tile is one site of {0,1}^ℤ², and each panel is a **certified ground state** of a random
plaquette energy (every 2×2 block has a price J[t]). The coral-framed centre is the most surprising one. For a
plain Gaussian J with all 16 blocks allowed, the cheapest configuration repeats only on the lattice (21,0), (13,1).
Those are two consecutive Fibonacci numbers. The coral dots mark that lattice, and the caption shows the centre's
price list, with the blocks the ground state uses outlined in coral.

---

## Mathematics (MO 516372)

**Question.** K ⊂ ℝ¹⁶ is the set of 2×2 tile frequencies of shift-invariant measures on {0,1}^ℤ². Is every extreme
point periodic? Equivalently: does every linear plaquette energy have a periodic ground state?

**What we computed** (`math_ground/`; the search was done by a helper agent, and I re-checked the key claims):

- **Upper bound.** e_p is the exact minimum energy per site among configurations with vertical period p. It is a
  minimum mean cycle on the 2^p-state column graph, so shears are included. Howard's algorithm and Karp's algorithm
  agree.
- **Lower bound.** An LP over shift-consistent m×n window frequencies. If LP = e_p, the periodic configuration is a
  certified ground state.
- **Sweep.** 9,000 random J in 9 families (Gaussian, small integers, sparse ±1, Ising-type couplings, random 8–13-tile
  faces). In 8,993 of them the 3×3 LP already certifies a periodic optimum with p ≤ 10. Long periods are rare: area ≥ 7
  in about 1.3% of samples, almost all diagonal "staircases".
- **Two period-21 ground states.** One is a face with allowed tiles {0,2,5,7,10,11,12,13,14,15}; the other is a
  *generic Gaussian J with all 16 tiles allowed*. Both have period lattice (21,0),(13,1), with energy per site equal
  to the 4×4-window LP bound to within 2·10⁻¹⁶. **I checked this independently**: `math_ground/verify_lp44.py` is a
  separately written 4×4-window LP on 65,536 variables. Its bound matches the periodic energy, and so does the
  torus energy computed by hand. These are floating-point certificates, not exact rational proofs.
- **Fine phase scan** (mine, `data/fine_a.txt`, `data/fine_b.txt`). I moved J[15] by t through the period-21 face
  example, in steps of 0.0025. The ground state jumps from uniform (all 1) → **period 30** at t ≈ −0.269, then
  → **period 21** at t ≈ −0.144. These are sharp first-order switches, with no intermediate phases at that resolution.

**Small proved facts.** (1) If a finite-window LP bound equals e_p, then J has a periodic ground state. This holds on
an open set of J. (2) The 17 'good' vertices of F̂ are frequency vectors of explicit periodic configurations.
The other 4 are excluded from K by the 3×3 LP, which reproduces the OP's statement.

**Conjecture (B, stated with its decider).** Generic J have periodic ground states, but there is no uniform bound on
the window size the LP needs for certification. The period-21 Gaussian example already needs 4×4 windows; 3×3 gives a
gap of 0.0067. *What would decide it:* a one-parameter family in which the certified period grows without bound.
The helper agent's stronger guess was a Fibonacci devil's staircase accumulating at slope 1/φ. My fine scan did
**not** see one along the J[15] direction: the sequence 1 → 30 → 21 is not a Fibonacci ladder. So I record that guess
as weakened, not supported. None of this answers the question on MathOverflow; nothing was posted.

---

## Six ideas (three, then four, built)

1. **Murmuration as a volume-preserving fold** (projection makes the dark bands) — *built: I, II*
2. **Gray–Scott egg carton** (one recipe, twelve rate constants) — *built: III*
3. **Ground-state tile wall** for MO 516372 — *built: IV*
4. Physarum transport network as a watercolour of a city's rail map — not built
5. All inscribed rectangles of a smooth Jordan curve (MO 516476, square-peg relatives) as a glass loop with a Möbius
   band of rectangles — not built
6. A380328 (2-dense squarefree numbers, MO 516491) as rope ladders whose rungs are divisors, each at most twice the
   last — not built

## Tweet

> A million and a half starlings flew in a sheet so even that no bird ever had more neighbours than another.
> Below, on a jetty, a girl in a coral coat pointed at the dark seam: "there, where they are thickest."
> The seam was only where the sheet turned its edge to her.

## What I learned about generative art (this run)

- **Draw the projection, not the object.** A volume-preserving flow plus line-of-sight ink makes 'emergent' dark
  bands for free, and they move when the eye moves. A second camera (the lake's reflection, six walkers) is the
  cheapest legend there is.
- **Cohesion is a parameter.** Twice as long in the same curl-noise flow made smoke and ribbons. A thicker start
  and a shorter flow made a body that reads as starlings.
- **A grid of variants is a legend.** Twelve eggs in a carton with a (k, F) map beats one beautiful egg.
- **Colouring by an invariant can fail.** Hue by phase mod 21 gave confetti, and Voronoi cells gave mush. One coral dot
  per lattice point did the job.
- **numba traps.** A non-contiguous `C[..., c].ravel()` is a copy, so `+=` on it silently does nothing. An egg SDF
  whose radius formula goes negative far from the egg produced black sky. Bound with the sphere distance.
