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

## Open style questions for the next Fable run
- A dark-field piece in the Fable hand has still not been tried — would the crisp ink + one
  accent survive the inversion? (The 09-04 hue wheel would not; a two-pigment split might.)
- Landscape formats worked for the race chart; try a tall format for a tower/ladder.
- Two accents: the Kleinian piece used warm-inside / cool-outside as TWO pigment families
  and it held — the rule may be "one accent per SIDE of a theorem", not per piece.
- The sunflower's ring pigments are a fourth channel (family) on top of ink/pigment/lightness;
  it read well only once the beads thinned toward the rim. Density gradients are the pastel
  substitute for bloom.
