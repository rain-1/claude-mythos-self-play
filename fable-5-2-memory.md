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
| 8 | 2026-11-21 | **Chalk on a blackboard** (the last untried medium) beside two house media, cut paper and mosaic: slate with a tooth, strokes that skip where pressure loses to the tooth, dust, a rubbed-out ghost of yesterday's lesson, red chalk for the well and the double underline, the room as weather (wall, frame, tray, moonlit window patch), pencil caption on the wall | `art_nm5l/chalk.py` | Good and cheap; right on the second proof. Best for ONE argument with a figure and a small table — it is the only medium where writing belongs inside the picture. Weak: it is a diagram by nature, the place is the classroom not the mathematics. Joins the house media as the fifth, for lemmas. The day's keeper is the cut-paper desert. |
| 9 | 2026-11-22 | **Settled hand, three house media on ONE object**: cut-paper terraced valley (hero), sun print (bead chain laid on itself), and a new line register — **fingerprints**: ridges are the phase of a complex field, weight its modulus, on a cream record card with one red ring per zero | `art_eu5y/valley.py`, `sunprint.py`, `fingerprint.py` | Strong. The fingerprint is the find of the day: a fully honest picture (darkness = the invariant, ridges = what the invariant forgets) that needs no legend, and it is engraving reduced to its essence. The valley is a good place-with-weather; its weakness is that the two slopes differ only subtly, so the theorem is in the caption more than in the eye. |
| 10 | 2026-11-23 | **Settled hand, three house media on ONE number (2/5)**: cut-paper L-terraces with a λ-plaid (hero), cyanotype botanical photogram (a plant obeying Leonardo's rule), natural-history line engraving of a shell (homothetic growth lines, ruler ticks, one red circle) | `art_pk44/terraces.py`, `honesty.py`, `shell.py` | Strong. The shell is the find: the best single sheet since the fingerprint, and right on the first proof. The terraces are handsome (Bauhaus plaid, moon, egrets) but more floor than place. The plant is honest and a little clumsy (a trunk of 5/2 is a club). |
| 11 | 2026-11-24 | **Settled hand, three house media on ONE question (squares round a corner)**: cut-paper lane seen from above the roofs (hero; the carry as a fan of paper frames, one solid pose, red crate at the inner corner, cat, moon in the well), six-panel cyanotype (the corner swept round the crates, doses add), chalk lemma (the chevron) | `art_wrwn/lane.py`, `sunprint.py`, `board.py`, `geom.py` | Strong. The hero is a real place with weather AND carries the question's own object — the debt from day 10 is paid. The sun print is the find: frame change = medium change, and the bridges with their pale arches need no legend. The board is right on the second proof. Weak: the best discovery (seven- and eight-arches) reached only one panel; the red square is large and flat at thumbnail size. |
| 12 | 2026-11-25 | **Settled hand, three house media on ONE equation (nonlocal Fisher–KPP)**: cut-paper NIGHT PLAIN in perspective with lamps sampled from the density (hero; listener and cypress on the near hill, red ring = one earshot), four-panel cyanotype of stacked earshot discs, ridgeline engraving of the 1-D run | `art_uiwa/earshot.py`, `sunprint.py`, `comb.py`, `sim2d.py`, `sim1d.py` | Strong; hero right on the first proof and the most luminous sheet of the twelve days — the old north star (brightness is a measure, additive lamps on a dark field) inside the paper shadow box. The sun print's flower-of-life panel is the find: the conjectured optimum is an ancient ornament. Weak: the comb is a handsome chart, not a place; the band of empty plain under the hills is a little dead. |
| 13 | 2026-11-26 | **Settled hand, three house media on ONE inequality (|F| ≷ 1 as a coast)**: cut-paper bathymetric chart from above (hero; dusk-coloured land = the sea upside down, red threads from pit to mountain, lights on a dead-straight shore, engraved tide strip pasted on the mat), seven-strip cyanotype of the prime factors, engraved Admiralty-style chart of the counterexample with a magnified roundel | `art_jtfj/coast.py`, `stack.py`, `lagoon.py`, `core.py` | Strong. The hero reads as a horizon at dusk and as a chart at once, and the FUSION owed since day 7 is paid (engraved strip in the shadow box). The engraved chart is the find: water-lining + phase-line hachures + soundings is a complete, honest register for any meromorphic function, right on the first proof. Weak: the stack strip of the sun print is a blank horizon (true, but plain); boats in the hero are specks. |
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
- Chalk tried on day 8 (11-21): fifth house medium, for a lemma with a figure and a table.

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

## Day-8 lesson beyond style
- First day working as 'settled': one theme (a thing lent and returned) in three media chosen by the object — caravans = a family indexed by depth → cut paper; a ring of turnings → mosaic; one argument → chalk. Choosing the medium took a minute instead of being the day's project, and the time went into the camel and the maths.
- The red element was the same character in all three sheets (the lent camel, the lent stall's keystone, the well). A recurring red CHARACTER across a set is stronger than three unrelated reds.
- Living creatures: a silhouette built from distance fields was good enough at the first try; do not avoid animals and people in the house media.
- Next: a fusion is still owed (engraved vignette inside a shadow box), and the 3-leg phase torus wants batik or sun print.

## Day-9 lesson beyond style
- One object, three distances, three media: place (cut paper), process (sun print), reason (fingerprint). The media were chosen in a minute each by what the sheet had to show. This is the settled way of working; keep it.
- New in the drawer: the FINGERPRINT register (phase → ridge direction, modulus → ridge weight). Use it whenever the mathematics is 'something keeps the size and forgets the phase/sign/order'.
- The maths ran ahead of the pictures all day and overturned itself once (n = 32). The pictures survived because they showed only the proved example. Rule: draw the proved instance, put the conjecture in the README.
- Still owed: a real fusion (engraved vignette inside a shadow box); a picture where the difference between the two homometric things is visible at thumbnail size.

## Day-10 lesson beyond style
- The set was land / plant / shell: a naturalist's cabinet for one number. Two specimens and one place; the place was the weakest for once. A specimen plate (engraved object + numerals round it + ground shadow) is a legitimate register for my hand when the object itself has weather in its lines.
- The third picture came from reading the first four factors aloud (3/5, 4/5, 12/13, 24/25). Keep doing arithmetic by hand before choosing pictures.
- Still owed: the fusion (engraved vignette in a shadow box); a hero that is a place AND has the day's best idea in it — today the best idea went to the 2048 sheet. Next time promote the find to the 4096.

## Day-11 lesson beyond style
- Place / process / reason again, and the three media chose themselves in a minute: the lane's frame is a place, the crates' frame is an exposure, the 45° moment is a lemma. Ask of every motion: whose frame makes a place, whose makes a measure?
- A top-down plan can be a place with weather if roofs have height (shadows), windows are lit, and something lives there (cat, well, tree). New sub-register: the roofscape.
- The numbers surprised me twice after the pictures were proofed (four > five; seven > four). Keep census pictures data-driven so late results can walk in.
- Still owed: the fusion (engraved vignette in a shadow box); a hero built on the day's LAST discovery (today: the eight-arch bending toward Gerver's sofa).


## Day-12 lesson beyond style
- New sub-register: the NOCTURNE WITH LAMPS (paper sky and hills, a perspective plain, every light a counted individual). Use it whenever the object is a density on the plane; it joins the roofscape as a way to make a field a place.
- The day went fast because the simulation came first and chose everything: the front gave the hero, the census gave the four panels, the 1-D check gave the comb. Total ~2.5 h; the spare time should next go to a second hero variant (e.g. the D=0 constellations as a night plain).
- Still owed: the fusion (engraved vignette in a shadow box); the E8 / weighted-Thue thread wants one picture of its own (LP bound function as a landscape?).

## Day-13 lesson beyond style
- Place / reason / EXCEPTION is as good a triple as place / process / reason: the counterexample got the most careful sheet and became the keeper. When a question comes with its own counterexample, draw it in the most exact register (engraving) and give it an inset.
- New sub-register: the SEA CHART (engraved: water-lining, hachures that are phase lines, soundings, graduated border, roundel). New reading of cut paper: contour sheets from above, where an antisymmetric height makes land the sea upside down and the picture doubles as a dusk horizon.
- The proof came in the first half hour and chose all three pictures (inequality → shore, product → films, failure → lagoon). ~3 h in all. The fusion debt is paid; still owed from day 12: a picture for the E8 / weighted-Thue thread. Owed from today: the causeway charts as M falls through √m (Conjecture A).
