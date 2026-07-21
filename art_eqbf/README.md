# What the Constant Could Not Keep

*Triptych, 2026-07-21 — run `claude/laughing-davinci-eqbfvl`*

Two days before this run, on **July 19, 2026**, the mathematician Levent Alpöge
announced an explicit counterexample to the **Jacobian conjecture** — open since
Keller, 1939 — found in a morning's work with the assistance of Claude Fable.
The map `F = (a,b,c) : ℂ³ → ℂ³`,

    a = (1+xy)³z + y²(1+xy)(4+3xy)
    b = y + 3x(1+xy)²z + 3xy²(4+3xy)
    c = 2x − 3x²y − x³z

has **constant Jacobian determinant −2** — at every point of space it is a
local diffeomorphism, crushing nothing, folding nowhere, locally losing no
information at all — and yet it sends **three distinct points**

    (0, 0, −1/4),   (1, −3/2, 13/2),   (−1, 3/2, 13/2)

to **one point** `q* = (−1/4, 0, 0)`. Local memory perfect; global memory
broken. The conjecture said the local promise forces the global one. It does
not.

This run verified everything from scratch (`verify.py`, sympy) and then painted
the geometry of *how* a map that never folds can still forget. The whole map is
governed by one cubic: with `t = y + 1/x`,

    P(T) = c·T³ − 2T² + b·T − 2a,   P(t) = 0,   P′(t) = 2/x,

and `(x,y,z)` are *rational* in `(t, P′(t), a,b,c)` — so the fiber over a
present `(a,b,c)` is exactly the root set of a cubic, and `x = 2/P′(t)`. Where
the cubic has a **double root** (the discriminant veil `Δ = 0`), `P′(t) → 0`
and the two merging preimages **escape to infinity in opposite directions** —
the fold every honest map would show is hidden entirely at infinity. Where
`c = 0` (the wall), the cubic drops to a quadratic and the third preimage
returns along the plane `x = 0`.

## Certificates (all in `verify.py`, `mono.py` — run them)

- `det DF ≡ −2` exactly (symbolic).
- `F` of each of the three points is exactly `(−1/4, 0, 0)`; the affine fiber
  over `q*` is exactly these three points (sympy `solve`).
- The cubic-model identities of the live MO question ("Galois structure of the
  new counterexample…"): `b = 4t + 2/x − 3ct²`, `2a = ct³ − 2t² + bt`,
  `P′(t) = 2/x`, and the rational inversion — all residues 0 (symbolic).
- Monodromy of the cubic over the base, computed by root continuation along
  complex loops (matching error ≤ 2·10⁻¹⁵): loop around the wall `c=0` →
  **identity**; loop around one branch point → **transposition (1 2)**; loop
  around both real branch points → **3-cycle (0 1 2)**. The two transpositions
  generate a group of order 6: the Galois/monodromy group is **S₃**, as the MO
  question claims.

## The pieces

### 1. `hero_4096.png` — *The Veil Where Two Pasts Flee* (4096²)

The base plane through `q*` spanned by the wall direction and the cusp
direction: chart `(a,b,c) = (−1/4 + u, 4v/3, v)`. Every pixel is a present;
brightness is the *presence* of its three pasts. Amber chamber: all three
pasts real and near; graded rings are equipotentials of `log|Δ|`; the ember
contour family inside is the escape field (how far the pasts have run). At the
**cyan veil** `Δ = 0` two pasts flee to opposite infinities — the light flares
as they run and dies where they pass beyond sight (the dark moat). The two
mirror **cusps** are triple roots — the last places where all three pasts were
one. The gold star on the wall is `q*` itself: the one present with three
whole pasts, sitting exactly where the third sheet returns from infinity along
`x = 0` (the horizontal seam).

### 2. `wells_2560.png` — *Three Pasts, One Present* (2560²)

Source space: the real plane through the three collision points (isometric
chart; the mirror symmetry is exact, since `F∘σ = (a,−b,−c)` for
`σ(x,y,z) = (−x,−y,z)` fixes `|F − q*|`). The field is `U = log|F − q*|²`:
three wells — the three pasts — drain the same water. Rivers are gradient
descent of `U`, hue by destiny (verdigris = the well at the origin of the
`x=0` sheet, gold = the twins); cyan separatrix contours pass through the two
saddles at `(±1.23094, 2.45318)`, `U = 2.84899`. From far away the rings
enclose all three wells as one — one present; only up close does the water
choose a past.

### 3. `braid_2560.png` — *The Braid of Forgetting* (2560²)

The S₃ monodromy as an armillary around the gold star of `q*` (every loop here
is a loop of presents encircling `w = 0`, the wall direction through `q*`).
Inner ring: the loop around the wall — identity; three strands come home
unexchanged (the wide cyan strand is the sheet that lives at infinity,
swinging around the two quiet golden ones). Middle ring: a loop around one
branch point — a transposition; two pasts fuse into one double-length ember
thread while the third keeps its own gold. Outer ring: the loop around both
real branch points — a 3-cycle; **three pasts, one thread**, a single strand
closing only after three circuits, its color walking gold → teal → violet →
ember → gold. The braid pinches glow where two sheets draw near: the moments
of almost-forgetting. Forgetting grows with the size of the journey.

## Files

- `verify.py` — symbolic verification of the counterexample + cubic model
- `mono.py` — monodromy continuation engine (+ branch points, permutations)
- `field.py` — cubic root/discriminant fields on the hero slice
- `kit.py` — render kit (tonemap, ridges, splats, bloom)
- `hero.py`, `wells.py`, `braid.py` — the three pieces
- protos: `hero_1024.png`, `wells_768.png`, `braid_900.png`

Seeds: MathOverflow front page 2026-07-21 (the live Jacobian-counterexample
cluster: "Could the Jacobian conjecture be undecidable?", "The simplest case…",
"Galois structure of the new counterexample…") × Philosophy.SE front page
("Can memory be defined as a universal principle of life rather than a simple
function of brains?").
