# Directed Hamiltonian double covers of the hypercube (MO 208368)

D_d = Q_d with every edge replaced by two opposite arcs (d·2^d arcs).
Question: can the arcs be partitioned into d directed Hamiltonian cycles?
Vertices are integers, bit i = coordinate i; arc (v,i) means v -> v xor 2^i.
A "transition sequence" lists the coordinates flipped along a cycle.

**Answer (literature + our computations): yes for every d except d = 3.**

## Summary table

| d | status | source |
|---|--------|--------|
| 1 | trivial (the digon) | - |
| 2 | 1 decomposition | computed |
| 3 | impossible | PROVED below (also MO answer by "The Masked Avenger") |
| 4 | exactly 3312 decompositions, 34 orbits under Aut(Q4), 25 under Aut(Q4) x reversal | COMPUTED (exhaustive) |
| 5 | exists; exactly 96 are invariant under the cyclic coordinate shift | COMPUTED, verified |
| 6-10 | explicit shift-invariant decompositions | COMPUTED, verified |
| even d | trivial from undirected Hamilton decompositions | PROVED (given Aubert-Schneider / ABS) |
| all d != 3 | exists | FROM LITERATURE (Stong 2006) |

---------------------------------------------------------------------

## 1. d = 4: classification of the 3312 decompositions  [COMPUTED, `d4_orbits.py`]

Exhaustive: 2688 directed Hamiltonian cycles, 3312 decompositions (unordered 4-sets).

**Orbits under Aut(Q4) (order 384):** 34 orbits.

| orbit size | stabiliser | number of orbits |
|---|---|---|
| 24 | 16 | 4 |
| 48 | 8 | 7 |
| 96 | 4 | 16 |
| 192 | 2 | 7 |

(4·24 + 7·48 + 16·96 + 7·192 = 3312.) No decomposition has trivial stabiliser.

**Orbits under Aut(Q4) x <reverse all four cycles> (order 768):** 25 orbits.

| orbit size | stabiliser | number of orbits |
|---|---|---|
| 24 | 32 | 2 |
| 48 | 16 | 6 |
| 96 | 8 | 7 |
| 192 | 4 | 8 |
| 384 | 2 | 2 |

9 of the 25 are "chiral" (a union of two Aut(Q4)-orbits swapped by reversal); 16 are equivalent
to their own reversal under some automorphism.

**Per-orbit table** (orbit numbering as in `solutions.json` / `d4_orbits.json`; "type" = transition
sequence up to rotation, reflection and relabelling of coordinates; "counts" = how often each
cycle uses coordinates 0..3):

| # | size | Aut-orbits inside | stab Aut | stab Aut x rev | paired | cyclic-4 | antipodal fixes each cycle | type(s) | counts per cycle |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 192 | 96+96 | 4 | 4 | | | | A | 6442,4624,2446,4264 |
| 1 | 384 | 192+192 | 2 | 2 | | | | A | 6442,2446,6442,2446 |
| 2 | 192 | 192 | 2 | 4 | | | | A | 6442,2446,6442,2446 |
| 3 | 192 | 192 | 2 | 4 | yes | | | A | 6442,2446,2446,6442 |
| 4 | 384 | 192+192 | 2 | 2 | | | | B,B,C,C | 6442,4624,2464,4246 |
| 5 | 192 | 96+96 | 4 | 4 | | | | B | 6442,4624,4264,2446 |
| 6 | 192 | 96+96 | 4 | 4 | | **yes** | | B | 6442,4624,4264,2446 |
| 7 | 96 | 96 | 4 | 8 | | | | B | 6442,6442,2446,2446 |
| 8 | 48 | 48 | 8 | 16 | | | | B | 6442,6442,2446,2446 |
| 9 | 48 | 48 | 8 | 16 | | | | B | 6442,2446,6442,2446 |
| 10 | 48 | 48 | 8 | 16 | | | | B | 6442,6442,2446,2446 |
| 11 | 96 | 96 | 4 | 8 | | | | B | 6442,2446,6442,2446 |
| 12 | 48 | 48 | 8 | 16 | yes | | | B | 6442,2446,6442,2446 |
| 13 | 192 | 96+96 | 4 | 4 | | | | C | 6424,4642,2464,4246 |
| 14 | 96 | 96 | 4 | 8 | | | | D | 4444 x4 |
| 15 | 192 | 192 | 2 | 4 | | | | D | 4444 x4 |
| 16 | 96 | 96 | 4 | 8 | yes | | | D | 4444 x4 |
| 17 | 48 | 24+24 | 16 | 16 | | | yes | E | 6622,6622,2266,2266 |
| 18 | 48 | 48 | 8 | 16 | | only with reversal | yes | E | 6622,6262,2626,2266 |
| 19 | 24 | 24 | 16 | 32 | | (order-8, see below) | yes | E | 6622,6622,2266,2266 |
| 20 | 24 | 24 | 16 | 32 | yes | (order-8, see below) | yes | E | 6622,2266,2266,6622 |
| 21 | 96 | 96 | 4 | 8 | | | | F | 6442,6442,2446,2446 |
| 22 | 192 | 96+96 | 4 | 4 | | | | F | 6442,6442,2446,2446 |
| 23 | 96 | 48+48 | 8 | 8 | | **yes** | | F | 6442,2446,4264,4624 |
| 24 | 96 | 96 | 4 | 8 | yes | | | F | 6442,2446,2446,6442 |

