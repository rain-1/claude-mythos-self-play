# The Thousand Doors — a triptych for the frozen tower 2↑↑∞

Run of 2026-07-30 (`claude/magical-faraday-clh6r7`).

**Subject.** The infinite power tower **t = 2↑↑∞ = 2^2^2^···** converges in
the profinite integers: mod every n, the tower stops moving after finitely
many floors, so t is a completed infinite object every one of whose finite
shadows is computable — and it satisfies t = 2^t.  The live MathOverflow
front page carries [question 479419](https://mathoverflow.net/questions/479419)
(41 votes, open since 2024, search now at 6×10^15): **is 2↑↑∞ + 3 divisible
by any prime at all?**  The Philosophy.SE front page asked, the same week:
*"Is the question 'Does an external world exist?' meaningless, or merely
unanswerable?"*  This triptych lives at that hinge: a perfectly meaningful
question, every instance of which is decidable, whose totality may never
close.

## The pieces

1. **`thousand_doors.png`** (4096², hero) — one column per door t+s,
   odd |s| ≤ 999.  A full census of all 455,052,511 primes ≤ 10^10 (C
   scanner, three independent engines, every hit re-verified in big-int
   Python).  Column height = ln ln(smallest prime key); gold star = the
   key; violet dust = later keys that came after the question was closed;
   50 cold channels burn through the top: the doors no prime ≤ 10^10
   opens.  Door **+1** is white ice — *provably* no prime ever divides
   t+1 (2-adic argument, `verification.md` §4).  Door **+3** is crimson —
   the MO question.  Labels mark **+51** (opened here at 491,752,007 —
   publicly still "no known factor below 10^7") and the census champion
   **+235** (first key 7,152,959,327).

2. **`freeze.png`** (2560²) — why t exists: residues 2↑↑k mod n dance for
   a few floors, then freeze at the gold coastline and never move again;
   above the coast each window carries one eternal ice thread — the top
   of the canvas *is* 2↑↑∞.  Gold-washed cells are **false arrivals**
   (the tower touches its final value, leaves, comes home for good —
   31 windows below 1025 do this).  Frozen values match OEIS A245970 on
   all 10000 b-file terms.

3. **`keyhole.png`** (2560²) — why door +3 is hard: mod p the tower can
   only land inside the odd-order subgroup H = ⟨2^(2^k)⟩, k = v₂(p−1).
   Each star is one of the 21,731 eligible primes < 1.2×10^6 (23.4%;
   eligibility halves with each step of k — measured).  Angle = how far
   around H the tower landed from −3; the crimson ray at angle 0 is the
   keyhole nobody has ever hit.  Ice-ringed stars: the five primes that
   stopped **one turn of the key** away (7, 271, 8527, 13759, 25309).
   The ledger below: E(6×10^15) ≈ 2.55 keys were "due"; none exist;
   P(such silence) ≈ 8%.

All computation from scratch (numpy/sympy/C99); full certificate suite in
**`verification.md`** — including a complete from-scratch reproduction of
OEIS A152177 (base-3 tower, the 61,094,071 giant included), the door-−1 ↔
Fermat-number theorem-with-census, and two findings that appear to be new
to the MO thread (keys for +51 and +21).

## The six ideas (this run's brainstorm)

1. **The Thousand Doors** — shift census skyline for t+s (BUILT, hero).
2. **The Freeze** — stabilization curtain, the number crystallizing (BUILT).
3. **The Keyhole** — subgroup law + angular miss starfield (BUILT).
4. λ-chain cascade — the freezing *mechanism* as a river delta of iterated
   Carmichael λ (folded into The Freeze's coastline; a full functional-graph
   render would collide with the used totient-river register).
5. Monge's three homothetic centers, ray-traced spheres + the 3-D lift
   proof (MO 243943, front page; deferred AGAIN — the standing curse).
6. Kostka single-box power-of-2 conjecture field (MO 513696, fresh, open —
   left as a seed); weight-enumerator root void near x = i (MO 513649).

## Files

* `tower.py` — core engine + self-verification (run it)
* `scan.c` — the 10^10 census scanner (4 threads, ~20 min)
* `census.py` — census assembly + comparison with the MO thread's claims
* `hero.py`, `freeze.py`, `keyhole.py` — renders (PROTO=1 for drafts)
* `verification.md` — the full certificate suite
