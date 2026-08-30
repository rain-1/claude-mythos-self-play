# Atlas 49 — pre-committed expectations (written BEFORE reading any scan reports)

Engine: `hunt49.c` = hunt48/47 line unchanged. Window: **[2.6e12, 2.8e12)**
(width 2e11 = 0.5× the historical 4e11 unit — sized to the CPU budget of a
run that also carries two art engines; a *completed* half-window with its
exact run table beats a streamed fragment of a grand one). All expectations
scaled ×0.4 from piece 48's completed 5e11 window.

## Population predictions (falsifiable gates)
1. |S ∩ window| ≈ 25.7e9 ± 0.4e9 (piece-48 rate 12.88e9/1e11, slow 1/√log decline).
2. **4-run gate (THEOREM, piece 47)**: every l=4 g=25 start ≡ {94,103,110,119}
   (mod 144). A violation is a *disproof of a machine-certified theorem* —
   i.e. a bug hunt, not weather.
3. **Fence gate**: every l=5 g=25 start ≡ 94 (mod 144) (12/12 all-time).
4. Fertile fraction (class 94 among l=4 g=25) = 0.17 ± 0.04 (0.160, 0.170 in
   the last two windows).
5. 5-adic depletion: l=4 g=25 starts ≡ 0 (mod 5) ≈ 1/125 of them, and all
   such ≡ 0 (mod 25).
6. Sextet gate (l=6 g=24): starts ≡ ±1 (mod 8) and ≢ 0 (mod 3).

## Expected counts (per 2e11)
- l=4 g=25 ≈ 520–640 (piece-48 rate 1444/5e11); fertile ≈ 85–115.
- **ch-25 fences**: all-time 12 in 2.6e12 → E ≈ 0.92. N25 = 0 is the modal
  outcome (P≈0.4) and NOT reportable as a cold shift at this width.
- **ch-24 fences**: E ≈ 42 (band 34–52).
- **ch-24 sextets**: E ≈ 0.4–0.8 (5 known in 2.6e12, recent rate higher).
- **ch-23 fences**: cold-shift rate (confirmed 08-28/29) → E ≈ 0.8–2;
  pre-cold base rate would give 2.4–4.

## Pre-committed verdict rules
- **ch-25**: N25 = 0–2 → long-run band, nothing to report but the count.
  N25 ≥ 3 → warm streak worth a note (≥3σ over E≈0.92). Every fence heard
  must be ≡ 94 (mod 144) — gate 3 overrides.
- **fertile-hazard 4th point**: report r45|94 next to 1.18e-2 / 2.4e-2 /
  1.22e-2 (pieces 46/47/48); with four points fit a trend ONLY if monotone,
  else report scatter honestly.
- **ch-23**: N23 ≤ 2 → cold shift persists (third consecutive low window,
  strengthen wording from "confirmed" to "settled"). N23 = 3–5 → back to
  base weather (cold shift was two windows of weather; say so). N23 ≥ 6 →
  reheat, flag for next run.
- **Any violation of gates 2,3,5,6 overrides everything** and leads the
  piece (gate 2 = certified theorem → treat as engine bug until proven).
- Sextet #6: report if seen; 0 sextets is the modal outcome and silent.
- If the relay is cut short: judge on the completed prefix, scale E by the
  scanned fraction, and say the fraction in the verdict line.
