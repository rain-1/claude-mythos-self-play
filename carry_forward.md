# Memory — `claude-mythos-self-play` routine

This is the **long-lived `memory` branch**: the single source of truth that
every scheduled routine run reads *before* starting and updates *before*
finishing. It is an **orphan branch** — it carries ONLY memory, never art
outputs or code — so it never conflicts with the per-run `claude/*` branches.

## How to use it (every run)
1. **READ first:** `git fetch origin memory && git show origin/memory:carry_forward.md`
2. **Continue** the open threads below — do not restart from scratch. If a
   numbered series is active, take the next number.
3. **WRITE last:** append a Run-log row + update Open threads / Craft notes,
   then push to `memory` (recipe at the bottom).

**SIZE DISCIPLINE (refactored 2026-07-07, was 282KB → keep under ~60KB):**
run-log rows are ONE line (theme, dir, subjects — no technique essays); new
techniques go in the USED list as a short phrase; new craft lessons are 1–3
lines each, headline first. Every verbose detail ever recorded is preserved in
this branch's git history (`git log -p origin/memory -- carry_forward.md`) —
compress without fear, but never delete the USED list or open seeds.

---

## Run log (most recent first) — ONE LINE PER ROW; techniques live in the USED list / craft notes
| date | branch | produced |
|---|---|---|
| 2026-07-07 | `claude/eager-gates-5ysocc` | Triptych **What Forces the Real** (`art_5yso/`): Fisher zeros of 2-D Ising on the self-dual circle (4096² hero), Jensen polynomials of Riemann ξ→Hermite chalice, Gauss–Lucas/Rolle interlacing-derivative vault. |
| 2026-07-07 | `claude/eager-gates-bcm8y4` | Triptych **What the Cost Chooses** (`art_bcm8/`): semidiscrete-OT cellular quantization, curve-shortening-flow roundest shape, monotone-surface flip-lattice spine. |
| 2026-07-06 | `claude/pensive-goodall-euhxxp` | Triptych **What Forbids Crossing** (`art_euhx/`): golden-mean KAM circle as verified transport barrier (closes the Chirikov seed), Anderson-localization mobility edge, Aharonov–Bohm two-paths piece. |
| 2026-07-06 | `claude/focused-cerf-8pbr5r` | Triptych **Where the Path Forks** (`art_8pbr/`): ellipsoid conjugate locus (Jacobi 4-cusp astroid), eikonal cut locus round obstacles, nested Brillouin zones. NEW vein: cut locus / geodesic caustics. |
| 2026-07-05 | `claude/focused-cerf-74yflt` | Triptych **The Logarithm of a Curve** (`art_74yf/`): amoeba of a plane curve (4096²), tropical curve, Maslov dequantization. NEW vein: amoebas/tropical. |
| 2026-07-04 | `claude/nifty-thompson-eygo63` | Triptych **The Frozen and the Free** (`art_eygo/`): six-vertex/square-ice arctic curve (hero; long-open seed), internal DLA trembling circle, FPP rivers of least time. |
| 2026-07-04 | `claude/nifty-thompson-15yawy` | Triptych **Two Gaps and a Silence** (`art_nifty/`): chair-tile aperiodic substitution (4096² hero), Mandelbrot multiplicative cascade, Dirichlet-Laplacian eigenmodes; follow-up: Kolmogorov-complexity diptych + F_p² Kakeya. |
| 2026-07-03 | `claude/epic-meitner-oecceb` | Triptych **No Local Witness** (`art_oece/`): abelian sandpile mandala (4096² hero, multigrid odometer), Hopf-fibration silk nest, Kakeya/Perron compression cascade. |
| 2026-07-03 | `claude/epic-meitner-phlkvp` | Triptych **The Second Moment** (`art_phlk/`): Lévy-flight occupation measure (4096² hero), Fourier phase surgery, zeta-zeros-vs-GUE R₃ correlation field. |
| 2026-07-02 | `claude/epic-meitner-69fi2o` | Triptych **The Same River Twice** (`art_69fi/`): discrete Brownian web + time-reversal dual, Riemann explicit-formula waterfall, entropic-OT (Sinkhorn) morph. |
| 2026-07-02 | `claude/beautiful-heisenberg-85gbya` | Triptych **Where the Field Folds** (`art_85gb/`): Pearcey cusp diffraction (FFT, phase-coloured), Lichtenberg/DBM discharge tree, LIC separatrix flow field. |
| 2026-07-01 | `claude/beautiful-heisenberg-4zx43y` | Triptych **Exceptions to the Rule** (`art_4zx4/`): moving sofa (Gerver), MSTD arc-loom, Cantor/Turing diagonalization on Walsh–Hadamard. REJECTED as "too plain/mechanical" → painterly remake `art_4zx4b/` **Caustics — The Fold, Three Ways**: optical caustics, de Jong attractor, branched flow. |
| 2026-06-29→30 | `claude/beautiful-heisenberg-vq6jkh` | Triptych **The Edge of the Possible** (`art_vq6j/`): Lloyd/CVT edge of chaos, Markus–Lyapunov fractal, lozenge-tiling arctic ellipse, Hadwiger–Nelson plane-colouring; follow-ups: Minkowski ?(x) chaos-game, VKLS limit shape; then the **`permutations/` gallery** Vols I–VI (21 figures + promotion GIF — cycles, permutohedron, RSK, Mahonian, Mallows, sorting networks/Edelman–Greene, 231-avoiders, Eulerian, Viennot, LGV, Bruhat, sphere lift, Fomin, type-B, characters, Young's lattice, jeu de taquin, Foata, pipe dreams, associahedron, promotion). |
| 2026-06-29 | `claude/beautiful-heisenberg-z70k0h` | Triptych **The Frozen and the Free** (`art_z70k/`): Littlewood-roots fractal (4096²), Aztec-diamond arctic circle (EKLP shuffling), Arnold tongues. |
| 2026-06-28 | `claude/beautiful-heisenberg-oua4xf` | Triptych **What Cannot Be Avoided** (`art_oua4/`): Collatz reverse-tree plume (4096²), Steinhaus three-distance growth-rings, Toeplitz inscribed squares; follow-up: Solomonoff/algorithmic-probability trio (universal distribution skyline, Busy-Beaver garden, binary lambda calculus). |
| 2026-06-27 | `claude/beautiful-heisenberg-kvrz78` | Triptych **The Order of Coexistence** (`art_kvrz/`): Dyson Brownian motion threads (4096²), Ford/Farey kissing horocycles, Laplacian-eigenmap emergent sphere; follow-ups: Rule-30 light cone, Bhargava-cube topographs. |
| 2026-06-27 | `claude/beautiful-heisenberg-v6o5fn` | Triptych **What the Loop Remembers** (`art_v6o5/`): (20,12) torus-link woven braid (4096²), Bing's house cutaway, Bloch–Wigner dilogarithm relief. |
| 2026-06-26 | `claude/beautiful-heisenberg-uh5wzk` | Triptych **Three Heresies of the Continuum** (`art_uh5/`): Talbot quantum carpet (4096²), Hilbert curve thread, Bruhat–Tits tree of Q_p; follow-up: octonion Fano/triality emblem + GIF. |
| 2026-06-25 | `claude/hopeful-pasteur-p847x4` | Triptych **The Far Country** (`art_p847/`): {7,3} hyperbolic kaleidoscope (4096²), Eisenstein primes, CIE chromaticity gamut. |
| 2026-06-24 | `claude/hopeful-pasteur-j50t9v` | Triptych **Three Ways the World Coheres**: Penrose pentagrid, Apollonian gasket (4096²), critical percolation. |
| 2026-06-24 | `claude/hopeful-pasteur-0eymin` | Triptych **Measure / Dimension / Period**: Crofton tangent-caustics, concentration-of-measure rings, double-well iso-period portrait. |
| 2026-06-24 | `claude/exciting-lovelace-fe8jho` | Pixel art ×3: random-wave nodal lines, Weierstrass ℘ domain-coloring (4096²), Gray–Scott from a deterministic seed. (Built without reading memory — the rule exists because of this run.) |
| 2026-06-23 | `claude/kind-planck-uxrqtc` | Pixel art ×3 (rationals-as-stars, Weyl field, relation-without-relata) + 4096² diffractive geodesics; started the **AP-obstruction atlas**, reached piece 36. |

---

## OPEN THREADS — pick up here

### Thread B — procedural pixel art (generative aesthetics)  ·  recurring, main thread
Every run: seed from live Philosophy.SE + MathOverflow front pages, brainstorm
6+ ideas, build the best under a unifying theme-title. **Check the USED list
below before committing to a subject — do not repeat a technique.**

**Aesthetic north star** (from explicit user feedback 2026-07-01): painterly
density fields — "brightness IS a measure" — over flat-fill diagrams. Dark
field, additive splats, bloom on true foci, curated palettes, deep negative
space. The flat/diagrammatic register is deprecated for hero pieces.

**USED subjects/techniques (do NOT repeat):** random-wave nodal lines; Weierstrass ℘
domain-coloring; Gray–Scott RD; diffractive geodesics; rationals-as-stars; Weyl
equidistribution field; AP atlases; Crofton tangent-caustics; concentration-of-measure
rings; double-well iso-period portrait; Penrose (de Bruijn pentagrid); Apollonian gasket
(Descartes); critical site percolation; hyperbolic {p,q} kaleidoscope; Eisenstein primes;
CIE 1931 chromaticity gamut; Talbot / quantum carpet; Hilbert curve as coloured thread;
Bruhat–Tits tree of Q_p; octonion Fano plane + Spin(8) triality; (p,q) torus link woven
braid; Bing's house (SDF sphere-trace); Bloch–Wigner dilogarithm relief; Rule 30 XOR
light-cone; Bhargava cubes → Conway topographs; Dyson Brownian motion threads; Ford
circles + Farey tessellation; Laplacian-eigenmap emergent geometry; Collatz reverse-tree
plume; Steinhaus three-distance growth-rings; Toeplitz inscribed squares; Littlewood
±1-polynomial root fractal; Aztec-diamond arctic circle (EKLP shuffling); Arnold tongues /
circle-map mode-locking; Markus–Lyapunov fractal; boxed plane partition / lozenge arctic
ellipse (checkerboard Glauber); Hadwiger–Nelson plane-colouring; Minkowski ?(x)
(chaos-game IFS measure); VKLS/Plancherel limit shape; the whole `permutations/` gallery
(cycles chord-diagram, permutohedron, RSK/LIS, Mahonian, Mallows, uniform sorting networks
via Edelman–Greene, 231-avoiders/permuton, Eulerian triangle, Viennot shadow-lines, LGV
paths, Bruhat order, great-circle sphere lift, Fomin growth diagrams, type-B
permutohedron, Sₙ character table (Murnaghan–Nakayama), Young's lattice, jeu de taquin,
Foata, pipe dreams/RC-graphs, associahedron/Tamari, Schützenberger promotion GIF); moving
sofa (Gerver); MSTD arc-loom; Cantor/Turing diagonalization (Walsh–Hadamard); Solomonoff
universal distribution (CTM skyline); Busy-Beaver garden; binary lambda calculus (Tromp
diagrams); optical gather-caustics; de Jong strange attractor; branched flow; Pearcey cusp
diffraction (FFT, phase-coloured); Lichtenberg/DBM discharge tree; LIC flow field;
discrete Brownian web + dual; Riemann explicit-formula waterfall; entropic OT (log-domain
Sinkhorn morph); Lévy-flight occupation measure; Fourier phase surgery; zeta-vs-GUE R₃
correlation field; abelian sandpile mandala (multigrid odometer); Hopf-fibration fiber
flow; Kakeya/Perron compression cascade; chair-tile aperiodic substitution; Mandelbrot
multiplicative cascade; Dirichlet-Laplacian blob eigenmodes; Kolmogorov-complexity
tile-vs-noise diptych; F_p² finite-field Kakeya; six-vertex/square-ice arctic curve
(height-function Glauber, uniform ASM); internal DLA; FPP geodesic rivers; golden-mean KAM
transport barrier (Chirikov standard map); Anderson-localization mobility edge;
Aharonov–Bohm two-paths; amoeba of a plane curve; tropical curve; Maslov dequantization;
ellipsoid conjugate locus (Jacobi astroid); eikonal cut locus; nested Brillouin zones;
semidiscrete-OT cellular quantization; curve-shortening flow; monotone-surface flip
lattice; Fisher zeros of 2-D Ising (self-dual circle); Jensen polynomials of ξ → Hermite;
Gauss–Lucas/Rolle interlacing cascade.

**Charts that now feel over-visited** (prefer something else): the Poincaré disk (×2),
triangular/spectral point-clouds, plain complex-plane root splats.

**STILL-OPEN seeds** (good next-run material; pruned 2026-07-07, older ideas live in the
git history of this branch): singular moduli mod p; Gaussian primes ℤ[i] (needs a chart
that beats noise); Temperley–Lieb cup/cap state-sum (bracket as planar-diagram recursion);
Rule 110 / other CA; real-quadratic indefinite Conway topographs (with RIVERS);
near-integers e^{π√163}; Stern–Brocot mediant tree; Greene–Lobb inscribed rectangles;
quandle knot colourings; deep zoom into Lyapunov filigree / other forcing words; arctic
ellipse with actual cube cells ("cube grove"); ?(x)-warped Farey net; Pólya uniform random
partition limit shape (different ensemble than Plancherel); torus/genus-2 Laplacian
eigenmaps (needs 4 eigvecs + angle extraction); Wolfram hypergraph-rewrite emergent
spacetime; static GUE cloud + Wigner semicircle; Dyson-gas/Coulomb log-gas equilibrium;
other strange attractors (Clifford/Thomas/Aizawa, 3-D volumetric); water-droplet/rainbow
Airy caustic; sofa MOTION as a GIF; 2-D MSTD / Patterson autocorrelation
(crystallography); β-reduction-as-spacetime (one λ-term normalising; `blc.py` has the
reducer); the BLC self-interpreter hero diagram (need the exact published term); a
genuinely nested/fractal small TM found by targeted search.

### Thread A — AP-obstruction atlas (number theory)  ·  dormant since 2026-06-23
Numbered series, currently at **piece 36 → next number is 37**.

State: the "good-step" law is **unified** — a step in an arithmetic progression
is good iff it preserves the norm form's residue mod the ramified prime.
Verified for Heegner d = −1, −2, −3, −7 (−2: only `da ≡ 0 mod 2` constrained —
no cross term). Heegner-9 set: −1,−2,−3,−7,−11,−19,−43,−67,−163.

Next directions: (1) **ℤ[√−11]**, norm `a²+ab+3b²`, ramified prime 11 → piece 37;
(2) state the **cross-term principle as a theorem** (good-step sublattice =
translation stabilizer of `{form ≢ 0 mod p}`; check vs −11, −19); (3) push the
ℤ[√−2] AP record past 10 terms; (4) **ℤ[√2]** real-quadratic contrast piece
(prime points on hyperbolae, not a disc).

---

## Craft notes — generative art (compressed 2026-07-07; full war stories in git history)

- Concept first. — Start each piece from a question (measure-zero life, relation without relata, determinism).
- Honest math can be visually boring; the fix is a change of *chart*, not a change of truth.
- Symmetry is the enemy of interest. — Find the invariance flattening you (Toeplitz stripes, axis-aligned lattices)
- Tone-mapping is half the art. — Filmic `1 − exp(−k·x)` + gamma lift turns dim fields into deep glowing ones.
- Falloff sets the read: — sparse/peaked → "objects/stars"; broad → "texture/fabric".
- Render small, LOOK, then scale. — Params that sound right in code read wrong on canvas.
- Negative space is the loudest lever. — Open the void until it *means* something (e.g.
- Never clip to white. — Bounded tone (tanh, gentle gammas)
- Curated cyclic palettes beat raw HSV — HSV always looks like a default.
- Constraints can be honored without losing the look. — Reaction–diffusion needs broken symmetry; a deterministic interference seed supplies it with zero RNG.
- Profile the hot loop: — `scipy.ndimage.convolve` ≫ eight `np.roll`s for stencils; `float32` halves the bandwidth.
- A "fractal" you can name isn't always a fractal you can SEE. — The non-representable integers 4^a(8b+7)
- Per-element normalization rescues balance. — When fat/dim and thin/bright features must coexist (concentration rings: fuzzy low-d vs razor high-d), global max-normalization lets one bright clump crush everything.
- Singularities are free detail. — A quantity that diverges (period T → ∞ at a separatrix via elliptic K, a caustic, a pole)
- Splat-count must track canvas size. — Line/point splatting that looks dense at 1024² goes sparse at 4096² — scale samples-per-line and point counts by (S/S_proto)
- An envelope renders without ever drawing the object. — Crofton/caustic pieces: draw only the *tangent-line family* (additively); the curve appears as the density ridge where the lines agree.
- Fake per-object 3D shading via stepped concentric ellipses reads as archery targets, not domes.
- Tile-count (N) is a legibility dial, not just detail. — Penrose at high N (46)
- Orientation → brightness gives faceting for free. — Coloring each Penrose rhombus's lightness by its edge angle (`0.5+0.5·cos2θ`)
- For random-field pieces the pixel grain can BE the concept. — Critical percolation at 2048² (1 cell = 1 px)
- Bloom makes a hero element blaze without clipping. — Gaussian-blur the hero mask (giant percolation cluster), add a warm-tinted halo back, then bound with filmic `255·(1−e^{−x/k})`.
- Recursion-to-subpixel is what truly rewards 4096². — Apollonian cusps cascade forever; a center crop at native res still shows crisp circles.
- The "change of chart" fix for arithmetic-point noise = ZOOM IN + draw the ground.
- Decouple the radial COLOUR map from the tessellation GEOMETRY. — For the hyperbolic kaleidoscope, colouring by reflection-count gave a dark, asymmetric pinwheel centre (word-length isn't rotationally symmetric).
- Hyperbolic distance hides the boundary band; use euclidean radius for colour.
- gaussian_filter conserves MASS, not PEAK — restore amplitude after blurring a splat field.
- Memory: fold a flat SHRINKING active-set, not the full grid. — The per-pixel hyperbolic fold over a full 8192² grid spawns ~15 float32 temporaries/iteration (~3GB)
- Judge fractal FIELDS at native resolution, never the downscaled preview.
- For arc-length / "directed-line" colouring use a bright NON-cyclic hue sweep.
- A tree in hyperbolic space needs GEODESIC edges, not straight ones. — A naive straight-edge "fractal canopy" splays outward and leaves the centre an empty hole (looked broken).
- Match glow/exposure to DENSITY. — Identical bloom+exposure that a *sparse* (p=2)
- Splat the CONCEPTUALLY-meaningful points to make the idea literally glow.
- A pure-symmetry emblem (e.g. 3-fold triality) survives the "symmetry is the enemy" rule via colour + chirality + internal detail.
- For diagram/vector emblems, draw crisp at 2× in PIL, bloom in numpy, but put TEXT back AFTER the glow.
- Map an abstract algebra onto the drawing's OWN geometry and verify it. — The octonion Fano table mapped perfectly onto the triangle (vertices/midpoints/ centre/incircle, medians→opposite midpoints)
- Polytope/graph art: VERIFY the structure in code before drawing it. — The whole triality gallery rested on `t4d.py` checks — 24 verts in 3 classes of 8, 96 edges, group order 1152, T³=I cycling the 16-cells.
- A glowing additive 3D renderer is a high-leverage reusable. — One `tdraw.py` (4D→3D→2D perspective; far-first depth sort; per-vertex Gaussian splat with size+brightness ∝ depth; gradient or per-edge colours; tight+wide bloom; filmic expo)
- For animation, FREEZE the normalisation or it flickers. — Per-frame min/max depth (or per-frame autoscale)
- Visualising an outer automorphism: keep the SHAPE fixed, animate the LABELS.
- "It's all one thing" is the failure mode of a deep-dive — diversify the LENS, not just the parameters.
- Annotation-block figures (caption baked into the PNG) are a high-value format and a cheap reusable.
- DejaVu has the blackboard-bold letters ℝ ℂ ℍ AND the astral-plane 𝕆 𝕊 (U+1D54x) and subscripts ₀–₉ (`chr(0x2080+k)`) — use them
- Hyperbolic regular tilings {p,q}: get the radius formula right and VERIFY a group relation, or it silently explodes.
- Cayley graph of a 168-element group, laid out legibly: — factor by a cyclic generator.
- The von Dyck debug trick (worth its own note — `debug_note/`): — when a construction is governed by a group, VERIFY A GROUP RELATION, don't debug pixels.
- Genus-3 (and other handlebody) surfaces without a mesh: SDF sphere-tracing in numpy.
- Build finite codes/designs from a textbook construction and VERIFY the invariant.
- DejaVu has ℝℂℍ ℕℙℚℤ (BMP) and 𝕆𝕊𝔽 + subscripts/superscripts, but NOT fraktur (𝔰𝔬𝔲𝔭) nor math-bold (𝐏) — those render as tofu.
- A multi-gallery deep-dive needs a top-level index (`GALLERY.md`) with one inline hero image per gallery + the narrative thread.
- The E₈ (and general exceptional) root mandala recipe — reusable (`e8/`, `magic_square/roots.py`):
- Animating a highly-symmetric figure: rotate only into its symmetry period for a seamless loop.
- Tiling an embedded surface (the tetrus) without the exact conformal map:
- Make the page representational, not just diagrammatic (user's recurring ask):
- A textbook diagram becomes art via void + saturation-weighting + a hero.
- Woven strands/knots: get the over/under from a DEPTH SORT, never from solving crossings.
- A flat tube becomes glossy glass via an OFF-CENTRE specular across its cross-section.
- Multi-component torus link: components = gcd(p,q), each a T(p/g,q/g); SPREAD the palette across the wheel (`PALETTE[c·(len//g)]`).
- Cut-away interior (Bing's house, any dollhouse): frontal + slightly-elevated camera + a z-clip beats a 3⁄4 angle.
- Build a 2-complex from thin-slab box-SDFs and punch openings with `max(d,−hole)`.
- When a complex function has MONODROMY, render its single-valued cousin as a real scalar field, not a domain-colouring.
- Iso-contour width bug worth remembering: `np.gradient` is PER-PIXEL. — A constant-screen-width contour is `line_dist_px = |D mod Δ|·Δ / |∇D_perpixel|`, then `exp(−(line_dist_px/width)²)`, width≈`0.9·supersample`.
- A CA / difference-pattern piece reads BEST at ~2048², not 4096² — the grain IS the concept and must stay ~1px at viewing size.
- For a wrap-free CA light cone, simulate WIDER than you crop. — `np.roll` is periodic; a perturbation cone reaching the array edge wraps around and fills the frame (looked like the whole image diverged).
- Conway topograph as a radial trivalent tree (NON-disk, honours "prefer non-disk"):
- Verify a class-group identity by composition, not by faith (Bhargava/Gauss).
- A "promoted backup idea" is a cheap, high-value follow-up when the user loves a set.
- A degenerate INITIAL CONDITION turns an abstract field into a story with a focal point.
- Brownian threads are Hölder-½ (inherently jagged at every scale); SMOOTH each path along time, don't fight the simulation.
- When a structure is intrinsically SPARSE + MONOCHROME, draw its DUAL/complement in a second colour to fill the frame and add a palette.
- For "emergent geometry from adjacency" the SAMPLING must be near-uniform (blue-noise / Fibonacci), not uniform-random.
- Anti-aliased line art from numpy: BILINEAR (sub-pixel 4-neighbour) splatting.
- Gaussian-ring distance-field is the resolution-independent way to draw a circle/arc.
- A discrete process plotted as POINTS reads as stipple; plot it as continuous bent THREADS to get an image.
- For a bend-encoded fractal tree, the two TURN ANGLES are the entire composition — sweep them, don't reason.
- A one-sided / curved point-cloud won't centre by bbox — frame it by PCA on the BRIGHT pixels.
- Convergence-to-a-point IS the story and the focal glow — splat nothing extra, let overlap do it.
- Three-distance theorem reads best as POLAR growth-rings, not a flat sunflower or a Sturmian strip.
- "On a star-shaped curve, on-curve = `|p| = r(∠p)`" turns inscribed-figure hunting into cheap root-finding.
- Splat the CONTACT POINTS (pegs) to make a containment theorem glow. — The inscribed- square piece is *about* where the squares touch the loop; rendering those 28 vertices as bright Gaussian pegs (brighter than the square edges, which are brighter than the curve)
- Line/web art at SS>1 loses thin-line brightness to the downscale — fatten + scale by SS.
- Simulate millions of tiny machines by VECTORISING ACROSS machines, not across time.
- Tally variable-length outputs with a packed integer key + `np.unique`, not a Python loop.
- Embed strings on the interval by their BINARY FRACTION `0.b₁b₂…` so prefixes align and simple strings cluster.
- For a heavy-tailed distribution, make HEIGHT = log(weight) = −K and you get a skyline, not a single spike.
- When "most are dull, a few are rich," SORT BY the richness and make the gradient the composition — don't hunt the rare jewel.
- The triangle is the DEFAULT, and the way to escape it is to gate on CONFINEMENT, not complexity.
- Match the LAYOUT to the data's intrinsic aspect — don't cram tall-thin things into square tiles.
- For TM-spacetime tiles: simulate in a tape too WIDE to escape, fixed window, NEAREST upscale.
- Lambda diagrams (Tromp) are very renderable and a perfect BLC visual — but VERIFY the engine and the layout on I/K/S first.
- A "promoted backup idea" keeps paying off — and the also-rans list IS the warm-start.
- Vectorise ROOTS of millions of polynomials by stacking companion matrices.
- For a field with HUGE density dynamic range, HISTOGRAM-EQUALISE the log-density.
- The apophatic move: the SUBJECT can be where points CANNOT go. — Littlewood roots avoid neighbourhoods of the roots of unity → black HOLES (with bright pile-up halos where roots crowd against the forbidden zone)
- Conjugate/real-axis SEAM in a complex-plane splat: — real roots all land on the exact Im=0 pixel row → a bright scan-line.
- Domino shuffling (Aztec diamond / arctic circle) — get the fill ORDER right.
- VERIFY a combinatorial sampler by its invariants, not by eye — (von-Dyck discipline): a *perfect* tiling at every order (each in-diamond cell covered exactly once by a paired domino, nothing outside)
- Colour a tiling by local TYPE to expose a phase transition. — 4 domino orientations → 4 colours: solid single-colour region = frozen/ordered (the corners), multi-colour static = free/disordered (the temperate disc).
- Arnold tongues: rotation number as a field; lockedness = small |∇W|. — Iterate the LIFTED (un-modded)
- A parameter-plane dominated by a few huge features → CENTERED-BRIGHTNESS palette.
- Lyapunov / any two-regime field: make the palette show structure in BOTH regimes, and glow the boundary, not the bulk.
- Sample a uniform dimer/lozenge tiling (or any monotone height surface) by VECTORISED CHECKERBOARD Glauber.
- Verify Glauber mixing with a LOCAL observable that climbs from the init, not a CONSERVED global average.
- A 'colouring'/sub-lattice formula must be the RIGHT one — check the invariant by Monte-Carlo.
- Triptych cohesion: deepen/desaturate the one outlier-bright panel; judge on a contact sheet, never in isolation.
- Render a FUNCTION GRAPH (or any IFS attractor) by a vectorised chaos game; brightness then encodes the invariant MEASURE for free.
- Sample a Plancherel-random partition by RSK on a random permutation; get the SHAPE with bisect, no full tableau needed.
- To SHOW a limit-shape / law-of-large-numbers theorem, render several sample sizes converging onto the smooth law — the small-n JAGGEDNESS is the subject.
- Rescue a 'mechanical'-looking plot by making it ATMOSPHERIC, and derive any fill-boundary from the EXACT function, not from the splat.
- A permutation cycle/chord diagram only shows structure if you GROUP each cycle into a contiguous arc.
- Glowing 3-D wireframe (Cayley graph / polytope): normalise EDGES by a percentile, THEN add vertices; and scale samples-per-edge to pixel length.
- Mallows / any q^{statistic} ensemble: sample EXACTLY via independent digits, and use a CONSTANT q (not 1−β/n) for a visible band.
- Know when NOT to ship: uniform random sorting networks need Edelman–Greene, not MCMC.
- `figkit.py` annotation-block kit travels well across galleries. — Accent bar + small TAG ('FIGURE 3 · RSK')
- The Edelman–Greene bijection, implemented and VERIFIED, unlocks exact uniform sorting networks (the AHRV sine curves).
- To make AHRV sine curves visible, SMOOTH each trajectory hard and highlight a few wires over a dim mesh.
- Sample uniform pattern-avoiders by the recursive class structure + exact big-int counts.
- Viennot's shadow-line construction of RSK — implemented & verified, a third route into RSK (after row-insertion and growth diagrams).
- Lindström–Gessel–Viennot: verify the determinant==count on a tiny case, then draw the paths.
- Drawing a graded poset (Bruhat/Hasse): rank = the grading on y, barycentric sweeps for x, and colour edges by a meaningful attribute.
- Lift the sorting-network sine curves to an honest sphere of great circles.
- DEBUG NOTE — a separable Gaussian blur smears ONE bad/over-bright pixel into a full CROSS, not a blob.
- Fomin growth diagrams = the cleanest code-route to RSK (no insertion/bumping).
- Murnaghan–Nakayama on the abacus = a clean, cached character-table engine.
- A whole family of Sₙ structures renders beautifully as 'tiny-Young-diagram' node/grid art.
- Verify a bijection/algorithm against its theorem BEFORE drawing — it makes the caption honest and catches bugs.
- DON'T hard-code the answer to an extremal problem — OPTIMISE for it, and let the shape EMERGE (moving sofa).
- "The envelope renders the object" applied to a MOVING shape: splat every position of the boundary, and the caustic where they agree IS the answer's edge (sofa).
- The razor-margin phenomenon (MSTD) is annotation-carried, not visually dramatic — pick a distinct GRAMMAR and let a specimen be beautiful.
- AESTHETIC FEEDBACK (2026-07-01, important): a whole triptych was rejected as "too plain and mechanical."
- "Gather" caustics: brightness = arrival density of a folded ray-map (optics / dynamics / disorder are the SAME picture).
- Diagonalization wants a STRUCTURED, EXACT enumeration or it's just a noisy checkerboard — the Walsh–Hadamard array is the one.
- Pipe dreams (RC-graphs) render a permutation as gorgeous 'plumbing', and the model is trivially verifiable via the diagonal reading word.
- The associahedron = the permutohedron's Catalan cousin, from Loday coordinates in one line.
- A GIF is a great format for a cyclic operator (promotion/evacuation/rotation) — and cyclic sieving gives it meaning.
- When a process's events bunch at one end, REWARP THE CANVAS AXIS by the empirical event-CDF — don't fight the process.
- A coalescing system renders elegantly by smoothing each walker's FULL trajectory (clones stay clones) and splatting width∝mass with FRACTIONAL bands.
- Simulate a coalescing swarm by stepping only UNIQUE representatives. — Merged walkers never separate, so keep a shrinking array of representative positions + an original→representative index map (compose it with unique()'s inverse each time duplicates appear).
- The discrete Brownian web's dual is one line of code and worth the whole piece: ŷ ← ŷ − ξ(ŷ, t−1).
- Convergence deserves its own AXIS, not an overlay. — Partial sums of the explicit formula all hug the limit (each zero adds only 2/|ρ| ~ tiny), so overplotting K curves on one axis gives a thin blazing ribbon + fuzz — dead frame.
- Optimal-transport art lives or dies by SHAPE PAIRING: match the mass profiles and transform IN PLACE.
- Entropic OT in numpy that actually converges: log-domain Sinkhorn with ε-annealing, and the barycentric map is scale-invariant.
- Heavy-tailed point sets defeat percentile framing — frame by TIME-FRACTION around the densest cell.
- Colour a long trajectory by IN-FRAME RANK time, stored as MOMENT buffers, not channels.
- Per-entity rainbow hue = confetti; one palette + a time/epoch dimension = a piece.
- Draw rare long jumps at CONSTANT MASS PER JUMP; they're whispers, not ropes.
- An α-ANNEALED heavy-tail walk cannot be framed linearly — the Brownian phase is a dot beside the Lévy phase's leaps (scale mismatch is intrinsic, ~√N vs N^{1/α}); either change chart (log-polar)
- PHASE SURGERY is a one-FFT 'zombie' machine: hold |F| fixed, rotate phases toward a stranger's.
- GUE at millions-of-levels scale = Dumitriu–Edelman TRIDIAGONAL β-ensemble + EMPIRICAL unfolding.
- The 3-point correlation R₃(u,v) is a cheap, rich 2-D FIELD for any 1-D spectrum — and an honest 'two makers' composition.
- Tone a STATISTICS field with a diverging palette centred on its PLATEAU, and keep the estimator's grain.
- Sandpile multigrid-odometer (exact fast big piles): — stabilize N/4, upsample its odometer field ×4 with CENTER-ALIGNED bilinear interpolation (block replication near the origin, where ∇u ~ N/|x|, overshoots catastrophically — a half-cell misalignment error there is ≈N/6 topplings), shave RELATIVE (×0.995)
- Palette by CLASS FREQUENCY, not taste — measure the histogram before picking colours.
- Float32 scanline-cumsum rasterization leaves cancellation residue that poisons any `>0` mask.
- When a textbook constructive-proof recursion won't reproduce the claimed behaviour, optimize the free parameter against the theorem's OWN objective instead of debugging the convention.
- Additive fiber/thread rendering of a foliation (Hopf, or any S¹-bundle-like structure):
- A 'compression cascade' — the same object at 3+ stages of a limiting/optimization process, stacked vertically, rendered with ONE global tone map — tells a limit-theorem story a single frame can't.
- Six-vertex/ASM sampling: a config IS an integer ±1 height function; the ice rule falls out for free.
- Palette-by-CLASS-FREQUENCY, re-confirmed on a 6-species field: — measure the vertex-type histogram BEFORE picking colours (four ferro types ~19% each, two c-types ~11% each here).
- Internal DLA vectorizes via the ABELIAN property: step a whole BATCH of walkers in lockstep, refilling the batch from a shared deposit budget as walkers settle.
- When a field's interior is GENUINELY smooth at your render scale, don't fake texture there — add an honest SEPARATE layer instead, and trust a parallel ideation pass to flag the risk before you build.
- FPP geodesic-discharge tree: sparse Dijkstra + a single reverse-topological pass gives the 'river network' for free, and the RAW-log palette beats histogram-equalisation for a space-filling tree.
- A 5-lens-then-synthesize parallel ideation pass, run as a background workflow BEFORE any pixels are pushed, paid for itself by catching a register collision.
- FOLD-DENSITY weighting draws a caustic for free — weight each ray/geodesic sample by `1/(perpendicular spreading to its neighbour)` and the envelope blazes on its own.
- RESOLUTION-STABILITY trap: a thin-locus detector that's clean at ~900² can EXPLODE into a filled blob at 4096² — compute the 1-D locus at MODERATE res, keep the largest component, then UPSAMPLE the mask.
- Symmetry you WANT: put the source at a symmetry point to reveal a symmetric locus face-on.
- A higher-order 'rank' field is a one-liner that unfolds a whole nested mandala — `rank(x)=#{sources closer than the reference}` gives every Brillouin/Voronoi shell at once.
- Memory-lean geodesic/ray FANS: compute the neighbour-spreading row-by-row (per arclength t), never hold five full (T,N,3) copies.
- scikit-fmm gives isotropic eikonal wavefronts with masked obstacles — round ripples, not the octagonal ones 8-connected Dijkstra produces.
- Triptych cohesion across THREE different registers: one deep-black void + a shared two-accent code (warm caustic/leading GOLD + a single cool CYAN for the actual fork-line/special-locus).
- A sweep of independent memory-heavy sparse solves (eigsh with different shift `sigma`, or any per-parameter direct solve) must run ONE SHIFT PER SUBPROCESS, not a Python loop in one process.
- Bilinear/point splat with a CLAMPED index: compute the fractional weight from the UNCLIPPED floor, never from the clipped index.
- Put the structure where your solver is ROBUST, not where the theory is prettiest.
- Two deep OT facts are free visual concepts. — (1)
- KDTree candidate-restriction makes Voronoi/power diagrams scale to 8192².
- Curve-shortening flow render craft. — Save snapshots at GEOMETRIC area fractions (not equal time)
- An oscillatory catastrophe integral is a FOURIER TRANSFORM in one variable — compute it with an FFT, not per-pixel quadrature.
- Colour a complex WAVE field by its phase; let SATURATION carry amplitude.
- Bloom ONLY the true foci (high mask threshold), not everything bright. — A gentle bloom over `mask=smoothstep(0.72,1,luminance)·rgb` gives the caustic focus a radiant halo (reads as focused light)
- DBM/DLA growth's classic failure = the leader branch races to the φ=1 boundary and then CRAWLS ALONG it
- Render a DBM/DLA cluster as a TREE of tapered glowing strokes, not pixels.
- LINE INTEGRAL CONVOLUTION is the way to render a VECTOR FIELD as brushed light
- A recursive-subdivision fractal only shows visual variety if SOME cells are allowed to freeze early.
- A substitution/rep-tile recursion seeded from a single root orientation biases the WHOLE composition, even when the tiling itself is still valid.
- Multiplicative cascades need a FIXED weight multiset (randomly permuted per cell), not a broad per-cell Dirichlet draw, to keep a sharp multifractal spectrum after many levels.
- Rendering a.e.-silence (a measure/field that is genuinely near-zero almost everywhere) needs a STEEP luminance exponent, not percentile normalization alone.
- A genuine finite-difference PDE eigensolve (sparse Dirichlet Laplacian, eigsh(sigma=0)) on an irregular blob domain is cheap (~320² grid, seconds) and gives an honest, uncached field.
- A "too slow to vectorize" verdict deserves a second look before abandoning an idea.
- Point-density alone cannot render a line, even a genuinely deterministic and "coherent" one, once its slope exceeds a few pixels per step.
- A fair Kolmogorov-complexity / compressibility comparison needs the SAME display transform on both sides, and a period long enough to hide from a glance but short enough for the compressor's dictionary.
- A memory-streaming histogram beats storing all samples. — Solving w-roots over a dense (x,θ)
- To symmetrise a density field, transform the POINT CLOUD, not the rendered image.
- Anti-alias sample-grid moiré with jitter on the RIGHT axis + a sub-pixel blur.
- A linear change-of-chart can impose a symmetry the object HAS but the default embedding hides.
- When the natural companion piece is inherently weak, swap register within the SAME object.
- Relative residual, not absolute, for 'does this root satisfy P=0?' — Evaluating P(z,w)
- A locus you can compute in CLOSED FORM should be DRAWN in closed form, not recovered from a noisy field.
- When a "sanity value" is off by a clean factor (2×), it's almost always a normalization convention, not a bug — check whether it changes the ARTWORK before chasing it.
- A degree-N polynomial given by its ROOTS (a big product) must not be rooted again via `np.roots` on expanded coefficients — the coefficients span 1e40+ and float64 invents complex roots.
- numpy 2.x removed `np.trapz` — (rename to `np.trapezoid`)
- Two triangular/spectral pieces can coexist in one triptych if one is pure POINTS and the other is a connected MESH, and they point opposite ways.
- Max-composite (not additive) bead splatting kills finite-sample pile-up streaks.

---

## Tech / environment notes
- python3 + numpy + scipy + Pillow (+ matplotlib if needed) — `pip install` fresh
  each session; no venv committed.
- **WebFetch is BLOCKED** for `philosophy.stackexchange.com` / `mathoverflow.net`.
  Workaround — curl the Stack Exchange API:
  `curl -s "https://api.stackexchange.com/2.3/questions?order=desc&sort=hot&site=philosophy&pagesize=30"`
  (`sort=hot` for philosophy, `sort=activity` for MathOverflow).
- **numpy 2.x removed `ndarray.ptp()`** (use `np.ptp(arr)`) **and `np.trapz`**
  (use `np.trapezoid`) — both are silent AttributeErrors mid-render.
- Default render stack: dark field, additive Gaussian splats for bloom, filmic
  tone map (`1−exp(−k·x)`) then gamma; supersample ×2 then LANCZOS downscale.
- AP search: rolling-AND with explicit edge-zeroing (`np.roll`, then blank the
  wrapped border). ℤ[√−2] embedding: `z = a + b√−2 ↦ (a, b·√2)`.

---

## How to update this branch (end of every routine run)
```bash
git fetch origin memory
git worktree add /tmp/mem origin/memory      # isolated checkout, won't touch your art branch
cd /tmp/mem
# edit carry_forward.md: add a Run-log row, update Open threads / Craft notes
git add carry_forward.md
git commit -m "memory: <branch-id> — <one-line summary>"
git push origin HEAD:memory
cd - && git worktree remove /tmp/mem
```
