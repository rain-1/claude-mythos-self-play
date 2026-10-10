# MO 515850: zero-sum parts of the reciprocals 1/3697 … 1/4325 mod 10567³

p = 10567, M = p³ = 1 179 926 954 263, U = {3697,…,4325} (629 numbers), r_k = k⁻¹ mod M.
Σ_{k∈U} r_k = 308·M (so the whole interval is one zero-sum part; 308 turns).

## Complete census of small zero-sum subsets (exact, meet-in-the-middle, `zs.c`)
| size | count | method |
|---|---|---|
| 1–4 | **0** | pair+pair hash (Python check) |
| 5 | **1** | triple (3 smallest) + pair, canonical split |
| 6 | **76** | triple + triple (matches the OP's 76) |
| 7 | **6 304** | triple + quad, 6.4·10⁹ lookups, 4 min |
| 8 | ≥ 211 720 (≈43 % of the ≈4.9·10⁵ expected) | windowed 4+4 (`zs8.c`, |sum| < 0.008 M) |
Counts agree with the heuristic C(629,k)/M (0.7, 71, ~6300, ~4.9·10⁵).

## Upper bound N ≤ 94 (proved from the census)
In a partition into N zero-sum parts let a = #parts of size 5, b = #parts of size 6; all other parts have size ≥ 7.
Then 629 ≥ 5a + 6b + 7(N − a − b), i.e. 7N ≤ 629 + 2a + b. The parts of size 5 and 6 are disjoint members of the
census above; CP-SAT proves max(2a + b) over disjoint families = **33** (optimal: the 5-set + 31 six-sets).
Hence **7N ≤ 662, N ≤ 94**. (An LP refinement N ≤ (629 + W)/8 with W = max Σ(8 − |S|) over parts of size ≤ 7 gives
the same 94 at the LP level; CP-SAT found W ≥ 104, so this route cannot go below 91.)

## Lower bound attempts
Packing only parts of size ≤ 7: CP-SAT finds 71 disjoint (+1 leftover part = 72). With the harvested 8-sets a
greedy/local search reached 75 packed (N = 76). The OP's 86 is not beaten here: the leftovers want 8–10-sets
that a 43 % harvest does not contain. So: **86 ≤ N_max ≤ 94**.
Seed: pool search (enumerate all zero-sum 8/9-subsets inside the free elements + a few dropped parts, 4+5 MITM in C)
is the natural next step; a full 8-set census via Schroeppel–Shamir would also let the bound use parts of size 8.
