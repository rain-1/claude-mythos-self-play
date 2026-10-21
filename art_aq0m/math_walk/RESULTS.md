# MO 392723: the identity Σ_k W(a_k; others) = 1

Setup. U_0,…,U_n are iid uniform on the unit circle (complex numbers e^{iφ_k} with iid uniform φ_k). Put
S = Σ_k a_k U_k and T_k = S − a_k U_k (T_k is independent of U_k). Then P(E_k) = W(a_k; others), where
E_k = {|T_k| < a_k}.
Equivalently, |T_k|² < a_k² ⇔ |S|² < 2a_k S·U_k ⇔ **w_k > 1/2**, where

  w_k := a_k (S·U_k)/|S|² = Re(a_k U_k / S) = ∂ arg S / ∂φ_k .

Geometrically, E_k says that the circle traced by wave k, with all the other waves frozen, goes around the origin.

## 1. Theorem and direct proof

**Theorem.** Let n ≥ 2, or let n = 1 with a_0 ≠ a_1. Then Σ_{k=0}^n P(E_k) = 1.
(When n = 1 and a_0 = a_1, the event is a boundary case of probability one. The Bessel integral gives
W = 1/2 there, so the identity still holds under the half-convention.)

**Proof.** There are two pointwise facts.

(i) **Partition of unity.** Σ_k w_k = Σ_k a_k S·U_k/|S|² = |S|²/|S|² = 1 whenever S ≠ 0. This is the
infinitesimal form of the fact that rotating all phases together rotates S rigidly: Σ_k ∂_{φ_k} arg S = 1.

(ii) **Arc lemma.** Let C be a circle of radius a centred at T, and let γ be any arc of C that avoids 0.
Then the continuous change of arg along γ satisfies |Δ_γ arg| ≤ 2π. To see this, take the two cases in turn:
- If 0 lies outside the closed disc, the disc sits inside a sector of opening less than π. So arg stays in an
  interval of length less than π.
- If 0 lies inside the disc, the disc is convex and contains 0. So arg is monotone along C with total change
  2π, and any arc changes it by an amount in [0, 2π].

Now truncate. For ε > 0 put w_k^ε = w_k·1{|S|>ε}. Then |w_k^ε| ≤ a_k/ε, so Fubini applies:
E[w_k^ε] = E[I_ε(T_k)], where

  I_ε(T) = (1/2π)∫_{φ: |T+a_k e^{iφ}|>ε} ∂_φ arg(T + a_k e^{iφ}) dφ.

The set where |T + a_k e^{iφ}| ≤ ε is an arc (it is {cos(φ−φ_0) ≥ c}). So the domain of integration is a single
arc avoiding 0, and by (ii) we get |I_ε| ≤ 1. Suppose |T| ≠ a_k and ε < ||T| − a_k|. Then the ε-disc misses C,
and I_ε(T) is the winding number of C about 0, which equals 1{|T| < a_k}. By bounded convergence,
E[w_k^ε] → P(E_k), provided P(|T_k| = a_k) = 0.

That proviso holds for n ≥ 2. Write T_k = Z + cV, with V uniform and independent of Z. If Z ≠ 0, then
|Z + cV| = a_k holds for at most two values of V. The case Z = 0 is itself a null event: it is impossible when Z
is a single vector, and otherwise it follows by the same conditioning.

Summing over k, Σ_k E[w_k^ε] = P(|S| > ε) → 1, because P(S = 0) = 0. Hence Σ_k P(E_k) = 1. ∎

As a by-product we get P(E_k) = E[w_k] = P(w_k > 1/2). This is a curious "mean equals median-type" identity for
the share w_k of |S|² carried by wave k.

**Analytic one-line proof (Bessel form).** Since J_0' = −J_1,

 Σ_k a_k J_1(a_k t) Π_{j≠k} J_0(a_j t) = −d/dt Π_j J_0(a_j t),

and therefore Σ_k W(a_k; ·) = Π J_0(0) − lim_{t→∞} Π J_0(a_j t) = 1.

**Mean motion (Weyl).** For z(t) = Σ a_k e^{i(ω_k t + φ_k)}, d arg z/dt = Σ_k ω_k w_k holds exactly. Averaging,
using equidistribution on the torus, gives mean motion Σ_k ω_k E[w_k] = Σ_k ω_k P(E_k). So P(E_k) is the share
of the mean rotation that is driven by wave k. Taking all ω_k equal to 1 recovers the identity.

**Topological reading.** Put N = Σ_k 1_{E_k}. N is the winding of arg S along the "staircase" loop on the torus
T^{n+1}: turn φ_0 once, then φ_1, and so on. The diagonal loop (all phases turning together) always has winding 1.
The two loops are homotopic in T^{n+1}, but the homotopy can cross Z = {S = 0}, which has codimension 2. So
N ≠ 1 pointwise, while the theorem says E[N] = 1.

## 2. Are the E_k disjoint? No.

The table below gives Monte Carlo estimates from 4×10^6 samples (`walk.py`; full output in `walk_output.txt`).
The columns P(E_k) and the sum are exact values from the Bessel integral. The sum of the Monte Carlo estimates of
P(E_k) and the Monte Carlo value of E[N] agree with 1 to within 5×10^-4.

