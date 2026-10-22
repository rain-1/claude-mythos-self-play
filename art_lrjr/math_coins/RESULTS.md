# Incremental cyclic Latin squares (MathOverflow 516225)

## Convention (checked against the OP's n=5 example)
L[i][j] = (i + q(j)) mod n, values **0..n-1**. Incremental means that for every k in 0..n-1, every
ordinary (non-wrapping) diagonal i+j=const and i-j=const has **at most k+1 cells with L <= k**.
For each c the cells with L <= c-1 then form an (n,c)-coins placement.
The example q = (0,3,1,4,2) = 3j mod 5 satisfies this. The stricter reading "at most k cells with L <= k",
0-based, already fails at k=0, so that reading is wrong. The 1-based form "at most k cells with
1 <= L <= k" is the same condition.

## 1. Cyclic squares: exhaustive counts (cyclic.c; outputs in sols_n.txt)
| n | #q valid | linear | toroidal (= valid for all shifts q+b) | non-toroidal | up to symmetry (=#/2) |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 1 | 0 | 1 |
| 2,3,4 | 0 | 0 | 0 | 0 | 0 |
| 5 | 10 | 10 | 10 | 0 | 5 |
| 6 | 0 | 0 | 0 | 0 | 0 |
| 7 | 30 | 28 | 28 | 2 | 15 |
| 8 | 10 | 0 | 0 | 10 | 5 |
| 9 | 38 | 0 | 0 | 38 | 19 |
| 10 | 78 | 0 | 0 | 78 | 39 |
| 11 | 142 | 88 | 88 | 54 | 71 |
| 12 | 1116 | 0 | 0 | 1116 | 558 |
| 13 | 5808 | 130 | 4524 | 1284 | 2904 |
| 14 | 22300 | 0 | 0 | 22300 | 11150 |
| 15 | 31666 | 0 | 0 | 31666 | 15833 |
| 16 | 643466 | 0 | 0 | 643466 | 321733 |

Runtimes: n=14 took 11 s, n=15 took 69 s and n=16 took 506 s, on one core. The n=17 count was stopped: it
would take about 1 h. Only the q(0)=0 branch finished, with 66761 solutions (about 3.5 min per branch),
so the full n=17 count is roughly 10^6. `python3 verify.py --brute 5` re-derives n=5 by
brute force. The general counter (below), run without the symmetry reduction, also finds exactly 10
row-cyclic squares at n=5. For n=7 the 2 non-toroidal solutions are (4,1,3,6,2,0,5) and (5,0,2,6,3,1,4).

**Symmetries (proved, and confirmed by computation for n<=13).** The dihedral group preserves
"incremental", but the only elements that keep a square cyclic are the identity and column
reversal q(j) -> q(n-1-j). Row reversal turns +i into -i. Transpose and the other elements would
need q(j)=j+c, which is never valid. Column reversal never fixes a permutation when n>1, so the
number of classes is exactly half the count. Cyclic relabelling L -> L+b (the same as q -> q+b, a
cyclic row shift) is **not** a symmetry in general. Exactly the toroidal solutions are closed under it.

**Theorem (proved).** q is valid for *every* shift q+b if and only if the 0-layer r(j) = -q(j) mod n
is a toroidal (modular) n-queens solution.
- If r is toroidal, every layer L=k is a vertical cyclic shift of r and so is also toroidal. Each
  diagonal then holds at most one cell of each value, which gives at most k+1 cells with value <= k.
- Conversely, a wrapped diagonal conflict in r becomes an ordinary conflict in the 0-layer of a
  suitable shift q+b.

The "toroidal" column therefore equals the number of toroidal n-queens solutions, OEIS A007705
(1,0,0,0,10,0,28,0,0,0,88,0,4524,0,0,0,140692...). Every value class being an ordinary queens
solution turns out to be the same condition as being toroidal.

