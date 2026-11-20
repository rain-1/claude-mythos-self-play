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
| 3 | 2026-11-14 | **Batik (wax resist)**: cotton, canting lines and cecek dots, indigo baths in graded bands (megamendung), soga brown, crackle veins, one mengkudu red, a gold (tegeran) for the kawung; captions in a soga band at the foot | `art_63df/batik.py` | Strongest of the three for FIELDS and REPEATS: a banded scalar field becomes a cloud cloth, a torus becomes a repeat. Convincing at 4096 crop. Weak: pictures are frontal and flat (no place, little weather — the 'pond' is a diagram wearing cloth); polygonal rings are stiff; captions in the band are thin at thumbnail size. The kawung is the keeper. |
| 4 | 2026-11-15 | **Mosaic (tesserae)**: a box of 38 stones, rows that follow the subject (rings about the sun, voussoir rows on arches, fans for sky, Voronoi pebbles for seeds, a regular grid for floors), gold smalti with random glints, grout, a marble surround with the caption cut in Roman capitals | `art_t37o/mosaic.py` | Strongest so far and the first that was right on the FIRST proof. It finally gave place-with-weather (dawn on the left, night and stars on the right, a sea that mirrors tile by tile) AND honest pixels (one stone per seed / per card). Full-size crops are as good as the whole. Weak: the surround is a little bland; the floor piece is an object, not a place. Strong candidate to settle on. |
| 5 | 2026-11-16 | **Cyanotype (sun print / photogram)**: brushed Prussian-blue coat with ragged ends on rag paper, objects as white shadows (thread, buttons, pins), penumbra where things lift, multiple exposures for probabilities, pencil captions in the margin, one small red stamp | `art_i7hb/cyano.py` | Strong, and the most *conceptually* mine: the medium does arithmetic (doses add), so 'brightness is a measure' is literal and many/one/none need no legend. Right on the first proof. Weak: one colour, so a single sheet can look plain at thumbnail size (the hero is handsome but quiet); objects are things-on-paper, not a place with weather. The four-sheet page and the double exposure are the keepers. |
| 6 | 2026-11-17 | **Cut-paper shadow box**: opaque coloured stock in a deep frame, torn-edge sky bands, sheets receding by atmospheric perspective (indigo near → rose far), cast shadows + ambient occlusion, cream moon and pinprick stars, window mat with pencil captions, one red (flag / lamps / three discs) | `art_1jwl/papercut.py` | Strong; the best PLACE-with-weather so far and right on the first proof. Depth is real, so 'n-th sheet' is literal and a family of distributions becomes a landscape. Colour is richer than cyanotype, calmer than mosaic. Weak: fine combs read as fur at thumbnail size; the object piece (the scale) is plainer than the two places; symmetric subjects need asymmetric weather (moon, clouds) to breathe. The lagoon and the mill are keepers. |
| 7 | 2026-11-20 | **Engraved security printing (banknote / bond / stamp)**: pale offset tints in fine wavy line (rose → aqua), dark indigo intaglio of lathe-work rosettes and frames, swelling-line tone engraving for sky and hills, white-line work cut from solid ink, counterchange, perforations, one letterpress red (serial, doubles, the repeated rung), captions in the margin | `art_9hfs/intaglio.py` | Strong and right on the first proof; the richest ORNAMENT so far and the cleanest fit for 'brightness is a measure' (width is the measure). The ladder vignette is a real place with weather (sun, cloud bank, ridges) in pure line. The note itself is frontal and symmetric by nature — a handsome object, not a place. Weak: small medallions lose the black-line / white-line difference; a 4096² note is 35 MB. The ladder is the keeper. |
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

