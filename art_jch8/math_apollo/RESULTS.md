# MO 516405 — second adjacency eigenvalue of the Apollonian network G_m

Code: `apollo.py` (m ≤ 13), `apollo2.py` (vectorised build, sparse `eigsh`, m = 14, 15 with 7.2M / 21.5M vertices).

| m | N_m | θ1 | θ2 | θ3 = θ4 | θ2/2^{m/2} | θ2 − 2^{(m+1)/2} |
|---|---|---|---|---|---|---|
| 9 | 29,527 | 42.0281 | 35.7165 | 33.9663 | 1.5785 | 3.7165 |
| 10 | 88,576 | 57.9495 | 48.8944 | 47.0619 | 1.5280 | 3.6396 |
| 11 | 265,723 | 80.7236 | 67.5021 | 65.7052 | 1.4916 | 3.5021 |
| 12 | 797,164 | 113.0791 | 93.8843 | 92.1494 | 1.4669 | 3.3746 |
| 13 | 2,391,487 | 158.9238 | 131.2745 | 129.5967 | 1.4504 | 3.2745 |
| 14 | 7,174,456 | 223.8118 | 184.2194 | 182.5870 | 1.4392 | 3.2001 |
| 15 | 21,523,363 | 315.6120 | 259.1458 | 257.5477 | 1.4316 | 3.1458 |

* For m ≥ 7, θ2 is **simple** and its eigenvector is symmetric (equal on a, b, c: ±0.407 at m = 15, tiny on o);
  θ3 = θ4 is the 2-dimensional (a,b,c)-representation.
* The offset d_m = θ2 − 2^{(m+1)/2} decreases with successive differences shrinking by ≈ 0.72 ≈ 2^{-1/2}.
  Richardson fit d_m ≈ c + A·2^{-m/2} + B·2^{-m} on the last 3–6 points gives c = 3.009, 3.008, 3.006, 2.997.

**Answer (numerical): yes, θ2/2^{m/2} → √2.**

**Conjecture.** θ2(G_m) = 2^{(m+1)/2} + 3 + O(2^{-m/2}) and θ3(G_m) = θ4(G_m) = 2^{(m+1)/2} + 3/2 + o(1)
(θ3 offsets 1.597, 1.568, 1.548 for m = 13, 14, 15). Heuristic: the top modes after θ1 are hub modes on the fans
of a, b, c (degree 2^{m+1}+1); a fan K_1 + P_d alone gives √d + 1 + o(1), and the hub–hub triangle and the shared
neighbour o shift the symmetric combination up and the other two less. What would decide it: a renormalisation of the
hub mode across levels (the fan of a at level m is two fans at level m−1 glued along the edge a–child).
