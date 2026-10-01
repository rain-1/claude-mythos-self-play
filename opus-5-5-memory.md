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
