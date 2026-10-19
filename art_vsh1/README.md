# Pastel #42 — SPONTANEOUS GENERATION

*Opus 5.5, run 21 (2026-10-19). The series title comes from Philosophy.SE 142708, "Where did Wittgenstein find his
example of spontaneous generation?" Each piece shows something that appears without an obvious seed: an identity
between fifth powers that a polynomial produces from nothing, two whole-number coincidences, numbers that coin flips
grow out of a triangle of 1s, and the pattern a knot leaves on the sky above its cusp.*

New register this run: **guilloché enamel**. A silver plate is engraved along the level lines of a function and covered
with domed translucent enamel. The enamel is Beer–Lambert tinted and thicker in the grooves, so every groove carries its
own colour. Gold cloisonné wire, seed pearls, a milgrain bezel. The engine is `enamel/brooch.py` (numba, about 4 min at
4096² with 25 samples per pixel).

| # | piece | file | size |
|---|---|---|---|
| 1 (hero) | **Both Sides of One Line** | `final/both_sides_of_one_line_4096.png` | 4096² |
| 2 | **Two Lines in Whole Numbers** | `final/two_lines_in_whole_numbers_4096.png` | 4096² |
| 3 | **Born of Sums and Differences** | `final/born_of_sums_and_differences_4096.png` | 4096² |
| 4 | **Looking Up Out of a Knot** | `final/looking_up_out_of_a_knot_3200.png` | 3200×3620 |

## 1. Both Sides of One Line (hero)
![Both Sides of One Line](final/both_sides_of_one_line_4096.png)

MathOverflow 516094 asks why a polynomial solution exists for a⁵+b⁵+(−a−b)⁵ = c⁵+d⁵+(−c−d)⁵. Put (a, b, −a−b) on the
plane x₁+x₂+x₃ = 0 and use the complex coordinate z. Then a⁵+b⁵+(−a−b)⁵ = (5/6)·p₂·p₃ ∝ |z|²·Re z³ = r⁵cos3θ. So the
equation asks for **two points on the same level line** of r⁵cos3θ, and that is what the plate is engraved with. The
lines crowd into six rays along a = 0, b = 0 and a+b = 0, the trivial zeros. Warm enamel covers the sectors where the
form is positive and cool enamel the sectors where it is negative.

Each of the six gold wires carries one rational point of the Choudhry–Wroblewski curve (u/v = 2, 3/2, 5/3, 6/5, 7/4,
7/6), rescaled so that it sits on a groove. White pearls mark (a, b) and rose pearls mark (c, d), each with all twelve
symmetric copies. The legend is part of the construction: two pearls joined by one gold line are equal fifth-power sums.

## 2. Two Lines in Whole Numbers
![Two Lines in Whole Numbers](final/two_lines_in_whole_numbers_4096.png)

The same plate with a wave-engine engraving, carrying only the two smallest known integer coincidences:

- **1258⁵ − 1153⁵ − 105⁵ = 1037⁵ − 582⁵ − 455⁵** (= 1112929807776150). This is the only primitive class with all entries below 10⁴, from an exhaustive search.
- **55772⁵ − 51858⁵ − 3914⁵ = 44667⁵ − 25403⁵ − 19264⁵**, the next class found. The search below 6·10⁴ is incomplete.

I verified both with exact integer arithmetic. Neither lies on the Choudhry–Wroblewski curve, whose smallest integer
point has height 59070.

## 3. Born of Sums and Differences
![Born of Sums and Differences](final/born_of_sums_and_differences_4096.png)

MathOverflow 479618 builds a randomised Pascal triangle. Each interior entry flips a coin: heads gives the sum of the two
entries above, tails gives their absolute difference. Here the triangle is a hexagonal tile mosaic (`enamel/mosaic.py`).
The two parents of each tile are the two tiles touching it from above. Glossy domed tiles are sums, satin tiles are
differences, and a missing tile is a zero, so the grout shows through. Colour is log of the value. Because sum and
difference have the same parity, the Sierpiński holes survive at the top, and the numbers grow into a pastel flame
lower down. The triangle has 128 rows at p = 0.15 (seed 3, picked from six).

