# Squares round a corner — notes for MO 518136

*Question (MO 518136): M_n = the largest total area of n congruent squares, rigidly joined, that can be
carried round the right-angled corner of a corridor of width 1. Known: M_1 = 1, M_2 = 1.16202…;
asked: is M_3 = (36+24√2)/49 = 1.42737…?*

Everything here is normalised the other way: the squares have side 1 and the corridor has width w;
the area carried is n / w².

## Lemma 1 (the search for a motion is one-dimensional) — proved

Let S be any compact set. For a turning angle t put u = (cos t, sin t), v = (−sin t, cos t),
h_u = max_S u·p, h_v = max_S v·p and

    g(t)  = max over p in S of  min( h_u − u·p ,  h_v − v·p ),
    W_u(t) = width of S in direction u,   W_v(t) = width in direction v.

Then S can be carried round the corner of a corridor of width w **iff** there is an arc [t0, t1] of
angles with

    W_v(t0) ≤ w,     g(t) ≤ w for all t in the arc,     W_u(t1) ≤ w

(or the same with u and v exchanged).

*Proof.* In coordinates x = u·p, y = v·p the corridor at angle t with inner corner at (a, b) is
{x ≤ a + w, y ≤ b + w} minus the open quadrant {x < a, y < b}. S fits iff a ≥ h_u − w, b ≥ h_v − w and
no point of S is strictly below-left of (a, b). The last condition describes a down-set D(t), so the
admissible corners form F(t) = D(t) ∩ {a ≥ A, b ≥ B} with (A, B) = (h_u − w, h_v − w): if (a, b) ∈ F(t)
then the whole box [A, a] × [B, b] ⊂ F(t). Hence F(t) is non-empty iff (A, B) ∈ D(t), i.e. iff
g(t) ≤ w; it is then connected and contains (A, B), which moves continuously with t. So wherever a
motion exists, the motion "pressed against both outer walls" exists. Lying in an arm at angle t means
W_v(t) ≤ w (resp. W_u), and that part of F(t) is connected to (A, B) as well. ∎

For a union of polygons g(t) is a maximum over vertices and over the points of edges where the two
distances are equal, so the corridor width needed is a minimax of an explicit function of one angle
(`corner.py`: `profiles`, `width`, `width_fast`). Checks: unit square → 1; two squares → 1.162021
with the squares meeting at a vertex at ±23.07° (matches the octic of the question); the staircase
→ 1.4273699 = (36+24√2)/49.

## Rows ("skylines") — a closed form, and four beat five

A *row* is n unit squares side by side, the i-th raised by h_i.

**Observation (numerical, 9 digits, n = 3…7; `skyline.py`, 16 random starts each, 46,080 angles).**
The least corridor width for a row of n ≥ 3 squares is

    w_n = (n + 4)(√2 − 1)/2,        area carried  A_n = 4n(3 + 2√2)/(n + 4)².

| n | w_n | side 1/w_n | A_n |
|---|---|---|---|
| 3 | 1.449747 | 0.6898 | 1.427370 = (36+24√2)/49 — the staircase of the question |
| 4 | 1.656854 | 0.6036 | **1.457107 = (3+2√2)/4** |
| 5 | 1.863961 | 0.5365 | 1.439118 |
| 6 | 2.071068 | 0.4828 | 1.398823 |
| 7 | 2.278175 | 0.4390 | 1.348727 |

Attained by: both end squares at height 0, the middle one (or two) raised by exactly w_n − 1, the
others anywhere in an interval (n = 5: 0.75…0.85 all work) — so the optimum is unique only for
n = 3, 4. n/(n+4)² is largest at n = 4: **in a row, four squares carry more than three and more than
five.** (For n = 2 the formula fails: the best row gives 1, the tilted pair 1.1620.)

**Where the formula comes from (chevron lemma).** A row longer than the corridor is wide must at some
moment stand at 45° to the walls. Seen from the row, the corridor is then a chevron
{Y − √2w − |x − c| ≤ y ≤ Y − |x − c|}. The end squares must hang below the outer V, the square over
the apex must clear the inner corner: with rise = (height of the square over c) − (height of an end),

    rise_left ≥ 1 + c − √2 w,     rise_right ≥ 1 + (n − c) − √2 w,

