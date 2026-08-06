# AP-obstruction atlas, piece 41 — ℤ[√2]: THE DEBT OF CHANNEL SEVENTEEN

S = { n : v_p(n) even for every prime p ≡ 3, 5 (mod 8) } (absolute norms of ℤ[√2]).
Piece 40 (3.2×10¹⁰): channel 14 spoke at 5,341,738,436 exactly as the model
predicted (20 fences vs ~21-23 expected); channel 17 stayed silent against
E ≈ 5-6 expected — P(silence) < 1%. This piece pushes the census to **10¹¹**
(3.125×) to make channel 17 either speak or become a certified anomaly.

## 1. The census

`sqrt2_deep41.c` = piece 40's segmented full-factorization sieve + word-level
scan pass (~50× faster serial scan). Re-certification before launch:
|S|(4×10⁹) = 601,376,078 — matches pieces 39/40 EXACTLY; l=5 per-gap run
tables at 4×10⁹ byte-identical to piece 39's (`cert_4e9_rungap.txt`).

RESULTS (filled after census):
- |S|(10¹¹) = (TBD), density (TBD)
- per-gap l=5 counts: see `atlas41_data.json` / the piece caption
- channel 17: (TBD)
- channels 23, 24, 25: (TBD)
- l=6: (TBD; theorem 24 | g + iid estimate >10¹³ predict none)

## 2. New: the l=4 singular series (R4) and the gap-scaling theorem at l=4

`R4_values.txt` (rig: piece 40's `density40.py`, l=4, K=22): the theorem
R(u·g) = R(g) for good-u (all prime factors ≡ ±1 mod 8) holds numerically at
l=4 to all computed digits:

    R4(7) = R4(17) = R4(23) = R4(1) = 0.31505
    R4(14) = R4(2) = 0.15752
    R4(21) = R4(3) = 1.2602

and the bad-square case R4(25) = 0.7687 ≠ R4(1) (5 is bad; 25 = 5² is not a
good-u multiple) — both sides of the theorem confirmed on fresh values.
Local giants at l=4: R4(24) = 5.20, R4(15) = 3.02, R4(16) = 1.91, R4(8) = 1.30.

## 3. Verdict and interpretation

(TBD after census: either the first g=17 fence — factor-certified via
`certify_run.py` — or the debt ledger E ≈ (TBD), P(silence) ≈ (TBD).)
