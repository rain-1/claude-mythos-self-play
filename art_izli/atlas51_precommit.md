# Atlas 51 precommit — window [3.0, 3.1]e12 (HALF-width window: 1e11)

Written BEFORE reading the alarm/record analysis (only the live OCC stream's
first lines were glimpsed mid-run, showing routine l=4 g=24 traffic).

Rules of judgment (inherited from 48–50, adjusted to 1e11 width):
1. **Gates are theorems.** Any 4-run class outside {94,103,110,119} mod 144,
   any fence start ≢ 94 (mod 144), any sextet failing (≡±1 mod 8 ∧ ≢0 mod 3),
   or any l=4 g=25 start ≢ 0 (mod 25) ⇒ treat as ENGINE BUG until proven.
2. **ch-25 fences:** E ≈ 0.47 per 1e11 (0.93 per 2e11 band). Grading:
   N25 ≤ 1 long-run band (count is the report); N25 ≥ 3 in THIS half-window
   alone = warm streak continuation (piece 50 left streak N=3 over 2e11 —
   this window decides whether the streak grades to "warm epoch" (N25 ≥ 2
   here) or regresses (0–1)).
3. **ch-23:** REPORT COUNT ONLY (rule set after the 08-30/08-31 whipsaw); no
   verdict wording unless |N23 − E| > 3σ with E scaled to 1e11 (E ≈ 3·0.5·?
   — piece 50 saw N23=6 per 2e11 ⇒ E~3 here, σ~√3).
4. **N24:** expectation ~19–20 per 1e11; report only.
5. **Sextets:** drought stands at 3 consecutive 2e11 windows (P≈0.26).
   0 sextets here extends drought to ~3.5 windows (P≈0.2, still weather);
   ≥1 ends it.
6. **New-channel fences (14/17):** report any; 4th-ever would be notable but
   is expected eventually (both channels opened by 08-31's finds).
7. |S| checkpoint must match density stream within 1e-6 relative.
