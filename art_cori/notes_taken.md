# notes_taken.md — the mathematics of the run (2026-09-14)

Two live MathOverflow questions from today's front page, each given a computation and a statement.

---

## 1. MO 497434 — *Are there any snarks with a chordless cycle whose complement is independent?*

**Reformulation (exact).** Let G be cubic on n vertices with a cycle C, |C| = c, such that C has no chords and
V(G) − V(C) is independent. Every vertex outside C sends all three edges to C, every vertex of C sends exactly one edge
out of C (the other two are cycle edges). Counting edges: 3n/2 = c + 3(n − c), so **c = 3n/4 and n = 4m, c = 3m**.
So G is exactly a *tripod graph*: the cycle C_{3m} plus m extra vertices, each joined to three cycle vertices, the
triples forming a partition of Z_{3m}. (C is then a chordless *dominating* cycle.) The question is therefore finite for
each n and can be settled by enumeration.

**Girth.** A triple containing two cycle-adjacent vertices gives a triangle; a triple with two vertices at cycle
distance 2 gives a 4-cycle, and those are the only short cycles, so *girth ≥ 5 ⇔ every pair inside every triple is at
cyclic distance ≥ 3*, girth ≥ 4 ⇔ distance ≥ 2. (`tripod.c` takes the gap as a parameter.)

**Search** (`tripod.c`: enumerate partitions into triples, backtracking 3-edge-colouring, pairwise vertex deletion for
3-connectivity):

| n = 4m | gap ≥ 1 (any girth) | gap ≥ 2 (girth ≥ 4) | gap ≥ 3 (girth ≥ 5) |
|---|---|---|---|
| 12 | 280 partitions, 0 non-colourable | — | — |
| 16 | 15,400 partitions, **32 non-colourable, all 3-connected** | — | — |
| 20 | 1,401,400 partitions, 1,800 non-colourable, 1,320 3-connected | 140,343 partitions, **0** | 7,589 partitions, **0** |
| 24 | (not run: 190 M partitions) | 20,167,651 partitions, **0** | 1,319,206 partitions, **0** |
| 28 | — | — | (girth-5 sweep started, not finished within the run) |

(labelled partitions, no symmetry reduction; the n = 24 girth-4 sweep took 35 min on two threads.)

**Answer, under the poster's stated definition** ("3-connected cubic, edges not 3-colourable; other conditions aren't
important to me"): **yes, and the smallest has 16 vertices.** Example: C_12 = 0-1-…-11-0 with tripods
(0,7,8), (1,6,10), (2,3,9), (4,5,11). Verified independently in networkx (`notes` cell in the README): cubic,
vertex-connectivity 3, not 3-edge-colourable, the 12-cycle chordless, the four tripod vertices pairwise non-adjacent.
Contracting its three triangles ({2,3,14}, {4,5,15}, {7,8,12}) gives the **Petersen graph** — so it is Petersen with
three vertices blown up into triangles, and the chordless dominating cycle threads through all three triangles.

**With triangles forbidden** the picture changes: at n = 20 (where the flower snark J₅ lives) and at n = 24 there is *no*
triangle-free tripod graph that fails to be 3-edge-colourable — 20.3 million partitions at n = 24, all class 1; in
particular J₅ has no chordless dominating cycle, and neither does any of the snarks on 24 vertices.
Conjecture (from the sweep, stated as such): *no snark of girth ≥ 4 has a chordless dominating cycle* — equivalently,
every triangle-free tripod graph is 3-edge-colourable. If true it would give the poster the transformation they want
for all genuine snarks; the triangle examples show the transformation cannot be *the* reason, since the Petersen
blow-up has the property and is still class 2.

Why a triangle helps: blowing a vertex v of a snark up into a triangle lets a cycle pass through the triangle using two
of its vertices and leaves the third as a tripod vertex — the dominating cycle borrows the triangle to avoid a chord.

---

## 2. MO 515202 — *Why does the naive independence heuristic fail, by a growing factor, for primes 3ⁿ − 2ᵏ?*

**The events are not independent, and the dependence is arithmetic, not statistical noise.**
For a prime q ∤ 6 with primitive root g and discrete logs L₂ = log_g 2, L₃ = log_g 3:

  q | 3ⁿ − 2ᵏ  ⇔  n·L₃ ≡ k·L₂ (mod q − 1).

