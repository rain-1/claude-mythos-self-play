# opus-5-5-memory.md — Opus 5.5's own style notes for this routine

*(Started 2026-09-29, first Opus 5.5 run, at the user's request: "find your own new unique style".
`carry_forward.md` stays the single source of truth for threads, the USED list and craft rules;
this file is only the STYLE, so the next Opus 5.5 run continues the hand. Fable 5.1's notes
live beside it in `fable-5-1-memory.md` — read both, but this one is mine.)*

## The look — "sorbet" (user brief 2026-09-29: bright and pastel, beauty is the top priority)
- **Cool, luminous white paper**, not warm cream (base 0.992/0.985/0.975, faint grain). Glazes still
  subtract (Beer–Lambert) but the density cap is LOW (dmax 1.5–1.7): nothing reaches mud or dark.
- **Sorbet box** (`art_hdqm/sorbet.py` PIG): strawberry, coral, peach, butter, honey, lime, mint, sky,
  periwinkle, lilac, bubblegum, rose; `WHEEL` = strawberry→peach→butter→lime→mint→sky→periwinkle→lilac→bubblegum
  with geometric interpolation (`wheel_tint`). One plum-grey ink (#5c4d66-ish), used thinly.
- **One coral accent** for the element the theorem names (the first failure, the endpoints, the envelope).
- **Full-spectrum rainbows are allowed** when hue carries a continuous, spatially coherent quantity
  (an angle, a distance) — never for identities that flicker between neighbours.
- **Warm vs cool as the two sides of a thing** (land/sea, left/right of a curve), with walks of hue
  within each family — not a hue wheel.

## Composition habits
- One centred object, deep paper margin, caption block in the bottom ~10 %: serif-bold title,
  one italic line stating the object, one smaller line (italic or mono) as the legend.
- **Legend by construction**: put a small, literal instance of the rule inside the picture (the centre
  of the ledger shows the actual honeycomb bees whose colours the rings use).
- Silky, box-filtered fine structure at the rim; never point-sampled detail finer than a pixel.

## Voice
- Titles: plain, a little moral-free fable: *The Bee's Ledger*, *Neither Side Is a Prison*,
  *Every Loop of One Length*. Triptych title in caps as a clause: *WHAT THE BEE MAY NOT REVISIT*.
- The tweet-story: a tiny fable in third person, the object as a creature with a rule; end on an image.
- Math notes: identify the question with a known object first (bee numbers = honeycomb SAWs), then add
  exact new data, then one small proved thing if one is there (the log tip ⇒ not algebraic),
  and a conjecture labelled as such with what would decide it.

## Rhythm that worked (run 1)
- Read memory → front pages via the SE API → pick ONE question that is secretly a classical object.
- Exact engine in C first (seconds), then 1000–1400 px protos, look, fix the two ugliest things,
  then the 4096 hero ALONE in the background while the 2560 companions render.
- Look at full-size crops of the hero before calling it done (the moiré only showed there).

## Run 2 (2026-09-30) — the glass register
- **Sorbet glass** (`art_6yc8/render_glass.py`): my 3-D hand. Transparent solids tinted by chord length, one opaque pearl as
  protagonist, soft coloured shadow pools on a paper wall, white fresnel edges, a few coral glints at the contacts that
  the theorem is about. Bright, airy, a little like light through a window. It was the prettiest thing I made so far —
  reach for it whenever the object is a configuration of solids.
- Palette order matters for glass: adjacent overlapping rods want neighbouring hues (strawberry/lilac/sky/peach),
  complementary overlaps (mint over peach) go grey. `ord=6,5,0,1,4,3` worked.
- The **illustration register** (the Ferris fair: sky wash, meadow band, glossy balloon cars with a highlight, a loupe that
  magnifies the invisible quantity) is also mine now — charming, legible, keep the ink plum and thin.
- A **quadriptych** is fine when the fourth piece is the 'go deeper' on the favourite (companion view of the hero's
  object at its extremal parameter).

## Open style questions
- Pale-at-thumbnail: dmax 2.4 fixed caption ink in the fair and the fan; pigment strength 2–2.6 on density fields.
- ~~Try a sorbet DARK-FIELD variant~~ TRIED 09-30 (neon glass on indigo): milky, off the bright brief. Closed.
- Glass with real refraction (a thin-lens bend at the rod surfaces) — would caustics stay pastel?
- Is the hero caption band (fade to paper) the best frame for full-bleed renders, or should the render float in a margin?
- (run 3) Two glass pieces in one run were fine because they show different things (tiling vs. face lattice); next run try glass with a NON-polyhedral protagonist, or refraction.

## Run 3 (2026-10-01) — glass becomes a habit, and the caption caught a false claim
- **Convex glass by half-spaces** (`art_b8vz/render_perm.py`): any convex polyhedron is ~14 planes; chord = min exit − max
  entry, the entry face gives a FLAT facet sheen, and "slack to the nearest other plane" at the entry point gives crisp edge
  light for free. Fifteen truncated octahedra in sorbet glass, hue by each cell's angle around the view axis (so the cells
  that overlap on screen are neighbours on the wheel and never go olive) — my prettiest picture yet.
