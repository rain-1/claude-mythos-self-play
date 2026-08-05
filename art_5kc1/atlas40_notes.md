# AP-obstruction atlas, piece 40 — ℤ[√2]: THE OPEN CHANNELS

S = { n : v_p(n) even for every prime p ≡ 3, 5 (mod 8) } (absolute norms of ℤ[√2]).
Piece 39 found the l=5 equal-gap-run gap set {1,2,4,7,8,9,15,16,18} below 4×10⁹ and
noted g = 14, 17 as "admissible but unseen — two open channels". This piece asks:
**why are they silent, and when do they first speak?**

## 1. The census, 8× deeper

`sqrt2_deep.c`: unified segmented full-factorization sieve (per segment, divide out
all primes ≤ √X from a residual array; the leftover cofactor is 1 or a single large
prime — a p·q leftover with p, q > √X would exceed X). Certificates:
- |S|(4×10⁹) = [CERT4E9] (piece 39: 601,376,078) — [CERTMATCH]
- |S|(3.2×10¹⁰) = [S32], density [DENS32].
- l=5 first occurrences below 4e9 reproduce piece 39 exactly (574/4892/... per gap).
- Sliding-window counts W5 per gap at 4×10⁹ from the independent `capcount.c` pass
  sum to [W5SUM] vs piece 39's 58,590 maximal runs — [W5MATCH].

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

[FITTABLE]

Predictions at 4×10⁹: W5(14) ≈ [P14], W5(17) ≈ [P17] (observed 0 — consistent:
[CONS]). Expected first fence: g=14 near X ≈ [X14], g=17 near X ≈ [X17].

**Deep-census verdict (3.2×10¹⁰):** [VERDICT]

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
