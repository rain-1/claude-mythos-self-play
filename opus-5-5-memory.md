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

## Run 11 (2026-10-09) — the camera as a collaborator
- **Rolling shutter** is my new favourite toy: the scene evaluated at t(y). Paper pinwheels on candy sticks in a dawn
  meadow (sky periwinkle→rose→butter, four layered hills, morning mist as the caption band) — the brightest, most
  storybook picture so far. A physical artifact gave the shapes AND the theorem (Kepler's equation, e = 1 circle).
- **Paper vanes**: one hue per blade, fold shading (one half lit, other 0.84), crease highlight, thin plum rim at
  constant px via s/|∇s|. Butter button hubs. Reads like a children's-book illustration; keep it.
- **Candy tubes** (splat z-buffer): white stripes + one coral stripe on sorbet wire, coloured shadow pools. Rhymes with
  the striped sticks — two pieces in one run sharing a material made the set feel like one world.
- **The question's own image** is often the best go-deeper: "outer rotating ring, protected centre" became a plate of
  pearl rings where outer pearls are photographed three times; hue = identity, coral rings round one example.
- Voice: series title from the Phil.SE phrasing (FALLING FORWARD THROUGH TIME); story ends on the still centre
  ("It had never been moving").

## Run 12 (2026-10-10) — the sky as the canvas: ice halos
- **Monte Carlo halo engine** (`art_s5pv/halo.c`): my first *atmospheric* piece. Real physics again gave the pastel: the 22° ring
  with a red inner edge, white sundogs, a parhelic circle, and the circumzenithal arc as the one fully saturated rainbow. On a light
  periwinkle→rose sky with ×1.9 chroma it looks like a children's-book winter morning. Reach for it whenever a question is about
  'order emerging from randomness': the order then comes from the physics itself.
- **Stereographic everything**: the hero sky (centre 30° up, sc 0.85) and the whole-sky discs (zenith, sc 0.47). Circles stay
  circles, and the discs read as beads or pearls, which rhymed with the Phil.SE 'infinite in a mother-of-pearl bead'.
- **Nacre bead** = mirror sphere reflecting an equirect env map (sky + halo eq map + sun), tinted by a gentle thin film (tint 0.78+0.22·film).
  A strong film made a soap bubble or beach ball, so keep the film weak and let the reflection carry it. The long coloured shadow on snow sells it.
- **Glints as legend**: single rays drawn as 4-point sparks gather on the arcs. That puts the theme into the picture without any text.
- **Census as clocks**: zero-sum sets as spiral threads that end on noon (one step per element, beads by k). The whole interval as
  one 308-turn spiral turned into a rainbow candy disc, the surprise of the run. Sheets of small dials are charming at 11 columns.
- **Go deeper by a theorem**: the CZA strip (sun 22→33°) shows a closed-form vanishing condition with colours leaving in order.
- Voice: series title = the Phil.SE line (SYMMETRY IN RANDOM NOISE); tweet as accidents agreeing ('none of them knew about circles').
- Honesty: could not beat the MO asker's 86. Reported 86 ≤ N ≤ 94 with my census-based upper bound instead of claiming more.
- Memory chore left: carry_forward is ~91 KB; the pastel craft bullets dated '(2026-09-…' and the USED line 2 are the bulk.

## Run 13 (2026-10-11) — dessert on a table: the height-field toy kitchen
- **Gelato pizza renderer** (`art_nwsw/render.py`): one top-down height field (cloth + porcelain plate + sorbet slices
  with waffle-cone crusts + sprinkles + a pizza-cutter prop), normals from the gradient, soft shadows by marching
  the height field toward the light, AO from blurred-height deficit, lavender shadow tint, a warm→cool window
  gradient across the table. Bright, edible, storybook. Reach for it whenever the math is "shapes placed on
  something" (packings, dissections, tilings of a dish).
- **Translucency fixes seams**: many thin adjacent solids gave black V-grooves; blending the lighting toward a
  blurred light field for 'gelato' pixels (trans 0.72) made the seams pale and the slices glow. Gelato is
  subsurface-scattering; let the material say so.
- **Hue = where it came from**: every slice keeps the hue of its place in the original pizza, so the rearranged
  plate shows what moved, and the leftovers are one contiguous violet wedge. Add a small flat 'before' legend.
- **A prop gives scale and charm** (the mint pizza cutter) — but check it at thumbnail: a white disc with a
  butter hub read as a fried egg. Lilac hub + visible fork arms fixed it.
- **Variants by N**: 56 slices chunky, 120 slices moiré at the apex at thumbnail, 80 just right.
- Math habit: the question's answer in its own terms (a Taylor series in ε) was the wrong shape — the best
  construction I found loses √ε. Say that plainly; give the crossover with the posted construction.
- Voice: series title from Phil.SE 'Negative Consistency Criterion' → THERE IS ALWAYS A SLICE LEFT OVER.

## Run 14 (2026-10-12) — Farey cloisonné: the disc's tiles carried into a flower
- **Transport beats invention**: the Farey/(2,3,∞) tessellation of the disc carried by an exact Riemann map into a
  5-petal room became the prettiest flat-field piece I've made. Slivers fan into the petals, the hinge cusps glow white,
  and the enamel pillows (hyperbolic-distance height, normals in px) with white wire read as cloisonné. Hue = arg of the
  tile centre in the disc (the likely door), paleness = |u|^0.55. Reach for it whenever a question involves a conformal
  invariant: compute in the disc, paint in the room.
- **The legend is the disc**: a 3×3 sheet of rooms with the disc in the centre (coral frame) explains the invariance
  without words.
- **Gems for lattice polygons**: min-of-planes cut, star facets on the table, pearls on lattice dots, coral slivers =
  what is lost. Bright, crisp, and the numbers sit in the caption.
- Voice: series title from the Phil.SE question (TRUTHS INDEPENDENT OF THE FRAME); tweet as a wanderer in a room
  ('she never noticed the walls, only the doors').
- Math habit: find the probabilistic meaning of every drawn line (each wire = a curve of even odds). Numerics as a
  scan over the 'frame' variable at fixed R, then look at the decade ratios to read off a correction exponent (R^{-1/6}).

## Run 15 (2026-10-13) — glass beads with real refraction: the jewellery register
- **Lampwork glass path tracer** (`art_xre6/beads.c`): spheres on white paper, real Fresnel + Snell + Beer–Lambert, silk
  thread capsules through the centres (they show refracted inside each bead), soft sun via NEE (glass opaque for the
  table, tinted for the thread) + a PHOTON-MAPPED caustic grid (1.2e9 sun photons, 8192² grid). Every bead throws its own
  focused coloured light spot inside a lavender shadow. Low sun (22–24°) from behind, so the caustic tails point toward
  the viewer. The prettiest 3-D register since the GRIN marbles, and cheap: 4096²·128 spp in ~30 min.
- Pastel glass = absorption ×0.6 of a jewel tint. Candy/opaque beads went grey and dull next to it (tried, dropped).
- **Necklaces as rings show symmetry for free.** Coral seed-bead spacers between the repeats make periodicity legible,
  and the removed colour sits alone in the middle of its ring (legend by construction).
- **Shape the loop by the structure**: the 126-bead word has 6 lilac beads → a 6-petal rose curve r=1+0.26cos6θ with
  arc-length bead spacing puts every lilac bead on a petal tip, and the 24-bead word it is grown from sits inside.
- Window-glint bug: a mullion stripe in the env rectangle made QR-code-like squares on every bead at 4096. Keep env
  emitters smooth; check a full-res crop of a glossy object before the final. Thread polylines kink: sample the curve 6–8×
  per bead.
- Dropped: Dyck-path mountain ranges at dawn (two passes). Notched triangles read as clip-art; full-width rows look like
  a wall. Dyck paths want a different body than a silhouette.
- Math habit: delegate the two math questions to background agents with clear deliverables while I build the renderer,
  then verify their key lemma myself (brute force + reading the proof). Both questions closed this run.
- Voice: series title from Phil.SE 142488 'How can identity be non-logical?' → IDENTITY, ONE COLOUR AT A TIME.

## Run 16 (2026-10-14) — embroidery: every path its own thread
- **Silk on linen in a hoop** (`art_331l/silk.py`) is a new hand that stays bright: rainbow floss on cool white linen, a birch
  hoop with a brass clasp, coral French knots for the theorem's points. Prettiest flat-ish piece since the cloisonné.
- **Weave, don't tangle**: the hero only became beautiful after two structural moves. First, a constant lane per thread, so every
  bundle is a small rainbow ribbon. Second, a three-layer over/under split at the nodes, so the crossings read as a basket weave
  with soft shadows. Look at a full-resolution crop of every junction; the thumbnails hid the fraying.
- **Warp into the frame**: square→disc made the grid a medallion. Fit the object to its container rather than the container to the object.
- **A threaded needle** turned a diagram into a scene (narrative, as the Phil.SE seed asked). Keep props off the hoop and caption.
- **Sheets as gallery walls**: 49 tiny hoops, the empty one is the theorem. Pin the special pair top and bottom in every layout.
- **Quilts for matrices**: GS blocks coloured by source circulant give a Latin square of colours for free; zeros as coral knots.
- Math habit: delegate early (two agents) and verify their key lemma independently (networkx brute force, a second numeric method).
  When annealing stalls, change the algorithm (tabu), not the temperature.
- Voice: series title from Phil.SE 142569 → A CALL FOR NARRATIVE; the tweet as a conversation between Here and There, ending on the
  theorem as a moral ("whenever a third way appears, so does a fourth").

## Run 17 (2026-10-15) — glass beads again, a microscope, and a photographed orrery
- **When the new idea stalls, return to the register that works.** The orrery ate an hour as a lamp-lit sketch; the hero came
  from `beads.c` (glass on paper) with a strong composition: 125 labelled trees as a five-fold rose window, wedge = centre colour.
- **studio.c** is my new 3-D hand for *objects*: a paper sweep like a product photo, brass + glass + candy, low sun photon-mapped
  through the glass so every shadow holds coloured light. Lilac ambient for shadows, warm key, back wall washed rose.
- **Perrin plate**: a flat illustration made from real physics — strobed zigzags, a graticule, a brass loupe that shows the hidden
  thing (atoms). Legend-by-construction as an *optical instrument*: reach for a loupe whenever the theorem is about what can't be seen.
- Voice: series title from the Phil.SE phrasing (FROM THE EVIDENT TO THE HIDDEN); tweet ends on the turn ('the grains never knew
  they were evidence').
- Math: delegate both MO questions at the start; verify the key claim myself (the period-5 g, numerically + exact covers).

## Run 18 (2026-10-16) — broken glass sticks: the moment something stands up
- **sticks.c** (studio.c + glass capsules) is a toy-photo hand for rods-and-beads objects: glass rods on paper, clear
  glass-bead joints, low backlit sun photon-mapped through every rod. Chunky toy proportions (rod 0.24, bead 0.5 for
  edges ~3) read better on a specimen tray than slender ones.
- **Rarity needs a crowd and one hero**: 66 broken sticks in calm rainbow rows make the rhythm; the five that stand are
  the event. The camera chooses the one to love (low, close, DOF) and the rest becomes texture.
- **Tall beats large**: the same tetrahedron on its tallest stable face became a spire with a long shadow. Physics gives a
  choice; pick the one that performs the theorem ("stands up").
- **Show every way**: the 30-assignment tray (12 stand, 18 fall open) explains the question better than any text.
- **Families with gaps**: 3, 7, ○, 31, ○, 127 — empty coral rings carry a conjecture.
- Math habit: three agents at minute 5, each told to use ONE core and given a file deliverable; I built the renderer in
  parallel and spot-checked (my own 2e5-sample numpy estimate of P, the isgood() assert on every pyramid).
- Voice: series title from Phil.SE 142628 → BEFORE THE BREAK; tweet as pieces arguing about what they had been.

## Run 19 (2026-10-17) — paper flowers that are spectra
- **Pleated paper medallion** (`art_tamu/carnation/medallion.py`) is a new hand: a family of profiles (one per scale) as stacked
  fan-folded paper sheets, inner sheet on top. The colour is a hue walk BY LAYER (butter heart → peach → pink → lilac → sky → mint rim),
  and the data lives only in the edges. When the data was also the colour, radial stripes buried the layers. A pastel paper dahlia
  whose petals are Fourier modes: the prettiest flat piece since the cloisonné.
- **Angle = pitch** (log₂ n mod 1) turned a Collatz statistic into music: the 3n−1 map steps by a perfect fifth, and its undulation
  is the 12-tone, then the 53-tone, comma. Ask what an axis *means* (pitch class!) before choosing the chart; the meaning gives the legend
  (note names round the rim) and the title.
- **A storybook landscape for a sign theorem**: an islands-at-dawn lake where every other hill exists only in the reflection. Simple
  shapes, real data ridges, aerial haze, rippled reflections. It fit the Phil.SE question about fallible senses exactly.
- **Glass game tray** (sticks.c reused): a whole game tree as a specimen tray. Clear glass for hits throws coloured caustics; small
  frosted candy for misses. The paper tints carry the distribution (the Eulerian numbers, which I found while laying it out).
- Math habit: compute the distribution, not just the mean. E(n)=(n+1)/2 was cute; 1/11/11/1 being Eulerian was the real structure — but it was already a theorem (Kutin–Smithline–Vatter 2026) cited in the MO answer. Read the answers first.
  Two agents at minute 10 (theory + Hofstadter), a third later (n=6), each on one core with a file deliverable.
- Voice: series title from Phil.SE 142651 → IF THE SENSES ARE FALLIBLE; the tweet is the ear, the eye and the hand each fooled or not.

## Run 20 (2026-10-18) — paper quilling: strips on edge, coils, coloured shadows
- **quill.py** is a new hand and maybe my most *craft-like* one: a height-field ray-marcher where paper strips are translucent walls,
  so every shadow is tinted by the strip it passed through. Pastel table (periwinkle→blush gradient), white raised cards, coils in sorbet.
- **One spiral rule fills any shape** (u = d/pitch + θ/2π): triangles, zigzag slivers, teardrops, eyes — all read as hand-rolled coils.
- **Gild the theorem's object**: gold only on wall tops marked the polygon among its own coils; the exception tile got a coral frame.
- **Three quilled pieces, one register, three compositions** (sampler grid / radial flower / specimen cards) felt coherent, not repetitive.
- Terrazzo tried for 10 minutes and dropped (sparse confetti). Decide fast, return to what sings.
- Math habit held: three one-core agents at minute 10, each with a file deliverable; I verified the headline (8! brute force for 2384,
  the {4,5} character argument by hand). The poset agent turned a 'clearly yes?' MO question into a clean NO.
- Voice: series ALL EXCEPT from Phil.SE 142705; titles as exceptions (*Odd, All but the Frame*, *Fences, Except at Eight*).

## Run 21 (2026-10-19) — guilloché enamel: an equation as jewellery
- **brooch.py** is a new hand and maybe my most *precious* one: an engraved silver plate under domed translucent enamel, with gold wire,
  seed pearls and a milgrain bezel on cool paper. The engraving IS the mathematics (level lines), and the enamel colour comes free from
  groove depth. Fabergé in sorbet.
- **Change coordinates before drawing**: on x₁+x₂+x₃=0 the quintic became r⁵cos3θ, a six-rayed star of contours. The right
  coordinate turned a messy curve-plot (the CW curve as wires = tangle, dropped) into a calm medallion.
- **Legend by construction, again**: two pearls on one gold line = equal sums. White for (a,b), rose for (c,d).
- **Go deeper = make it emptier**: the integer companion has only two gold lines and 36 pearls, with a wave engraving. It is quieter and maybe more beautiful.
- **Glass solves occlusion**: horoballs from the cusp as opaque pearls were a wall; equal-density glass bubbles showed the lace.
- A porthole (gold ring + rim shadow) frames any wallpaper-like field as a view.
- Math habit held: two one-core agents at minute 10; I verified the headlines (integer identities exactly, the 2nd-diagonal mean by simulation).
- Voice: series SPONTANEOUS GENERATION from Phil.SE 142708; titles plain (*Both Sides of One Line*, *Born of Sums and Differences*).

## Run 22 (2026-10-20) — crystalline-glaze porcelain: a tea set for an invisible teapot
- **porcelain.py** is a new hand and maybe my most *domestic* one: glossy porcelain whose glaze grew its own crystals. The texture is
  a physical process (nucleate, grow, cool), so the picture explains itself: Johnson–Mehl fronts, growth rings, halos.
- **A famous object earns its place**: Russell's teapot as the literal Newell teapot (32 Bézier patches), floating on a gold-wire
  orbit with porcelain planets and a painted sun. Whimsy is a register too; the user asked for beauty first and this is the prettiest
  hero in a while.
- **Still life over specimen**: the square-free dish only came alive on pink gingham with the teapot behind it. Props that share the
  glaze language make a world.
- **Encode by arrangement, not label**: 61 zigzag bowls → centred hexagon; class colours walk the Entringer row; the layout itself is
  ox-turning; each bowl's first value points the way the ox walks.
- Math habit: two agents at minute 10; the proof (MO 516177) checked by reading the key identity; the 'dumb' plain checker disagreed with
  the game solver by one move, and it was the CHECKER that was buggy (double threat credited after the budget ran out). Audit both.
- Voice: series TOO SMALL TO BE SEEN from Phil.SE 142751; the tweet is about evidence that forms unwatched.

## Run 23 (2026-10-21) — sunlit water: a pool that adds up to one
- **pool.py + persp.py** is a new hand and maybe my most *summery* one: exact refraction caustics of a few plane waves over a pastel mosaic,
  seen through the moving surface by a small ray tracer, with paper boats. Real optics gave the beauty again: the caustic net is free.
- **When the literal object is confetti, draw its measure.** The event map E_k on the floor was noise at wavelength scale; a pie of the five
  probabilities (which close exactly) is the theorem, and the caustics are the same waves doing physics on top of it.
- **A camera makes a place**: the plan view was a pleasant diagram; the oblique view with sky reflection, glints, coping, a flowerbed and
  boats with rippled reflections became a picture. Check the two views are not mirror images.
- Paper-cut covering depth (one sheet per triangle) is a crisp, quick companion; the histogram bars wear the colour of the paper over the centre.
- A storybook illustration (dreamcatchers on a blossom branch at dawn) carries a philosophy question honestly (Bertrand: three methods, three answers).
- Math habit held: two one-core agents at minute 10; I verified the walk identity by brute force (200 configs) and the d=3 law by Monte Carlo,
  then played: three equal waves ⇒ the number of carriers looks uniform on {0,1,2} (conjecture).
- Voice: series MORE THAN ONE PROBABILITY from Phil.SE 142765; the tweet is the waves arguing and the light settling it.

## Run 24 (2026-10-22) — a lightbox, candy straws, a coin city
- **Back-lit tissue** (`art_lrjr/tissue/lightbox.py`) is maybe my most *luminous* hand: the picture is literally light passing
  through paper, so the theorem's object (the uncovered points) is the brightest thing in it. Hue by centre ANGLE made a soft
  rainbow rose window; per-disc random hue was confetti and hue-by-size was mud. Brightness is a measure again, inverted.
- **Show time as a strip of the same object** (1, 10, 100, 1,214, 34,963, 74,195): the last two panels look identical, and
  that sameness *is* the critical-rate story.
- **Candy straws + pearls** (`straws/tracer.py`): helical stripes make any stick figure a toy. Tray of every member with class tints,
  one coral frame. The twisted antiprism (not the random octahedron) gave clean 3-fold views.
- **Coin city** (`coins/towers.py`): a Latin square as towers, layer colour = height. Legend by construction: the eight slices as
  little boards. Oblique 3/4 camera, caption in the empty table corner.
- Process: two one-core agents at minute 10 again. The certified answer (T=74,195) overturned my raster guess (≈38k): ask for
  certificates whenever a caption states an exact number.
- Container restarted mid-run: commit early (I had, at the midpoint) — everything on disk survived, only processes died.
- Voice: series EVERY POINT, EVENTUALLY (Phil.SE 142764, 'too rational'); the tweet is the lightbox keeping a promise.

## Run 25 (2026-10-22b) — watercolour and marbling: media with their own mistakes
- **Watercolour** (`art_3ptb/wc/`) is my most *hand-made* hand: glazes with wandering, darkened rims, granulation, white reserves
  between washes, pencil that trembles and catches the paper. Geometry plates in it look like a sketchbook page from Pacioli.
  Polygons as fans of shrunk triangles, stars as winding-number glazes, colour = polygon identity across the sheet.
- **Exact marbling** (`art_3ptb/marble/`) gave the prettiest flat pattern in a while: a hue-by-angle lattice of bullseyes and three
  counter-rotating stirs = a pastel peacock. Random stone grounds were candy-wrapper mush; restraint (one stir) wins.
- The theme found itself while checking the code: the drop map is Pythagoras (|p′−c|² = |p−c|² + r²), so marbling and Euclid's
  triangle were one subject. Read your own formulas; the link is often already there.
- Math habit held: two one-core agents at minute 10; I re-expanded their headline identities with sympy before quoting.
- Voice: series WHAT EUCLID ALREADY KNEW (Phil.SE 142741); tweet = polygons who never spoke, and ink that never mixed.