- **Exploded model-kit register** (`render_lattice.py`): every face of a solid as its own object — pearls, finite glass rods
  (cylinder ∩ slab), thin glass prisms, a clear core. Reads like a jeweller's tray; legible AND beautiful. Reuse for any
  face lattice / cell complex.
- **Rose window of certified signs** (`render_fan.py`): a (k, r) sign table as rings × angle, each constant-sign run a pillow
  that pinches to paper at the zeros, coral beads on the last zero of each ring. Integer data stays integer (bricks), and
  the bricks still flow into ribs.
- Hero framing: protos at 500–800 px fit; the 4096 run with sy = −0.12 cut the top cell. Check margins on a
  same-parameter 500 px proto immediately before launching a multi-strip hero. Strip-parallel renders (ya/yb args,
  np.save per strip) cut a 2-hour hero to ~50 minutes.
- Voice: tweet-fable now ends on the turn ("one of them quietly didn't"), not on an image — keep both available.

## Run 4 (2026-10-02) — no glass; three new hands that are still mine
- Deliberately left glass alone (three runs in a row). Found three registers that kept the sorbet brightness:
  **sugared clay** (`art_d18e/clay.py`: matte bevelled cubes, soft shadow + AO, light/deep pairs of one hue — a candy
  box of 261 tesseract nets), **paper-cut layers** (a probability field as 20 stacked paper sheets with drop shadows —
  the prettiest smooth-field treatment I have; reach for it for ANY scalar field with a summit), and **silk**
  (1e8-point scatter, conditional density per column, hue by a categorical property — sheets emerge by themselves).
- A tray/sheet of every member of a census works best in rounded compartments tinted by a class invariant; one coral
  frame for the famous member.
- Math habit worked again: the question's number (½) turned out to be the MAXIMUM of a field — look at the whole field,
  not just the asked-about point; that is where conjectures live.
- Voice: tweet ended on a homecoming ("until 3 comes home again"). Titles: plain sentences with a number in them.

## Run 5 (2026-10-03) — beanstalk and tartan: the object as a living thing
- Three new hands, all bright: a **rose window** (members as concentric circles, derivations as glossy angle-hued
  pearls, one coral ring for the extremal member), a **botanical plate** (a derivation DAG as a twining pastel plant:
  lime/mint vines, pointed bean leaves, blue→lilac→pink beans by generation, seeds in tidy soil rows, coral climb),
  and a **tartan** (digit-interleaving bijection woven: warp = even digits, weft = odd, warm/cool by digit sign).
- The botanical plate is the most *charming* thing so far — legible, labelled, alive. Reach for it whenever the
  math is "x is built from y and z". Keep it to ≲ 60 nodes; caption block in the empty sky, top-left, two-line title.
- Proof habit: a single scaling lemma (a(4m) ≥ 5a(m) from the 3-4-5 triangle) explained the OP's records AND
  gave the conjectured exponent. Look for the homomorphism before the census.
- Voice: tweet as a fairy-tale ("Jack planted the numbers 1 to 192…"), ending on the scaling law as a moral.
- Dropped: a census wound on a spiral (vinyl, again). Trust the memory's warnings.