**Linear q(j)=aj+b (linear.c, checked for all n<=60, all a with gcd(a,n)=1 and all b).** q is
valid **iff gcd(a(a-1)(a+1), n) = 1**, and when that holds it is valid for all n values of b. So
linear solutions exist iff gcd(n,6)=1, and there are n·#{a : a, a±1 units mod n} of them, which is
p-3 times p for a prime p. The "if" direction follows from the theorem. The "only if" direction is
verified for n<=60 but not proved. The example q=2j works for all n coprime to 6.
**Linear solutions do not dominate the counts.** Already at n=13 they are 130 of 5808 (2%). For n
divisible by 2 or 3 every solution is non-linear and non-toroidal. Those solutions use the extra
room the incremental condition allows: a diagonal may hold two 1s if it has no 0.

## 2. All incremental Latin squares, cyclic or not (general.c, general_sym.c)
The squares are built layer by layer, each value class as a permutation matrix, with cumulative
diagonal counters. For n=7, layer 0 is reduced by D4 and each case is weighted by its orbit size.
| n | incremental Latin squares | D4 classes | row-cyclic among them |
|---|---|---|---|
| 1 | 1 | 1 | 1 |
| 2, 3 | 0 | 0 | 0 |
| 4 | **16** | 3 | **0** |
| 5 | 416 | 52 | 10 |
| 6 | **28268** | 3605 | **0** |
| 7 | 118442032 (26 s) | — | 30 |

This **confirms the OP**: n=4 and n=6 have incremental Latin squares but no cyclic ones. The 3
classes for n=4 are (rows) 1023/2310/0132/3201, 1023/3210/0132/2301 and 2013/1320/0231/3102.
Lists are in gen_n.txt. n=8 looks out of reach with this method: the count grew about 4000-fold
from n=6 to n=7.

## 3. Explicit squares: squares.json (check with `python3 verify.py`, which prints ALL OK)
For n = 11, 12, 13 and 17 the file gives:
- a linear q=2j, where gcd(n,6)=1;
- a toroidal but non-linear q, for 13 and 17 (at n=11 all 88 toroidal solutions are linear);
- one or two non-toroidal q, for all four values.

It also gives one solution for each n in {1, 5, 7..40}. verify.py checks each q independently: q is a
permutation, and for every c every row and column has exactly c coins and every diagonal at most c.
It also labels each q as linear, toroidal-nonlinear or non-toroidal. Random-order backtracking
(find.c) finds a solution for each n<=40 in under 20 s.

## 4. Conjectures (evidence only)
- **C1 (agrees with the OP's claim).** Cyclic incremental squares exist for every n except 2, 3, 4
  and 6. Evidence: no solutions at 2, 3, 4 and 6 from exhaustive search; a solution for every other
  n<=40 (verified).
- **C2.** Linear q works iff gcd(a(a²-1), n)=1. Verified for n<=60; the "if" direction is proved.
- **C3.** The count is dominated by non-toroidal solutions as n grows. Toroidal/total is 1, 0.93, 0.62
  and 0.78 for n=5, 7, 11 and 13, and toroidal solutions are completely absent when gcd(n,6)>1.
  Counts grow roughly 4-30x per step but unevenly: 15 -> 16 jumps 20x, while 14 -> 15 grows only
  1.4x. This suggests odd multiples of 3 are the hardest case.
- Neither 10,0,30,10,38,78,142,1116 (cyclic) nor 16,416,28268 (all incremental) is in the OEIS.
  Both look like new sequences. The toroidal part is A007705.

## Files
cyclic.c (exhaustive counter) · cyclic_prog.c (the same counter with progress output, used for
n=17) · find.c (randomized search for solutions) · linear.c · general.c / general_sym.c (non-cyclic
squares) · analyze.py, strong.py, extra.py (symmetry, toroidal and shift analysis) · make_json.py ·
verify.py · sols_n.txt, gen_n.txt (raw lists).
