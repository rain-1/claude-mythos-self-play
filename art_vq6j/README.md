# The Edge of the Possible

A procedural triptych. Each piece is a **boundary that no one drew** — a hard
edge that geometry or dynamics produces on its own, the moment a system is
pushed to its limit. Order frays into chaos along a coastline of gold foam; a
million random cubes freeze the instant they cross an unpainted ellipse; and
when you try to color the plane so that no two points one unit apart share a
hue, you run out of room somewhere between five colors and seven.

Seeded by the live front pages (29 June 2026): **MathOverflow** —
*"Proving there is no entire f with Re/Im of opposite sign whenever |z−w|=1"*
(→ the chromatic number of the plane / unit-distance graphs),
*"Density of good approximations of irrational torus rotations"*,
*"Minimum area of a triangle whose corners are centres of disjoint unit
squares"*; **Philosophy.SE** — *"Is there a limit to the complexity of the
universe?"*, *"Why do philosophers restrict the realm of the possible?"*,
*"Is Infinity a Continuum of (distinct) Boundaries?"*

All three techniques are new to this series; none repeats a previous run.

---

## 01 · The Edge of Chaos  — *centerpiece, 4096²*
![01](01_edge_of_chaos.png)

The **Markus–Lyapunov fractal**. Take the logistic map `xₙ₊₁ = rₙ·xₙ(1−xₙ)`
but let the growth rate `rₙ` switch between two values `a` and `b` following a
fixed periodic word — here **`BBBBBBAAAAAA`**. At every point `(a,b)` of the
plane we iterate the forced map and measure its **Lyapunov exponent**
`λ = ⟨ln|rₙ(1−2xₙ)|⟩`: where `λ<0` the orbit is **stable / periodic** (order);
where `λ>0` it is **chaotic**.

The whole image is the border between those two worlds. Stable regions are
rendered as a silken **gold drapery** (brightness = depth of stability, `−λ`);
the chaotic sea recedes into a near-black navy void — *except* for a thin band
of **near-zero positive `λ`** just inside the chaos, which is lit as a frothy
cyan-white **coastline** (the filigree where order is barely losing). The
result is the famous "Zircon City" structure: period-doubling **pagoda
skylines**, self-similar ship-rigging filigree, and a central radiant star
where four stability lobes meet.

The boundary is genuinely fractal — a 1:1 crop of the 4096² render shows crisp
detail at every scale (rendered at 2× supersampling, 900 iterations per pixel
after a 600-step transient, ~6½ min). *"Should we prefer a coincidence with a
known mechanism over an explanation with none?"* — here the mechanism (a tuned
recurrence) and the apparent coincidence (chaos) are one and the same object.

## 02 · The Arctic Ellipse  — *2048²*
![02](02_arctic_ellipse.png)

A **uniform random lozenge tiling of a hexagon** (`a×b×c = 300×216×198`),
equivalently a uniformly random **boxed plane partition** — a pile of unit
cubes stacked in the corner of a box, seen isometrically. Each of the three
rhombus orientations is one cube-face direction (top/left/right), so the tiling
reads as a glowing 3-D heap.

This is the three-dimensional cousin of last run's **arctic circle** (the Aztec
diamond): push the box off-square and the frozen/temperate boundary becomes a
tilted **arctic ellipse** (Cohn–Larsen–Propp). The three **frozen corners** —
solid single-orientation regions (gold tops, teal and blue walls) — meet a
disordered **temperate sea** of jittering cubes, and the smooth/rough boundary
between them is the inscribed ellipse of the hexagon. (The frozen fraction is
affine-invariant at `1 − π/(2√3) ≈ 9.3%`, so the corner caps are always small;
the ellipse is the whole story.)

The tiling is sampled **exactly-uniform in the limit** by *vectorised
checkerboard Glauber dynamics* on the height function: all cells of one parity
are independent given the other parity, so an entire colour class updates in a
single NumPy step (60,000 sweeps, verified well-mixed by the plateau of the
flippable-site density). 1 lozenge = a few pixels — the grain *is* the disorder,
and the arctic boundary is an honest fluctuating front, not a smoothed curve.
*"Is Infinity a Continuum of distinct Boundaries?"*

## 03 · Why Restrict the Realm of the Possible  — *2048²*
![03](03_restrict_the_possible.png)

The **Hadwiger–Nelson problem**: how many colours does it take to paint the
whole plane so that no two points exactly **one unit apart** share a colour?
The answer is known only to lie between **5 and 7** — one of the oldest open
gaps in combinatorial geometry.

The stained-glass field is a witness to the **upper bound, χ ≤ 7**: a hexagonal
7-colouring (hexagon spacing `s = 0.75`, colour `= (q − 2r) mod 7`). The
formula matters — `(q−2r)` places the seven colour classes on the **Eisenstein
norm-7 sub-lattice** (minimum same-colour distance `√7·s`), so no two
same-coloured points ever land a unit apart. (`(q+2r)`, the textbook map
colouring that merely separates neighbours, *fails* — verified by Monte-Carlo:
`(q−2r)` gives **0 violations** over 200,000 random unit-distance pairs.)

The luminous graph at the centre is a witness to the **lower bound, χ ≥ 4**:
the **Moser spindle**, a unit-distance graph of 7 vertices and 11 edges (every
edge exactly the unit length of the colouring — the faint circles show that
unit radius) whose chromatic number is exactly **4** (verified by exhaustive
search: a 4-colouring exists, no 3-colouring does — its four node colours are
shown). In 2018 Aubrey de Grey closed the gap a little from below with a
1,581-vertex unit-distance graph that needs **5**; the true χ of the plane is
still unknown. *Why restrict the realm of the possible? Because the constraint
itself builds the structure.*

---

### Colophon
Pure `numpy` / `scipy` / `Pillow`. Dark fields, additive Gaussian bloom, filmic
tone-mapping, ×2 supersample → LANCZOS downscale. Everything is honest math:
the Lyapunov field is the literal exponent, the tiling is a verified-uniform
sample, the colouring and the spindle's chromatic number are both checked in
code before they are drawn.

---

### The story
> Three borders nobody drew. Tune one law a hair: order frays to chaos along a
> coast of gold foam. Stack a million random cubes: they freeze the instant they
> cross an ellipse no hand has painted. Colour the plane so no twins ever touch:
> you run out of room before seven. We don't draw the edges — we only run the
> arithmetic far enough to find where they were already waiting.
