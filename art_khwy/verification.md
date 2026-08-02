# THE APERTURE — verification notes (run 2026-08-02, branch `claude/magical-faraday-khwy9k`)

Triptych: **One Thread Through Every Meeting** (4096² hero) · **The Ladder of
Fainter Creases** (2560²) · **The Toll of Twenty-Two** (2560², atlas piece 38).
Philosophical seed: Phil.SE front page, *"Intrinsic Reality and the Limits of
Observation"* — each piece asks what a bounded instrument (n lines, a Taylor
disk, a norm form) can hold of an unbounded structure.

---

## Piece 1 — One Thread Through Every Meeting  (MO 513798, live, 0 answers)

**Question (poster):** what is the maximum k such that an n-line arrangement
induces a k-gon? Upper bound k ≤ n⌊(n−1)/2⌋ (each pair of lines adjacent at
most once); poster asks whether it is attained, with best known k=17 for n=7.

### Results (all polygons SIMPLE, matching the poster's own examples)

**Reduction (proved, `polylib.py`).** For odd n, a simple k-gon with
k = n(n−1)/2 must use every pairwise crossing exactly once as a corner. Along
each line the sides then form a perfect matching of its n−1 crossings by
segments with no crossing in their interiors — forcing the consecutive pairing
(1,2)(3,4)…(n−2,n−1) in the order along the line. Segments of two different
lines meet only at that pair's crossing, which is never interior to a forced
segment, so **the union is automatically a non-crossing 2-regular graph** on
all C(n,2) crossings. Hence the bound is attained iff some simple arrangement
makes this forced graph a **single cycle**.

**Parity Theorem.** For every simple arrangement (no two parallel, no three
concurrent) of n lines, n odd, the number C of cycles of the forced graph
satisfies  **C ≡ ⌊(n+1)/4⌋ (mod 2)**  — equivalently (−1)^(V−C) = Jacobi(−2|n),
V = n(n−1)/2. Proof structure:
1. *Wall-crossing invariance.* Deforming the arrangement changes the forced
   graph only at triple-concurrence events. The local rewiring gadget
   (3 shared vertices, ≤6 outer stubs) was enumerated exhaustively — all
   2³ straddle-patterns × 2³ left-right orders — and every case changes the
   cycle count by an even amount, independent of the outside connection
   (chord-diagram parity lemma). `gadget_check.py`: **64/64 configurations
   conserve parity**. Numerical wall tests: 4,000 triple-flips + 4,000
   parallel-wall crossings, **zero parity violations** (`flip_test.py`,
   `wall2_test.py`).
2. *Connectivity.* Relabel the target arrangement so its angle order matches;
   then interpolate angles order-preservingly (avoiding all parallel walls)
   and offsets freely — a generic such path crosses only triple walls. So C's
   parity is a constant of n.
3. *Anchor: the regular tangent arrangement* (lines tangent to the unit circle
   at n-th roots of unity) is simple for every odd n (crossing parameters
   tan(πδ/n) are strictly ordered; no two tangents parallel for n odd). Its
   forced graph is a circulant system whose cycle count is computed exactly by
   the orbit analysis of the pairing map: **C_reg = (n−1)/4 for n ≡ 1 (mod 4),
   (n+1)/4 for n ≡ 3 (mod 4)** (e.g. n=5: 1 = the pentagram 10-gon; n=7: 2 =
   one 7-cycle + one 14-cycle; n=11: 3; n=13: 3).
Census: 22,500 random arrangements, n = 3..19 (`parity_census.py`) — observed
parities match the theorem for every n with zero exceptions.

**Corollary (three closed doors).** In any simple polygon on n lines, every
line must carry an even number of unused crossings (each used corner consumes
exactly one side-endpoint on each of its two lines). Hence u = #unused
crossings cannot be 1 or 2; combined with the parity theorem, for
n ≡ 1, 7 (mod 8):  k ≤ n(n−1)/2 − 3, with the three dropped crossings forming
a line-triangle.

**Witnesses (all verified from first principles by `verify_polygon.py` /
`verify_hero.py`: exact segment-intersection tests, sides-on-lines residuals
< 1e−8, distinct corners, single cycle, each line-pair adjacent once):**
- n=5: simple **10-gon** (bound attained), `win_n5_*.npy`
- n=7: simple **18-gon** = 21−3 (beats the poster's 17; and 19, 20, 21 are
  impossible by the above ⇒ **k_max(7) = 18 exactly**), `win18_n7_*.npy`
- n=9: simple **33-gon** = 36−3 (⇒ **k_max(9) = 33 exactly**), `win18_n9_*.npy`
- n=11: simple **55-gon** — every crossing of 11 lines on one thread
  (**bound attained**), `win_n11_*.npy`
- n=13: simple **78-gon** (**bound attained**), `win_n13_*.npy`
Aesthetically annealed copies (same certificates re-verified): `hero*_n*.npy`.

**Summary for odd n:** the Eulerian bound n(n−1)/2 is attainable **iff
n ≡ 3, 5 (mod 8)** (necessity proved; attainability witnessed for n = 3, 5,
11, 13 — for n = 19, 21 annealing reached C = 3, single cycle not yet found);
for n ≡ 1, 7 (mod 8) the maximum is n(n−1)/2 − 3, attained for n = 7, 9.
Even n not treated here (bound n(n−2)/2; different local structure).

*Caveats for a would-be MO answer:* the gadget/connectivity argument is
computer-assisted and sketched above; the chord-diagram parity lemma is
classical. n=19/21 attainability and all even n remain open here.

---

