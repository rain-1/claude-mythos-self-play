# Verification — "The Thousand Doors" triptych

Subject: **t = 2↑↑∞ = 2^2^2^···**, the frozen tower, as an element of the
profinite integers **Ẑ**.  For every modulus n the sequence 2↑↑k mod n is
eventually constant, so t is well defined; it satisfies **t = 2^t** in Ẑ.
Live seed: [MO 479419] "Is 2↑↑∞ + 3 divisible by a prime number?"
(41 votes, open; search extended to 6×10^15 as of 2026-07-30, no factor).
Philosophy.SE front-page frame: "Is the question meaningless, or merely
unanswerable?" — every finite shadow of t+3 is decidable; the full
question may never close.

## 1. Engines (three independent implementations)

* **A. CRT/λ-chain** (`tower.py: T(a,n)`): split n = 2^e·m (or general
  a-part), t ≡ 0 mod 2^e (v₂(2↑↑k) = 2↑↑(k−1) → ∞), and
  t mod m = a^(t mod λ(m)) mod m for gcd(a,m)=1 — pure congruence, since
  ord_m(a) | λ(m).  Recursion bottoms out at λ-chain length ≤ O(log n).
* **B. hzy's totient algorithm** (the MO poster's code, reimplemented
  verbatim: `towermod(a,m) = a^(φ(m)+towermod(a,φ(m))) mod m`).
* **C. C scanner** (`scan.c`): same chain re-derived in C99 with an SPF
  sieve to 10^9, segmented sieve to 10^10, deterministic Miller–Rabin,
  memoized t mod n for n < 2^25.

Checks passed:
* A vs **OEIS A245970** (2↑↑∞ mod n): **10000/10000 b-file terms exact**.
* A vs B: 600 random moduli ≤ 10^6, bases 2 and 3 — all agree.
* A vs **literal towers**: 2↑↑5 = 2^65536 computed as an exact 19,729-digit
  integer, reduced mod 200 random n — agrees; freeze heights ≤ 5
  literal-checked.
* A vs C: every hit and three completeness windows (below).

## 2. The scan (deep computation)

All primes 2000 < p ≤ 10^10: r = t mod p computed by the chain;
door hit recorded when r ≤ 999 (odd) or p − r ≤ 999 (odd).
Primes p ≤ 2000 handled exhaustively in Python (a small prime can open
many doors).

* **Prime count: 455,052,208 = π(10^10) − π(2000) exactly** (455,052,511 − 303).
* **All 2001 recorded hits (p > 2000) verified** individually with engines
  A *and* B in big-int Python: p prime and p | t + s.  0 failures.
* **Completeness windows** (recompute every hit from scratch in Python,
  compare sets): [10^6, 1.2×10^6] — 24/24 hits agree;
  [2×10^9, 2×10^9+2×10^5] — agree (empty); champion window around
  7,152,959,327 — agrees and contains the (+235) hit.
* **Global cross-check p < 10^6**: full census recomputed in Python:
  2393/2393 hits agree exactly — in particular all 50 shut doors are
  honestly shut below 10^6 by two engines.
* **Tripwire**: r = p−1 (which would mean p | t+1) is *provably impossible*
  (§4); the scanner aborts if it ever occurs.  It never did — 455M primes
  double as a live test of the theorem and of the code.
* **Equidistribution**: (t mod p)/p over all 455,052,208 primes,
  8192 bins: χ² = 8308 vs dof 8191 (z ≈ +0.9) — statistically uniform;
  the only structural deviation is a +3.8% excess in the lowest bin
  (t mod p is always a *power of 2* mod p, and tiny landings 1,2,4,…
  are reachable with probability ~1/M each, far above 1/p).
* **v₂(p−1) tally** matches the 2^−k law to 6 decimal places.

## 3. Census results (odd shifts |s| ≤ 999, primes ≤ 10^10)

* **950 of 1000 doors open**; mean keys per door 2.95 (≈ ln ln 10^10 + M).
* **50 doors stay shut through 10^10**:
  +1 (sealed by theorem), +3 (the MO question), −39, −87, +93, +121,
  −129, −173, −183, +183, +193, +253, −297, +315, +345, −353, +367, −377, +391,
  +417, −425, −437, +457, −465, −503, +505, +511, −533, +535, −567, −587,
  −617, +637, −645, +693, −699, +721, +765, −789, +801, −819, −825, +861,
  +867, −875, −909, −927, −935, −959, +963.
  (Naive Mertens average predicts ≈ 24 survivors of 1000; survival is
  convex in the accumulated hazard and small primes deal hazard unevenly
  across residue classes of s — Jensen's inequality explains the excess.)
* **New opening for the MO thread**: hzy's 2024 comment lists +51 among
  shifts with "no known factor below 10^7".  Our scan finds
  **t + 51 ≡ 0 mod 491,752,007** (verified engines A and B).
* **Discrepancy with the same comment**: it also lists **+21**, but
  **t + 21 ≡ 0 mod 2,127,133** — a key *below* 10^7, verified with the
  poster's own algorithm.  (Their list was partial/"…", so possibly a
  transcription slip; −21 opens at 5.)
