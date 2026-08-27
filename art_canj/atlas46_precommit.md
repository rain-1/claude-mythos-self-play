# Atlas 46 — pre-committed expectations for relay [1.6e12, 2.0e12)

Written BEFORE reading the relay's rungap/alarm outputs (the engine was
launched with l>=4 OCC logging; a few early l=4 lines were glimpsed at
launch-sanity time; no counts, no quintets seen).

## Channel 25 (gap 25) quintets ("fences", start ≡ 94 mod 144 by the gate)
- Historical (windows [4e11,8.8e11) + [8.8,1.2e12)): 3 + 2 fences in 8e11,
  and r45(25) historically 3–5e-3.  Scaled to this 4e11 window with the
  slowly-rising 4-run population: **E_hist ≈ 2.5–4.5** (Poisson).
- The last two windows ran cold: [1.2,1.6e12) had 1 vs E≈2.5–4.5, with the
  measured suppression localized at the 4→5 rung (r45(25) = 1.0e-3).
  Under "cooling is law" (r45 stays ≈1.0e-3): **E_cool ≈ 0.8–1.2**.
- Decision rule (pre-committed):
  - N25 ≤ 1  → third consecutive cold window: cooling is now the law until
    refuted; cumulative 3-window count vs E≈7.5–13.5 (P(≤3 | 9) ≈ 2.1%).
  - N25 ∈ {2,3} → indeterminate; verdict "the weather holds its breath".
  - N25 ≥ 4  → cooling refuted; the two cold windows were weather after all.

## The 4→5 rung, 5-adic hypothesis (the WHY question of this piece)
Structure: a ch-25 run n, n+25, ... lives over one residue n mod 5.
If 5 | n then membership forces n ≡ 0 (mod 25), and then posts are
25(j+k) with j..j+4 covering ALL residues mod 5 — the 5th post pays an
extra 5-adic toll (the j+k ≡ 0 (mod 5) post needs ≡ 0 (mod 25)).
All six known fences have start ≢ 0 (mod 5) (1,3,1,2,1,1 mod 5).
- Pre-committed test: classify every l=4 start by s mod 5 (and mod 25 when
  s ≡ 0 (mod 5)).  If the 4-run population mix is stationary in height and
  overwhelmingly s ≢ 0 (mod 5), then a 5-adic depth-5 obstruction CANNOT
  explain a height-drift in r45(25) — the cooling would have to be either
  fluctuation or a non-local (archimedean / density) effect.
- Prediction under pure singular-series locality: r45(25) within the
  s ≢ 0 (mod 5) class should match the historical 3–5e-3 once the class mix
  is accounted; a genuine drop INSIDE the generic class refutes the 5-adic
  explanation.
- Comparison channel: ch-24 (gap 24, no 5-adic content, r45 ≈ 3.9e-3,
  loudening): E[N24 quintets] ≈ 65–85 this window.

## Sextets (l=6, any gap ≡ 0 mod 24)
Empirical rate 2 per 8e11 → **E ≈ 0.8–1.2** this window; P(≥1) ≈ 55–70%.
Gate: start ≡ ±1 mod 8 and ≢ 0 mod 3 (2-adic + 3-adic certificate, run 08-24).

## Channel 23 (l=5 g=23)
Historical ~6–7 per 4e11 → E ≈ 5–8.