so the larger rise is ≥ 1 + n/2 − √2w. If moreover the row lies flat in the arm (1 + rise ≤ w), then
(1 + √2) w ≥ n/2 + 2, which is the formula, with equality for the symmetric bridge.
**Gap:** a lopsided row could enter the arm slightly tilted (this is exactly why n = 2 escapes), so
"1 + max rise ≤ w" is not automatic; the argument above only gives 1 + min(rise, …) ≤ w. The numerics
say the bound holds for n ≥ 3; I have not closed the gap.

## Free search (3 parameters per square; `opt.py`, multistart Nelder–Mead with an overlap penalty)

| n | best found | shape | starts |
|---|---|---|---|
| 2 | 1.162021 | two squares sharing a vertex, ±23.07° | 16 |
| 3 | 1.427369 | the staircase (all parallel) | 32 + 40 |
| 4 | 1.456440 → row value 1.457107 | the bridge 0, r, r, 0 with r = 4(√2−1) − 1 | 40 |
| 5 | 1.437846 (row: 1.439118) | near-rows only | 40 + 60 |
| 6 | **1.398990** (row: 1.398823) | a row with three squares tilted by 0.2°–5° | 60 |
| 7 | **1.498097** | a two-storey arch: three on top, legs of two on each side, tilts up to 8° (`polish.py`) | 60 |
| 7, all parallel and mirror-symmetric | **252/169 = 1.491124** (w = 13/6 to 9 digits) | same arch; top squares at x = −1, 0, 1, legs at ±1.3104 and ±2.3104 (`arch7_sym.json`) | 24 |
| 8 | **1.582978** | arch of four on top (already bending like Gerver's sofa) and legs of two | 44 |

The landscape is a minimax with several active kinks, and Nelder–Mead converges poorly on it (it
approaches the row values from below for n = 4, 5), so these are lower bounds found, not optima.
Polyominoes on a common grid are much worse (U-hexomino 1.2, 2×3 block 0.98, I-tromino 0.96).

## Conjectures

* **C1.** M_3 = (36+24√2)/49 (the question) — nothing better in 72 free starts.
* **C2.** M_4 = (3+2√2)/4 = 1.457107…, attained only by the bridge.
* **C3 (a valley).** M_5 < M_4 and M_6 < M_4, but M_7 > M_4: the sequence M_n is **not monotone**.
  Best known: 1, 1.1620, 1.4274, 1.4571, 1.4391, 1.3990, 1.4981, 1.5830 for n = 1…8. The reason is
  visible in the pictures: up to six squares the best assembly found is one storey high; a second
  storey (side < 1/2 … here 0.463) first pays at seven. M_n → 2.2195 (Gerver's sofa, optimal by Baek).
* **C3′.** The best parallel mirror-symmetric seven-arch carries exactly 252/169 (lane 13/6 squares
  wide) — a rational value in a problem full of √2; worth an exact derivation.
* **C4.** Rows: w_n = (n+4)(√2−1)/2 exactly for all n ≥ 3 (close the gap in the chevron lemma).
* For n = 6 the best row is NOT optimal: tilting three of the squares by a few degrees gains 0.00017.

## "Room" of a motion

For the canonical motion, the set of points that are inside the corridor at every moment is the
largest sofa that can make the same journey. Its area (pixel count, 3 digits): n = 2: 1.69; 3: 1.74;
4: 1.95; 5: 2.03; 6: 1.97; 7: 2.01 — against Gerver's 2.2195. The crates use 69 %, 82 %, 75 %, 71 %,
71 %, 67 % of the room their own journey leaves.

## Files
`corner.py` (criterion), `opt.py n starts [seed0]` (free search → best_n.json), `skyline.py` (rows),
`polish.py n` (restarts from best_n.json), `chosen.json` (the six assemblies of the sun print), `best_n.json`, `arch7_sym.json`, logs.
Nothing was posted to MathOverflow.
