# Which level decides — the Spectre, verified

**Object.** The Spectre (Smith, Myers, Kaplan, Goodman-Strauss, 2023): a single 14-sided
tile that tiles the plane only aperiodically, *without reflections* (the "chiral aperiodic
monotile" — the strictly-chiral version is the curved-edge tile drawn here).  The
substitution system (nine metatile labels Γ Δ Θ Λ Ξ Π Σ Φ Ψ, seven children per supertile,
the Γ "Mystic" being a pair of tiles one of which is turned by 30°) is ported from Craig
Kaplan's public `spectre.js` into `spectre.py`.

**Checks made on the port (level 4, 4,401 tiles; the hero is a window on level 5, 34,649 tiles).**
* Every tile's placement matrix has det = +1.000000 and every tile polygon has the same
  orientation sign: *all tiles are proper rotations of one shape, none reflected* (the
  substitution reflects once per level, and that reflection is applied uniformly).
* Rasterized at 2400², sum of tile areas / union area = 0.9956 with the only overlap being
  shared-edge pixels (7.6% of pixels lie on an edge at that resolution): the tiles neither
  overlap nor leave holes.  In the hero window at 8192² the id-map has **0 uncovered pixels**.
* Substitution matrix Perron eigenvalue = 7.8729833462 = **4 + √15** to 10 digits (the
  inflation factor of tile counts per level).
* Share of the 30°-turned Mystic partner ("Gamma2") among tiles: 0.11270 at level 4,
  0.11273 in the hero window.

**What the hero paints.**  Base pigment = label of the tile's level-2 supertile (9 pastel
pigments); lightness = a random gain per level-1 supertile (and a mild one per level-3),
plus a per-tile jitter; coral glaze on every Gamma2 tile; ink weight by hierarchy: tile
edges (fine graphite) < level-1 borders < level-2 borders (ink) < level-3 borders (ink + soft
halo).  Tile edges follow Kaplan's curved outline (cubic Béziers, bulge 0.5 alternating
in/out along the 14 edges — the curve that forbids reflections).  Painter's unfinished edge:
the tiling fades to paper toward the frame along an irregular front.

Why "which level decides": the philosophy front page was arguing downward causation —
if micro-laws are complete, what work is left for the higher level?  Here the tile's shape
(micro) forces the supertile hierarchy (macro), and yet *where this tile goes* is only
explicable through its level-2, level-3, … ancestors.  Both directions of "because" are
true at once, and neither is shorthand for the other.
