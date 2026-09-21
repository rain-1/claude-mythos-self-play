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

## Run #11 (09-12) — what moved
- **A word carried the triptych again** (*Keep*: to keep going, to keep in, to keep up), as *Wake* did in run #6:
  the minimum conditions for life (Phil.SE 141591) → a garden of Lenia creatures; the cheapest way to keep Brownian
  motion in a ball (MO 511767) → a space–time river; how to be a good clown (141633, "the most important thing is the
  nose") → a siteswap sheet with one coral nose per juggler.
- **Cloud + a few ink paths + coral law** is the register for a stochastic process: two thread versions of the keeper
  (disc, 1-D) were fuzz; the picture arrived when the *distribution* became the pigment (3,000 paths sampled at equal
  time steps, tinted by the FORCE at each point) and eight actual paths became the ink. "Force as palette" joins
  "history as palette" and "momentum as pigment".
- **A garden of motions**: the first CA-creature piece of the series. Straight movers alone are pick-up sticks; the
  sheet came alive with a bending river (Urium), drifting rings (Synptera), a wander that ends (Kronium) and rosettes
  (spinners). Each species is its own world (its own rule) composited by adding absorbance — layers cost nothing on paper.
- **The specimen sheet stayed a diagram** (the clown) and that is allowed for the light companion; beads at equal time
  steps + one common vertical scale made it honest, the nose made it a joke that works once per sheet.
- Titles: *What Counts as Alive* (hero), *The Cheapest Way to Stay* (tall 2560×4096), *How to Be a Good Clown*;
  triptych *Keep*. The tweet-story spoke to the creature in the second person.
- Mathematics: the Hopf–Cole/Doob answer to the p = 2 case of MO 511767 with cost certificates (4.763 ± 0.069 vs
  4.6932; disc 8.208 vs 8.2035), a PROPOSITION that the L²-optimal keeper's peak force has an infinite mean (Bessel-3
  tail, measured f·P flat), a stated conjecture for the L^∞ keeper (band / bang–bang), BEGW's (b+1)^n − b^n verified
  15/15, Orbium's speed ∝ R (0.0473 R at R = 13, 26, 52).

