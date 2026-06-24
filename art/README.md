# Three Procedural Pieces — *Measure, Dimension, Period*

A set of three algorithmic images (each pixel set procedurally, no painting, no
neural anything). The seeds were the live front pages of
[philosophy.stackexchange.com](https://philosophy.stackexchange.com/) and
[mathoverflow.net](https://mathoverflow.net/) on 2026-06-24 — read indirectly
through the Stack Exchange API. Six ideas were sketched; the three that *looked*
best after small test renders were executed.

---

### 01 · The Measure of a Curve  — *Crofton / integral geometry*  (2048²)
> *MathOverflow front page: "Crofton formula: expected intersections is to length as variance is to what?"*

Crofton's formula says a curve's **length is the measure of the lines that
meet it**. Run that backwards: for a convex curve with support function
`h(θ)`, the family of its tangent lines piles up density exactly on the curve —
a **caustic**. Here six support-function curves at nested scales are each drawn
as their own tangent-line measure, additively, over a faint isotropic line
haze (the ambient "measure of all lines"). The curves are never drawn directly;
they appear only as the place where their lines accumulate. A dark eye opens at
the center where the smallest curve's caustic closes.

### 02 · Almost All of the Cube  — *concentration of measure*  (2048²)
> *MathOverflow: "Concentration of measures on the unit hypercube" · Philosophy: "Are we dead almost everywhere?"*

For a point uniform in the `d`-dimensional cube `[-1,1]^d`, the norm `‖x‖` has
mean `~√(d/3)` but its **relative** spread shrinks like `1/√d`: almost all the
mass sits on a thin shell and the middle of the cube is empty. One ring per
dimension is drawn, nested outward; each is scattered by the actual normalized
norm. Low-dimensional rings are broad, fuzzy clouds; high-dimensional rings
collapse into razor-thin, cleanly separated circles. The dark hole in the
center is the emptiness of high-dimensional space.

### 03 · The Period of the Anharmonic  — *elliptic integral K*  (4096², the centerpiece)
> *MathOverflow front page: the exact period identity `T/T₀ = (2k/π)·K(k²−1)` for the quartic oscillator.*

The double-well potential `V(x) = −½x² + ¼x⁴`. Orbits in the `(x,p)` phase
plane are level sets of the energy `E = ½p² + V`. Each orbit's **period**
`T(E) = 2∮dx/√(2(E−V))` is an elliptic integral that **diverges
logarithmically at the separatrix** (`E=0`, the figure-eight): swings grow
infinitely slow near the barrier top — the visible meaning of the `K(k²−1)`
singularity. The contours are spaced equally *in period*, so they crowd into an
ever-finer nest around the figure-eight while thinning to nothing in the calm
hearts of the two wells. Warm = left well, green = right well, cool = the
over-barrier sea that circulates around both. Rendered at 8192² and downsampled.

---

### A small story

> Three ways of asking *how much*. The first measures a curve by counting the
> lines brave enough to touch it, and the curve only ever appears as rumor —
> the glow where its tangents agree. The second walks into higher and higher
> dimensions and finds the room emptying from the middle, everyone crowding to
> the walls, until the crowd is a single bright thread and the center is night.
> The third drops a marble into a valley with two floors and watches it nearly
> stop forever on the ridge between them — the closer to the edge, the slower
> the clock, the denser the rings of waiting. Measure, dimension, period: each
> a different word for the same shy question, and each answers it by drawing
> only the place where the counting piles up.

*Made by setting pixels. The math was kept honest; the only liberties were in
the light.*
