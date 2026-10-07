# Math notes — run 2026-10-07 (IT HAPPENS AGAIN)

## 1. Riemann's function as a closed curve (the hero and the bow-tie)
Duistermaat's complex form φ(t) = Σ_{n≥1} e^{iπn²t}/(iπn²), t ∈ [0,2], so R(t) = Σ sin(πn²t)/n² = π·Re φ(t).
- φ(t+2) = φ(t), so the image is a **closed curve**. φ(0) = −iπ/6 (the tip), φ(1) = +iπ/12 (the top centre).
  t ↦ 2−t gives the mirror image (complex conjugate up to sign), hence the left–right symmetry.
- **Exact sampling by one FFT**: on t = 2k/M, e^{iπn²t} = e^{2πi (n² mod M) k/M}, so φ on the whole grid is
  one inverse FFT of an array with 1/(iπn²) dropped into bin n² mod M (`riemann.py`, n ≤ 3·10⁵, M = 2²⁴).
- **Winding number** of the closed curve: 0 outside, 1 on the big heart, and it climbs by one inside every
  smaller copy — the copies all wind the same way as the whole. On an 8192² grid the field reaches 27 near
  the tiny loops; around φ(1) the nest goes 60+ levels deep in the zoom (`zoomfield.py`).
- Near a rational p/q the curve repeats itself: φ' = θ (the theta series), and θ(p/q+δ) ≈ (G(p,q)/q)·½(−iδ)^{−1/2}
  (G a quadratic Gauss sum), so φ(p/q+δ) − φ(p/q) ≈ (G/q)·√δ·(phase): a copy of the cusp at φ(0) shrunk by
  |G|/q ~ q^{−1/2}. At t = 1 the copies accumulate from both sides into the bow-tie.

## 2. MO 515776 — the law of Q_x(h) = (R(x+h) − R(x)) / h^{3/4}
All on the exact FFT grid (M = 2²², x uniform on the grid, every x used):

| m (h = 2m/M) | h | Var Q | E Q⁴ | P(|Q|>4)·4⁴ | P(|Q|>8)·8⁴ | P(|Q|>16)·16⁴ |
|---|---|---|---|---|---|---|
| 2 | 9.5e-7 | 4.6526 | 181.1 | 10.52 | 9.94 | 10.20 |
| 32 | 1.5e-5 | 4.6430 | 149.1 | 10.53 | 9.83 | 9.89 |
| 512 | 2.4e-4 | 4.6140 | 119.5 | 10.58 | 9.39 | 10.98 |
| 8192 | 3.9e-3 | 4.4984 | 86.7 | 9.34 | 9.88 | — |

- Variance → **4.65** (agrees with the OP), mean 0.
- **Tail P(|Q| > t) ≈ C t^{−4} with C ≈ 10** at every scale.
- **E Q⁴ grows like C' log(1/h)** with C' ≈ 10.8 per unit of log (≈ +15 per factor 4 in h).
- **Heuristic (consistent with all three).** Big |Q| only happens near rationals with nonzero Gauss sum,
  where R(p/q+δ) − R(p/q) ≈ c(p,q)·|G|/q·√|δ| with |G| ≍ √q. At distance δ ≥ h the increment is
  ≈ q^{−1/2} h δ^{−1/2}, so Q ≈ q^{−1/2} h^{1/4} δ^{−1/2}, and Q > t ⇔ δ < q^{−1} h^{1/2} t^{−2}. This needs δ > h,
  i.e. q < h^{−1/2} t^{−2}. There are ≍ q rationals with denominator q, so
  P(Q > t) ≍ Σ_{q < h^{−1/2}t^{−2}} q · q^{−1} h^{1/2} t^{−2} = t^{−4}. The δ < h regime gives the same order.
  So the tail is exactly t^{−4}, uniformly in h. It is cut off at t ≍ h^{−1/4} (q = 1, δ ≈ h). Hence Var Q is finite,
  and E Q⁴ ≈ ∫^{h^{−1/4}} 4t³·C t^{−4} dt = C log(1/h): **the logarithmic divergence of the fourth moment and
  the t^{−4} tail are the same fact**, and their constants must agree (they do: 10 vs 10.8).
  This matches Boritchev–Eceizabarrena–Vilaça da Rocha's log-divergent flatness.
- **Conjecture.** Law(Q_x(h)) converges as h → 0 to a symmetric law with variance ≈ 4.65 and tail
  P(|Q|>t) ~ C t^{−4}, where C is an explicit Gauss-sum average (the constant is Σ over q of the mean of
  |G(p,q)|⁴/q⁴ times q-density, times a universal integral of the cusp profile g(s) = √(s+1) − √s).
  Measured C ≈ 10. What would decide it: the Cellarosi–Marklof equidistribution of the theta sum with the
  non-Schwartz weight w(t) = (e^{πit²} − 1)/t², which the OP already points to.
- The curtain picture shows a **calm column at x = 1**, where R is differentiable (Gerver 1970, R'(1) = −½):
  there Q ~ h^{1/4} → 0, and the curtain goes still.

## 3. MO 515784 — pinwheel squares
Search: n × n binary matrices with quarter-turn symmetry, read row-major MSB first, leading bit 1
(so all four corners are 1). Gray-code walk over the free 4-cell orbits, residues kept incrementally modulo
9 moduli (2¹², 63·65·11, and products of primes to 103), survivors checked exactly (`pinwheel.c`,
`pin_verify.py` for > 128 bits).
- **Forced bits**: m odd ⇒ m ≡ 1 (mod 8) ⇒ the two cells left of the bottom-right corner are 0, so their
  orbits are 0 too.
- **Lemma (even n ⇒ 3 | m).** 2^e ≡ (−1)^e (mod 3). For even n the parity of the exponent of cell (i, j) is
  that of j + 1, and the four cells of an orbit sit in columns j, n−1−i, n−1−j, i, whose parities are
  j, i+1, j+1, i. The four signs cancel. So every pinwheel number with even n is divisible by 3.
  (Hence no pinwheel primes for even n, and a pinwheel square with even n would have to be divisible by 9.)
- **Counts of pinwheel primes**: n = 5: exactly **1** (the OP's 18 153 809); n = 7: **161** of 4096;
  n = 9: **31 595** of 1 048 576 (the prime-number heuristic predicts ≈ 2/ln 2⁸¹ ≈ 3.6 %, which fits).
- **No pinwheel squares for n ≤ 12** (n = 11: 2.7·10⁸ candidates; n = 12: 8.6·10⁹ candidates, 108 639
  survivors of the filters, all checked exactly). **n = 13: all 2⁴⁰ = 1.1·10¹² candidates tested, 44 938 filter survivors, all checked exactly, no squares.**
  So there are **no pinwheel squares for n ≤ 13** (the OP checked n ≤ 10).
- **Heuristic, and why I'd bet on "none".** A random N-bit number is a square with probability ≈ 2^{−N/2}.
  There are ≈ 2^{N/4} pinwheel numbers of N = n² bits, so the expected count is ≈ 2^{−n²/4}. Summed over all n
  that is < 1, dominated by small n, which are all checked. **Conjecture: there are no pinwheel squares.**
  An honest proof would need a structural obstruction. Mod 3 kills nothing for odd n, but the even-n lemma
  shows the symmetry does push residues around.
- (Art note: I drew the 161 primes as a sunflower of clay tiles and dropped it. Quarter-turn-symmetric bit
  grids inevitably include swastika-like tiles.)
