# Verification ledger — run 2026-08-22 (`art_40a8/`)

Every number in the triptych and notes, with how it was checked.

## Hero: THE SKY OF OPEN DOORS (MO 514531, x⁴+y⁴+z⁴ = 51 t⁴)

1. **Fiber reduction.** A rational point with z/t = p/q (lowest terms) is
   equivalent to a rational point on the plane quartic C_M: X⁴+Y⁴ = M Z⁴,
   M = 51q⁴−p⁴ (x = X/(qZ), y = Y/(qZ)). Genus 3; quotients: the conic
   r²+s² = M u² and the genus-1 quartic D_M: a² = M − v⁴ (a = X²/Z², v=Y/Z).
   A point of C_M is exactly a point of D_M with a ∈ ℚ². (Algebraic identity,
   checked symbolically on the N=17 control below.)
2. **Local criteria for D_M** (fiberlib.py): closed forms derived this run —
   only p ≡ 3 (mod 4) and p = 2 can obstruct; exact congruence conditions on
   v_p(M) and the unit part. VALIDATED against a brute-force ℚ_p solver
   (bounded Hensel lifting, both charts) for p ∈ {2,3,7,11,19,23} × all
   M < 400: **0 mismatches** (`validate_local`).
3. **Census** (fibers_stage1.py): 7,495 fibers q ≤ 96 → 6,607 conic-dead,
   25 local-dead (deeper wall), 863 locally-alive survivors. Internal
   consistency: every conic-dead fiber is also D-dead at the same prime
   (checked exhaustively; 0 exceptions).
4. **Jacobian.** ellfromeqn(a²−(M−v⁴)) = [0,0,0,4M,0], i.e. y² = x³+4Mx —
   PARI-verified identity (M=17 shown; formula exact for all M).
5. **Ranks** (stage2.gp): PARI ellrank on all 863 survivors: 806 rank exactly
   1, 28 in [1,3], 3 rank 2, 7 rank 3, 9 rank 0, 10 undecided [0,2]. 0 errors.
6. **Root numbers** (rootno.gp): ellrootno exact: **841/863 survivors have
   w = −1**; the 22 exceptions are precisely the fibers with even rank
   verdicts {(0,0),(0,2),(2,2)}. For N=17: 348/1449 have w = −1. (BSD parity
   used only as commentary; ranks above are unconditional descent bounds.)
7. **Point sweeps** (deep3.gp): hyperellratpoints on every survivor to
   x-height 2·10⁵; the 14 highest-priority favorites (all 7 rank-3, the
   rank-2s, and the lowest near-miss rank-1s) to 5·10⁶; fiber (1,1) (M=50)
   separately to 4·10⁷. Square-a test on every point found:
   **zero squares** → no solution of 51 arises on any of these fibers at
   these heights. Near-miss anatomy of M=50: points (±1,±7),
   (±7199/2797, ±19345207/2797²) — 19345207 is not a square (4398²=19342404,
   4399²=19351201).
8. **Positive control** (end-to-end): the N=17 fiber M = 17·583⁴−758⁴:
   pipeline reports rank 2 with explicit generators AND finds the point
   (v,a) = (765, 1066²), a square ⇒ reconstructs Tomita's
   758⁴+765⁴+1066⁴ = 17·583⁴ exactly.
9. **Family curves** (famhunt.c): A⁴+N·B⁴ = 51C⁴ for all 28 primitive
   N = u⁴+v⁴, u≤v≤9, searched to C = 200,000 with double residue masks +
   exact 4th-root: **0 hits** (so no solution of 51 has two variables in
   ratio u:v with u,v ≤ 9 below that height).
