# Atlas 50 — pre-committed expectations (written BEFORE launching the scan)

Engine: `hunt50.c` = hunt49/48/47 line unchanged (copied verbatim from
`art_e7az/hunt49.c`). Window: **[2.8e12, 3.0e12)** (width 2e11, the
established half-window unit; 3 OMP threads, 1 core reserved for art
renders per the oversubscription lesson). Expectations scaled from the
completed pieces 48 (5e11) and 49 (2e11).

## Population predictions (falsifiable gates)
1. |S ∩ window| ≈ 25.7e9 ± 0.4e9 (piece-49 measured 25.78e9 per 2e11;
   1/√log decline is negligible at this depth).
2. **4-run gate (THEOREM, piece 47)**: every l=4 g=25 start ≡ {94,103,110,119}
   (mod 144). A violation is a disproof of a machine-certified theorem —
   i.e. a bug hunt, not weather.
3. **Fence gate**: every l=5 g=25 start ≡ 94 (mod 144) (13/13 all-time).
4. Fertile fraction (class 94 among l=4 g=25) = 0.17 ± 0.04
   (last three completed windows: 0.160, 0.170, 0.160).
5. 5-adic depletion: l=4 g=25 starts ≡ 0 (mod 5) ≈ 1/125 of them, and all
   such ≡ 0 (mod 25).
6. Sextet gate (l=6 g=24): starts ≡ ±1 (mod 8) and ≢ 0 (mod 3).

## Expected counts (per 2e11)
- l=4 g=25 ≈ 520–650 (piece 49: 599); fertile ≈ 85–115.
- **ch-25 fences**: all-time 13 in 2.8e12 → E ≈ 0.93. N25 = 0–2 is the
  long-run band; N25 = 0 modal.
- **ch-24 fences**: E ≈ 45 (band 34–56; piece 49 measured 49).
- **ch-24 sextets**: E ≈ 0.4–0.8. The drought is now 2 completed windows
  (7e11 since sextet #5); at E≈0.15/1e11 that is P(0)≈0.35 — a third
  dry window would put the drought at ~2σ, REPORTABLE as a note only.
- **ch-23 fences**: piece 49 reversed the "cold shift" to weather. Base
  weather rate ≈ 0.5–0.7 per 1e11 → E ≈ 1.0–1.4 for this window.

## Pre-committed verdict rules
- **ch-25**: N25 = 0–2 → long-run band, report the count only. N25 ≥ 3 →
  warm streak note. Every fence heard must be ≡ 94 (mod 144); gate 3 overrides.
- **r45|94 5th point**: report next to 1.18e-2 / 2.4e-2 / 1.22e-2 / 1.04e-2.
  Five points: fit a trend ONLY if monotone over the last four; else
  "scatter, no trend" stands.
- **ch-23 re-grade (4th window)**: N23 = 0–1 → say "quiet, consistent with
  either reading; still weather until a run of lows". N23 = 2–4 → base
  weather CONFIRMED, cold-shift chapter closed. N23 ≥ 5 → warm swing —
  the channel is simply noisy at this width; widen next window.
- **Sextet #6**: report if seen (ends the drought); 0 sextets → report the
  drought length in windows with its Poisson P-value, nothing more.
- **Any violation of gates 2,3,5,6 overrides everything** and leads the
  piece (gate 2 = certified theorem → treat as engine bug until proven).
- If the relay is cut short: judge on the completed prefix, scale E by the
  scanned fraction, and say the fraction in the verdict line.
