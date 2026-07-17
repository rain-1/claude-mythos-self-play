# Verification — What the Line Won't Tell (art_1zz8)

Hero linkage: ground g=2.359240, crank a=1.541658, coupler b=2.378095, follower c=1.920212, coupler point mu=0.334059-0.268486j
Grashof class: ('crank-rocker', np.float64(-0.35969908086881475))

## 1. Roberts–Chebyshev cognates (the hero's theorem)

- Roberts point O_C = O_A + mu(O_B−O_A) = 0.788126-0.633422j — pivot triangle
  O_A O_B O_C is similar to coupler triangle A B P **by construction, exactly**.
- Cognate 2 rigidity along the whole motion: coupler-length error 1.11e-15; coupler-point identity error 2.29e-15
- Cognate 3 rigidity: coupler-length error 2.22e-15; coupler-point identity error 1.33e-15
- cognate 2 simulated INDEPENDENTLY as its own four-bar (g=1.0111, a=1.0192, b=0.6607, c=0.8230): every traced point lies on the original curve to max 4.56e-05 (sampling-limited; scales as n^-1/2).
- cognate 3 simulated INDEPENDENTLY as its own four-bar (g=1.6940, a=1.7075, b=1.3788, c=1.1070): every traced point lies on the original curve to max 4.57e-05 (sampling-limited; scales as n^-1/2).
- Machine classes: original=crank-rocker, cognate2=double-rocker(Grashof), cognate3=rocker-crank

## 2. The coupler curve is a tricircular sextic

- Implicit fit over 4000 curve points: smallest singular value at degree 6 = 9.48e-17 (a degree-6 algebraic curve fits to machine precision); at degree 5 = 2.49e-03 (no quintic fits — ratio 2.6e+13).
- Degree-6 leading form proportional to (x²+y²)³: relative residual 2.68e-15 (triple circularity — the signature of four-bar coupler curves).

## 3. The three clocks (dwell measures) disagree

- Total variation per cycle: |d alpha| = 6.283185 (= 2π: 1.000000 turns), |d gamma| = 3.949996 (0.6287 turns), |d beta| = 2.958147 (0.4708 turns)
- Pointwise share of the three normalized dwell measures ranges over [0.000, 0.579] (equal share would be 0.333 everywhere): the same point-set carries three genuinely different clocks.

## 4. Configuration-space topology across the Grashof gates

- Gates (change points): a1* = g+c−b = 1.901357, a2* = c+b−g = 1.939067, a3* = g+b−c = 2.817123
  - a < a1* (a=1.6000): 2 component(s), winding numbers (w_alpha, w_gamma) = [(-1, 0), (-1, 0)]
  - a = a1* (a=1.9014): 1 component(s), winding numbers (w_alpha, w_gamma) = [(0, 0)]
  - a1* < a < a2* (a=1.9200): 1 component(s), winding numbers (w_alpha, w_gamma) = [(0, 0)]
  - a = a2* (a=1.9391): 1 component(s), winding numbers (w_alpha, w_gamma) = [(0, 0)]
  - a2* < a < a3* (a=2.3000): 2 component(s), winding numbers (w_alpha, w_gamma) = [(0, -1), (0, 1)]
  - a = a3* (a=2.8171): 2 component(s), winding numbers (w_alpha, w_gamma) = [(0, -1), (0, 1)]
  - a > a3* (a=3.0500): 1 component(s), winding numbers (w_alpha, w_gamma) = [(0, 0)]

Interpretation: below a1* the machine's world is two disjoint circles each
winding once in the crank direction (the crank spins; two mirror assemblies).
Between a1* and a2* possibility is one contractible loop (everything rocks).
Between a2* and a3* it is two circles winding once in the FOLLOWER direction —
with opposite orientations. Beyond a3* possibility closes again into one loop.
At each gate the worlds meet at folded (collinear) configurations.
