# The finite futures of one defector — spatial Prisoner's Dilemma (Nowak & May 1992)

**Model** (`nowak.py`). Square lattice, Moore neighbourhood, self-interaction included, deterministic
synchronous update. A cooperator whose 3×3 block (itself included) holds *n* cooperators scores *n*
(C–C pays 1, C–D pays 0). A defector with *m* cooperating neighbours scores *b·m* (D–C pays *b*,
D–D pays 0). Each site then adopts the strategy of the highest-scoring site of its 3×3 block, itself
included; on an exact tie it keeps its own strategy. Initial condition: one defector in an infinite
sea of cooperators (the grid is 2T+41 wide for T generations, so the frontier, which advances one
site per generation, never sees the edge).

## Theorem (finiteness of futures)
Every decision compares a cooperator score *n* ∈ {1,…,9} with a defector score *b·m*, *m* ∈ {1,…,8},
or two scores of the same type (independent of *b*). Hence the update map depends on *b* only through
the set of fractions *n/m* below *b*. The fractions *n/m* > 1 with *n* ≤ 9, *m* ≤ 8 are, in lowest
terms,

    9/8, 8/7, 7/6, 6/5, 5/4, 9/7, 4/3, 7/5, 3/2, 8/5, 5/3, 7/4, 9/5, 2, 9/4, 7/3, 5/2, 8/3, 3, 7/2, 4, 9/2, 5, 6, 7, 8, 9

— 27 breakpoints cutting (1, ∞) into **28 open intervals**, and on each open interval the map is
literally the same map. (At a breakpoint itself the tie rule enters; those 27 measure-zero games are
a separate census, not run here.) So the single defector has at most 28 futures, for all time.

## Census (`census_futures.py`, `render_futures.py`, certificate `futures_2560_cert.json`)
One run per interval (at its midpoint), trajectories compared by the SHA-1 of every generation up to
T = 100 (and the counts by time up to T = 300 in `futures_T300.json`). **Ten distinct futures:**

| b-interval(s) | future |
|---|---|
| (1, 9/8) | the seed alone, fixed |
| (9/8, 7/5) | **breathing, period 2**: 9 → 1 → 9 … (the neighbours defect since 8b > 9, the block's corners then lose to the outer cooperators scoring 8 since 5b < 8, the block collapses to the seed and grows again) |
| (7/5, 8/5) | **breathing, period 3**: 9 → 5 → 1 → 9 … (the block loses its corners, then its edges, then regrows) |
| (8/5, 9/5) | the 3×3 block, frozen (corner 5b > 8 beats the adjacent cooperators, but 5b < 9 cannot beat a cooperator with a full house) |
| (9/5, 2) | the **evolutionary kaleidoscope**: defectors and cooperators both grow; chaotic bulk, D₄-symmetric forever, D-fraction 0.66 at T = 300 |
| (2, 9/4) | the **cross**: defection grows only along the two diagonals, 17.6 sites per generation (9, 193, 369, 537, … the count is affine in t after generation 10: exactly +176 per 10 generations) |
| (9/4, 7/3) | cooperator **islands** in a sea of defection (self-similar H-shaped islands); D-fraction 0.781 |
| (7/3, 8/3) | islands, differs from the previous only at generation ≥ ~80 near the frontier (counts 19,989 vs 20,013 at t = 80) |
| (8/3, 3) | islands, a third variant (differs from the second only in the hash; equal counts to t = 100) |
| (3, ∞) | defection takes everything: the (2t+1)² square |

The three island futures are honest distinct trajectories (different sets of comparisons become active
when b crosses 7/3 and 8/3) that the eye cannot separate at generation 120; the sheet draws them all
because the census is the piece.

**Threshold 9/5 = 1.8** is the famous Nowak–May threshold for the growth of a defector cluster with
self-interaction (a corner defector of a block scores 5b and must beat a cooperator with a full house
of 9), and **b = 2** is where a 2×2 cooperator cluster can no longer grow; both fall out of the fraction
list. The finiteness itself is elementary but I have not seen the complete list drawn.

## Small conjecture, played with
The count sequence of the cross future is affine, 9 + 176·(t/10 − 1) for t ≥ 10, i.e. the four
diagonal arms each add 4.4 sites per generation on average — a period-5 pattern along the arm (22 sites
per 5 generations per arm). Conjecture: every future of one defector with b ∉ (9/5, 2) is eventually
periodic up to the frontier translation (the kaleidoscope interval is the only one whose bulk is not
eventually periodic). Checking it would take a bulk-periodicity test on the counts of the three island
futures to T ≈ 1000, which the engine can do in minutes.