Transition types: A = 0102010302120213, B = 0102013201020132, C = 0102030130321013,
D = 0102032123031213 (balanced, each coordinate 4 times), E = 0102101301021013
(antipodally symmetric), F = 0102101302012023.
Q4 has 9 types of Hamiltonian cycle (class sizes 768, 384, 384, 384, 192, 192, 192, 96, 96 directed
cycles); only these 6 occur in decompositions. The three that never occur are
0102010301020103 (the reflected Gray code), 0102010310121013 and 0102013102010232.
Full transition sequences of every cycle of every representative are in `solutions.json`.

**Cyclic symmetry of order 4 on the cycles.**
- An automorphism of Q4 permuting the four cycles in a single 4-cycle exists exactly for orbits
  6 and 23: 192 + 96 = **288 decompositions**. In all cases the automorphism has order 4 and is
  conjugate in Aut(Q4) to the pure cyclic coordinate shift rho: x_i -> x_{i+1}. Exactly
  **12 decompositions are invariant under rho itself** (cross-checked independently by
  `ansatz_count.c`: 48 generating cycles = 12 x 4).
- Orbit 18 (48 decompositions) has such a cyclic permutation only in the form
  (order-4 automorphism) o (reversal).

**The order-8 map s:(x1,x2,x3,x4) -> (x2,x3,x4,1-x1).** Aut(Q4) has 48 elements of order 8, all
conjugate to s (vertex cycle type 8+8).
- Decompositions invariant under some conjugate of s: exactly orbits 19 and 20, i.e. **48
  decompositions**, each invariant under 4 order-8 elements; hence exactly **4 decompositions are
  invariant under s itself** (192 incidences / 48 conjugates).
- In every case s acts on the four cycles as a product of two transpositions, **never as a
  4-cycle**. So s^2 (order 4) and the antipodal map s^4 fix each of the four cycles.
  There is no decomposition of the form {C, sC, s^2C, s^3C}.
- Orbit 20 is of paired type (two cycles and their reverses); orbit 19 is not.
  These two are the most symmetric decompositions (stabiliser 16 in Aut(Q4), 32 with reversal).
- Each cycle is individually fixed by the antipodal map exactly in orbits 17-20 (144 decompositions;
  type E). No cycle in any decomposition is mapped to its own reverse by the antipodal map.

**Paired vs unpaired.** 456 of the 3312 decompositions are of the trivial "cycle and its reverse"
type {C1, C1^-1, C2, C2^-1} (orbits 3, 12, 16, 20, 24: 192+48+96+24+96); these correspond
bijectively to the 456 undirected Hamiltonian decompositions of Q4 found this way.
**2856 are genuinely unpaired** (contain no cycle together with its reverse). A decomposition with
exactly one reverse pair is impossible (the remaining edges form a 2-regular graph, so the other two
cycles are forced to be a reverse pair too).

---------------------------------------------------------------------

## 2. d = 3 is impossible

### PROVED (human-checkable)

*Lemma 1.* Every Hamiltonian cycle of Q3 has transition sequence a b a c a b a c with
{a,b,c} = {0,1,2}. Call a its *dominant* direction.
Proof: each coordinate is flipped an even number >= 2 of times and the total is 8, so the counts are
(4,2,2). The same coordinate is never flipped twice in a row, so the dominant coordinate a occupies
alternate positions. The other four positions hold b,b,c,c in cyclic order b,b,c,c or b,c,b,c; the
first gives the subword a b a b, which is a closed walk of length 4 - impossible. QED

