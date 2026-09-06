# The retreat that ends in a cusp — zero-surface-tension Hele-Shaw suction (`hele.py`)

**Setting.** A blob of viscous fluid Ω(t) between two plates, sucked out through one point at
rate |Q| (Darcy: velocity = −∇p, Δp = 0 in Ω, p = 0 on the free boundary, p ~ (Q/2π) log|z| at the
sink).  Write Ω(t) = f(D, t) with f(ζ,t) = Σ_{k=1}^K a_k(t) ζ^k the Riemann map of the unit disc
normalised at the sink (f(0) = sink).  Then the free-boundary problem is exactly the
**Polubarinova–Galin equation** (1945)

    Re[ f_t(ζ,t) · conj(ζ f'(ζ,t)) ] = Q / 2π      on |ζ| = 1 .

For a polynomial f both sides are trigonometric polynomials of degree K−1, so the equation is a
square linear system for the 2K−1 real unknowns Re a_k', Im a_k' (Im a_1' = 0 fixes the rotation
gauge): **polynomial maps stay polynomial** — the solution is exact up to the ODE integration
(RK4, step 0.002, shrinking to 0.00004 as the cusp approaches; PG residual 8e−13).

**Two conservation laws** (Richardson 1972) are the certificate:
* area A(t) = π Σ k|a_k|² satisfies A' = Q exactly (error 3e−6 at the cusp instant, from the
  final bisection step);
* the harmonic moments M_m = (1/π)∫_Ω z^m dA, m ≥ 1, are constant (max drift 7e−7 over the run,
  measured by contour quadrature ∮ z^m z̄ dz / 2πi with 4096 nodes, independent of the ODE).

**The cusp.**  Under suction the coefficients evolve so that a zero of f'(ζ) = Σ k a_k ζ^{k−1}
moves toward the unit circle; when it reaches it the map stops being univalent and the boundary
has a 3/2-power cusp with infinite velocity (v = Q/(2π|f'|) on the rim).  For the one-mode family
f = aζ + bζ^{k+1} the whole story is closed-form: the PG equation gives

    a a' + (k+1) b b' = Q/2π,      (a^{k+1} b)' = 0,

so with C = a₀^{k+1} b₀ the cusp comes when a = (k+1)|b|, i.e. a^{k+2} = (k+1) C, at which moment
the area is π(a² + (k+1)b²) with b = C/a^{k+1}: for a₀ = 1, b₀ = ε and k = 5 only **36.5 %** of the
fluid is out when ε = 0.02, 57 % when ε = 0.005, 73 % when ε = 0.001 — **no matter how small the
initial ripple, the model dies before the fluid is gone** (as ε → 0 the removed fraction → 1 only
like 1 − ((k+1)ε)^{2/(k+2)}).  This is the ill-posedness of the suction problem (Shraiman–Bensimon
1984, Howison 1986): the missing physics, surface tension, is what continues the story, and it
has to be imported from outside the model — the Hele-Shaw version of the Phil.SE question
"can this problem be solved within the field that posed it?"  (141420).

**The piece** (`render_hele.py`, seed 27, K = 7, a₁ = 1, |a_k| ≤ 0.16/k): a generic blob whose
three near-simultaneous cusps form at t = 0.8291 (|f'| zeros at radii 1.0000, 1.0142, 1.0165)
after **26.0 %** of the area has left.  Strips = fluid removed per time slice (28 slices, warm → cool),
their rims in ink; coral = the boundary at the cusp instant and the three cusp points; pale mint
+ web = the fluid still there when the description ends, with the streamlines of the flow at that
instant (images of the disc's radii under f — they pinch at the cusps where the speed is infinite)
and five equipotentials; faint ink = the same equations continued 0.09 time units past the cusp,
where the map is no longer one-to-one and the curve grows swallowtails no fluid can follow.

Seeds scanned (40): first-cusp time 0.32–0.91, area removed 6–29 %, 1–3 zeros of f' within 6 % of
the circle at the first cusp; seed 27 was the only one with three within 1.7 %.
