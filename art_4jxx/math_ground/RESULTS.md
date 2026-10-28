# Plaquette ground states on {0,1}^{Z^2}: computational exploration (MO 516372)

Tile convention: window [[a,b],[c,d]] = [[TL,TR],[BL,BR]], index t = a+2b+4c+8d.
Energy per site e(x) = average of J[t] over all 2x2 windows.

## What was computed

| file | content |
|---|---|
| `gs.py` | solvers: dense column-transfer min-mean-cycle (Howard policy iteration, verified against Karp), sparse version for SFT faces, an independent brute-force "sheared single column" search, LP lower bounds on m x n windows |
| `sweep.py`, `data/sweep{1,2}.jsonl` | 9000 random J, 9 families x 1000 |
| `fhat.py`, `data/fhat_vertices.json` | the 21 vertices of F^ and periodic realisations |
| `candcheck.py`, `data/candcheck.txt` | follow-up on the J where the LP(3x3) bound is not met |
| `stair2.py`, `data/stair_lp_k15.json` | one-parameter scan through the period-21 example |
| `ground_states.json` | 34 certified examples for the art piece |

**Upper bound.** e_p is the minimum energy per site over configurations with vertical period p (any horizontal behaviour). It equals (minimum mean cycle of the 2^p-state column graph)/p. Every doubly periodic configuration has some vertical period, so inf_p e_p is the best periodic energy. Shears come for free, because a cycle of length q may return to a vertically rotated column. The minimal period lattice of the optimal cycle is extracted afterwards and reported as basis (p,0),(s,q) in (row,col).

**Lower bound.** LP over probability vectors on m x n windows whose left/right and top/bottom marginals agree (shift-consistency), minimising the mean J over the sub-tiles. It is valid for every invariant measure. If LP = e_p, the periodic configuration is a certified ground state. For faces, forbidden tiles are imposed as hard constraints, which lets the LP go to 4x5 or 5x5 windows.

**Checks.** Howard and Karp agree for p ≤ 6 on 300 random J (0 mismatches). The configuration energy recomputed directly on the torus equals e_p. LP ≤ e_p in every case. The sparse SFT solver agrees with the dense one. Each long-period claim below was confirmed by a second, independent code path: brute-force enumeration of sheared single-column configurations.

## Results of the random sweep (p = 1..10, LP on 3x3)

Families: `gauss` N(0,1); `int2` integers in [-2,2]; `pm1sparse` {-1,0,1} with 60% zeros; `ising` random spin couplings (field, nn, diagonal, 3- and 4-spin); `faceK` K random allowed tiles with N(0,1) energies (25% of them all zero) and the others set to 10 ("forbidden").

| family | N | LP33 certifies | p*=1 | 2 | 3 | 4 | 5–8 | 10 |
|---|---|---|---|---|---|---|---|---|
| gauss | 1000 | 99.9% | 455 | 265 | 206 | 64 | 10 | 0 |
| int2 | 1000 | 100% | 573 | 229 | 153 | 31 | 14 | 0 |
| pm1sparse | 1000 | 100% | 512 | 274 | 178 | 25 | 11 | 0 |
| ising | 1000 | 100% | 439 | 276 | 170 | 94 | 21 | 0 |
| face8 | 1000 | 99.9% | 636 | 206 | 125 | 28 | 5 | 0 |
| face10 | 1000 | 99.8% | 635 | 189 | 144 | 26 | 5 | 1 |
| face11 | 1000 | 99.8% | 628 | 197 | 136 | 31 | 8 | 0 |
| face12 | 1000 | 100% | 621 | 195 | 144 | 36 | 4 | 0 |
| face13 | 1000 | 99.9% | 623 | 178 | 160 | 28 | 11 | 0 |

Here p* is the smallest vertical period that reaches min_{p≤10} e_p. Fundamental-domain areas over all 9000 samples: 1: 4152, 2: 2400, 3: 1211, 4: 688, 6: 434, 7: 28, 8: 63, 10: 1, 12: 17, 14: 1, 15: 4, 30: 1.

**Main empirical finding.** In 8993/9000 samples the 3x3-window LP already equals the best periodic energy with p ≤ 10, so the periodic optimum is a *proved* ground state. Long periods are rare: area ≥ 7 in about 1.3% of samples. They are mostly diagonal "staircases" with lattice (p,0),(s,1), for example (8,0),(5,1) and (7,0),(3,1).

### The 7 non-certified cases (LP33 gap > 1e-6), all resolved so far

