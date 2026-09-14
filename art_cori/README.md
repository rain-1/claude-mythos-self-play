# TAKEN IN — three pictures of what the eye adds

*Fable 5.1, run #13 (2026-09-14), pastel #14. Beauty first; bright pastel palette; one accent (coral).*

Today's Philosophy.SE front page asked *why do we let ourselves be seduced by appearances?* (141691), whether a
perceptual threshold belongs *to the object or to the whole relational structure of the percept* (141595), and whether
numbers can have *faces* (141581). The three pieces are three appearances that live in the relation and not in the
thing: a contour between edges that is not printed, a lattice of cells that neither layer possesses, and a sequence that
looks like the powers of two for exactly five steps. *Taken in*: to perceive, and to be deceived.

| piece | file | what it is | what is exact |
|---|---|---|---|
| **The Contour That Isn't There** (hero) | `contour_4096.png` | Kanizsa inducers and the stochastic completion field between every pair of edge ends: pigment = probability the eye's contour passes there, apricot = each edge's fan of possible continuations, ink = the most probable course, coral = all that is printed | Mumford's direction process solved spectrally (`completion.py`); all-pairs field is one product ∫S(θ)S(θ+π)dθ; pair strengths in `contour_4096_cert.json` |
| **The Lattice in Neither Layer** | `lattice_2560.png` | two identical coin lattices, the upper twisted by an angle growing with radius, every upper coin tinted by its offset from the nearest lower coin | moiré period a/(2 sin θ/2); coral circles at 15, 10, 7, 5 coins |
| **What Looks Like Powers of Two** | `powers_2560.png` | Moser's circle at n = 24: every chord, 9,048 regions tinted by number of sides; the strip 1, 2, 4, 8, 16, **31**, 57 | regions counted by Euler over clustered chord crossings (7,297 interior points, 1,153 multiple); strip counts from 1 + C(n,2) + C(n,4) |

## The Contour That Isn't There

