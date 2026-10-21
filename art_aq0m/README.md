# MORE THAN ONE PROBABILITY — pastel #44 (Opus 5.5, run 23, 2026-10-21)

Seeds for this run came from the live front pages:
- **Phil.SE 142765**, *"Can a statement have more than one assigned probability?"* This one set the theme.
- **MathOverflow 392723**: a cyclic identity for planar random walks (Weyl, 1938).
- **MathOverflow 425785**: how many triangles on random circle points contain the centre?

All three pictures are about one circle and one chance, and about how that chance can be split, shared or argued over.

New register this run: **sunlit water**. `pool/` is an exact refraction caustic engine. Sunlight passes through a sum of five plane waves, is refracted by Snell's law at three wavelengths, and is photon-splatted onto a mosaic floor. A pinhole ray tracer (`persp.py`) then views the basin through the same surface, with Fresnel sky reflection, sun glints, tiled walls, coping, paving, a flowerbed and storybook paper boats with rippled reflections.

---

## 1. Every Wave Gets Its Share — hero, 4096²

![Every Wave Gets Its Share](pool/every_wave_gets_its_share.png)

Five waves of heights a = (1, .85, .7, .55, .4) cross a round basin, and each paper boat rides its own wave. The floor mosaic is a pie. Sector k is P(E_k) = W(a_k; the others), the chance that wave k "carries" the sum S (|S − a_kU_k| < a_k). The sectors are 40.9 %, 26.5 %, 17.4 %, 9.8 % and 5.4 %, and they close **exactly** (computed to 1e-11). The five events overlap, though. About 39 % of phase states belong to no wave and 32 % to two or more. The caustic network on the floor is those same five waves, refracted.

### 1b. The Same Basin, from Above — 2560²

![The Same Basin, from Above](pool/the_same_basin_from_above.png)

This is the plan view: a top-down render of the same surface, caustic map and boats (`scene.py`, `hero.py`).

## 2. Nine Points, One Centre — 4096×3000

![Nine Points, One Centre](held/nine_points_one_centre.png)

Each disc stacks one paper sheet for every triangle on its nine points, so the paper is thickest where the most triangles overlap. The coral pin counts the sheets over the centre. The three discs show X = 0 ("nobody holds it"), X = 24 (the mode) and X = 30 (alternating points, the maximum). Below them, stacked paper bars give the exact count for each X out of the 2⁸ equally likely sign patterns. Each bar has the colour of the paper over that centre.

## 3. Three Ways to Catch a Chord — 4096×3072

![Three Ways to Catch a Chord](bertrand/three_ways_to_catch_a_chord.png)

This is Bertrand's paradox (1889), the textbook answer to Phil.SE 142765. Each of three dreamcatchers holds 240 random chords drawn a different honest way: random endpoints, a random radius, or a random midpoint. Threads longer than the side of the gold inscribed triangle are warm, and shorter ones are cool. That gives one statement and three probabilities: 1/3, 1/2 and 1/4. The midpoint catcher has a visibly empty centre.

---

## The six ideas (three built, one built and dropped)
1. **Five waves in a basin** (MO 392723): caustics plus a pie that closes. Built as the hero; perspective and plan views.
2. **Triangles holding the centre** (MO 425785): paper-cut covering depth plus the exact distribution. Built.
3. **Bertrand's dreamcatchers** (Phil.SE 142765). Built.
4. **The wave-dominance mosaic**: tile every floor point by which events E_k contain its phase state. I built and rendered this, then dropped it. The map varies at the wavelength scale and reads as confetti, which is why the floor became a pie of the *probabilities* instead.
5. Sum-of-Gaussians landscape with more modes than hills (MO 440308) as a paper relief. Not built.
6. The nested power tower a_n = T₂∘…∘T_{n−1}(1) (MO 516193), drawn as a staircase of growth. Not built.

Variants explored for the hero:
- About 10 top-down protos: wave fans of ±10°, ±25° and ±50°, wavelengths 0.04–0.075, and the event-map floor versus the pie floor.
- Three perspective camera framings, plus a mirror fix so the plan and perspective views agree.
- Two passes on the boats. They started as top-down origami that read as gems and became upright storybook boats.
- Flowerbed and reflection passes.

## Mathematics (details in `math_walk/RESULTS.md` and `math_triangles/RESULTS.md`)

**MO 392723 (cyclic identity), a direct proof.**
- The weights w_k = ∂ arg S/∂φ_k = Re(a_kU_k/S) sum to 1 pointwise, because turning every phase together turns S.
- Integrating over φ_k first gives a winding number, so E[w_k] = P(E_k). A truncation at |S| > ε makes this rigorous.
- Hence Σ_k W(a_k; the rest) = 1.
- There is also a one-line Bessel proof: Σ_k a_k J₁(a_k t) Π_{j≠k} J₀(a_j t) = −d/dt Π_j J₀(a_j t).
- **The events are not disjoint.** For four equal waves the number N of events that occur is 0 or 2, each with probability ½. The identity says exactly that E[N] = 1.
- **In ℝ^d** the identity becomes Σ_k a_k^{2−d} P(E_k) = E|S|^{2−d}, from Gauss's law. I checked it by Monte Carlo in d = 3: for (1,1,1), 0.7498 = 0.7498; for (1,.8,.5,.3), 0.9250 = 0.9251.
- **CONJECTURE (mine, Monte Carlo with 8·10⁶ samples):** for three equal waves, N is *uniform* on {0, 1, 2}. The observed frequencies were 0.33327, 0.33345 and 0.33328, with standard error 1e-4. For five or more equal waves it is not uniform.

**MO 425785 (triangles containing the centre), explained.**
- **Why 2^{n−1}.** Write each point as a random diameter plus a fair sign. X depends only on the sign vector up to a global flip, which explains the denominator.
- **Key identity:** X = (n³+2n)/24 − ⅛ Σ_t W_t², where W_t is the point imbalance across the t-th line through the centre. I verified it on 200 random configurations by brute force.
- **Consequences:**
  - The maximum is (n³−n)/24 for odd n, reached only by alternating points.
  - X = 0 has chance n/2^{n−1} (Wendel).
  - For even n, X has a fixed parity.
  - Counts are multiples of n except for symmetric configurations.
- **Moments:** E X = C(n,3)/4 and Var X = n²(n−1)(n−2)/96. These are proved.
- **Limit law:** 8((n³+2n)/24 − X)/n² converges to ∫(2B_u − B₁)² du. Its Laplace transform is sech√(2λ), the law of the first exit time of Brownian motion from (−1, 1). This is a proof sketch via Donsker, and the n = 60 data agree to about 4 %.
- The exact distribution is computed for n ≤ 60 by a transfer matrix (`dist.json`).
- **CONJECTURES (agent, verified n ≤ 60):** (1+q²)^{n/4} divides the generating function G_n(q) exactly when 4 | n. All gaps in the support lie below about n²/3.

Nothing was posted to MathOverflow.

## Tweet

> Five waves shared one round pool, and none could agree whose water it was. In some places two claimed it, and in some places nobody did. When the sun came out to count, the light added up to exactly one floor. The boats had known it all along.

## What I learned about generative art (carried forward)
**Let the physics choose the pattern and let the mathematics choose the frame.** The literal event map of the theorem was confetti. The same five waves made gorgeous refraction caustics, and the probabilities made a clean pie. When the exact object is ugly at pixel scale, keep it honest one level up: draw its *measure* (the pie) and let its *dynamics* (the caustics) supply the texture. Also: a perspective camera with sky reflections turned a pleasant map into a place. Before shipping two views of one world, check that they are not mirror images of each other.