10. **Direct sweep sanity** (nhunt.cpp): N=51, T=24,000 meet-in-the-middle:
    0 primitive hits (consistent with the poster's reported 1.6·10⁷ search).

## Piece 3: THE FOUR GUESTS (x⁴+y⁴+z⁴ = 17 t⁴)

11. **Engine certificate**: nhunt (meet-in-the-middle over value windows,
    z the largest variable, exact __int128/uint64 arithmetic, gcd-primitivity)
    re-found ALL FOUR known nontrivial solutions (t = 583, 1011, 1259, 2353)
    plus the trivial (0,1,2;1) — and nothing else — in 3 minutes at T=32,000.
12. **New bound**: T = 60,000 sweep (nhuntw): only those five primitives.
    Largest previously known t was 2,353, so the "no fifth solution" bound
    is pushed ×25 beyond the known record (variables to ~122,000).
13. 17-sky census: 5,692 fibers q ≤ 96 → 4,119 conic-dead, 124 local-dead,
    1,449 survivors (25.5% vs 51's 11.5%); ranks: 534 rank 0, 353 [0,2],
    338 rank 1, 208 rank 2, 6 rank 3, 1 rank 4, 3 alarm-timeouts.
    Square landings found by the sweep at exactly the fibers of the trivial
    solution (p/q = 0/1, 1/1, 2/1) — as they must be.

## Piece 2: THE GATE OF TWENTY-FIVE (atlas 42, ℤ[√2] runs)

14. **Gate theorem** (hand-derived, then machine-checked two ways):
    l=5 gap-25 run starts satisfy n ≡ 14 (mod 16) and n ≡ 4 (mod 9), i.e.
    n ≡ 94 (mod 144). Machine check 1 (gatecheck.py): survivor classes at
    modulus 2⁸·3⁵·5⁴ are exactly mod16={14}, mod9={4} (and l=3: {0,7,14,15}
    × {0,2,4}; l=4: {7,14} × {2,4}). Machine check 2 (dump25.c, real data
    0..8·10⁹): 135 sampled l=3 starts + both l=4 starts — **0 violations**
    (l=4 starts 2138837006 ≡ 14 mod 16 ≡ 2 mod 9; 3541787687 ≡ 7 mod 16).
15. **Closure certificates**: for g ∈ {3,5,6,10,11,12,13,19,20,21,22} every
    residue class mod 256 dies (finite check) ⇒ **no l=5 run with those gaps
    exists at any depth** — independently re-proving the atlas's "only 25
    silent" and adding 19–22 which had l=4 runs but were not yet certified.
16. **Gate-width surprise**: total gate density for g=25 is 0.00340 vs
    0.00081 for g=17 (both from the same finite computation) — the silent
    channel has the WIDER gate; its rarity lives in the gap-width tail
    — l=3 runs with gap 25 occur at 6.1·10⁻⁷ per unit depth in
    [2e10, 1.6e11] against 6.8·10⁻⁶ for gap 17: 11× rarer despite the wider
    door, because three consecutive gaps of 25 sit deep in the tail of the
    gap law at member density ≈ 0.138.
17. **Prediction discipline**: prediction25.md committed while the hunt was
    at ~50% coverage: E[fence in [1.6e11,4e11)] ≈ 0.22–0.43,
    P(silent) ≈ 65–80%, median fence 6·10¹¹–1.2·10¹². Verdict recorded in
    the final piece and README after the hunt exited.
18. Hunt rig integrity: hunt25.c = the memory branch's hunt17.c (piece 41)
    unmodified except the filename; segmented full-factorization sieve,
    ordered consumption, O(1) run state; in-window "FIRST" alarms for
    channels 14/17/23/24 fired at 1.604e11/1.624e11/1.722e11/2.176e11,
    confirming live coverage of the new window.

## Addendum (found while waiting for the hunts)

19. **Parity law, exact**: on all 2,312 survivor curves of both surfaces,
    w(y²=x³+4Mx) = ε(v₂(M), M′ mod 16)·(−1)^k with
    k = #{p≡3 (4): v_p(M)≡2 (4)} and ε the finite table in
    notes_514531.md — **0 mismatches** (hypothesis tested after the ε-free
    version already gave 863/863 on the 51-surface). The 51-walls force the
    ε=−1 cell {(1,1),(1,9)}; the 22 even-parity fibers are exactly those
    with k odd.
20. Pass C run standalone: hyperellratpoints(50−x⁴, 4·10⁷) — see
    passC log in the repo (points unchanged from H=10⁵: the (1,7) and
    (7199/2797, …) rungs only; no square).
