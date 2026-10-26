# Fair right regular n-gon prisms (static models vs. experiment)

Setup: a right prism over a regular n-gon with circumradius R = 1, apothem a = cos(π/n), length (cap-to-cap) L, half-length h = L/2.
The die has n+2 faces. "Fair" means each cap gets probability 1/(n+2).

Scripts in this directory: `prism_fair.py` (VO–S solid angles, closed form, table), `asym.py` (sympy series),
`extras.py` (bounds, monotonicity checks, barrier model), `hurst_hyde.py` (re-analysis of published pentagonal-prism data).
All numbers below were computed with mpmath at 40 digits on one core.

## 1. Solid-angle model

**Closed form for the cap's solid angle (proved).** Seen from the centroid, a cap is a regular spherical n-gon. Let β be the
angle between the axis and the direction to an edge midpoint, so cos β = h/√(h²+a²). Napier's rule on the right spherical
triangle (centre, edge midpoint, vertex) gives cos(α/2) = sin(π/n)·cos β, where α is the polygon's vertex angle. By Girard,
Ω = nα − (n−2)π, so

  Ω_cap(h) = 2π − 2n·arcsin( sin(π/n) · h/√(h²+a²) ).

This matches the Van Oosterom–Strackee triangle-fan sum to 1e-40. The faces' solid angles add up to 4π to 1e-40.
The same formula reproduces the "CSA Base" column of Hurst–Hyde, Table 2 (see §2) to 4 digits.

**Fair length in closed form (proved).** Setting Ω_cap = 4π/(n+2) reduces the condition to sin(π/n)·cos β = sin(π/(n+2)). Then

  L*(n) = 2 cos(π/n) sin(π/(n+2)) / √( sin²(π/n) − sin²(π/(n+2)) )
        = 2 cos(π/n) sin(π/(n+2)) / √( sin(2π(n+1)/(n(n+2))) · sin(2π/(n(n+2))) ).

Special values: L*(4) = √2 (the cube, a sanity check) and L*(6) = 2^{1/4}·√3.
Root-finding with the VO–S formula agrees with the closed form to better than 1e-38 for every n in the table.

| n | L*(n) (R=1) | L*/√n | n/√(n+1) (circum-disc) | L*/(edge) | insphere/Gibbs-fair L=2cos(π/n) |
|---|---|---|---|---|---|
| 3 | 0.9241763718304 | 0.533573477055 | 1.5 | 0.53357348 | 1.0 |
| 4 | 1.414213562373 | 0.7071067811865 | 1.788854382 | 1.0 | 1.4142136 |
| 5 | 1.770453249536 | 0.7917707633894 | 2.041241452 | 1.5060375 | 1.618034 |
| 6 | 2.059767143907 | 0.8408964152537 | 2.267786838 | 2.0597671 | 1.7320508 |
| 7 | 2.308425068924 | 0.8725026646573 | 2.474873734 | 2.6601885 | 1.8019377 |
| 8 | 2.529495134937 | 0.894311581446 | 2.666666667 | 3.3049447 | 1.8477591 |
| 9 | 2.730440269834 | 0.9101467566113 | 2.846049894 | 3.9916366 | 1.8793852 |
| 10 | 2.915936671042 | 0.9221001393301 | 3.015113446 | 4.7180846 | 1.902113 |
| 11 | 3.089118278076 | 0.9314042055824 | 3.175426481 | 5.4823594 | 1.9189859 |
| 12 | 3.252195671138 | 0.9388280230945 | 3.328201177 | 6.2827596 | 1.9318517 |
| 13 | 3.406792098215 | 0.9448741226891 | 3.474396145 | 7.1177792 | 1.9418836 |
| 14 | 3.554138761626 | 0.9498835393611 | 3.614784456 | 7.9860773 | 1.9498558 |
| 15 | 3.695194672563 | 0.9540951618554 | 3.75 | 8.8864524 | 1.9562952 |
| 16 | 3.830723581687 | 0.9576808954217 | 3.880570001 | 9.8178206 | 1.9615706 |
| 17 | 3.961345246635 | 0.9607673453773 | 4.006938427 | 10.779199 | 1.9659462 |
| 18 | 4.087570704848 | 0.9634496546592 | 4.12948321 | 11.769691 | 1.9696155 |
| 19 | 4.209827217237 | 0.9658006005107 | 4.248529157 | 12.788474 | 1.9727226 |
| 20 | 4.328476333478 | 0.9678767320657 | 4.364357805 | 13.834791 | 1.9753767 |
| 21 | 4.4438272524 | 0.9697226075919 | 4.477215043 | 14.907943 | 1.9776617 |
| 22 | 4.556146887218 | 0.9713737801764 | 4.587317109 | 16.00728 | 1.9796429 |
| 23 | 4.665667574092 | 0.9728589403968 | 4.69485534 | 17.132196 | 1.9813719 |
| 24 | 4.772593063318 | 0.9742014795897 | 4.8 | 18.282128 | 1.9828897 |
| 25 | 4.877103237837 | 0.9754206475675 | 4.902903378 | 19.456544 | 1.9842294 |
| 26 | 4.979357874132 | 0.9765324217447 | 5.003702333 | 20.654949 | 1.9854177 |
| 27 | 5.079499672608 | 0.9775501677763 | 5.102520386 | 21.876872 | 1.9864767 |
| 28 | 5.177656723655 | 0.9784851474894 | 5.199469469 | 23.121873 | 1.9874244 |
| 29 | 5.273944532733 | 0.9793469135329 | 5.294651389 | 24.389532 | 1.9882759 |
| 30 | 5.368467697236 | 0.9801436190046 | 5.388159061 | 25.679454 | 1.9890438 |
| 50 | 6.992187883234 | 0.9888446935131 | 7.00140042 | 55.678691 | 1.9960535 |
| 100 | 9.947098456078 | 0.9947098456078 | 9.950371902 | 158.33903 | 1.9990131 |
| 1000 | 31.6068730793 | 0.9994970864644 | 31.60697706 | 5030.3984 | 1.9999901 |


