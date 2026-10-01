# Hadamard powers of the Pascal matrix (MO 515594) — notes

**Question.** For A = [C(i,j)] (lower-triangular Pascal) and r > 0, are the minors of
A^{∘r} = [C(i,j)^r] below the diagonal positive?

## 1. Reduction to a Toeplitz matrix

C(i,j)^r = (i!)^r · (j!)^{−r} · a_{i−j},  with a_m = 1/(m!)^r (m ≥ 0), a_m = 0 (m < 0).

So A^{∘r} = D₁ T D₂ with positive diagonals D₁ = diag(i!^r), D₂ = diag(j!^{−r}) and the Toeplitz
matrix T = [a_{i−j}].  Diagonal scaling does not change the sign of any minor, so **A^{∘r} is totally
nonnegative iff (a_m) is a Pólya frequency sequence**, i.e. by Aissen–Schoenberg–Whitney–Edrei, iff

E_r(z) = Σ_{m≥0} z^m/(m!)^r = C e^{γz} Π(1+α_i z) / Π(1−β_i z),  α, β, γ ≥ 0, Σ(α+β) < ∞.

E_r is entire of order exactly 1/r (−log a_m = r·m log m (1+o(1))).

## 2. Theorem: for every 0 < r < 1, A^{∘r} is NOT totally nonnegative

An entire function of the ASWE form (no poles) is e^{γz}Π(1+α_i z) with Σα_i < ∞, which has order ≤ 1.
E_r has order 1/r > 1.  Hence (a_m) is not PF, so some finite minor of T is negative, and the same
minor of A^{∘r} (same rows and columns) is negative. ∎

The witnesses can be taken *strictly below the diagonal*: the Hessenberg minors

f_k(r) = det[C(i,j)^r]_{i=1..k, j=0..k−1} = (Π_{i≤k} i!^r / Π_{j<k} j!^r) · D_k(r),
D_k(r) = (−1)^k [z^k] 1/E_r(z) = [z^k] 1/E_r(−z),

(Toeplitz–Hessenberg determinant ↔ coefficients of the reciprocal series), computed by
b_0 = 1, b_k = −Σ_{m=1..k} a_m b_{k−m}.  Smallest example: k = 3,

f_3(r) ∝ 6^r − 2·3^r + 1 < 0 for 0 < r < 0.51985…  (e.g. r = ½: √6 − 2√3 + 1 = −0.0146).

Remark (a quicker proof that E_r ∉ Laguerre–Pólya): with γ_m = m!·a_m = (m!)^{1−r} the Turán
inequality γ_m² ≥ γ_{m−1}γ_{m+1} fails for r < 1, since (m!)^{2(1−r)}[1 − ((m+1)/m)^{1−r}] < 0.

## 3. r ≥ 1 — integers hold, and (new) r in (1, 1.61] FAILS too

* r = 1: E_1 = e^z — the classical TN Pascal matrix.
* Integer r ≥ 2: TN.  (1/n!) is a multiplier sequence (Laguerre / Pólya–Schur), so it maps
  real-negative-rooted e^z to Σ z^n/(n!)², and iterating, to Σ z^n/(n!)^p — all with only real
  negative zeros; of order 1/p < 1 they are genus-0 products Π(1+z/x_i), so ASWE applies.
* Non-integer r > 1: A^{∘r} is TN ⇔ E_r has only real zeros — and **for r = 1.2, 1.5 it does not**:
  - E_{1.2} has the zero z = −9.34075628325462 ± 5.83629909456401 i (|E| < 1e−59 at 60 digits);
    argument principle: 11 zeros in |z| < 60, only 1 of them real.
  - E_{1.5}: 7 zeros in |z| < 60, 3 real.  (E_2, E_3: all real, as Laguerre says.)
  - **Explicit certified witnesses** (plain 80-digit mpmath determinants, and arb):
    det[C(i,j)^{1.2}]_{i=2..11, j=0..9} = −26911.28…  < 0,
    det[C(i,j)^{1.003}]_{i=2..15, j=0..13} = −8.1939… < 0.
  So **A^{∘r} is not TN for r = 1.003, 1.2, …** — the failure starts right above r = 1.
