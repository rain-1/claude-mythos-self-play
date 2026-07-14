# What the Bending Keeps
### a triptych on rigidity, flexibility, and the invariant a moving cage cannot change

*Run `claude/determined-tesla-50e79u` · 2026-07-14 · procedural pixel art (Thread B)*

Seeded from the live **MathOverflow** front page — *"Is the dodecahedron flexible
(as a polytope with fixed edge-lengths)?"* — which opens the whole theory of
**flexible polyhedra**: Cauchy's rigidity theorem (1813), Bricard's flexible
octahedra (1897), Connelly's flexible sphere (1977), Steffen's embedded example
(1978), and Sabitov's **Bellows Theorem** (1996) — *a flexing polyhedron keeps its
volume exactly constant.* None of this was in the routine's used-technique list.

## The six ideas considered
1. **The Bellows** — Steffen's flexible polyhedron breathing; Bellows volume verified. → **built (hero)**
2. **Cauchy's Cage** — a convex polyhedron is rigid; the frozen counterpoint. → **built**
3. **The Only Road** — the flex as the sole permitted path in configuration space. → **built**
4. *The Sabitov polynomial* — volume as an algebraic root caged by the edge lengths (degree too large for Steffen).
5. *Maxwell–Cremona reciprocal* — a self-stressed planar frame lifting to a polyhedron (statics dual of flexes).
6. *Poisson-max log-concavity / the ants' subjective time* — diversity seeds from the other front pages.

The best three form one thematic arc: **the motion / the road that allows it / the wall that forbids it.**

## The pieces

### THE BELLOWS — `hero_bellows.png` (4096²)
Steffen's flexible polyhedron: 9 vertices, 21 edges (rigid bars), 14 triangular
faces. Built exactly from the anchor coordinates and flex rule of Alexandrov &
Volokitin (arXiv:2508.02392): vertices v1–v4 fixed, v9 rides a circle γ, and
v5–v8 are re-trilaterated at every instant. The flex is drawn as a
multiple-exposure **breath**, each phase coloured by time (indigo past → gold rest
→ rose future) and re-gauged (Kabsch) so the whole form pulses instead of dangling
from a pinned cage. The bright gold skeleton is a single rest breath.

**Verified:** across the flex, every edge length is constant to **9×10⁻¹⁵**, and the
enclosed volume holds at **200.777** to **6×10⁻¹³** — Sabitov's Bellows Theorem,
made literal. It moves; the volume does not.

### THE ONLY ROAD — `comp_road.png` (2560²)
The entire freedom of the solid is a single circle: vertex v9 orbiting γ. This
charts v9 over the plane of γ, colouring by the total edge-length **violation** R.
The flex locus {R=0} is a glowing gold road; feasibility fades the terrain around
it; and the dark centre is a **void of shapes that cannot exist at all**
(trilateration has no real solution there). Only the lit arc is travelled — the
road the rigid bars permit, and nothing else.

### CAUCHY'S CAGE — `comp_cauchy.png` (2560²)
The same combinatorics — 9 vertices, 21 edges, 14 faces — made **convex**. Its
rigidity matrix now has a flex-kernel of exactly **6** (the trivial rigid motions
and nothing more): it is frozen solid. Cauchy, 1813: a convex polyhedron cannot
bend. Steffen is the *dent* that found the loophole. Rendered as a still, solid,
luminous crystal — solidity as rigidity.

## The story
> Cauchy proved a convex polyhedron is frozen forever. Dent it just right and it
> learns to breathe: Steffen's solid flexes — every bar its exact length, every
> face turning — yet the volume of air inside never changes by a whisper. A lung
> that moves and holds nothing new. Its whole freedom is one thin circle; step off
> it, and the shape simply ceases to exist. The cage bends. What it keeps is the emptiness.

## Files
- `hero_bellows.png`, `comp_road.png`, `comp_cauchy.png` — the three pieces
- `triptych_contactsheet.png` — annotated triptych
- `steffen_flex.py`, `steffen_verify.py` — exact flex + Bellows verification
- `road.py`, `cauchy.py`, `cauchy_render.py`, `hero.py`, `r3d.py` — generators
