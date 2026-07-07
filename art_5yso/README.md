# What Forces the Real

A procedural triptych (branch `claude/eager-gates-5ysocc`, 2026-07-07) about a
single question that runs through physics, arithmetic, and calculus alike:
**what pins the zeros of a system onto a line or a curve — and why does that
confinement feel like reality itself?**

Seeded by the live front pages: MathOverflow's *"Is RH equivalent to
hyperbolicity of the shift-0 Jensen polynomials?"* and *"Isoperimetric problems
with fractal boundary"*, and Philosophy.SE's *"Is reality inherently logical?"*
and *"What Privileges the Real?"*.

Three theorems, three registers, one thread — *a zero is forbidden to leave.*

---

### 01 — The Self-Dual Circle  (4096², hero)
**Fisher zeros of the 2-D square-lattice Ising model.** Onsager's exact free
energy `-βf(v)` is a single-valued analytic function of `v = sinh(2K)`; its
partition-function zeros accumulate **exactly on the Kramers–Wannier self-dual
circle `|sinh 2K| = 1`** (verified: on `|v|=1`, `w=(1+v²)/v = 2cosθ` is real in
`[-2,2]` — the circle *is* the locus, to 2e-16). The picture is the complex-`v`
plane: warm ordered phase outside, cool disordered sea inside, the Coulomb field
of the zero-gas radiating (contours of `Im(-βf)`), the ring drawn as a gas of
zeros whose density (verified to integrate to **exactly one zero per lattice
site**) crowds at `v=±i` and *vanishes* at the pinch `v=+1` — the self-dual
point `sinh(2Kc)=1`, where the ring kisses the physical real-temperature axis.
That kiss is the phase transition: the one place the imaginary zeros touch the
real world.

### 02 — The Chalice of Hermite  (2100×2400)
**Jensen polynomials of the Riemann ξ-function.** For the Pólya sequence
`a(n) = ∫₀^∞ Φ(u) u^{2n} du / (2n)!` (moments of Riemann's Φ), the Jensen
polynomials `Σ C(d,j) a(n+j) Xⁿ` are **hyperbolic (all roots real) ⟺ the Riemann
Hypothesis.** Every row here is one such polynomial's roots (cyan) laid on its
own real axis — all real, all the time (verified). Degree grows upward; the roots
fan into the **Wigner semicircle** and, as the shift `n` climbs, settle onto the
zeros of the **Hermite** polynomials (gold) — the very spectrum a random
Hermitian matrix (GUE) would choose. Griffin–Ono–Rolen–Zagier's theorem, made
into a chalice.

### 03 — The Vault of Rolle  (2400²)
**The Gauss–Lucas cascade.** Take the (hyperbolic) polynomial whose roots are the
first 60 Riemann zeta zeros. Differentiate: by Rolle's theorem the roots stay
real and **interlace** between the old ones (verified at all 60 levels). Keep
going — 60 derivatives — and the whole spectrum flows up through a woven vault to
a single apex: the mean of the zeros (`98.760981`, exact). Once a thing is real,
every rate of its change is real too, all the way down to the one number it
forgets into.

*All fields honest and verified — see `verify.py`.*
