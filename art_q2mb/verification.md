# Independent verification of the claw-free Schur-positivity counterexample

**Subject.** MathOverflow question 513515, *"Is this a counterexample to the claw-free
Schur-positivity conjecture?"* (2026-07), asks whether the 12-vertex example published in an
anonymous GitHub repository — with no paper, no preprint, and unknown authorship — really
refutes the conjecture (attributed to Gasharov, stated by Stanley) that the chromatic
symmetric function of a claw-free graph is Schur-positive.

This document reports a **complete, independent, exact verification built from first
principles** — no Sage, no sympy, no computer-algebra system. Everything is computed from
the graph's edge list with integer/rational arithmetic (`verify.py`, `extras.py`;
plain Python + `fractions.Fraction`; numpy only for a brute-force coloring cross-check).
We worked only from the edge set as stated in the MO question, not from the repository's code.

## The graph

H has vertices {a,b,c,d,u,v,x,y,l,m} and 12 edges

    ab, bc, cd, da,  au, av, uv,  cx, cy, xy,  bl, dm

(a 4-cycle *abcd*, triangles *auv* and *cxy* hung at the opposite corners *a* and *c*,
pendant edges *bl* and *dm*).  G = L(H) is its line graph: **12 vertices, 22 edges**,
connected.

## Results

1. **G is claw-free.** Exhaustive check of all centered triples: zero induced K₁,₃.
   (Line graphs are always claw-free; checked directly anyway.)

2. **The Schur expansion of X_G has exactly one negative coefficient:**

       [s_{(3,3,3,3)}] X_G = **−64**,

   confirming the repository's claimed value. The support of the Schur expansion is
   32 of the 77 partitions of 12 — precisely the partitions with all parts ≤ 4
   (note α(G) = 4), **except** (4,4,4) and (4,4,3,1), whose coefficients vanish.
   Every one of the other 31 coefficients is positive (full table in `results.json`).
   Notably −64 is also the coefficient of **smallest magnitude** in the whole expansion
   (the largest is 225504 at (2,1¹⁰)).

3. **e-expansion** (relevant since e-positive ⇒ Schur-positive): exactly two negative
   coefficients, [e₍₅,₄,₃₎] = −192 and [e₍₄,₄,₄₎] = −256. (Full table in `results.json`.)

4. **Local minimality — H is edge-critical.** For **every** connected subgraph H′ ⊊ H
   (all 2¹² edge subsets scanned), X_{L(H′)} is Schur-positive. Removing *any single
   edge of H — even a pendant edge —* restores Schur-positivity. The two pendant edges
   are essential to the counterexample. (This does not prove 12-vertex global minimality,
   but it shows the example is irredundant.)

5. **G is not an incomparability graph.** An exhaustive backtracking search shows the
   complement of G admits **no transitive orientation**. This is exactly as consistency
   demands: Gasharov's theorem proves Schur-positivity for claw-free *incomparability*
   graphs, so the counterexample necessarily lives in the gap between "claw-free" and
   "claw-free incomparability" — and it does.

6. **Neighborhood scan** (`variants.py`). Among all 64 ways to re-attach the two pendant
   edges, only the original placement (pendants at b and d, the two cycle vertices
   between the triangle corners) is Schur-negative. Among all 33 single-edge additions
   to H, exactly one preserves negativity: the diagonal ac joining the two
   triangle-bearing corners, giving a 13-vertex claw-free graph with
   [s₍₃,₃,₃,₃,₁₎] = −64 — the wound persists with a singleton part appended.
   Among 228 structural variants (C₄/C₅/C₆ cores, all placements of the two triangles
   and two pendants), only the original C₄ configuration — triangles at opposite
   corners, pendants at the two remaining corners — is negative; no C₅ or C₆ analogue
   exists in this family. Line graphs of 400 random connected graphs (8–12 edges):
   all Schur-positive. In total: 725 nearby/random machines scanned, and the failure
   is exactly the original design and its one 13-vertex extension (`variants.json`).

## Method and cross-checks

* **p-expansion.** X_G = Σ_{S⊆E} (−1)^{|S|} p_{λ(S)} computed by a signed DFS over edges
  with exact cancellation pruning (if an edge's endpoints are already joined, the subtree
  cancels in pairs S ↔ S△{e}). 163296 surviving leaves; all 77 coefficients nonzero, and
  their signs alternate as (−1)^{n−ℓ(λ)}, as forced by the Whitney/NBC theorem — first
  internal consistency check. (163296 is simultaneously the number of acyclic
  orientations |χ_G(−1)| and the coefficient [s_{1¹²}], as it must be.)

* **Character table.** The full 77×77 character table of S₁₂ was computed by
  Murnaghan–Nakayama recursion on beta-sets and verified by (i) Σ (f^μ)² = 12!,
  (ii) the trivial and sign characters, and (iii) **full exact row orthogonality**
  Σ_λ χ^μ(λ)χ^ν(λ)/z_λ = δ_{μν} for all 3003 pairs, in exact rational arithmetic.

* **Schur coefficients.** [s_μ] X_G = ⟨X_G, s_μ⟩ = Σ_λ c_λ χ^μ(λ) (since ⟨p_λ, s_μ⟩ = χ^μ(λ)).

* **e-coefficients.** Exact 77×77 Gaussian elimination over ℚ expressing X_G in the
  {e_μ} basis in p-coordinates; the solution re-multiplied out and checked against the
  p-expansion coefficient-by-coefficient.

* **Chromatic polynomial four ways.** χ_G(k) computed from (i) the p-expansion
  (p_λ ↦ k^{ℓ(λ)}), (ii) the Schur expansion via hook-content
  s_μ(1^k) = Π (k+j−i)/h(i,j), (iii) an independent deletion–contraction recursion, and
  (iv) brute-force enumeration of proper colorings for k = 3, 4. All agree:
  χ_G(3) = 0, χ_G(4) = 5376, χ_G(5) = 758160 — G is 4-chromatic with ω(G) = 4.

* **Stable-partition census** (independent DFS over partitions of V into independent
  sets, verified against χ_G via falling factorials): 94154 stable partitions in all;
  those with ≤ 4 blocks — the entire 4-coloring ecology — comprise exactly three types:

       type (4,4,2,2): 32     type (4,3,3,2): 160     type (3,3,3,3): 32

  So proper 4-colorings *of the equal-quarters type exist* (32 of them, up to color
  names): the monomial expansion is positive at (3,3,3,3), as it always is, while the
  Schur weight there is −64. Curiously −64 = −2 · 32.

## Conclusion

The anonymous example is **correct**: G = L(H) is a connected, claw-free, 12-vertex,
4-chromatic graph whose chromatic symmetric function is not Schur-positive, with the
unique negativity −64 at the equal-quarters shape (3,3,3,3). The Gasharov–Stanley
claw-free Schur-positivity conjecture is false, and the failure is razor-thin: one
partition out of 77, the smallest coefficient in the expansion, destroyed by deleting
any single edge of H.

*(Produced 2026-07-25 by an automated art-and-mathematics routine; the verification code
in this directory is self-contained and runs in under 10 seconds.)*
