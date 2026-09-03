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

## Also-rans (ideas 4–6)
- Zarankiewicz drawing of K_{n,m} with the exact minimum of (3,3)-even zero counts by coding
  theory (MO 514851: the code is ker(T_n ⊗ T_m), dim = C(n,2)C(m,2) − (C(n,2)−n+1)(C(m,2)−m+1)) — string art.
- Snake-in-the-box with bounded covering radius on a Gray-code map (MO 514865) — plain.
- Cell-division tissue with a lineage palette and Lewis / Aboav–Weaire laws — too close to
  the Voronoi registers already used.

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
