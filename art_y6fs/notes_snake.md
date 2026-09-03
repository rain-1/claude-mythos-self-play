# Notes — The Snake That Sees Every Room (MO 514865)

**Question (MO 514865, unanswered).** A snake in the hypercube Q_n is an induced path (a
snake-in-the-box). Call a vertex set D-dense if every vertex of Q_n is within graph
distance D of it. Is there a universal D such that Q_n has a D-dense snake for every n?

**What we computed** (`snake.py`, `snake_2560_cert.json`).

| n | rooms 2ⁿ | min covering radius | snake length used | method |
|---|---|---|---|---|
| 2 | 4 | 1 | 3 | exhaustive (5 snakes from vertex 0) |
| 3 | 8 | 1 | 5 | exhaustive (22) |
| 4 | 16 | 1 | 8 | exhaustive (305) |
| 5 | 32 | 1 | 14 | exhaustive (41 186) |
| 6 | 64 | 1 | 20 | local search, instant |
| 7 | 128 | 1 | 31 | local search, instant |
| 8 | 256 | **1** | 59 | local search, 0.9 s (a first greedy pass had left 6 rooms at distance 2) |
| 9 | 512 | ≤ 2 | 110 | local search, 150 s budget; 6 rooms at distance 2 |
| 10 | 1024 | ≤ 2 | 183 | local search, 150 s budget; 27 rooms at distance 2 |

So D = 1 (a *dominating induced path*) exists for every n ≤ 8, found exhaustively for
n ≤ 5. For n = 9, 10 the search budget ran out at a handful of uncovered rooms; nothing
here suggests the answer changes.

**Counting.** A snake of L rooms dominates at most L + 6L… more precisely an interior snake
room has n−2 non-snake neighbours, so 1-density needs 2ⁿ − L ≤ (n−2)L + 2, i.e.
L ≥ (2ⁿ−2)/(n−1): 37 for n = 8 (we used 59), 64 for n = 9, 114 for n = 10. Longest known
snakes are far longer (98 in Q₈), so the count never obstructs. **Conjecture:** D = 1
suffices for all n — every hypercube has a dominating induced path. A construction would
likely go by products: a 1-dense snake of Q_n and the 4-cycle structure of Q_2 (Q_{n+2} =
Q_n × Q_2) suggest a doubling recipe, which is what the search's solutions look like when
drawn (long runs inside one 4×4 block, then a hop).

**Search.** Exhaustive: DFS over induced paths from vertex 0 (all snakes are equivalent under
the hypercube's symmetry to one starting at 0). Heuristic: grow greedily toward uncovered
rooms with random tie-breaking, then iterate "cut the snake at a random point and regrow",
accepting whenever the number of rooms farther than 1 does not increase. Inducedness of the
drawn snake is asserted explicitly (every hypercube edge between snake rooms joins
consecutive rooms).

**The picture.** Q₈ = Q₂⁴ drawn as a 4×4 grid of 4×4 blocks: each 2-bit coordinate is a
4-cycle laid out in Gray order (00, 01, 11, 10), so every hypercube edge is a step of ±1 mod 4
in exactly one of four directions — neighbouring cells, a wrap across a block, a hop to the
neighbouring block, or a wrap across the whole map. Each room is tinted by the snake room
that sees it (hue = position along the snake), so the map is the snake's territories; the
snake itself is an ink thread with coral beads, short steps thick, hops and wraps as
thinner arcs.
