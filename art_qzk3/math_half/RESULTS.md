# MO 516850 — graphs with exactly half of their spanning subgraphs connected

`C(G)` = number of connected spanning subgraphs of `G` (= Tutte `T_G(1,2)`), `m` = number of edges.
"Half-connected": `C(G) = 2^(m−1)`.

## What was checked (`half.py`, `walk.py`)

* Exhaustive over the graph atlas (all graphs on ≤ 7 vertices): the half-connected graphs are
  `K_2`, `K_3` and exactly one graph on 7 vertices (13 edges, 4096 of 8192) — the triangular
  prism with an extra vertex joined to the four corners of a rectangular face. Agrees with the
  counts 0,1,1,0,0,0,1 in the question.
* For that graph, connected spanning subgraphs by number of edges 6…13:
  `672, 1220, 1139, 689, 284, 78, 13, 1` (sum 4096; 672 spanning trees).

## Three small lemmas

1. **Parity.** `C(G)` is odd iff `G` is connected and bipartite.
   *Proof.* `T_G` has integer coefficients, so `T_G(1,2) ≡ T_G(−1,0) (mod 2)`, and
   `T_G(−1,0) = ± P_G(2)/2` for connected `G`, which is ±1 if `G` is bipartite and 0 otherwise. ∎
   (Checked on every connected graph with ≤ 7 vertices.) So a half-connected graph with `m ≥ 2`
   is not bipartite, and the question is 2-adic: since `0 < C(G) < 2^m`,
   **`G` is half-connected ⇔ `2^(m−1)` divides `T_G(1,2)`.**
2. **2-connected.** If `G` has a cut vertex, `C(G) = C(G_1)·C(G_2)`; for the product to be
   `2^(m−1)` both factors are powers of two with ratios `C(G_i)/2^(m_i) ∈ {1, 1/2, 1/4, …}`
   multiplying to 1/2, so one side is a single vertex. Hence every half-connected graph on
   ≥ 3 vertices is 2-connected.
3. **Gluing along two vertices.** For a piece `H` with terminals `s,t` let `a` = number of
   connected spanning subgraphs and `b` = number with exactly two components separating `s`
   from `t`; `σ = (a+b)/2^m`, `β = b/2^m`. Gluing pieces in parallel at `s,t` gives
   `C/2^m = Π σ_i − Π β_i`. So one wants `Π σ_i − Π β_i = 1/2`.
   Computer search over all 6900 distinct pieces on ≤ 7 vertices: the only solutions with two
   pieces are trivial (`K_3` = edge ∥ path) — **no half-connected graph on 8…12 vertices has a
   2-vertex cut with both sides of ≤ 7 vertices.** The examples for n = 8, 9, 10 are
   "3-connected-like"; small solutions do not compose.

## Heuristic and conjecture

For a graph with minimum degree ≫ 1 the probability that a random half of the edges is
connected is ≈ `exp(−Σ_v 2^(−deg v))`, so half-connected graphs live where
`Σ_v 2^(−deg v) ≈ ln 2`, i.e. degrees ≈ `log₂ n + 0.5`, `m ≈ (n/2) log₂ n`. In that window there
are roughly `C(N,m)/n!` graphs (N = n(n−1)/2) and the "probability" that `T(1,2)` lands exactly
on `2^(m−1)` is of order `2^(−m)`; the product grows super-exponentially in `n`.

**Conjecture.** Half-connected graphs exist for every `n ≥ 7`, and their number grows faster
than any exponential. (Evidence is thin: 1, 1, 2, 12 for n = 7…10.)

A Metropolis walk on labelled graphs (`walk.py`, energy `|log₂C − (m−1)|`) finds n = 10
examples within minutes (8 labelled hits in 6.7 million steps, m = 22…26; see
`walk_n10_s1.json`).

**New examples on 11 vertices** (the question's list stops at n = 10). Three pairwise
non-isomorphic half-connected graphs, each re-verified with the independent pure-Python count
in `half.py` (`walk_n11_s2.json`):

* m = 27, C = 2^26: 0-2 0-3 0-5 0-7 0-8 0-10 1-2 1-6 1-8 1-10 2-3 2-6 2-9 3-5 3-6 3-7 4-5 4-8 5-8 6-7 6-9 6-10 7-8 7-10 8-9 8-10 9-10
* m = 25, C = 2^24: 0-1 0-2 0-3 0-8 0-9 0-10 1-4 1-5 1-7 1-8 1-9 2-4 2-5 2-6 3-4 3-5 3-6 3-10 4-6 4-10 5-7 5-9 6-7 6-8 7-8
* m = 26, C = 2^25: 0-2 0-4 0-5 0-8 0-10 1-4 1-5 1-8 1-10 2-8 2-9 3-4 3-6 3-7 4-6 4-8 4-9 5-7 5-8 5-9 5-10 6-7 6-8 7-10 8-10 9-10

So the counts continue 0,1,1,0,0,0,1,1,2,12, (≥3). The n = 10 walk hit 6 of the 12 classes in
four minutes. An n = 12 walk of ~35 CPU-minutes found nothing (each step costs 3^12 operations;
this is a budget limit, not evidence).

What would settle the question: one infinite family. The lemmas say where *not* to look —
not bipartite, no cut vertex, apparently no small 2-cuts, and (because bounded-degree families
have `C/2^m → 0` exponentially) degrees must grow like `log₂ n`.
