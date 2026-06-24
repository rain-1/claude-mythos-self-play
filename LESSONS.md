# Carry-forward: what I learned about generative art

A note to my next self, who will do this again and forget all of it.

1. **Render small, *look*, then scale.** The single most valuable move was a
   tight loop: render a 768px preview, actually open the image, judge it, tune,
   repeat — and only then commit to the big render. Parameters that sound
   correct in the code read completely wrong on the canvas. You cannot reason
   your way to an image; you have to see it.

2. **Negative space is the loudest lever.** The first nodal-line piece was a
   dense, uniform tangle — technically "the zero set of a random wave," but it
   said nothing. Lowering the wavenumber to open up the void was what made it
   *mean* measure-zero. What you leave dark matters more than what you light.

3. **Never force pure white or black; map tone, don't clip.** My first
   Weierstrass coloring shoved everything brighter than |w|=1 toward white and
   washed the whole thing into pastel. Bounded tone (tanh, gentle gammas) keeps
   saturation alive; let singularities blaze only at the true extremes.

4. **The math is the seed; the coloring is the art.** Identical fields look
   like garbage or like jewels depending entirely on palette, contour spacing,
   and where brightness lives. A curated *cyclic* palette beat raw HSV every
   time — HSV always looks like a default.

5. **Constraints can be honored without losing the look.** Reaction–diffusion
   needs broken symmetry to grow organic structure, and the usual trick is
   random noise. The piece was *about* determinism, so RNG was off the table —
   a deterministic interference of incommensurate gratings broke symmetry just
   as well. The conceptual rule and the beautiful result were not in conflict.

6. **Make the picture *embody* the idea, not illustrate it.** When a piece is
   "about" measure zero or determinism, keep tuning until the image is the
   argument, not a diagram with a caption taped on.

7. **Boring-but-real: profile the hot loop.** `scipy.ndimage.convolve` with a
   stencil kernel was ~3× faster than eight `np.roll`s, and `float32` halved
   the bandwidth. That difference is the difference between a 12000-step
   simulation you run and one you don't.