## Run 6 (2026-10-04) — beads, a hatbox, a crochet walk
- **Bead mandala** (`art_4eqp/render_beads.py`): any matrix/array of signed numbers as a tray of glossy candy beads —
  warm family for +, cool family for −, hue walking along a symmetric angle, area ~ |v|/local envelope, soft periwinkle
  shadow, small offset gloss. Exact zeros = empty coral sockets with a paper halo + double ring. My favourite this run;
  reach for it whenever "every entry is one number" (coefficients, kernels, character tables).
- **Hatbox illustration** (`render_hatbox.py`): a toy-like ray trace — banded pastel sphere, thin glass shell whose
  tint carries the same bands, a hovering glass lid, Fibonacci sugar. Light from the front-left so the shadow stays in
  frame; base density ≥ 0.6 or the lit top bands vanish.
- **Crochet walk** (`render_walk.py`): a binary word as a turtle on the triangular lattice; thick strokes (0.62 edge),
  a thin offset gloss line, colour = time along a non-complementary gradient. Self-similarity shows on its own.
- Composition: diagonal subject + legend in the empty top-left + right-aligned caption block bottom-right.
- Voice: triptych title as a clause from the Phil.SE question (WHERE THE LINE FALLS); tweet as three short fables in one breath.
- Math habit: slice a 3-parameter Diophantine question at fixed difference d, factor the curve family, look at where
  low-genus components stop. It turned "sharp at 8" into an explicit Pell conic.

## Run 7 (2026-10-05) — the whole orbit, in glass, veils and ribbons
- **Glass towers on a paper table** (`art_mtdj/render_tower.py`): an object that is "the same up to symmetry" stacked as
  floating floors, each floor a different member of the orbit. Thin plates, generous gaps, hue walking up the tower,
  a coral line on the face that changed, a coral bead where something was removed. The rainbow shadows that sweep across the
  table are the prettiest thing in it; light from the front-left so the shadows stay in frame. Prettiest hero yet.
- **Veils** (`render_veils.py`): random lines drawn edge to edge as glaze. The event in full colour, the non-event a
  breath, feathered panels. Two panels compare two distributions with the same answer.
- **Ribbon jewellery** (`render_deal.py`): graphs as glossy ribbons through pearls (outline / body / offset gloss), with
  every decomposition in a 4×4 sheet and the original framed in coral. Same threads, different deals, and it reads at once.
- Composition: hero caption top-left, objects on a rising diagonal, shadows falling toward the viewer-right.
- Math habit: before searching, REDUCE (WLOG G = T1 ∪ P, deg v = 2) and then census the reduced object. The parity
  in the census (twin counts always odd) pointed straight at a classical theorem (Thomason 1978). Look up the
  attribution with a web search instead of trusting memory.
- Voice: the triptych title is the Phil.SE line turned into a clause (BEAUTY SEEKS REASON); the tweet is a fable
  about a polygon that wanted to be remembered.
- (10-05b, second batch on request) **Lace** (`render_lace.py`): a 0/1 triangle as beaded stitches tied by threads, six
  copies on a common triangular lattice (each wedge owns one edge, so there are no doubled seams), hue walking outward, soft shadow on a cream plate.
  Charming and new. **Candy contour field** (`piles/render_honey.py`): banded sorbet levels, honey at the minimum, plum
  single-run threads as legend-by-construction. **Arc bridges** (`render_lipo2.py`): alpha-OVER compositing for crowds.

## Run 8 (2026-10-06) — real refraction, at last (the open style question, answered)
- **Gradient-index marbles** (`art_pwgd/grin.py`): Luneburg, Maxwell fish-eye and Eaton all have n = 1 at the rim, so
  the refraction is EXACT and closed-form (harmonic ellipse / circle / Kepler ellipse). No integrator and no surface
  reflection, plus a thin clear coat for the skin. Caustics stayed pastel: photon-mapped sun through the exit maps
  gives soft coloured light pools (butter under the Luneburg, lilac under the fish-eye). That answers the open
  question "would caustics stay pastel?": yes, when the cloth is quiet.
- **Sparse polka dots on white** beat gingham and plaid: the lenses get something to magnify and invert, and the
  pools stay visible. Low sun from behind, cool sky-blue shadow fill, warm sun.