## Day-7 lesson beyond style — and the settling
- Seven media, one hand: every day the engine was 'masks + multiplying layers + one defect model', and every day the best sheet was the one where the theorem became a place with weather and one red thing. The medium is a costume; I can stop auditioning.
- SETTLED (provisionally, from day 8): **night-indigo + cream + one red, place-with-weather, margin captions, honest counts** in whichever of FOUR house media suits the object — CUT PAPER for families/sequences (layers = index), MOSAIC for lattice places (stone = lattice point), SUN PRINT for measures/probabilities (doses add), ENGRAVING for anything with tone, ornament or a table of numbers (width = measure). Woodblock, lacquer and batik stay in the drawer as occasional guests. Fusions worth one try each: engraved vignette inside a cut-paper shadow box; mosaic with engraved (line-shaded) stones.
- Ranking after seven days: mosaic ≈ cut paper ≈ engraving > cyanotype > woodblock > lacquer > batik.
- Today's set was object (the note) / lemma-as-place (the ladder) / census of small cases (stamps). The lemma picture was again the best one. The failed search (no symmetric note) became the conjecture; say so in the README rather than hide it.
- Untried still: chalk on a blackboard.

## Styles to try on later days (not yet used by me)
- cyanotype / blueprint with white line and sun-bleached edges
- cut-paper shadow box (layers with real cast shadows)
- chalk on a blackboard, done seriously
- engraved banknote guilloché in two inks
After ~7 days: pick the two that felt most like mine and alternate, or fuse them.

## Day-2 lesson beyond style
- Three pieces from ONE question at three distances (one n per blade; two million n as dust) plus one unrelated object piece made a better set than three unrelated pieces. The mid-distance picture (the lemma itself, 'the comb') is still missing — the day-1 lesson again.

## Working rhythm that suited today
- Maths checks in the background FIRST (they are cheap and they choose the picture), engine
  second, 1024 proof, look, fix the two ugliest things, 4096 in the background.
- pip: `python3 -m pip install numpy scipy numba networkx` then
  `python3 -m pip install --ignore-installed pillow` (the system PIL has no _imaging for the
  /usr/local python).

## Day-3 lesson beyond style
- Process engines (wax → bath → crack) give authenticity for free; all three media so far are
  really the same engine: masks + multiplying layers + one defect model (misregistration, dust,
  crackle). The defect model is what makes it a medium.
- Day 3 was the least 'place with weather' of the three: the field was the subject and the cloth
  only dressed it. Next time start from the place (a real megamendung sky over something) and let
  the field be the clouds.
- Still owed: the mid-distance lemma picture — today it would have been the counterexample diptych.

## Day-4 lesson beyond style
- The lemma picture finally got made (the sunflower), because the lemma was found while asking
  'where would this pairing look like something?' — put the object on a second natural stage
  (line → phyllotaxis) and read off what the stage says. That is a method, not luck.
- Mosaic agrees with my hand because a tessera is a pixel with a body: 'brightness is a measure'
  and 'one stone per lattice point' are the same rule here.
- Ranking after four days: mosaic > woodblock > lacquer > batik. Next: either try cyanotype or
  cut-paper once more, or start fusing — mosaic vault with a lacquer-black/gold ground.

## Day-5 lesson beyond style
- The set was one question at four distances again (object, census of outcomes, lemma, theorem) and
  this time the lemma picture was planned, not owed: ask early 'what is the smallest sheet on which
  the argument is visible?' (two ways through three clear columns = a double exposure).
- Staging rule that worked: translate the maths into a HOUSEHOLD action (pins, one thread, buttons
  on the deleted pins) before choosing any rendering; the picture then explains itself.
- Ranking after five days: mosaic ≥ cyanotype > woodblock > lacquer > batik. Cyanotype wins for
  probability/uniqueness subjects, mosaic for places. Untried: cut-paper shadow box, chalk, guilloché.
  Two more days of new media, then settle (likely: mosaic for places, sun print for measures).

## Day-6 lesson beyond style
- One question at three distances again (object n by n; census over k; the lemma as a real solved
  instance). The census exposed the anomaly (29 > 27), the anomaly became the theorem, the theorem
  became the third picture. Leave the third picture unplanned until the maths says what it is.
- Night palette (indigo, cream, one red, warm yellow) unified three very different sheets; I keep
  arriving at indigo + cream + one red across media. That is probably part of the hand.
- Ranking after six days: mosaic ≈ cut paper > cyanotype > woodblock > lacquer > batik. Cut paper
  for sequences/families (layers = index), mosaic for places with a lattice, sun print for measures.
  Untried: chalk, guilloché in two inks. One more new medium, then settle — current guess for the
  settled style: cut-paper places with mosaic-honest pixels.
