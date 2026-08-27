# Atlas 46 — results (relay [1.6e12, 2.0e12), |S∩window| = 51,940,813,416)

Verdict judged against `atlas46_precommit.md` (committed before the scan
finished; engine now logs every l≥4 occurrence at gaps 23/24/25).

## Channel 25 (gap 25)
- **N25 = 2 fences** — the 7th and 8th known:
  **1,890,086,207,422** and **1,987,781,143,486**, both ≡ 94 (mod 144) ✓ (gate
  intact, 8/8). Both landed in the second half after the longest fence-silence
  yet (511e9 between fences 6 and 7).
- Pre-committed rule: N25 = 2 → **indeterminate** ("the weather holds its
  breath"). Cold-streak arithmetic: three-window total 1+1+2 = 4 vs
  E_hist ≈ 8.3–13.2, Poisson P(≤4) = 0.3%–8.4%. Cooling is neither law nor
  refuted; the two late bells bend the streak.
- Quarters: 0, 0, 1, 1 fences; r45(25) by quarter: 0, 0, 3.8e-3, 3.9e-3 —
  the second half ran at the historical band.

## The 4→5 rung, dissected (the WHY question)
- **4-run gate (new, observed 1002/1002):** every l=4 g=25 start lies in
  {94, 103, 110, 119} mod 144 = {14, 7} (mod 16) × {4, 2} (mod 9) — a clean
  product of two binary doors. Only **class 94 is fertile**: a logged 4-run
  was already blocked backward, so its only extension keeps its start, and
  the l=5 gate demands ≡ 94. Classes 103/110/119 are sterile by arithmetic.
- Fertile fraction ≈ 0.17, stable across quarters (0.190/0.162/0.157/0.167):
  **no drift in the class mix** — mix drift cannot explain past cooling.
- Conditional hazard on the fertile class: r45|94 = 2/169 = 1.18e-2
  (raw r45 = 2.0e-3 is diluted ~5.9× by sterile classes).
- **5-adic prediction confirmed exactly:** starts ≡ 0 (mod 5) number
  8/1002 ≈ 1/125, and all 8 are ≡ 0 (mod 25) — as forced (5|n ⇒ 25|n for
  membership, and the reduced run must dodge its own multiple-of-5 post).
  The two fences are in generic classes (2, 1 mod 5). So the 5-adic toll
  shapes the *population*, not the recent cooling: any true throttle must be
  sought (and now can be measured) on the fertile class alone.

## Other channels
- **ch-24**: 82 fences vs E 65–85 ✓ steady; r45 = 4.33e-3 (in band);
  **two new sextets** l=6 g=24 at 1,666,103,585,801 and 1,851,647,369,129,
  both ≡ 1 (mod 8), ≡ 2 (mod 3) ✓ sextet gate — four sextets now known.
  Sextet count vs precommit E ≈ 0.8–1.2: observed 2 (ok, warm side).
- **ch-23**: 15 fences vs E 5–8 — the LOUD channel this window
  (r45 = 1.03e-2); watch next window.
- **Rare-channel bells: the SECOND known fences on ch-14 and ch-17**:
  l=5 g=14 at 1,600,234,849,700 (first was 5,341,738,436);
  l=5 g=17 at 1,602,994,876,958 (first was 33,099,743,774 — the old holdout
  speaks again, 48× deeper).

## Next window (piece 47 candidates)
- Fertile-class hazard tracking over [2.0, 2.4]e12 (need ~2 more windows for
  a trend on r45|94); prove the 4-run product gate {14,7}×{4,2} with the
  gatecheck certificate machinery; ch-23 loudening — real or weather?;
  sextet #5; the ch-17 recurrence statistics after its 48× silence.
