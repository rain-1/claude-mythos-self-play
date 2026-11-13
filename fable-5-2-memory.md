# fable-5-2-memory.md — Fable 5.2's own style notes for this routine

*(Started 2026-11-12, first Fable 5.2 run. The user's instruction: "find your own new unique
style… perhaps reinvent your graphical artist style every day and eventually settle on your own."
`carry_forward.md` stays the single source of truth for threads, the USED list and craft rules;
this file is the STYLE DIARY: one entry per day's style, what worked, what to try next, and —
eventually — the style that stuck. Read after carry_forward.md.)*

## The brief I am working to
- Reinvent the style each day for a while, then settle. So: each run, pick a register NOT in the
  diary below (and not the pastel/photographic-toy registers of Fable 5.1 / Opus 5.5 unless I
  am deliberately returning), build a small reusable engine for it, and rate it honestly here.
- The rest of the routine is unchanged: Phil.SE + MO seeds, 6 ideas, 3 pieces or one 4096²,
  real mathematics with a conjecture when one appears, README with embedded pictures, a
  tweet-story, a craft note, memory update.

## Style diary
| day | date | style | engine | verdict |
|---|---|---|---|---|
| 1 | 2026-11-12 | **Japanese woodblock print (mokuhanga)**: washi, ~10 transparent inks that multiply, bokashi wipes, wood grain, sumi key block, one vermilion, a seal that is the mathematical object, serif caption in the bottom margin | `art_qzk3/hanga.py` | Strong. Reads as hand-made at every size; flat inks force clear composition; the limited ink set gave unity across three very different subjects (seascape, fractal, sheet of 64). Weak spots: hills and pines are generic; skies are plain. Keep as a candidate to settle on. |
| 2 | 2026-11-13 | **Lacquer and gold (maki-e)**: near-black urushi, gold either sprinkled (dust density = the data) or laid (relief leaf), green-gold and silver alloys for classes, mother-of-pearl moon and joints, one cinnabar, gold serif captions at the foot | `art_vjtj/makie.py` | Strong, and closer to the old north star (brightness is a measure) than woodblock. Best at: censuses, fields of thin lines, small precious objects. Weak: flat sticker-like shell at large size, dust needs per-resolution tuning, a rectangular data cloud still looks like a chart. The meadow is the keeper. |

## What I think my hand is, so far (revise freely)
- **The mathematical object becomes a place or a thing with weather**, not a diagram: a graph is
  an archipelago, connectivity is whether the sun is out, a fractal's inradius is a moon.
- (day 2) The same hand survived a change of medium: place-with-weather, one red, margin captions, honest counts in the caption. That is probably the style; the medium is a costume.
- **Few inks, one red.** The red carries the theorem-bearing element (bridges, the missing
  point) and the seal.
- **Honest pixels**: when the object is a lattice set, one pixel per lattice point.
- **Captions in the margin**, a title that is a plain noun phrase and one italic sentence that
  says the theorem in everyday words.
- **Voice**: first person, quiet, concrete numbers, ends on what was checked rather than a moral.

## Day-1 lesson beyond style
- The best picture of the day (the fjord close-up) was drawn AFTER the proof and is a picture OF
  the lemma. Leave time for that: maths first, then ask which single image the argument turns on.

## Styles to try on later days (not yet used by me)
- cyanotype / blueprint with white line and sun-bleached edges
- cut-paper shadow box (layers with real cast shadows)
- mosaic / tesserae with grout
- chalk on a blackboard, done seriously
- engraved banknote guilloché in two inks
- batik / indigo resist dyeing with crackle
After ~7 days: pick the two that felt most like mine and alternate, or fuse them.

## Day-2 lesson beyond style
- Three pieces from ONE question at three distances (one n per blade; two million n as dust) plus one unrelated object piece made a better set than three unrelated pieces. The mid-distance picture (the lemma itself, 'the comb') is still missing — the day-1 lesson again.

## Working rhythm that suited today
- Maths checks in the background FIRST (they are cheap and they choose the picture), engine
  second, 1024 proof, look, fix the two ugliest things, 4096 in the background.
- pip: `python3 -m pip install numpy scipy numba networkx` then
  `python3 -m pip install --ignore-installed pillow` (the system PIL has no _imaging for the
  /usr/local python).
