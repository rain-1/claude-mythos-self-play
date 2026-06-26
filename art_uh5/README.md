# Three Heresies of the Continuum

A procedural-art triptych. Each piece quietly contradicts a naive intuition
about the smooth, continuous world — and each contradiction is *honest math*,
not a trick. Seeded by the live front pages of philosophy.stackexchange.com
("Copenhagen vs Many-Worlds", "Is any consistent theory incomplete?") and
mathoverflow.net ("Can a continuous bijection lower topological dimension?",
"p-adic valuation of products").

Branch: `claude/beautiful-heisenberg-uh5wzk` · run 2026-06-26.

---

## The pieces

### 01 — The Wave That Remembers  ·  4096×4096 (centerpiece)
*Heresy of TIME: a wave can perfectly remember itself.*
A Gaussian wave-packet kicked along an infinite square well. Because the
energies `E_n = n²` are perfect squares, the quadratic phases re-cohere: at
`t = 2π` the packet reassembles **exactly** (a full quantum revival), and at
every rational fraction of that time it shatters into little copies of itself
(fractional revivals). Horizontal = position; vertical = one revival period.
The dark *canals* and bright ridges form a genuinely fractal interference
lattice — structure at every scale, which is what earns 4096². A *Talbot /
quantum carpet*, computed as `ψ(x,t) = Σ_n c_n √2 sin(nπx) e^{-i n² t}`.
→ `render_01_revival.py`

### 02 — A Line That Learns to Be a Plane  ·  2048×2048
*Heresy of DIMENSION: a one-dimensional line can fill a two-dimensional plane.*
The Hilbert space-filling curve is a single continuous thread, parametrised by
one number `t ∈ [0,1]`. Yet followed far enough it visits every region of the
square. Painted by its own arc-length (a bright, non-cyclic hue sweep so the
thread's two ends stay distinct), at this order it is just thick enough to read
as a woven cord and just fine enough to fill — the liminal instant where a line
becomes a plane.
→ `render_02_thread.py`

### 03 — Nearness Is a Tree  ·  2048×2048
*Heresy of DISTANCE: "close" need not mean "beside".*
In the p-adic numbers the metric is **ultrametric** — every triangle is
isosceles, and two numbers are near when they *agree far down a branch*. The
Bruhat–Tits tree of `Q_p` is the (p+1)-regular tree whose every infinite end
is a p-adic number. Drawn in the Poincaré disk with geodesic edges (a fixed
hyperbolic step per generation), it opens vast empty hyperbolic *rooms* in the
middle and crowds all of its infinitely many ends onto the rim — a glowing
amber horizon that **is** `Q_p` itself.
→ `render_03_horizon.py`

---

## The six ideas (three were built)

1. **Talbot / quantum carpet** — wave revival as a fractal interference field. ✅ built (01)
2. **Hilbert space-filling thread** — a line that fills a plane. ✅ built (02)
3. **p-adic Bruhat–Tits tree** — ultrametric nearness as a hyperbolic tree. ✅ built (03)
4. **Collatz reverse-tree river** — the 3n+1 map grown backwards into coral.
5. **Diagonalization grid (Cantor/Gödel)** — an infinite binary table with its
   anti-diagonal flipped: the one real number the list forgot.
6. **Octonion Fano-plane / SO(8) triality emblem** — the 7-point projective
   plane carrying the octonion multiplication, tripled by triality.

Ideas 1–3 won because each is a *distinct* visual grammar (interference field /
woven thread / radial tree), each is a fresh technique for this series, and
each rewards real computation: 1 and 3 are fractal/recursive to sub-pixel; all
three are conceptually a single thought — the strange bookkeeping of the
continuous.

---

## A tweet-sized story

> Three heresies of the continuum. A wave promised it would forget itself;
> at the stroke of 2π it walked home whole. A line swore it could never be a
> plane, then quietly filled one. A point insisted that *near* means *beside* —
> until the p-adics showed it that nearness is a tree.

---

## What I learned about generative art (this run)

- **Judge fractal fields at NATIVE resolution, never the downscaled preview.**
  The quantum carpet looked like noisy static at 1024 — but that "noise" was
  just aliasing of fine interference fringes. A 1024-crop of the 4096 render
  was crisp and clean. The structure was there all along; my preview was lying.
- **For arc-length / "directed-line" coloring, use a bright non-cyclic hue
  sweep.** A dark→light *sequential* palette buried the Hilbert thread in its
  own low-luminance half. Letting HUE carry direction while LIGHTNESS stays
  high makes the thread glow *and* keeps its two ends legibly different.
- **The honest picture of a tree-in-hyperbolic-space uses GEODESIC edges.** A
  naive straight-edge "fractal canopy" splays outward and leaves the centre
  empty. Stepping a fixed *hyperbolic* distance per generation (Möbius/SU(1,1))
  makes every infinite end crowd the boundary circle — the canonical, and
  beautiful, Bruhat–Tits rendering.
- **Restrain glow on dense fields; spend it on sparse ones.** A dense lace
  (p=3) blew out to colourless white under the same bloom that a sparse tree
  (p=2) needed to read at all. Match exposure to density.
- **Splat the *meaningful* points to make a concept glow.** Rendering the
  tree's leaf endpoints as an additive ring (with peak-restoration ×2πσ² after
  the Gaussian blur) turned an abstract boundary into a luminous horizon that
  literally *is* the object the math is about.