*Lemma 2.* A Hamiltonian cycle with dominant direction a uses all four a-edges, and its two
b-edges are exactly the two b-edges lying in one facet x_a = const (they differ in coordinate c).
Proof: if the first b-step is u -> u+e_b, the following steps a, c, a lead to u+e_b+e_c, so the second
b-step is u+e_b+e_c -> u+e_c. Both b-edges have the a-coordinate of u. QED

*Theorem.* Q3 has no three Hamiltonian cycles covering every edge exactly twice. In particular D_3
has no decomposition into 3 directed Hamiltonian cycles.
Proof: each direction has 4 edges, hence must be used 8 times in total; each cycle uses a
direction 2 or 4 times, and 8 = 4+2+2 is the only possibility, so the three cycles C_0, C_1, C_2 have
distinct dominant directions 0, 1, 2. Look at the four 0-edges, indexed by (x1,x2) in {0,1}^2. C_0
uses each of them once, so C_1 and C_2 together must use each of them exactly once. By Lemma 2, C_1
uses a "row" {(s,0),(s,1)} (same x1) and C_2 uses a "column" {(0,t),(1,t)} (same x2). A row and a
column share the edge (s,t), which is then used three times, while (1-s,1-t) is used once. QED

Note the proof never uses orientations: even the *undirected* statement (3 Hamiltonian cycles, every
edge twice) fails. (The proof on MathOverflow by "The Masked Avenger" is different: a 2-colouring of
vertices by the rotational sense of the local 3-cycle of transitions, analysed face by face.)

### COMPUTED (`d3.py`)
- 12 directed Hamiltonian cycles (6 undirected); 0 triples; 0 undirected double covers by 3
  Hamiltonian cycles (multisets allowed) - confirms the theorem.
- **Maximum number of pairwise arc-disjoint directed Hamiltonian cycles = 2.** There are exactly
  12 such pairs, in 2 orbits (of 6 each) under Aut(Q3) x reversal:
  1. **Reverse pair** {C, C^-1}. Leftover 8 arcs = the 4 edges not on C (a perfect matching), each
     in both directions: **four digons** (directed 2-cycles).
     Example: C = 0,1,3,2,6,7,5,4; leftover digons 0<->2, 1<->5, 3<->7, 4<->6.
  2. **Two cycles with the same dominant direction a**, oriented so that they traverse the four
     a-edges in opposite directions (they share exactly those 4 edges). Leftover 8 arcs =
     **two directed 4-cycles**, one around each facet x_a = 0 and x_a = 1, parallel translates of each
     other with the same sense of rotation.
     Example: 0,1,3,2,6,7,5,4 and 0,2,3,7,6,4,5,1; leftover 0->4->6->2->0 and 1->5->7->3->1.
  The leftover is never a single closed 8-walk and never a Hamiltonian cycle.

---------------------------------------------------------------------

## 3. d >= 5: explicit decompositions via a cyclic-shift ansatz  [COMPUTED, verified]

**Ansatz.** Let rho be the cyclic coordinate shift (bit i -> bit i+1 mod d). Look for ONE directed
Hamiltonian cycle C such that C, rho C, ..., rho^(d-1) C are pairwise arc-disjoint (then they
partition all d·2^d arcs). rho maps arc (v,i) to (rho v, i+1) and so acts freely on arcs, with 2^d
orbits, labelled by rho^(-i)(v). Hence:

> C works iff the map (v,i) -> rho^(-i)(v), restricted to the 2^d arcs of C, is a bijection onto the
> vertex set.   [PROVED - immediate]

`ansatz_sat.py` solves this with SAT (out-degree 1, in-degree 1, one arc per label, lazy subtour cuts).

| d | result | time |
|---|---|---|
| 2 | found | 0 s |
| 3 | UNSAT (consistent with section 2) | 0 s |
| 4 | found; exhaustive count 48 cycles C = 12 decompositions | 0 s |
| 5 | found; **exhaustive count 480 cycles C = 96 decompositions** | 0 s |
| 6, 7, 8 | found | < 0.1 s each |
| 9 | found | 1.2 s |
| 10 | found (CaDiCaL, 1000 rounds of subtour cuts) | 192 s |
| 11 | INCONCLUSIVE: search stopped after ~20 min / 550 cut rounds (2048 vertices; the lazy-cut SAT loop is just slow here, no evidence of infeasibility) | - |