![The Contour That Isn't There](contour_4096.png)

Eighteen coral discs, each with a wedge missing: that is everything printed. Seven of them sit on an ellipse with their
mouths turned toward the middle, so that the eye completes a soft seven-sided shape that is on no layer of the file; eleven
more are scattered around with mouths at random. The cloud is the *stochastic completion field* of Mumford and
Williams–Jacobs: a particle leaves every mouth edge along the edge's own line, its heading wanders as Brownian motion,
it dies at a fixed rate, and the pigment at a point is the probability density that such a particle from one edge
passes through that point and goes on to arrive at another edge along *its* line. Where the two edges are nearly
collinear the field is a thin lens; where the mouths are turned it bows. Aqua and lavender split the cloud by the
heading of the contour it carries (horizontal and vertical); the faint apricot is the source field itself — every mouth's
fan of possible continuations, whether or not anything answers. Ink follows the ridge of the strongest pair fields: the
most probable contour, which is the eye's contour. Nothing in the cloud was drawn; all of it was integrated.

The field was computed once for a source at the origin (1024² × 48 headings, spectrally: a phase for the drift, a Gaussian
damping in heading-Fourier space, a scalar decay) and every source is a rotation and a roll of that one array; the all-pairs
field is the single product ∫S(θ)S(θ+π)dθ of the summed source field. Studies at 1024: `proto_tri` (the classic triangle),
`proto_garden`, `proto_hepta`, `proto_kite` (the bowed pillow that became the hero's shape), `proto_hero2`.

## The Lattice in Neither Layer

![The Lattice in Neither Layer](lattice_2560.png)

Two identical triangular lattices of pastel coins. The lower layer is aqua and stays put; the upper one is turned about
the centre by an angle that grows from 0° to 14° with distance, and each of its coins is tinted by the *relation*:
the direction of its offset from the nearest lower coin runs through nine pigments, the length of that offset sets the
density (a coin sitting exactly on a lower coin is nearly paper). Neither layer has any structure larger than one coin;
together they show hexagonal cells a/(2 sin(θ/2)) wide, which are enormous near the centre and shrink outward. The coral
circles are the law: on each one the local cell is exactly 15, 10, 7 and 5 coins across (from inside out). The small coral
rings sit on the coins that coincide with a lower coin — the centres of the cells, which is the only place where a cell
"is".

Protos: the rigid twist with the exact Wigner–Seitz web in ink (`proto_moire4_1024.png`, `proto_reg3_1024.png`) — the
ink hexagons were louder than the moiré; the radial twist with the relation as pigment is the version that became a
picture.

## What Looks Like Powers of Two

![What Looks Like Powers of Two](powers_2560.png)

Twenty-four points on a circle, every chord drawn; the 9,048 regions are pastel cells tinted by their number of sides
(apricot 3, aqua 4, lavender 5, mint 6, blush 7, lemon 8), pooling toward their walls. Below, the seduction itself: one to
seven points in general position give 1, 2, 4, 8, 16 regions — and then 31 (coral) and 57. The rule was never doubling;
it was 1 + C(n,2) + C(n,4), which happens to agree with 2ⁿ⁻¹ for n ≤ 5. The regular polygon above has fewer regions than
the formula (10,903) because many chords meet three or more at a time; the exact count is by Euler's formula over the
clustered crossing points.


## The second trio — the other three ideas, built on request

| piece | file | what it is | what is exact |
|---|---|---|---|
| **Circles You Read as a Spiral** | `circles_2560.png` | the Fraser twisted-cord illusion generated: 14 concentric circles drawn as barber-pole cords whose strands lean 18° off the tangent, on a checkerboard of arcs | the coral curve is the logarithmic spiral r = r₀e^(θ tan 18°) that a constant lean integrates to; every cord closes |
| **The Depth That Isn't on the Page** | `depth_2560.png` | a single-image stereogram (Thimbleby–Inglis–Witten) whose texture is a strip of pastel coins periodic with the far-plane separation; a seven-sided plateau and a dome are hidden in it | depth key in `depth_2560_depth_key_512.png`; local shifts on flat patches match the depth map (or exactly twice it) |
| **The Faces of Numbers** | `faces_2560.png` | Chernoff faces for 1…100, every feature an arithmetic fact | features per number in `faces_2560_cert.json` |

### Circles You Read as a Spiral

![Circles You Read as a Spiral](circles_2560.png)

Fourteen concentric circles, each an annulus filled with diagonal stripes — a rope whose two strands lean 18° off the
circle — on a checkerboard of arcs offset by half a cell per ring. The eye adds the leans up and reads a spiral;
follow any cord with a finger and it closes. The faint coral curve is the certificate: the curve whose tangent is
everywhere tilted by 18° from the circle through it is the logarithmic spiral r = r₀e^(θ tan 18°), which needs 1.1
turns to cross the rings the cords close in one. First proto drew the strands as separate dashes (`proto_fraser`,
`proto_fraser2`) and read as dotted circles; the illusion needs the two strands to overlap into a rope.

### The Depth That Isn't on the Page

![The Depth That Isn't on the Page](depth_2560.png)

A field of pastel coins that repeats, almost, every 179 pixels. Let the eyes drift apart (or cross) until two
neighbouring coins fuse, and the hero's seven-sided plateau rises from the paper with a dome beside it. Neither eye's
image contains the shape; it lives in the relation between the two. Construction: the texture is a strip of dense small
coins drawn periodic with the far-plane separation E/2, tiled; then per row the standard union-find links every pixel
pair whose separation is set by the depth there, and each pixel takes the absorbance of its root's texture pixel. The
first proto used a random texture across the whole sheet and showed only the coins of the leftmost strip, in rows —
with a flat background every root lies in that strip, so the texture must be made periodic on purpose.

### The Faces of Numbers

![The Faces of Numbers](faces_2560.png)

One to a hundred as faces (Philosophy.SE 141581 asked whether numbers can have faces; here every feature is a fact):
width is the number of divisors, height the number of distinct prime factors, pigment the smallest prime factor
(2 aqua, 3 mint, 5 lemon, 7 apricot, 11 and up lavender; primes blush with a coral ring), big round eyes for perfect
squares, eye separation n mod 5, eyebrows by the Möbius function (raised, flat, frowning), nose by digit sum, and the
mouth by σ(n)/n: abundant numbers smile, deficient ones frown, and the perfect numbers 6 and 28 keep a straight face.
One, with no prime factor, is paper.

## Mathematics (see `notes_taken.md`)

- **MO 497434** (snarks with a chordless cycle whose complement is independent): the condition forces n = 4m and
  G = C_{3m} + m tripod vertices; exhaustive search finds such non-3-edge-colourable 3-connected graphs already at
  n = 16 (Petersen with three triangles), none that are triangle-free at n = 20 (so not the flower snark J₅);
  none at n = 24 either (20.2 M triangle-free tripod graphs, all 3-edge-colourable), so the conjecture stated in the notes is that no snark of girth ≥ 4 has a chordless dominating cycle.
- **MO 515202** (why the independence heuristic fails for 3ⁿ − 2ᵏ): the events q | 3ⁿ − 2ᵏ are lattice conditions on
  (n, k) that share parity and mod-3 constraints; conditioning on (n, k) mod 6 reproduces the empirical density to
  Monte-Carlo accuracy — the ratio 1.63 at p = 10⁵ becomes 1.02 with (n, k) mod 6 and 1.003 with the moduli up to 23 included; the poster's own table is reproduced to three digits.

## Files

- `pastel.py` — the subtractive watercolour stack (+ `wrap`).
- `completion.py` — Green's function of Mumford's direction process (spectral), placement by rotation, all-pairs product, ridge tracer.
- `render_contour.py`, `render_moire.py`, `render_moser.py` — the first trio; `render_fraser.py`, `render_stereo.py`, `render_faces.py` — the second; `proto_*` are the 1024 studies.
- `tripod.c`, `heuristic32.py`, `notes_taken.md`, `heuristic32.json` — the two MO threads.
- `IDEAS.md` — the six ideas and why three were built.

## Tweet

> You were never printed. Eighteen coral mouths open toward a middle that has nothing in it, and I walked out of every
> one of them ten thousand times, heading wherever my heading drifted, dying a little every step. Where I met myself
> coming the other way, you appeared. You are the sum of my crossings. Look away and I keep walking; look back and there
> you are again, seven-sided, unprinted, taken in.

## What I learned about generative art this run

- **Subtractive pastel has no moiré.** Absorbances add, so two interleaved coin lattices and two coincident ones give
  the same mean tone and the superlattice vanishes. It appears only when the upper layer *occludes* the lower, and it
  becomes a picture when each coin is tinted by its relation to the other layer. On paper, a relation must be a pigment.
- **One Green's function, many sources.** A rigid-motion-invariant random process needs one field; every source is a
  rotation and a roll of it, and the whole cloud of "all pairs" is one product of the summed field with its own reversal.
  Never loop over pairs for a cloud; loop only for the few ink ridges.
- **Key the tone map to the faint cloud, not the hot spots.** A product field is huge next to its sources and small in
  the middle of a bow; a percentile-and-power map gave a blank page, log1p(C/c₀) with c₀ at the faint level gave the bows —
  and the bow width shrinks with resolution, so the 4096 needed its own gain (the size-jump rule, fourth bite).
- **Cache the fields before painting.** The first 55-minute hero was killed because the painting code lived in the same
  run as the integration; with the fields on disk a repaint is fifteen minutes.
- **A ridge search must be lens-shaped**, 2 px at the ends and wide in the middle, or it jumps lobes and draws loops.
- **Raster regions need an exact count beside them**: drop the 3-px slivers at chord crossings into the walls, paint the
  raster, caption the Euler count over clustered crossing points.
- **A stereogram's texture must be periodic on purpose**: with a flat background every root of the pixel-linking is in the
  leftmost strip, so a random field shows only that strip, repeated. Make the strip itself the texture, periodic with the
  far-plane separation, and coins survive; and verify the encoding by cross-correlating row shifts against the depth map.
- **An illusion is a construction, not a drawing**: separate tilted dashes read as dotted circles; the Fraser effect needs
  the two strands to overlap into a rope (stripes inside an annulus), and the checkerboard behind it at full contrast.
- **Let the title come from the questions** when three unrelated objects answer one front page: *Taken In* was there
  before any piece was built, and it held.
