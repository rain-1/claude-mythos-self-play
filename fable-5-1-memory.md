# fable-5-1-memory.md — Fable 5.1's own style notes for this routine

*(Started 2026-09-02, first Fable 5.1 run, at the user's suggestion. `carry_forward.md` stays
the single source of truth for threads, the USED list and craft rules; this file is only
the STYLE: what a Fable-run piece looks and sounds like, so the next run can continue the
hand rather than reinvent it. Read after carry_forward.md, update when the style moves.)*

## The look (pastel, second register of the series)
- **Paper, not void.** Warm white paper with fiber grain; every layer is pigment density
  (Beer–Lambert); the deepest tone is chosen (dmax ≈ 2.4), black is unreachable.
- **A bright box, one accent.** Pigment box: coral, apricot, lemon, pistachio, mint, aqua,
  cornflower, lavender, orchid, blush. ONE accent per piece (coral so far) for the
  theorem-bearing element (the turned tile, the cone point, the crossing, seed 0, the root).
- **Crisp warm-grey ink, no halos.** Ink #57505b as exp(−(d/w)²) of a distance field; width
  encodes hierarchy; halos ≤ 0.12 or the page muds.
- **Hierarchy as palette.** When the object has levels, each level owns one channel:
  pigment (grandparent), lightness (parent), ink weight (level), accent (special leaf).
  09-03: for a group orbit, side-of-curve → warm/cool, first letter → pigment, word depth →
  darkness; for a tree, arc-length of the Peano curve → hue (patches = subtrees).
- **The relation, not the points.** (09-03) A point set is drawn by the segments the
  theorem names (parastichy threads); ink on the primary relation, pigment on the secondary.
- **Air.** Painter's unfinished edge on all-over patterns; large negative space around single
  objects; the sunflower's rim thins to paper; Indra's curve floats in paper with its pearls.
- **Captions as ink.** Serif title (DejaVu Serif Bold), one italic line (Liberation Serif
  Italic) that states the theorem in plain words; on full-canvas pieces lift the pigment under
  the caption first (`Sheet.caption_strip`), never a pasted box.

## The voice
- Titles are verdicts or questions in plain English: *Which Level Decides*, *The Tide of
  Four Primes*, *The Sunflower of Fifths*, *Indra's Curve*, *The Tree and Its Path*.
- The tweet-story is in the second person or the object's voice, one image, no moral.
- Notes are answer-grade: convention fixed against the poster's own data, exact numbers in
  tables, certificates named, a conjecture stated with what it would take to prove it —
  and when a check fails, first ask whether the CHECK was the wrong question (09-03: twice).
- A theorem that falls out in two lines (nearest family = convergent) gets stated as a
  theorem with its proof, not buried as an observation.

## Working rhythm that suited this hand (keep)
- Verify the port before painting (chirality / overlap / eigenvalue / traces), THEN the proto
  at 1024, THEN look and fix the two ugliest things, THEN the 8192 hero alone in the
  background while the other two pieces are built. 09-03: the hero needed a v2 after seeing
  the full-size crops (elements sub-pixel at 60k seeds → 48k, thicker threads, density
  gradient) — budget one hero re-render (~6 min at 8192² SS).
- Beauty-first runs skip the atlas without guilt; the numbered series survives a pause.
- Write docs while renders run; commit the interim state before the last hour; do the memory
  size chore in the worktree while the last renders finish.

## Run #3 (09-04) — what moved
- **Three modalities as three materials** became the register for anything with an "actual vs
  possible" structure: ink thread (what happened), pigment cloud (what usually happens), thin ink
  loops (what could happen), one coral loop (the theorem). The clock piece used the same grammar:
  pigment for the shrinking arcs, coral for the two that never shrink.
- The hue wheel (phase of the leading term → 10-pigment cycle) held up on paper because the
  pigments are pastel and the density is soft; on a dark field it would have been an HSV wheel.
- Specimen sheets are allowed as companions (nine moons, one pigment each, the origin's cross
  turning coral when swallowed) — the hero stays a single object.
- Titles this run: *The Sum That Came Home*, *Nine Phases of a Zeta*, *Two Hands Cover the Clock*;
  triptych *In Some World, In Every World*. The tweet-story spoke to the object in the second person.

## Open style questions (after run #3)
- A dark-field piece in the Fable hand has still not been tried — would the crisp ink + one
  accent survive the inversion? (The 09-04 hue wheel would not; a two-pigment split might.)
- Landscape formats worked for the race chart; try a tall format for a tower/ladder.
- Two accents: the Kleinian piece used warm-inside / cool-outside as TWO pigment families
  and it held — the rule may be "one accent per SIDE of a theorem", not per piece.
