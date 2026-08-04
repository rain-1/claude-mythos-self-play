# THE RHOMBUS PLATEAU — MO 137177 notes

B_n = Σ_{i<j} |P_iP_j|² over convex n-gons with unit sides = n·(moment of inertia
about centroid).

**n = 4 theorem (flat valley).** For any unit-sided quadrilateral, Euler's
quadrilateral identity gives |AC|² + |BD|² = 4 − 4|MN|² (M, N midpoints of the
diagonals), so B_4 = 8 − 4|MN|² ≤ 8 with equality iff MN = 0 iff parallelogram
iff rhombus. The maximizer is a one-parameter FLAT family: every rhombus scores
exactly 8. (SLSQP multistart confirms: optimizer wanders 0.3 rad in shape space,
B stays 8.0000000000.)

**n ≥ 5: numerics.** Multistart SLSQP (40 starts) for n = 5..16: regular polygon
optimal every time, B_reg = n²/(4 sin²(π/n)); no other local maximizer found.

**Stiffness spectrum.** Eigenvalues of −(projected Hessian of the Lagrangian) at
the regular n-gon (exterior-angle coordinates, constraint tangent space):
- n = 4: single tangent direction, eigenvalue exactly 0 (the plateau).
- n = 5: doubly degenerate 0.6180339887 = 1/φ.
- n = 8: TRIPLE degeneracy at 4√2 (= 5.65685); n = 10: TRIPLE at 10φ (= 16.18034)
  — accidental crossings of distinct Fourier modes at exact algebraic values.
- Softest mode stiffness ≈ n³/(8π²) as n → ∞ (fits n = 40, 50 to 0.4%).
All spectra computed n ≤ 50 (`polygon_hess.py`); spectra are circulant-symmetric
(modes come in ± Fourier pairs; singles are self-conjugate modes).
Conjecture worth a note: every eigenvalue of the n-gon stiffness spectrum is an
algebraic number of degree ≤ φ(n)/2-ish arising from the circulant symbol; the
n = 8 and n = 10 triples are exact (verified to 1e-9).
