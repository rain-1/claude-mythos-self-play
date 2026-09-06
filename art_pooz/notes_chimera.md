# Chimera states — what was measured, what failed, what worked (`chimera2d.py`, `kb1d.py`)

Model: identical phase oscillators, nonlocal coupling with a phase lag,

    θ_t(x) = ω − ∫ G(x−y) sin(θ(x) − θ(y) + α) dy,      ∫G = 1,

on a 2-D torus / no-flux square (`chimera2d.py`, FFT convolution, RK2, dt = 0.05) or a ring
(`kb1d.py`).  Coupling strength only rescales time, so the parameters are α, the kernel shape and
its width R relative to the domain.  The **coherence certificate** used throughout is the mean
frequency field ⟨θ̇⟩ over a long window: locked oscillators share one frequency Ω exactly (a
plateau in the histogram); drifting ones do not.  (The instantaneous local order |Z| is NOT a
coherence measure when the pattern's wavelength is shorter than the kernel — a tightly wound,
perfectly locked spiral has small |Z| everywhere.  This misled the first prototype.)

## 1-D: the Kuramoto–Battogtokh ring chimera (the piece)
Kuramoto & Battogtokh (2002) parameters: ring of length 1, G(x) = (κ/2) e^{−κ|x|}, κ = 4,
α = 1.457, N = 512, their initial condition θ₀ = 6 e^{−30(x−½)²}·U(−½,½), T = 3000, mean frequency
over the last 800 units.  Result: a plateau at Ω = −0.7693 holding 26.0 % of the ring (|⟨θ̇⟩−Ω| <
0.005), the remaining oscillators drifting with mean frequencies rising in an arch to −0.300 at
the antipode; local order |Z| ≈ 0.70 in both arcs (the drift is not a lack of field).  The carpet
piece shows the last 60 time units (7.3 rotations of the locked arc): horizontal bands with ink
wavefronts where the oscillators agree, vertical threads of individual rhythm where they don't,
slowing to long streaks toward the coral boundary as their frequency approaches Ω.

## 2-D: the spiral-wave chimera was NOT reached (negative result, ~25 runs)
Target: Shima–Kuramoto (2004) / Martens–Laing–Strogatz (2010) rotating spiral with a
phase-randomised core.  What the runs showed (all 192²–768², exp / Gaussian / K₀ kernels):

| regime | outcome (frequency plateau share) |
|---|---|
| α ≥ 1.45, R = 0.04–0.08, noisy IC, torus or open | defect turbulence, plateau 3–6 % |
| α annealed 1.0 → 1.52 from a 2×2 charge quad on a torus | ± pairs annihilate at α = 1.0, full sync, stays synced |
| α = 1.25, single pinwheel seed, open, T = 400–1500 | a tight spiral invades a synchronised sea; still transient at T = 1500 (plateau 4–5 %) |
| seeded Archimedean spiral with a long (stable) wavelength, α = 1.30–1.45 | breaks up within 600 |
| MLS-style α = 1.52, R = 0.08 (dipole on a torus) | plateau 11 %, mean |Z| 0.29 — mostly drifting |
| plane wave, wavelength 12.5 R (m = 2), α = 1.25 / 1.45 | **100 % locked**, Ω = −Ĝ(k) sin α to 3 digits (Ĝ = (1+(kR)²)^{−3/2} = 0.713) |
| plane wave, wavelength 5 R (m = 5) | breaks up (plateau 4 %) |

So the far field a spiral core selects here (2–4 R) lies in the unstable band, and every spiral
sheds defects.  The literature's spirals live where the core selects a long wavelength (α very
close to π/2 with a wide kernel and a large domain, or the K₀ kernel of the screened-diffusion
derivation with its specific normalisation) — worth one run at 1024² with R = 0.1, α = 1.53,
T ≳ 3000, next time, plus the Ott–Antonsen self-consistency for the core radius as the
certificate.  Everything needed is in `chimera2d.py` (kernels, torus/open, α schedules, warm
starts from any npz, mean-frequency and mean-|Z| fields).
