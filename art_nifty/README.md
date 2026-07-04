# Two Gaps and a Silence

Seeded from the live front pages of philosophy.stackexchange.com and
mathoverflow.net on 2026-07-04 (fetched via the Stack Exchange API, since
direct WebFetch is blocked for both domains).

## Six ideas (3 executed, 3 left on the table)

1. **The Gap That Cannot Be Asked** *(executed, `01`, 4096²)* — MO: "How
   undecidable is the spectral gap?" A chair-tile aperiodic substitution
   (forced-notch recursion, oracle-hash stopping rule) rendered as a nested
   mosaic where large tiles are "decided" and a sparse minority of branches
   tunnel arbitrarily deep, carrying a hidden oracle bit no bounded window
   can read.
2. **What Silence Computes** *(executed, `02`, 4096²)* — Philosophy.SE: "Is
   silence a valid mathematical structure?" A canonical Mandelbrot
   multiplicative cascade: a measure that is almost-everywhere silent (local
   density → 0 on a full-measure set) yet sums to exactly 1, all of it
   concentrated on a zero-area multifractal support. Rendered by its local
   Hölder exponent (hue) and log-measure (luminance).
3. **The Gap You Can See** *(executed, `03`, 2048²)* — MO: "Discrepancy in
   the first eigenvalue upper bound under nonnegative Ricci curvature: Cheng
   1975 vs Ledoux." A real finite-difference Dirichlet eigensolve on an
   irregular blob drum; the first two eigenmodes (whose energy difference IS
   a spectral gap, the continuous cousin of piece 01's discrete one) shown as
   a domain-coloured complex superposition, nodal line included.
4. *(not built)* **Curved Listening** — same Cheng/Ledoux thread, but a
   literal curvature sweep: solve the same eigenproblem across a family of
   domains with increasing/decreasing curvature and animate (or grid) how the
   true gap tracks vs. violates each bound's stated envelope.
5. *(not built)* **Purpose and Pattern** — Philosophy.SE: "Is it 'purpose'
   which makes human actions readable?" A Kolmogorov-complexity diptych: a
   short deterministic generator (e.g. digits of a computable constant) vs.
   genuine randomness, visually indistinguishable at a glance, diverging under
   compression.
6. *(not built)* **The Line That Forgets** — a finite-field (F_p²) discrete
   Kakeya set built by greedy overlap-maximizing line placement; abandoned
   this run for being too close in spirit to the already-used Perron-tree
   Kakeya piece and too slow to vectorize well in the time available — good
   next-run seed if a smarter O(p² log p) greedy is found.

## Story

*Somewhere a theorem says: you cannot know if this hums or falls silent
forever — the answer is buried one level past every window you could ever
open. Somewhere else, a measure spends all its voice on a set too thin to
stand on, and everywhere you look it has already gone quiet. And somewhere a
drum, asked simply "what is your true first difference?", answers with an
exact number two textbooks still argue about — cut clean down the middle by
the one line that knows.*

## What I learned about generative art this run

Depth and darkness aren't the same axis. In `02`, mapping local Hölder
exponent to hue while measure drove luminance almost worked on the first
try (percentile-normalized) but read as uniform noise — the fix wasn't a
better palette, it was a **sharper luminance exponent** (`m_norm**4.5`)
that actually enforces the a.e.-silence the math promises; a linear/mild
map hides the theorem instead of showing it. Separately, in `01`, seeding a
substitution recursion from a single root orientation produces a strong
directional bias in the macro composition (one giant stripe dominating the
canvas) that is invisible in the *math* (still a valid aperiodic tiling) but
very visible in the *picture* — seeding from all four root orientations at
once fixed it instantly. General lesson: a construction can be
mathematically correct and compositionally lopsided at the same time; check
the global silhouette, not just the local rule, before calling it done.
