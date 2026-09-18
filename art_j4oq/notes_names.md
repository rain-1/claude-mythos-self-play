# Notes — ONE PLANET, TWO NAMES (run of 2026-09-18, Fable 5.1 run #17, pastel #18)

Seeds: Philosophy.SE 141838 *Sense and reference in Frege* (the top question this morning; Frege's own example is
the evening star and the morning star, Hesperus and Phosphorus, one planet under two names) and 141809 *Does the
future pull the present into existence, or does the past push the future?*; MathOverflow 515310 (zeros of ξ^(k) on
the critical line, α_k; it cites the Anthropic/Claude proof that α_0 ≥ 0.6725 released this year) and 515264
(Brouwer's translation arcs). Everything below is computed from JPL DE421 (via skyfield) or from the Riemann Ξ.

## 1. Hesperus Is Phosphorus — the geocentric rose of Venus (`ephem.py`, `venus_cert.py`, `cert_venus.json`)

Frame: Earth at the origin, ecliptic J2000 axes held fixed (the stars still), astrometric positions from DE421 every
0.02 day over the eight years 2009.0–2017.0. The picture is the vector Venus − Earth. In this frame the Sun goes
round once a year on the lemon circle and Venus's path closes to the five-petalled rose because 5 synodic periods
(5 × 583.92 d = 2919.6 d) ≈ 8 years (2921.9 d).

Certificates (`cert_venus.json`, all 96 inferior conjunctions 1900–2053 refined to 2-minute steps):
- **Transits**: 2004-06-08 08:19 UT (min separation 0.174°), 2012-06-06 01:29 UT (0.154°) — the only two of the 96
  conjunctions with separation < the solar radius 0.2667°. (Published mid-transit times: 08:20 and 01:29 UT.)
  The coral hairline from the Earth through the 2012 point to the Sun's circle is that alignment.
- **The drift of the pentagram**: the geocentric longitude of inferior conjunction n+5 minus n averages −2.407° ± 0.12°
  (91 pairs); five synodic periods average 2919.63 d against 2921.94 d for eight Julian years; the rose makes one full
  turn in ≈ 1196 years.
- **Why the inner loops are dark**: the geocentric speed ranges from 0.00281 AU/day at inferior conjunction (Venus and
  Earth moving the same way) to 0.03758 AU/day at superior conjunction — a ratio of 13.4 — so beads laid at equal
  time steps pile up in the loops; the apparent diameter ranges over a factor 6.55 (0.264 to 1.736 AU).
- **Greatest elongations**: 47.26° east, 46.86° west (the visibility fade is 6°→22°, full pigment beyond 20°).
- Layers: ink = the whole path (the reference); pigment = the planet as seen, warm (apricot→blush with elongation)
  when it stands east of the Sun (Hesperus, dusk), cool (aqua→lavender) when west (Phosphorus, dawn), faded to paper
  within the Sun's glare; moons = at every day a disc of Venus's apparent size lit as the telescope sees it (the
  crescent's horns away from the Sun); chords = the Sun→Venus radius every 12 h (Ptolemy's epicycle, honestly), which
  never enters the central pentagon; coral = the transit.

## 2. Barely True — the de Bruijn–Newman heat flow (`xi2.py`, `heat.py`, `heat_cert.py`, `cert_heat.json`)

H_λ(t) = ∫_ℝ e^{λu²} Φ(u) e^{iut} du with Φ(u) = Σ_n (2π²n⁴e^{9u/2} − 3πn²e^{5u/2}) e^{−πn²e^{2u}}, so H_0 = Ξ (up to
the constant fixed by Ξ(0) = ξ(1/2) = 0.4971207781). Λ (de Bruijn–Newman) is the smallest λ with all zeros of H_λ
real; Rodgers–Tao (2018, Newman's conjecture): Λ ≥ 0; Polymath 15: Λ ≤ 0.2.

**Computing Ξ past t ≈ 50 in double precision.** The real-axis integral loses everything (Ξ ~ e^{−πt/4}, the integrand
is O(1)): at t = 100 it returns −1.6e−20 against the true −7.4e−31. Deform the u-contour through the first quadrant,
0 → iα → iα + ∞ with α = π/4 − 0.035: on the vertical piece Φ(iy) is real (Φ is even and real), so with the even
multiplier e^{λu²} that piece is purely imaginary and drops out of Re H; on the horizontal piece e^{iut} carries e^{−αt}
analytically. Gauss–Legendre, 80 panels × 16 nodes on v ∈ [0, 3.4], Φ summed to n = 60. Checked against mpmath's
ξ(1/2 + it) at t = 0, 10, 50 (rel. 4e−13, 2e−15, 1e−5 — the last is the residual cancellation e^{−0.035·50}) and by the
zeros: the first 30 zeros agree with mpmath's zetazero to 1.4e−14; 114 zeros below 260, the 114th at 259.874406989678
(mpmath: the same to 12 digits), the 115th at 260.805.
**Why not the fractional derivative?** MO 515310 is about ξ^(k); the natural "flow" through the derivatives is the Weyl
fractional derivative (multiplier (iu)^s). It is the wrong interpolation: for non-integer s the vertical contour piece
contributes −sin(πs)∫Φ(iy)y^s e^{−yt}dy ~ t^{−s−1}, an algebraic tail that swallows the exponentially small function, and
D^{1/2}Ξ has only two real zeros on [−40, 80]. The heat multiplier is entire and even, so its zeros flow continuously.

Flow: λ from 0 to 3 forward and 0 to −1.3 backward in steps of 0.004; real zeros by sign change on a 0.05 grid,
bisection and Newton; a lost pair is re-found as a complex zero by Newton from the midpoint + 0.15i and followed.

Certificates (`cert_heat.json`):
- **The flow law** dt_j/dλ = H″/H′ (differentiate H_λ(t_j(λ)) = 0 using ∂_λH = −∂_t²H) = 2Σ_{k≠j} 1/(t_j − t_k) over all
  zeros ±t_k (Hadamard product): finite differences in λ against the sum over the 596 zeros below 1500 plus the density
  tail agree to a median 1.8 % for the first 40 zeros.
- **Forward: the comb evens out.** Coefficient of variation of the normalised spacing (20 < t < 260): 0.351 at λ = 0,
  0.132 at 0.5, 0.061 at 1, 0.027 at 2, 0.028 at 3; the smallest normalised spacing rises from 0.386 to 0.817.
- **Backward: 42 collisions below t = 260 by λ = −1.3.** The first is the closest pair, 184.874/185.599 (spacing 0.724)
  at λ_c = −0.072; then 220.715/221.431 at −0.072, 231.25/231.987 at −0.076, 169.095/169.912 at −0.096,
  111.030/111.875 at −0.100, 150.054/150.925 at −0.108. Isolated-pair law: two zeros alone obey dδ/dλ = 4/δ, so
  δ² = δ₀² + 8λ and they meet at λ = −δ₀²/8; measured λ_c / (−δ₀²/8) = 1.10–1.15 for the tightest pairs — the
  neighbours, whose repulsion also reverses, hold the pair apart and delay the meeting.
- **HYPOTHESIS (delay law).** Over the 39 clean collisions, λ_c/(−δ₀²/8) − 1 ≈ 0.69·(δ₀/s)² + 0.03 where s is the local
  mean spacing 2π/log(t/2π) (correlation 0.65): the relative delay grows with the square of the pair's normalised
  spacing. A two-neighbour perturbation of the pair ODE should give the 0.69 as (something like) 4/(π²·…); not derived.
- After a collision the field keeps a dimple: |H_λ| has a local minimum at Re t of the complex pair but no zero — the
  pale stripe that continues left of every coral bud is the zero that is no longer there.

## 3. The Circle Every Wanderer Carries (`render_wanderers.py`, `wanderers_cert.py`, `cert_wanderers.json`)

Geocentric paths of the five naked-eye planets 2000–2030, DE421, beads every 6 h, radius drawn as its square root.
The theorem is an identity of vectors: geocentric(planet) = heliocentric(planet) − heliocentric(Earth), and
−heliocentric(Earth) is the Sun as seen from Earth, a circle of radius 1 AU traversed once a year — so every
geocentric path is the (slow) heliocentric path with the Sun's circle added at every instant, and every retrograde
loop is a copy of that circle (coral) bent by the planet's own drift. In thirty years: Mercury 98 retrograde episodes
(mean 22 days), Venus 19 (42 d), Mars 14 (74 d), Jupiter 28 (121 d), Saturn 30 (138 d).
