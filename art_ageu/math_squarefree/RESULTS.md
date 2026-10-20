# Quarter-turn anti-symmetric square-free colourings (run 22)

A 2-colouring of the n×n grid is *square-free* if no axis-parallel square (any side) has four corners of one
colour (Bacher–Eliahou: these exist exactly for n ≤ 14). Call it *anti-90* if turning the grid a quarter turn
swaps the two colours: colour(rot90 p) = 1 − colour(p). (Needs n even; it forces exactly n²/2 cells of each colour.)

Exact counts by SAT enumeration over the n²/4 free cells (`count_anti90.py`, `orbits.py`; every solution
re-checked by brute force):

| n | anti-90 square-free colourings | orbits under transpose/rotation/complement |
|---|---|---|
| 4 | 12 | 4 |
| 6 | 84 | 21 |
| 8 | 304 | 76 |
| 10 | 680 | 170 |
| 12 | 64 | 16 |
| 14 | **76** | **19** |
| 16 | 0 | 0 |

So the extremal size 14 is reached *with* the quarter-turn anti-symmetry. The count is not monotone (64 at 12,
76 at 14). The central 12×12 of an anti-90 14-colouring is an anti-90 12-colouring ("onion" restriction):
the 76 restrict to only **32** of the 64 (28 of them extend in exactly 2 ways, 4 in exactly 5 ways); the other
32 twelve-patterns are dead ends.

The dish in `dish_final.png` uses one of the 76 (the one in `../math_squaregame/squarefree.json`, key `14_sym`).
