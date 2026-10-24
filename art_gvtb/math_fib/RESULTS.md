# MO 497943 — Lyapunov exponent of X_{n+1}=U_nX_n+V_nX_{n-1}, U,V ∈ {1±α}

**Method (task 1).** Y'=U+V/Y; in t=log y each map f_{u,v} is a strict contraction of the invariant interval [a,b]
(a=(1−α)(1+1/b), b=(1+α)(1+1/a)), since |d log f/d log y| = v/(uy+v) < 1. Hence the dual operator
(Ph)(y)=¼Σ h(u+v/y) maps analytic functions to analytic ones and P^k log → η uniformly, with min/max of P^k log bracketing η.
I represent h by Chebyshev interpolation in log y (N=200/400 nodes, `eta_koopman.py`); convergence in ~40 iterations,
N=200 vs 400 agree to < 7e‑16 on the whole grid. Checks: MC with 1e9 steps (`mc2.py`, all within 1.2σ, σ≈1e‑5),
exact 4^12‑word brackets (`bracket.py`), and the series below (agreement 2e‑15 at α=0.05). Values (`eta.csv`, step 0.01):

| α | η | α | η | α | η | α | η |
|---|---|---|---|---|---|---|---|
|0 |0.48121182505960 (log φ)|0.25|0.47236243383236|0.50|0.44261939092862|0.75|0.37396669492212|
|0.05|0.48086601125910|0.30|0.46832349062833|0.55|0.43316149720101|0.80|0.34983305356813|
|0.10|0.47982466945263|0.35|0.46342305732891|0.60|0.42205279469992|0.85|0.31806295444470|
|0.15|0.47807584810713|0.40|0.45758214966708|0.65|0.40891130695372|0.90|0.27263025448618|
|0.20|0.47559876754878|0.45|0.45069502910462|0.70|0.39317379956353|0.95|0.19448793092820|

**Small α (task 2).** Write Y=φ+Σα^k y_k (stationary processes), U=1+αs, V=1+αt. Order 1: y₁'=s+t/φ−y₁/φ², so E y₁²=φ;
order 2: y₂'=y₁²/φ³−y₂/φ²−t y₁/φ², so E y₂=1/(φ²+1); and η=log φ+α²(E y₂/φ−E y₁²/(2φ²))+…, giving
**c₂ = 1/(3φ+1) − 1/(2φ) = −1/(2√5 φ) = −(5−√5)/20 ≈ −0.1381966011.** Higher orders by solving the (triangular) linear
system for stationary moments exactly in Q(√5) (`series.py`; odd c vanish by α→−α symmetry):
c₄=−(17−3√5)/200≈−0.0514590, c₆=−(197−59√5)/1500≈−0.0433813, c₈=−(2847√5−4795)/50000≈−0.0314217,
c₁₀=−(98715−43553√5)/62500≈−0.0212405. Through α¹⁰ the residual vs numerics is 2e‑15 at α=0.05, 2e‑9 at α=0.2.

**Closed form? (task 3).** η is the top Lyapunov exponent of an i.i.d. product of the 4 matrices [[u,v],[1,0]], i.e. an
integral against the Furstenberg measure μ; no closed form is known for any two‑point‑law family of this kind, and none is
expected (cf. Viswanath 2000: x_{n+1}=x_n±x_{n−1}, growth 1.13198824…, computed numerically from a fractal Stern–Brocot
measure; Embree–Trefethen 1999 for ±βx_{n−1}; Janvresse–Rittaud–de la Rue 2008/10). Explicit stationary laws of random
continued fractions are known only for special continuous laws (Letac–Seshadri, GIG laws). What *is* rigorous: η is
real‑analytic on (−1,1) (Ruelle 1979; products of positive matrices; [[u,v],[1,0]]² > 0). μ always has full support [a,b]
(the image of (1−α,1+α) covers almost all of [a,b]; no gaps for any α). But dim_H μ ≤ h/χ with h=log4,
χ = 2η−½log(1−α²) (Lyapunov exponent of the IFS in log y; Feng–Hu), so **μ is singular for α > α\* = 0.9041921190624**
(where χ=log 4) despite full support. By Hochman–Solomyak (Invent. Math. 2017, Furstenberg measures with algebraic entries)
dim μ = min(1, h_RW/χ) for rational α, h_RW = log 4 if the semigroup is free.

**Conjectures (task 5), with evidence.**
1. η is strictly decreasing on [0,1) (true on the 0.01 grid; all computed c_{2k}<0, k≤5).
2. **α→1:** η(α) = (1/9)·log(1−α) + C + O(1−α), C ≈ 0.52518638 (numerics at 1−α=1e‑3…1e‑8, error ~0.05(1−α)).
   Heuristic proof of 1/9: log X_n ≈ k_n log(1−α) with min‑plus recursion k_{n+1}=min(k_n+A_n, k_{n−1}+B_n),
   A,B ~ Bernoulli(½); d_n=k_n−k_{n−1}∈{−1,0,1} is a Markov chain with stationary law (1/9, 2/3, 2/9), so E d = 1/9.
   Consistent with c_{2k} ≈ −1/(9k) (the Taylor coefficients of (1/9)log(1−α²)). Hence radius of convergence 1, and
   **η changes sign at α₀ = 0.99118203713519** (X_n → 0 a.s. for α > α₀).
3. μ is absolutely continuous for α < α\* (dim = 1 there by Hochman–Solomyak for rational α; a.c. not proved).

**Files.** `eta.csv` (α=0…0.99, 15 digits); `stationary.npz`: alphas 0.05…0.95 step 0.01, `support` (a,b),
`hist_linear` (4000 equal bins on [a,b], masses), `hist_log` (4000 bins equal in log y), `eta`. Built by CDF fixed‑point
iteration on 2^18 log‑grid points (`stationary.py`; E log Y from it matches η to ≤1.2e‑7; L1 vs 1e8‑sample MC at noise level).
Other: `table.py` (table, α₀, α\*, α→1), `table_out.txt`, `series10.txt`, `mc_check.txt`.
