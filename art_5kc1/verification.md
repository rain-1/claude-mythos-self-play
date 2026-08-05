# Verification — run 2026-08-05 (`art_5kc1/`), triptych "THE VERDICT OF THE LAST STEP"

## Piece 1 — THE LAST STEP (MO 513606, hero 4096²)

**Setting.** N = 2^(n−1) + 3, Lucas–Lehmer orbit s(0) = 4, s(k+1) = s(k)² − 2 mod N.
The poster conjectured: N prime ⟹ s(n−2) ≡ 14 (n odd) / −4 (n even) (mod N)
(their form: s(n−2)/2 ≡ 7 resp. −2). Necessity was answered on MO (score 6, via
Chebyshev identities) while this run was underway; we verified it independently
with a cleaner proof and then attacked the **sufficiency** question, which remains
open there: *can a composite N ever pass?* (If not, this is a genuine primality
test for the family, as the poster hoped.)

**Independent proof of necessity (ours).** Write ω = 2 + √3, so s(k) = ω^(2^k) +
ω^(−2^k). Let τ = (√6 + √2)/2; then τ² = ω. Let m = 2^(n−2) and let N be prime.
For n ≥ 4, N ≡ 3 (mod 8) so (2|N) = −1; and N ≡ 2^(n−1) mod 3 gives:

- **n odd:** N ≡ 19 (mod 24): (3|N) = −1, (6|N) = +1. In GF(N²), Frobenius fixes
  √6 and negates √2, so τ^N = (√6−√2)/2 = 1/τ, i.e. **ω^((N+1)/2) = τ^(N+1) = 1**.
  Since (N+1)/2 = m + 2: ω^m = ω^(−2), hence s(n−2) = ω² + ω^(−2) = **14**.
- **n even:** N ≡ 11 (mod 24): (3|N) = +1, (6|N) = −1. Now ω ∈ GF(N) and Frobenius
  negates both √2 and √6, so τ^N = −τ and **ω^((N−1)/2) = τ^(N−1) = −1**. Since
  (N−1)/2 = m + 1: ω^m = −ω^(−1), hence s(n−2) = −(ω + ω^(−1)) = **−4**.

Verified (`verify_necessity.py`): the whole chain — the mod-24 splits, both Euler
statements, ω^m itself, and the endpoint — holds for **all 16 primes with n ≤ 800**
(n−1 ∈ OEIS A057732 exactly), with GF(N²) arithmetic written from scratch.

**Why sufficiency is genuinely at risk (the honest part).** In the classic
Lucas–Lehmer test the target is 0, which forces ω^(2^(p−1)) = −1 and hence a full
2-power order — that is what makes the converse provable. Here the target is 14 ≠ 0:
passing only forces, at each prime p | N, ω^m ≡ ω^(±2) — i.e. ord_p(ω) divides
2^(n−2) ∓ 2 = 2·(2^(n−3) ∓ 1), whose 2-part is 2. **No largeness of ord_p(ω) follows**,
so the standard order argument cannot rule out composite passers ("liars"), and
different prime factors may even choose different signs. The question is a real one.

**The scan** (`scan_liars.py`, gmpy2, 4 processes): for every n in [3, 20000]
compute s(n−2) mod N ((n−2) modular squarings) and compare with the target; check
primality by BPSW. Tripwires: prime-fails-test (necessity breach — never fired);
composite-passes (liar — see result in `liars_final.txt` header and story.md).
Result at time of rendering: **no liar for any n ≤ 20000** — every exact landing is
prime, every prime lands exactly. (Extension beyond 20000 noted in the file if the
background pass advanced further by push time.)

**OEIS cross-validation.** The scan's passers/primes match the fetched b-file of
A057732 (2^k + 3 prime) EXACTLY over the whole range — including the terms 17187,
17220, 17934 and the *absence* of any term between 8739 and 17187 (a genuinely
empty stretch of ~8.4k exponents; `check_a057732.py`, `b057732.txt`). This also
corrected a garbled from-memory tail of the sequence during the run — the
computation, not the recollection, was right.

**BONUS FINDING — the restart composites.** Ranking composites by relative
distance |s − target|/N exposed 11 spectacular "near-misses" (relative distance
down to 10^−4200): n = 77, 221, 426, 441, 462, 7482, 8466, 9642, 10626, 14229,
18102. For every one, the final residue is EXACTLY an early integer term of the
pure Lucas sequence — s(3) = 37634, s(4) = 1416317954, or s(7) — because the
orbit mod N is periodic and returns to its seed: we verified the ring congruence
**ω^(2^(n−2)) = ω^(2^j) (mod N)** in (ℤ/N)[√3] for each (j ∈ {3, 4, 7}), i.e.
ord_N(ω) | 2^j·(2^(n−2−j) − 1). The n ≡ 6 (mod 12) cases all restart to s(4) and
all have 35 | N. This is precisely the anatomy a LIAR would need — a restart
with j = 1 (odd n, s(1) = 14) or the signed variant for even n; the observed
restart spectrum stays at j ≥ 3. *Whether j ≤ 2 restarts are excluded for
N = 2^(n−1)+3 is an open sub-question — a proof would be a partial sufficiency
theorem.* The 11 restarts are the brightest ticks in the hero's ledger.

