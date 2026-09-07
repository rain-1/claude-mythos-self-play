# MO 514975 — longest run of 1s vs longest run of 0s: the gap tends to exactly 2

Question: for a uniform string in {0,1}^n let L_0, L_1 be the longest runs of 0 and of 1,
ℓ*(n) = E max(L_0, L_1), ℓ_*(n) = E min(L_0, L_1). Asked: liminf ℓ_*/ℓ*.

The posted answer (score 4) gives the key identity **max(L_0,L_1) ~ 1 + R_{n−1}** where R_m is the
longest run of 1s in a uniform string of length m (proof: pass to the difference string
d_i = s_i ⊕ s_{i+1}, uniform of length n−1; a run of length r in s is a run of r−1 zeros in d),
hence ℓ* = 1 + E R_{n−1}, ℓ_* = 2 E R_n − E R_{n−1} − 1, and both ~ log₂ n so the limit is 1.

## What the identity also says (not stated there)

    ℓ*(n) − ℓ_*(n) = 2 − 2 (E R_n − E R_{n−1})  →  **2**,

because E R_n − E R_{n−1} → 0. So *the expected difference between the longest run of 1s and the
longest run of 0s tends to exactly 2*, and the ratio approaches 1 from below like 1 − 2/log₂ n.
The increment E R_n − E R_{n−1} ≈ 1/(n ln 2) (the derivative of log₂ n), so the gap is
2 − 2/(n ln 2) + o(1/n): at n = 2¹⁰ the exact gap is 1.99718, and 2 − 2/(1024 ln 2) = 1.99718.

## Exact machinery (`runs.py`)

P(R_n ≤ L) = q_L(n) with q_L(m) = 1 for m ≤ L and q_L(m) = Σ_{j=0}^{L} q_L(m−1−j)/2^{j+1}
(a block of j ones followed by a zero); evaluated at n = 2^k by powers of the (L+1)×(L+1)
companion matrix; E R_n = Σ_{L≥0} (1 − q_L(n)). Brute force over all 2^n strings for n ≤ 14
matches the two identities to every printed digit.

| k = log₂ n | E R_n | gap ℓ* − ℓ_* | ratio ℓ_*/ℓ* | 1 − 2/k |
|---|---|---|---|---|
| 4 | 3.42530823 | 1.82546997 | 0.57919507 | 0.500 |
| 8 | 7.33869851 | 1.98875345 | 0.76134219 | 0.750 |
| 12 | 11.33312001 | 1.99929565 | 0.83788751 | 0.833 |
| 16 | 15.33277068 | 1.99995597 | 0.87754933 | 0.875 |
| 20 | 19.33274884 | 1.99999725 | 0.90163665 | 0.900 |
| 24 | 23.33274747 | 1.99999983 | 0.91780625 | 0.917 |
| 28 | 27.33274737 | 1.99999999 | 0.92941031 | 0.929 |

E R_n − log₂ n → 0.3327474 along n = 2^k (the classical Erdős–Rényi constant γ/ln 2 − 3/2 +
periodic fluctuation, sampled at one phase of the period). The liminf of the ratio is 1, and the
ratio is < 1 for every finite n by the gap → 2 statement. Comment-grade; the gap → 2 corollary is
the one line worth adding under the accepted answer.
