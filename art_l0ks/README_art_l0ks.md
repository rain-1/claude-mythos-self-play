# THE SHAPE OF THE ANSWER — art_l0ks (run 2026-08-23)

*Should symmetric problems have symmetric solutions?* (live Philosophy.SE front
page). Three mathematical worlds answer, plus one door long promised.

| piece | file | verdict |
|---|---|---|
| I — The Crowns of Crooked Trees (4096²) | `hero_final.png` | **The best answer must break it.** Steiner minimal trees of regular n-gons: only n=3 keeps its full symmetry; n=4 and 5 keep an inhabited middle at broken symmetry; from n=6 the interior is abandoned forever — the shortest network is the rim minus one edge, an orbit of n equally-best crooked crowns. |
| II — The Beautiful Wrong Answer (2560²) | `malfatti_final.png` | **The symmetric answer can be a beautiful lie.** Malfatti's 1803 three-tangent-circles proposal is never optimal (Zalgaller–Los 1994); verified here across 44,850 triangle shapes, zero exceptions — even in the equilateral triangle the lopsided greedy packing wins by 1.364%. And the lie is at its *best* exactly where the symmetry is greatest. |
| III — The Sea That Forgives the Edges (2560²) | `sea_final.png` | **Sometimes symmetry is earned in the limit.** The reciprocal-addition Pascal triangle (live MO 514552): golden boundary rivers (B₁ = φ) decay like (−1/3)^j; the interior flows to √2, the fixed point of x↦2/x, remembering only one number — its conserved dissent M̄. New law: A(n,k)−√2 ≈ (−1)ⁿM̄2⁻ⁿC(n,k), so the asked-about constant is **C = √(2/π)·M̄ = 0.05222181**, verified to 7 digits. |
| Atlas 43 — The Door Past the Gate (2560²) | `atlas43_final.png` | **The fence was heard.** First gap-25 quintuple in the ℤ[√2] norm set: **n = 458,171,603,806** ≡ 94 (mod 144), exactly as piece 42's gate theorem demanded, inside its pre-committed hazard window. Verified by full factorization. |

All computations verified before rendering; see `verification.md`.
Engines: `steiner.py` (convex-position SMT census), `malfatti.py`,
`tri_science.py` / `tri_precise.py` (MO 514552), `hunt25.c` (Atlas relay),
renders `hero_render.py`, `malfatti_render.py`, `sea_render.py`,
`atlas_render.py`, shared `artlib.py`.

Also-rans (brainstormed, not executed — see `ideas.md`): partition of ℝ³ into
unit circles (MO 28647), maximally-irrational approximation sequences
(MO 514489), the trigonometric-sum ladder (MO 514561).
