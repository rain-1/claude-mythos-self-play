# Atlas piece 44 — pre-committed model (written BEFORE the scans, 2026-08-24)

## The overlooked landmark (already verified this run)

The 08-23 relay's own ledger contains, unread until today:

    hunt_alarms_400000000000_560000000000.txt:  L6+! l=6 gap=24 start=536462850079

**The first length-6 equal-gap run of consecutive members in the ℤ[√2] atlas.**
Verified independently this run by full factorization of every integer in
[n₀−60, n₀+204]: members at offsets {0,24,48,72,96,120} exactly, consecutive
(no members between posts), flanked by a member at −1 (gap 1) and +133
(gap 13), so the run is maximal at l=6. Gap 24 obeys the piece-39 theorem
l=6 ⇒ 24 | gap. Post factorizations in verification.md.
n₀ = 536,462,850,079 ≡ 7 (mod 8), ≡ 1 (mod 3).

## How lucky was it? (singular series + empirical calibration)

R(l, g=24) by density44.py (K=22): R₃=2.709, R₄=5.198, R₅=7.216, R₆=15.83.
Observed maximal-run counts over the whole relay [4e11, 8.8e11), g=24:
l=3: 2,629,651 · l=4: 18,229 · l=5: 73 (19/27/27 by window) · l=6: 1.

Chain-extension model: r₅₆ = r₄₅ · (R₆/R₅)/(R₅/R₄) = 4.00e-3 · 2.193/1.388
= 6.33e-3 ⇒ **E[l=6 over the relay] ≈ 73 × 6.33e-3 ≈ 0.46** ⇒ P(≥1) ≈ 37%.
The sextet came roughly twice ahead of expectation — lucky, not miraculous.

## Pre-committed predictions for this run's two scans

1. **Recovery scan [8.30e11, 8.80e11)** (every-occurrence logging): must find
   EXACTLY 2 quintets of gap 25 — the known fence 830,595,732,286 plus the
   one unlogged occurrence, both ≡ 94 (mod 144) (gate theorem, piece 42).
   Any other count contradicts the 08-23 rungap ledger.

2. **Continuation [8.8e11, 1.2e12)**, W = 4e11 (amended from 1.2e11 before
   launch, after timing the rig at ~31 min per 1.6e11 window):
   - ch-25 quintets: relay rate 4/4.8e11 rising (1/1/2 by window);
     **E ≈ 3.3–4.2, P(silent) ≈ 2–4%.** Every fence must be ≡ 94 mod 144.
   - l=6 g=24 sextets: E ≈ 60.8 × 6.33e-3 ≈ **0.38** ⇒ P(≥1) ≈ 32%.
   - l=6 g=48: zero l=5 g=48 seen in the whole relay ⇒ E ≪ 0.01; silence
     expected.
   - drift check: r₃₄(25) has risen 2.53/2.59/2.73e-3 by window; predict
     r₃₄(25) ∈ [2.7, 3.0]e-3 in the continuation window.
