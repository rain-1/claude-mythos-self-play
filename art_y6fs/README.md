# Three Pictures of the World — `art_y6fs/` (2026-09-03, Fable 5.1, pastel #3)

Seeded by the live Philosophy.SE question *"Are there any models of reality outside the big
four?"* (141195: the ceramic, the organic, the dramatic, the automatic) and the MathOverflow
front page (509849 on the ratios of 2ⁿ3ᵐ; 514840 on roots of unity without analysis).
Three pieces, one per non-ceramic picture; the ceramic one — the made thing — is the triptych.

| piece | file | picture of the world | theorem in the picture |
|---|---|---|---|
| **The Sunflower of Fifths** (hero, 4096²) | `sunflower_4096.png` | automatic: one rule turning, no maker | the visible spiral families of a Vogel spiral with divergence log₂3 are the convergents 12, 53, 306, 665 — the equal temperaments whose fifth is a record; **theorem**: the nearest family is always a convergent (Lagrange), intermediates only ever the opposed family |
| **Indra's Curve** (2560²) | `kleinian_2560.png` | dramatic: everything is one thing in disguise | quasi-Fuchsian limit set (tr a = 1.91+0.05i, tr b = conj), tr[a,b] = −2 to 1e−16; 1.42 M curve points in Jordan order (gap p99 1.65 px); 62 672 cusp-horoball images as pearls, precisely invariant |
| **The Tree and Its Path** (2560²) | `ust_2560.png` | organic: one organism, every part connected | uniform spanning tree by Wilson; leaves 0.2955 vs Burton–Pemantle 0.2945 (all four degrees within 0.002); LERW branch growth exponent 1.238 vs 5/4 |

Notes with tables and certificates: `notes_sunflower.md` (+ `census_table.md`),
`notes_kleinian.md` (+ `kleinian_2560_cert.json`), `notes_ust.md` (+ `ust_extra.txt`).
Engines: `pastel.py` (Beer–Lambert watercolor stack: paper, pigment box, ink, caption strip),
`sunflower.py`, `kleinian.py`, `ust.py`, `census_extra.py`, `ust_extra.py`.
Protos at 1024 kept: `proto_sun_1024.png`, `proto_ust_1024.png`.

## The other three (built on request — "I want to see the other 3 as well")

| piece | file | seed | what got verified / found |
|---|---|---|---|
| **The Brick Factory** (2560²) | `brickfactory_2560.png` | MO 514851, Turán's brick factory | Zarankiewicz drawing of K(16,16): 3136 crossings counted exactly = Z(16,16). The (3,3)-even relaxation R(n,m) computed exactly via the code's product structure (`even33.py`): **R = Z in every case (3,3)…(3,9), (4,4), (4,5), (4,6), (4,7)** — conjecture R(n,m) = Z(n,m), which is stronger than Zarankiewicz's conjecture since R ≤ cr ≤ Z |
| **The Snake That Sees Every Room** (2560²) | `snake_2560.png` | MO 514865, unanswered | a snake (induced path) with covering radius 1 exists in Q_n for all n ≤ 8 (exhaustive n ≤ 5, local search above); the drawn Q₈ snake has 59 rooms and every other room is next door; conjecture D = 1 for all n |
| **Every Cell Remembers Its Grandmother** (2560²) | `tissue_2560.png` | the "organic" picture, done as lineage | 2579 cells from one by Errera-rule division + partial relaxation; mean sides 5.968, Lewis's law increasing (slope 0.12), Aboav–Weaire a = 1.30; colour = clone at generation 3, shade = generation 6 |

Notes: `notes_brickfactory.md`, `notes_snake.md`, `notes_tissue.md`; certificates
`brickfactory_2560_cert.json`, `even33_table.txt`, `even33_46.txt`, `snake_2560_cert.json`,
`tissue_2560_cert.json`. Engines: `brickfactory.py`, `even33.py`, `snake.py`, `tissue.py`.

## Tweet-sized story
*The sunflower was tuning itself. Every seed a fifth higher than the last, it counted its own
spirals — twelve, then fifty-three, then three hundred and six — and each count was a scale
someone had once built by hand, believing they had invented it.*

## What I learned about generative art this run
- **Threads, not beads.** A point set is a halftone until you draw the relation that makes it a
  structure: the parastichy segments (k → k+m) turned a flat disc of dots into a flower, and
  which m you connect is the theorem.
- **Skip pearls you cannot draw.** A Möbius image of a disc is a disc only if the pole is
  outside it; the exterior-of-a-circle cases were the "beach balls" in the first draft. Every
  wrong-looking blob was a real mathematical object drawn with the wrong primitive.
- **The certificate has to match the scale of the process.** Mean tree-path length between
  points at distance r is set by the box, not by r (heavy tail); the LERW exponent lives in the
  branch-to-radius-r length. Twice a "failed" check was a wrong question.
- Pastel wants density gradients, not flat washes: florets dense at the heart and thinning to
  the rim gave the sunflower a body; a uniform bead density read as an archery target.
- **The "also-rans" were not worse ideas, they were unfinished ones.** Asked to build them,
  the brick factory produced the run's sharpest conjecture, the tissue its prettiest surface,
  and the snake an answer-shaped table. The ranking at idea time measures confidence, not value.
- Growth is a similarity: dilate the whole tissue when cells divide, never let a fixed domain
  do the growing (crowded centre, ballooning rim). Full Lloyd relaxation erases history;
  a tissue keeps its young cells small.
- A hypercube on paper: Q_{2k} as a k-fold nested 4×4 torus grid in Gray order makes every
  edge a short step; the 16×16 Karnaugh map made half the steps into cross-page arcs.
