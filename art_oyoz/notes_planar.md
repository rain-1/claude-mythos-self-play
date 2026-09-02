# The tide of four primes — MO 409058, worked to the integer

**Question (MO 409058, 12 pts):** for every N, are the n ≤ N whose *proper divisors* form a
planar divisibility graph more numerous than those that don't?  The accepted answer says no
(almost all n have ≥ 4 distinct prime factors ⇒ a hypercube ⇒ non-planar), but nobody said
*when* the majority flips.  It is an integer, and here it is.

## Convention
The poster's own list of non-planar n ≤ 1000 (via Freddy Barrera / SAGE) is reproduced with
**0 mismatches** only under the reading *proper divisors = all d | n with d < n, including 1*
(`planar_sig.py`; excluding 1 gives 125 mismatches).  n = 1 (empty graph) is counted planar.

## Planarity depends only on the exponent signature
`networkx.check_planarity` on representatives with small primes, all signatures with ≤ 4
primes and exponents ≤ 5:

    PLANAR       : p, p², p³, p⁴, pq, p²q, p³q, pqr
    minimal NON-PLANAR (up-set generators): p⁵, p²q², p⁴q, p²qr, pqrs

(p⁵: the divisors 1,p,…,p⁴ are a K₅; pqrs: the 3-cube of divisors of pqr plus … ; etc.)

## Exact counting
    P(N) = 1 + π(N) + π(√N) + π(∛N) + π(⁴√N)
         + Σ_{p≤√N} [π(N/p) − π(p)]              (pq)
         + Σ_p [π(N/p²) − [p³ ≤ N]]              (p²q)
         + Σ_p [π(N/p³) − [p⁴ ≤ N]]              (p³q)
         + Σ_{p<q, pq² < N} [π(N/(pq)) − π(q)]   (pqr)

Every argument is of the form ⌊N/m⌋, so one Lucy_Hedgehog table (all π(⌊N/k⌋), O(N^{3/4}))
serves the whole formula (`planar_race.py`).  Cross-checked against a brute-force signature
sieve at N = 100, 10³, 5·10³, 2·10⁴, 10⁵: exact agreement.

| N | planar P(N) | share |
|---|---|---|
| 10⁴ | 6,740 | 0.674 |
| 10⁶ | 556,857 | 0.557 |
| 10⁷ | 5,154,947 | 0.515 |
| 10⁸ | 48,107,702 | 0.481 |
| 10⁹ | 451,844,526 | 0.452 |
| 10¹⁰ | 4,266,430,301 | 0.427 |
| 10¹¹ | (tide_data.json) | 0.40 |

## The crossing, integer by integer
D(N) = #planar − #non-planar steps by ±1 per integer.  A segmented signature sieve over
[22,468,750, 53,875,000) (`planar_window.py`, self-tested against the Lucy counts) gives:

* **first tie**              D(N) = 0 at **N = 26,855,026**
* **first non-planar lead**  D(N) < 0 at **N = 26,855,313**
* **11 lead changes** (sign changes of D) between 26,855,313 and 26,855,493
* **last N with planar strictly ahead: N = 26,855,491** (27 short planar excursions after
  the first crossing, the longest 39 integers, max height 5)

## Certificate that the lead never returns (up to the bound reached)
Because |D(N+1) − D(N)| = 1, if D(N_k) < 0 and N_{k+1} − N_k < |D(N_k)| then D < 0 on
[N_k, N_{k+1}].  Chained Lucy checkpoints (each step 0.9·|D|) from the window's end:
see `planar_window.log` / `planar_window.json` for the bound reached (target 10¹²).
So: **non-planar is strictly ahead at every N from 26,855,492 up to the certified bound.**

## Asymptotics and a conjecture
Landau: #{n ≤ N : ω(n) ≤ 3} ~ N (log log N)² / (2 log N) → share → 0, extremely slowly
(0.40 at 10¹¹; the formula's leading term alone is far too small at these heights — the
secondary terms of the Sathe–Selberg expansion dominate for many more decades).

**Conjecture.** D(N) < 0 for every N ≥ 26,855,492; equivalently, 26,855,491 is the last
integer at which planar-divisor numbers are in the majority.  Certified computationally to
the bound above; a full proof needs explicit (effective) upper bounds for π₂, π₃ and the
p²q, p³q counts beyond 10¹² — the explicit Landau-type bounds in the literature should close
it, since the share is already 0.40 and decreasing.

Files: `planar_sig.py` (classification), `planar_race.py` (exact counts), `planar_window.py`
(crossing + certificate), `tide_data.py` (strata for the chart), `render_tide.py`.
