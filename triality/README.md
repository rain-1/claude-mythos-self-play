# Triality — a deep exploration

*Spin(8), the 24-cell, and the only threefold symmetry in the world of simple
Lie groups.*

Triality is the strangest and most beautiful of the symmetries of symmetry. This
gallery is an attempt to see it from as many sides as possible — as an algebra,
as a diagram, as a polytope, as a rotation you can watch, as a group you can
walk, and as the exceptional jewel it leaves behind. Every figure here was
generated from first principles and the group theory was **verified in code**
(see `t4d.py`): 24 vertices in three classes of 8, 96 edges, symmetry group of
order 1152, and an explicit order-3 isometry `T` cycling the three 16-cells.

---

## 1. What triality is

The Lie algebra **so(8)** (the infinitesimal rotations of 8-dimensional space)
is the rank-4 algebra `D₄`. It is exceptional among *all* simple Lie algebras in
one specific way:

- Almost every simple Lie algebra has an outer-automorphism group that is
  trivial or, at most, `Z/2`.
- `D₄` alone has outer-automorphism group `S₃` — the full symmetric group on
  three things. **The order-3 elements of that `S₃` are triality.**

The reason is visible in the **Dynkin diagram** (`02_d4_dynkin_triality.png`):
`D₄` is the only diagram shaped like a three-pointed star — a central node with
three identical legs. You can permute the three legs any way you like, and the
algebra doesn't notice. That `S₃` of leg-permutations is `Out(so(8))`.

## 2. The three eights

`so(8)` has three *different* irreducible representations that all have the same
dimension, 8:

- **8_v** — the **vector** rep (azure here): ordinary 8-dimensional space.
- **8_s** and **8_c** — the two **chiral spinor** reps (gold and rose).

For any other `so(n)` the vector and spinor reps have different dimensions and
can never be confused. Only in 8 dimensions do all three coincide in size — and
triality is exactly the symmetry that **cyclically permutes them**:
`8_v → 8_s → 8_c → 8_v`. The three legs of the Dynkin diagram *are* these three
representations.

## 3. The geometric home: the 24-cell

Each of the three 8-dimensional reps has a **weight diagram** — 8 points in the
4-dimensional Cartan space:

- `8_v`: the 8 points `±e_i` (vertices of a 16-cell / 4-orthoplex)
- `8_s`: the 8 points `(±½,±½,±½,±½)` with an even number of minus signs
- `8_c`: the same with an odd number of minus signs

Together these 24 points are the vertices of the **24-cell** — the unique
self-dual regular 4-polytope, with 24 vertices, 96 edges, and 24 octahedral
cells, *the* polytope with no analogue in any other dimension. Its three
16-cells are precisely `8_v`, `8_s`, `8_c`, and **triality is the rotation of
4-space that cycles them**.

- `03_the_24cell.png` — the 24-cell in 3D, three-coloured.
- `01_d4_coxeter_rose.png` — the same polytope projected onto the F₄ Coxeter
  plane: a 12-fold rose of two rings of twelve, 96 edges weaving the three
  colours.
- `06_three_interlocking_16cells.png` — the decomposition `24 = 8 + 8 + 8`
  drawn as three interpenetrating cross-polytopes.

I found the triality rotation explicitly by searching the 1152-element symmetry
group `W(F₄)`: it is the clean matrix

```
T = ½ · [ -1  1  1  1 ;  -1  1 -1 -1 ;  -1 -1  1 -1 ;  -1 -1 -1  1 ]
```

with `T³ = I`, orthogonal, sending each 16-cell onto the next.

## 4. Triality in motion

- `anim_24cell_spin.gif` — the 24-cell turning by an *isoclinic* (Clifford)
  double rotation, the rigid hypnotic spin unique to 4 dimensions.
- `anim_triality_cycle.gif` — **triality itself.** We apply `T^t = exp(t·logT)`
  continuously. The polytope rotates and, every one-third of the loop, lands
  back on the *identical* 24-cell — but the colours have advanced one step. The
  shape is invariant; only the names cycle. That is the outer automorphism, made
  visible.

## 5. The octonion connection

Triality and the **octonions** are two faces of one fact. The octonion
multiplication map is a bilinear product `8_v × 8_s → 8_c`, and it is
*triality-equivariant* — rotate the inputs by triality and the output rotates to
match. The octonion multiplication table is the **Fano plane** (see the
companion piece `art_uh5/04_the_triality_engine.png` in this repo), and that
Fano emblem, "tripled by triality", is the same `S₃` acting that we see here on
the Dynkin legs and the 16-cells.

## 6. What triality leaves behind: G₂

If you ask which part of `so(8)` is **fixed** by triality — invariant under the
whole `S₃` — the answer is the smallest of the exceptional Lie algebras:

- fixed by an order-2 element: `so(7) = B₃` (dimension 21)
- fixed by the full triality `S₃`: **`G₂`** (dimension 14)

`05_g2_fixed_by_triality.png` shows the G₂ root system — 6 short roots (inner
hexagon) and 6 long roots (outer hexagram), the densest rank-2 root system, a
Star of David. The exceptional groups begin where triality's symmetry ends.

## 7. A Cayley diagram in 3D

`04_permutohedron_cayley_s4.png` — the Cayley graph of the symmetric group `S₄`
drawn as the **permutohedron** (a truncated octahedron). Its 24 vertices (one
per permutation — and 24, like the 24-cell) are joined by edges coloured by the
three generators `(12), (23), (34)`; the square faces are the relations
`(s_i s_{i+1})² = 1` for non-adjacent generators and `s_i² = 1`, the hexagonal
faces are `(s_i s_{i+1})³ = 1`. The whole group presentation, made solid — the
cleanest way to *walk* a finite group in three dimensions.

---

## Files

| file | what |
|---|---|
| `t4d.py` | verified 4D math: 24-cell, edges, triality `T`, Coxeter planes |
| `tdraw.py` | glowing additive 3D renderer (bloom + depth cueing) |
| `01_d4_coxeter_rose.png` | 24-cell on the F₄ Coxeter plane (12-fold rose) |
| `02_d4_dynkin_triality.png` | the D₄ Dynkin diagram + the S₃ that is triality |
| `03_the_24cell.png` | the 24-cell in 3D, three-coloured |
| `04_permutohedron_cayley_s4.png` | Cayley diagram of S₄ in 3D |
| `05_g2_fixed_by_triality.png` | G₂ root system — the fixed subalgebra |
| `06_three_interlocking_16cells.png` | `24 = 8_v + 8_s + 8_c` |
| `anim_24cell_spin.gif` | isoclinic 4D rotation |
| `anim_triality_cycle.gif` | the triality automorphism in motion |

## A closing thought

Most symmetries permute *things*. Triality permutes the very *kinds* of things —
it cannot decide whether a point is a vector or a spinor, because in eight
dimensions there is no honest difference. It is the universe admitting that some
of its most basic categories are a matter of viewpoint, and that the viewpoint
can be rotated. The 24-cell is just the place where you can hold all three
viewpoints in your hand at once.
