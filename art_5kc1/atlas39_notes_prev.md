# AP-obstruction atlas, piece 39 — Z[√2]: THE PICKET FENCE

S = { n : v_p(n) even for every prime p ≡ 3, 5 (mod 8) } — the absolute norms of Z[√2]
(units have norm ±1, so ± is free; 2 is ramified; p ≡ ±1 (mod 8) split).

**Census to 4×10⁹** (`sqrt2_sieve.c`, `sqrt2_scan2.c`, ~2.6 min, OpenMP):
|S| = 601,376,078. Odd members ≡ ±1 (mod 8); classes 3, 5 (mod 8) empty (proved:
odd part of a member is ≡ ±1 mod 8). Density at 4e9 ≈ 0.150 — the DENSEST country
in the atlas so far, twice the two-squares density.

**Equal-gap runs of consecutive members** (maximal, l = #terms):
- l=3: 29,231,485 runs; l=4: 3,172,415; l=5: 58,590; **l=6: ZERO below 4×10⁹.**
- First runs: l=3 at 7,8,9 (g=1); l=4 at 223..226 (g=1); l=5 at 574..578 (g=1)
  — all witnesses re-verified by sympy factorization, and the following element
  (10, 227, 579) verified absent each time.
- Gap-1 runs cap at 5 (mod-8 loom: 6 consecutive residues must hit {3,5}).
- l=5 gaps observed: {1,2,4,7,8,9,15,16,18}. 2-adic-tower admissible classes
  (exhaustive checker `tower_check.py`, K=16 bits): {1,2,4,7,8,9,14,15,16,17,18}
  — g = 14, 17 are admissible but unseen: two open channels.

**THEOREM (l=6 needs 24 | g).** A 6-term equal-gap AP inside S requires g ≡ 0 (mod 24).
  - p = 3 (≡ 3 mod 8, inert): if 3 ∤ g, any 6-term AP hits 0 mod 3 twice at spacing 3;
    both hits need v₃ even, but they differ by 3g with v₃(3g) = 1 — contradiction. So 3 | g.
  - 2-adic tower: exhaustive check over n mod 2¹⁶ for every g ≤ 100 leaves only
    g ≡ 0 (mod 24). Example of the tower in action: g = 3 survives mod 8 (phase 6),
    but the phase forks n ≡ 14, 30 (mod 32) and both die (odd parts hit 3, 5 mod 8
    at the terms n+6 resp. n+12) — matching the census zero for (l=5, g=3).
  The suppression is NOT a finite-level congruence artifact you can wash out:
  each added term pushes the run one level deeper into the tower of the ramified prime.

**The inversion.** Under an iid-gap null (observed gap histogram), l=6 fences expected
below 4×10⁹: ~7,600 (even conditioned on the 58,590 achieved l=5 runs, ~13% should
extend). Observed: 0. Meanwhile plain 6-term APs with g = 24 (other members allowed
between the posts) start at n = 1: (1, 25, 49, 73, 97, 121); an 8-term at 1753.
What is scarce is not arithmetic structure but SOLITUDE: the country is so dense
(the run-extension ratios at g=24 go 8541 → 32 → 0 for l = 3 → 4 → 5) that six
equally-spaced members with nothing between should first occur past ~10¹³.
Piece 38's country (Z[√−11]) was too sparse for long fences; this one is too crowded.
The atlas gains its first obstruction-by-abundance.

Good-step law update (Thread A): for d = 2 the ramified prime is 2 and goodness is
NOT decided at one level (mod 8) — it is decided in Z₂, layer by layer (the l=6
theorem needed mod 32; deeper runs need deeper levels). The "unified good-step law"
should be restated 2-adically for the ramified prime 2.
