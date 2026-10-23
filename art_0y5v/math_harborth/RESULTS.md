# Integral plane drawings of maximal planar graphs (Harborth's conjecture)

All drawings: straight-line, crossing-free, no vertex lies on a non-incident edge, every edge has integer
length. All exact data are in `drawings.json` (float coords, exact coords as strings, `[i,j,length]`, CCW faces).

| graph | field of coords | edge lengths | max edge | min face angle |
|---|---|---|---|---|
| octahedron (4-reg) | Q(√3) | 26 (outer △), 4 (inner △), 14 (×6) | **26** | 16.4° |
| **icosahedron (5-reg)** | Q(√3), C3-symmetric | 159 (outer △), 39 (inner △), 16, 49, 55, 56, 109 | **159** | 10.8° |
| icosahedron, alt. | Q (integer coords), mirror-symmetric | 12…287 | 287 | 5.1° |
| pentagonal bipyramid | Q (integer coords) | 12…119 | 119 | 9.5° |
| snub disphenoid | Q (integer coords) | 12…119 | 119 | 9.5° |
| triakis tetrahedron (deg 6) | Q (integer coords) | 21…170 | 170 | 9.5° |

**Icosahedron** (vertex 0–2 = outer face, 3–8 = hexagon, 9–11 = inner face): coordinates are
(x/2, y·√3/2) with (x,y) =
(−159,−53),(159,−53),(0,106),(−71,−13),(−55,−29),(55,−29),(71,−13),(16,42),(−16,42),(39,−13),(0,26),(−39,−13).
The rotation by 120° maps the drawing to itself, so only 10 edge orbits had to be made integral.
Integer-coordinate version: (0,224),(63,−56),(−63,−56),(−30,0),(0,0),(30,0),(15,−20),(0,−40),(−15,−20),(15,−8),(0,−28),(−15,−8).

**Octahedron**: (0,0),(13,13√3),(−13,13√3),(0,10√3),(−2,8√3),(2,8√3).

## Method
Search over lattices Z×√k·Z (point (x,y) = (x, y√k); squared length dx²+k·dy²), with symmetry to cut down
the number of conditions:
* mirror x→−x induced by an involutive automorphism fixing the outer face (`msearch.py`, `ico_mirror3.py`);
  vertices on the axis only need 1 coordinate, and edges crossing the axis are free;
* C3 rotation in the Eisenstein lattice (`ico_c3.py`): icosahedron = 4 vertex orbits, 10 edge orbits;
* plain backtracking for comparison (`gsearch.py`).
Partial drawings are pruned by face orientation and crossings.

## Verification (`finalize.py`, run `python3 finalize.py`)
Exact integer arithmetic. Every squared length (dx²+k·dy²)/s² is checked to be the square of an integer.
Planarity is checked with exact integer orientation tests on the lattice coordinates. The map to the plane is
affine, so this test is valid there too. Each check covers all edge pairs and vertex–edge incidences, and
counts 2n−5 bounded triangular faces. Lengths were checked again independently with sympy.

## Completeness within each searched class
* Octahedron: 26 is the smallest max edge found. The mirror search covered lengths ≤ 120–150 for k ∈ {1,2,3,5,6,7,10,11,13,14,15,21,30,35,39,42,51}, and the general search covered lengths ≤ 100 for k ∈ {1,2,3,5,6,7,11,15}.
* Icosahedron: 159 is the smallest max edge among C3-symmetric Eisenstein-lattice drawings with max edge ≤ 350.
  287 is the smallest among mirror-symmetric integer-coordinate drawings with max edge ≤ 800.
* A non-symmetric search found no icosahedron with max edge ≤ 60 (k=1, 3).

## Open
Smaller or fatter (min angle > 11°) icosahedron drawings without symmetry or in other fields; the general
conjecture; no lengths ≤ 60 for the icosahedron/bipyramid were found.
