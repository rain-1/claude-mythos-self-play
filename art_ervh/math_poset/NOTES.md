# g(n) = max e(P)/#Aut(P)  (MO 516140)

Notation: e = #linear extensions, f(P) = e(P)/#Aut(P), Z_a = fence (zigzag) on a
elements (Z_1 = point, Z_2 = 2-chain), Z_a* its dual (≠ Z_a only for odd a ≥ 3).
For connected C put h(C) = e(C)/(|C|!·#Aut C). For P = ⊔ m_C·C:

    f(P) = n! · ∏_C h(C)^{m_C} / m_C!          (exact; Aut(⊔) = ∏ Aut(C)≀S_{m_C})

## 1. Exact values (full enumeration, n ≤ 11)

All unlabeled posets were generated with nauty's `genposetg` (counts reproduced:
1,2,5,16,63,318,2045,16999,183231,2567284,46749427; connected: …,2360719,43944974),
with a C plug-in (`posetplugin.c`) computing e(P) by DP over down-sets and #Aut by
backtracking with twin-class reduction. Results were re-checked by a separate
Python implementation (`analyze.py`) and, for n ≤ 6, by naive brute force over all
naturally-labelled relations (`verify_small.py`). n = 11 took 162 s on one core;
n = 12 (1.1·10⁹ posets, est. ~65 min) was not run.

| n | g(n) | all optimal posets | fence union? |
|---|------|--------------------|--------------|
| 1 | 1 | Z1 | yes |
| 2 | 1 | Z2 ; Z1⊔Z1 | yes |
| 3 | 3 | Z2⊔Z1 | yes |
| 4 | 6 | Z2⊔Z1⊔Z1 | yes |
| 5 | 25 | Z4⊔Z1 | yes |
| 6 | 75 | Z4⊔Z2 ; Z4⊔Z1⊔Z1 | yes |
| 7 | 525 | Z4⊔Z2⊔Z1 | yes |
| **8** | **2384** | **Q7⊔Z1 ; Q7*⊔Z1** | **NO** (best fence union: Z4⊔Z2⊔Z1⊔Z1 = 2100) |
| 9 | 15372 | Z6⊔Z2⊔Z1 | yes |
| **10** | **107280** | **Q7⊔Z2⊔Z1 ; Q7*⊔Z2⊔Z1** | **NO** (best fence union 76860) |
| **11** | **798435** | **Q8⊔Z2⊔Z1** | **NO** (best fence union 704550) |

Cover relations for every optimal poset (and the next 3 values of f with their
posets) are in `optimal.json`.

**The non-fence components** (both are height-2 trees, Aut trivial):

* **Q7** (7 elements, e = 298, beats Z7: e/Aut = 272/2 = 136): the fence
  x1>x2<x3>x4<x5>x6 plus one extra minimal element y < x3.
  Covers: 2<1, 2<3, 4<3, 4<5, 6<5, y<3. Q7* is its dual (not isomorphic).
  Check: e(Q7 ⊔ pt) = 8·298 = 2384 (also verified by brute force over 8!).
* **Q8** (8 elements, e = 1613 > E_8 = 1385, self-dual): x1>x2<x3>x4<x5>x6 plus a
  minimal y < x3 and a maximal z > x4. Covers: 0<4 0<5 0<6 1<4 1<7 2<5 3<4.

So the answer to the "in particular" is **negative**: already at n = 8 no
disjoint union of fences (and duals) is optimal. The optima n ≤ 11 are still
disjoint unions of pairwise non-isomorphic connected posets with trivial Aut,
except that two isolated points (h(pt)²/2! = 1/2 = h(Z2))
may replace Z2 — this is the source of the ties at n = 2, 6.

Best connected posets (exact, from the enumeration): k=5: path 2>1<3<4>0 (e=11,
height 3, beats Z5 e/Aut=8); k=6: Z6 (61); k=7: Q7 (298); k=8: Q8 (1613);
k=9: 9348; k=10: 61658; k=11: 465590 — for k ≥ 6 all are height-2 trees.

## 2. Fence unions (theory, exact optimum n ≤ 40, `fences.py`)

e(Z_a) = E_a (Euler zigzag: 1,1,1,2,5,16,61,272,1385,…). Aut(Z_a) = 1 for a ≤ 2
and a even (the reversal is an *anti*-automorphism, Z_a self-dual); for odd a ≥ 3
reversal is an automorphism, #Aut = 2, and Z_a ≇ Z_a* (W vs M shape).
Hence h(Z_a) = E_a/a! for even a, E_a/(2·a!) for odd a ≥ 3, and the best fence
union is a knapsack over these classes (solved exactly by DP over n with
Fractions; `fence_unions.json`).

