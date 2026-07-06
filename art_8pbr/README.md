# Where the Path Forks

*A procedural triptych on the **cut locus** — the thin, measure-zero skeleton
where the shortest way home stops being unique.*

Leave a point and walk in a straight line (a geodesic). For a while there is
exactly one shortest path back. Then, on a razor-thin set, something breaks:
two different roads home come out **exactly equal length**, or a whole family of
paths **refocuses** to a point. That set of indecision is the *cut locus* (and
its cousin the *conjugate locus*). Everywhere else the path is determined; only
on this seam does it fork.

Seeded by the live front pages of **MathOverflow** — *"When is the cut locus a
finite tree?"* — and **Philosophy.StackExchange** — *"Is the path of human
technological development predictable?"* The answer the geometry gives: yes,
predictable everywhere — except on a thin bright graph where it is genuinely,
provably undecided.

Every claim below is checked in `verify.py`.

---

## 1 · The Astroid of Return  ·  4096×4096  *(hero)*
![hero](01_preview.png)

Fire geodesics in **every** direction from a single point on a **triaxial
ellipsoid** and let them run. On the far side they do not scatter — they
**refocus** onto a four-cusped **astroid**: the *conjugate locus*. This is
**Jacobi's Last Theorem** (the conjugate locus of a generic point on an
ellipsoid has exactly four cusps), rendered by letting the geodesics draw their
own caustic. Brightness is the **fold density** of the geodesic congruence
(1 / how fast neighbouring geodesics spread) — where the map folds, light
piles up. The horizontal **electric-cyan segment** is the true *cut locus* (where
two equal-length shortest geodesics tie); note that it ends **exactly at two
cusps of the astroid** — the classical fact that the cut locus terminates on the
conjugate locus.

*Engine:* geodesics integrated in the ambient chart (`r'' ∝ −(r'ᵀAr'/rᵀA²r)·Ar`),
RK4, unit-speed and on-surface to machine precision; caustic = fold-density splat;
conjugate points = first perpendicular-refocus of the fan.

## 2 · The Ridge of Two Ways  ·  2048×2048
![p2](02_preview.png)

A wavefront leaves the warm source and sweeps a pond of stones, bending around
each one (a genuine **eikonal** solve, `|∇d| = 1`). Behind every stone the two
arcs of the *same* wavefront **collide** — and there the shortest path is no
longer unique: the **cut locus**, drawn in gold. Because the stones make the
domain **multiply-connected**, the cut locus is a finite **graph with cycles**,
not a tree — the literal answer to *"when is the cut locus a finite tree?"*

## 3 · The Ways Home Are Numbered  ·  2048×2048
![p3](03_preview.png)

On a **flat torus** the cut locus of a point is its **Wigner–Seitz cell**
boundary — a finite graph (the glowing cyan hexagon at the centre). But there
are higher ways home: the *k-th* **Brillouin zone** is where the origin is only
the *k-th*-nearest lattice image — the *k-th* shortest return.
`zone(x) = 1 + #{ lattice v ≠ 0 : |x−v| < |x| }`. Stacked, the zones are nested
star-polygon shells: a crystalline stained-glass mandala of every way home,
numbered.

---

### Verification (`verify.py`)
- **Piece 1:** sphere geodesic closes to `1e-12`; unit-speed exact; triaxial
  stays on-surface to `4e-16`; **conjugate-locus cusp count = 4** (Jacobi).
- **Piece 2:** `|∇d| = 1.000` off the cut locus (eikonal); arrival-direction
  jump `0.005 rad` off vs `0.81 rad` on the cut locus (two shortest paths of
  equal length collide); one cut arc behind each obstacle.
- **Piece 3:** 1st Brillouin zone area = lattice-cell area to `0.5%` (the
  Wigner–Seitz cell tiles the plane); zone index finite everywhere.

*Run:* `python ellipsoid.py && python hero_build.py && python hero_final.py`
(hero), `python piece2.py`, `python piece3.py`, `python verify.py`.
