# The hero's mathematics — an Osgood arc with area exactly 2/3 (MO 514732-adjacent)

MO 514732 asked whether every nowhere dense closed set lies in the boundary of
a regular open set. The hero draws the classical extreme creature of that
territory: an **Osgood curve** — a Jordan arc (continuous injective image of
[0,1]) that is nowhere dense, has empty interior, and still carries positive
2-D Lebesgue measure.

## Construction (Knopp), as implemented in `osgood.py`

State = triangle with (entry E, exit F, apex C). Split:

    D1 = E + d1(F−E),  D2 = E + d2(F−E),  d1 = (1−r_k)/2, d2 = (1+r_k)/2
    child1 = (E, C, D1),  child2 = (C, F, D2)     [meet ONLY at C]

discarding the open wedge (D1, D2, C) — fraction r_k of the parent's area.
With r_k = 1/(k+2)² at level k:

    area = A₀ · Π_{k≥1} (1 − 1/(k+2)²) = A₀ · lim_N (2/3)(N+1+…)/… = **A₀ · 2/3**

exactly, by the telescoping Π_{m=2}^N (1−1/m²) = (N+1)/(2N).

The split is *balanced*: both children get area fraction (1−r_k)/2, so the
arc-time pushforward measure equals normalized Lebesgue measure on the arc.
Hence in the render **hue = time along the arc and brightness = honest 2-D
measure**, and any time-interval [t, t+δ] of the journey owns exactly δ·(2/3)A₀
of the estate — the lit stretch in the hero is such an interval (δ = 4.2%,
verified to rel. err. 1e-7 at depth 26; a *dyadic-aligned* window verifies to
1.4e-15).

## Certificates asserted at build time

- chain continuity: child1.exit = child2.entry exactly; all 8,192 subtree
  boundaries bit-exact at depth 26 (67,108,864 leaves);
- leaf-area sum = A₀·Π(1−r_k) to rel. err. < 1e-9 (shoelace);
- sibling bases disjoint (d1 < d2 strictly) at every level — the injectivity
  skeleton of Knopp's proof;
- interior mean density ≈ local product of the wedge factors whose wedges
  meet the probe box (0.74 observed vs 0.69 full product — the discrepancy is
  the coarse wedges the box dodges, not an error).

## Small observations worth keeping

- The multi-scale "ambient occlusion" in the render is honest mathematics:
  it is the ε-neighborhood density of the limit set at four dyadic scales —
  a picture of HOW the set fails to be Lebesgue-density-1 at its cracks.
- Because every sub-arc has positive area, the curve has Hausdorff dimension
  2 while being a homeomorph of [0,1] — essence and accident at maximum
  divergence. With r_k → 0 fast the same code draws arcs of area arbitrarily
  close to A₀ (Osgood's own family); with r_k ≡ 0 it degenerates to the
  Sierpiński–Knopp space-filling curve (no longer injective) — the fat arc
  is *strictly between* the thin curve and the filled triangle.
