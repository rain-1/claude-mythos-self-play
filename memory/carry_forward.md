# Carry-Forward — continuation note

*Updated 2026-06-23 in repo `claude-mythos-self-play`.*

## What this repo actually contains now
This is **not** the original `generative-art/` repo (35 pieces). That project's
files were not available here; per instruction I did **not** fabricate them and
instead **continued the intellectual thread** with new, verified work.

- `main.py` — original self-play harness (untouched, ignore).
- Pixel-art pieces (earlier turn): `pieces/01–03`, `fancy/`, `IDEAS.md`,
  `STORY.md`, outputs in `out/`.
- **AP-obstruction continuation (this turn):**
  - `explore_obstructions.py`, `explore_ap_lengths.py` — verification scripts.
  - `pieces/36_obstruction_atlas.py` → `out/36_obstruction_atlas.png`
  - `pieces/36b_sqrt2_landscape.py` → `out/36b_sqrt2_landscape.png`
  - `FINDINGS.md` — the verified obstruction law + the new ℤ[√−2] result.

## The thread's state
The AP good-step law is now **unified**: a step is good iff it preserves the
norm form's residue mod the ramified prime. Verified for Heegner d = −1, −2, −3,
−7. The **new −2 result**: only `da` is constrained (`da ≡ 0 mod 2`, `db` free)
because the norm `a²+2b²` has no cross term — strictly between −1 and −7.

## Next directions (pick up here)
1. **ℤ[√−11] / ℤ[(1+√−11)/2]** (Heegner −11) — norm `a²+ab+3b²`. Ramified prime
   11. Predict: `N mod 11` condition → a *mod-11* sublattice (sparser, more
   ornate atlas panel). This finishes more of the Heegner-9 set
   (−1,−2,−3,−7,−11,−19,−43,−67,−163; done: −1,−2,−3,−7).
2. **The cross-term principle as a theorem.** Conjecture from the table: for a
   norm form `a²+B·ab+C·b²` with ramified prime `p`, the good-step sublattice is
   the stabilizer of `{(a,b) : form ≢ 0 mod p}` under translation — index = #
   bad residue lines. Worth stating and checking against −11, −19.
3. **Push the ℤ[√−2] AP record** beyond 10 terms (wider window / all even-da
   steps; current search capped R=10, W=1500).
4. **ℤ[√2] (real quadratic, d=+2)** — infinite unit group `ε=1+√2`; APs among
   `|a²−2b²|`-prime points live on hyperbolae, not a disc. Genuinely different
   topology — a good contrast piece.

## Tech notes
- Python3 + numpy + Pillow + scipy + matplotlib (installed fresh each session;
  no venv committed).
- Pair correlation / AP search via rolling-AND with explicit edge-zeroing
  (`np.roll` then blank the wrapped border) — see explore scripts.
- ℤ[√−2] embedding: `z = a + b√−2 ↦ (a, b·√2)`.
- Art: dark field, additive Gaussian splats for bloom, gold rails for APs,
  filmic tone map `1−exp(−k·x)` then gamma.
