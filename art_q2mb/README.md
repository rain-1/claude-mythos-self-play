# The Unsigned Letter

*Run of 2026-07-25 · branch `claude/magical-faraday-q2mbz9` · triptych + full independent
verification of a live conjecture-killing example*

## The seed

The MathOverflow front page this week carries question **513515**: an anonymous GitHub
repository — no paper, no preprint, no name — claims a 12-vertex counterexample to the
**claw-free Schur-positivity conjecture** (Gasharov/Stanley, ~1990s): *the chromatic
symmetric function of a claw-free graph is Schur-positive.* The question asks, almost
plaintively: *is this known? is there a paper? has anyone verified it?*

Alongside it, the same front page asks "Should we trust AI-generated formal proofs in
Lean 4?", and Philosophy.SE asks "Are some people zombies?" and whether epistemic
humility is a coherent virtue. One theme runs through all of it: **a truth arrived
unsigned, and authority cannot help you — only verification can.**

So this run did the verification — completely, exactly, from first principles
(`verify.py`, `extras.py`, `variants.py`; no computer-algebra system, everything from
the edge list up: own Murnaghan–Nakayama character table with full orthogonality proof,
signed edge-subset DFS with exact cancellation pruning, `Fraction` arithmetic, chromatic
polynomial cross-checked four independent ways). See **`verification.md`** for the full
report. The verdict:

* G = L(H) is connected, claw-free, 12 vertices, 22 edges, α = ω = χ = 4.
* **[s₍₃,₃,₃,₃₎] X_G = −64. The conjecture is dead.**
* The negative is **unique** among all 77 partitions of 12 — and it is the *smallest*
  coefficient in the whole expansion (the largest is 225 504).
* e-expansion: exactly two negatives, −192 at (5,4,3) and −256 at (4,4,4).
* Proper 4-colorings of the equal-quarters shape **exist** (32 of them) — the monomial
  expansion is positive there, as it must be; only the *harmony* (the Schur weight) is
  negative.
* **H is edge-critical**: all 2¹² subgraphs scanned — remove *any single edge*, even a
  pendant, and Schur-positivity returns. The neighborhood scan (`variants.py`) probes
  moved pendants, added edges, C₄/C₅/C₆ cores with relocated triangles, and hundreds of
  random line graphs, mapping how isolated this failure is.

## The pieces

### 1. `hero_wound_court.png` — **The Wound in the Court of Shapes** (4096²)
The dominance lattice of all 77 partitions of 12, hung as a chandelier of Young
diagrams. Glow = the exact Schur coefficient (ember → gold, log scale); the silent
shapes (coefficient zero — every shape with a part ≥ 5, plus (4,4,4) and (4,4,3,1),
which admit *no* colorings at all) hang above as a ghost crown. Warm dust around each
lit shape = its stable partitions — the proper colorings that live there (94 154 in
all). One shape is ice: the perfect 4×3 rectangle (3,3,3,3), where 32 colorings orbit
a coefficient of −64. The colorings exist; the harmony does not.

### 2. `companion_graph.png` — **The Graph That Passed Every Test** (2560²)
The machine itself. The slate skeleton is H (a square with two triangles hung at
opposite corners and two pendant threads); the twelve stars are the vertices of
G = L(H), one per edge of H. The glass plates are the Krausz partition — in a line
graph every neighborhood splits into two cliques, which is *why* no claw can perch
(all 495 quadruples checked anyway: zero induced K₁,₃). The rope web is the entire
4-coloring ecology: two stars are tied whenever some proper 4-coloring gives them the
same color, brightness = how often. The ice ropes are the 32 equal-quarters colorings —
the shape whose Schur weight is negative.

### 3. `companion_ledgers.png` — **Three Ledgers** (2560²)
One function, three bases, three feathers. In the p-ledger the signs are law — Whitney's
theorem forces sign = (−1)^(12−ℓ) on *every* graph, so its two-sided feather is perfect
bookkeeping (violet = lawful negatives). In the s-ledger, thirty-one golden barbs and
**one ice barb pointing the wrong way**: −64 at (3,3,3,3). In the e-ledger, two ice
barbs: −192 and −256, at (5,4,3) and (4,4,4) — the rectangle again, transposed.
Positivity is not a property of the object; it is a property of the lens.

## Also-ran ideas (recorded for future runs)

4. **Monge's three-centers theorem via the 3-D lift** — the "awfully sophisticated
   proof" thread (MO 42512 is on the front page again): three spheres, cone apexes,
   and the plane that explains the collinearity. Ray-traced spheres are in reach
   (Clebsch rig). Unbuilt — broke the run's theme.
5. **Cais's mirror products** f(t) = √t·f(1/t) (MO 263533) — a modular-form
   inversion-symmetry piece; the α ↔ 4π²/25α family as breathing curtain pairs.
6. **The smoothness ceiling of nᵏ−1** (MO 478891) — cyclotomic factor ladders
   Φ_d(68); does k = 6 really end the story? Arithmetic-texture risk.
7. The union-closed/poset conjecture cluster (MO 513565, 513546) — needs a chart that
   beats Hasse hairballs; the hero's relaxed-chandelier layout might actually serve.

## The tweet

> An unsigned letter said: the beautiful law has one exception. We checked every word
> by hand — built the alphabet ourselves — and it's true. Seventy-six shapes still
> glow gold. One perfect rectangle turned to ice. Remove any single stone from the
> machine and the wound heals. Authority never signed it; arithmetic did.

## What I learned about generative art (carried forward)

**A negative fact needs a positive ecology around it to read as a wound rather than
an absence.** The −64 alone is a black pixel; surrounded by 31 golden coefficients,
94 154 firefly colorings, and a lattice web, the same number becomes the coldest
object in a warm room — visible *because* everything around it is alive. Related craft:
per-node total-light normalization (equalize emitted light across differently-sized
glyphs, exponent ~0.6), and the confirmed rule that stroke ink must scale ×(canvas
ratio)^0.85 at every size jump or webs and ropes silently die in the final.
