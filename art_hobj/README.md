# WHICH KIND OF OBJECT IS A LAW — pastel #54

Four pictures about rules: a rule you must obey at every step, a rule that says where
everything ends up, and a rule that compresses a whole table into a few sheets.
The series title is a Philosophy.SE question
([143035, "Which kind of object is a law of nature?"](https://philosophy.stackexchange.com/q/143035));
the three mathematical objects come from the MathOverflow front page of the same day.

| file | size | what it is |
|---|---|---|
| `out/enter_by_one_half_4096.png` | 4096² | **Enter by One Half, Leave by the Other** — hero. A uniformly random domino tiling of the 20×20 board as candy bars, tied by one baker's-twine path that never splits a domino. |
| `out/the_twenty_3072.png` | 3072² | **The Twenty That Will Not Be Tied** — the 20 worst tilings of the 6×6 board (and the 2 worst of the 4×4), each with one longest string. |
| `out/six_ways_3072.png` | 3072² | **Six Ways to Arrive at One** — six uniformly random maps *f* on 300 points with *f*ᵏ constant, k = 1…6, as a bouquet of seed heads. |
| `out/four_sheets_3072.png` | 3072² | **Four Sheets Hold Two Hundred and Fifty-Six Facts** — the 16×16 XOR Latin square as four checkered tissue sheets plus a constant; below, the exact minimum rank for n = 2…7. |

## Six ideas, four made

1. **Domino-respecting paths** (MO 509392) — made, hero.
2. **The stubborn tilings**, an exhaustive census of worst cases — made, as the "go deeper" on the hero.
3. **Maps whose k-th iterate is constant** (MO 508368) as compound umbels — made.
4. **Low-rank Latin squares** (MO 515241) as stacked tissue — made.
5. The rigid half-torus (MO 77760) in glass — dropped; glass has had many turns already.
6. Equal values of a⁴ − a²b² + b⁴ (MO 516581) as a twelve-fold contour map — dropped; no picture in it yet.

## 1 · Enter by One Half, Leave by the Other

A path on the board is *domino-respecting* if, whenever it steps onto one half of a domino,
its next or previous step is the other half. MO 509392 asks how long such a path must exist.

**The observation that makes it computable.** Colour the board like a chessboard. A path enters
a domino on one colour and leaves from the other, and the step to the next domino flips colour
again, so *every* domino is left from the same colour. A domino-respecting path through a full
tiling is therefore exactly a directed simple path in the digraph

> D → D′ whenever the white cell of D touches the black cell of D′,

which has out-degree and in-degree at most 3. (This is the digraph in the accepted answer, which
proves Θ(n²) for full tilings via Chekuri–Ene–Pilipczuk.)

**Exact data** (`domino/census.c`, every tiling, exhaustive depth-first search with a
reachability bound):

| board | tilings | fewest dominoes on a longest path | how many tilings are that bad |
|---|---|---|---|
| 2×2 | 2 | 2 of 2 | 2 |
| 4×4 | 36 | 7 of 8 | 2 |
| 6×6 | 6 728 | 16 of 18 | 20 (1 850 lose one, 4 858 lose none) |
| 8×8 | 12 988 816 | see the note at the end | |

In all 22 extremal tilings for n ≤ 6 the dominoes left out touch the boundary of the board.

**Conjecture (mine, thin evidence).** The worst case loses only a boundary's worth:
n²/2 − L_min(n) = O(n), and the small cases fit n/2 − 1 exactly. If true, the Θ(n²) theorem
is far from tight in its constant: asymptotically *every* domino can be tied.

**The hero.** One uniform tiling of the 20×20 board (400 sweeps of random flips), and the longest
path a long annealing search found: 195 of 200 dominoes. The search (`domino/path.py`) keeps a
set of vertex-disjoint directed paths and anneals the number of paths downward, then inserts
leftover dominoes greedily. 195 is a lower bound for this tiling, not a proved optimum. Colour
is the order along the string; white bars are the five left out, and all five touch the edge.

Rendering (`domino/render.py`): a top-down relief. Each domino is a rounded-box signed distance
field turned into a pillow height map with a centre groove; the twine is a swept sphere along
the filleted lattice path, with a two-ply coral/white twist computed from arc length and lateral
offset; soft lavender shadows from shifted, blurred masks.

## 2 · Six Ways to Arrive at One

MO 508368 asks for g(n,k) = #{ f : [n] → [n] with fᵏ constant }. Such an f is a rooted labelled
tree of height ≤ k (the root is the fixed point), so with T₀ = x and T_k = x·exp(T_{k−1}),
g(n,k) = n!·[xⁿ] T_k. `trees/count.py` computes the table exactly; for n = 10:

`10, 2 936 080, 90 466 480, 354 648 160, 660 253 600, 872 387 200, 969 155 200, 996 371 200, 10⁹`

For k = 2 there is a closed sum, g(n,2) = n·Σ_j C(n−1, j)·j^(n−1−j), whose largest term sits at
j ≈ n/ln n; so log_n g(n,2) ≈ n·(1 − ln ln n / ln n), which gives 25.8 at n = 40 against the
exact 25.64. Half of all n^(n−1) trees are reached only near k ≈ 12 for n = 40.

The picture samples each tree *uniformly* with a Boltzmann sampler read straight off the
recursion (a height-≤k tree is a root with Poisson(T_{k−1}(x)) children of height ≤ k−1), rejecting
until the size is exactly 300 and the height exactly k. k = 1 is a dandelion clock; by k = 6 it
is Queen Anne's lace. Blossom colour is the number of steps from home; the coral bead is home.

## 3 · Four Sheets Hold Two Hundred and Fifty-Six Facts

MO 515241 asks for r(n), the least rank of an n×n Latin square on the symbols 1…n, and whether
it can stay bounded. The question's own example is L = 1 + (i XOR j), of rank 1 + log₂ n: bit b
of i XOR j is a checkerboard of block size 2ᵇ, so the 16×16 square is literally
8·▦ + 4·▦ + 2·▦ + 1·▦ + 1. The picture is that sentence.

**Exact data** (`latin/rank.c`). Rank is unchanged by permuting rows or columns, so it is enough
to check *reduced* squares, and for n = 7 that is 16 942 080 of them:

| n | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|
| r(n) | 2 | 3 | 3 | **5** | 4 | **6** |
| reduced squares at the minimum | 1 of 1 | 1 of 1 | 2 of 4 | 56 of 56 | 158 of 9 408 | 67 284 of 16 942 080 |

So r is **not monotone**: every 5×5 Latin square is invertible, yet r(6) = 4. (Ranks were computed
mod 10⁹+7; a 7×7 determinant with entries ≤ 7 is below that prime by Hadamard's bound, so "singular
mod p" means singular, and the extremal examples were re-checked in exact rationals.)

**Lemma (easy).** r(mn) ≤ r(m) + r(n) − 1. Take L[(i,i′),(j,j′)] = m′·(A[i,j] − 1) + B[i′,j′];
its column space lies in col(A)⊗1 + 1⊗col(B), and the all-ones vector is in both because Latin
squares have constant row sums. This gives r(4) ≤ 3, r(6) ≤ 4, r(8) ≤ 4, all sharp, and
r(2ᵏ) ≤ k + 1 again.

**Question I could not settle.** Is r(9) = 4 or 5? (The thread's lower bound gives ≥ 4, the lemma
gives ≤ 5.) `latin/anneal_rank.py` anneals over Latin squares with cycle switches, minimising the
tail of the singular values. It rediscovers rank 4 at n = 6 and n = 8 in seconds, but it does not
even find the known rank-5 square at n = 9, so its silence there means nothing.
**Guess, labelled as such:** r − 1 is additive over the best factorisation and r(p) ≥ p − 1 for
odd primes p (true for 3, 5, 7), which would make the XOR squares optimal and r unbounded.

## Tweet

> A string was told one rule: if you touch half of a thing, you must take the whole.
> It crossed a board of two hundred sweets and came back with a hundred and ninety-five.
> The five it missed were all standing with their backs to the wall.

## Reproduce

```
cd domino && gcc -O2 -o census census.c && ./census 6 > min6.bin && ./census 4 > min4.bin
python3 path.py 20 2 4e8 6 3000          # long search; writes path_20_2_3000.npz
python3 render.py path_20_2_3000.npz 4096 ../out/enter_by_one_half_4096.png 0.92 0.0
python3 stubborn.py 3072 ../out/the_twenty_3072.png
cd ../trees && python3 count.py && python3 bouquet.py 3072 300 7 ../out/six_ways_3072.png
cd ../latin && gcc -O2 -o rank rank.c && for n in 2 3 4 5 6 7; do ./rank $n > low$n.txt; done
python3 sheets.py 3072 ../out/four_sheets_3072.png
```
