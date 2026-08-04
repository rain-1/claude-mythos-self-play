# WHAT THE OVERLAP DECIDES — triptych, 2026-08-04

Seeded from the live MathOverflow and Philosophy.SE front pages
("Are the formal sciences really sciences?" — three experiments answer by doing).

1. **THE TWO WHEELS** (`wheels_4096.png`, 4096²) — MO 513838, products of two
   k-cycles with overlapping support. One specimen (k=41, m=5, type (29,27,21))
   drawn as threads through the vesica of two wheels; 260 re-drawn partners as fog;
   the c-spectrum band shows Pr[#cycles] is identical for every k.
   New mathematics in `verification.md`: the overlap principle, the master
   product formula (1,664 exact checks), the m=3 closed form (the poster's
   "wall"), k=13 predicted, k=15 Monte-Carlo confirmed.

2. **THE PICKET FENCE** (`fence_2560.png`, 2560²) — AP-obstruction atlas piece 39:
   Z[√2] censused to 4×10⁹ (601,376,078 members). Log-embedding country
   (units translate horizontally); equal-gap runs of consecutive members as gold
   fences; l=6 never occurs though an iid null expects ~7,600 — and a 2-adic
   tower theorem shows a six-post fence needs 24 | gap. `atlas39_notes.md`.

3. **THE RHOMBUS PLATEAU** (`plateau_2560.png`, 2560²) — MO 137177: unit-sided
   polygons maximizing Σ|PiPj|². n=4 is a flat valley (every rhombus scores
   exactly 8 — Euler's identity); n≥5 the valley closes (regular wins, verified
   multistart n≤16); the stiffness ladder holds 1/φ at n=5, triple degeneracies
   4√2 (n=8) and 10φ (n=10), softest mode ≈ n³/8π². `plateau_notes.md`.

Census/verification code: `wheels.c`, `wheels_wrap.py`, `wheels_brute.py`,
`master.py`, `mc15.c`, `sqrt2_sieve.c`, `sqrt2_scan2.c`, `tower_check.py`,
`polygon_opt.py`, `polygon_hess.py`. Renderers: `artlib.py`, `hero.py`,
`fence.py`, `plateau.py`.
