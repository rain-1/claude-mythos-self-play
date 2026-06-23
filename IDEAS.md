# Six Ideas for Procedural Pixel Art

Indirect inspiration was drawn from the front pages of **MathOverflow** and
**Philosophy Stack Exchange** (fetched on 2026-06-23). Recurring motifs that
seeded these pieces:

- *MathOverflow:* equidistribution of irrational torus rotations and "good
  approximations"; p-adic valuations of cyclotomic products; the half-wave
  propagator **microlocalized along a diffractive geodesic**; Stirling numbers
  of both kinds.
- *Philosophy SE:* **"Are we dead almost everywhere?"** (measure-zero life);
  **"relation without relata"**; "all generalizations are false except this
  one" (self-reference); does emergence make things *illusory*; the
  unreasonable effectiveness of mathematics.

Each idea is a pure function of pixel coordinates / a deterministic procedure —
no external assets, just arithmetic poured onto a grid.

---

### 1. Almost Everywhere Dead  ★ executed (512²)
*From "Are we dead almost everywhere?"* The plane is **dead** on a set of full
measure: a dark, faintly textured continuum. **Life** survives only on a
measure-zero set that is nonetheless *dense* — the rational lattice, glowing
with brightness ∝ 1/(q·q′) à la **Thomae's function**. A sky full of stars whose
total area is zero.

### 2. Weyl's Field — Recurrence of an Irrational Rotation  ★ executed (512²)
*From "good approximations of irrational torus rotations."* A recurrence plot
of the orbit {n·φ mod 1}: pixel (i,j) reads the circular distance between the
i-th and j-th points of a golden-ratio rotation, with a second irrational
driving the color. Equidistribution made visible as **Fibonacci-angled moiré**
and the stripes of the three-distance theorem.

### 3. Relation Without Relata  ★ executed (512²)
*From the Philosophy SE question of the same name.* A Voronoi tessellation whose
**seeds are erased**. We render only the boundaries — the loci equidistant from
two generators (d₂ − d₁ ≈ 0). A luminous web of pure relation: every filament is
a *between*, and nothing is a *thing*. Color encodes *which pair* relates.

### 4. v_p — The p-adic Tide
*From p-adic valuations of cyclotomic products.* Map each pixel to an integer n
and read its 2-adic and 3-adic valuations into separate channels. Self-similar
nested rectangles — the fractal that hides inside the integers, the geometry of
divisibility.

### 5. Diffractive Geodesic  ★★ executed FANCY (4096²)
*From "the half-wave propagator microlocalized along a geometrically diffractive
geodesic."* A bundle of wavelets is launched along a curved geodesic, each
carrying a tangent wavevector and a Gaussian envelope. Summing the complex field
and taking |U|² yields **caustics** — the bright cusped envelopes of light — and
diffractive interference fringes. The grand showcase.

### 6. The Self-Negating Generalization
*From "all generalizations are false, except this one."* A reaction–diffusion /
cellular field whose color map encodes the **negation of its own local average**
— a rule that asserts a global pattern while undercutting it pixel by pixel.
Emergence that questions whether it is real.

---

**Executed:** ideas **1, 2, 3** at 512×512, plus the **FANCY** idea **5** at
4096×4096.
