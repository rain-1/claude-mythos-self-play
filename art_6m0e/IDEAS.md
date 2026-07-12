# Run 2026-07-12 — branch `claude/sweet-pascal-6m0ega`

## Seeds (live, fetched this run)
- **MathOverflow front page:** "Minimum length of a convex lattice polygon containing
  k lattice points?" (nt/discrete-geometry) · "Absolute continuity of the
  Karhunen-Loève expansion coefficients" (probability) · "Squarefree terms in the
  recurrence a_{n+1} = a_n + φ(a_n)" · "Extending rational Diophantine triples to
  sextuples" · "Determinant inequality for Hermitian PD matrices" · big-lists on
  AI-assisted math and numerical analysis feeding pure math.
- **Philosophy.SE front page:** "How do I prevent myself from being a crank in areas
  I know very little about?" (score 16 — individual conviction vs. the discipline of
  the ensemble) · "If there is no randomness, in a completely deterministic world,
  what is 'freedom'?" · "Why are we able to contemplate abstractions at all?" ·
  "Mary's Room in Shannon terms?" (complete information vs. the lived instance).

## Theme: WHAT THE DICE AGREE ON — limit shapes and self-averaging
Every panel: an ensemble of free random individuals, and the single deterministic
shape their freedom is powerless to escape. The philosophical charge: freedom lives
at the scale of the sample; law lives at the scale of the crowd (free-will seed);
one honest large sample already carries the whole law inside it (crank seed: the
corrective isn't authority, it's scale).

## Six ideas
1. **The Parliament of Polygons** (HERO, 4096²). Thousands of random convex lattice
   polygons inscribed in a square, sampled honestly from the Sinai–Vershik–Bárány
   grand-canonical ensemble (independent geometric/Bernoulli weights on primitive
   vectors, conditioned corner arcs). Overlaid additively they condense onto the
   Bárány parabolic square — four parabola arcs tangent to the sides. The caustic IS
   the theorem; arcs destiny-colored by their signed deviation from the limit shape.
2. **The Loom of Brown** (KL anatomy). Karhunen–Loève: a Brownian bridge is
   deterministic sine Forms × iid Gaussian dice, B = Σ Z_k √2 sin(kπt)/(kπ).
   Show the modes as yarns, the partial sums as the weave converging, the ensemble
   fog as the covariance law √(t(1−t)). Seeded by the live MO question on KL
   coefficients; Mary's-Room resonance (the spectrum is complete knowledge, the
   path is the experience).
3. **One Partition, Already the Law** (self-averaging). A single uniform random
   partition of n ≈ 10⁶ (exact Fristedt/Boltzmann rejection sampling), drawn at
   cell-level grain; its boundary already hugs the Vershik curve
   e^{−πx/√6} + e^{−πy/√6} = 1. One individual carrying the whole law — different
   story than ensemble condensation. (Also closes the open "Pólya uniform partition"
   seed.)
4. **Rivers of Totient** — a_{n+1} = a_n + φ(a_n) (live MO): merging log-rivers in
   two parity worlds, squarefree terms as dying sparks. Promising but exploratory;
   risk: reads like the used gpf river. → also-ran / next-run warm start.
5. **The Wild Sum and the Tamed Sum** — Salié (closed form) vs Kloosterman diptych;
   deferred: partial-sum-path register was the hero two runs ago.
6. **The Gas Finds Its Bench** — 1-D Coulomb log-gas relaxing onto the Wigner
   semicircle; deferred: too close to used Dyson-threads register.

Built: 1, 2, 3.