**Conjecture (this run's).** The parity-split test is a genuine primality test
for N = 2^(n−1)+3: no composite passes. Evidence: all n ≤ 20000 (extension
running); the only structured approaches to the target are restarts, observed
only at j ≥ 3.

**Near-miss data.** For each composite the final residue's circular distance
|s − target|/N is recorded; the minimum over n ≤ 20000 is reported in the ledger
strip of the hero (tick height = −log₁₀ distance). Under the uniform heuristic
P(liar at n) ≈ 2^−(n−1), the expected number of liars with n ≥ 4 is ≈ 2^−2; the
scan's silence is consistent with — but far beyond — that heuristic, since
structured composites (Carmichael-style conspiracies) are the real worry and none
appear.

**Hero accuracy.** Each column n = 3..1027 is the true orbit (recomputed
independently of the scan; endpoints agree), y = s/N; the two rails are the true
target heights 14/N → 0⁺ and (N−4)/N → 1⁻. Gold/ice stars = the 17 primes ≤ 1027.

## Piece 2 — THE SCALE MODEL (MO 513938, 2560²)

Claim under test (poster's, two cases): for odd a, α = v₂(a−1), β = v₂(a+1),
q_j = (a^j − 1)/2^α on odd j:  v₂(q_x − q_y) = v₂(x−y) if α > β, and
v₂(x−y) + β − 1 if β > α.

**Unified law (one LTE line).** q_x − q_y = a^y·(a^(x−y) − 1)/2^α with x − y even,
and LTE gives v₂(a^M − 1) = α + β + v₂(M) − 1 for even M. Hence **always**

    v₂(q_x − q_y) = v₂(x − y) + (β − 1),

both of the poster's cases at once (for odd a exactly one of α, β equals 1).
Equivalently |q_x − q_y|₂ = 2^−(β−1) |x−y|₂: the map is a **2-adic similarity**
with exact ratio 2^−(β−1). Verified: 32,595 exact checks over 90+ moduli a
(exhaustive small + random to 10^12, exponents to 10^6), **0 failures**
(`verify_lte.py`).

**Corollaries (verified in the same run).**
- Image = **one ball**: {u ≡ q₁ (mod 2^β)}, so exactly 2^(R−β) residues mod 2^R
  occur, each equally often (the odd j form a ball of radius 1/2; a similarity
  of ratio 2^(1−β) scales it to radius 2^−β). All 26 (a, R) table rows
  in `verify_lte.py` output confirm count, equidistribution, and ball address.
- For odd p | a − 1 the p-normalized map is an **isometry** (LTE, odd case):
  v_p(Q_x − Q_y) = v_p(x − y); 400/400 random checks. The only prime that can
  rescale is 2, and the ratio is exactly β − 1 halvings.

**Is it known?** Yes in substance: it is the standard lifting-the-exponent
valuation of a^M − 1 (classical, Birkhoff–Vandiver era). The clean packaging —
"the normalized map is a similarity of ratio 2^(1−β), an isometry at every odd
prime" — we did not find stated anywhere, and it is what the picture draws.

**Render accuracy.** Each panel's point set is the exact graph (Monna/bit-reversal
coordinates, j over 2^16 odd residues, q mod 2^30); 200 random pair-checks of the
law run inside the renderer per panel (assertions, 1200 total). The drawn strip
boundaries are the theorem's ball, not a fit to the points.

## Piece 3 — THE OPEN CHANNELS (Atlas piece 40, ℤ[√2], 2560²)

(quantitative results filled from `capcount_out.txt`, `deep_rungap.txt`,
`deep_records.txt` — see `atlas40_notes.md` for the full analysis.)

- New unified segmented full-factorization sieve (`sqrt2_deep.c`) re-derives the
  piece-39 census as certificate (|S|(4×10⁹) = 601,376,078 expected) and extends
  the country 8× to 3.2×10¹⁰.
- Singular series R(g) (`density40.py`): exact 2-adic bracket mod 2^22 (lo = up to
  6 decimals for all g used) × closed-form odd-prime factors [proved: for bad
  p ∤ g, p > 5, joint density = 1 − 5/(p+1)] × numeric brackets for p = 3, 5 and
  p | g. Headline: **R(14) = R(2)/1 exactly = 0.0564 and R(17) = R(1) = 0.1128**
  — the 2-adic tower gives 14 and 17 the *same* local density as the most common
  gaps; but their neighbors are giants (R(15) = 4.33, R(16) = 1.36, R(18) = 0.457),
  which is why 15, 16, 18 appear below 4×10⁹ and 14, 17 do not.
- Model: E[W₅(g)] ≈ C₅(g) × q(g), C₅ = plain-AP counts (exact, from census),
  q = probability the four inter-post windows are empty (fit from observed gaps).
  Prediction for the first g = 14 and g = 17 fences and the census verdict at
  3.2×10¹⁰: see `atlas40_notes.md`.
