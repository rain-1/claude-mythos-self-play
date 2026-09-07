# Rain on a pond — the Cauchy–Poisson problem with surface tension (*The Rings That Never Came Home*)

Linear water waves in real millimetres: g = 9810 mm/s², σ/ρ = 72 000 mm³/s², ν = 1 mm²/s.
A drop is an initial dimple η₀ = −A exp(−r²/2b²) with zero initial velocity (b = 2.5–7 mm);
its evolution is

    η̂(k, t) = η̂₀(k) cos(ω(k) t) e^{−2νk²t},     ω² = g k + (σ/ρ) k³.

Several drops at different positions and ages superpose in Fourier space: the whole pond is
ONE inverse FFT (5120² for the final).

## Certificates (`rain.py`, `rain_2560_cert.json`)

* **Energy.** With ν = 0 the linear energy Σ_k (g + σk²/ρ)(|η̂|² + |η̂₀ sin ωt|²)/2 is constant in
  time; it is, to six digits (9.06419e10 at t = 0.5, 1.0, 1.5 s for the unit drop).
* **Group-velocity minimum.** c_g(k) = (g + 3σk²/ρ)/(2ω) has a minimum of **177.1 mm/s at
  wavelength 43.3 mm** (phase-velocity minimum 230.6 mm/s at 17.0 mm). No part of the
  disturbance travels slower, so at age t the drop has a calm heart of radius c_g,min·t whose
  edge is a caustic (a fold of the stationary-phase map k ↦ c_g(k)); the loudest ring sits just
  outside it (measured 194 mm at t = 1 s against 177 mm: the Airy shift of a fold caustic).
* **Capillary ripples run ahead** (c_g → ∞ as k → ∞) and are the first to die (e^{−2νk²t}).

## What the picture draws

Crests warm, troughs cool; the second pigment of each family (lemon / lavender) is weighted by
the local wave number |∇η|/|η| so the capillary ripples ahead of each system read as a
different fabric from the gravity rings behind. Coral hairline = the circle r = c_g,min·t of
each drop; coral bead = where it fell. Nothing else is drawn: every ring is the computed field.

The rings leave and do not return — the wake in its third sense, the vigil. Seven drops, seed 11,
ages 0.2–1.5 s, on a 1 m pond.