| a | P(E_k) | Σ | P(N=0) | P(N=1) | P(N=2) | P(N=3) | P(E_0∩E_1) |
|---|---|---|---|---|---|---|---|
| (1,1,1) | 1/3 each | 1.000000 | .3335 | .3333 | .3332 | 0 | .1110 (=1/9?) |
| (1,.8,.3) | .69016 .23005 .07979 | 1.000000 | .2325 | .5357 | .2319 | 0 | .1586 |
| (2,1,.7,.5) | .91790 .03807 .02603 .01800 | 1.000000 | .0702 | .8628 | .0641 | .0029 | .0291 |
| (1,1,1,1) | 1/4 each | 1.000000 | .4996 | 0 | .5004 | 0 | .0834 (=1/12?) |
| (1,.85,.7,.55,.4) | see §4 | 1.000000 | .3887 | .2879 | .2585 | .0642 | .1095 |

So the E_k overlap with positive probability, and with positive probability none of them occurs. The partition
of the probability space into events with probabilities P(E_k) does not happen at the level of the events
themselves. Instead it happens through the **signed partition of unity** w_k, which satisfies Σw_k ≡ 1 and
E[w_k] = P(E_k). The w_k can be negative, so w_k cannot simply be used as selection probabilities.

Two natural disjoint candidates were tested and both fail:
- "K = argmax_k w_k" gives (.604, .264, .109, .020, .004) for the five-wave vector, against P(E_k) =
  (.409, .265, .174, .098, .054).
- "K = argmin_k |T_k|/a_k" also fails.

Both candidates are correct only for equal amplitudes, and there only by symmetry.

*Open (no conjecture):* whether there is a natural (equivariant, local) choice of disjoint events. Any partition
with these probabilities exists trivially, but no natural one was found.

*Observed, unproven:* P(E_0∩E_1) = 1/9 for (1,1,1) and 1/12 for (1,1,1,1). For (1,1,1,1), N ∈ {0,2} almost
surely.

## 3. Higher dimensions

The plain identity **fails** for d ≥ 3. Take three unit vectors in R^3: P(E_k) = P(cos∠ < −1/2) = 1/4, so the
sum is 3/4.

**Theorem (d ≥ 2, same genericity).** With U_k uniform on S^{d−1}:

  Σ_k a_k^{2−d} P(E_k) = E |S|^{2−d}.

When d = 2 the right-hand side is identically 1, which recovers the theorem of §1.

**Proof.** Replace the weight w_k by the Coulomb flux weight v_k = a_k^{d−1} (S·U_k)/|S|^d. By Gauss's law,
E[v_k | T_k] is the flux of x/|x|^d through the sphere of radius a_k centred at T_k, divided by the area of
S^{d−1}. That equals 1{E_k}. Moreover Σ_k a_k^{2−d} v_k = |S|^{2−d} pointwise.

The truncation argument is the same as in §1. The flux through any part of a sphere is a signed solid angle, and
it is bounded by 2|S^{d−1}| because each ray meets the sphere at most twice. That gives the bounded convergence
needed. ∎

Checks:
- **d = 3:** W_3(b; a) = (2/π)∫_0^∞ (sin bt − bt cos bt)/t · Π sinc(a_j t) dt and
  E|S|^{−1} = (2/π)∫Π sinc(a_j t) dt. The identity also follows from the exact derivative
  −d/dt[t Π sinc(a_j t)] = nΠsinc − Σ_k cos(a_k t)Π_{j≠k} sinc.
  - Numerically, for (1,.85,.7,.55,.4): Σ a_k^{-1}P(E_k) = 0.8091458 = E|S|^{-1}, while ΣP(E_k) = 0.6745.
  - For (1,.8,.3): the P(E_k) are 25/32, 1/8 and 1/64, with sum 0.92188.
- **d = 4, three unit vectors (exact):** Σ a^{-2}P(E_k) = 3(1/3 − √3/(4π)) = 0.5865033. The mean-value
  computation E[max(|U+V|, 1)^{-2}] gives the same value to 16 digits. Monte Carlo for the five-wave vector agrees
  within its noise (0.6780 vs 0.6786).

## 4. Artwork dataset (d = 2, a = (1.0, 0.85, 0.7, 0.55, 0.4))

The values come from two independent methods: the Bessel integral and angle quadrature with the last angle in
closed form. The methods agree to 3×10^-8.

| k | a_k | P(E_k) = W(a_k; others) |
|---|---|---|
| 0 | 1.00 | 0.4090311 |
| 1 | 0.85 | 0.2646657 |
| 2 | 0.70 | 0.1742928 |
| 3 | 0.55 | 0.0984137 |
| 4 | 0.40 | 0.0535967 |
| Σ | | 1.0000000 (Bessel: 1 − 1.3×10^-11) |

The pairwise intersection matrix and the distribution of N are in `walk_output.txt`. The machine-readable values
are in `artwork_data.json`.

Files: `walk.py` (all numerics), `artwork_data.py` (writes `artwork_data.json`), `walk_output.txt`. Everything runs
on a single core in about 1 minute.
