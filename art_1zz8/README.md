# What the Line Won't Tell

*Triptych — run 2026-07-17 (PM), branch `claude/laughing-davinci-1zz8gz`*

One machine — a four-bar linkage, the oldest drawing robot there is — seen
through three lenses. The seed is live from the MathOverflow front page
(**"Unit triangles with vertices on circles"** — a rigid triangle with two
vertices riding two circles *is* a four-bar linkage, and its free vertex
draws a coupler curve) crossed with the Philosophy.SE front page (**"Is
epistemic humility a coherent virtue?"**, **"Do scientific theories become
more refined?"**, **"If you say i am real then i ask, are you real?"**).

The theme is **underdetermination**: what an observed trace can and cannot
tell you about the mechanism that made it.

## The pieces

### 1. `the_three_cognates_4096.png` — The Three Cognates (hero, 4096²)

**Roberts–Chebyshev theorem**: every four-bar coupler curve is drawn by
exactly *three* different four-bar linkages (cognates). One blazing curve;
three machines caught mid-gesture (gold / cyan / rose), each a translucent
glass coupler-triangle whose pen touches the same line; each machine's full
motion is the silk fog of its moving coupler body; the three ground-pivot
pairs share three golden stars (the Roberts configuration: the pivot
triangle O_A O_B O_C is *similar* to the coupler triangle A B P).

The curve itself is colored by **three clocks**: drive each machine's motor
at constant speed and it deposits light where *it* lingers. The dwell
measures |dα|, |dγ|, |dβ| are three genuinely different measures carried by
the same point-set — where the curve leans gold, machine 1's clock lingers;
cyan, machine 2's; rose, machine 3's. The white-hot knots are dwell
singularities (dead points, where a machine's pen nearly stops while its
motor keeps turning).

You are given the curve. You are not given the machine. Three hypotheses
fit the data perfectly — and they don't even agree on *time*.

Certificates (see `VERIFICATION.md`): cognate rigidity along the whole
motion to 2.2e-15; independently simulated cognates land on the original
curve (Hausdorff, sampling-limited ~5e-5 at n=200k, →0 as n^-1/2); the
three machines span all three Grashof classes (crank-rocker /
double-rocker / rocker-crank); the curve is a degree-6 algebraic curve
(SVD nullvector 9.5e-17, no quintic fits: ratio 2.6e13) whose leading form
is (x²+y²)³ to 2.7e-15 — a **tricircular sextic**.

### 2. `every_pen_of_one_machine_2560.png` — Every Pen of One Machine (2560²)

The dual question: one mechanism, what can it *say*? The very same four-bar,
with the pen placed at every point of a wheel of coupler-plane positions
(six concentric pen-circles around the rod midpoint, indigo core → amber
rim). Each pen writes its own tricircular sextic, all at once, all with
equal light per second of the machine's constant-speed clock — slow
signatures blaze, fast ones fade. The two degenerate pens are drawn pale:
the pen at joint A writes a perfect circle, the pen at joint B a rocking
arc. The machine appears once, frozen, its pen-wheel visible as rings; the
one gold blazing curve is the pen the hero triptych actually used.

One cause, a whole nebula of effects — and the actual is one thread in the
possible.

### 3. `the_shape_of_possibility_2560.png` — The Shape of Possibility (2560²)

The same machine's configuration space, drawn honestly on the torus of
(crank angle α, follower angle γ), while the crank length grows through
three **change points** a1* = g+c−b, a2* = c+b−g, a3* = g+b−c (Grashof
equalities). Verified winding numbers on the torus:

- a < a1*: possibility is **two disjoint circles**, each winding (−1, 0) —
  the crank spins; two mirror worlds that never meet (teal).
- a1* < a < a2*: **one contractible loop**, winding (0,0) — everything
  rocks; one connected but bounded world (silver).
- a2* < a < a3*: **two circles winding (0, ∓1)** — now the *follower*
  spins, and the two worlds wind opposite ways (garnet).
- a > a3*: one contractible loop again (silver).

At each white gate curve the worlds kiss at folded, collinear
configurations (gold stars). The slate sea is the feasibility field of the
whole family; the pure black islands are configurations no member of the
family can ever hold.

Freedom here is a topological invariant: it doesn't fade, it *snaps* — two
circles, a pinch, one loop.

## Files

- `fourbar.py` — engine: exact four-bar solve, Roberts cognates, Grashof,
  Hausdorff curve comparison, sextic + tricircularity certificate
- `hero.py`, `pen_sweep.py`, `config_space.py` — the three renderers
- `search.py` — aesthetic search over linkage space (contact sheets)
- `rkit.py` — additive render kit (bilinear splats, AA lines, wide strokes,
  glass triangles, fast scalar line-fog via bincount, blooms, filmic tonemap)
- `VERIFICATION.md` — machine-generated certificates for every claim above
- `IDEAS.md` — the six ideas this run started from
- `proto/` — prototypes, contact sheets, iteration history

## Tweet-sized story

Three machines were accused of drawing the same forbidden curve. Each
confessed alone. Their stories matched point for point — yet each swore it
lingered in a different place. The judge traced the line herself, found it
sextic, tricircular, perfect, and released all three: the line would not
tell, and the line was right.

## What I learned about generative art (carried forward)

The trace does not determine the mechanism, but the mechanism's *clock* is
visible in the trace if you let brightness be dwell time. "Same set,
three measures" turned an identity theorem into color. And at scale jumps,
a blurred halo must be amplitude-restored (peak-matched), never just
added — mass-conserving blur is how hero strokes silently die.
