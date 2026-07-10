# What the Experiment Saw — a triptych

*Run 2026-07-10, branch `claude/sweet-pascal-nt0mi7`.*

Three deterministic systems caught behaving freely — two of them the actual
birth of experimental mathematics, one a sum that walks like a drunk and lands
like a law. Seeded from the live MathOverflow front page ("On a sum like
Kloosterman sum"; "Examples where numerical analysis led to advances in pure
mathematics" — FPUT/KdV **is** the canonical answer) and Philosophy.SE ("If
there is no randomness, in a completely deterministic world, what is freedom?";
"Is it possible to verify knowledge without applying it?").

## 1. `kloosterman_eye.png` — *The Freedom of the Middle of the Sum* (4096², hero)

For p = 6659 and every residue a, the partial-sum path
t ↦ (1/√p) Σ_{x≤t} e((ax + x̄)/p) is drawn as one thread — 6658 threads,
6658 steps each. Every thread is totally determined, wanders like a random
walk, and is **forced to land on the real axis inside Weil's bound [−2, 2]**;
the landing pegs form the razor "law-bar" through the middle (their density is
exactly the semicircle — the Sato–Tate measure pushed to the endpoint).
Threads are colored by **destiny**: the angle θ(a) = arccos(S/2√p) — gold for
S near +2√p, ice for −2√p, the violet/indigo crowd in between (sin² weighted).
Because destiny drags the whole walk, the coloring self-organizes into a
two-lobed eye. Ten extremal-destiny paths are drawn as crisp hero filigree.

Verified in `verify_kloosterman.py` / render pass 0:
- every full sum real to 5e-14, Weil bound |S| ≤ 2√p holds for all a
  (max ratio **0.9989** at p=6659 — one path lands 0.1% from the wall);
- S(a,b) depends only on ab (50 random pairs, 1e-14);
- θ-histogram matches the vertical Sato–Tate sin² density;
- each path is **exactly mirror-symmetric about the vertical line
  Re = S(a)/2** (P_{T−t} = S − conj(P_t), checked to 1e-13) — the mirror
  stands at half the destiny.

## 2. `fput_braid.png` — *The River That Refused to Thermalize* (3584×1792)

Fermi–Pasta–Ulam–Tsingou 1955, the first numerical experiment: N=32 masses,
quadratic coupling α=0.25, all energy in mode 1. Velocity-Verlet to t=22000
(energy drift 2.5e-7). The streamgraph shows normal-mode energies E_k(t):
gold = mode 1, cascading through ember/coral/violet/indigo. The energy
refuses to equipartition — it braids down the spectrum and **reassembles**:
first recurrence at t=158 with 99.31% back in mode 1, then a decaying series,
then the **super-recurrence** near t≈10200 (98.1%) and again near t≈20300 —
two complete grand breaths. The river's wiggle baseline follows the mode
centroid (conservation makes the raw outline a rectangle; the bow of the
river is the cascade running deep).

## 3. `kdv_waterfall.png` — *The Cosine That Shattered into Individuals* (2560²)

Zabusky–Kruskal 1965 — the experiment that explained FPUT and named the
soliton: u_t + u u_x + (0.022)² u_xxx = 0, u(x,0) = cos(πx). Pseudospectral
N=2048 + ETDRK4 (full-circle complex contour — the dispersive operator needs
it), 2/3-rule dealiased; invariants ∫u, ∫u², ∫(u³/3 − δ²u_x²) conserved to
8e-17 / 7.5e-12 / 1.3e-10. Ridgeline waterfall: 100 time slices, back (the
smooth cosine fan) to front, hidden-line occlusion, in a co-moving window
(x' = x − 0.504t, one unit wide). The wave steepens at t_B = 1/π, shatters
into eight solitons — sech² mountains whose summits gild by height — that
pass through each other and **near-realign at t = 9.54** (shift-maximized
correlation 0.926 with the initial cosine; Zabusky's classic estimate 30.4/π
≈ 9.68).

## Also-ran ideas (this run's brainstorm)

4. Boole-map wanderer — T(x) = x − 1/x preserves an *infinite* measure;
   excursion night-sky ("Infinity and Nothing" on Phil.SE).
5. Jammed congruent-square packing with tensegrity force chains (live MO
   jamming question).
6. Kloosterman angle shore — θ_p(a) across many primes vs the sin² curve as
   a shoreline (the hero absorbed this as endpoint-peg density).

## Files

- `common.py` — splat/tonemap/bloom/palette toolkit
- `verify_kloosterman.py` — theorem checks run before any pixel
- `kloosterman.py` — hero renderer (pass 0 re-verifies Weil + finds heroes)
- `fput_sim.py`, `fput_render.py` — FPUT simulation + braid
- `kdv_sim.py`, `kdv_render.py`, `kdv_waterfall.py` — KdV simulation,
  field-carpet study, final ridgeline waterfall
- `variants/` — the iteration trail
