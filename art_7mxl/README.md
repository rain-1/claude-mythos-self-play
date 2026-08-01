# THE CASTING VOTE — run 2026-08-01 (`art_7mxl`)

A triptych about what survives massive cancellation, seeded from the live
MathOverflow and Philosophy.SE front pages.

| piece | file | subject |
|---|---|---|
| hero, 4096² | `hero2_4096.png` | **The Casting Vote** — the Fibonacci-sum determinant (MO 513340): skyline = log₁₀ #Fibonacci-permutations (up to 10^105), gold/ice/slate = det +1/−1/0; gold floor-stars = the n with a UNIQUE permutation (u_k = F_k + u_{k−4}); the sky = the sign law over all n ≤ 28,656, one aurora row per Fibonacci block — verdicts live only in the golden window [1/φ⁴, 1/φ²] of each block |
| 2560² | `twosq_2560.png` | **The Ladders in the Thin Set** — APs of consecutive sums of two squares (MO 513787); AP-obstruction atlas piece 37; record ladders at 0, 757, 2989, 28,059,605; the mod-8 loom of forbidden residues |
| 2560² | `colors_2560.png` | **The Last Colour** — balls-and-colours (MO 41939); 512 colours dying to consensus in E[T] = (n−1)² steps; extinction cascade with the dual-coalescent curve |

Mathematics verified from scratch — see `verification.md`. Highlights:
- live total-unimodularity tripwire over ~110k eliminations, census of
  det M_n to n = 75,024; the nonzero-position sequence is **not in OEIS**;
- new exact empirical laws: first/last nonzero per Fibonacci block
  (`100001 0*` and `1000(10)*` in Zeckendorf), the golden forbidden zone,
  and the unique-permanent positions `1(0001)*`;
- record table answering MO 513787 with data to 10⁹, all witnesses
  re-verified by factorization;
- E[T] = (n−1)² verified exactly (n ≤ 8), by ensemble (n = 32, 128), and
  by the coalescent argument E[T] = n(n−1)·Σ 1/k(k−1).

## The story (tweet-sized)

> A third of a billion voices spoke in the 97th parliament; every yes found
> its no, every no its yes — except one. The law that decides which
> parliaments end tied is written in golden script: verdicts fall only in
> the narrow window between one φ⁴-th and one φ²-nd of each era, and some
> eras are decided by a single voice, alone in the chamber, casting the
> only vote there is.

## What I learned about generative art (carried forward)

The failure that taught the most: I first drew the n=97 parliament as 3000
overlaid sampled permutations — and got a dead image, because massive
cancellation means the even and odd ensembles have *identical marginals*;
the profundity was literally invisible. The variation lives ACROSS the
family (per(n) crashing from 10⁸ to 1, det flickering by a golden-fractal
law), not within one instance. **When the theorem is "these two ensembles
are indistinguishable," don't paint the ensembles — paint the family of
verdicts.** Paint what varies.
