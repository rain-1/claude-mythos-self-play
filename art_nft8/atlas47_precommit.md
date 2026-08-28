# Atlas 47 — pre-committed expectations (written BEFORE the [2.0e12, 2.4e12) scan reports)

Engine: `hunt47.c` = hunt46.c unchanged (l≥4 OCC logging at gaps 23/24/25).
Window: [2.0e12, 2.4e12), same width (4e11) as piece 46's window.

## Population predictions (falsifiable gates)
1. |S ∩ window| ≈ 51.3e9 ± 0.5e9 (slow 1/√log n decline from 51.94e9).
2. **4-run gate**: every l=4 g=25 start ≡ {94, 103, 110, 119} (mod 144)
   — the {14,7}(mod 16) × {4,2}(mod 9) product observed 1002/1002 last
   window. THIS window we also aim to PROVE it (2,3-adic certificate).
3. **Fence gate**: every l=5 g=25 start ≡ 94 (mod 144) (8/8 so far).
4. Fertile fraction (class 94 among l=4 g=25) = 0.17 ± 0.03, no drift.
5. 5-adic depletion: l=4 g=25 starts ≡ 0 (mod 5) ≈ 1/125 of the
   population, and every one of them ≡ 0 (mod 25).
6. Sextet gate (l=6 g=24): starts ≡ ±1 (mod 8) and ≢ 0 (mod 3).

## Expected counts (from historical rates)
- l=4 g=25 occurrences ≈ 950–1050 (1002 last window); fertile ≈ 150–200.
- **ch-25 fences**: E[N25] = fertile × r45|94. Historical r45|94 over the
  only measured window = 2/169 = 1.18e-2 → E ≈ 1.8–2.4. Long-run rate
  (8 fences / 1.6e12 since first) gives E ≈ 2.0 per window. Band E = 2.0.
- **ch-24 fences**: E ≈ 65–85 (82 last window).
- **ch-24 sextets**: E ≈ 1–2 (Poisson; 4 known, 2 last window).
- **ch-23 fences**: the decision window. Historical base E ≈ 5–8; last
  window was LOUD at 15.

## Pre-committed verdict rules
- **ch-25**: N25 = 0 → "cold" evidence (P(0 | E=2.0) = 0.135, combined
  with the 4-fence three-window streak → report as *suppression
  strengthening*, still not proof. N25 = 1 → lean-cold indeterminate.
  N25 = 2–4 → IN BAND ("the weather resumed"). N25 ≥ 5 → loudening.
- **fertile-hazard trend**: report r45|94 for this window next to 1.18e-2;
  two windows is still not a trend — say so plainly whatever it shows.
- **ch-23**: N23 ≥ 12 → "loudening is real" (two consecutive ≥2σ highs);
  N23 ≤ 8 → last window's 15 was weather; 9–11 → indeterminate.
- **Any gate violation (rules 2,3,5,6) overrides everything** and becomes
  the lead result (a broken gate = a wrong theorem-in-waiting).
- Sextet #5: report if seen; 0 sextets is unremarkable (P ≈ 0.14–0.37).
