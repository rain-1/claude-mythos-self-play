# Verification notes — run 2026-07-31 (`art_mt4z/`)

Triptych **PASSING** — three live MathOverflow subjects about the gap between
passing a test and having the property (Phil.SE front page: "Are some people
zombies?", "Is epistemic humility a coherent virtue?").

---

## 1. The Republic of Rest (hero, 4096²) — MO 513737 "A Level (not wobbly) table theorem?"

**Question** (live, 0 answers, jul 2026): let h be smooth on the closed unit
disk with h = 0 on the boundary circle.  Given d, must there be 3 points at
pairwise distance d with equal h?  Can you do it for a square of points?

**Model.**  Table placements = (center c, rotation θ).  Feet of a tripod of
side d: circumradius R = d/√3; feet of a square table of side d: R = d/√2.
Heights are read at the vertical projections (the standard hovering model).

* **Coplanarity lemma (exact, drives the violet layer):** the four lifted feet
  (f_i, h(f_i)) of a square are coplanar ⟺ h₁ + h₃ = h₂ + h₄, because the two
  diagonals of a square share their midpoint in the plane; a plane is affine,
  so coplanarity is equality of the two lifted midpoints.  Thus the classical
  wobbly-table functional g = h₁ − h₂ + h₃ − h₄ is not just a trick: g = 0 is
  *exactly* "a rigid flat tabletop can touch all four feet."  Since
  g(θ + π/2) = −g(θ), every center admits balanced (all-four-touching)
  orientations — the codimension-1 surface rendered as the violet atmosphere
  (brightness = smallest achievable tilt of the resting plane).
* **Level tripod = 2 equations in 3 unknowns** (u₁ = h₂−h₁, u₂ = h₃−h₁):
  solution set is generically a union of **curves** in (c, θ).
* **Level square = 3 equations in 3 unknowns**: generically **isolated
  points**.

**Rotation lemma (why two feet can always agree):** rotating a tripod by 2π/3
permutes its feet cyclically, so u₁(θ+2π/3) = u₂−u₁ and u₂(θ+2π/3) = −u₁,
i.e. v = (u₁,u₂) satisfies v(θ+2π/3) = Mv(θ) with M = [[−1,1],[−1,0]],
M³ = I, eigenvalues e^(±2πi/3).  Two corollaries: (a) u₁ + u₁∘ρ + u₁∘ρ² = 0
(ρ = 2π/3 shift), so u₁ vanishes on every θ-fiber — two feet can always be
leveled; (b) if v never vanished on a fiber, its winding number about 0 would
be ≡ ±1 mod 3 — in particular nonzero — for *every* center, since ṽ satisfies
ṽ(θ+2π/3) = R_{±2π/3}ṽ(θ) in M's eigenbasis.

**Computation** (`table_lib.py`).  Terrain = (1−r²)·Σ₁⁶ Aₘ cos(kₘ·x+φₘ)
(analytic, h = 0 and smooth at the shore; seed 42, d = 0.70 for the hero).
Level-tripod curves: dense θ-scan for u₁-roots on a 320² center lattice,
neighbour sign-changes of u₂ on each u₁-sheet, Newton polish with the 2×3
pseudo-inverse, then pseudo-arclength continuation (step 0.0016) with spatial-
hash dedupe.  Every traced placement satisfies |h_i − h_j| < 1e-10 (analytic
evaluation, no grids).  Level squares: 3-D grid scan + full Newton on
(u₁,u₂,u₃), dedupe, residuals < 1e-11.

**Hero-terrain results (seed 42, d = 0.70):**
* level-tripod solution set: **19 closed curves** in (position × angle)-space,
  21,406 traced placements;
* level squares: **exactly 4 isolated placements** (heights k = +0.136,
  +0.242, +0.150, −0.198 on the earlier seed-7 check; seed-42 values in
  `hero_stats_final.npy`);
* balanced-but-tilted square placements exist at every center (wobbly-table
  IVT, verified: every fiber of the 640²-center scan has ≥ 2 sign changes
  of g).

**d-sweep** (3 terrains × 12 sides, `sweep_results.json`): see run log —
level-tripod curves existed for **every** (terrain, d) tested; level squares
are few (0–8) and **do vanish** for some (terrain, d) pairs, supporting the
guess that the square version of MO 513737 needs more than topology (cf.
Fenn's table theorem, which levels a square on a *hill* — a positive bump on
a convex support — not on a general sign-changing floor).

The dimensional hierarchy — touching is a surface, resting level is a curve,
standing true is a point — is the subject of the piece.

## 2. The Seams to the Horizon (2560²) — MO 122539 "Unreasonable effectiveness of Padé"

Object: f(z) = (1−z³)^(−1/2), Taylor coefficients binom(2k,k)/4^k on z^{3k}
(exact rationals).

* **Composition theorem** (by Padé uniqueness): if P/Q is the [m/m] Padé of
  g(w) = (1−w)^(−1/2) then P(z³)/Q(z³) is the [3m/3m] Padé of f.  All
  computations are done on g at 220–400 digits (mpmath Toeplitz solve) and
  composed.
* **Markov certificates** (g(w) = (1/π)∫₁^∞ (t−1)^(−1/2) dt/(t−w) is a
  Markov/Stieltjes function): for every computed order m ∈ {2,…,48} all m
  poles are **real to 220 digits**, lie in the cut (1,∞), poles and zeros
  interlace (p₁<z₁<p₂<…), and consecutive orders' poles interlace
  (verified m = 47 vs 48).  Under z = u^{1/3} the pole set is exactly the
  three rays — the seams.
* **Exact error law**: |f − [144/144]|/|f| = 2|φ(z³)|^97 with
  φ(u) = (√(1−u)−1)/(√(1−u)+1), verified against a fresh 400-digit Padé at 8
  points spanning the plane (near cut, far field, near origin): max deviation
  **0.012 digits**.  (First attempt used approximants stored at 40 digits as
  the reference — the "13-digit discrepancy" was the reference's own storage
  noise.  Fixed by recomputing at dps=400.)  The warm field renders this law;
  its level sets are the Green equipotentials of the cut plane.
* Taylor next-term surrogate validated: mean |dev| 0.15 digits in the
  measurable float64 band.
* **Effectiveness certificate**: at z = 1.7+0.4i, |f − T₂₉₁| ≈ 3.7e+68
  (divergent — outside the disk) while |f − [144/144]| ≈ 3.0e-14; at
  z = −2.2+0.1i: 2.9e+97 vs 2.7e-26.  Same 97 coefficients of information.

## 3. The Nine Hundred Million Winters (2560²) — Pólya's conjecture

λ(n) = (−1)^Ω(n) sieved for **every n ≤ 2³⁰** by own segmented C sieve
(`liouville2.c`, 4 threads, ~3 min; per-4096-block sums + per-block max
prefix of the partial sum, so the block data *rigorously* brackets
L(x) = Σ_{n≤x} λ(n) everywhere).

* Sieve verified against sympy factorint for all n ≤ 8192 (block sums −64,
  +42 … match exactly), and against published values L(10⁵) = −288,
  L(10⁶) = −530.
* **First violation of L(x) ≤ 0 (x ≥ 2): x = 906,150,257, L = +1** —
  Tanaka's 1980 value, reproduced from scratch.  The per-block max-prefix
  data proves no earlier x ≥ 2 has L(x) > 0 within 2³⁰ (only blocks
  221228–221310 can touch positive; each was drilled exactly).
* **Maximum: L = +829 at x = 906,316,571** (matches literature).  The
  positive region within 2³⁰ is an archipelago: **136 maximal runs,
  305,426 positive integers**, spanning [906,150,257, 906,488,079].
* Closest earlier approach: L = −2 at x = 48,512.
* L(2³⁰) = −34,472.

Haselgrove (1958) proved L(x) > 0 infinitely often; Tanaka (1980) found the
first crossing.  The piece plots L(x)/√x (linear x, per-pixel-column min/max
envelope of exact values — 2¹¹-step exact prefix below 2²⁵, exact block
boundaries above), with the inset showing exact per-integer L on the island.

---

*Everything computed this run: own sieves, own Padé solves, own Newton
continuation; no values taken on faith beyond the cited literature
cross-checks. Code in this directory reproduces all numbers.*
