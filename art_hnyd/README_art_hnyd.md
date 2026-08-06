# WHAT THE REPLACEMENT KEEPS — triptych, 2026-08-06

Branch `claude/serene-fermi-hnyd4x`. Philosophical seed: the live Phil.SE front
page — *"Recurring Consciousness Replacement Theory"* (Q140227: consciousness is
replaced every instant by a new one that inherits all the memories and lives
under the illusion of continuity). Mathematical seeds: three fresh MathOverflow
questions about what survives repeated replacement. Every piece is verified
computation; see `verification.md`.

## The pieces

### 1. `settle_4096.png` — THE LAST TO SETTLE (hero, 4096²)
**MO 513971** (0 answers): alternately sort the rows, then the columns, of a
binary matrix into lexicographic order; the process always settles into a
doubly-sorted fixed point. The artwork is pixel-native: ONE 4096×4096 uniform
random binary matrix actually run to its fixed point (T = 6 sorts), each pixel
lit by the pass in which it last changed — cold indigo (pass 1) through mauve
and ember to blazing gold (pass 6). The last act of the whole process is
22 adjacent swaps of near-identical columns (gold threads, stitch knots at
top); 1423 rows were still moving one pass earlier (orange ticks, left ledger);
129 restless cells changed in every single pass (white stars). Science:
poster's exact values verified, **new exact μ₅ = 36573599/2²⁵**, worst case
2n−3 exhaustive to n = 5, Monte Carlo to n = 8192, and the conjecture
**E[T] ≈ 2.0 + 1.7 ln ln n** (the replacement cascade squares the rarity of
surviving ties each round).

### 2. `ledger_2560.png` — THE LEDGER OF SIGNS (2560²)
**MO 513954** (0 answers): the structured rank-one downdate
M ← M − (Mx)(Mx)ᵀ/(xᵀMx) hands EXACTLY one direction to the null space per
replacement — n₊ or n₋ drops by one according to sign(xᵀMx), everything else
kept. Answered **YES** by one Sylvester congruence (no D⁻¹; proof + exact
rational verification in `verification.md`/`inertia_verify.py`). The render:
a signature-(66, 42, 12) operator drained to zero in exactly 108 replacements —
amber positive spectrum above the shore, teal negative below, one white-hot
comet dying into the shore per stage, the kernel-ledger strip counting
(n₊, n₋, n₀) underneath. Eigenvalue magnitudes are flung violently along the
way; the signature count is the only thing the replacement keeps.

### 3. `debt17_2560.png` — THE DEBT OF CHANNEL SEVENTEEN (2560², ATLAS PIECE 41)
The AP-obstruction atlas continues: S = norms of ℤ[√2], l = 5 equal-gap fences
of consecutive members, census pushed 3.2×10¹⁰ → **10¹¹** with piece 40's
segmented full-factorization sieve (re-certified: |S|(4×10⁹) = 601,376,078
exactly). Channels ordered by opening depth form a staircase — 574, 4892,
2.0×10⁵, …, 2.1×10⁹, 5.3×10⁹ — and then the staircase breaks: gap 17, whose
local densities equal gap 1's EXACTLY (piece 40's gap-scaling theorem), stays
silent while the calibrated model's expected fences pile up as ghost rungs.
See `atlas41_notes.md` for the verdict at 10¹¹.

## Files
- `sort_lib.py`, `exact_small.py`, `mc_scale.py`, `mc_topup.py`,
  `analyze_sorting.py`, `hero_trace.py` — MO 513971 science
- `inertia_verify.py`, `cascade_data.py` — MO 513954 science
- `sqrt2_deep41.c`, `atlas41_analyze.py`, `certify_run.py` — atlas piece 41
- `render_hero.py`, `render_cascade.py`, `render_atlas41.py`, `artlib.py`
- `verification.md` (certificates), `mo_drafts.md` (post-ready answer/comment),
  `ideas.md` (the 6-idea sheet), `story.md`