* 20 doors open only above 10^7 — first-key champions:
  +235 → 7,152,959,327; −333 → 4,523,828,377; +697 → 3,261,427,973;
  +501 → 2,269,660,423; −147 → 2,247,748,249; +723 → 1,254,580,111.
* **Door −1 belongs to the Fermat numbers.**  t ≡ 1 (mod p) is guaranteed
  whenever ord_p(2) is a power of 2 — i.e. exactly when p divides a
  Fermat number F_j = 2^(2^j) + 1.  All 20 census keys of door −1
  (3, 5, 17, 257, 641, 65537, 114689, 274177, 319489, 974849, 2424833,
  6700417, 13631489, 26017793, 45592577, 63766529, 167772161, 825753601,
  1214251009, 6487031809) were individually checked: each has ord = 2^j
  and divides F_0…F_23 accordingly.  A prime with odd-order part M > 1
  could also open door −1 by landing on the identity (probability 1/M);
  expected ≈ 2.5 such coincidences by 10^10 — **none occurred** (its own
  ~8% silence, mirroring door +3).
* Base-4 contrast (from an MO comment): the same door +3 in the base-4
  tower opens at once — 4↑↑∞ + 3 ≡ 0 mod **7** (verified).

## 4. The +1 theorem (why door +1 is ice)

**No prime divides 2↑↑∞ + 1.**  Suppose p | t+1, i.e. 2^x ≡ −1 (mod p)
where x = t mod (p−1).  Then ord_p(2) is even and x ≡ ord/2 (mod ord), so
v₂(x) = v₂(ord) − 1 < v₂(ord) ≤ v₂(p−1).  But t is divisible by every
power of 2 in Ẑ, so x = t mod (p−1) satisfies x ≡ 0 (mod 2^(v₂(p−1))),
i.e. x = 0 or v₂(x) ≥ v₂(p−1).  x = 0 gives 2^0 = 1 ≡ −1, p = 2,
impossible (t is even).  Contradiction.  ∎
(t+1 is therefore a *unit* in Ẑ — an infinite integer with no prime
divisor at all; the scan's 455M primes never once contradicted this.)

## 5. The keyhole law (panel 3 data)

For each prime p: k = v₂(p−1); the frozen exponent x = t mod (p−1)
satisfies 2^k | x, so **t mod p lands inside H = ⟨2^(2^k)⟩**, the cyclic
subgroup of odd order M = oddpart(ord_p(2)).  Door +3 needs −3 ∈ H
*and* the landing to hit it exactly.

Measured on all 92,937 odd primes p < 1.2×10^6 (BSGS discrete logs in H,
every dlog re-verified by exponentiation):
* eligible (−3 ∈ H): 21,731 = **23.38%**; by stratum k = 1,2,3,4,5,6:
  34.9%, 17.7%, 9.0%, 4.2%, 2.3%, 1.2% — the 2^−k halving law, measured.
* **one-turn-off primes** (landing exactly one generator step from −3):
  p = 7, 271, 8527, 13759, 25309.
* smallest angular miss in sample: 6.8×10^−5 of a full turn.
* **Sawin–Goucher ledger**: E(X) = Σ_{p ≤ X eligible} 1/M ≈ ln ln X + C
  with C = −1.046 fitted on the sample tail;
  **E(6×10^15) ≈ 2.55 expected keys, 0 found: P(silence) ≈ e^−2.55 ≈ 7.8%**
  — unusual, not miraculous.

## 6. OEIS A152177 reproduced from scratch (base-3 tower)

"Smallest prime factor of G+n, G any sufficiently large power tower of 3
(e.g. Graham's number)": all 34 terms recomputed by ascending prime scan
with the base-3 chain — including a(4) = **61,094,071** and
a(16) = 147,331, a(26) = 101,117.  (Result: see `a152177.log`;
MATCH: True.)

## 7. Possibly new, MO-comment-ready

1. t + 51 ≡ 0 (mod 491,752,007) — closes one of the six "±100 stubborn
   shifts" from the 2024 comment thread.
2. t + 21 ≡ 0 (mod 2,127,133) — contradicts the comment's list at 10^7.
3. The full ±999 census to 10^10 (50 survivors listed above) — data of
   this shape doesn't appear in the thread or OEIS (only the base-3
   A152177 analogue exists for 0 ≤ n ≤ 33; a base-2 "smallest prime
   factor of 2↑↑∞ + n" sequence appears to be absent).
4. The measured keyhole statistics (23.38% eligibility at 1.2e6; the
   one-turn-off list; E(6e15) ≈ 2.55 with fitted C).
Posting is left as a decision for a future run (per memory-branch policy).

[MO 479419]: https://mathoverflow.net/questions/479419
