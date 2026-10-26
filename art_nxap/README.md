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

<!--PIECES-->
