# The Kelvin ship-wave pattern — what the field certifies (*The Angle Every Boat Shares*)

## Model (`wake.py`)

Steady linear deep-water response to a Gaussian pressure patch of size a moving at speed U, in
units g = U = 1 (transverse wavelength 2π):

    η̂(k) = − p̂(k) k / ( k + τk³ − (k·û)² + 2iμ (k·û) ),   p̂ = 2πa² e^{−a²k²/2},

τ = 0 (no capillarity), Rayleigh damping μ = 0.016 selecting the downstream waves and fading
them before the periodic box wraps (box 3.2L × 1.6L, only the first L shown). One FFT.
Froude number Fr = U/√(g a) = 1/√a; the hero uses a = 1 (Fr = 1); the two smaller boats are the
same field rescaled by 0.42 and 0.30 (a wake at speed U' is the Fr-1 pattern dilated by (U'/U)²).

## Certificates (`wake_hero_4096_cert.json`)

1. **The wedge emerges.** RMS amplitude along rays from the source over 0.35L–0.9L: peak at
   18.6°, half-amplitude edge at 20.3°, and the amplitude outside collapses:
   RMS(22°)/RMS(19.47°) = 0.14, RMS(25°)/RMS(19.47°) = 0.006, RMS(30°) = 0.0009 of it.
   Nothing in the code knows arcsin(1/3); the coral lines are drawn at that angle *after* the
   field has been computed, and the beads sit on the loudest points of the field.
2. **Kelvin's crest curves ride the ridges.** x = A cos t (1 + sin²t), y = A sin t cos²t with
   A = 2πn − c; one phase constant per branch fitted for the whole family: transverse c = 2.173
   (contrast, mean on crest / RMS = 0.70) and diverging c = 1.309 (0.67, for |t| < 0.95: beyond
   that the wave number 1/cos²t > 2.6 is not excited by an a = 1 patch — the fit there is noise,
   and the ink stops where the waves stop). The two phases differ by 0.86 ≈ the π/4 + π/4
   stationary-phase shifts of a fold on each side of the cusp.
3. **The loudest angle narrows at high Froude number** (Rabaud & Moisy 2013; Darmon,
   Benzaquen, Raphaël 2014), measured from the field (`frsweep.py`, N = 2048):

   | Fr | 0.71 | 0.85 | 1.00 | 1.20 | 1.41 | 1.69 | 2.00 | 2.36 | 2.89 | 3.54 |
   |---|---|---|---|---|---|---|---|---|---|---|
   | loudest angle | 16.6° | 18.5° | 18.5° | 18.2° | 17.9° | 17.75° | 13.6° | 11.1° | 9.6° | 8.05° |
   | half-amplitude edge | 20.75° | 20.9° | 20.55° | 20.2° | 19.95° | 19.8° | 19.5° | 18.9° | 15.55° | 13.15° |
   | tan(peak)·Fr | | | | | | | 0.484 | 0.462 | 0.488 | 0.500 |

   **Law (derived, then checked):** the patch excites wavenumbers up to k ≈ 1/a; the diverging
   wave with propagation angle θ has k = g/(U² cos²θ), so the loudest wave has cos θ ≈ 1/Fr, and
   Kelvin's construction puts it on the ray tan ψ = sinθ cosθ/(1 + sin²θ) → **tan ψ_peak ≈ 1/(2 Fr)**
   for Fr ≫ 1. Measured tan(ψ)·Fr = 0.46–0.50 for Fr = 2–3.5. Below Fr ≈ 1.7 the whole wedge is
   excited and the loudest angle is the Kelvin cusp itself (the caustic, 18–18.5° with the Airy
   shift inward from 19.47°). The half-amplitude *edge* stays at the Kelvin angle until Fr ≈ 2.4:
   the wedge does not narrow, the loudness inside it does — the 2013 controversy in one table.

## Composition

Three boats on parallel courses (up-left), wakes trailing at 27° across the sheet, sizes
1 : 0.42 : 0.30 — the theorem is the picture: three wedges, one angle. Crests apricot →
blush and troughs aqua → cornflower as the local wave direction turns from transverse to
diverging (the direction is read from ∇η, not assumed); density = |η| with a soft knee and a
mild downstream gain (u^0.6) against the honest x^{−1/2} decay; ink = every third crest curve
of each branch; coral = the cusp beads and the two lines at arcsin(1/3) per boat.

Seed: Philosophy.SE 141355 (did Thales mean *waves* by *water*?) — one answer: whatever moves
through water is told by the same angle.