All decompositions for d = 5,...,10 are stored in `solutions.json` and pass the independent checker
`verify.py` (checks each list is a permutation of the vertices, consecutive vertices adjacent in Q_d,
and that the d·2^d arcs are all distinct).

Example d = 5 (apply the 5 cyclic bit-rotations to get the 5 cycles):
`C = 0 2 18 26 27 19 23 21 29 31 15 13 5 7 6 22 20 4 12 28 30 14 10 8 9 11 3 1 17 25 24 16`

**All shift-invariant solutions for d = 5** (`ansatz_count.c`, `d5_classify.py`): exactly 96
decompositions {C, rho C, ..., rho^4 C}. Under the normaliser of <rho> in Aut(Q5) (coordinate maps
i -> a·i+b, and complementing all bits; order 40) together with reversal (order 80) they form
**6 orbits of size 16**, each with stabiliser exactly <rho> (order 5). None contains a reverse pair,
and none has cycles fixed (or reversed) by the antipodal map. The six generating cycles are in
`solutions.json` under `d5_all_shift_invariant_orbit_reps` (coordinate-usage counts of C:
(10,8,8,2,4), (8,10,8,4,2), (6,14,6,4,2), (8,8,6,4,6), (8,8,4,8,4), (6,8,4,6,8)).

---------------------------------------------------------------------

## 4. General structure

**Even d is trivial [PROVED, given the literature].** If Q_{2k} has an (undirected) Hamiltonian
decomposition into k Hamiltonian cycles H_1..H_k, then orienting each H_j both ways gives 2k directed
Hamiltonian cycles using each arc exactly once. Such decompositions exist for all k >= 1 (Ringel for
d a power of 2; Aubert-Schneider 1982 / Alspach-Bermond-Sotteau 1990 for all even d). So the checked
observation is correct: **for even d the problem is solved trivially**, and this was already pointed
out in the MO answer by j.c. The interesting cases are odd d; for even d the interesting refinement is
*unpaired* decompositions. For d = 4: 456 paired, 2856 unpaired (section 1). All shift-invariant
decompositions found for d = 6, 8, 10 are unpaired as well (rho-invariant with rho acting as a d-cycle; a
reverse pair C, rho^j C = C^-1 would force 2j = 0 mod d, possible only for j = d/2 - not excluded a
priori, but did not occur in the solutions found).

**Odd d.** d = 3 is impossible (section 2). For odd d >= 5 existence is Stong's theorem (section 5);
our computations give explicit, very symmetric examples for d = 5, 7, 9 (and even d = 6, 8, 10).

**Necessary counting condition [PROVED - trivial].** In any decomposition, each direction i is used
2^d times in total, and each cycle uses each direction a positive even number of times. For d = 3
this forces the (4,2,2) pattern that kills d = 3; for d >= 4 it is no obstruction.

**CONJECTURE (cyclic ansatz).** For every d >= 2 with d != 3 there is a directed Hamiltonian cycle C
of Q_d whose d images under the cyclic coordinate shift are pairwise arc-disjoint, i.e. D_d has a
Hamiltonian decomposition on which Z_d (coordinate rotation) acts regularly on the cycles.
*Evidence:* found for d = 2, 4, 5, 6, 7, 8, 9, 10 (SAT finds them instantly, suggesting they are
plentiful: 1, 12, 96 such decompositions for d = 2, 4, 5). Not proved; we did not find this statement
in the literature (Stong's paper was not accessible to us in full text, so it may or may not use a
similar symmetry).

**Remark (d = 4, order-8 twist).** The analogous ansatz with the twisted shift s (order 8, x_4 ->
1 - x_1) FAILS for d = 4: s never permutes the cycles of a decomposition cyclically (section 1).

We did not find a new short general construction for odd d within the time budget.

---------------------------------------------------------------------

## 5. FROM LITERATURE (web search; statements as found, with how they were verified)

