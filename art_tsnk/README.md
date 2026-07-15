# WHAT RETURNS IN FIVE

*A triptych. One recurrence, three worlds.* — run `claude/cool-edison-tsnkhu`, 2026-07-14.

Seeded from the live MathOverflow front page (*"Cluster algebras of type A and X"*,
Fock–Goncharov λ-lengths and shear coordinates) and the live Philosophy.SE front
page (*"What exactly is dialectical about the wave-like progress diagram?"* — progress
that must **return**).

At the bottom of cluster type A₂ lives one little map — the **Lyness recurrence**

```
        y_{k+1} = (1 + y_k) / y_{k-1}
```

and its one astonishing property: **every orbit comes back after exactly five steps.**
No approximate return, no return "in measure" — five, for every point, forever
(Zamolodchikov periodicity of the A₂ Y-system). The same recurrence surfaces, wearing
three different costumes, in dynamics, in arithmetic, and in spherical geometry. Each
panel is that one law made visible in one of its worlds, and each **verifies the law in
its own terms** (`verify.py`, all checks pass).

---

## I · The Golden Anchor — *dynamics* (hero, 4096²) — `hero_final.png`

The Lyness map `(x,y) → (y, (y+1)/x)` on the plane, charted in `(ln x, ln y)`. Its
orbits ride an invariant pencil of cubics `(x+1)(y+1)(x+y+1) = K·xy`; I draw the level
sets as growth-ring caustics — ellipses hugging the fixed point, softening toward
pentagons at the rim (the tropical limit of the pencil). Every ring is threaded with the
**envelope of its own 5-cycle chords** `p→f(p)`, and three chosen shells are flooded with
the chords themselves as gold/violet light-fog. Two explicit five-cycles blaze as
constellations: a gold pentagon `p→f(p)→…` and its cyan pentagram `p→f²(p)`.

The pupil of the eye is the map's unique positive fixed point — and it is exactly the
**golden ratio** `(φ, φ)`. There the invariant `K` bottoms out at its minimum
`(φ+1)²(2φ+1)/φ² = 11.0901699…`, and the map rotates neighbours by rotation number
**1/5** — the reason five is the period. Everything returns; the golden point is the
still centre it all returns *to*.

Verified: exact period 5 over 2000 random rational seeds (`Fraction` arithmetic, 0
failures); invariant exactly constant along orbits; fixed-point residual 0; rotation
number 0.200000.

## II · The Cloth — *arithmetic* (companion, 2560²) — `frieze_final.png`

The very same recurrence over the integers is a **Conway–Coxeter frieze**. Take a random
triangulation of a 56-gon; count the triangles at each vertex (the *quiddity*); grow a
band of numbers in which every 2×2 diamond obeys `ad − bc = 1`. The Conway–Coxeter
theorem then works three miracles at once: **every entry is a positive integer**, the
band **closes** back into a row of 1s, and it carries a glide symmetry. I weave one full
period as a diamond lattice of beads, each lit by `log₂` of its entry — bright veins run
where large numbers chain out of the busy vertices (max entry here: **4030**).

The cyan beads are the theorem's secret: an interior entry equals **1** exactly at the
**diagonals of the triangulation** — so the scattered cyan constellation *is* the
triangulation, woven bodily into the cloth. The generating polygon glows as a maker's
seal in the corner; count its diagonals and you count the cyan lights. The cloth
remembers the shape that made it.

Verified: closure row of 1s; all entries positive integers; every diamond `ad−bc=1`;
glide symmetry; and the 1-cells ↔ diagonals bijection holds exactly (53 of each).

## III · Five Right Angles — *geometry* (companion, 2560²) — `penta_final.png`

Gauss's **pentagramma mirificum**. On the sphere, iterate the self-polar star rule
`P_{k+3} = normalize(P_k × P_{k+1})`; after five steps it closes into a spherical
pentagram whose vertices are mutually perpendicular (`P_i · P_{i+2} = 0`) — five right
angles, a figure so pleased with itself Gauss drew it in his notebook. Because the
vertices are 90° apart the star sprawls across the whole globe, an armillary sphere of
great-circle arcs; the bright pentagram is the hero, and the violet weave behind it is a
one-parameter **family** of pentagrammas breathing as the seed angle sweeps.

And the arcs remember the recurrence: the `tan²` of the five star-arcs, read in pentagon
order, satisfy the Lyness relation exactly — the same five-fold return, now measured in
angles on a ball.

Verified: closure to 2.4e-16; self-polarity to 2.8e-17; `tan²(arcs)` satisfy Lyness to
8.6e-16; Gauss's identity `Π yₖ = 3 + Σ yₖ` to 1e-8.

---

## A tweet-sized story

> Three strangers met at a well and found they knew the same song. One counted
> in orbits, one in whole numbers, one in the right angles of a star. Each had
> been told, in their own country, that anything worth doing must return — and
> each returned in five. The golden point at the centre never moved. It had
> only been waiting for the song to come back around.

## What I learned about generative art this run

**The size-jump is a downscale problem, not a brightness problem.** Both companions
looked right at the 1024 proto and went dead at 2560 — not because the layers were
darker (percentile-normalization erases absolute scale) but because a 1-pixel line
becomes *sub-pixel* when the final is downscaled for viewing, and sub-pixel lines
vanish. The fix isn't more exposure; it's **fattening the line layers by a gaussian
∝ canvas size before compositing**, so a stroke stays a stroke through the shrink. Same
lesson the memory branch records for 4096² skeletons, now confirmed to bite at the
humble 2560 jump too. Render small, but *judge the fatten at final size on the actual
downscaled pixels.*

Files: `verify.py` (the proof battery), `hero.py` / `frieze.py` / `penta.py` (the three
pieces), `kit.py` (shared additive-splat / bloom / tonemap kit), `IDEAS.md` (the six
candidates and why these three).