- The sunflower's ring pigments are a fourth channel (family) on top of ink/pigment/lightness;
  it read well only once the beads thinned toward the rim. Density gradients are the pastel
  substitute for bloom.

## Run #4 (09-05) — what moved
- **The translation register**: source and target at one scale on one sheet (the leaf top-left, the page
  bottom-right; the ghost leaf behind the circle), coins tinted by where they *came from*, coral on the
  exact conformal images of the source's straight rows. Beauty came from the target's coin-size gradient
  (crowding at petal tips, big coins in the belly), not from any new pigment.
- Three pieces, one object (the same 9,566/4,235 coins told twice) plus one exact cousin (the Doyle spiral
  where nothing is lost) — the "one object, three lenses" spine held; the hero was the least
  beautiful and the most certified, the circle the most beautiful: next time give the hero the circle's
  air (a ghost behind, more paper around).
- Titles this run: *The Leaf Told on a Page*, *Nothing Lost in the Spiral*, *The Leaf Told in a Circle*;
  triptych *What Survives Translation*. The tweet-story addressed the leaf in the second person.
- The numerical story ran in the notes, not on the sheet: a theorem (Cayley–Hamilton families of
  isospectral strings) and a closed form (nearest missing dragon point) for two 0-answer MO questions,
  both comment-grade.

## Open style questions after run #4
- The hero's page had two coins overflowing its corners; is a translated object allowed to break its
  own frame? (It read as honest at 4096, awkward at 1024.)
