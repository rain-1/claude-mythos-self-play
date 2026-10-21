# Triangles containing the centre (MO 425785)

n i.i.d. uniform points on a circle centred at O; X = number of the C(n,3) triangles that contain O.
Files: `tri.py` (brute force plus transfer matrix, writes `dist.json`), `analyze.py`, `an2.py`, `an3.py` (moments, support, limit checks).
`dist.json` = {n: {X: count}}, where count = 2^{n-1}·P(X = x), for **3 ≤ n ≤ 60**. It reproduces the MO table for n = 3..9 exactly. For n ≤ 16 it was also checked against brute force using the k_i formula.

## 1. Why 2^{n-1}: X as a function of a sign vector

Write θ_j = φ_j + π·[s_j = −1] with φ_j ∈ [0,π) and s_j ∈ {±1}. Under the uniform law, the φ_j are i.i.d. uniform on [0,π) and the s_j are independent fair signs. Almost surely the φ_j are distinct, so relabel them so that φ_1 < … < φ_n.

**Lemma.** Let k_i be the number of other points in the open half-circle (θ_i, θ_i+π). Then
k_i = #{j>i : s_j = s_i} + #{j<i : s_j ≠ s_i}.
Proof: check the four cases of (s_i, s_j).

A triangle fails to contain O iff its vertices lie in a half-circle. In that case exactly one vertex sees the other two counter-clockwise within angle π. So X = C(n,3) − Σ_i C(k_i,2), and this depends only on s. Two further facts:
- s and −s give the same configuration rotated by π.
- Every sign vector has probability 2^{−n}.

So P(X = x) = #{s : s_1 = +1, X(s) = x} / 2^{n−1}, for every choice of the diameters.

**Walk form (the key identity).** Let P_t = s_1+…+s_t and S = P_n, and define
W_t = (s_{t+1}+…+s_n) − (s_1+…+s_t) = S − 2P_t.
Geometrically, W_t is (number of points on one side) − (number on the other side) for a line through O lying between diameters t and t+1. So Q := Σ_{t=0}^{n−1} W_t² is the sum, over the n combinatorially distinct lines through O, of the squared imbalance. Then

**X = (n³ + 2n)/24 − Q/8.**

Proof: number the 2n slots around the circle as φ_1..φ_n, φ_1+π..φ_n+π, and let c_u = ±1 mark whether slot u is occupied. Then c_{u+n} = −c_u. For an occupied slot t, k_t = (n + W_t)/2, where W_t is the sum of the c's over the next n slots. Also Σ k = C(n,2), and the squares at antipodal slots agree. Together these give Σ k_i² = (n³ − 2n² + Q)/4. Finally X = C(n,3) − (Σk² − Σk)/2.

Consequences:
- **Maximum.** For odd n, every W_t is odd, so Q ≥ n and X_max = (n³−n)/24. This is attained only by the alternating, "regular" configuration (count 1).
- For even n, W_t alternates between 0 and ±2, so Q ≥ 2n and X_max = (n³−4n)/24. This has count 2^{n/2}, so P = 2^{1−n/2}.
- **Minimum.** X = 0 iff all points lie in a half-circle. The count is n, which is Wendel's theorem.
- **Parity (proved).** For even n, every attainable X has X ≡ X_max (mod 2). The reason: V = W/2 alternates in parity, and odd squares are ≡ 1 (mod 8), so ΣV² ≡ n/2 (mod 4). This explains the zero at every other entry in the even rows.

**Multiples of n.** Rotating the labelling by one diameter sends s ↦ (s_2,…,s_n,−s_1). This generates a cyclic group of order n acting on the classes {±s}, and it preserves X. The count for each x is therefore a sum of orbit sizes d | n.
- An entry is not ≡ 0 (mod n) exactly when some configuration with that X has rotational symmetry.
- For odd n the final 1 is the alternating configuration, which is fixed by the whole group.
- For n = 9, the entry 30 at X = 27 = 3·3·3 comes from an orbit of size 3: three clusters of 3 points, which has 3-fold symmetry.
- For even n, the antipodally symmetric configurations give the counts at the maximum, 4, 8, 16, …, and so on.

## 2. Exact distribution: a transfer matrix (this is the recursion)

Σ_{s∈{±1}^n} q^{Q(s)} = Σ_{S≡n (2)} [(D A)^n]_{S,−S}, where:
- A is the adjacency matrix of the steps ±2 on {−n,…,n};
- D = diag(q^{W²}).

In words, it counts walks with steps ±2 from S to −S, weighted by q raised to the sum of squared positions. Then G_n(q) := Σ_x count(x) q^x = ½ Σ_s q^{((n³+2n)−3Q)/24}. Polynomial dynamic programming gives all n ≤ 60 in about 4 minutes on one core. It needs about O(n⁶) operations, and int64 is exact up to n = 62.

