# AP-obstruction atlas, piece 40 — ℤ[√2]: THE OPEN CHANNELS

S = { n : v_p(n) even for every prime p ≡ 3, 5 (mod 8) } (absolute norms of ℤ[√2]).
Piece 39 found the l=5 equal-gap-run gap set {1,2,4,7,8,9,15,16,18} below 4×10⁹ and
noted g = 14, 17 as "admissible but unseen — two open channels". This piece asks:
**why are they silent, and when do they first speak?**

## 1. The census, 8× deeper

`sqrt2_deep.c`: unified segmented full-factorization sieve (per segment, divide out
all primes ≤ √X from a residual array; the leftover cofactor is 1 or a single large
prime — a p·q leftover with p, q > √X would exceed X). Certificates:
- |S|(4×10⁹) = 601,376,078 (piece 39: 601,376,078) — EXACT MATCH (from `capcount`).
- |S|(3.2×10¹⁰) = 4,588,527,208, density 0.1434 (down from 0.1503 at 4×10⁹ — the
  Landau-type C/√log n thinning).
- l=5 first occurrences below 4e9 reproduce piece 39 exactly (574/4892/... per gap).
- Sliding-window counts W5 per gap at 4×10⁹ from the independent `capcount.c` pass
  sum to 58,590 = piece 39's count EXACTLY, per-gap identical
  (40629/9723/772/1499/4785/1064/104/13/1).
- Global-count confirmation of the gap-scaling theorem: C5(14)/C5(2) = 1.020,
  C5(17)/C5(1) = 1.0004, C5(23)/C5(1) = 0.999, C5(7)/C5(1) = 1.008.

## 2. The singular series — the discovery

R(g) = exact relative local density of the 5-post pattern (2-adic bracket mod 2^22,
which CLOSES to 6 decimals; odd bad primes p ∤ g, p > 5 by the closed form we
proved: joint density = 1 − 5/(p+1); numeric brackets for p = 3, 5 and p | g):

    g : 1      2      4      7      8      9      14     15     16     17     18     24
    R : 0.1128 0.0564 0.0282 0.1128 0.9161 0.9145 0.0564 4.329  1.360  0.1128 0.4573 7.216

**R(14) = R(2) and R(17) = R(1) — exactly**, and this is a THEOREM, not numerology:

> **Gap-scaling invariance.** R(u·g) = R(g) for every odd u ≡ ±1 (mod 8) all of
> whose prime factors are good (≡ ±1 mod 8). *Proof:* n ↦ u·n is a
> measure-preserving bijection of ℤ₂ and of ℤ_p for every bad p (u is a unit
> there), it maps the gap-g pattern onto the gap-ug pattern, and it preserves
> the S-condition at 2 because the allowed odd parts {±1 mod 8} form a subgroup
> containing u's odd part. ∎

14 = 7·2 with 7 good, 17 = 17·1 with 17 good — so the silent channels inherit
their local densities from g = 2 and g = 1 verbatim. (9 = 3² is NOT such a u —
3 is bad — which is why R(9) = 0.914 ≠ R(1); the numerics confirm both sides of
the theorem.) The tower does not disfavor the silent channels at all. What it does is
favor their NEIGHBORS: R(15)/R(14) = 77, R(16)/R(14) = 24, R(18)/R(17) = 4. The
gaps that were found first below 4×10⁹ (15, 16, 18) are the local giants; 14 and 17
are runts in a rich neighborhood, paying the same emptiness cost.

2-adic admissibility for l=5, g ≤ 26: open = {1,2,4,7,8,9,14,15,16,17,18,23,24,25};
frozen = the rest. So there are FIVE silent open channels ≤ 26: near 14, 17 and far
23, 24, 25.

## 3. The model and its verdict

W5(g) = C5(g) · q(g): C5 = number of 5-term g-APs wholly in S (exact, census);
q(g) = probability the 4 inter-post windows contain no member (fit
ln q = a − b(g−1) + c·[g odd] on the nine speaking gaps):

    ln q = -0.125 - 0.6863(g-1) + 0.324[g odd]   (9 gaps, residuals <= 0.8;
    q spans 1 -> 6e-6 across g = 1..18 — each unit of gap costs a factor ~2 of
    solitude; odd gaps are slightly cheaper per unit)

Predictions at 4×10⁹: W5(14) ≈ 2.6, W5(17) ≈ 0.84 (observed 0/0 — a mild 7%
Poisson slip for 14, unremarkable for 17). First fences expected at
X ≈ 1.5×10⁹ (g=14, i.e. "overdue") and X ≈ 4.7×10⁹ (g=17).

**Deep-census verdict (3.2×10¹⁰):** CHANNEL 14 SPOKE. First l=5, g=14 fence at
n = 5,341,738,436 — only 1.34× past the old shoreline — and 20 maximal runs below
3.2×10¹⁰. Witness independently factor-certified (all five posts in S, all four
windows empty, flanking gaps 18 and 6):
  5341738436 = 2²·17²·4620881,  5341738450 = 2·5²·106834769,
  5341738464 = 2⁵·3²·31·41·14593,  5341738478 = 2·2670869239,
  5341738492 = 2²·1335434623.
**Channel 17 keeps its silence** through 3.2×10¹⁰ (as do the far channels 23, 24,
25). Channel 18 grew from 1 run to 2. l = 6: still ZERO (theorem 24 | g stands).
The atlas records its first *predicted-then-heard* channel: the model put ~21-23
fences below 3.2×10¹⁰ for g=14 (scaling the 4×10⁹ prediction by the observed
growth), and the census found 20 — agreement within Poisson error. **But the same
calibration puts E[W5(17)] ≈ 5-6 below 3.2×10¹⁰, and the census found NONE:
P(silence) < 1%. Channel 17's quiet is no longer luck — it is the next riddle.**
Something beyond the (2,3,5,...)-local model suppresses odd-gap-17 solitude, or
the emptiness fit's parity term hides structure; piece 41's opening question.

## 4. Thread A updates

- The good-step law for d = 2 stays 2-adic (piece 39); the new content is
  *quantitative*: the tower's surviving densities, not just admissibility, are the
  observable — and equal local densities can hide 100× differences in when a
  configuration first appears, because the neighborhood competes for the same
  emptiness.
- l=6: still ZERO below 3.2×10¹⁰ ([L6CHECK]); theorem 24 | g stands; iid estimate
  of the first l=6 fence (>10¹³) unchallenged.
- Next: piece 41 candidates — first l=5 fence at g=14/17 if the deep verdict left
  them open (segmented targeted hunt is cheap: only n ≡ [phases] survive);
  ℤ[√−2] AP record past 10 terms; restate cross-term principle for −11, −19.