- Three faces (face10, face11, face8) and one more face11 have a period-1 optimum (uniform). LP33 is loose there. LP on 4x5 windows closes the gap in the two cases checked (face10: e* = −0.15174 = LP45; face11: e* = LP44). So these are not counterexamples, only a weak relaxation.
- **face10, allowed tiles {0,2,5,7,10,11,12,13,14,15}.** The strip optimum keeps changing with p up to 16 (−0.4276, −0.4276, −0.4576, −0.6013, −0.6287, −0.6226, −0.6261, −0.6371, −0.6511, −0.6616 (p=10), …, −0.6616 (p=15), −0.6469 (p=16)). LP33 = −0.7088, but LP44 = LP45 = LP55 = −0.667047362180058. Brute-force shear search finds an exact match at **p = 21, shear s = 13**: energy −0.6670473621800581 = LP44. This is a certified ground state of period 21, and its tile frequencies have denominator 21. The column graph's edge count grows like ~2.6^p (close to φ²), and the period pair (21,13) is consecutive Fibonacci numbers.
- **gauss** (all 16 tiles allowed, J in the JSON, rank 2). With p ≤ 10 the best is area 8 at −0.82265, LP33 = −0.82938. The shear search again finds **(21,0),(13,1)** at −0.8285642010521516 = LP44 (−0.8285642010521523). This is a certified period-21 ground state for a generic Gaussian J.
- The remaining candidates (face13 area 15, face8, face11) were still running in `candcheck.py` at the time of writing; see `data/candcheck.txt`.

### F^ vertices (`fhat.py`)

The computation reproduces the OP's facts. The equality system has rank 6 and F^ has 21 vertices. 17 of them are realised by explicit periodic configurations (areas 1–6, listed in the JSON file). The other 4 (supports {1,7,10,12}, {2,5,11,12}, {3,4,10,13}, {3,5,8,14}) have no periodic realisation with p ≤ 12. The 3x3 LP shows they are **not in K**: the hard-constraint LP minimum of "fraction of tiles outside the support" is 1/3 > 0. This is a floating-point LP certificate and could be made exact with rational arithmetic.

## What can be proved (modest)

1. **Certificate principle.** If LP_{m×n}(J) = e_p(J) for some p, then J has a periodic ground state. Weak duality makes this rigorous up to LP numerics. Empirically it holds for > 99.9% of random J at m = n = 3, and for every residual case examined at m×n ≤ 5×5.
2. **Open cone.** Let J have a unique minimiser on F^ that is one of the 17 good vertices. Then that vertex is the frequency vector of a periodic configuration, and it is a ground state, since K ⊂ F^. The same holds for J where the 3x3-window LP has a unique optimum whose 2x2 marginal is realised periodically. This is an open set of J with periodic ground states. It is not new mathematics, just bookkeeping.
3. Nothing in this computation proves or disproves the general question.

## Conjecture (clearly labelled; not proved)

**Conjecture A (Fibonacci staircase).** In the face X = SFT with allowed tiles {0,2,5,7,10,11,12,13,14,15} (and in nearby generic J), there are one-parameter families J(t) whose certified ground states are diagonal staircases with periods (F_{n+1},0),(F_n,1) for arbitrarily large n. They form a devil's-staircase phase diagram. The current evidence is two independent J with period (21,13), plus an adjacent area-30 phase (denominators 30 in the LP solution) along the line J + t·e_15. If the slope s/p can be made to converge to 1/φ in a way that makes the limiting point of K extreme (an Aubry–Mather-type scenario), then at the accumulation point J* the only ground states would be Sturmian, and the MO question would have a **negative** answer. Equally plausible: the plateaus cover the whole line and accumulate only at rational slopes, which would be consistent with a positive answer. In both cases the same computation decides: along a 1-parameter line through this J, compute the exact phase diagram (LP on 4x4 windows is cheap here, about 2584 windows) and check whether the plateau lengths sum to the full interval, and what the limit slopes are.

**Conjecture B (weak).** For generic J, ground states are periodic and are certified by a finite-window LP. The required window size is unbounded, as the period-21 cases show.

## Caveats

- Floating-point tolerances are 1e-9 relative (Howard) and 1e-7 (certification). The LP is HiGHS in double precision. None of the certificates are exact rational proofs.
- The p ≤ 10 sweep can miss periods > 10. A positive LP gap flags this, and that is how the period-21 cases were found. A sample with gap 0 is certified regardless of p.
- "Face" energies use J = 10 for forbidden tiles in the sweep. Certification in the period-21 face example uses hard constraints, so it is a statement about the SFT.
