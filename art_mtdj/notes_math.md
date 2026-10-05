# Math notes — run 2026-10-05 (pastel #28, BEAUTY SEEKS REASON)

## MO 515731 — Which polygons are forgetful?  **SOLVED: forgetful ⇔ isogonal**

*Forgetful* means that deleting any one vertex leaves congruent polygons.

**Theorem.** A convex n-gon (n ≥ 4) is forgetful iff it is inscribed in a circle and its arcs are all equal
(regular) or, when n is even, alternate a, b, a, b, … In other words, the forgetful polygons are exactly the
**isogonal (vertex-transitive) polygons**. (n = 3: equilateral.)

*Proof.* The OP shows that the vertices are concyclic. Every deleted polygon has the same circumcircle,
so a congruence between two of them fixes the centre and is a rotation or reflection. Write the polygon
as its cyclic arc sequence x_1..x_n (with Σ = 2π). Deleting the vertex between x_i and x_{i+1} merges them
into one arc s_i = x_i + x_{i+1}, so the arc multisets M_i = M − {x_i, x_{i+1}} + {s_i} must all be equal.
Let m = min x. Since s_i ≥ 2m > m, the number of m's in M_i is #m(M) − c_i, where c_i = number of minimal
arcs among {x_i, x_{i+1}}. So c_i is constant: c = 2 gives all arcs equal (regular); c = 0 is impossible;
c = 1 means minimal and non-minimal arcs alternate (n even). For the non-minimal arcs y_j: take y_max. Deleting
next to it puts y_max + m into the multiset as its maximum. Deleting next to any other y_j leaves y_max
in place and adds y_j + m, so the maximum is max(y_max, y_j + m), and this has to equal y_max + m. Hence
y_j = y_max, and the arcs alternate m, y. Conversely, alternating arcs: merging any adjacent pair gives
(a+b) followed by a,b,…,a,b or by b,a,…,b,a. These are mirror images, so they are congruent. ∎

Checked exhaustively over integer arc sequences (n = 4..8, arcs 1..5): no other forgetful sequences.
`forgetful_check.py`.

## MO 515726 — can adding a vertex change every edge of the unique shortest tour?  **NO (via Thomason's parity)**

**Reduction.** Suppose T1 (the unique optimum in G) and T2 (the unique optimum in G' = G + v) share no edge.
Let x, y be v's neighbours in T2, and P = T2 − v, an x–y Hamiltonian path of G edge-disjoint from T1. Join
x, y by a new edge e*. Then H = T1 ∪ P ∪ {e*} is a 4-regular (multi)graph with a Hamiltonian decomposition
(T1, P + e*). **Thomason (1978)**: the number of Hamiltonian decompositions of a 4-regular graph is even. So there is
another decomposition {D1, D2}, with e* ∈ D2. Put Q = D2 − e*, an x–y Hamiltonian path of G. Then D1 ∪ Q is the
same edge multiset as T1 ∪ P, so w(D1) + w(Q) = w(T1) + w(P). Here D1 ≠ T1, so uniqueness gives
w(D1) > w(T1), hence w(Q) < w(P), and Q + xv + vy is a tour of G' that is cheaper than T2. Contradiction.
(If x, y are adjacent in T1, then e* is parallel to a T1 edge and the multigraph version of the parity is needed.
Thomason's lollipop argument does not use simplicity. All n ≤ 10 data below include this case.)

**Independent computation.** WLOG G = T1 ∪ P and deg v = 2 (extra edges only add competitors).
- LP feasibility (`ham_lp.py`, scipy HiGHS): no weights exist for any (T1, P) with n ≤ 9.
- Re-decomposition census (`ham_redecomp.py`): every pair has a twin decomposition, for n = 5..10
  (5, 30, 231, 1960, 18477, 191 370 pairs).
- The number of twins is **always odd** (n ≤ 9 exhaustive: e.g. n = 9 distribution 7, 9, 11, …, 23). That matches the
  parity. Random 4-regular simple graphs and unions of two random Ham cycles on 9–11 vertices
  (`hd_parity.py`, ~1,100 graphs): every decomposition count is even.
- Minimum number of twins: 5 (n = 5, 6), then 7 (n = 7, 8, 9). The instance drawn has 15 twins (n = 11).

## MO 499477 — two kinds of random line with the same chance

Configuration (found numerically, since the OP's figure wasn't fetched): three circles in a row, tangent, with
**red (1) – green (r) – black (r²)**, green in the middle. A on red, B and C on green. Then
P(line AB meets black) = P(line BC meets black). For r = 0.62 this is 0.304702 (quadrature: chord directions
from a point of a circle are uniform, so P_BC = E_B[2 arcsin(r²/|B − c_black|)]/π). MC with 2·10⁶ samples agrees.
**The equality is not pointwise in B** (for B at angle 1.0: cone/π = 0.299 but red-arc fraction = 0.154). It is
a statement about averages. Possible route: the inversion about the external homothety centre with power
t_red·t_black swaps red ↔ black and fixes green.

## MO 515413 — Narayana polynomials mod 2

OP's identity f(2^m + k) = f(k)(1 + t^{2^m}) verified for all n ≤ 512. The parity triangle is a Sierpiński
variant (density 0.125 at n ≤ 512). Not drawn (too familiar a picture).

## Second batch (same day, on request): ideas 4–6

### MO 499431 — piles and the last pile (`piles/piles.py`, `piles/field.py`)
Exact expected size of the last pile by memoised recursion over sorted pile tuples. **The balanced split is optimal in
every case checked:** K = 3 for N ≤ 500, K = 4 for N ≤ 200, K = 5 for N ≤ 60, K = 6 for N ≤ 40 (no violations).
- **Runner-up pattern (new observation):** the second-best split is always the balanced one with ONE rock moved between
  two equal piles. Examples: (166,167,167) → (166,166,168), and (50,50,50,50) → (49,50,50,51). Holds in all 254 cases checked
  (K = 3 to N = 150, K = 4 to 80, K = 5 to 45).
- Balanced E grows like c_K √N (K = 4: E(80) = 3.624, E(90) = 3.852, ratio ≈ √(90/80)).
- The K = 3 field E(a,b,c) over the simplex: the minimum is at the centre, and a Y-shaped low valley runs toward the three
  edge midpoints (two equal piles, one empty). Note: bilinear interpolation on the (a,b) square grid is
  anisotropic, so symmetrise over the 6 permutations before contouring.

### MO 515601 — the lipogram map d (`render_lipo2.py`)
No proof. **Conjecture: d ∉ G.** Heuristic: an f ∈ G uses a fixed finite set of floors and constants, so it can
read only boundedly many "digit scales" of n. d must act on all decimal places at once: its zero set
{0, 7, 77, 777, …} is infinite but exponentially sparse, and d(n·10 + 7) = d(n) at every scale. A proof would need a structure theorem for
the zero sets (or the growth regimes) of functions in G restricted to ℕ.

### MO 515413 — Narayana parity (`narayana.py`, `render_lace.py`)
Identity checked for all n ≤ 512, as before. Drawn after all, as a doily, because the hexagonal six-copy layout
makes the familiar Sierpiński structure look new.
