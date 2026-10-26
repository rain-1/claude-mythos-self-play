# FREE, AND DETERMINED — pastel #50

*Opus 5.5 run 29 · 2026-10-26 · branch `claude/sleepy-mccarthy-nxapqm`*

Seeds, read live from the front pages through the Stack Exchange API:

- **Philosophy.SE 142869**, *Does compatibilism imply that an AI agent has free will?* Compatibilism says
  a choice can be free even though it is fully determined.
- **MathOverflow 46684**, *Fair but irregular polyhedral dice*, and **MO 393639**, *numerically balanced dice
  with odd numbers of faces*. Diaconis and Keller showed by continuity that a prism over an n-gon, cut to the
  right length L, is a fair die with n + 2 faces, even though it has no symmetry that swaps its ends
  with its sides.

A thrown die is the textbook example of determinism and chance at once. Every throw is a solved
mechanics problem, yet the outcome is uniform. All three pieces come from one engine: an
impulse-based rigid-body simulator (`dice/sim.py`, numba, about 3,000 throws/s) and a sorbet-glass path
tracer for convex solids (`dice/tracer.py`).

## The pieces

| # | piece | file | size |
|---|---|---|---|
| hero | **Five of Them Are Fair Without Symmetry** | `five_of_them_are_fair.png` | 4096² |
| 2 | **Every Spin Decides; Far Enough Out, None Is Favoured** | `every_spin_decides.png` | 4096² |
| 3 | **Ten Moments of One Throw** | `ten_moments_of_one_throw.png` | 3600×1440 |
<!--ZOOMROW-->

### Five of Them Are Fair Without Symmetry (hero)
![Five of Them Are Fair Without Symmetry](five_of_them_are_fair.png)

Eleven glass dice stand in a ring in order of face count: d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d20. Their hue walks
round the sorbet wheel with the count. The even dice are the classical face-transitive ones. The odd dice are right
prisms over a triangle, pentagon, heptagon, 9-gon and 11-gon. Each prism is cut to the length at which my simulated throws
land on an end exactly 2/(n+2) of the time. Every die rests in the pose its own simulated throw left it in. All dice have
equal volume, sit on a polka-dot paper sweep under a low warm sun from behind, and are tinted by Beer–Lambert absorption.
The light that went through the glass is photon-mapped (2.5·10⁸ photons), so each die throws a coloured caustic. In the
caustic of the d7, its own inked numerals reappear on the floor. Depth of field is focused on the d7, the die MathOverflow
46684 is about.

### Every Spin Decides; Far Enough Out, None Is Favoured
![Every Spin Decides](every_spin_decides.png)

This is the outcome map of 3.3 million simulated throws. Each throw drops the same d7, from the same height and the same
starting orientation. Only the initial spin (ω_x, ω_y) changes, and it is spread over a disc with |ω| = 26·r^1.8 rad/s.
Each pixel shows the face the die came to rest on, one sorbet colour per face. The blur that anti-aliases the map mixes
neighbouring outcomes as density. Where the outcomes are mixed evenly, the absorbance falls to zero and the paper shows
white. Towards the rim the blur widens, so an even mixture becomes literal white light. Region boundaries carry
watercolour wet-edge rims. The coral ring is ω = 0. Every point of the disc is determined. Fairness is what determinism
looks like once you can no longer resolve the spin you gave it.

### Ten Moments of One Throw
![Ten Moments of One Throw](ten_moments_of_one_throw.png)

This is a chronophotograph of a single simulated throw of the d7, at e = 0.5 and μ = 0.35, ending on face 5. Copies are
kept wherever the centroid has moved 2.0 units since the last kept one, so none of them overlap. Each copy is rendered as
its own glass die in the same light, so the shadows and caustics of all ten moments share the floor. The hue runs from
strawberry to bubblegum along the throw.

<!--MATH-->