## Open style questions after run #11
- The dark-field Fable piece is STILL untried; Lenia creatures as light on a dark ground would be the most natural test
  of all so far (Chan's own renders are dark-field).
- The keeper river is calm; would a *landscape* version with time across and many short horizons stacked (T = 0.5, 1, 2,
  4) show the deadline flare as a family?
- The garden's coral rings sit on torus seams sometimes; a windowed (non-periodic) world with a painter's fade would
  put every ending inside the frame.

## Run #12 (09-13) — what moved
- **One question, three locations of the pattern**: Phil.SE 141658 (*is patterned-ness in the system or in the
  observation scale?*) was answered three times — in the crowd (Bohmian two-slit paths: each path jerky, the
  ensemble fringed), in the law (the strange eigenmode of a chaotic stirring: two inks, one shape), in the
  distance (a stealthy hyperuniform pattern: disorder up close, paper-flat from afar). Triptych title *Where the
  Pattern Lives*; each piece is titled *The Pattern Is in the …* — the first run with a parallel-titled trio.
- **Use the theorem as the integrator**: the RK4 hero lost one of 8,000 paths at a node (order broken, a path
  flung 2,400 units); the 1-D no-crossing + equivariance theorem makes every path the u-quantile of |ψ|², exact
  and 50× faster (`bohm.quantile_paths`). When a picture's object has a conservation law, draw the law, not the ODE.
- **Square-root time** for a fan that is linear in the far field: rays became parabolas, the near field got the
  lower half, the braiding the upper — the second non-linear axis in the series (log time for trees, 09-11).
- **Speed as pigment** on a two-family cloud (cool/warm by slit, second pigment by lateral speed) gave a smooth
  hue gradient from axis to flank; "force as palette" (09-12) and "speed as palette" are now both in the box.
- **A protocol search is a composition tool**: a single sine-flow period has islands; a block of three random
  phases repeated is periodic, globally chaotic, and 11 of 24 such protocols have a real positive leading
  eigenvalue (a stationary pattern). Pick the protocol by its spectrum, then by its beauty.
- **A ramp of observation scale across the sheet** (Gaussian smoothing width growing left → right, constant
  contrast gain, both bands the same) is the pastel form of "seen from far": it turned a certificate (number
  variance) into a picture without a chart.
- Titles: *The Pattern Is in the Crowd* (hero), *The Pattern Is in the Law*, *The Pattern Is in the Distance*.
  The tweet-story spoke to the particle in the second person.

## Open style questions after run #12
- The dark-field Fable piece is STILL untried (13 runs): Bohmian paths as light on a dark ground would be the
  natural test — the fringes are literally light.
- Would the two-slit hero take a third slit, or unequal slit weights (which break the no-crossing axis — coral
  would have to go)? Asymmetry might give the fan a lean.
- The far piece is two strips — a diagram register; could the ramp of scale be RADIAL (a disc: sharp centre,
  smooth rim) so one pattern makes one object?

## Run #13 (09-14) — what moved
- **Three appearances that live in the relation**: *why are we seduced by appearances?* (141691) and *is a threshold
  in the object or in the relational structure of the percept?* (141595) became a contour the eye adds between coral
  pac-men, a lattice of cells that neither coin layer possesses, and a sequence that is the powers of two for exactly
  five steps. Triptych title *Taken In* — the first title that is a pun on perceiving/being deceived; it arrived
  before the pieces this time, from the questions themselves.
- **Cloud = the all-pairs product, fans = the source marginal, ink = the ridge**: the completion-field register is
  "cloud + a few ink paths + coral law" (09-12) again, but the cloud is now a *product* of two fields and the fans are
  a second, warmer material for "where the eye looks and finds nothing". Two pigments by contour orientation
  (aqua horizontal, lavender vertical) stayed subtle; apricot for possibility was the addition that made air.
- **The relation as pigment** (moiré): tinting each coin by its offset to the other layer is the exact pastel form
  of "the pattern is in neither layer"; the rigid-twist version with an ink Wigner–Seitz web was a diagram, the radial
  twist a rosette. Subtractive pastel has no moiré at all until one layer occludes the other — a physical fact the
  hand had never met.
- **A mandala is allowed** when the object IS a mandala (Moser's circle): cells tinted by side count, pooled toward the
  walls, exact count by Euler in the caption, the seduction (1, 2, 4, 8, 16, 31) as a strip with the breach in coral.
- Titles: *The Contour That Isn't There* (hero), *The Lattice in Neither Layer*, *What Looks Like Powers of Two*;
  triptych *Taken In*. The tweet-story spoke to the contour in the second person.
- Mathematics, both answer-grade for 0/1-answer MO questions: the tripod reformulation of MO 497434 (n = 4m,
  exhaustive search, Petersen-with-triangles example at n = 16, triangle-free conjecture), and the residue-class
  explanation of MO 515202's "growing factor" (mod 6 explains 98 % of it; mod 720720·17·19·23 all of it).

- **Second trio on request** (as in run #4): the Fraser cords, the coin stereogram and the number faces were finished in forty minutes on the warm stack; the faces sheet is the light companion register again (a specimen sheet, one coral accent for primes), the stereogram is the first piece in the series whose object is invisible in the README by construction.

## Open style questions after run #13
- The dark-field Fable piece is STILL untried (14 runs); illusory contours as light would be the most literal test yet.
- The moiré rosette is calm and even; would a *composition* (two rosettes, or one rosette with a torn edge) hold more?
- The completion hero's strays are decorative; an Ehrenstein ring (line ends → illusory disc) would give the eye a second
  kind of nothing to complete.

## Run #14 (09-15) — what moved
- **The philosophy page was about saying** (*why is lying wrong*, *when do we stop stating the truth*, the Barber,
  *is meaning beyond words*), and the mathematics of saying is discrepancy theory — a territory the series had never
  entered: a yes/no sequence whose every ledger balances (Erdős), the same vectors told in every order (Steinitz), and a
  number told as a tree (Matula). Triptych title *What Can Be Said*; found after the first piece, from the questions.
- **A computed certificate can be the hero's object**: the length-1160 discrepancy-2 sequence is Konev–Lisitsa's record,
  refound by SAT in 78 s (`erdos_sat.py`), verified over every ledger, and then *looked at*: the rectangular loom was a fan of
  divisor rays, the polar rose a shell with a white crescent of zero cells — the structure the solver was forced into.
  The prettier layout was also the more revealing one.
- **Families that drift with depth** (warm lemon→orchid, cool lavender→mint, reversed so rim and heart both contrast) are
  the pastel form of a hue wheel for a signed, two-valued field; the plain warm/cool version was a pale tartan.
- **Glazes for a line drawing**: roses of circles as disc unions at 0.14 made the flower of orderings a body; the balanced
  knot lives in an inset with the coral √5/2 circle (Banaszczyk), the first piece whose accent is a *bound*.
- **The garden register** (from run #11) took the Matula trees: blossom clusters by depth, tapered branches, grass, coral
  bamboo stalks for 1, 2, 3, 5, 11, 31, 127 — a specimen sheet that reads as a garden, not a grid.
- Titles: *The Longest Honest Answer* (hero), *The Meaning of a Number Is a Tree*, *The Order You Tell It In*. The tweet-story
  spoke to the answerer in the second person.
- Mathematics: one hypothesis with numbers (near the wall, discrepancy-2 sequences are near-multiplicative: defect 0.126 at
  1160 vs 0.44–0.69 for shorter solutions; χ₃ agreement 0.81) and one clean lemma (interleaved angle blocks give a rose of
  m circles through the origin).

## Open style questions after run #14
- The dark-field Fable piece is STILL untried (15 runs); the ledger rose as light (zero cells dark, ±2 bright) is now a
  strong candidate — the crescent would become a shadow.
- The rose of orderings is airy; would many polygons (a meadow of small roses) or a single rose with all m up to 96 hold more?
- The garden's trees are mostly Y-shapes because most numbers have two or three prime factors; a sheet of primes only
  (each the previous tree on a stem) would show the recursion better.

## Run #15 (09-16) — what moved
- **The philosophy page asked whether the end of one universe can begin another**, and the MO page was on Morgan–Tian's
  finite-extinction chapter: the answer was Ricci flow with surgery — a three-sphere whose neck pinches, is cut, and becomes
  two worlds that each round off and die at a point. Never touched in 71 runs. The sky at last scattering (the plasma's end,
  light's beginning) and a paint film whose every crack ends on an older one made the trio. Triptych title = the hero's title.
- **Glass as a register**: every moment of a flow drawn as an x-ray of a solid (chord length = density), stacked at equal
  time steps — dwell as tone, like the strobe register but for a shape rather than a point. A monotone hue walk through
  time is the pastel form of a time axis; two families head-on greyed the heart.
- **A film strip of moments** under the superposition is the new companion device (nine small glass objects with their
  times); it does the explaining so the hero can stay one object.
- **The sky register**: a Mollweide ellipse is speckle at any size; the picture lives in a magnified window whose footprint
  is drawn on the ellipse, with the certificate (the acoustic scale) inside the window.
- **Craquelure**: the first lattice-fracture piece; two convincing wrong pictures before the right one (unconverged
  relaxation, broken Newton III). Cells tinted by the age of their walls, ink by crack age.
- Titles: *Where One World Becomes Two* (hero), *The Last Light*, *Every Crack Ends on an Older One*. The tweet-story
  spoke to the world with a waist in the second person.
- Mathematics: the S³ warping equation is linear in ψ² (u_t = u_ss − 2 in arclength gauge) — the observation that made the
  solver; neck law measured toward −2 with the theorem's logarithmic slowness; children round to 3 %; a pinch threshold for
  the dumbbell family; a stated pinch-time hypothesis (T ≈ ψ₀²/2, measured ~2×).

## Open style questions after run #15
- The dark-field Fable piece is STILL untried (16 runs); the glass x-ray as LIGHT on a dark ground (the flow's dwell as
  luminosity) is now the strongest candidate of all — it IS an x-ray.
- Would the hero take a tall format with time going down (each moment a glass vase, overlapping) instead of the superposition?
- The craquelure cracks are zigzag hairlines; a smoothed crack path (bond midpoints) and a drying front for hierarchy would
  make it a ge-ware glaze.

## Run #16 (09-17) — what moved
- **The philosophy page's top question was about Ramanujan and the forgotten** (141788), and the MO page carried both
  Ramanujan's 1/π series and Gauss's unpublished ellipse map: the triptych *What We Inherit and Whom We Forget* was the
  question's own title. The mathematics of inheritance is genealogy — the first population-genetics piece in 73 runs
  (Galton–Watson's own 1875 question, surnames dying), as a Wright–Fisher forest.
- **A layout theorem instead of a layout algorithm**: children sorted under their parents ⇒ planar, and every family a
  contiguous block. Pigment dealt at random per founder (nine pigments + own strength), sepia ink for the present's family
  tree, coral for the root and the last forgetting. Two-sided log time.
- **Sunburst register** for a modular function: log-radial warp of the disc (one ring per decade of 1 − |w|), argument →
  nine-pigment cycle, tone by a bell in log|R|, phase-aliasing guard, hairlines at |R| = φ^{k/2}. The first modular-function
  disc since 07-28, and it held in pastel because the centre is paper.
- **The light companion as a family sheet**: five ellipses from round to needle with the pulled-back polar net, pigment by
  |w|, tone by harmonic measure; the tips fade to paper as the certificate says they must. A diagram register, allowed.
- Titles: *The Names That Reach Us* (hero), *A Fraction of a Fraction*, *What the Circle Cannot See*. The tweet-story spoke
  to a forgotten name in the second person.
- Mathematics: Tavaré's lineage count matched to 1 % over 300 runs; fixation 1,975 vs 1,998; the two-name era is 41 % of a
  run; the winding-number certificate for Gauss's map; the crowding table (rim share ~ e^{−πa/2b} vs area share ~ (b/a)³).

## Open style questions after run #16
- The dark-field Fable piece is STILL untried (17 runs); the sunburst as light (paper → black, pigments → glow) is the most
  natural test yet — the rim flames are already luminous in structure.
- The hero's bottom third is one flat pigment with a sepia tree; would tinting the winner's block by *descendant count*
  (fate as palette) give it a body without breaking "one name = one pigment"?
- The ellipse sheet has too much paper between rows; a single needle ellipse at full width with a magnified tip inset may
  say the same thing with more presence.

## Run #16, second trio (09-17, on request: "please do the next 3")
- The three also-rans were built in ~2 hours on the warm stack: a partition drawer-sheet, a prime-gap knot loom
  (tall format), and a complete census field of convex polyominoes with an inset of the exceptions. All three are
  specimen-sheet register — allowed for companions built the same afternoon — and each carried an answer-grade
  number for its MO question (bound verified for all x ≤ 10⁹; seven convex polyominoes whose congruent halves must
  be non-convex, the first of their kind).
- The user's reaction to the first trio was "gorgeous. I loved it." — keep the hand: names dealt as pigments,
  sunburst warp, tips fading to paper.

## Run #17 (09-18) — what moved
- **The philosophy page's top question was Frege's sense and reference**, whose own example is Hesperus and Phosphorus:
  the triptych *One Planet, Two Names* took the example literally — Venus around the Earth for eight years with the stars
  held still (the pentagram of Venus, the first ephemeris piece in 74 runs), tinted by which star the eye names it (warm
  east of the Sun at dusk, cool west at dawn, paper in the glare) over one ink path (the reference). Skyfield + DE421.
- **The strobe register found a physical gradient again**: geocentric speed varies 13× between the conjunctions, so beads
  at equal time steps make the inner loops deep and the outer arcs faint with no tone map at all; the phases of Venus
  (a disc of its apparent size at every day, lit as the telescope sees it) laid along the path gave the ribbons a
  crescent-fringed, Sun-facing edge. Ptolemy's epicycle drawn honestly (the Sun→Venus radius every 12 h) never enters
  the central pentagon — a void as certificate.
- **A wrong interpolation is invisible in a proto**: the Weyl fractional derivative of Ξ (the natural flow through the
  ξ^(k) of MO 515310) has algebraic tails t^{−s−1} for non-integer s and only two real zeros at s = ½; the picture would
  have been a comb of lies. The de Bruijn–Newman heat flow (entire, even multiplier) is the honest flow and the more
  famous object (Λ ≥ 0 Rodgers–Tao, Λ ≤ 0.2 Polymath). Ξ past t ≈ 50 in double precision needs the contour 0 → iα →
  iα + ∞ with α = π/4 − ε: the vertical piece is purely imaginary and drops out, the horizontal one carries e^{−αt}
  analytically (and must be STORED with that decay divided out — float32 underflowed at t ≈ 150 and painted a black slab).
- **A field beats a thread drawing for a flow of zeros**: the zero tracks alone were a ruled sheet; |H_λ|/envelope as
  tone, sign as warm/cool families drifting with height, zeros as paper threads, coral buds at the collisions and the
  dimple beyond each bud (the zero that is no longer there) made a textile that evens out to the right. The "future pulls
  the present" question (141809) is the picture's reading: λ = 0 is the first moment every zero is real.
- **The companion is the hero's whole family**: five geocentric rosettes on one sheet (√-radius), the theorem an
  identity of vectors (geocentric = heliocentric + the Sun's circle), the heart of the sheet being the previous piece.
- Titles: *Hesperus Is Phosphorus* (hero), *Barely True*, *The Circle Every Wanderer Carries*; triptych *One Planet, Two
  Names*. The tweet-story spoke to the planet in the second person.
- Mathematics: transit times to the minute (2004-06-08 08:19, 2012-06-06 01:29 UT), the pentagram's drift −2.407°/8 y
  (one turn in 1196 y), the flow law dt_j/dλ = 2Σ 1/(t_j − t_k) to 1.8 %, 42 backward collisions below 260 with the
  isolated-pair law λ_c = −δ₀²/8 holding to 10–15 % for the tightest pairs and a stated DELAY HYPOTHESIS
  (relative delay ≈ 0.69 (δ₀/s)²).

## Open style questions after run #17
- The dark-field Fable piece is STILL untried (18 runs); the Venus rose as light (the glare a real glow, the crescents
  luminous) is now the most literal candidate of all.
- The five-planet sheet's Mars band is a solid lavender disc at thirty years; would fifteen years (an unfinished crown
  for Saturn) or a per-planet time window read better?
- The heat textile is calm; a λ-axis warped to give the collisions room (signed square root) might carry more drama.

## Run #18 (09-19) — what moved
- **The philosophy page's top question was personal identity** (141876: memories removed ten minutes at a time, every cell replaced), and the
  hot MO page carried Winkler's potato puzzle: the triptych *What Makes It the Same* answered three ways — the curve two bodies share, the
  pattern the water passes through, the shape an affine map carries whole. The title was there before the pieces this time (a first).
- **The same mark twice**: the hero's grammar is repetition across bodies — every loop drawn on the body where it was made AND on the other
  body in its own skin, one pigment per moment, so identity is checked by the eye rather than asserted by the caption. Pure translation
  sweeps keep the two drawings congruent on the page. First 3-D shaded bodies in the Fable hand (ray-cast pastel, grazing light).
- **A fluid piece with no field**: the street is threads only (dye streaklines) plus the moving frame's streamlines as ink; the paper does
  the rest. The 4096 candy lesson: keep the proto's counts at the size jump.
- **The mathematics was a proposition with a proof this time** (vertex types are affine invariants ⇒ m even, corners split evenly ⇒
  4 − n), certified by a Jacobian rank, and it answers an open question in the thread; the search's degenerate 'solutions' were caught by
  the same rank. Stated the k-piece hypothesis (n − 2 is optimal generically).
- Titles: *What Two Bodies Share* (hero), *The Eddy Is Not the Water*, *One Cut, Two of the Same*. The tweet-story spoke to the reader
  as the body in the second person, and let the eddy finish the sentence.

## Run #18, second batch (09-19, on request: pieces 4 and 5 of the six)
- *Ten Minutes at a Time* took the hero's engine with one body and a straight push: the families warm (entry) and cool (exit),
  the two tangencies as coral points with a soft glow, both ghosts dashed, nine frames. The visible face carries the death; the
  rebirth is on the far side and lives in the strip — the air on the left is the 'far side' the caption names.
- *The Water That Is Only Sky*: the first optics piece in the Fable hand — a side-view ray fan tinted by fate (warm direct, cool
  turned, sepia absorbed), the fold as one ink envelope, a hot-ground band, and a tall inset of what the eye sees with the coral
  fold line where the erect and inverted images join. The inset's pile-up of bars at the fold is the caustic's brightness for free.

## Open style questions after run #18
- The dark-field Fable piece is STILL untried (19 runs); the potatoes as glass with the loops as light is now the most natural test
  (the bodies are already ray-cast: swap paper for black and pigment for glow).
- The hero's page is a pair of specimens with air above and below; a third body (three potatoes, pairwise curves) would fill it but the
  theorem is about two — is the air the honest choice?
- The street reads at 4096 × 2129; would a tall stack of three streets at h/a below, at and above the stable ratio (the pattern dying)
  carry more than one street? 

## Run #19 (09-20) — what moved
- **The medium as the object**: folded tissue paper IS an absorbance stack, so the pastel engine rendered
  the physics without pretending — the first piece where the paper's own behaviour was the theorem's
  illustration. Keep looking for objects that are natively subtractive (stained glass, layered vellum,
  overprinted screens).
- **A glyph globe is a new register**: tile a sphere (or any parameter surface) with the very objects it
  parametrises; pigment by an invariant, ink for the loci, coral for what random throws do. Candidates:
  quadrilaterals, conics, pentagons, knots by crossing number.
- **String art from arithmetic**: chord families defined by an algebraic turn (π/π̄) envelope circles
  exactly — the certificate and the beauty are the same object; look for other groups acting on point
  sets (units of real-quadratic fields on hyperbolas, Eisenstein turns).
- Titles this run: *Folded Into Itself*, *Every Triangle on One Globe*, *The Circle a Lattice Can Draw*;
  triptych *The Same Wax*. The tweet-story spoke to the questioner in the second person, one image per
  piece.
- Working rhythm held (verify → 1024 proto → fix two ugliest things → hero alone in the background), but
  TWO heroes were lost: one to a channel-mixing blur (grey), one to OOM beside a 5120² render. Next run:
  crop-check the proto's saturation against the texture, and never start a second render while the
  hero is in its wash phase.

## Open style questions after run #19
- The dark-field Fable piece is STILL untried (20 runs). The submarine comb is now the easiest test: the
  threads are already a density field, so swapping paper for black and pigment for glow would take an hour.
- Three of this hand's last five heroes are fans of lines radiating from somewhere. That is starting to be
  a signature rather than a coincidence — is it the hand, or am I reaching for the same composition?

## Run #20 (09-21) — what moved
- **Plot the inferred quantity, not the raw one.** The best move of the run cost one line: `x` against `t`
  is a pencil of straight lines and a dull picture; `x/t` against `log t` is the same object combing itself
  into integer strata, and the coordinate change is the act of inference made visible. Look for this wherever
  a family of objects converges to something an observer would estimate: running means, empirical
  frequencies, posterior modes, orbit averages.
- **Colour the identity, the geometry carries the fate.** Keying hue to *when* a thread dies gave a left-right
  gradient; keying it to *which* stratum it belongs to gave a comb of coloured bands from the same data. The
  thing the viewer should be able to name goes in the pigment.
- **Let the accent be the line.** The Wythoff piece drew the two golden rays in ink *and* put coral beads on
  them — redundant, and the ink deadened the coral. Dropping the ink and lifting the pigment under the beads
  made the beads themselves read as the two rays. One accent, doing one job, with the sheet cleared for it.
- **A certificate in the caption beats a certificate in an inset.** A 13×13 Grundy table looked charming and
  ate a quarter of the canvas; `the first twelve: (1,2) (3,5) (4,7) …` in mono under the caption says the
  same and leaves the board whole.
- **Honesty is a compositional element too.** This run's conjecture only holds over the range where the
  measurement converges, and saying exactly where that range ends — with the table that shows the windows
  still moving — made the notes better than a clean claim would have. Run the convergence control before
  stating an exponent.
- Titles this run: *Already on the List*, *Every Square Already Knows*, *Where You Have Not Looked*; triptych
  *Only the Address Is Missing*. The tweet-story was in the second person, one image, no moral — and for the
  first time it ended on the object rather than the observer.
- Rhythm note: a piece was **abandoned on purpose** (Pinchuk's map) after 25 minutes, when the target plane
  turned out to be 2.5 units wide and 60 tall. The verified fact it produced went into the notes as an
  also-ran and the time went into a third piece that worked. Budget an abandonment per run; it is cheaper
  than a mediocre third panel.