Rows (counts out of 2^{n−1}):
```
10: 10 0 0 0 0 0 0 0 10 0 0 0 0 0 20 0 0 0 20 0 30 0 0 0 30 0 20 0 30 0 60 0 50 0 40 0 80 0 80 0 32
11: 11 0 0 0 0 0 0 0 0 11 0 0 0 0 0 0 22 0 0 0 0 22 0 11 22 11 0 0 33 0 0 22 11 33 0 0 66 22 11 33 44 55 11 0 66 66 11 44 110 66 22 55 77 44 11 1
12: 12 0 0 0 0 0 0 0 0 0 12 0 0 0 0 0 0 0 24 0 0 0 0 0 24 0 12 0 24 0 24 0 36 0 0 0 24 0 60 0 0 0 72 0 60 0 36 0 120 0 72 0 72 0 108 0 96 0 144 0 204 0 156 0 160 0 240 0 192 0 64
```

## 3. Moments (exact)

E[W_t] = 0 and E[W_t²] = n, so E Q = n² and **E X = C(n,3)/4**.

For Rademacher sums, E[W_t² W_u²] = n² + 2c² − 2n, with c = n − 2|t−u|. Hence:
- Var Q = Σ_{t,u} (2(n−2|t−u|)² − 2n);
- **Var X = Var Q / 64 = n²(n−1)(n−2)/96**. This is proved, and it agrees with the data for all n ≤ 60.

Higher cumulants, fitted as polynomials and matching every n ≤ 60:
- κ₃(X) = −n²(n−1)(n−2)(n−4)(2n−1)/960
- κ₄(X) = n²(n−1)(n−2)(17n⁴ − 187n³ + 553n² − 452n + 16)/26880

## 4. Limit law: Brownian hitting time

Scale P_{⌊nu⌋} ≈ √n·B_u. Then W ≈ √n·(B_1 − 2B_u), and by Donsker's theorem

**T_n := Q/n² = 8((n³+2n)/24 − X)/n² ⇒ T = ∫_0^1 (2B_u − B_1)² du.**

The process Y_u = 2B_u − B_1 is Gaussian with covariance 1 − 2|u−v|, and it is antiperiodic (Y_1 = −Y_0). Its covariance operator is the inverse of −¼ d²/du² with antiperiodic boundary conditions. The eigenvalues are 4/(π²m²) for m odd, each with multiplicity 2. Therefore

E e^{−λT} = Π_{k≥0} (1 + 8λ/(π²(2k+1)²))^{−1} = **sech √(2λ)**.

So T has the law of the **first exit time of standard Brownian motion from (−1,1)**, with E T = 1, Var T = 2/3, κ₃ = 16/15, κ₄ = 272/105. Equivalently,

X = n³/24 + n/12 − (n²/8)·T_n.

The fluctuations are of order n², not n³. The exact cumulants above, scaled by (8/n²)^k, converge to 2/3, 16/15 and 272/105. The numerical Laplace transform at n = 60 is within about 4% of sech √(2λ) for λ ≤ 5, with an O(1/n) error.

## 5. Structure of G_n(q): theorems vs conjectures

- No product or closed formula: G_n factors trivially for odd n ≤ 15 and for n ≡ 2 (mod 4) up to 14 (sympy). The transfer matrix is the natural recursion. Σ_n x^n G_n is not a single continued fraction, because the walk's endpoints are tied by W_n = −W_0.
- **CONJECTURE A** (verified for n ≡ 0 (mod 4), n ≤ 60). (1+q²)^{n/4} divides G_n(q) exactly: no higher power divides it, and the quotient has some negative coefficients. Equivalently, Σ_s i^{X} X^j = 0 for j < n/4. No proof yet. One idea is a sign-reversing involution on the even-indexed positions where V_t ≡ 2 (mod 4).
- **Support** (data for n ≤ 60). The support sizes are:
  - odd n = 3, 5, …: 2, 4, 8, 16, 30, 53, 85, 134, 196, 276, 376, 495, …
  - even n = 4, 6, …: 2, 4, 8, 14, 25, 42, 63, 92, 130, 177, 233, …

  **CONJECTURE B.** For odd n ≥ 15, every integer in [L(n), (n³−n)/24] is attained. For even n, every integer of the right parity in [L(n), (n³−4n)/24] is attained. Here L(n) = (largest missing value)+1 grows like about c·n², with c ≈ 1/3 for odd n and c ≈ 0.27 for even n (L(59) = 1207, L(60) = 987). All the gaps sit at small X, near the "all in a half-circle" end. Smallest values: 0, n−2, 2(n−3), 3(n−4), …. The value abc (a+b+c = n) comes from three tight clusters.
