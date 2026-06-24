# Three Ways the World Coheres

A procedural-art triptych (run 2026-06-24). Each piece sets the pixels of a PNG
from a single mathematical idea, with no hand-drawn marks. Seeded by the live
front pages of philosophy.stackexchange.com and mathoverflow.net.

| # | piece | size | technique | the question it answers |
|---|---|---|---|---|
| 01 | **Order Without Period** | 2048² | cut-and-project / de Bruijn pentagrid → Penrose rhombi | *Can there be order that never repeats?* — MathOverflow: "generating functions for objects with irrational sizes" |
| 02 | **The Unreasonable Packing** | **4096²** | Apollonian gasket via Descartes' Circle Theorem (complex form) | *Why is mathematics so unreasonably effective?* — every curvature here is a whole number nobody assigned |
| 03 | **Emergence** | 2048² | critical site percolation (p≈0.5927) + connected-component labelling | *Does emergence make things illusory?* — philosophy.SE, same day |

## The pieces

**01 — Order Without Period.** Slice a periodic 5-dimensional lattice at an
irrational angle and project the shadow into the plane. What falls out is a
Penrose tiling: two rhombi, laid so the pattern never once repeats yet never
makes a mistake. The facet shading is the tiles' own orientation — the famous
3D-cube shimmer, free.

**02 — The Unreasonable Packing (centerpiece).** Four mutually tangent circles,
then Descartes' theorem applied forever: each gap demands exactly one more
circle, and its curvature is forced by the three around it. Start from
(−1, 2, 2, 3) and the arithmetic never leaves the integers — whole numbers
precipitating out of pure geometry, recursing past the pixel. Zoom into any cusp
and the cascade is still going.

**03 — Emergence.** Sixteen million cells each flip a weighted coin, alone,
caring about nothing. At exactly the critical probability a single gold cluster
suddenly reaches from edge to edge — a connected, fractal whole with no global
cause. The grain you see up close is the coin-flips; the coral you see from
across the room is the thing they became.

## A tweet-sized story

> Three ways the world coheres without being told to: a tiling that never repeats
> yet never slips; circles that settle into whole numbers no one assigned; one
> shape spanning the void, sewn from coin-flips that never met.
> Order keeps arriving uninvited.

## Reproduce

```bash
pip install numpy scipy Pillow
python3 scripts/quasicrystal.py 2048 32 01_order_without_period.png
python3 scripts/apollonian.py  4096 16000 02_the_unreasonable_packing.png
python3 scripts/percolation.py 2048 crit 03_emergence.png 19
```