(The edge length is 2 sin(π/n). For the d7, i.e. n = 5: L*/R = 1.770453249536 and L*/edge = 1.5060.)

**Which disc gives L = n/√(n+1)?** Take a disc of radius r at distance h. Its solid angle is 2π(1 − h/√(h²+r²)). Setting
this to 4π/(n+2) gives h/√(h²+r²) = n/(n+2), so L = 2h = n·r/√(n+1). The formula L = n/√(n+1) is therefore the
**circumradius disc** (r = R = 1). The apothem disc gives n·cos(π/n)/√(n+1).
- *Proved:* n·cos(π/n)/√(n+1) < L*(n) < n/√(n+1). The polygon contains the inscribed disc and lies inside the circumscribed disc,
  so the solid angles are nested. Each solid angle also decreases strictly in h.
- *Proved (series):* the **equal-area disc**, r_eff² = (n/2π)·sin(2π/n), is far better. L*·√(n+1)/n = r_eff + O(n⁻⁵).
  Exactly, (r_eff·n/√(n+1) − L*)/√n = (π⁴/15)·n⁻⁵·(2 − 7/n) + O(n⁻⁷). The reason is that a regular n-gon and its
  equal-area disc differ in polar moment only at O(n⁻⁴).

**Asymptotic expansion (derived exactly with sympy from the closed form, not fitted).** With x = 1/n, L*²/n is analytic at x = 0, and

  L*(n)/√n = 1 − 1/(2n) + (3/8 − π²/3)/n² + (π²/6 − 5/16)/n³ + (π⁴/90 − π²/8 + 35/128)/n⁴
             + (5π²/48 − 5π⁴/36 − 63/256)/n⁵ + O(n⁻⁶).

So c0 = 1 and c1 = −1/2. The first polygon correction is −π²/(3n²); it is the r_eff correction
r_eff = 1 − π²/(3n²) + π⁴/(90n⁴) + …. Equivalent forms:
- L*·√(n+1)/n = 1 − π²/(3n²) + π⁴/(90n⁴) + O(n⁻⁵), the same as r_eff up to O(n⁻⁵).
- L*/√(n+1) = 1 − 1/n + (1 − π²/3)/n² + (π²/3 − 1)/n³ + ….
- L*/√(n+2) = 1 − 3/(2n) + (19/8 − π²/3)/n² + ….

## 2. Literature: measured fair prism lengths (only what I actually read)

| Source | Die | Measured or fitted "fair" length, converted to L/R (R = circumradius) | Solid-angle L*/R |
|---|---|---|---|
| Hurst & Hyde, arXiv:2609.01643 (Aug 2026), https://arxiv.org/abs/2609.01643 | pentagonal prism (d7). 11 dice (9 printed sizes + 2 commercial), dice-tower drops onto hard laminate, 41,068 rolls | Linear interpolation of their Table 1 between die F (h/r = 1.5636, base frequency 0.2956) and die 14 (1.6946, 0.2216) puts the 2/7 crossing at **≈ 1.581**. Their fitted model (a, p) = (1.46, 2.33) gives **1.583** (my computation) | 1.7705 |
| Bereuter, US Patent 4,900,034 (1990), https://patents.google.com/patent/US4900034A/en | pentagonal prism (d7), hard plastic, rolled on foam-backed felt | Patent text: "fits precisely in a circle 1 inch in diameter … the length of the prism is 0.753 inch", so **L/R = 1.506** | 1.7705 |
| Taniguchi & Uehara, arXiv:1810.12108 (2018), https://arxiv.org/abs/1810.12108 | 11-gon prism (d13), R = 10 mm, 500 tosses per height from 20 cm onto a wooden desk | Linear fit gives a fair height of 20.255 mm; they recommend **20.3 mm, so L/R ≈ 2.03**. Cylinders (R = 1): 21.011 mm. Cylinders of radius 0.9595: 20.160 mm | 3.0891 |