- **MathOverflow 208368**, "Can we find 3 disjoint directed Hamiltonian cycles in the cube?", asked
  by domotorp, 3 June 2015 (read via the public Stack Exchange API). Content of the thread:
  - Accepted answer by "The Masked Avenger" (2015): sketch that d = 3 is impossible (colour each vertex
    by clockwise/counter-clockwise sense; every face needs two adjacent vertices of each colour;
    contradiction on three mutually adjacent faces).
  - Answer by j.c. (2015): cites Alspach, Bermond, Sotteau, "Decompositions into cycles I: Hamilton
    decompositions" (1990), Proposition 1: the n-cube has a Hamilton decomposition for all n (for odd
    n: Hamiltonian cycles plus a perfect matching); the even case uses Q_{2m} = C_4 x ... x C_4 and a
    corollary of a theorem of Aubert and Schneider. Notes that this answers the question positively
    for even d.
  - Answer by domotorp himself (timestamp November 2026): the question "was essentially known":
    a decomposition exists precisely when d != 3; odd d >= 5 was settled by Stong (below).
- **R. Stong, "Hamilton decompositions of directed cubes and products", Discrete Mathematics 306
  (2006), no. 18, 2186-2204** (DOI 10.1016/j.disc.2005.09.021). We could NOT access the paper
  itself. The statement is taken from N. C. Behague, "Semi-perfect 1-factorizations of the
  hypercube" (arXiv:1811.06389; Discrete Math. 2019), whose Theorem 3 attributes to Stong: *for
  d != 3 the symmetric directed hypercube can be partitioned into d directed Hamilton cycles*. We read
  this in Behague's text directly (bibliography entry [Sto06] as above). Our computations agree for
  d = 2,...,10.
- **Even hypercubes (undirected):** Ringel (1954/55; year differs between sources) for d a power of
  2; Aubert and Schneider (1982) and Alspach-Bermond-Sotteau (in "Cycles and Rays", Kluwer 1990, pp.
  9-18) for all even d. (From secondary sources: arXiv:2004.02750, arXiv:1905.10114 and the MO
  answer; primary papers not read.)
- **Stong, "Hamilton decompositions of Cartesian products of graphs", Discrete Math. 90 (1991)** -
  cited (arXiv:2412.13392) for product results on Hamilton-decomposable graphs. Not read.
- **Bermond, Darrot, Delmas, Perennes, "Hamilton circuits in the directed wrapped butterfly
  network"** (Discrete Appl. Math., 1998; HAL hal-00407356). Only abstracts seen: the directed wrapped
  butterfly of degree d contains at least d-1 arc-disjoint Hamilton circuits; conjectured to decompose
  into d Hamilton circuits except (d,n) = (2,2), (2,3), (3,2); verified by computer for primes up to
  12000 in a reduced form. This concerns butterfly digraphs, not D_d; no direct statement about the
  hypercube was found there.
- Not found / unsure: any published count of the 3312 decompositions for d = 4, or the cyclic-shift
  ansatz above.

---------------------------------------------------------------------

## Files

- `q.py` - original exhaustive enumeration (d <= 4).
- `d4_orbits.py` -> `d4_orbits.log`, `d4_orbits.json` - section 1.
- `d3.py` -> `d3.log` - section 2.  `d4_checks.py` - independent cross-checks (456 undirected
  decompositions of Q4; exactly 4 decompositions invariant under s, with s acting as two swaps).
- `ansatz_sat.py` (needs `python-sat`; `SOLVER=cadical` selects CaDiCaL instead of Glucose; logs in
  `ansatz_big.log`, `ansatz_d10_cadical.log`) -> `ansatz_d{N}.json`; `ansatz_count.c` (exhaustive count,
  d <= 5; `./ansatz_count 5 all` lists all 480 cycles -> `ansatz_d5_all.txt`); `d5_classify.py`
  -> `d5_ansatz_orbits.json`.
- `verify.py` - independent checker (`python3 verify.py solutions.json`).
- `build_solutions.py` -> `solutions.json`.

---------------------------------------------------------------------

## Addendum: d = 11 FOUND  [COMPUTED, verified]

The d = 11 run that was stopped here was repeated by the repository owner on a home computer with
`ansatz_sat.py 11` and returned a generating cycle C (`d11_C.txt`). Independently checked: C is a
permutation of the 2048 vertices, consecutive vertices are adjacent in Q_11, and the 11 cyclic
coordinate shifts of C use 22,528 distinct arcs, i.e. all of them. No cycle is the reverse of
another. The 11 cycles are in `ansatz_d11.json`. The cyclic-ansatz conjecture now has evidence for
d = 2, 4, 5, 6, 7, 8, 9, 10, 11.
