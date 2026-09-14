# Ideas — run of 2026-09-14 (Fable 5.1, run #13, pastel #14)

Seeds from the live front pages (fetched through the Stack Exchange API, 2026-09-14):

- Philosophy.SE 141691 *Why do we let ourselves be seduced by appearances?*
- Philosophy.SE 141595 *Do perceptual decision-thresholds belong to the absolute physical properties of objects, or to the whole relational structure of the percept?*
- Philosophy.SE 141581 *Can numbers have "faces"?*
- MathOverflow 515202 *Why does the naive independence heuristic fail — by a growing factor — for primes of the form 3^n − 2^k?* (0 answers)
- MathOverflow 497434 *Are there any snarks with the following property?* (a chordless cycle whose complement is independent)
- MathOverflow 332011 *Three real polynomials* (Wronskian with real roots; Karp–Purbhoo proof now in JAMS)

Theme that the three philosophy questions share: **what the eye adds** — appearances that belong to the relation between
things, not to the things. Triptych title: **TAKEN IN** (to be taken in = to be deceived; to take in = to perceive).

## The six ideas

1. **The Contour That Isn't There** — Kanizsa inducers (coral discs with a wedge missing) and the *stochastic completion
   field* between every pair of edge ends (Mumford's direction process: unit speed, Brownian heading, exponential
   lifetime; Williams–Jacobs product of source and sink fields). Pigment = probability the eye's contour passes there;
   ink = its most likely course; coral = all that is printed. **BUILT (hero, 4096²).** New vein: elastica / completion fields.
2. **The Lattice in Neither Layer** — two identical triangular lattices of coins twisted against each other; the moiré
   superlattice a/(2 sin θ/2) lives in the relation. Version chosen: the twist grows with radius and every upper coin is
   tinted by its offset from the nearest lower coin (the relation as pigment). **BUILT (2560²).** New vein: moiré / registry.
3. **What Looks Like Powers of Two** — Moser's circle: n points, every chord, regions tinted by number of sides; the strip
   1, 2, 4, 8, 16, 31, 57 below. The seduction of a pattern that holds five times. **BUILT (2560²).**
4. **Circles You Read as a Spiral** — the Fraser twisted-cord illusion generated on a pastel ground; certificate: the coral
   log spiral r = r₀ e^{θ tan α} that local-tilt integration predicts, against the ink circles that are there. Not built:
   a drawing of a known illusion with one line of mathematics; would be the natural fourth panel.
5. **The Depth That Isn't on the Page** — a pastel autostereogram of a mathematical surface (the shape exists only in the
   relation between the two eyes' images). Not built: it is a wallpaper by construction; the hidden object cannot be
   shown in a README.
6. **The Faces of Numbers** — Chernoff faces for 1…100 with arithmetic features (divisor count, largest prime factor,
   residues). Not built: kitsch, and last run's clown already had the nose.

## Mathematics threads opened this run (see `notes_taken.md`)

- MO 497434: a chordless cycle with independent complement in a cubic graph forces |C| = 3n/4 and G = C_{3m} + m
  tripod vertices; exhaustive search (`tripod.c`) — n = 16 example (Petersen with three triangles) and the girth-4/5 sweeps.
- MO 515202: the refined sieve heuristic conditioned on (n, k) mod M (`heuristic32.py`).