## Piece 2 — The Ladder of Fainter Creases  (MO 513816, live, 0 answers)

F(x) = Σ_{n≥0} 3⁻ⁿ√(1 + x/4ⁿ),  F(x) = √(1+x) + F(x/4)/3.

All claims verified in `fseries.py`, `fasympt.py`, `fexact.py` (mpmath,
dps 60–90):

1. **Taylor law** c_m = C(½,m)/(1 − 4⁻ᵐ/3) — verified to 1e−42 (m ≤ 11).
2. **Hadamard structure** F = √(1+·) ⊙ L with
   L(x) = Σ_m x^m/(1−4⁻ᵐ/3) = Σ_j 3⁻ʲ/(1 − x/4ʲ): a Lindelöf-type series
   with simple poles at +4ʲ — the mirror of F's branch ladder at −4ʲ
   (two representations agree to 1e−61).
3. **Analytic continuation / classification.** F is analytic on ℂ∖(−∞,−1]
   and continues to a multivalued function whose only singularities are
   square-root branch points at −4ⁿ, n ≥ 0, of weight 3⁻ⁿ (monodromy: the
   n-th sign flips; branch jump on (−4^{m+1},−4^m) equals
   2Σ_{j≤m}3⁻ʲ√|1+x/4ʲ|, verified to 1e−32). **Infinitely many singularities
   ⇒ F is not algebraic and not D-finite** (a D-finite function has finitely
   many singularities). Moreover √(1+x) is not q-holonomic for the dilation
   x→x/4 (shifted square roots √(1+x/4ᵏ) are linearly independent over ℚ(x)
   — distinct branch points), and F − F(·/4)/3 = √(1+x), so **F is not
   q-holonomic either**: its exact class is the inhomogeneous first-order
   q-difference equation above with algebraic inhomogeneity.
4. **Far-shore law (exact identity).** For x > 1/4:
   **F(x) = Σ_{k≥0} C(½,k)/(1 − 4ᵏ/6) · x^{½−k}  +  x^{−log₄3} Φ(log₄ x)**,
   Φ(u) = Σ_j φ_j e^{2πiju},  φ_j = −Γ(s_{−j})Γ(−½−s_{−j})/(Γ(−½)ln 4),
   s_{−j} = log₄3 − 2πij/ln4  (Mellin poles of 1/(1−4ˢ/3)).
   Verified: Φ periodic to 1e−71, Fourier coefficients match the Γ-formula
   (|φ₁| ≈ 8.3e−8, |φ₂| ≈ 2.0e−14, matched to 12 digits), and the identity
   holds to ~1e−58 at x = 0.51, 2, 10, 100. Note the **mirror symmetry** of
   the two shores: modulator 1/(1−4⁻ᵐ/3) at 0, 1/(1−4ᵏ/6) at ∞, bridged by
   the log-periodic exponent log₄3 (the "Cantor exponent" of the (3,4)
   system). The rendered curtain: monodromy branch values
   Im F_ε(−4ᵘ)/2ᵘ for all 2⁷ sign patterns — pitchforks at every crease,
   settling onto the Bernoulli-convolution spectrum {Σ ±6⁻ⁿ}.

---

## Piece 3 — The Toll of Twenty-Two  (AP-obstruction atlas, piece 38)

S = {n = x² + xy + 3y²} (norm form of O_{ℚ(√−11)}, disc −11, h = 1; n ∈ S iff
every prime p with (−11/p) = −1 divides n to an even power; 2 is inert since
−11 ≡ 5 (mod 8); 11 is ramified; mod 11 the form is the square (x+6y)², so
S mod 11 ⊆ {0,1,3,4,5,9} — verified: census residue histogram is exactly
supported there).

C sieve (`sieve11.c`/`sieve11b.c`), all n ≤ 4×10⁹ by direct (x,y) marking
(~7.5×10⁹ lattice points): |S| = 593,798,441 (density 0.14845). Equal-gap runs
of **consecutive** elements of S:
- ℓ=3 first at 3, 4, 5 (gap 1).
- **ℓ=4 first at 33,092,159, gap 22 = 2·11** (elements 33,092,159 / 181 /
  203 / 225). Double-engine verified: the C bitset scan and an independent
  sympy factorization scan agree on the full local element list; the four
  members are factor-certified in S with explicit representations
  Q(5612,251), Q(5631,220), Q(4285,1614), Q(4010,1805); the run is maximal
  (flanking gaps 3).
- **No ℓ=5 run exists below 4×10⁹.**
Contrast (piece 37, d = −1): ℓ=4 by 757, ℓ=5 by 2989, ℓ=6 by 28,059,605.
The ℤ[√−11] country is dramatically more hostile to marching, despite being
denser: with 2 inert, any 4 consecutive integers contain n ≡ 2 (mod 4) ∉ S,
killing gap-1 runs at length 3; and the good-step law at the ramified prime
taxes long runs with gap ≢ 0 (mod 11). The observed toll 22 = 2·11 is the
minimal tribute to both primes at once.

---

### Reproduction
```
python3 search7.py 7 20000 1        # component census (n=7: never 1 cycle)
python3 parity_census.py 7 2500     # parity law, n=3..19
python3 gadget_check.py             # 64/64 local flip cases conserve parity
python3 anneal.py 11 2 600          # finds the 55-gon
python3 hunt18.py 7 1 900           # finds the 18-gon
python3 verify_polygon.py full 11   # first-principles verification
python3 fexact.py                   # the exact far-shore identity
gcc -O3 -o sieve11 sieve11.c -lm && ./sieve11 4000000000
python3 hero.py; python3 ladder4.py; python3 toll.py
```
