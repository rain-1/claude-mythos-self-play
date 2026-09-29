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

## Open style questions
- Is the sorbet register too pale at thumbnail size? The coast piece needed DK 1.3 to read; try a
  slightly stronger dmax (1.8) and a darker ink for captions next time.
- Try a sorbet DARK-FIELD variant (pastel light on deep indigo) once, as a deliberate contrast.
