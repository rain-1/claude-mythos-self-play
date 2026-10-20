# Square achievement game (MathOverflow 514742): computational results

Game: two players alternately claim cells of an n x n grid. The first to own the 4 corners
of an axis-parallel square (any size) wins. A full board with no such square is a draw.
X = first player.

## Summary

| n | value (perfect play) | X moves needed (exact min) | nodes (main solver, all ID iterations) | independent check |
|---|---|---|---|---|
| 3 | draw | - | 1 (Erdos-Selfridge at root) | - |
| 4 | draw | - | 297 | verify2: no win within 8 X moves (162.9K nodes) |
| 5 | **X wins** | **10** (19 plies) | 2.39M (d=10 iteration: 0.63M) | verify2: win within 10 (50.1M nodes, 39 s); **and no win within 9** (56.9M nodes, 43 s) |
| 6 | **X wins** | **8** (15 plies) | 1.30M (d=8 iteration: 0.64M), ~5 s | verify2: win within 8 (52.6M nodes, 29 s) **and no win within 7** (85.4M nodes, 56 s) |
| 7 | **X wins** | **8** | 4.92M (d=8: 0.52M), ~4 s | verify2: win within 8 (318.5M nodes, 173 s) **and no win within 7** (1.22G nodes, 736 s) |
| 8 | **X wins** | **8** | 15.3M (d=8: 1.58M), ~12 s | - |
| 9 | **X wins** | <= 8 | 2.15M (d=8 only), 3 s | not re-run after the fix (old buggy run timed out) |
| 10 | **X wins** | <= 8 | 12.0M, 15 s | - |
| 11 | **X wins** | <= 8 | 10.0M, 11 s | - |
| 12 | **X wins** | <= 8 | 54.8M, 61 s | - |
| 13 | **X wins** | <= 8 | 39.5M, 51 s | - |
| 14 | **X wins** | <= 8 | 211.9M, 320 s | - |

**Minimum vs upper bound.** "exactly k" means a win within k AND no win within k-1 X moves.
n=5, 6 and 7: both halves confirmed independently by verify2 (after the fix below).
n=8: minimum from the main solvers only. n=9..14: depth 8 searched directly, so 8 is only an
**upper bound** there (no lower-bound search was run).

