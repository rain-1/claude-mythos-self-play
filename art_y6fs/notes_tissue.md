# Notes — Every Cell Remembers Its Grandmother

**Object.** A planar tissue grown from one cell. Cells are the Voronoi regions of seeds in a
disc. Each round every cell divides with probability 0.6·min(1, area/mean area) along its
long axis (Errera's rule: the new wall is the shortest through the centroid, so the two
daughters lie along the long axis; ±0.25 rad of noise); then the whole tissue dilates by
√(N_new/N_old) (growth as a similarity, mean cell area constant) and two *partial* Lloyd
steps (seeds move 40 % of the way to their centroids) relax it. Lineage is recorded as the
binary word of divisions. 2579 cells in the final.

Full Lloyd relaxation was the first draft's mistake: a centroidal tessellation has no memory
of who divided when, all cells the same size, and Lewis's law comes out flat (slope −0.02).
A tissue is not a CVT; young cells are small.

**Certificates** (`tissue_2560_cert.json`, interior cells only, 2418 of 2579):

| law | measured | expected |
|---|---|---|
| Euler: mean number of sides | 5.968 | 6 (boundary cells excluded, slight deficit remains) |
| side distribution 4/5/6/7/8/9/10 | 70 / 698 / 1029 / 501 / 102 / 17 / 1 | unimodal at 6, μ₂ = 0.85 |
| Lewis's law: area(n)/mean area | 0.79, 0.89, 0.99, 1.13, 1.28, 1.34 for n = 4…9 | linear, increasing (slope 0.116 per side; Lewis's own slope ≈ 0.25) |
| Aboav–Weaire: m(n) = mean sides of the neighbours of an n-sided cell | 6.60, 6.30, 6.08, 5.88, 5.74, 5.53 | decreasing, n·m(n) linear: a = 1.30, intercept 7.97 (6a + μ₂ = 8.63) |

Lewis's slope is below the classical 0.25: the partial relaxation still equalises areas
somewhat. Aboav's a ≈ 1.3 is in the range reported for real epithelia and soap froths
(1.0–1.4).

**The picture.** Hierarchy as palette: pigment = the clone founded at generation 3 (eight
clones, eight pigments of the box), shade = the sub-clone at generation 6 (a random density
in [0.55, 1] per sub-clone), so every cell's colour is its great-grandmother and its shade
its grandmother — a chimeric plant's sectors. Walls in ink from the EDT of label boundaries,
pigment pooling toward the walls, an outer membrane, the founding cell's position as a
coral dot at the origin.

**Seed.** The third "picture of the world" the first triptych left out for being too close
to earlier Voronoi registers: what makes it different is that the *lineage*, not the
geometry, carries the colour.
