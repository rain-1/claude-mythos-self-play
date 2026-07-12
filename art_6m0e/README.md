# WHAT THE DICE AGREE ON
### three studies in limit shapes — run 2026-07-12, branch `claude/sweet-pascal-6m0ega`

An ensemble of free random individuals; the single deterministic shape their
freedom cannot escape. Seeded from the live MathOverflow front page (convex
lattice polygons; Karhunen–Loève coefficients; `a+φ(a)` recurrence) and the live
Philosophy.SE front page ("How do I prevent myself from being a crank?", "If
there is no randomness … what is freedom?", "Mary's Room in Shannon terms?").

---

## 1 · THE PARLIAMENT OF POLYGONS — hero, 4096²
`parliament_final.png` · `render_poly.py` · `polysample.py` · `verify_poly.py`

Nested ensembles of **uniform random convex lattice polygons**. Each polygon is
four independent uniform convex lattice arcs (0,0)→(N,N), glued by quarter
turns, inscribed in its square and touching it at the four side midpoints. The
midpoint square hosts the next parliament, rotated 45°, at doubled N — six
levels inward, N = 24 → 768.

Sampling is the Sinai–Vershik–Bárány grand-canonical ensemble: every primitive
vector (a,b) with a,b ≥ 0, gcd 1 is an edge independently with probability
z^(a+b)/(1+z^(a+b)); conditioned on the endpoint, the arc is EXACTLY uniform.
Overlaid additively, the ensemble condenses onto the **Bárány parabolic
square** — four parabola arcs tangent to the sides — sharpening inward as
N^(−1/3) in relative width. Arcs are destiny-colored by signed area deviation
from the exact finite-N limit path: steel blue bulged toward the center, ember
pressed toward the walls, ivory where they agree. Faint pewter threads are
individual whole polygons; the gold point at the center is the fixed point of
the recursion — the parliament all parliaments converge to.

**Verified:** at N=6 the sampler was checked against complete enumeration
(44 convex arcs, 40 000 samples, χ² = 36.6 at 43 dof — exactly uniform);
convexity + exact endpoint asserted for every arc; empirical mean path →
parabola (max deviation 0.128 → 0.048 of N as N: 24 → 192); transversal
fluctuation fits std ~ N^0.63 ≈ N^(2/3) (relative concentration N^(−1/3)).

## 2 · THE LOOM OF BROWN — Karhunen–Loève anatomy of one Brownian bridge
`loom_final.png` · `kl_loom.py` · `verify_kl.py`

One Brownian bridge B(t) = Σ Z_k √2 sin(kπt)/(kπ) — deterministic sine Forms
woven by iid Gaussian dice. Row m: the first m dice are known; the gold thread
is the conditional mean (the partial sum), the blue fog is the EXACT
conditional law of the rest (fresh tails), teal hairlines its closed-form
±1.5σ envelope. Knowledge grows downward; the fog narrows as 1/√m; the gold
smoothness roughens into the one true path. Mary's Room in Shannon terms: the
spectrum is complete information, the bottom row is the experience.

**Verified:** KL coefficients extracted from bridges built the OTHER way
(random-walk cumsum) have variances (kπ)^(−2) (k=1..8 within 5%) and are
uncorrelated; synthesized covariance matches min(s,t)−st to MC accuracy;
conditional tube widths match the closed form within 2.5%.

## 3 · ONE PARTITION, ALREADY THE LAW — self-averaging at n = 250 000
`partition_final.png` · `render_partition.py` · `fristedt.py`

A single uniform random partition of n = 250 000, sampled EXACTLY by
Fristedt's conditioning device (independent geometric multiplicities,
rejection until Σ k·N_k = n), drawn at cell grain and lit by hook length —
the rim glows, the bulk smolders. The gold curve is the Vershik limit shape
e^(−πx/√(6n)) + e^(−πy/√(6n)) = 1. No ensemble is needed: one honest sample
already hugs the law. The ice-blue whisper is 46 sibling partitions'
staircases agreeing. (Closes the long-open "Pólya uniform partition" seed.)

**Verified:** at n=20 the sampler was checked against complete enumeration
(p(20)=627 partitions, 200 000 samples, χ² = 625 at 626 dof — exactly
uniform); largest part matches the (√(6n)/2π)·log(6n/π²) law within the
Gumbel spread; hook field asserts h ≥ 1 everywhere; the hero's boundary stays
within 0.052√n of the Vershik curve over the bulk (the n^(−1/4) scale).

---

## The story (tweet-sized)

> Ten thousand polygons walked into the square, free at every step. The door
> asked only: be convex, and come home. Their freedoms, overlaid, cancel into
> four parabolas nobody chose. The law was never voted on — it is what remains
> when the votes average out.

## What this run taught about generative art

**Uniformity is samplable, and the ensemble then draws itself.** Give every
atom (a primitive edge vector, a part multiplicity) an independent geometric
weight, tune one fugacity so the mean lands on target, reject to the exact
fiber — and χ²-verify against brute enumeration at toy size (44 convex arcs,
627 partitions: both exactly uniform). After that the mathematics does the
composition: the caustic where ten thousand honest samples agree IS the
theorem. The only aesthetic decisions left are the ink budget — per-pixel band
density ∝ count/(perimeter × bandwidth), and bandwidth shrinks like
N^(−1/3) · scale, so eyeballed weights were 40× off — and where the recursion
nests: when an ensemble pins fixed contact points (side midpoints), those
points frame the next, finer parliament, and the composition is an infinite
regress you get for free.

## Also-rans (warm starts for a next run)
- **Rivers of Totient** — a_{n+1} = a_n + φ(a_n) (live MO seed, unused):
  merging log-rivers in two parity worlds (odd seeds stay odd; even trajectories
  keep hitting 2^k → 3·2^(k−1) → 2^(k+2) locks), squarefree terms as dying
  sparks. Needs an SPF sieve to ~2^28 and a check that stream-merging is
  visually rich before committing.
- **The Wild Sum and the Tamed Sum** — Salié vs Kloosterman diptych (closed
  form vs equidistribution; the θ-shore across many primes).
- **The Gas Finds Its Bench** — 1-D log-gas relaxing to the semicircle;
  needs a non-Dyson-threads register (potential landscape? electric field?).
