# Run `claude/determined-tesla-n4fogv` — ideation

Seeded from the LIVE front pages (2026-07-13).

**MathOverflow (active):** *Gershgorin's 2nd theorem (disjoint circles): elementary
proof?* · srg(n,k,0,2) Moore graphs · difference of square and cube (Mordell/Hall) ·
prime-gap growth (log p)^{H_k} · laminated lattices Λ13 · divide space by surfaces ·
n·m coins generalizing n-queens.

**Philosophy.SE (hot):** *What Privileges the Real? (symbol grounding)* · *Is reality
inherently logical?* · *how do we detect Absurdity given the egocentric predicament?*
· Why can we contemplate abstractions at all? · consistent theory you don't believe
arithmetically sound.

## The marriage
The eigenvalues of a matrix are roots of its degree-n characteristic polynomial. By
Abel–Ruffini there is **no closed form** for n≥5 — you can never *write down* where
the spectrum is. Yet the matrix's own entries **cage** it: the diagonal is your naive
guess, the off-diagonal is your uncertainty, and Gershgorin's theorem *guarantees the
truth lives inside the cage you can draw*. That is the epistemology of the spectrum,
and it answers the philosophy front page directly: you bound the real you cannot see.

## Six ideas
1. **Gershgorin discs + the 2nd (capture) theorem** — LIVE MO hero. Complex plane;
   discs centred at a_ii, radius = off-diagonal row sum; eigenvalue-stars caged inside.
   2nd theorem: a connected component made of k discs holds exactly k eigenvalues →
   colour "resolved" isolated discs (gold, capture 1) vs a contested overlapping bath.
2. **Brauer's ovals of Cassini** — the strictly tighter cage: |z−a_ii||z−a_jj| ≤ R_iR_j.
   Lemniscate eyes nested inside the discs; the cage tightening onto the truth.
3. **Pseudospectra** of a strongly NON-normal matrix — resolvent-norm density field
   σ_min(zI−A); the ghost cloud bulges far past the eigenvalues where the spectrum is
   fragile to perturbation. The cage says where it MUST be; the ghost, where it could go.
4. Mordell / Hall near-misses |y²−x³| — record race (noise risk).
5. Moore graph srg(n,k,0,2) Hoffman–Singleton (hairball risk).
6. Laminated-lattice minimal-vector mandala (recipe already used-ish).

## Chosen triptych — "Where the Real Must Be"
- HERO 4096²: Gershgorin discs as a luminous overlap-nebula + capture colouring (1).
- Panel 2560²: Brauer Cassini ovals, the tighter cage (2).
- Panel 2560²: pseudospectra, the ghost (3).

Distinct registers: sparse jewel-discs + central bath / nested lemniscate eyes /
continuous glowing resolvent field. Two enclosure pieces + one density field.

All three VERIFIED in code before pixels (von Dyck discipline): every eigenvalue
inside its cage; capture count per component exact; pseudospectra by true σ_min grid.