**Verifier bug (found and fixed).** The first versions of verify.c/verify2.c returned "X wins"
at an O-to-move node where X had two open threats, even when X had used up its move budget (d=0).
So `verify n d` really certified "win within d+1". That's why `verify 6 7` and `verify2 6 7`
wrongly reported a win (coordinator's discrepancy). Fix: `if (d == 0) return 0;` for either side to
move. The main solvers always had this right (`if (nt >= 2) return d >= 1 ? WIN(1) : FAIL(0)`), and the
corrected verifier now agrees with them exactly for n=4,5,6,7. Every verifier number in the
table comes from the corrected binaries.

**Conclusion:** the first player wins for every 6 <= n <= 14, always within 8 of their own
moves. Together with Jenrich (n=5) and Bacher-Eliahou (n >= 15: every 2-colouring of
15x15 has a monochromatic square, so the full board can't be a draw and strategy stealing
gives X the win), this would settle the question: **draw for n = 3, 4; first-player win for
every n >= 5.** Caveat: this is computer-search evidence (the corrected independent plain verifier confirms
n = 6 and 7 exactly (win in 8, not in 7) and n=5 exactly (win in 10, not in 9); for n = 8..14 only the main solvers have been run,
so those results rest on sqgame.c/sqwide.c; their pruning rules are listed under Method), not a human-checkable proof. n=5 needs 10 moves and n >= 6 need 8,
because the bigger board gives X room to build double threats sooner.

## Principal variations
X plays the fastest win and O the longest resistance (both exact, via iterative deepening at
every node). Cells are (row, col), 0-based.

### n = 5 (X wins on move 19)
PV (cells as (row,col)), X fastest win vs O longest resistance:
   1. X (2,2)  [X needs 10 own moves incl. this]
   2. O (0,2)  [best resistance: X still needs 9]
   3. X (2,1)  [X needs 9 own moves incl. this]
   4. O (1,1)  [best resistance: X still needs 8]
   5. X (3,1)  [X needs 8 own moves incl. this]
   6. O (3,2)  [best resistance: X still needs 7]
   7. X (3,0)  [X needs 7 own moves incl. this]
   8. O (2,0)  [best resistance: X still needs 6]
   9. X (2,3)  [X needs 6 own moves incl. this]
  10. O (1,2)  [best resistance: X still needs 5]
  11. X (0,1)  [X needs 5 own moves incl. this]
  12. O (0,3)  [best resistance: X still needs 4]
  13. X (1,3)  [X needs 4 own moves incl. this]
  14. O (1,4)  [best resistance: X still needs 3]
  15. X (3,4)  [X needs 3 own moves incl. this]
  16. O (0,4)  [best resistance: X still needs 2]
  17. X (4,1)  [X needs 2 own moves incl. this]
  18. O (0,0)  [best resistance: X still needs 1]
  19. X (4,0)  [X needs 1 own moves incl. this]
OXOOO
.OOXO
OXXX.
XXO.X
XX...

### n = 6 (X wins on move 15)
PV (cells as (row,col)), X fastest win vs O longest resistance:
   1. X (2,2)  [X needs 8 own moves incl. this]
   2. O (0,3)  [best resistance: X still needs 7]
   3. X (1,2)  [X needs 7 own moves incl. this]
   4. O (1,3)  [best resistance: X still needs 6]
   5. X (2,1)  [X needs 6 own moves incl. this]
   6. O (1,1)  [best resistance: X still needs 5]
   7. X (3,2)  [X needs 5 own moves incl. this]
   8. O (3,1)  [best resistance: X still needs 4]
   9. X (3,3)  [X needs 4 own moves incl. this]
  10. O (2,3)  [best resistance: X still needs 3]
  11. X (4,3)  [X needs 3 own moves incl. this]
  12. O (4,2)  [best resistance: X still needs 2]
  13. X (3,4)  [X needs 2 own moves incl. this]
  14. O (0,0)  [best resistance: X still needs 1]
  15. X (1,4)  [X needs 1 own moves incl. this]
O..O..
.OXOX.
.XXO..
.OXXX.
..OX..
......

### n = 7 (X wins on move 15)
PV (cells as (row,col)), X fastest win vs O longest resistance:
   1. X (2,2)  [X needs 8 own moves incl. this]
   2. O (3,4)  [best resistance: X still needs 7]
   3. X (1,2)  [X needs 7 own moves incl. this]
   4. O (2,3)  [best resistance: X still needs 6]
   5. X (2,1)  [X needs 6 own moves incl. this]
   6. O (1,1)  [best resistance: X still needs 5]
   7. X (2,4)  [X needs 5 own moves incl. this]
   8. O (0,0)  [best resistance: X still needs 4]
   9. X (0,4)  [X needs 4 own moves incl. this]
  10. O (0,2)  [best resistance: X still needs 3]
  11. X (2,6)  [X needs 3 own moves incl. this]
  12. O (0,6)  [best resistance: X still needs 2]
  13. X (4,4)  [X needs 2 own moves incl. this]
  14. O (0,1)  [best resistance: X still needs 1]
  15. X (4,2)  [X needs 1 own moves incl. this]
OOO.X.O
.OX....
.XXOX.X
....O..
..X.X..
.......
.......

(The PV blocks above are raw program output and look best in a monospace view.)

## Method
* `sqgame.c` (n <= 8, uint64 bitboards). Boolean AND/OR search for "X forces a win within
  d of its own moves", with iterative deepening on d, so the first d that succeeds is the
  exact minimum. Rules, all sound:
  - take an immediate win; block a single opponent 3-of-4; an opponent double threat is a loss;
  - Erdos-Selfridge with O as Breaker: if the sum over squares with no O of 2^-(empty cells)
    is < 1/2 (X to move) or < 1 (O to move), X can never win, so that branch fails absolutely;
  - lower bound: X needs at least min(4 - X-count) moves over squares with no O;
  - O to move, with d = 1 and fewer than 2 X threats: fail;
  - skip cells that lie in no square still live for either side. Claiming such a cell is a pass,
    and the game is monotone (an extra cell never hurts its owner), so the pass is dominated;
  - transposition table with exact canonical keys (min over the 8 symmetries, byte-lookup
    permutations), storing a proven win bound and a proven fail bound.
* `sqwide.c` (n <= 16): same logic, with incremental per-square counts and a 128-bit Zobrist key
  minimised over the 8 symmetries. Validated against sqgame.c on n=5,6,7: identical node
  counts and results at every depth.
* `verify.c` (n <= 8) and `verify2.c` (n <= 16): deliberately plain independent verifiers.
  They use only "take an immediate win" and "block a single threat / a double threat loses",
  try every other legal move, and memoise on the exact board with no symmetry, no
  Erdos-Selfridge and no dominance. Move ordering is a heuristic only.

Commands: `gcc -O3 -march=native -o sqgame sqgame.c`, then `./sqgame n [maxd] [ttlog2] [timelimit]`;
`./sqwide n d [ttlog2] [timelimit] [from_d] [pv]`; `./verify n d`; `./verify2 n d [tbits] [timelimit]`.
Logs: n3.log..n8.log, wide.log, verify2.log.

## Square-free 2-colourings (SAT; `sat_squarefree.py`, CaDiCaL 1.5.3 via pysat)
Each axis-parallel square gives 2 clauses (not all 0, not all 1). Balance uses a
sequential-counter cardinality constraint. Every grid in `squarefree.json` was re-checked by
brute force over all squares.

| key | n | constraint | ones | solve time |
|---|---|---|---|---|
| "14" | 14 | exactly 98 ones (perfectly balanced) | 98/196 | 5.5 s |
| "14_sym" | 14 | rot90 anti-symmetric: colour(rot90 p) = 1 - colour(p) (balanced automatically) | 98/196 | 0.01 s |
| "13" | 13 | exactly 84 ones | 84/169 | 1.1 s |
| "13_sym" | 13 | rot180 symmetric: colour(rot180 p) = colour(p), 84 ones | 84/169 | 0.3 s |

Notes. rot90 *symmetry* (colour preserved) is impossible for every n >= 2: the four corners of a
square centred on the board's centre form one rot90 orbit, so that square is monochromatic.
rot90 *anti*-symmetry needs n even, because for odd n the centre cell would have to differ from
itself. So for 13 the symmetric pattern uses 180-degree symmetry.
