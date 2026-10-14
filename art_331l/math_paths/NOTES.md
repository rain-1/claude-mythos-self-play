# Largest number of simple paths between two vertices (MO 371851)

G simple undirected, f(u,v) = # simple u–v paths, f(G) = max_{u≠v} f(u,v).

## Headline

**THEOREM (PROVED, computer-assisted for finitely many cases).**
The set of values of f(G) over all finite simple graphs is exactly {0, 1, 2} ∪ {k : k ≥ 4}.
So **3 is the only positive integer that is not achieved.**

- "3 is impossible" has a short hand proof (§2).
- "every k ≥ 20 is achieved" comes from five explicit one-parameter families f = 5a + r, r = 0..4 (§3).
  The fact that each family satisfies the formula for *all* a ≥ 4 is proved by an affinity lemma (hand proof)
  plus a finite exact check of finitely many affine functions (`verify_families.py`).
- "every 4 ≤ k ≤ 19 is achieved" is in the exhaustive census (§1). (The census actually covers 4..11054 with ≤ 10 vertices.)

## 1. Exhaustive census (nauty geng + C path counter)

- `fpaths.c` / `fpaths2.c`: reads graph6, one DFS from every vertex u counts simple paths from u to every v
  simultaneously (bitmask DFS). `fpaths2` breaks ties among min-edge witnesses by smallest Σdeg² (more "even" pictures).
- Exhaustive over all connected graphs (`nauty-geng -c n`): n ≤ 9 (261,080 graphs at n=9, ~6 s) and n = 10
  (11,716,571 graphs; see §1b).
- Restricting to connected graphs is harmless: the max pair lies in one component, and a minimal-vertex witness is connected.

Results (n ≤ 9, exhaustive, PROVED by enumeration):

| largest n used | all of 4..K achieved | first k needing this n |
|---|---|---|
| n ≤ 7 | 4..44 | — (k=45 needs 8) |
| n ≤ 8 | 4..230 | 45 |
| n ≤ 9 | 4..1523 | 231 |
| n ≤ 10 | 4..11054 | 1524 |

Number of distinct values k ≥ 1 per exact minimum n: n=2:1 (k=1), 3:1 (k=2), 4:2 (4,5), 5:6, 6:21, 7:83, 8:406, 9:2380.
Max f with n vertices: f(K_n) = Σ_{j=0}^{n-2} (n-2)!/j!  (K9: 13700).

### 1b. n = 10 (exhaustive, 11,716,571 connected graphs, ~20 min on 2 cores)
- All of **4..11054** are achieved with ≤ 10 vertices; **11055 is the first k needing ≥ 11 vertices** (so n_min(11055) ≥ 11, proved by exhaustion; it is achieved by the §3 family).
- 16,610 further values first appear at n = 10 (first: k = 1524). Max with 10 vertices: f(K10) = 109601.
- n = 10 witnesses are min-edge but without the Σdeg² tie-break (first found by geng order).
- The only k ≤ 11054 not achieved by any graph on ≤ 10 vertices is k = 3.

Files:
- `census.json` — for every k achieved with ≤ 10 vertices (19,510 values; compact JSON, 5.8 MB; `census_k_le_200.json` is an indented subset): minimal n, minimal m (among n-vertex graphs),
  witness edge list (0-based), graph6, the maximising pair, degrees, and for k ≤ 60 **all k paths** (sorted by length).
  Every entry has f(u,v)=k re-verified with networkx; for k ≤ 60 maximality over all pairs is re-verified too.
- `census_table.tsv` — compact table. `census_n*.txt`, `census2_n*.txt` — raw per-n output `k m u v graph6`.

## 2. Why 3 is impossible (PROVED, hand proof)

**Lemma A (blocks multiply).** If u,v lie in different blocks, every u–v path passes through the same sequence of
cut vertices c_1,…,c_r, and the segment between consecutive ones lies in one block B_i of the block path.
Hence f(u,v) = Π_i f_{B_i}(c_{i-1}, c_i)  (c_0=u, c_{r+1}=v).

**Lemma B.** If a block B is 2-connected and not a cycle, f(B) ≥ 4.
*Proof.* B is a cycle plus at least one ear (ear decomposition), so B contains a theta subgraph Θ: three internally
disjoint a–b paths P1,P2,P3. In a simple graph at most one of them is the edge ab, so two of them, say P1,P2,
have interior vertices x ∈ P1, y ∈ P2. In Θ the x–y paths are: x→a along P1 then a→y along P2; x→a, a→b along P3,
b→y along P2; and the two symmetric ones starting x→b. That is 4 distinct paths, all simple paths of B. ∎
(Brute-force check: every 2-connected non-cycle graph with 4 ≤ n ≤ 9 has f ≥ 4, minimum exactly 4.)

