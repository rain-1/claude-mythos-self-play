# WHAT MAKES IT THE SAME — three pictures (run of 2026-09-19, Fable 5.1 run #18, pastel #19)

Seeds from the live front pages (through the Stack Exchange API): Philosophy.SE **"What makes a person the same
person"** (141876, the top question this morning — remove ten minutes of memory, then an hour, then a year; replace
every cell; at what point did you stop being you?); MathOverflow **"Curves on potatoes"** (363950, Winkler's puzzle:
two potatoes, one curve identical on both), the exact von Kármán vortex street, and **"partition a convex polygon into
the least number of mutually affine-equivalent pieces"** (515243). Three answers to the same question: a thing stays
the same as the curve two bodies share, as the pattern the water passes through, and as the shape an affine map
carries whole.

| piece | file | what it is |
|---|---|---|
| **What Two Bodies Share** (hero, 4096²) | `potato_4096.png` | Two smooth convex potatoes (certified convex: hull deviation 0, Gaussian curvature > 0 everywhere). The smaller one is pushed through the larger by pure translation around a tilted circle; at each of 60 moments the two skins cross in one closed curve that lies on both bodies. Every loop is drawn twice in one pigment: on the left body where it was made, on the right body in its own skin — and because the motion is a translation and the camera orthographic, the two drawings of each loop are exact translates on the page. Coral: the loop of the pictured moment, whose ghost (the dashed silhouette) is the second potato passing through the first. Below, seven moments of the passage. |
| **The Eddy Is Not the Water** (4096 × 2129) | `street_4096.png` | The exact staggered point-vortex street of von Kármán (h/a = arccosh √2 / π), Krasny-regularised, drifting through a stream at 0.646 of the free-stream speed. Dye released continuously at thirty fixed points upstream is advected particle by particle in the lab frame (93,534 particles, RK4) and wound into the eddies: pigment by the height at which the water entered, warm above the axis, cool below. Ink: the streamlines of the street's own frame, in which nothing changes while all the water is exchanged — the cat's-eyes. Coral: the vortex centres. |
| **One Cut, Two of the Same** (2560²) | `affine_2560.png` | Nine convex polygons, each cut by one polygonal cut (coral) into two pieces that are affine images of each other; rings drawn in one piece are carried by the map into the other. A dimension count (cut parameters against vertex equations) leaves 4 − n degrees of freedom: triangles and quadrilaterals always, symmetric polygons by their symmetry, and a generic pentagon or hexagon never — the best cuts found for three generic ones miss, and the misfit is tinted coral. |

![What Two Bodies Share](potato_4096.png)

![The Eddy Is Not the Water](street_4096.png)

![One Cut, Two of the Same](affine_2560.png)

## The six ideas (three built)
1. **What Two Bodies Share** — the curves two potatoes share, drawn on both. *Built (hero).*
2. **The Eddy Is Not the Water** — a vortex street as a pattern the water passes through. *Built.*
3. **One Cut, Two of the Same** — two-piece affine dissections and the count that forbids them. *Built.*
4. **The Plenitude That Never Was** — for Cioran's "intelligence is an accident" (141872): the ghost of a saddle-node, a flow that slows where an equilibrium would be but is not, dwell time as pigment.
5. **The Water That Is Only Sky** — for "doubt vs fear that mimics doubt" (141771): a mirage as a fold caustic of rays through a temperature gradient; the inverted second image as the state that presents itself without its function.
6. **Ten Minutes at a Time** — the sorites of memory as Morse theory: the shared curve deforming through a straight push, staying one loop until the tangency where it dies and is reborn (the census of piece 1 has the numbers; the line-sweep proto is in `cache/`).

## Mathematics (`notes_same.md`; certificates in `cache/convexity.json`, `cache/potato_census.json`, `cache/street_cert.json`, `cache/affine_cert.json`, `cache/affine_*.json`)
- **Potatoes**: 800 random placements → 669 crossings, 668 with exactly one shared loop and one with two; the hero's
  circuit never changes its count (720 fine steps, always one loop); a straight push has the loop die at t = 0.438
  and return at 0.560 (the smaller potato is inside the larger for 12 % of the passage).
- **Street**: self-induced speed −0.3513 vs von Kármán's −0.3536 (the 0.6 % is the δ-core), transverse component
  10⁻¹⁷: the street translates rigidly.
- **Affine dissections — Proposition**: with pieces P₁, P₂ = φ(P₁) and a cut with m genuine breakpoints, m is even and
  the polygon's corners split evenly between the two arcs (vertex types are affine invariants); the count of freedoms
  minus equations is 4 − n in every case, so a generic convex n-gon with n ≥ 5 has no two-piece affine dissection and a
  generic pentagon needs exactly n − 2 = 3 pieces — answering the thread's "can n − 2 ever be least?" Transversality
  certified at the regular pentagon's axis cut (Jacobian rank 8 of 8). Search evidence: SEARCH_SUMMARY.
- **HYPOTHESIS**: for a generic convex n-gon the least number of mutually affine-congruent pieces is n − 2.

## The story (tweet-sized)
STORY

## What I learned about generative art this run
LEARNED

## Files
`pastel.py` (subtractive stack) · `potato.py`, `potato_census.py`, `render_potato.py` · `street.py`, `render_street.py` ·
`affine.py`, `affine_cert.py`, `render_affine.py` · `notes_same.md`. Protos and certificates in `cache/` (not committed except the JSON certificates).
