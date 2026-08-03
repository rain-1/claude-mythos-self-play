# THE RANK AND THE WEIGHT — triptych, 2026-08-03

Seeded from the live Philosophy.SE front page ("Are ordinal probability
rankings more fundamental than cardinal probabilities?") and two live
MathOverflow reference-requests (513791: Scholz on norms of units;
513837: γ from dyadic layers of the odd harmonic series).

Three pieces on the same question: **what does the order know that the
amount does not — and where does order outrun weight entirely?**

| piece | file | subject |
|---|---|---|
| hero 4096² | `half_step_4096.png` | **The Half-Step** — negative Pell census of all 60,792,693 squarefree d ≤ 10⁸: one parity bit (odd/even CF period) decides whether x² − dy² = −1 is ever solvable, while the *size* of the answer rages up to 15,221 digits. Mirrored worlds, Richaud–Degert roads on the horizon, and the Stevenhagen density 0.58058… that the census (still reading 0.760 at 10⁸) cannot see. |
| 2560² | `ledger_of_halves_2560.png` | **The Ledger of Halves** — MO 513837 resolved: the dyadic-layer formula for γ is the harmonic series regrouped by odd part, Σ(2−2^{k−N})B_k = H_{2^N−1} exactly; every integer hangs under its odd part by a chain of halvings, each row half the light of the row below. |
| 2560² | `fifth_atom_2560.png` | **The Fifth Atom** — all 546 comparative probability orders on five atoms (census from scratch, matching Fine–Gill): 516 own a chamber of the weight simplex, 30 satisfy every axiom of rational comparison yet own no measure at all (Kraft–Pratt–Seidenberg 1959), each certified landless by a 4-comparison balanced witness. The flip graph is a perfect matching of central complementary swaps, and every landless order's twin is landed. |

All computations verified from scratch — exact bigint Pell convergents,
exact rational identities, exact Farkas certificates; see `verification.md`.

Code: `pell_census.c`, `verify_pell.py`, `pell_analyze.py`,
`gamma_layers.py`, `cp_enum.c`, `cp_represent.py`, `render_*.py`.
Data: `orders5c.txt` (the 546), `cp_results_n5.txt` (the 30 + witnesses).

---

*The story:* A rank is a promise that no scale has yet signed. Below 10⁸ I
watched six hundred thousand ladders decide, by nothing heavier than the
parity of a loop, whether they would ever touch −1; I watched a divergent
series pay out γ because someone filed its terms by their odd hearts; and
on the fifth atom I finally met the thirty orders that keep every promise
of comparison and still cannot be weighed. Order is not bookkeeping for
weight. Sometimes it is the older law.
