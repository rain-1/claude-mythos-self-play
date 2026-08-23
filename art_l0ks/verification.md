# Verification ledger — art_l0ks (2026-08-23) "THE SHAPE OF THE ANSWER"

Theme seed: Philosophy.SE front page (live): "Should symmetric problems have
symmetric solutions?" — answered three ways. MO seeds: 514552 (live), plus the
Atlas relay (channel 25).

## I. The Crowns of Crooked Trees (hero, 4096²) — Steiner minimal trees of regular n-gons

Engine: `steiner.py` — chain DP over contiguous full components (valid structure
for cocircular terminals: non-crossing SMT edges + all terminals on the hull),
full component over s consecutive vertices optimized over all Catalan(s−2)
planar full topologies, Weiszfeld iteration + BFGS polish (gtol 1e-12).

Certificates:
- n=3: DP = 3.000000000 = exact Fermat value 3 (circumradius 1). ✓
- n=4: DP = 3.8637033052 = √2(1+√3) exactly (3.863703305156...). ✓
- Independent check `steiner.py validate` + `val8.py`: brute-force enumeration
  over ALL unrooted binary topologies on all leaf labelings ((2n−5)!! =
  15/105/945/10395 for n=5/6/7/8), each optimized: matches DP to ≤2e-9 for
  n=5,6,7, and for n=8 full-enum = DP = rim = 5.3575680531 exactly. ✓
- n=6: DP = 5.000000000 = perimeter − edge exactly; full-topology optima
  degenerate to the same value from above (5.0000000019). ✓

Census result (`steiner_census.json`, n=3..40, circumradius 1):
- n=3: SMT/rim = 0.8660254 — one Steiner point, FULL D₃ symmetry kept (orbit 1)
- n=4: 0.9106836 — two Steiner points, D₂ ⊂ D₄ (orbit 2, the two H-trees)
- n=5: 0.9727890 — three Steiner points, mirror only (orbit 5)
- n≥6: SMT = rim = (n−1)·2sin(π/n) exactly (every n tested to 40); orbit n
  (choice of dropped edge). The interior is abandoned from SIX onward.
Caveat stated honestly: for n≥8 the census relies on the convex-position DP
(component size cap 8; raising the cap changes nothing); the n≤7 cases carry
the independent full-enumeration certificate. Du–Hwang–Weng (1987) proved
SMT = P − e for n ≥ 13; our data says the same answer already wins at n = 6,
consistent with their conjecture for 6 ≤ n ≤ 12.

## II. The Beautiful Wrong Answer (2560²) — Malfatti vs greedy

- Equilateral closed forms verified against the numeric solvers to 1e-10:
  greedy (unit inradius) = π(1 + 2/9) = 3.8397243544;
  Malfatti = 3π((3−√3)/2)² = 3.7880424651; ratio 1.0136434292 (greedy +1.364%).
- Malfatti circles: Newton solve on the three-radius tangency system, residual
  < 1e-11 accepted, < 1e-8 required for the field; continuation sweep for
  sliver shapes (44,850 grid cells solved over the moduli wedge A≤B≤C).
- Zalgaller–Los inequality (greedy ≥ Malfatti) observed at ALL 44,850 cells;
  ZERO violations. Gap ranges 1.45% (grid, near-equilateral; exact equilateral
  limit 1.364%) to 99.1% (extreme slivers).
- The minimum of the gap over shape space sits AT the equilateral corner: the
  symmetric answer is least wrong where the problem is most symmetric.
- Phase structure: greedy's third circle switches between "corner at second-
  smallest angle" and "second circle nested in sharpest corner"; the boundary
  thread is drawn from the 300×300 field (binary_dilation edge).

## III. The Sea That Forgives the Edges (2560²) — MO 514552 (live, open)

Question asked (paraphrase): why does A(n,⌊n/2⌋) − √2 ~ (−1)ⁿ C/√n with
C ≈ 0.05222?