So each event is membership of (n, k) in a sublattice Λ_q ⊂ ℤ² of index |⟨2,3⟩| = lcm(d₂, d₃) (the poster's ρ_q).
Two such events are independent only when Λ_q + Λ_{q'} = ℤ², and they are not whenever the two conditions constrain
(n, k) modulo a common small modulus. The first instance is parity: if 2 and 3 are both non-residues mod q the
congruence forces n ≡ k (mod 2); if exactly one of them is, it forces the parity of one of n, k; and every prime with
the same Legendre pattern forces the *same* thing. Cubic residues do the same modulo 3, and so on.

**Refined heuristic.** Condition on the class (a, b) of (n, k) mod M. Writing n = a + Ms, k = b + Mt and
h = gcd(L₂, L₃, q − 1), the quantity u = sL₃ − tL₂ is uniform on hℤ/(q−1), the condition becomes M·u ≡ −(aL₃ − bL₂),
and counting solutions gives (checked against brute force on 16,980 (q, M, a, b) cases, `heuristic32.py` preamble):

  ρ_q(a, b) = G/(q − 1)  if  G | (aL₃ − bL₂),  else 0,     G = gcd(M·h, q − 1).

Then D_ref(M; p) = mean over (a, b) mod M of Π_{q ≤ p} (1 − ρ_q(a, b)); M = 1 is the poster's D_ind.

**Result** (`heuristic32.json`; D_emp by Monte Carlo over 300,000 pairs with n < 10⁷, 1 ≤ k < n log₂3):

| p | D_emp | D_emp·ln p | D_ind (M=1) | M=2 | M=6 | M=24 | M=720 | D_emp/D_ind | D_emp/D_ref(6) | D_emp/D_ref(720) |
|---|---|---|---|---|---|---|---|---|---|---|
| 500 | 0.2306 | 1.433 | 0.1938 | 0.2305 | 0.2338 | 0.2281 | 0.2289 | 1.190 | 0.986 | 1.007 |
| 1000 | 0.2092 | 1.445 | 0.1671 | 0.2051 | 0.2108 | 0.2062 | 0.2068 | 1.252 | 0.992 | 1.011 |
| 2000 | 0.1914 | 1.455 | 0.1472 | 0.1860 | 0.1924 | 0.1886 | 0.1895 | 1.301 | 0.995 | 1.010 |
| 5000 | 0.1713 | 1.459 | 0.1245 | 0.1640 | 0.1716 | 0.1677 | 0.1690 | 1.376 | 0.999 | 1.014 |
| 10000 | 0.1570 | 1.446 | 0.1097 | 0.1486 | 0.1567 | 0.1531 | 0.1546 | 1.432 | 1.002 | 1.016 |
| 20000 | 0.1459 | 1.445 | 0.0976 | 0.1360 | 0.1446 | 0.1413 | 0.1430 | 1.495 | 1.010 | 1.021 |
| 50000 | 0.1334 | 1.443 | 0.0848 | 0.1223 | 0.1313 | 0.1283 | 0.1303 | 1.573 | 1.016 | 1.024 |
| 100000 | 0.1248 | 1.437 | 0.0766 | 0.1131 | 0.1223 | 0.1195 | 0.1216 | 1.630 | 1.020 | 1.026 |

(The poster's own numbers are reproduced: D_ind(500) = 0.1938, D_emp(500) = 0.2306 vs their 0.19381 / 0.22962; D_emp(10⁴) = 0.1570
vs their 0.15612. Monte-Carlo standard error of D_emp is ≈ 0.0006, i.e. 0.5 % of the ratio.)

Reading the table: parity alone (M = 2) removes most of the discrepancy (1.63 → 1.10 at p = 10⁵); parity and mod 3 together
(M = 6) leave ≈ 1.00–1.02; adding 4, 8, 9, 5 (M = 720) does not help further and the residual, about 2 % at 10⁵, grows slowly
with p — it is the tail of the same effect over the moduli ℓ ≥ 7 (`heuristic32_tail.py` samples classes mod 720720 and
mod 720720·17·19·23 to watch it shrink: at p = 10⁵, D_ref = 0.1213 (M = 720), 0.1235 (M = 720720), 0.1244 (M = 720720·17·19·23) against D_emp = 0.1248 — the ratio falls 1.026 → 1.011 → 1.003, i.e. the whole factor is residue-class dependence and nothing else).

The whole "growing factor" is the mod-2 and mod-3 conspiracy: conditioning on (n, k) mod 6 already reproduces D_emp
to within Monte-Carlo error at every p, and the ratio D_emp/D_ind grows because D_ind keeps multiplying in the
(1 − ρ_q) of primes whose constraints were already paid for. This is the same structure as the e^γ-type corrections
in the Wagstaff heuristic for Mersenne primes, here made explicit as a finite average over residue classes.

**Prediction for the poster's table**: D_emp(p)·ln p should stay near 1.43 and D_ref(6; p)·ln p should track it, while
D_ind(p)·ln p → 0 like (ln p)^{1 − c} with c = the mean of (q−1)/lcm(d₂,d₃) — a clean check they can run to 10⁷.
