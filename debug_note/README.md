# Debug Note — The von Dyck Trick

> **When a construction is governed by a group, verify a group *relation*. An
> algebraic identity localises a geometric bug faster than any amount of staring
> at pixels.**

![The von Dyck debug trick](von_dyck_debug.png)

## What happened

While building the Klein quartic's `{7,3}` heptagon tiling (gallery `psl168/`,
Figure 4), the central heptagon and first ring came out perfect — but a few
rings out, the tiles dissolved into an overlapping **scribble** (left panel).

The renderer was fine. The **geometry** was wrong. I had placed each heptagon's
vertices at radius

```
cosh R = cos(π/3) / sin(π/7)        # WRONG — this is the inradius
```

which is the distance from a heptagon's centre to an *edge midpoint*
(the inradius), not to a *vertex* (the circumradius). With the vertices in the
wrong spot, the hyperbolic rotations meant to glue neighbouring tiles no longer
lined up, so copies drifted across one another — and the error compounded with
each ring, which is why the centre looked fine and the outside looked insane.

## The trick

The symmetry group of the `{p,q}` tiling is the **von Dyck group**

```
Δ(2,3,7) = ⟨ a, b | a⁷ = b³ = (ab)² = 1 ⟩
```

where `a` rotates a heptagon by 2π/7 about its centre, `b` rotates by 2π/3 about
a vertex, and `ab` *must* be an involution (a half-turn about an edge midpoint).

So instead of debugging pixels, I asked the computer a one-line question:

```python
ab = a @ b
defect = max_abs( (ab @ ab) / (ab@ab)[0,0]  −  I )
```

| vertex radius | `(ab)²` defect | tiling |
|---|---|---|
| `cos(π/3)/sin(π/7)` (inradius, **buggy**) | **0.078** | scribble |
| `cot(π/7)·cot(π/3)` (circumradius, **fixed**) | **5 × 10⁻¹⁷** | perfect |

The buggy radius missed the relation by 0.078 — loudly **NO**. The correct
circumradius satisfied it to machine precision, and the tiling on the right
snapped into place.

## Why it generalises

This is a reusable move for *any* structure with a known presentation:

- **Tilings / crystallographic & von Dyck groups** — check `a^p = b^q = (ab)^r = 1`.
- **Polytopes & Coxeter groups** — check the braid relations of the generators.
- **Lie-theory / triality code** — I used the same idea earlier to confirm the
  triality matrix really had order 3 (`T³ = I`) before trusting any animation.
- **Quaternion / octonion bases** — check `i² = j² = k² = ijk = −1`, the
  composition law `|xy| = |x||y|`, before drawing anything.

A picture can hide a subtle error in plain sight. A defining relation cannot:
it is either satisfied or it is not, and the size of the violation points
straight at the broken ingredient.
