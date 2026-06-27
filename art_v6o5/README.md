# What the Loop Remembers

*A procedural triptych on **monodromy** — what changes, and what refuses to change,
when you go around.*

Generated 2026-06-26 · branch `claude/beautiful-heisenberg-v6o5fn`.
Seeded by the live front pages of **MathOverflow** (*"Kauffman bracket for Abelian
anyons"*, *"Bing's house with two rooms is contractible"*, Lewin's dilogarithm
formula) and **Philosophy.SE** (*"the difference between the absence of presence
and the presence of absence"*, *"why do philosophers restrict the realm of the
possible"*).

Three objects, one question: **when a path comes back to where it started, is it
the same path?** A loop can *remember* how it was wound (and never be undone); a
loop can be *tamed* until it forgets; or a whole space can forget every loop it
contains, and still refuse to be simplified.

---

## 01 · The Braid That Remembers  — *the loop that cannot forget*

![The Braid That Remembers](01_the_braid_that_remembers.png)

Abelian anyons are particles living in two dimensions plus time. Drag one around
another and the wavefunction picks up a phase that depends only on **how** the
paths wound — not on the details of the journey. Their histories are a **braid**,
and the **Kauffman bracket** assigns to that braid an invariant of the weave.

A *closed* braid is a link. Here it is the **T(20,12) torus link** — the closure
of the braid word `(σ₁σ₂…σ₁₉)¹²` — which splits into **gcd(20,12)=4** components,
each a `T(5,3)` knot, four anyons whose world-lines can never be combed apart.
The over/under weave — *the thing the bracket remembers* — was not painted in; it
falls out of the honest 3-D geometry. Every strand lives on a torus; a strand in
front simply hides the one behind (painter's algorithm by depth). 4096×4096.

## 02 · A House That Forgets Every Loop  — *trivial, yet not trivialisable*

![A House That Forgets Every Loop](02_a_house_that_forgets_every_loop.png)

**Bing's house with two rooms.** The upper room can be entered only by a chimney
(amber) that rises from the *bottom* face, straight up **through the lower room**,
and opens above. The lower room can be entered only by a chimney (teal) that drops
from the *top* face, down **through the upper room**, and opens below. Two walls
(gold) finish it.

The house is **contractible**: it has no hole a loop could snag on; topology says
you can shrink the entire thing to a single point, so *every loop is forgettable*.
And yet it is **not collapsible** — there is no free face to fold from, no honest
first step toward simplifying it. A thing that *is* trivial, that you cannot
*make* trivial by any local move. Sphere-traced as a cut-away dollhouse so the two
impossible chimneys can be watched threading the wrong rooms. 2048×2048.

## 03 · The Tamed Logarithm  — *the loop taught to forget*

![The Tamed Logarithm](03_the_tamed_logarithm.png)

The dilogarithm `Li₂(z)` is multi-valued: carry it once around `0` or `1` and it
returns *changed* — that change is its **monodromy**. The **Bloch–Wigner function**

```
    D(z) = Im Li₂(z) + arg(1−z)·log|z|
```

is the unique combination whose monodromy **cancels**: a single-valued, real,
real-analytic function on `ℂ∖{0,1}`. It is dead **zero on the whole real line** —
flat, degenerate tetrahedra of zero volume, *the presence of an absence* — and
rises to `±Cl₂(π/3) ≈ 1.015` at `e^{±iπ/3}`. Geometrically `D(z)` is the hyperbolic
volume of the ideal tetrahedron `(0,1,∞,z)`, the brick from which every hyperbolic
3-manifold's volume is built. The level sets are drawn equally spaced *in volume*,
so they crowd toward the two cusps where the gradient diverges — singular detail,
for free. 2048×2048.

---

### The story

> Three knots were asked to undo themselves. The braid laughed: *I am the going-
> around; remove it and there is no me.* The house tried, and found every wall was
> someone else's only door — trivial, the geometers swore, yet it could not take
> the first step. Only the dilogarithm obeyed: it folded its two infinities over
> each other so exactly that, going around, you arrive carrying nothing — and on
> the real line, where the tetrahedra lie flat, it had already forgotten how to be
> anything at all. A loop is just a road that returns. What it brings back is the
> whole question.

---

## Two more, by request — on irreducibility and composition

A different pair, built after the triptych: not about loops, but about *how much
work it takes to know a thing*.

### 04 · The Only Way to Know — *computational irreducibility, made visible*

![The Only Way to Know](04_the_only_way_to_know.png)

Rule 30 is a one-line cellular automaton (`s' = s₋ XOR (s OR s₊)`) that
manufactures genuine chaos from order. Wolfram's claim of **computational
irreducibility**: there is no shortcut — to know row *N* you must run rows
`1…N−1`. We make it visible by taking two universes whose start rows differ in a
**single bit** and XOR-ing their entire space-times. Outside the bit's reach the
histories are *identical* (dead black); inside, they have diverged into mutual
chaos. The damage spreads at most one cell per step, so its envelope is a
discrete **light cone** — the right edge ruler-straight at the speed limit, the
left edge a fractal front that advances only as fast as the chaos allows. The
teal ground is the irreducible Rule-30 substrate; the gold triangle is one bit's
worth of unforeseeable consequence. 2048×2048 (one cell = one pixel — the grain
*is* the point). *(Backup idea from the original six, promoted by request.)*

### 05 · The Cube That Composes to One — *Bhargava + Conway*

![The Cube That Composes to One](05_the_cube_that_composes_to_one.png)

A 2×2×2 integer cube, sliced three ways, gives three binary quadratic forms of
one shared discriminant. **Bhargava** (2004) proved they compose to the identity
of the form **class group** — a hand-built rediscovery of Gauss's composition
law. We take the cube `(-1,-1,-1,2,0,1,2,2)`: discriminant **−23**, the smallest
with three distinct classes. Its forms `(1,1,6)`, `(2,1,3)`, `(2,-1,3)` are the
*entire* class group `{1, g, g²}`, and `1·g·g² = 1` — verified here by Dirichlet
composition. Each form is drawn as its **Conway topograph**: a trivalent tree
whose faces are primitive vectors `(p,q)` labelled by `Q(p,q)`, obeying the
parallelogram law `Q(u+v)+Q(u−v)=2Q(u)+2Q(v)`, warm at the well and cooling
outward. 2048×2048 annotated plate. *(Backup idea from the original six,
promoted by request.)*

---

*Technique notes: honest math first (functional equations of `Li₂` verified to
1e-16; torus-link components from `gcd`; Bing's complex assembled from thin-slab
SDFs; Gauss composition verified against the C₃ group of D=−23; Rule 30 light
cone simulated 2× wider than the crop so the periodic boundary never wraps into
frame), then the picture draws itself. High-entropy fields (the CA) are kept at
2048² — both the right scale for the visible grain and a sane file size, since
noise barely compresses.*
