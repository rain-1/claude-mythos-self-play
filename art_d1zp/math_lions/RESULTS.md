# math_lions — "more than a third of everything" (MO 474916)

Question: X1..X4 i.i.d. ≥ 0. How large can P[X1+X2+X3 < 2·X4] be? Equivalently: how often can a given one
of four hold more than a third of the total. Call such a holder a *lion*; at most two of four can be lions.

**Status of the question (not mine):** the value is sup = 0.400695…; lower bound from the nested construction
(MO answer 484853, arXiv 2412.15179 Prop. 4.1), matching flag-algebra upper bound in arXiv 2611.29223
(announced in an MO answer this week). Everything below is my own checking and play.

## Checked (exact algebra, `formula.py`)
The nested law X = ε^G(1−ε^U), G geometric with P(one level deeper) = p, U uniform, ε → 0. Let k = number of
the n draws on the top level. Then for the threshold 1/(n−1) of the total:
k ≤ n−2 → all k are lions; k = n−1 → all but the smallest (n−2); k = n → none. Hence

    T_n(p) = [ Σ_{k=1}^{n−2} k·C(n,k)(1−p)^k p^(n−k) + (n−2)·n(1−p)^(n−1)p ] / ( n(1−p^n) ).

- n = 3: T = p/(1+p+p²) → 1/3 as p → 1 (the known value; never attained).
- n = 4: T = p(2−p)/((1+p)(1+p²)); maximum at the root p* = 0.47434645545… of p⁴−4p³−3p²−2p+2;
  **T* = 0.40069537232930… is a root of 16x⁴+8x³+99x²−32x−4.** (agrees with the published value)
- In the limit the shares of a hand sit on the 15 barycentres of the tetrahedron of shares:
  corners 23.64 %, edge middles 39.29 %, face middles 29.03 %, centre 8.04 %; lions 1, 2, 2, 0.
- No lions ⇔ the share point is inside the dual tetrahedron spanned by the four face centres.

## Conjecture (mine, numerics only)
**For every n ≥ 4, sup_μ P[X_1+…+X_{n−1} < (n−2)·X_n] = max_p T_n(p):**

| n | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|
| T_n | 0.476009 | 0.535714 | 0.582488 | 0.619753 | 0.650126 | 0.675410 | 0.696837 | 0.715267 |
| p_n | 0.38072 | 0.33349 | 0.30160 | 0.27705 | 0.25701 | 0.24017 | 0.22574 | 0.21321 |

T_n → 1 (take p ≈ c/n). Evidence: `search.py` maximises P/(1−P_tie) over all laws on {0..K} by L-BFGS from
random starts. n=4, K=48: 0.3849; n=5, K=36: 0.4515, atom at 0 of 0.405; n=6, K=36: 0.5032, atom 0.362 —
always one atom at 0 plus a cluster crowding geometrically under the maximum, i.e. a finite shadow of the
nested law, and always below T_n. This is weak evidence (small K, local search); no upper bound attempted.

## Observation: the supremum is approached absurdly slowly (`finite_eps.py`, 4·10⁷ hands each)
| ε | 1/2 | 0.4 | 1/10 | 10⁻² | 10⁻³ | 10⁻⁵ | 10⁻⁹ | 0 |
|---|---|---|---|---|---|---|---|---|
| P | 0.3056 | 0.3154 | 0.3479 | 0.3655 | 0.3733 | 0.3815 | 0.3888 | 0.4007 |

The deficit times log(1/ε) still grows (0.16, 0.19, 0.22, 0.25): slower than 1/log(1/ε). Reason: U near 0
gives heights far below the vault, and those hands are not hierarchical. Guess: deficit ~ c·loglog/log.