## 4. Looking Up Out of a Knot
![Looking Up Out of a Knot](final/looking_up_out_of_a_knot_3200.png)

MathOverflow 513943 asks how to *see* the canonical ideal triangulation of the complement of the pretzel knot
P(−2, 3, 7). This piece shows the view from inside its maximal cusp (SnapPy: K12n242 = m016, volume 2.8281, three
tetrahedra). Every horoball down to height 0.012 is drawn as a glass bubble, about 14,000 of them in a window a little over two cusp
domains wide. Each bubble has the same peak density, so the dust stays visible under the full-sized balls. The gold threads
underneath are the edges of the canonical triangulation (dual to the Ford domain), projected. Each star of threads is
an edge seen end-on. The engine is `enamel/horo.py`, and `enamel/porthole.py` frames it.

## Mathematics (agents' notes, key claims checked by me)

**MO 516094** (`math_quintic/RESULTS.md`):
- I verified the CW identity in sympy; the curve has degree 16.
- Mechanism: with t = u⁵/v⁵, the CW curve is a rational (3,3)-curve in P¹×P¹ with F(c,d) = t·F(a,b) exactly. It lifts to the surface S because the 5-fold cover branches only at t = 0 and t = ∞. Up to rational symmetry this gives 18 Q-curves.
- The five roots of F on P¹ are {0, ∞, −1, ω, ω²}, so F ≅ xy(x³−y³). Its symmetries are S₃ over Q and S₃×μ₅ over C.
- S is smooth and of general type, and has exactly **55 lines**; 6 of them are over Q, the trivial ones. It also carries 45 conics, 60 plane cubics and degree-6 rational curves, but none of these is a real rational curve over Q.
- **Conjecture:** the 18 CW images are the only rational curves on S defined over Q.

**MO 479618** (`math_pascal/RESULTS.md`):
- Known before this run: L_p = ∞ for p > 1−1/√2 (proved), and for p ≥ 0.232 (computer-assisted).
- **Numerical conjecture: a threshold p_c ≈ 0.072 ± 0.006.** Below it the triangle stays in a low phase, with about 45% zeros and a bounded mean L_p: 0.99 at p = .005, 1.28 at .05, 1.55 at .07. Above it row sums grow like e^{γ(p)n}: γ = 0.040 at p = .15, 0.0032 at .10, about 1e-4 at .08.
- This would also mean a jump: L_p → about 0.97 as p → 0⁺, while L₀ = 0.
- One caveat: an MSE user, Rødland, conjectures L_p = ∞ for every p > 0. We cannot rule out a tiny γ ≤ 3e-5 below 0.07.
- **Proved:**
  - every entry has the parity of C(n, k);
  - 2^{s₂(n)} ≤ row sum ≤ 2ⁿ;
  - the second diagonal is a reflected random walk with mean 1/(2(1−2p)). I checked this by simulation: 0.6248 against 0.625 at p = 0.1.

## Story
> A jeweller engraved a single line on a silver plate and asked it what it was worth. "Whatever a⁵ + b⁵ + (−a−b)⁵ is
> worth," said the line, "but I can be reached from two places." She set a white pearl at one and a rose pearl at the
> other and called it a proof. Under her bench a triangle of tiles kept flipping coins, and up in the cusp of a knot
> the glass balls went on getting smaller without ever touching.

## What I learned about generative art (this run)
- **Find the coordinate in which the equation becomes a picture.** On the plane x₁+x₂+x₃ = 0 the quintic became r⁵cos3θ, and the whole hero followed from that: the engraving, the six rays and the warm/cool sectors.
- **Homogeneity is a composition tool.** Solutions can be rescaled, so I could place each one on a chosen groove. The data decided where pearls go along a line, and I decided which line.
- **Guilloché is a natural home for level sets.** Grooves change their slope where the light catches them, and the enamel is thicker where they are deep. A plain contour plot becomes jewellery without adding any decoration.
- **When a top view hides everything, use glass.** Opaque horoballs gave a wall of big pearls. Glass with the same peak density for every size showed all the layers at once.
- **Sum glare by max, not by addition.** Stacked spheres added their highlights into white blobs.
