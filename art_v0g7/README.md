# What Passing Leaves — triptych, 2026-07-12 (evening run)

*Seeded from the live MathOverflow and Philosophy.SE front pages of today.
The Phil.SE question "What is the meaning of graffiti like 'Kilroy was
here!'?" runs under all three panels: existence known only through the
trace a passage leaves behind.*

## 1. Rivers of Totient (`rivers_hero.png`, 4096²)
The functional graph of **a → a + φ(a)** on [1, 2²⁷] — 134,217,728 integers,
each flowing to its successor. Chart: x = log₂ a, y = 1 − φ(a)/a.

Since φ(a) is even for a ≥ 3, **parity is conserved**: an odd sky (warm) and
an even sea (cool) share the plane but can never exchange mass — the only
bridge in the entire universe is 1 → 2 → 3 (verified: exactly 2
parity-crossing edges). The even sea is ruled by the doubling lock
2^k → 3·2^(k−1) → 2^(k+1) (verified k = 2..25), the sawtooth spine.
Ratio-preserving families (e.g. 9·2^k → 3·2^(k+2), both at φ/a = 1/3) make
horizontal channel bars. Brightness = upstream basin mass (max observed
17,509 sources; exit-mass conservation checked exactly: 134,217,728).
The gold thread is the MO poster's orbit 1, 2, 3, 5, 9, 15, 23, 45, … —
reproduced term-for-term including their squarefree indices 1..15 —
with squarefree terms as bright beads (whether infinitely many terms are
squarefree is the open question on today's front page).

## 2. The Whispering Gallery (`whispering_gallery.png`, 2560²)
One exact eigenmode of the disk, u = J_m(kr)cos(mθ), m = 120, with k a
Dirichlet zero j_{m,n} chosen so the **classical rotation number is 0.286445
≈ 2/7**: the billiard chords tangent to the caustic circle r_c = m/k almost
close into a heptagram, precessing 1.84°/return (ghost→blaze, 57 chords).
The wave cannot enter r < r_c (the violet void); its first antinode sits at
the Airy distance predicted by turning-point asymptotics (observed 0.64242
vs 0.64236). Ray tangency to r_c: 2×10⁻¹⁶. The front-page inequality
J_ν² ≤ J_{ν−1/2}² + J_{ν+1/2}² was tested at 490,000 grid points over
[0,420]² — it held at every one.

## 3. Kilroy Was Here (`kilroy.png`, 2560²)
The graph of one Brownian path, measured by dyadic squares at scales
ε = 2⁻⁴ … 2⁻¹⁰. Each lit cell carries total light ε^{3/2}; each level keeps
only the shell the next-finer level cannot reach (set-difference
stratigraphy), so the covering collapses onto the trace with per-pixel
brightness growing like ε^(−1/2) — cold blue plates far out, amber sleeve
at the graph. Measured: log₂N(ε) slope **1.489 ≈ 3/2** = dim_H(graph)
(Taylor; Mörters–Peres Thm 4.29); N(ε)·ε^{3/2} ≈ 1.59–1.89 across seven
octaves. Whether the 3/2-Hausdorff measure of the graph is 0, positive, or
infinite is OPEN — asked on today's MO front page. The walker is gone;
the boxes are how we know it passed.

---
Engines: `rivers.c` (linear sieve, mass accumulation, fog splatting, OpenMP),
`hero.py`, `whisper.py`, `kilroy.py`. Verifications in `stats.txt`,
`whisper_stats.txt`, `kilroy_stats.txt`. Ideation in `IDEAS.md`.
