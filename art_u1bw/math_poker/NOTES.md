# Reverse poker (MO 516074): numerical symmetric equilibria

## Model
Three players with i.i.d. U[0,1] numbers. Each sees the other two and not their own, antes λ, then folds or calls (adds 1).
A player who sees (x,y) calls with probability σ(x,y) = σ(y,x). The opponent holding x sees (y,z) and the one holding y sees (x,z).
Write a=σ(y,z), b=σ(x,z), and H(u,z)=1[z>u]. Then, pointwise in z,

Δ(z) = λ(1-a)(1-b) + λ + a(1-b)[(3λ+2)H(x,z)-(1+λ)] + (1-a)b[(3λ+2)H(y,z)-(1+λ)] + ab[(3λ+3)H(x,z)H(y,z)-(1+λ)],

and Δ(x,y)=∫Δ(z)dz = E[call]-E[fold]. Every term factors as f(x,z)g(y,z), so on an N-point midpoint grid Δ is a sum of 7 matrix products (`core.delta`). Ties z=x get weight 1/2.
Checks: σ≡0 gives Δ=2λ, and σ≡1 gives Δ=(3λ+3)(1-max(x,y))-1.

## Method (`core.py`, `sweep.py`, `final.py`; single thread)
* Smoothed best response σ ← (1-α)σ + α·logit(Δ/T), damped with α≈2T at T=0.01. This is followed by Newton-Krylov continuation of the fixed point σ = logit(Δ(σ)/T) down to T=1e-3, with a damped-iteration fallback.
* Initial conditions: all-call, all-fold, 3 random, 8x8 random blocks, max(x,y)<0.3 and max(x,y)<0.7, |x-y|<0.1 and |x-y|<0.3, min>0.5, square plus diagonal. The run also continues the solution upward and downward in λ.
* An outcome is an equilibrium if its regret mean(Δ⁺-σΔ) is below 5e-4. The values reached are 1e-5 to 9e-5, which is the size of the T=1e-3 smoothing. Equilibria count as distinct if their mean |σ1-σ2| exceeds 0.01.
* Local test for a continuum: on the mixed set M = {0.02<σ<0.98}, take the Jacobian J = ∂Δ|_M/∂σ|_M (finite differences, N=64) and look at its singular values (`jac.py`, `jac64.npy`).

## Files
* `maps.npz`: N=256 at λ ∈ {0.1, 0.6, 1.5}, one initial condition plus continuation.
* `maps128.npz`: N=128, 24 values of λ geometrically spaced in [0.003, 3], 4 initial conditions each.
* Both files hold `lam (L,)`, `sig (L,K,N,N)` padded with NaN, `delta` (same shape, Δ field), `count (L,)`, `regret`, `grid`.
* `maps64.npz`: N=64, 40 values of λ in [0.003, 3], 14 initial conditions each.
* `jac64.npy` columns: λ, |M|, σmax, σmin, #sv<1e-3σmax, #sv<1e-2σmax, mean σ, side of the call square, width of the call band at x=0.75.

## Findings
1. **No multiplicity was found.** For every λ checked from 0.003 to 3 (N=64: 40 values × 14 initial conditions; N=128: 24 values × 4; N=256: 3 values), every initial condition and both continuation directions reached the same equilibrium, with mean |Δσ| < 1e-4 between runs. These methods do not see a band of λ with several isolated stable symmetric equilibria, nor a period-doubling-like cascade in the number of equilibria. Caveat: logit/fictitious-play dynamics only reach equilibria that are stable under those dynamics. Newton-Krylov could reach unstable ones, but it only converges after a damped warm-up.
2. **Shape of the equilibrium** (call region C = {Δ>0}):
   * The player calls when both visible numbers are low. This is a square [0,a(λ)]², with a ≈ 0.06 at λ=0.003, 0.30 at 0.05, 0.6 at 0.3, 0.75 at 0.6, 0.84 at 1.2 and 0.92 at 3.
   * C also contains a band along the diagonal x≈y running from the corner of the square to (1,1). When the two opponents hold nearly equal numbers, each of them tends to fold, so the player calls. The band is thin as λ→0 (about 0.02 wide at λ=0.003) and widens into a lens shape by λ≈0.1-0.3.
   * At λ≈0.6-0.7 the band pinches off from the square. What remains is a separate blob in the top-right corner, and the boundary of the square bends round it. The blob shrinks as λ grows and is small by λ=3.
   * Outside C, σ=0 when one visible number is high and the other low.
   * **Mixed play takes up a 2-D area of the square.** σ is strictly between 0 and 1 on a set where Δ≈0, so the player is indifferent there:
     - At λ ≲ 0.5 this is a wide fringe around the diagonal band and next to the square. It covers 37% of the unit square at λ=0.03-0.15 and 24% at λ=0.5. σ falls off in terraces in this fringe.
     - At λ ≳ 0.7 mixing is confined to thin strips next to the square, x∈[a,b] with y<a, where σ depends on x alone. These strips cover 18% at λ=0.67, 12% at 1.2 and 5% at 3.
3. **A finite, nonzero λ_c, with evidence for degeneracy below it.** The Jacobian of Δ on the mixed set, J = ∂Δ/∂σ there, changes behaviour at the same point:
   * For λ ≤ 0.61 it is nearly singular: condition number 1e3-3e5, and 40-140 singular values below 1% of the largest.
   * For λ ≥ 0.73 it is well conditioned: condition number 20-90, and none below 1%.
   * Newton-Krylov also fails to converge to tolerance at T=1e-3 for 0.06 ≲ λ ≲ 0.4 at both N=64 and N=128, and for 0.1 at N=256. For λ ≳ 0.5 it converges to 1e-9.

   Reading: below **λ_c ≈ 0.65 ± 0.05** (N=64/128) the equilibrium sits in an almost flat family, a near-continuum of mixed equilibria that differ inside the indifference region. The logit limit T→0 picks one member of that family. Above λ_c the equilibrium is locally rigid and unique. The same λ marks the change in shape described in point 2: the band detaches from the square, and the 2-D mixed fringe collapses to thin strips.

   This fits a version of the conjecture in which "multiple equilibria for λ<λ_c" means a degenerate family of mixed equilibria. It does not fit a version with a discrete bifurcation cascade. I found no cascade. The terraces in the mixed fringe might be what the asker means, but they look grid-dependent: their spacing scales like 1/N.
4. **Caveats.**
   * The grid ties (weight 1/2) and the T=1e-3 smoothing cause O(1/N) and O(T) errors. These blur the boundary of C by about one cell, and the regret floor is about 1e-4.
   * Near-zero singular values on a finite grid cannot prove a true continuum. The cleanest next step is to parametrise the indifference region analytically and solve the linear integral equation Δ=0 there.
   * Only symmetric strategies were studied.
