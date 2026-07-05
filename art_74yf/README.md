# The Logarithm of a Curve
### a procedural triptych — `claude/focused-cerf-74yflt`, 2026-07-05

Seeded by the live **MathOverflow** front page, the question
*"Why is the number line two‑sided? What about three?"* — which is exactly the
question **tropical geometry** answers: an ordinary line has two ends, but a
**tropical line has three**. This triptych is one complex plane curve seen through
the logarithm, three ways.

Take a curve `V(P) = { (z,w) ∈ (ℂ*)² : P(z,w)=0 }` for a Laurent polynomial
`P = Σ c_ij z^i w^j`. Apply the logarithm to the coordinates and two shadows fall:

- **Amoeba(P)** `= { (log|z|, log|w|) }` — the *log‑modulus* shadow. A tentacled
  region whose arms shoot toward the ways-to-infinity, and whose bounded holes
  correspond to interior lattice points of the Newton polygon.
- **Tropical curve** — the piecewise‑linear *skeleton* of the amoeba: the corner
  locus of `max_ij( log|c_ij| + i·x + j·y )`. This is what the amoeba becomes when
  the logarithm is pushed to its limit — curved analysis straightened into
  combinatorics.

The curve chosen is a **degree‑6 Harnack curve** with a strictly‑convex,
`S₃`‑symmetric log‑coefficient valuation `v_ij = −λ(i²+j²+k²)`, `k=6−i−j`. Strict
convexity forces the *full unimodular triangulation* of the Newton triangle, so the
amoeba is **maximal**: all `(6−1)(6−2)/2 = 10` holes open. A linear "change of chart"
sends the triangle's three tentacle directions `(−1,0),(0,−1),(1,1)` (which sum to
zero) to three directions 120° apart, giving a true three‑fold mandala — the
three‑sided number line, made visible.

## The three pieces

**`01_amoeba_4096.png` (4096²) — The Amoeba.**
The log‑modulus shadow as a luminous density field. Solved by fixing `z = e^{x+iθ}`
and finding the `w`‑roots (batched companion‑matrix eigenvalues), sweeping a
memory‑streaming histogram over `(x,θ)` with the density symmetrised over the exact
`D₃` group of the curve. Teal flesh, gold ridges where the density concentrates on
the spine, black holes, tentacles fading to cool whiskers.

**`02_ordermap_2048.png` (2048²) — The Order Map.**
The straightened skeleton, rendered razor‑sharp and analytic. Each region of the
plane is flat‑coloured by the Newton‑polygon lattice point `(i,j)` that wins the
tropical maximum there — which is exactly `∇` of the **Ronkin function**
(Forsberg–Passare–Tsikh: the amoeba complement component *of order (i,j)*). The
tropical roads glow cyan like stained‑glass leading; the 10‑cell honeycomb is the
bounded complement, the fanning rainbow the 18 unbounded regions.

**`03_dequant.png` (2048²) — The Straightening (Maslov dequantization).**
The same curve, filmed as the logarithm's base runs to infinity. The amoeba scaled
by `1/λ` collapses onto the tropical curve (Viro patchworking / Maslov
dequantization). Overlaying the scaled amoeba at a ladder of `λ` values, each pixel
is coloured by the *deepest* `λ` (thinnest amoeba) that still contains it: warm
copper flesh far out, a blazing cool‑white skeleton at the limit. You can watch the
holes being born as `λ` grows.

## Verified (`verify.py`)
```
[1] max RELATIVE residual |P|/max|term| over 4000×6 roots = 3.85e-12   (roots lie on the curve)
[2] bounded complement components (connected interior-order regions) = 10  (= (d-1)(d-2)/2)
[3] fraction of clean-gradient pixels whose round(gradN) is a valid lattice pt = 1.0000
    max component of grad N = 6.005                                   (= Newton polygon max coord d)
[4] tropical unbounded rays = 18                                      (= 3d, triangle perimeter)
[5] interior lattice orders realised as holes = 10/10                (maximal Harnack amoeba)
```

## Files
`tropical.py` (root sampler + Ronkin integral) · `hero.py`/`hero_final.py`
(streaming amoeba builder + D₃ symmetrisation) · `color.py` (amoeba palette + spine +
bloom) · `tropmap.py` (analytic order map) · `ronkin.py`/`ronkin_color.py` (the true
Ronkin function, used to cross‑check the order labels) · `dequant.py` (the
dequantization) · `verify.py`.

---

*Story —* Take the logarithm of a curved complex equation and it forgets how to
bend. What was a smooth thing becomes an amoeba: a glowing body reaching three ways
toward infinity, the way an ordinary line has two ends but a tropical line has
three. Push the logarithm to its limit and the soft flesh cools and crystallizes
onto a skeleton of perfectly straight roads. Underneath, algebra was only ever
combinatorics — wearing curves as a disguise.
