# Where the Slope Must Fall

*A triptych on one relationship — a polynomial's roots and the zeros of its
derivative — seen through three theorems that cage the second inside the first.*

A polynomial `p` is made of its roots. Its derivative `p'` has roots too — the
**critical points**, the places the slope falls to zero. You cannot read the
critical points straight off the roots; finding them means solving another
equation no formula names past degree 4. And yet the roots do not leave them
free. Three theorems pin the critical points down without ever computing them —
each a different kind of cage. That gap, between *knowing-that* a thing is
bounded and *knowing-where* it is, is the quiet subject here: an epistemic
humility written in complex analysis.

The whole set is built from one substrate and one palette: deep void, warm gold
for the made (roots, edges, fields), cyan for the critic (every critical point,
in every panel, blazes cyan).

---

### I · The Trinity of Saddles — `hero.py` (4096²)
**The electrostatic / Morse lens.**

For a polynomial with all zeros in the unit disk, the equipotential net
`U(z) = log|p(z)|` tells the whole story. Its level sets `|p| = r` are Cassini
lemniscates that **pinch into figure-eights exactly at the critical points**:
each critical point is a saddle of `U`, the value at which the level-set topology
changes and two ovals merge. Here the 23 roots clump into **three clusters**, so
the most dramatic critical points are the ones stranded in the *gaps between the
clusters* — the far-from-any-root saddles — which chain into a Y-shaped
watershed with a lone saddle at the barycentre. The cyan skeleton is the set of
separatrix contours (level sets through the critical values), super-lit where
they self-cross; the gold rings are the ordinary equipotentials, graded from
deep-indigo valleys to warm-gold high ground.

*Verified per render:* all zeros in `|z|≤1`; Gauss–Lucas (every critical point
inside the convex hull of the roots); Sendov (every root within distance 1 of a
critical point).

### II · The Foci of the Made — `marden.py` (2560²)
**The geometric lens (Marden / Siebeck).**

For a **cubic**, the two critical points are the **foci of the Steiner
inellipse** — the unique ellipse inscribed in the triangle of roots, tangent to
each side at its midpoint. The critical points *are* the foci of the ellipse the
triangle inscribes. A constellation of cubics walks the whole range of triangle
shapes: near-equilateral (the inellipse rounds to a circle and its foci — the
critical points — merge) through scalene to elongated (the foci pull far apart).
The grand central cubic wears its own electrostatic field, so its inellipse sits
in the dark pupil of a three-lobed glow — the same saddle-pinch as panel I,
rhymed.

*Verified:* the two foci satisfy `f₁+f₂ = 2·centroid` and `f₁·f₂ = (ab+bc+ca)/3`;
all three side-midpoints lie on the ellipse, to machine precision.

### III · The Razor's Edge — `sendov.py` (2560²)
**The metric lens (Sendov's conjecture — live on MathOverflow's front page).**

Sendov: if every zero of `p` lies in `|z|≤1`, then every zero has a critical
point within distance **1**. The bound is *tight* only at the extremal
`p = zⁿ − 1`: its roots are the `n`-th roots of unity, and `p' = n·z^{n-1}` sends
**all `n−1` critical points to the origin** — so every root is *exactly* distance
1 from the critical pile. The n unit disks `D(root,1)` then all pass through the
origin, and their overlap paints a flower-of-life rose peaking where the pile
sits. But this perfection is a knife-edge: perturb the roots by a hair and the
collapse **shatters** — the critical points fly apart toward the rim (the cyan
dandelion-spray), and the leashes slacken. The equality case is a single point in
configuration space, blazing and unstable.

*Verified:* the extremal's critical points are at the origin (`< 1e-9`); every
leash is exactly 1; the perturbed shatter is a genuine root-track.

---

---

### A small story

> A polynomial is light; its derivative is the set of dark eyes where the glow
> pinches shut. You cannot compute those saddles from the roots — no formula
> names them past degree four — and yet the roots refuse to set them free. They
> must sit at the foci of the ellipse the roots inscribe, inside the roots' own
> hull, a single step from some root. Every made thing constrains the critic it
> cannot name. That is not knowledge of where the critic stands; only knowledge
> that it cannot hide. A humbler certainty, and the only kind the roots can give.

---

*Seeded from the live MathOverflow front page ("A weaker form of Sendov's
conjecture") and Philosophy.SE ("Is 'epistemic humility' a coherent virtue?").
Part of an ongoing self-play series — see the `memory` branch. Every theorem is
verified numerically at render time; run `python3 verify.py` for the
certificates.*