- Ghost-behind worked for the circle; would it work for the page (leaf ghost at the page's scale)?
- A dark-field Fable piece is still untried.

## Run #4, second trio (09-05, on request: "do the next 3 as well")
- The also-rans were finished the same day: the random map (flip chain, not CVS), the isospectral
  specimen sheet, the dragon birth-time field. The user also asked for the final pictures INLINE in the
  README — now a standing rule (see carry_forward.md, How to use it, item 4).
- Register notes: a random world in coins needs a finite rim (ideal points deadlock the layout); a
  specimen sheet of pairs puts the shared invariant once between the two portraits; a lattice field at 1 px
  per point with early generations thresholded to paper reads as an object rather than wallpaper.

## Run #5 (09-06) — what moved
- **The theme came from the mathematics, not the other way round**: three unrelated seeds (a fluid
  model, a swarm, a polynomial family) turned out to share one shape — the place where a
  description stops describing — and the triptych title *Where the Description Ends* was found
  after two pieces were built, not before. Let the title arrive late.
- **Streamlines fill an emptiness honestly**: the Hele-Shaw retreat had a big blank interior until
  the exact flow web (images of the disc's radii under the conformal map) went in; the web pinches
  at the cusps and *shows the reason* the model dies (speed ∝ 1/|f′| → ∞). When a region is empty,
  ask what field is defined there.
- **Roads + rungs**: a family of moving zeros drawn as roads (pigment per degree) is a diagram;
  adding the rungs between each zero and its mirror image (the relation the theorem is about)
  made it a body. Same lesson as the sunflower: ink the relation.
- **Coral stayed exclusive**: the roads use nine pigments and never coral, so the double points
  own the accent. When the hierarchy palette would use the accent pigment, drop it from the cycle.
- **rs-scaling bit again**: the 2560 finals came out hairline-thin because widths were scaled by
  the supersample only; every stroke/radius must carry `rs = FINAL/1024·SS`. Put it in the renderer
  header from the first line, before the proto looks good.
- **pkill -f bit a TENTH time** (exit 144, killed my own shell mid-edit, one render lost). The rule
  is absolute: never in a compound command; kill by PID.
- **A negative result can be a piece's footnote, not its grave**: the 2-D spiral chimera was hunted
  for two hours and not caught; the ORIGINAL 1-D chimera (Kuramoto–Battogtokh ring) took ten
  minutes and carries the same idea honestly as a space–time carpet. When the hero animal won't
  come, paint its smaller cousin and table what you learned (`notes_chimera.md`).
- Titles this run: *The Fluid Leaves Before the Model Does* (hero), *Where Two Roads Meet*,
  *The Part That Will Not Agree*; triptych *Where the Description Ends*. The tweet-story spoke to
  the fluid in the second person.

## Run #6 (09-07) — what moved
- **The theme came from a pun the front page handed over**: sleep/death (141468) + Thales' water
  (141355) → *Wake* in three senses (behind a boat, from sleep, for the dead), and each sense got an
  exact water/reversibility model. Let a word carry the triptych when the mathematics is three
  unrelated things.
- **Certificate-as-accent, formalised**: the coral is drawn only where the FIELD has already put the
  loudest amplitude (Kelvin beads on the cusps, calm-heart circles at c_g,min·t). The hero's
  composition IS its theorem: three boats, one angle.
- **Two-pigment families driven by a physical gradient** (∇η direction → transverse/diverging;
  |∇η|/|η| → capillary/gravity) are the pastel substitute for hue wheels: the eye reads two fabrics.
- **A loom register** for reversible dynamics: Kac's XOR closed form as radial warp × spiral weft,
  paper for white balls, pigment-by-experience for black; the greyness chart on a broken axis.
- Titles this run: *The Angle Every Boat Shares* (hero), *The Ring That Only Slept*, *The Rings That
  Never Came Home*; triptych *Wake*. The tweet-story spoke to the boat in the second person.
- The numerical side stayed small on purpose (one exact corollary for MO 514975: gap → 2; the
  Rabaud–Moisy law tan ψ = 1/(2Fr) measured then derived). Beauty-first runs may keep the maths to
  one clean line per piece.

## Open style questions after run #6
- Three scales of one object worked; would FIVE (a whole harbour) still read, or turn to hatching?
- The capillary-gravity wake (ripples ahead) is the untried cousin; the fishing-line piece wants a
  dark-field test — pastel has still not been inverted in this hand.
- The Kac ring's theorem ring (t = N) is one step thick: a magnified time-window inset is the fix.

## Run #7 (09-08) — what moved
- **Two philosophy questions answered by two exact models**: 'Is happiness a trap?' → the mushroom's trapped orbits ARE the happy ones (integrable, forever), and the free ones spend ages imitating them; 'Can freedom contain its own destruction?' → a lattice of cooperators that permits one defector. The MO front page (AI proofs, certifying without publishing) became the *method*, not a subject: certificates in every JSON, hypotheses stated as hypotheses.
- **String art is the pastel register for billiards**: individual chords as threads, envelopes as rings, two families by invariant (cool by ρ) and by closeness to the theorem (warm by ε), coral for the circle the theorem names. Fewer, longer, crisper.
- **A designed demonstration, declared**: the sticky orbits' launch phases were searched (64 tries) for the longest first sojourn; the caption says 'they circle for ages, then fall' and the notes say the phases were chosen. Honest curation beats a random sample that shows nothing.
- **The flat register is allowed for a companion when the object is flat**: the kaleidoscope's four transition colours are the piece; my two attempts to make it 'painterly' by persistence killed it.
- Titles: *Is Happiness a Trap?* (hero), *The Seed It Permits*, *One Defector, Ten Futures*; triptych *What Freedom Permits*. The tweet-story spoke to the orbit in the second person.

## Open style questions after run #7
- The mushroom silhouette is iconic (a T); would a rotated or cropped composition (cap only, mouth at the bottom edge) give more air?
- The dark-field Fable piece is STILL untried (string art on a dark field is the natural test).
- The futures sheet's bottom third was empty until the tile rows were spread; a 12-cell grid wants 3 rows that END near 0.93H.

## Run #8 (09-09) — what moved
- **Three questions, three zeros**: *Does One contemplate Zero?* → the Siegel disk whose rim is the orbit
  of the critical point; *I am not in a state of nothingness, therefore I am* → critical Ising, mean spin
  zero and loops at every scale; *What is completeness?* → the Rauzy tile as the closure of a countable walk.
  The triptych title *Not Nothing* was found after the second piece, as usual.
- **The first Julia set in sixty runs**, and it held in the pastel hand because the pigment went on the
  *invariant curves* (orbits as splats) and the ink on the *rays*, with coral only where the theorem points
  (the critical orbit). The Böttcher-Newton ray tracer is reusable; 64 rays, no branch jumps.
- **Two seas meeting**: a lattice field's window is a compositional choice; a stride search for the window
  where both giant clusters hold ~42 % gave the coastline. Warm/cool by spin, pigment by depth, ink on walls,
  coral at depth two — the nesting law told me depth is rare, so it became the accent.
- **Hierarchy as palette, third time**: the Rauzy tile's digit address is its colour (branch 1 pigment,
  branches 2–3 lightness, ink by level). Ghost translates without ink; the walk thread dropped (gauge streaks).
- **The size-jump rule bit again** (34 rings + size-scaled blur → pale hero; 96 rings + absolute 1.2 px blur →
  hero v2). Write `n_things ∝ FINAL` into the renderer signature next time, not into a re-render.
- The mathematics stayed one clean line per piece, with one exact corollary worth keeping: the nesting rate
  of CLE_κ loops, E[B] = (4π/(κs₀))·tan(πs₀), s₀ = |1 − 4/κ|, makes Ising (κ=3) and percolation (κ=6) share
  s₀ = 1/3, so percolation nests exactly twice as fast — measured 1.97. Pairs with 1/κ + 1/κ′ = 1/2 share s₀
  (3↔6, 16/3↔16/5, 8/3↔8); their nesting rates are in ratio κ′/κ (seed; my first draft said κκ′ = 16, wrong).
- Titles this run: *What Zero Draws* (hero), *Zero Is Not Nothing*, *Three Letters, One Shadow*; triptych
  *Not Nothing*. The tweet-story spoke to the critical point in the second person.

## Open style questions after run #8
- The dark-field Fable piece is STILL untried; the Siegel rays as light on a dark ground is the natural test.
- Can a critical field carry more than two families? (Potts q = 3 would want three seas.)
- The Rauzy piece is calm to the point of stillness — would the 3-D stepped surface behind it give it a body?

## Run #9 (09-10) — what moved
- **Three answers to one question**: *does a memory of the past prove there was a past?* → yes, given the law
  (the snow crystal's rings prove the cloud); only with a law (Kepler's rim proves F = ma was more than a
  definition); no (Gilbreath's column of ones proves nothing about the next row). The triptych title *What the
  Record Proves* came after the second piece, as usual.
- **History as palette** is now the register for grown objects: epoch → pigment, moment → ring, epoch boundary →
  coral. The first snow crystal in sixty-one runs; the model is exact and its symmetry is certified cell for cell.
- **Strobe density**: drawing orbits at equal TIME steps made Kepler's second law the picture's texture. This is
  the pastel form of "brightness is a measure" — dwell time as pigment density.
- **The sweep found the story**: the paper's parameters gave only ferns; β = 2 gave both plates and ferns from the
  vapour density alone, so the six-layer cloud could be written with one knob.
- Titles: *The Snow Remembers the Cloud* (hero), *What the Definition Predicts*, *The Triangle That Begins With
  One*; triptych *What the Record Proves*. The tweet-story spoke to the crystal in the second person.
- Mathematics: one clean mechanism (the n-th difference of primes is a Nyquist band-pass of the gaps; Gaussian
  law predicts the zero counts within 5 %) and two conjectures stated as conjectures for a live 3-point MO question.

## Open style questions after run #9
- The dark-field Fable piece is STILL untried; the strobe beads as light on a dark ground is now the best candidate.
- A Nakaya specimen sheet (ρ × β) would be the snow vein's companion; does the sheet register survive 25 crystals?
- The Gilbreath piece is calm and mosaic-like; would a window at j ~ 10⁵ (deeper crust, taller skyline) have more body
  without losing the column of ones?

## Run #10 (09-11) — what moved
- **One theorem, three dimensions**: the question *Could our universe be a neuron?* was answered by a convex hull —
  its facets are the knots of a 2-D web (a nerve cell to the eye), its edges the branches of a 1-D merger tree (a
  dendrite), and the poster's synapse, a black hole, became a pure lookup through exact geodesics. The triptych title
  was the question itself, as in run #7; the hero carried it too.
- **Draw the 1-skeleton**: facets alone were a halftone; the hull's edges made the web. The pastel web wants voids as
  paper, filaments as pigment, knots as halos, and one coral knot with the circle of what it swallowed.
- **Momentum as pigment, log time for trees**: the shock tree only became a tree on a geometric time ladder, and its
  colour is a conservation law (mean velocity of what each lump ate) mixing at every merger. Tall format 2560×4096
  worked for the tree — the first tall Fable piece.
- **A lookup that invents nothing** was the most beautiful piece of the run (the lens: Liouville, no gain, one minute
  of compute). The Fable hand can borrow a whole earlier picture as a texture and re-see it through a law.
- Titles: *Could the Universe Be a Neuron?* (hero), *The Tree of Shocks*, *Seen Through the Synapse*. The tweet-story
  spoke to the dust in the second person.
- Mathematics: certificates (Bozza's strong-deflection constant to five digits, Kida's exponent, momentum on the hull
  edge) and one new census with a hypothesis (the merger mass-ratio law drifts with the cutoff; conjectured stationary
  and non-uniform for scale-free spectra).

## Open style questions after run #10
- The dark-field Fable piece is STILL untried; the lens rings as light on a dark ground, or the web's knots as stars,
  are now the two best candidates.
- The tree's bottom quarter is hatching (free-flight stripes); would a linear-time companion with straight branches
  and a magnified root inset read better?
- Halos: capped √mass discs read as galaxy-cluster glows at 4096 but as confetti at 2048 — size the cap by FINAL.
