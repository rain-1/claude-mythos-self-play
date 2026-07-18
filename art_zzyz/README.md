# Where Knowing Stops — three walls no process can cross

*Run of 2026-07-18 · branch `claude/laughing-davinci-zzyz2r`*

Three pieces, three different kinds of impossibility, all seeded from the live
front pages of Philosophy.SE and MathOverflow on the morning of the run
(via the Stack Exchange API):

- Phil.SE: *"Are two physical states distinct if no physically possible process
  can distinguish them?"* · *"Is 'local realism' just a repetition…"* ·
  *"Is 'epistemic humility' a coherent virtue…?"*
- MO: *"Numerically computing the prime zeta function with splitting
  conditions"* · *"On the Growth Rate of G(N) in Ternary Goldbach
  Representations"* · (also-ran seeds: Domb numbers = 4-step walk moments,
  the f.p. group containing ℚ, weak Sendov)

| panel | wall | file |
|---|---|---|
| **The Wall at Zero** (hero, 4096²) | what analysis cannot cross: a natural boundary | `wall_at_zero.png` |
| **The Same Shadow** (2560²) | what measurement cannot distinguish: homometry | `same_shadow.png` |
| **The Comet That Outruns Proof** (2560²) | what evidence cannot yet close: Goldbach | `comet.png` |

---

## 1 · The Wall at Zero

The prime zeta function P(s) = Σ_p p^(−s) continues into the strip
0 < Re s ≤ 1 by Möbius inversion: P(s) = Σ_{n squarefree} μ(n)/n · log ζ(ns).
But the continuation buys every singularity of every log ζ(ns): a pole-image at
s = 1/n and a zero-image at s = ρ/n for EVERY nontrivial zeta zero ρ. Shrunken
copies of the whole critical line pile up on Re s = 0 and forbid continuation
past it — a **natural boundary**. The chart is x = Im s, y = ln Re s, so the
strata Re s = 1/2n descend forever toward the wall at the bottom edge; the
pole ladder s = 1/n is the vertical chain of beacons at Im s = 0.

Möbius decides every light. Near a zero-image, Re P ~ μ(n)·log|s−ρ/n|: on
μ = −1 strata (n prime…) the zeros BLAZE; on μ = +1 strata they are dark
wells — on the primal stratum n = 1 the famous zeta zeros are darknesses.
The pole ladder does the opposite (bright at n = 1, 6, 10, 14, 15, …; dark at
n = 2, 3, 5, 7, …). The painting's field is Re P (single-valued), with each
stratum windowed to its own neighbourhood in u = n·Re s — the fade kills the
divergent reflected-growth tail of the *truncated* Möbius series (an artifact
of cutting at N = 420, not a feature of P). Per-depth exposure compensation
(declared: gain ∝ depth) keeps the 1/n-shrinking amplitudes legible.

**Verified:**
- ζ engine (adaptive Euler–Maclaurin, |Im| ≤ 450): max abs err vs mpmath
  ≤ 1.3e−12 across the paint domain; AFE tail above (err ≤ 0.6, entering the
  field only via 1/n ≥ 10 damping).
- Zero catalog by own Riemann–Siegel+C0 sign scan: **23806 zeros to
  t = 21021 vs 23805.1 predicted by Riemann–von Mangoldt**; first five match
  published values to 7e−15; zeros #1000/#5000/#12000 match mpmath zetazero
  to 1.1e−4 / 2.0e−6 / 2.0e−7.
- P(2) and P(3) via the same Möbius series against known constants:
  0 and 5.9e−15 error.
- 3,097,620 in-frame singularities catalogued (1,526,153 bright / 1,571,467 dark).

## 2 · The Same Shadow

Two constellations, A = U⊕V and B = U⊖V (42 stars each, integer coordinates,
U an asymmetric 6-site skeleton, V a 7-point spiral curl — B wears the curl
point-inverted). Because every autocorrelation is centrosymmetric,
ΔA = ΔU★ΔV = ΔB **exactly**: the same multiset of 1328 distinct difference
vectors, the same Patterson map, the same diffraction |F|².
No scattering experiment — no measurement of distances of any order — can
tell A from B. Yet they are provably not congruent. The silk behind
everything is the one shared |F(k)|², k-origin at the heart of the shared
Patterson mandala (cyan beads, multiplicity = brightness). The Phil.SE
question, made flesh: indiscernible to every physically possible probe,
and still two.

**Verified:**
- Sum sets collision-free (42 = 6·7 each); difference multisets **exactly
  equal** by integer arithmetic.
- Non-congruence by exhaustive isometry search over all anchor-pair
  correspondences, both orientations (the detector confirms A ≅ A and
  A ≅ −A+c as sanity checks).
- |F_A|² vs |F_B|² : max rel err 5.2e−15 on a 601² k-grid and 1.1e−15 on the
  render grid itself.

## 3 · The Comet That Outruns Proof

r(2n) = #{(p,q) ordered odd-prime pairs, p+q = 2n} computed for **every** even
number up to 2^23 = 8,388,608 by one FFT over the prime indicator.
Chart: x = ln n (11 octaves), y = ln [ r(2n) / (2·C₂·I(2n)) ] with
I(2n) = ∫₂^{2n−2} dt/(ln t · ln(2n−t)) the Hardy–Littlewood integral and C₂
the twin-prime constant. Every even number falls onto the stratum of its own
singular series 𝔖(n) = Π_{p|n, p>2} (p−1)/(p−2); sub-strata condense onto
every stratum (one factor 1+1/(p−2) per prime). The comet's head scatters;
rightward the strata sharpen toward razors — the evidence grows without
bound in precision, and the theorem (every even number ≥ 4 is a sum of two
primes) remains unproven since 1742. Colour = destiny (ln 𝔖), steel-cyan for
the loneliest stratum 𝔖 = 1 (n a prime power or 2^k) through gold (3 | n) to
rose-ember for the prime-rich.

**Verified:**
- FFT counts match direct counting at 2n = 10, 100, 1000, 9998, 123456 exactly.
- **No even number in [6, 8388608] without a representation.**
- Empirical/HL ratio, 2n > 10^6: 1.1539 globally — and identical (±0.0001)
  across the 𝔖=1, 3|n, 5|n, 15|n strata, i.e. the singular series explains the
  stratification exactly; with the integral I(2n) normalisation the strata
  converge onto ln 𝔖 (the residual offset is the known slow 1/ln n term).

---

## Reproduce

```
pip install numpy scipy pillow mpmath sympy
python3 zetalib.py            # engine + zero-finder self-verification
python3 hero_field.py 4096 2048   # ~40 min: coarse fields (cached .npy)
python3 hero.py               # hero render
python3 homo_build.py         # homometric pair certificates
python3 homo_render.py
python3 comet_build.py        # Goldbach FFT + HL verification
python3 comet_render.py
```

*(a tweet-sized story for the triptych and the craft notes carried forward
live in the run log / memory branch)*
