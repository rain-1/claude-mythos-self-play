# Schneider's non-convexity index of sumsets — notes on MO 516522

Setting: M ⊂ ℝ^d compact, K = conv M, c(M) = inf{λ ≥ 0 : M + λK convex}, nM = M + … + M.
Write **a_n = n · c(nM)** (the amount of K that must be added to nM to make it convex).
The question asks for the best lower bound for c((n+1)M) in terms of c(nM), n and d.

## 1. A pointwise formula (used for every number below)

M + λK is convex iff it equals (1+λ)K, iff every u ∈ K lies in some m + s(K − m) with
s = λ/(1+λ): the hull shrunk towards a point of M by the factor s. So with

    s(u) = min over pieces P of M of  max_j (ν_j·u − h_P(ν_j)) / (h_K(ν_j) − h_P(ν_j)),
    s*   = max_{u ∈ K} s(u),              c(M) = s*/(1 − s*).

(ν_j runs over the edge normals of K and of the pieces; h is the support function.) For a union
of convex polygons this is exact, and sumsets cost nothing because support functions add:
the pieces of nM are the sums of n rows of the support table. `convex_union.py` does this;
`schneider.py` is the earlier points-only version.

Checks: simplex vertices give a_n = d for every n (c(nM) = 2/n in the plane); a square's
vertices give a_n = 1; the boundary of a 48-gon gives a = (1, 0, 0); the fat simplex
(vertices replaced by ε-copies of the simplex) gives a_n = max(0, d − (n+d)ε) — all reproduced
to 1e-12.

## 2. What is true

* **a_{n+1} ≥ a_n − 1 in every dimension.** (The MO answer states this with K a ball; the same
  three lines work for K = conv M: if (n+1)M + bK is convex then it is (n+1+b)K, and
  (n+1)M + bK ⊂ nM + (1+b)K ⊂ (n+1+b)K, so nM + (1+b)K is convex and a_n ≤ 1 + a_{n+1}.)
* It is **attained at n = 1 in the plane**: the boundary of any centrally symmetric polygon has
  a = (1, 0). The corner pieces of a regular 4-, 6- or 8-gon (keep a fraction t at each end of
  each edge) interpolate: a_1 = 1 and a_2 = 1 − 2t for the square.
* **The simplex line.** Fat simplices and the corner pieces of a triangle (equal arms t ≤ 1/3)
  both give a_n = 2 − (n+2)t in the plane, i.e. they satisfy with equality

      (n+d) a_{n+1} = (n+d+1) a_n − d.                                   (S)

  For d = 1 this is exactly the inequality proved in the linked answer on MO 511150.
* The "naive bound" of the question is false already for a circle (as the answer says), and so
  is (S) at n = 1: the circle has (S)-defect (n+3)a_n − 2 − (n+2)a_{n+1} = 2.

## 3. A conjecture I made today, and its counterexample

Since every failure above happens at n = 1 < d, I guessed: **(S) holds as an inequality "≥" for
all n ≥ d.** It is true for d = 1, and held with room to spare for every explicit family
(corner pieces of regular 3-, 4-, 5-, 6-, 8-gons, n = 2, 3) and for 3,960 random lattice point sets (the only positive defects were numerical misses on needle-thin triangles, whose true a_n is 2).

It is **false**. A hill-climb over sets of the form "end pieces of the edges of a convex
polygon" found, for a quadrilateral (`climb_0.json`: 7 segments and one vertex),

    a_2 = 0.959869,  a_3 = 0.697590,   5 a_2 − 2 − 4 a_3 = +0.00898 > 0.

Verified three ways: the search's own evaluation, a re-run at 3× and 6× the grid, and a brute
force over a 1600² grid with 100 refined candidates (all agree to 6 digits). A second apparent
violation (a triangle, +0.035) was an artifact of a missed maximum and disappeared at higher
resolution — so I only trust the one that survived the brute force. For triangles with unequal
arms I found no violation.

So the true extremal function for d = 2, n = 2 lies strictly between the proven a_3 ≥ a_2 − 1
and the simplex line, and it is *close* to the simplex line (the violation is under 1 % of a_2).

**Open (my current guess):** (S) holds for n ≥ d when K is a simplex; the excess for general K is
governed by how far K is from a simplex. I have no proof of either half.

## 4. Files

`convex_union.py` (the tool), `families.py`, `families2.py` (explicit families), `asym.py`
(triangle, one short arm: no violation), `survey.py`/`analyse.py` (random lattice sets),
`search2.py`, `climb.py` (structured search), `climb_0.json` (the counterexample).
