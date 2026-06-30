# The Anatomy of a Shuffle — a permutation-theory gallery

Eight lenses on the symmetric group `Sₙ` (five in Volume I, three deeper ones in
Volume II), each with its own visual grammar and each verified in code before it
is drawn. A permutation is the simplest possible
"mixing" of a finite set — and almost every deep structure in combinatorics is
hiding inside it. This gallery grew out of the main set's piece 05 (the
Vershik–Kerov limit shape of a random Young diagram); here we open up the object
that piece came from.

Build it: each `render_0N_*.py` is self-contained (`numpy`/`scipy`/`Pillow`),
sharing `figkit.py` (the caption blocks), `cycles.py` (cycle decomposition +
verified `H_n` / Golomb–Dickman statistics), and `sortnet.py` (a verified
reduced-word / wiring-diagram utility).

---

## 1 · The Cycles of a Random Permutation
![cycles](01_cycles.png)

Every permutation is a disjoint union of cycles. Drawn here as chords `i→σ(i)`,
with each cycle grouped into its own arc, the **cycle-length partition** becomes
visible as the sizes of the woven lenses — and it follows the **Poisson–Dirichlet
(GEM)** law. A random permutation has on average `H_n = 1 + ½ + … + 1/n ≈ ln n`
cycles, and its **longest cycle** swallows the **Golomb–Dickman** fraction
≈ 62.4% of all points (verified by simulation: 0.618 vs 0.6243). The giant cycle
is the rule, not the exception.

## 2 · The Permutohedron
![permutohedron](02_permutohedron.png)

Place each of the 24 permutations of `(1,2,3,4)` at its own coordinate in
3-space: the vertices of a **truncated octahedron**. Edges join permutations that
differ by an **adjacent transposition** (a swap of neighbouring positions),
3-coloured by which generator `s₁,s₂,s₃` is used. This single object is at once
the **Cayley graph** of `S₄`, the **Hasse diagram of the weak Bruhat order**, and
a space-filling polytope (6 square + 8 hexagonal faces). The identity and the
full reversal sit at opposite poles, `(4 choose 2)=6` steps apart.

## 3 · RSK and the Longest Increasing Subsequence
![rsk](03_rsk.png)

The **Robinson–Schensted–Knuth** correspondence bijects every permutation with a
pair of standard Young tableaux `(P, Q)` of the same shape (verified inset). The
length of the first row equals the **longest increasing subsequence** — the gold
chain climbing through the point-matrix — computable in `O(n log n)` by patience
sorting. **Ulam's problem**, answered by Logan–Shepp/Vershik–Kerov and
Baik–Deift–Johansson: for a random permutation the LIS concentrates at `2√n`,
with Tracy–Widom fluctuations of order `n^{1/6}`. The shape produced by RSK is
exactly the random Young diagram whose limit is piece 05 of the main set.

## 4 · Counting Disorder: the Mahonian Distribution
![mahonian](04_mahonian.png)

How many of the `n!` permutations have exactly `k` **inversions** (pairs out of
order)? The counts are the coefficients of the **q-factorial**
`[n]_q! = (1)(1+q)(1+q+q²)…(1+…+q^{n-1})` — MacMahon's *Mahonian* distribution.
Centred and scaled, the exact distributions march toward a **Gaussian** (mean
`n(n-1)/4`, variance `n(n-1)(2n+5)/72`): a central limit theorem for disorder,
because `inv(σ)` is a sum of nearly-independent digits (the Lehmer code).

## 5 · Order, Tuned by a Single Parameter — the Mallows Measure
![mallows](05_mallows.png)

The **Mallows measure** weights each permutation by `q^{inv(σ)}`, sampled here
*exactly* by drawing independent geometric Lehmer digits. One dial `q` sweeps the
whole symmetric group from order to chaos and back: `q<1` rewards few inversions
and the permutation matrix collapses onto a **diagonal limit-shape band**; `q=1`
is the uniform permutation (structureless noise); `q>1` drives it to the
anti-diagonal. The same "frozen ↔ free" story as the main set's tilings, now over
`Sₙ`.

---

# Volume II — going deeper

## 6 · The Sine Curves of a Perfect Shuffle
![sorting network](06_sorting_network.png)

The piece the first volume deliberately left undone: a **uniform random sorting
network** — a uniformly chosen *shortest* sequence of adjacent swaps that reverses
`1,2,…,n` (a reduced word for the longest permutation `w₀`). Sampling one
*uniformly* is the hard part: the naive braid/commutation Markov chain mixes far
too slowly (even `n=30` stays visibly biased after 30M moves). The honest route,
built here, is exact: sample a **uniform standard Young tableau of staircase
shape** (the Greene–Nijenhuis–Wilf hook walk), then map it through the
**Edelman–Greene bijection** to a reduced word — with the bijection's forward and
inverse *round-trip verified on every reduced word of `S₄` and `S₅`* (0
mismatches), and the inverse's special-case rule (trigger iff the bumped value is
already present in the row) derived and checked by hand.

Each wire's path is a trajectory. **Angel–Holroyd–Romik–Virág** proved that as
`n→∞` these converge to **sine curves** (six highlighted in white over the woven
mesh), the swarm fills an ellipse, and a marked particle's path is the shadow of a
great circle on a sphere. This is one of the most beautiful theorems in modern
combinatorics, drawn from a genuinely uniform sample.

## 7 · Catalan's Permutations
![patterns](07_patterns.png)

A permutation **avoids the pattern 231** if no three positions carry values in the
relative order 2-3-1. These are exactly Knuth's **stack-sortable** permutations,
and they number the **Catalan** number `Cₙ` (verified: 1, 2, 5, 14, 42, 132, 429,
…) — as do the avoiders of any single length-3 pattern (all six are
Wilf-equivalent). Sampled here *exactly uniformly* via the recursive Catalan
decomposition `σ = L · max · R`; at scale the matrix reveals the class's **permuton
limit shape** — a Brownian-wandering diagonal — structure that a uniform
permutation (white noise) has no trace of.

## 8 · The Eulerian Triangle
![eulerian](08_eulerian.png)

The **Eulerian number** `A(n,k)` counts permutations of `n` with exactly `k`
**descents** (`σ(i) > σ(i+1)`). Each row, per-row-normalised to brightness, sums
to `n!` and is symmetric — ascents and descents balance — and concentrates on a
bright central ridge at `k ≈ (n-1)/2` (built by the recurrence
`A(n,k)=(k+1)A(n-1,k)+(n-k)A(n-1,k-1)`, verified). Eulerian numbers also yield
Worpitzky's identity and the `h`-vector of the permutohedron in Figure 2.

---

### Honest math, first
Every figure is checked in code before it is drawn: cycle statistics against `Hₙ`
and Golomb–Dickman; the permutohedron's vertex/edge/face counts; RSK and the
Edelman–Greene bijection by exhaustive round-trip; the Mahonian, Mallows, Catalan
and Eulerian counts against their closed forms. Where an honest sample was hard
(the sorting network), the work went into the *sampler* rather than into faking the
picture.
