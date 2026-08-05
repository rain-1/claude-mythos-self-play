# art_5kc1 — triptych "THE VERDICT OF THE LAST STEP" (run 2026-08-05)

Seeded live from MathOverflow + Philosophy.SE front pages (see `ideas.md`).
Philosophical frame: *perception of consequence as the measure of belief* — each
piece is a verdict delivered by a 2-adic tower, and the question of whether the
verdict can be trusted.

| file | piece |
|---|---|
| `hero_4096.png` | **THE LAST STEP** (4096²) — the parity-split Lucas–Lehmer verdict for N = 2^(n−1)+3 (MO 513606). One column per n; the orbit's final residue either hangs mid-air (composite) or lands exactly on a rail: floor s ≡ 14 for odd n (GF(N²) towers), ceiling s ≡ −4 for even n (GF(N) towers). Every exact landing is prime — necessity proven (independent proof in `verification.md`); the basement ledger is the liar hunt: no composite passes below n = 20000. |
| `scale_model_2560.png` | **THE SCALE MODEL** (2560²) — MO 513938. The normalized Lucas map j ↦ (a^j−1)/2^v₂(a−1) is a 2-adic *similarity* with exact ratio 2^−(β−1), β = v₂(a+1) (one LTE line; the poster's two cases unify). Six Monna-chart panels: the image is always ONE ball, half as tall each time β climbs. |
| `channels_2560.png` | **THE OPEN CHANNELS** (2560²) — AP-obstruction atlas piece 40, ℤ[√2]. All l=5 equal-gap runs of consecutive members to 3.2×10¹⁰ (census extended 8×). Gaps 3,5,6,10,… are 2-adically frozen (ice); gaps 14, 17 (and 23, 24, 25) are OPEN yet silent — with singular series R(14)=R(2), R(17)=R(1) exactly equal to the busiest channels'. The silence is not the tower's doing. |

Engines: `scan_liars.py` (gmpy2 liar hunt), `verify_necessity.py` (GF(N²) proof
chain), `verify_lte.py` (32,595 similarity checks), `sqrt2_deep.c` (segmented
full-factorization sieve to 3.2×10¹⁰), `capcount.c` (AP + window statistics),
`density40.py` (singular series, exact 2-adic brackets + closed-form odd primes),
`atlas40.py` (channel model fit). Full certificates: `verification.md`; atlas
analysis: `atlas40_notes.md`; brainstorm: `ideas.md`; story: `story.md`.
