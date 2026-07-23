# The Economy of Attention

Triptych, 2026-07-23 (branch `claude/laughing-davinci-m3jsaf`).

Seeded from the live MathOverflow and Philosophy.SE front pages of the day.
Phil.SE was asking *"Does the Attention Economy Tend to Impoverish Our
Conception of Virtue?"* and *"The Metaphysics of Scale"*; MathOverflow was
asking three questions about where effort actually goes: a determinant that
costs nothing to know, an osculating conic that spends everything on one
point, and *"Where does Concorde spend its time."*  Three pieces about the
same currency.

## 1. The Ledger of Reflections — `hero_ledger.png` (4096²)

**Source.** MO 513368 (live front page): *"Is the determinant of the
'i+j is a power of 2' indicator matrix always −1 or 1?"* — posed as the
never-vanishing companion of the poster's Fibonacci-sum matrix (a seed this
series has carried for three runs).

**Mathematics.** `A_n[i,j] = 1` iff `i+j` is a power of two, `1 ≤ i,j ≤ n`.
The accepted MO answer proves the *permanent* is 1: there is **exactly one**
permutation π of {1..n} with every `i+π(i)` a power of two, hence
det ∈ {−1,+1}.  The answer leaves the sign open.  This run derives and
verifies the closed form

> **det A_n = (−1)^((n − r(n))/2)**, where r(n) = number of maximal runs of
> equal bits in the binary expansion of n.

Proof: on `[2^{k+1}−n, n]` (with `2^k ≤ n < 2^{k+1}`) the permutation is
forced to be the reversal `i ↦ 2^{k+1}−i`; what remains is the same problem
for `m = 2^{k+1}−n−1`, which is the **bitwise complement** of n below its
leading bit.  Complementing strips exactly one run, so the cascade has r(n)
stages; each stage is an involution with exactly one fixed point (the power
of two `2^k`, since `i = j = 2^k` gives `i+j = 2^{k+1}`).  So π has r(n)
fixed points and `(n−r(n))/2` transpositions.  ∎

Verified (`verify_ledger.py`): exact determinant (two independent 31-bit
prime moduli, plus exact `Fraction` elimination at n = 37, 100, 173, 256)
equals the formula and equals the constructed permutation's sign for **all
n ≤ 400**, plus spot checks at n = 1000, 2048, 2730, 3000, 4095, 4096.

**Image.** n = 2730 = 101010101010₂ — twelve runs, the deepest cascade below
4096; det = −1.  The number line lives on a log-spiral dial (one octave per
30°).  Each stage is a fan of nested arcs: arc = transposition
`i ↔ 2^{k+1}−i`.  Arc brightness strobes with the dyadic depth of the pair,
so each fan carries its own growth rings.  Gold stars = the twelve self-paired
powers of two; the ringed terminal star is the last entry of the ledger.  The
answer to a 2730×2730 determinant is twelve reflections — the cheapest audit
in the world.

## 2. Six Moments of Perfect Attention (×2) — `conics_attention.png` (2560²)

**Source.** MO "Osculating ellipsoids" (front page) pointed back to affine
differential geometry; the render is the planar story.

**Mathematics.** At every point of a smooth convex oval there is a unique
conic with 5th-order contact (the osculating conic).  Because 5 is odd, it
*crosses* the oval — except where contact jumps to order 6: the **sextactic
points**.  Mukhopadhyaya's six-vertex theorem (1909): every convex oval has
at least six.  Where affine curvature is positive the osculating conic is an
ellipse (attention that returns); where it dips negative the conic escapes
through a parabola into hyperbolae (attention that never comes back).

Engine (`conics_engine.py`): 5 derivative rows of `g(t) = Q(r(t))` in
contact-point-centered coordinates; osculating conic = SVD null vector;
sextactic function = det of the 6×6 with the 6th row appended.  Verified on
an exact ellipse: conic recovered to 5.5e−16 and sextactic det ≈ 8e−17
(machine zero — a conic osculates itself everywhere, so it has *no* sextactic
function).  The rendered oval `ρ = 1 + .09cos(2t+.7) + .055cos3t + .012cos(5t+1.9)`
has **12 sextactic points** (≥ 6 and even, as the theorem demands).

**Image.** Every osculating ellipse drawn as a closed ring, every hyperbola
as a whisker marched from its contact point; near-parabolic conics flash
silver.  The 12 sextactic conics are traced in gold near their moment of
contact, with gold beads on the oval.  The envelope of all that attention is
the oval itself.

## 3. Where the Time Is Spent — `dwell_web.png` (2560²)

**Source.** MO 501687 (live): *"Where does Concorde spend its time"* — carried
as an open seed from the 2026-07-23 run's also-rans.

**Mathematics.** 220 blue-noise cities in a disc.  Held–Karp 1-tree bound
with the classical subgradient (step = λ(UB−bound)/‖g‖², λ decaying on
stall), 8000 iterations; every edge that ever entered a relaxation is
recorded with its dwell (iterations held) and volatility (presence toggles).
Best tour by multi-start nearest-neighbour + 2-opt + Or-opt + double-bridge
iterated local search (~9000 kicks).  Certificate: best tour 21.83519 vs
Held-Karp lower bound 21.63651 -> the tour is provably within **0.92%** of
optimal, though no one ever computed the optimum.

**Image.** Rope thickness/heat = literal dwell; ember = high-churn contested
edges (where the deliberation actually happened); violet = edges tried
briefly and abandoned; gold = the best tour found.  City brightness = |π_i|,
the potential the ascent had to pay each city to behave.

---

*Also-rans this run: Gallai–Witt monochromatic homothets (noise risk),
Frankl union-closed golden-ratio frequency bound (chart risk), rank-1
elliptic curve generator walk (too close to used technique).*

---

*The auditor opened a ledger of 2,730 accounts and found every debt already
facing its mirror across a power of two. Twelve reflections down, one account
left, she signed the book: −1. Attention is the only currency the universe
accepts in exact change.*