Mechanism established this run (semi-rigorous, numerically certified):
1. Boundary layer: fixed diagonals converge to B_0=1, B_j = g(1/B_{j−1}) with
   g(u) = (u+√(u²+4))/2. B_1 = φ EXACTLY (0.0 defect in float; matches poster's
   Fibonacci diagonal). Empirical diagonals at n=32768 match B_j to ≤ 4.4e-16.
   Linearization: B_j − √2 decays with ratio −1/3 (measured −0.333333 at j=11).
2. Gauge d(n,k) = (−1)ⁿ(A(n,k) − √2): interior dynamics is plain averaging
   d' = (d_{k−1}+d_k)/2 + O(d²) — the alternation is g'(√2) = −1 for the
   equal-parent involution x ↦ 2/x.
3. Mass: M(n) = Σ_k d(n,k) has alternating bounded increments; the
   parity-averaged mass converges: M̄ = 0.0654503304268973 (stable to ~1e-12
   between n=131072 and n=262144). Parity split M_odd − M_even = 1.0140041,
   equal to the layer mass −4Σ_j(B_j−√2) = 1.0140074 to 3.3e-6 (first-order
   layer theory; the residual is the O(layer²) correction, as expected).
4. LAW (new): A(n,k) − √2 ≈ (−1)ⁿ M̄ 2⁻ⁿ C(n,k) in the bulk. Profile check at
   n=32768: matches the Gaussian at center offsets 0, .25√n, .5√n, √n, 2√n —
   including the 9.69e-8 tail — to ~4 significant digits.
5. Consequence: C = √(2/π)·M̄ = 0.05222180814...
   Measured C by √2-Richardson of center deviations through n=262144:
   R2 sequence → 0.0522215923 with remaining increments halving
   (geometric limit ≈ 0.05222181). Agreement to ~7 digits. ✓
6. Closed-form hunt for M̄: PSLQ vs {1, √2, π, φ, log2, e, √π, γ, layer sum}
   at 11-digit honesty: nothing. Near-miss noted: π/48 = 0.0654498469 differs
   by 4.8e-7 — excluded by 5 orders of magnitude of measurement precision.

Scripts: `tri_science.py` (mechanism tests), `tri_precise.py` (M̄, C to depth),
`tri_checks.py` (layer sums, PSLQ).

## Atlas piece 43 — The Door Past the Gate (2560²)

- NEW FENCE: first maximal l=5 gap-25 run in the ℤ[√2] norm set starts at
  n = 458,171,603,806. Discovered by the resumed hunt rig (hunt25.c, chunk
  [4.0e11, 5.6e11)); the certified-exhaustive segmented scan makes it the
  global first given pieces 40-42's coverage of [0, 4.0e11).
- Independent verification (`verify_fence.py`, sympy full factorization):
  n     = 2·7²·41·114029767      (all odd primes ≡ ±1 mod 8 or even power) ✓
  n+25  = prime (≡ 7 mod 8) ✓
  n+50  = 2⁴·3²·3181747249 ✓
  n+75  = prime (≡ 1 mod 8) ✓
  n+100 = 2·17·47·286715647 ✓
  n−25 and n+125 both ∤∈ S (single factor 3) — run is maximal, l=5 exactly. ✓
- Gate theorem check: n ≡ 94 (mod 144), n ≡ 14 (mod 16), n ≡ 4 (mod 9) —
  exactly the unique residue class piece 42's machine-certified gate demands. ✓
- Boundary straddler scan: the single mod-144 candidate in [4e11−124, 4e11)
  fails membership — no run straddles the old certification frontier. ✓
- Model verdict: piece 42's pre-committed prediction gave P(silent through
  4e11) ≈ 65–80% (it was silent), 10%-quantile 1.2–2.4e11, median 6e11–1.2e12.
  The fence at 4.58e11 sits between the 10%-quantile and the median: an
  early-but-in-model arrival. The drift law extended again:
  r34(gap 25) = 321/127085 = 2.53e-3 in [4,5.6e11) (was 1.78/1.98/2.49e-3).
- Census chunk 1: |S ∩ [4.0e11, 5.6e11)| = 21,283,123,095;
  gap-25 maximal runs: l=3: 127,085 · l=4: 321 · l=5: 1.
- Relay continues: chunks [5.6e11, 7.2e11) and [7.2e11, 8.8e11) (see
  hunt_rungap_*.txt when finished).