Result: **the optimal fence union never uses an odd fence ≥ 3**; it is
`Z1 (or 2·Z1) + distinct even fences`, the even sizes being {2,4,…,2r} with at
most one size omitted, e.g.
n=13: Z1+Z2+Z4+Z6; n=21: Z1+Z2+Z4+Z6+Z8; n=31: Z1+Z2+Z4+Z6+Z8+Z10;
n=40: 2Z1+Z2+Z6+Z8+Z10+Z12. So r ≈ √n components.

Why: E_a/a! = 2(2/π)^{a+1}(1+O(3^{-a})) (agrees to 4 digits for a ≥ 6), so
h(Z_a) ≈ (4/π)(2/π)^a and f/n! ≈ (2/π)^n (4/π)^{#components}/∏ m!·2^{#odd}.
Every extra component gains 4/π ≈ 1.27, but a repeated class costs 1/m (≤ 1/2)
and an odd fence costs 1/2, both > the gain; so components are distinct even
fences and their number is maximised: sizes 2,4,…,2r (sum r(r+1)) plus 1–2 points
and one size dropped to fix the parity/total. Ratio to the brute-force optimum:
equal for n ≤ 7 and n = 9; smaller for n = 8, 10, 11.

## 3. Beyond n = 11 (heuristic / lower bounds, `unions_best.json`)

Knapsack over: all connected posets ≤ 11 (top 60 per size — exact for unions
with components ≤ 11, by an exchange argument), all posets with tree Hasse
diagram of size 12, 13 (`oriented_trees.py`, 492180 and 2266502 classes,
counts = OEIS A000238), height-2 trees of size 14–17 (`trees.py`), fences.

| n | best found f | components | best fence union | ratio |
|---|---|---|---|---|
| 12 | 6169680 | Z1+Z2+C9 | 4227300 | 1.46 |
| 13 | 54954900 | Z1+Z2+Z4+Z6 (fence union!) | same | 1.00 |
| 14 | 536936400 | Z1+Z2+Z4+Q7 | 384684300 | 1.40 |
| 15 | 5449318875 | Z1+Z2+Z4+Q8 | 4679049375 | 1.16 |
| 16 | 56144088000 | Z1+Z2+Z4+C9 | 37432395000 | 1.50 |
| 20 | 1.316e15 | Z1+Z2+Z4+T13 | 7.375e14 | 1.78 |
| 21 | 1.861e16 | Z1+Z2+Z4+Q7+Q7* | 1.549e16 | 1.20 |
| 30 | 2.549e27 | Z1+Z2+Z4+Q7+T16 | 1.120e27 | 2.28 |
| 40 | 1.386e41 | Z1+Z2+Z4+Q7+Q7*+Q8+C11 | 4.663e40 | 2.97 |

(full table n ≤ 40 printed by `fences.py`). These f-values are rigorous lower
bounds for g(n) (explicit posets) and prove that fence unions are **not**
optimal for n = 8, 10, 11, 12 and every n in 14..40. g(12) = 6169680 and
g(13) = 54954900 hold unless some connected 12- (resp. 12/13-) element poset
whose Hasse diagram is not a tree has e/#Aut above that (best tree-Hasse
connected 12-poset: 3729204, far below 6169680 — so g(12)=6169680 needs only
that no non-tree connected 12-poset has e/Aut > 6169680).

Best connected h(k) decays like ≈ 0.665^k (ratios h_k/h_{k-1} for k=9..17:
0.644–0.686) vs (2/π)^k = 0.637^k for fences; the gap grows exponentially.

## Conjectures (labelled, from the data above)

* **Conjecture A.** g(n) is attained by a disjoint union of pairwise
  non-isomorphic connected posets with trivial automorphism group (plus possibly
  two isolated points in place of a 2-chain), each component being a poset whose
  Hasse diagram is a tree, of height ≤ 2 for components with ≥ 6 elements.
  (True for n ≤ 11.)
* **Conjecture B.** Fence unions are optimal exactly for n ∈ {1,…,7, 9, 13}.
  (Proven for n ≤ 11 and n = 12, 14..40 non-optimal; n = 13 and n > 40 heuristic.)
* **Conjecture C.** g(n)/max_{fence unions} f → ∞; the best connected k-element
  posets have e/k! ≥ c·λ^k with λ ≈ 0.66 > 2/π.

## Files
`posetplugin.c` + `build.sh` (genposetg plug-in; nauty 2.8.8 source taken from the
pynauty sdist), `raw/n*.txt` (top f-values, all optimal posets, top-60 connected),
`analyze.py` → `optimal.json`, `verify_small.py`, `fences.py` →
`fence_unions.json`, `unions_best.json`, `trees.py`, `oriented_trees.py`,
`raw/trees_k.json`, `raw/otrees_k.json`.