**Theorem.** f(G) ≠ 3. *Proof.* If some block is 2-connected and not a cycle, f(G) ≥ 4 by Lemma B.
Otherwise every block is K2 (contributes factor 1) or a cycle (any two of its vertices have exactly 2 paths), so by
Lemma A every f(u,v) is a power of 2. ∎
(Corollary: f(G) ≤ 2 ⇒ G's blocks are edges/cycles with ≤ one cycle on any block path; f = 2^j for cacti.)

## 3. Every k ≥ 4 is achieved (PROVED, computer-assisted)

**Even k (pure hand proof).** K_{2,a} (hubs u,v, middles m_1..m_a): f(u,v)=a, f(u,m)=a, and for two middles x,y:
x-u-y, x-v-y, x-u-z-v-y, x-v-z-u-y (z any of a−2 others) ⇒ 2+2(a−2)=2a−2. So f(K_{2,a}) = 2a−2 (a ≥ 2):
**every even k ≥ 2**.  (2-connected "theta" graphs always give even values: for x,y on different branches the
paths pair up by swapping the roles of the two hubs.)

**General family.** G_H(a) = gadget H (containing hubs u,v) + a middle vertices each adjacent exactly to u and v.

*Affinity lemma (hand proof).* A middle vertex interior to a path is entered from one hub and left to the other; u,v
occur at most once, so a path has ≤ 1 interior middle. Therefore for each pair *type* (both ends in H; one end in H and
one middle; two middles) the number of paths is exactly c0 + c1·a (paths with no interior middle don't depend on a; each
admissible interior middle carries the same number of paths, independent of a, by symmetry).
So f(G_H(a)) is a max of finitely many explicit affine functions, each determined by its values at a = 4, 5.

Five gadgets (vertices u,v,x,y,z,w; middles extra), `verify_families.py`, `families_slope5.json`:

| r | gadget edges (besides the a middles u–m–v) | max pair | f |
|---|---|---|---|
| 0 | K4 on {u,x,y,z} | (x, m) | 5a |
| 1 | triangle xyz, u–y, u–z, v–x | (y, m) | 5a+1 |
| 2 | u–z, u–w, v–y, x–y, x–z, x–w, y–z | (w, m) | 5a+2 |
| 3 | x adj u,v; y,z,w each adj u and x | (w, m) | 5a+3 |
| 4 | x adj u,v; z,w adj u,x; y adj v,x | (w, m) | 5a+4 |

For each gadget the script computes every pair-type line, checks affinity at a=6,7,8, then checks that every line
has slope ≤ 5 and value ≤ 5·4 + r at a=4 ⇒ the claimed line is the max for **all a ≥ 4**; plus brute force a=4..12.
Hence every k ≥ 20 is f(G) for G with ⌊k/5⌋+2+4 vertices or fewer. Together with the census (4..19): **all k ≥ 4.** ∎

Hand check of r=1, pair (y, m): ending …u–m: y-u, y-z-u, y-x-z-u, y-x-v-m'-u, y-z-x-v-m'-u → 3+2(a−1);
ending …v–m: y-x-v, y-z-x-v, y-u-z-x-v, y-u-m'-v, y-z-u-m'-v, y-x-z-u-m'-v → 3+3(a−1). Total 5a+1.

Side observation (verified a,b ≤ 11, not proved): hubs u,v with a middles, w adjacent to u and v, plus b middles between
u and w gives f = (b+2)(a+1) − 2; without the edge u–w, f = (b+1)(a+1) − 2 (b ≥ 2).

Exploration scripts: `search_fam*.py` (classify K_{2,a}+gadget families by eventual slope/residue; `fam_t4.txt`).
Slope-2 families of this type never gave odd values (consistent with the pairing argument above).

## 4. Grid graphs (`grid.c`, `grid_paths.json`)

Simple paths between opposite corners of the m×m grid (A007764): m=2: 2, 3: 12, 4: 184, 5: 8512, 6: 1262816 ✓.

Length (edges) histogram for m=5 (8512 paths; lengths are even, 8..24; 104 Hamiltonian):

| length | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 |
|---|---|---|---|---|---|---|---|---|---|
| count | 70 | 224 | 510 | 956 | 1586 | 2224 | 2106 | 732 | 104 |

(m=3: 4:6, 6:4, 8:2; m=4: 6:20, 8:36, 10:48, 12:48, 14:32; m=6 full histogram in the JSON.)

## Status summary
- PROVED: f(G)=3 impossible (hand). Every even k ≥ 2 (hand, K_{2,a}). Every k ≥ 4 (computer-assisted: census for
  k ≤ 19 + exact affine verification of five families for k ≥ 20). Hence value set = {0,1,2} ∪ [4,∞).
- PROVED by exhaustive enumeration: minimal vertex counts for every k listed in `census.json` (n ≤ 10).
- CONJECTURE / open: exact growth of n_min(k) (lower bound from f(K_n) ~ e·(n−2)!, so n_min(k) ≥ roughly log k/log log k;
  the families give n_min(k) ≤ k/5 + 6, very weak; the census suggests n_min(k) grows like the inverse factorial).