Details from these papers:
- *Hurst–Hyde.* Their model is p_base ∝ g/h^p and p_side ∝ (1−g)/(a·r)^p, where g is the centroid-solid-angle (CSA) proportion, a = 1.46 and p = 2.33. It fits all 11 dice with |Z| < 2 (ΣZ² = 13.9 on 9 degrees of freedom). The pure CSA model is rejected, with |Z| up to 37. They attribute the gap to an "energy barrier window": as the bouncing die loses energy, base→side transitions remain possible after side→base ones stop. Their die F was *designed* to be fair, yet its observed base frequency was 0.2956 against the 2/7 = 0.2857 target. An earlier square-prism version of the model (Hurst & Tandiman 2020, IJMMMAS 14, 95–101; cited by them, not read) used p = 2.427.
- *Taniguchi–Uehara.* The Yong–Mahadevan "dynamic" coin model, P_edge = 1 − (2/π)·arccos(t/√(1+t²)), gives fair thickness t = cot(π/N) for an N-faced die (4.057 for N = 13). They report it "does not fit experiments for n > 4"; the measured value is ≈ 2.03. They conjecture, with support for n = 3, 4, 5, 11, that P_caps(inscribed cylinder) < P_caps(n-prism) < P_caps(circumscribed cylinder) at equal height. Under the solid-angle model this is my proved nesting bound. They also report a commercial d5 (triangular prism) giving 51 caps in 100 tosses against an expected 40, and a d7 giving 28 against an expected 28.6.
- *Riemer, Stoyan & Obreschkow*, "Cuboidal dice and Gibbs distributions", Metrika 2013, https://arxiv.org/abs/1302.3925 (read via ar5iv). The solid-angle model contradicts cuboid data. They replace it with p_i ∝ exp(−β·E_i), where E_i is the normalized centroid height on face i. Fitted β is about 2.7–5.6 depending on the surface; typical values lie between 1 and 10. The paper says nothing about prisms or odd dice.
- I did **not** locate or read a paper titled "the trouble with d5", or Kapitaniak's dice-dynamics paper's numbers. So nothing is reported from them here.

**Observation:** every measured fair prism is *shorter* than the solid-angle prediction: by about 11–15% for n = 5 and about 34% for n = 11. Real dice under-weight the caps relative to the static solid angle, consistent with rolling ("rolling log", Taniguchi–Uehara) and with the energy-window explanation.

## 3. Alternative static models

**(a) Gibbs / centroid-height model (Riemer et al.)**, p_i ∝ exp(−β·d_i), where d_i is the distance from the centroid to face i.
*Proved:* for every β > 0 a prism is fair exactly when all the d_i are equal, i.e. h = a, so **L_G = 2cos(π/n)**. The answer is independent of β; such a prism has an insphere centred at the centroid. In general, any polyhedron with an insphere centred at its centroid is fair under every Gibbs model. Values: n=4 gives √2 (the cube); n=5 gives **φ = 1.618…** (the golden ratio); n=11 gives 1.919.
These are much closer to the measurements (d7: 1.58 / 1.51; d13: 2.03) than the solid-angle values (1.77; 3.09).
As n → ∞, L_G → 2 while L*_solid ~ √n: the two models disagree on the scaling exponent.

**(b) Equal minimum tipping barrier** (a crude toy model; my own). Define a face's barrier as min over its edges of (distance from centroid to edge − distance from centroid to face). Equating the cap and side barriers gives √(h²+a²) − h = 1 − a, so **L_B = (2a−1)/(1−a)** for n ≥ 4 and L_B = 1 for n = 3. Values: n=4 gives √2, n=5 gives 1+√5 = 3.236, n=6 gives 5.464, n=10 gives 18.43, and L_B ~ 2n²/π². This model goes the *wrong* way compared with experiment (it predicts longer prisms), so equal barriers are not a fairness criterion.

## 4. Statements

- **Proved:** the closed form for L*(n) above; the apothem-disc < L* < circumradius-disc bounds; L*/√n → 1 with the exact series above; the error of the equal-area disc approximation is O(n^{-4.5}) in L*; the Gibbs-model fair length is 2cos(π/n) for all β.
- **Numerically observed** (dense real-n grid on [3, 10^6.1], 40-digit arithmetic, not proved): L*/√n, L*/√(n+1), L*/√(n+2) and L*·√(n+1)/n are all strictly increasing in n and tend to 1. From the series, L*·√(n+1)/n increases to 1 like 1 − π²/(3n²).
- **Coincidence noted:** at n = 4 all three models (solid angle, Gibbs, barrier) give L = √2, as symmetry requires.
