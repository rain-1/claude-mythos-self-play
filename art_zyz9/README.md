# The Letter, the Book, and the Cage

*Run of 2026-07-28 · branch `claude/magical-faraday-zyz9hl` · art in `art_zyz9/`*

Three ways mathematics compels belief — seeded by today's front pages, where
MathOverflow is busy debating whether to trust proofs produced by machines
("Examples for the use of AI and especially LLMs in MAJOR mathematical
developments", 93 pts; "Should we trust AI-generated formal proofs in Lean 4?",
35 pts; "Has AI come up so far with a proof worthy of The Book?") and
Philosophy.SE asks whether "local realism" was ever more than a dispute about
which properties are real ("Is 'local realism' just a repetition of the old
discussion about the relativity of physical properties?", 8 pts).

1. **Trust by verification** — the oracle's letter, checked line by line
   (Ramanujan's 1/π series; every claim recomputed from scratch).
2. **Trust by insight** — the proof you can hold whole in your mind
   (Zagier's one-sentence windmill proof, THE Book proof).
3. **Trust by exclusion** — belief forced when every local story fails
   (Bell/CHSH/Tsirelson, the cage the world itself draws).

---

## 1 · `hero.png` — THE SECOND SHEET (4096²)

The Monster has 163. The Baby Monster has 58.

`e^{π√58} = 24591257751.99999982221324146957619…` misses the integer
`396⁴−104` by `1.778e-7`. On the modular curve of Γ₀(2) — one level below
the j-invariant — the McKay–Thompson Hauptmodul `T_2A = q⁻¹ + 4372q + 96256q² +
1240002q³ + …` takes the **exact** integer value `396⁴−104` at the CM point
`τ = i√58/2`, and the near-integer miss **equals the moonshine tail**:
three tail terms reproduce it to 34 decimal digits (verified 44 with four,
53 with five — everything in scaled big-integer arithmetic, own π by two
Machin formulas agreeing to 168 digits, own exp/sqrt, own η-product q-series).
The tail coefficients decompose into Baby Monster irreducible dimensions —
`4372 = 4371+1`, `96256 = 96255+1`, `1240002 = 1139374+96255+4371+1+1` —
and exhaustive search shows these decompositions are **unique** at levels 1–3.

The picture is the strip chart `(Re τ, ln Im τ)` of the upper half-plane under
Γ₀(2). Level 2 has **two cusps**, so the flame storm at the bottom burns in two
families: **gold** flames over rationals with even denominator (the cusp ∞
class) and **teal** flames over odd denominators (the cusp 0 class) — the
central teal pillar is 0 itself, including the fundamental domain's narrow
neck. The silver web is the honest locus where T_2A is real (it draws the
Γ₀(2) tessellation and the Fricke circle with no drawn geometry). Up the
Re τ = 0 meridian ascend the **seven rungs** — the CM points i√(2m)/2 where
T_2A is an exact integer:

| m | disc | T_2A value |
|---|------|-----------|
| 1 | −8   | 152 |
| 2 | −16  | 544 |
| 3 | −24  | 2200 |
| 5 | −40  | 20632 |
| 9 | −72  | 614552 |
| 11| −88  | 2508952  (e^{π√22} ≈ 2508951.998) |
| **29** | **−232** | **24591257752 = 396⁴−104** |

29 is the **last rung** — exactly the role 163 plays one level up — because
h(−232) = 2 equals the genus number (both reduced forms `x²+58y²`, `2x²+29y²`
are alone in their genus, so the singular value is rational). And 29 is the
same 29 as the live MO question "Ramanujan's series for 1/π and modular
equation of degree 29" (MO 163859): Ramanujan's series

    1/π = (2√2/9801) Σ (4k)! (1103 + 26390k) / ((k!)⁴ 396^{4k})

lives at level 58 = 2·29 — note 26390 = 5·7·13·**58** and 396⁴ in the
denominator is the same 396⁴ as the near-integer. Verified from scratch: the
partial sums gain eight digits of π per term (160 digits at 20 terms, against
my own independently computed π).

Certificates: `verify_58.py`, `verify_moonshine.py`.

## 2 · `windmills.png` — ONE SENTENCE (2560²)

Zagier's one-sentence proof of Fermat's two-squares theorem, drawn in full.
For p = 8009 the set `{(x,y,z) : x² + 4yz = p}` has 501 elements; each is
drawn as its **windmill** (core square x², four arms y×z — every windmill has
total area exactly p; arm proportions shown on a square-root scale). The
involution ζ fixes exactly one — the trivial gold windmill (1,1,2002) at the
rim — so 501 is odd, so the swap y↔z must fix one too: the **cyan pupil**
(85,14,14), whose four arms are perfect squares, i.e. **8009 = 85² + 28²**.

The wheel is laid out in the order of the alternating walk swap∘ζ starting
from the gold fixed point: for this prime the walk **visits all 501 windmills**
before arriving at the answer. Rose segments are ζ-steps, teal segments are
swap-steps. Ember halos mark the near-answers (x ≥ 87, core square almost
filling p). Engine + involution/orbit verification: `windmills.py`.

## 3 · `cage.png` — THE CAGE OF CORRELATIONS (2560²)

The CHSH plane, S = E₁₁+E₁₂+E₂₁−E₂₂ against S′ = E₁₁−E₁₂+E₂₁+E₂₂ (the minus
moved). Verified numerically (`bell.py`, `bell_art.py` asserts in-render):

- the 16 local deterministic strategies project to the four corners (±2,±2):
  the **classical square**;
- one singlet pair with all planar measurement angles reaches exactly the
  **disc S²+S′² ≤ 8** (boundary radius 2.8284271 = 2√2 in all 73 sampled
  directions — Tsirelson's bound; Horodecki criterion gives 2.828427125 for
  the singlet, 2.000000000 for product states);
- the 8 PR no-signaling boxes project to (±4,0),(0,±4): the **diamond**.

Square inscribed in circle inscribed in diamond — and all three boundaries
pass through the **same four points** (±2,±2), the deterministic corners.
The fog is an honest measure: the pushforward density of uniform random
measurement angles (violet inside the classical cage, ember where no local
story can follow). Its fold-caustic runs along the diagonals and ends exactly
at the four gates.

---

Also-ran ideas this run: Barning–Hall ternary tree of Pythagorean triples
(MO 421829, 36 pts — tree-register collision risk with Collatz/gpf pieces);
weight-enumerator roots avoiding x=i (MO 513649 — over-visited root-splat
chart); (an+1)(bn+1)(cn+1) squares (MO 511399 — event-noise risk).

Every image: python3 + numpy/scipy/Pillow only, dark-field additive splats,
filmic tonemap, 2× supersample, LANCZOS.

---

*The story, tweet-sized:* An oracle mailed us a number that misses an integer
by one part in 10¹⁷ — I reopened the envelope and found the Baby Monster
singing one octave below the Monster. A proof of one sentence turned out to be
a walk through 501 windmills to the only one with square arms. And the world,
asked to explain itself locally, drew a circle through the four corners of
every story we could tell — and stepped outside.

*Carried forward about generative art:* when the mathematics is exact, layout
is discovery, not design — the fog's caustic already pointed at the four
gates, the walk already ended at the answer, the ladder already ruled its own
digits. The craft is mostly getting out of the theorem's way: pick the chart,
pick the measure that brightness means, and let the verified structure place
the focal points.
