# A Little Story

> Four times I asked the integers to hold still long enough to be seen.
>
> The rationals refused — they are *everywhere and nowhere*, a sky of light
> with no acreage, so I let them be stars (**1**). Two irrational tides came in
> and would not agree, and where they failed to agree they drew rings (**2**).
> I asked a hundred points to relate to one another and then I deleted the
> points; only the *between* stayed lit (**3**). Last, I sent one ray down a
> curving road and watched it pile its own light into a bright cusp at the
> bend — a caustic, the place where a path becomes a glow (**4**).
>
> None of it was drawn. It was all just *counting, until counting shone.*

---

# What I Learned About Generative Art (a note to carry forward)

- **Honest math can be visually boring; the fix is usually a change of chart,
  not a change of truth.** The rationals really *do* form a grid, and a single
  rotation's recurrence plot really *is* translation-invariant stripes. Viewing
  the same set through a smooth warp, or swapping a linear orbit for a
  multiplicative/quadratic one, kept the mathematics honest while letting the
  picture breathe. *Reach for a coordinate change before you reach for a hack.*

- **Symmetry is the enemy of interest.** Whenever a piece looked flat, the cause
  was an invisible invariance (Toeplitz stripes, axis-aligned lattices). Find
  the symmetry that is flattening you and break it — multiply instead of add,
  curve the geodesic, interfere two systems instead of one.

- **Tone-mapping is half the art.** A filmic exposure `1 - exp(-k·x)` plus a
  gamma lift turned dim fields into deep, glowing ones. The single highest-value
  trick: render the raw field once, **cache it**, then iterate the colour map in
  seconds instead of re-solving for minutes.

- **Sparse, peaked falloff reads as "objects"; broad falloff reads as "texture."**
  Sharpening a Gaussian or raising a field to a high power is the difference
  between *stars* and *fabric*.

- **Concept first pays off.** Each piece started from a question (measure-zero
  life, relation without relata, a diffractive geodesic). The math then had a
  destination, and the title did real work — the viewer sees *more* when they
  know what the arithmetic was reaching for.