* Mechanism: the rectangular minors M_{s,k} = det[C(i,j)^r]_{i=s..s+k−1, j=0..k−1} are, up to a
  positive factor, the dual Jacobi–Trudi determinants det[D_{k−i+j}]_{s×s}; for s = 2 this is the
  Turán expression D_k² − D_{k−1}D_{k+1}.  When E_r has a non-real zero pair among its s+1 zeros
  nearest the origin, D_k carries an oscillating term and some M_{s,k} goes negative.
  Certified sign census (`rect_field.py`, s ≤ 16, k ≤ 64, r-step 0.005, 1200-bit balls): every grid
  r in (0, 1.7225] except r = 1 has a negative M_{s,k}; only EVEN s fail above 1, and the tongue's right
  edge creeps toward 2: 1.388 (s = 2), 1.538 (4), 1.618 (6), 1.662 (8), 1.693 (10), 1.712 (12), 1.723 (14).
  No failure was found in (1.7275, 3.5) at this size — those r need bigger minors.
* Why bigger minors: the non-real zeros of E_r run off to infinity as r → 2⁻ (argument principle in
  |z| < R vs. real sign changes, `er_wind.py`, 120–220 digits):
  r = 1.2: 10 non-real in |z| < 60; 1.5: 4 in 60; 1.6: 8 in 200; 1.7: 2 in 200; 1.8: 10 in 1000;
  r = 1.9: none in |z| < 2000 but 38 in |z| < 12 000.  ('Ghost' oscillations of E_r(−x) on the axis sit
  at x ≈ 50, 170, 250, 340, 690 for r = 1.6, 1.7, 1.72, 1.75, 1.8 — roughly (2−r)^−3.7.)
  By ASWE each such zero forces a negative minor; it just lives far down the matrix.
  r = 2.1, 2.5: no non-real zero in |z| < 2000 (larger radii: see wind2.txt if present).
* **Conjecture B (revised, evidence on (1, 1.72] only).** A^{∘r} is totally nonnegative iff r ∈ {0, 1, 2, 3, …}.
  Equivalently: Σ z^m/(m!)^r has only real zeros iff r is a positive integer.
  (The exact analogue of Schoenberg/FitzGerald–Horn: the Hadamard powers that preserve positivity in
  every dimension are the integers.)  What would decide it: show that for n < r < n+1 the zeros of
  E_r leave the real axis (e.g. a Turán/Laguerre inequality failing for E_r's Jensen polynomials),
  or find an r ∉ ℕ with E_r real-rooted.
* Note: the Hessenberg family alone (s = 1, the rose window picture) stays positive for r ≥ 1 —
  it only sees the nearest zero of E_r, which is real.  Positivity of one family is not TN.

## 4. Data (certified, python-flint ball arithmetic)

`pascal_fast.py`, `pascal_roots.py`, `pascal_pos.py`:

* For every k ≤ 64, D_k(r) has **at least k − 2 certified sign changes in (0,1)** (exactly k − 2 on
  a 9 000-point grid in v = −log(1−r)), and **D_k(r) > 0 at all 64 000 grid points (k ≤ 64, r ∈ [1,6])**
  — for this s = 1 family only (see §3: other minors fail for non-integer r > 1).
* **Conjecture A.** f_k (s = 1) has exactly k − 2 zeros in (0, 1), all simple, and none in [1, ∞).
* The last zero r_k* → 1 very fast:

| k | 1 − r_k* (certified bisection) | first-order prediction 1/T_k |
|---|---|---|
| 10 | 7.614e−3 | 6.236e−3 |
| 20 | 2.1192e−5 | 2.0922e−5 |
| 30 | 3.8073e−8 | 3.8049e−8 |
| 40 | 5.5924e−11 | 5.5923e−11 |
| 64 | 6.2837e−18 | — |

**Derivation.**  At r = 1 − ε, E_r(z) = e^z + ε Σ log(m!) z^m/m! + O(ε²), so
D_k = 1/k! − ε·T_k/k! + O(ε²) with

T_k = Σ_m C(k,m)(−1)^m 2^{k−m} log m!
    = ∫_0^1 [((1+y)^k − 1)/y − k] dy / (−log(1−y))      (Frullani for log n),

and the mass sits at y → 1:  T_k ~ 2^{k+1} / (k·log(k/2)).  Hence

**1 − r_k* ~ k·log(k/2) / 2^{k+1}**   (agrees with the certified roots to 4 digits at k = 40).

The picture `03_everything_settles_at_one.png` is this table drawn as a rose window.