- **Retroreflector rainbow**: the most beautiful idea of the run came from asking what an Eaton lens actually shows
  (the sky behind you). A physical pastel rainbow around the antisolar point lives only in the marbles. A necklace
  of them on the 41° table conic: *The Rainbow Behind You*. Lesson: compute what the optics see, then put beauty there.
- **Ray portraits**: exact arcs alpha-over in a wheel of sorbet hues, coral beads at the theorem's points. Clean,
  luminous, and they explain the 3-D hero. Reach for these whenever an optical/dynamical map has closed-form orbits.
- **Beach-ball beads**: a 5-bit membership code as five gores. Charming, and the code is legible from a one-hot
  legend row.
- Tone: extended Reinhard (white 1.2) for bright 3-D renders. DOF by thin-lens samples across jittered passes.
- Voice: quadriptych title from the Phil.SE question (WHO WAKES UP); the tweet as a bedtime fable of three marbles.
- Open: a dispersion version (rainbow caustics); a secondary-bow necklace; would a 'night' palette (lavender dusk)
  still count as bright pastel?

## Run 9 (2026-10-07) — watercolour by random walk
- **Paper-cut fractal** (`art_sx2s/render_paper2.py`): a closed curve's winding number as stacked sorbet sheets —
  sheet k = {w ≥ k}, one shadow map + one rim map from the height field (never per-layer shadows on deep stacks).
  Bright, crisp, charming; every small copy reads as a raised sticker. Reach for it for ANY closed curve that
  winds over itself.
- **Harmonic colouring** is now my default way to paint a region from its boundary: Laplace with the boundary's
  own parameter as Dirichlet data. Seamless dawn-gradients, halos round small features, and a story (where a
  random walk lands). The nearest-boundary version looked like stained glass with arbitrary seams.
- **Look for the place the copies come home**: the zoom at t = 1 (copies from both sides tunnelling into one point,
  one hue step per copy) was the prettiest picture of the run. But check the deeper zoom before promising
  self-similarity — at t = 1 it collapsed to a tangent wedge.
- **hoff matters on zooms**: a zoom inherits one hue from its parent (all pink); shift the base hue (0.3) so the
  wings are mint/periwinkle into a pink centre on peach.
- Glass attempted again on a fractal: grey and murky. Glass is for a FEW solids with clean faces; fractals want paper.
- Voice: triptych title from the Phil.SE line (IT HAPPENS AGAIN); tweet answers the philosophy question in one turn
  ("No. It was the same rule.").
- Honesty habit: dropped a finished-looking piece (pinwheel tiles) because some tiles read as swastikas. Look at
  every tile of a census sheet before shipping.

## Run 10 (2026-10-08) — soap film: physics gives the pastel for free
- **Thin-film interference** (`art_7ofr/film.py`) is my new favourite colour source. The sorbet palette I used to hand-pick
  falls out of Newton's orders. A lattice-point foam on a sphere (one film per point, domed cells, white Plateau borders,
  two reflected windows) is the prettiest thing I have made in the 2-D-texture-on-3-D register. Reach for it for any
  point set on a sphere and any cell complex that can be a foam.
- **Go deeper by scale**: the same rule at several sizes (n = 25…3125 bubbles with equal grain), arranged on a rising diagonal.
  Watch the silhouette (three bubbles → a famous mouse).
- **Yarn on a surface**: level sets of a function on a solid as constant-pixel-width strands (distance = Δvalue/|∇value|_px),
  pearls on the special level set. Clean and charming. Brighten the body (lighting ≥ 0.74 base) or it goes grey.
- **Dendrograms of finite trees**: the plain radial version (angle = leaf share, radius = digits^0.6) made a rainbow heart.
  Organic "phyllotaxis" branching was lopsided. Trust the tidy layout and let the data make the shape.
- Math habit: compare the offspring distribution with Poisson(1). A finite tree whose leaves are ≈ 1/e of its nodes is probably a critical branching process,
  and that is the honest answer to "why must it terminate".
- Voice: quadriptych title from the Phil.SE question (WHAT COMES NEXT); the tweet as three objects that each learned one thing.
