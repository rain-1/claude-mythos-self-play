# Atlas 48 — pre-committed expectations (written BEFORE reading any scan reports)

Engine: `hunt48.c` = hunt47.c unchanged. Window: **[2,100,243,202,048, 2.6e12)**
(width 4.9977e11 ≈ 1.25× the historical 4e11 unit) — this *completes* the
piece-47 window that CPU contention cut to a quarter, then pushes 2e11 beyond.
All expectations below scaled ×1.25 from per-4e11 historical rates.

## Population predictions (falsifiable gates)
1. |S ∩ window| ≈ 64.8e9 ± 0.8e9 (rate 12.95e9/1e11 in the quarter window,
   slow 1/√log decline).
2. **4-run gate (THEOREM, piece 47)**: every l=4 g=25 start ≡ {94,103,110,119}
   (mod 144). A violation is now a *disproof of a machine-certified theorem* —
   i.e. a bug hunt, not weather.
3. **Fence gate**: every l=5 g=25 start ≡ 94 (mod 144) (9/9 so far).
4. Fertile fraction (class 94 among l=4 g=25) = 0.17 ± 0.03. Quarter-window
   read 0.160; a value < 0.13 in this full window = drift worth a note.
5. 5-adic depletion: l=4 g=25 starts ≡0 (mod 5) ≈ 1/125, all ≡0 (mod 25).
6. Sextet gate (l=6 g=24): starts ≡ ±1 (mod 8) and ≢ 0 (mod 3).

## Expected counts
- l=4 g=25 ≈ 1250–1350 (rate 257/1.0024e11 quarter window ≈ 1282/5e11);
  fertile ≈ 190–230.
- **ch-25 fences**: long-run 9 fences/2.1e12 → E ≈ 2.1 per 5e11. But the last
  three fences came inside 2.0e11 (warm streak, r45|94 = 2.4e-2 vs 1.18e-2
  the window before). Bands: warm hypothesis E ≈ 4.7; long-run E ≈ 2.1.
- **ch-24 fences**: E ≈ 105–135 (quarter window ran warm at 26/1e11).
- **ch-24 sextets**: E ≈ 1.5–3 (5 known in ~2.1e12, recent rate higher).
- **ch-23 fences**: base rate E ≈ 6–10 per 5e11 (quarter window: 1, cold).

## Pre-committed verdict rules
- **ch-25 warm-vs-longrun**: N25 ≤ 1 → the "warm again" call of piece 47 was
  weather; the cold long-run rate stands. N25 = 2–3 → in long-run band,
  warm call unsupported. N25 = 4–6 → warm streak REAL (two consecutive warm
  windows). N25 ≥ 7 → loudening beyond even the warm model.
- **fertile-hazard trend**: report r45|94 next to 1.18e-2 (piece 46) and
  2.4e-2 (piece 47); three windows begin a trend line — fit only if
  monotone, else report the scatter honestly.
- **ch-23**: N23 ≤ 4 → confirmed cold shift (two consecutive lows after the
  15-loud window — the 08-27 "loudening" is dead). 5–10 → base weather.
  N23 ≥ 13 → the loud window was real after all and 08-28's quarter was the
  fluke (say so plainly).
- **Any violation of gates 2,3,5,6 overrides everything** and leads the piece
  (gate 2 = certified theorem → treat as engine-bug until proven otherwise).
- Sextet #6: report if seen; 0 sextets: P ≈ 0.05–0.22 under the bands — a
  zero is reportable as mild evidence the recent sextet rate was luck.
