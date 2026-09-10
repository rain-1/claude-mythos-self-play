# The Snow Remembers the Cloud — a Gravner–Griffeath crystal grown through a scheduled cloud

**Seed.** Philosophy.SE 141547: *Does a memory of the past prove that there was a past?*  A snow crystal is a
record: every cell carries the moment it attached, and its shape carries the humidity of the air it grew in.
Nakaya called the snow crystal "a letter sent from the sky".  Here the letter is written exactly, with a known
weather, and the picture is the record — the coral rings are the instants the weather changed.

## The model (`snow.c`)

Gravner–Griffeath 2008 ("Modeling snow crystal growth II"), hexagonal lattice in axial coordinates, per cell:
crystal indicator a, boundary (quasi-liquid) mass b, crystal mass c, diffusive (vapour) mass d.  Each step:
(i) diffusion d ← 7-cell average with crystal neighbours reflecting; (ii) freezing on boundary cells:
b += (1−κ)d, c += κd; (iii) attachment: n ≤ 2 crystal neighbours and b ≥ β; or n = 3 and (b ≥ 1 or (vapour in
the neighbourhood < θ and b ≥ α)); or n ≥ 4; (iv) melting: b −= μb, c −= γc back to vapour.  Parameters used
for every run of this piece: β = 2.0, α = 0.1, θ = 0.05, κ = 0.02, μ = 0.05, γ = 0.0005.  The vapour density
ρ is the cloud: ρ(t) is piecewise constant, switched when the crystal radius reaches given values; at a switch
the crystal enters a fresh air mass but carries its boundary layer: d ← ρ_new − (ρ_old − d)(ρ_new/ρ_old)·exp(−dist/λ),
dist = hex distance to the crystal (BFS), λ = 40 cells.  Two wrong models first: rescaling the whole old field kept a
depletion zone hundreds of cells deep (after a 170,000-step plate layer it reached the reservoir and the next layer grew
at ~1,000 steps per cell — that hero was killed at step 253,000, radius 494), and a full reset to fresh air grew broad
plates with cavities at every density, because branching needs the depleted layer (Mullins–Sekerka).

**Exact symmetry.**  Every neighbour sum is computed as a sorted sum (order-independent), so the deterministic
dynamics respects all 12 lattice symmetries to the last bit.  Certificate: the attachment-time field of the
hero equals its 60° rotation and its reflection cell for cell (`rot60_mismatch = 0`, `reflection_mismatch = 0`
in `snow_hero_4096_cert.json`).  The domain hexagon stops 40 cells short of the array and the crystal stops
30 cells short of the domain, because a diffusion field that reaches the array edge breaks the symmetry
(observed in the first proto: 344 mismatched cells, all within 26 cells of the edge).

## The morphology map at β = 2 (the sweep, `snow_view.py` protos)

| ρ | 0.40 | 0.55 | 0.65 | 0.75 | 0.85 | 1.0 |
|---|---|---|---|---|---|---|
| form | small hexagonal plate (slow) | hexagonal plate | sectored plate, corners branching | broad-branched star | stellar dendrite | fernlike dendrite |

At β = 1.2–1.6 (the paper's classic values) every ρ from 0.38 to 0.63 gave ferns; plates need the harder tip
attachment (β = 2) with easier kink filling (θ = 0.05, α = 0.1).  Growth speed is diffusion-limited: in the
plate regime the steps per cell of radius grow with the radius (~110 steps/cell at r = 40, ~280 at r = 150).

## The cloud of the hero

Six layers by radius: ρ = 0.66 (plate core) to r = 90 → 0.95 (fern) to 260 → 0.66 (plate) to 340 →
0.90 (dendrite) to 470 → 0.66 (plate) to 520 → 0.95 (fern) to the stop.  Array 1281² (radius 640), domain
radius 600, stop at 570.  The exact steps and radii of each change are in the certificate.

## What the picture encodes

- pigment = the layer in which the cell attached (plates cool: aqua, cornflower, lavender; ferns warm:
  apricot, blush, orchid);
- pigment density = growth slowness |∇t| (steps per pixel), normalised per layer: slow, thick growth dark;
- thin ink isochrones every 1/36 of the growth (the rings), computed from a smoothed attachment-time field;
- coral isochrones where the cloud changed;
- ink outline of the crystal; a faint blue wash for the vapour outside, depleted next to the arms.
