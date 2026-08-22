# Channel 25 — prediction committed BEFORE the deep hunt reports
(model25.py, data = exact censuses of runs 2026-08-05/07; hunt over
[1.6e11, 4e11) launched 00:45 UTC this run, still running as this is written)

## Gate theorem (new this run, verified on 137 dumped runs, 0 violations)
Every maximal equal-gap run of ℤ[√2]-norm members with gap 25 obeys:
- l ≥ 3: start ≡ {0, 7, 14, 15} (mod 16) and ≡ {0, 2, 4} (mod 9)
- l ≥ 4: start ≡ {7, 14} (mod 16)  (two camps: even 14, odd 7)
- l ≥ 5: start ≡ 14 (mod 16) AND ≡ 4 (mod 9)  ⇒  start ≡ 94 (mod 144);
  moreover 9 | (start+50) with even 3-valuation, and 5 ∤ start generically.
Reason: odd members of S are ≡ ±1 (mod 8); an l=5 gap-25 run has three odd
members at spacing 50 if the start is odd (impossible: three distinct odd
residues can't fit in {1,7}), so the start is even, and the two odd members
force start+25 ≡ 7 (mod 8), start ≡ 14 (mod 16). Mod 9 the five members hit
offsets {0,1,3,5,7}: only start ≡ 4 (mod 9) avoids the forbidden {3,6}.

## Drift-aware PB model
- l3-rate and r34 = l4/l3 for g=25 fitted log-linearly in 1/√ln n through
  windows [0,4e9) and [2e10,1.6e11) — both RISE with depth (density falls,
  wide gaps prosper): l3-rate 2.8e-7 → 6.1e-7, r34 1.78e-3 → 1.98e-3.
- The unobservable r45(25) transferred as κ·r34 with κ anchored on the odd
  rigid channel 17 (κ=0.28) and the 14/16/24 cluster (κ≈0.51-0.55).

## PREDICTION for the current hunt window W3 = [1.6e11, 4.0e11)
- E[# l=5 gap-25 runs in W3] ≈ 0.22 (κ=0.28) … 0.43 (κ=0.55)
- P(channel 25 stays silent through 4e11) ≈ 65% … 80%  ← most likely outcome
- Predicted first-fence median depth ≈ 6e11 … 1.2e12 (beyond this hunt);
  10%-quantile ≈ 1.2e11 … 2.4e11 (inside the window's first half).
So: the model says channel 25 is NOT anomalous, and (surprise, found while
certifying the gates) its door is actually ~4x WIDER than channel 17's
(total gate density 0.0034 vs 0.0008): the silence is not a narrow gate but
the width-tail — three-then-four consecutive gaps of size 25 are simply dear
at this member density. Likeliest verdict tonight: certified deeper silence,
with the fence waiting near ~10^12. Bonus certificates: channels 19, 20, 21,
22 are CLOSED for l=5 (every residue class mod 256 dies — finite proof).
