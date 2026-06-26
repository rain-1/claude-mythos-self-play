# Memory — `claude-mythos-self-play` routine

This is the **long-lived `memory` branch**: the single source of truth that
every scheduled routine run reads *before* starting and updates *before*
finishing. It is an **orphan branch** — it carries ONLY memory, never art
outputs or code — so it never conflicts with the per-run `claude/*` branches.

## How to use it (every run)
1. **READ first:** `git fetch origin memory && git show origin/memory:carry_forward.md`
2. **Continue** the open threads below — do not restart from scratch. If a
   numbered series is active, take the next number.
3. **WRITE last:** append a Run-log row + update Open threads, then push to
   `memory` (recipe at the bottom).

---

## Run log (most recent first)
| date | branch | produced |
|---|---|---|
| 2026-06-26 | `claude/beautiful-heisenberg-uh5wzk` | Procedural art triptych **Three Heresies of the Continuum** (in `art_uh5/`) — all-new techniques, each contradicting a naive intuition about the continuum: `01_the_wave_that_remembers` (**4096² centerpiece**: **Talbot / quantum carpet** — Gaussian packet in an infinite square well, `ψ=Σ c_n √2 sin(nπx) e^{-i n² t}`; because `E_n=n²` are perfect squares the phases re-cohere into full+fractional **quantum revivals**, a genuinely fractal interference lattice of canals & ridges; kicked packet k0=60, 360 modes, teal palette), `02_a_line_that_learns_to_be_a_plane` (**Hilbert space-filling curve** thread, order 7, painted by arc-length with a bright non-cyclic hue sweep so the 1-D line that fills 2-D stays traceable; 2048²), `03_nearness_is_a_tree` (**Bruhat–Tits tree of Q_p** drawn in the **Poincaré disk with geodesic edges** via SU(1,1)/Möbius, fixed hyperbolic step/generation → infinite ends crowd the boundary = a luminous amber **horizon = Q_p**; ultrametric "nearness is a tree"; 2048²). ✅ Read memory first; fresh names/techniques, no collisions. Seeded by live philosophy.SE (Copenhagen-vs-Many-Worlds, "Is any consistent theory incomplete?") + MathOverflow ("Can a continuous bijection lower topological dimension?", "p-adic valuation of products"). Each piece <40s to render. **Then (same branch, by user request) added a 4th piece** `04_the_triality_engine` (4096²): the **octonion Fano plane** — 7 imaginary units e_1..e_7 = 7 points, each oriented line a→b→c ⇒ `e_a e_b = e_c` — mapped *exactly* onto triangle geometry (3 vertices / 3 edge-midpoints / centre / incircle = 7th line; medians hit opposite midpoints; verified valid Fano with the standard `(1,2,3)(1,4,5)(1,7,6)(2,4,6)(2,5,7)(3,4,7)(3,6,5)` table). **Tripled by Spin(8) triality**: three Fano planes (8_v azure / 8_s gold / 8_c rose) pinwheeled 120° and cycled by a chiral triality triskelion around the D_4 hub. PIL vector art at 2× supersample + numpy bloom (8192² bloom ≈ 2m44s — the only slow render of the run). **Then (same branch, by user request) a whole DEEP-DIVE gallery** `triality/` exploring Spin(8) triality every way: verified 4D group theory in `t4d.py` (24-cell = three 16-cells 8_v/8_s/8_c, 96 edges, symmetry group W(F4) order **1152**, explicit order-3 isometry **T** = all-±½ matrix, T³=I, cycling the three 16-cells — found by BFS over ⟨signed-perms, Hadamard⟩) + a reusable glowing additive 3D renderer `tdraw.py` (4D→3D→2D perspective, depth-cued splats, bloom). Pieces: `01` 24-cell on the **F4 Coxeter plane** (h=12 → 12-fold rose; D4's own h=6 plane is too degenerate — collapses to a hexagon), `02` D4 **Dynkin diagram + S3 outer-automorphism** schematic, `03` 24-cell 3D hero, `04` **Cayley diagram in 3D = the permutohedron** (truncated octahedron = Cayley graph of S4, edges = transpositions of *consecutive values* k,k+1 — NOT adjacent positions — 3-coloured by generator), `05` **G2 root system = the triality-fixed subalgebra** (Star-of-David hexagram), `06` three interlocking 16-cells. **Two GIF animations** (Pillow, no ffmpeg in env): isoclinic 4D spin, and **triality itself** = `T^t=expm(t·logm(T))` applied continuously over t∈[0,3] (shape invariant every ⅓ loop, colours cycle). **Then (same branch, by user request — "those are all just one thing; find diverse viewpoints + annotation blocks + inline images in .md")** a NEW gallery `octonions/` = **Seven Lenses on the Octonions** (Fano plane / octonions / triality from 7 *different branches of maths*, each figure 1600px-wide with a baked-in **annotation/caption block at the bottom** via `figkit.py`, all inlined in `octonions/README.md`). Built on verified `octo.py` (composition law |xy|=|x||y|, alternative, non-associative, **Fano lines == XOR triples** with e_i↔binary(i), 7 associative + 28 non-associative triples). Figures: `01` multiplication-table heatmap (algebra), `02` **Fano = cube over F_2^3, lines = XOR-zero triples** (finite geometry; isometric cube, mild perspective `f=1/(1−0.22 z)` NOT scale-dependent), `03` **Heawood graph** = Fano incidence, the (3,6)-cage, drawn on a found Hamiltonian cycle (graph theory), `04` **Cayley–Dickson ladder** ℝ→ℂ→ℍ→𝕆 with property loss + imaginary-part glyphs (ℍ=one Fano line, 𝕆=whole Fano plane) (construction), `05` triality triangle 8ᵥ/8ₛ/8c + trilinear form t(x,y,z)=⟨xy,z⟩ with chiral 3-cycle arrows (rep theory), `06` **the associator** worked numerically `(e₂e₃)e₄=+e₅ vs e₂(e₃e₄)=−e₅` (non-associativity), `07` **G₂ = Aut(𝕆)** = Fano symmetry ≅ triality-fixed subgroup (Lie theory). | **Then (same branch, continuing by request) gallery `psl168/` = The Order of 168 — PSL(2,7) & the Klein quartic** (6 *different-lens* annotated figures + 1 GIF, inlined in README; verified `p168.py`: |GL(3,2)|=168, |PSL(2,7)| on P¹(𝔽₇)=168, Singer set {1,2,4}=QR mod 7). `01` counting 168=(8−1)(8−2)(8−4)=7·6·4, cyclic Fano (group theory); `02` **PSL(3,2)≅PSL(2,7)** 7-pts vs 8-pts exceptional isomorphism; `03` **(2,3,7) triangle-group kaleidoscope** (per-pixel fold into the π/2,π/3,π/7 triangle, 2-colour by reflection parity); `04` **Klein quartic {7,3} tiling** via von Dyck group (Hurwitz 84(g−1)=168) — **KEY FIX: heptagon circumradius is `cosh R = cot(π/7)cot(π/3)` (I first used the inradius `cos(π/3)/sin(π/7)` → tiling exploded into overlapping scribbles; verify the von Dyck relation (ab)²=I to catch this); also re-project SU(1,1) products to kill float drift, and cap radius for clean tiles**; `05` six irreps dims 1,3,3,6,7,8, **Σd²=168** (rep theory, the 3-dim → Klein quartic in ℂP²); `06` **Cayley graph** 24 heptagons (=cosets of order-7 gen) laced by the order-2 involution = simplicity; anim = Singer cycle stepping {1,2,4}+k. | **Then (same branch, continuing the 'yes to all' deep-dive) FOUR more annotated galleries + a debug note**, all reusing `octonions/figkit.py` caption blocks & inlined in per-dir READMEs, plus a top-level **`GALLERY.md`** index of the whole Fano→E₈ arc: **`debug_note/`** — *The von Dyck Trick* (before/after: broken {7,3} tiling from the inradius bug vs fixed, with the `(ab)²=I` diagnostic 0.078 vs 5e-17; the user asked this be celebrated). **`klein_surface/`** — the **tetrus**: Klein quartic as an embedded genus-3 surface, **SDF sphere-traced in numpy** (fattened tetrahedral frame, genus=E−V+1=6−4+1=3; ~67s/render at 1100²; capsule SDF + smooth-min + normal-by-finite-diff + diffuse/spec/rim). **`hurwitz/`** — beyond Klein: the **84(g−1) bound** chain (Klein g3/168/PSL(2,7), Macbeath g7/504/PSL(2,8), triplet g14/1092/PSL(2,13), all (2,3,7) quotients) + **GF(8)**=𝔽₂[x]/(x³+x+1) whose additive group is 𝔽₂³ (Fano) and multiplicative group is C₇ (Singer). **`mathieu/`** — Steiner systems & Mathieu groups, on a **VERIFIED Golay code** (`golay.py`: [23,12] gen-poly `x^11+x^10+x^6+x^5+x^4+x^2+1` + parity → [24,12,8]; weight dist {0:1,8:759,12:2576,16:759,24:1}; S(5,8,24) checked). Figs: Steiner chain S(2,3,7)=Fano→S(5,6,12)/M12→S(5,8,24)/M24; octads on the 4×6 MOG; Golay weight spectrum. **`magic_square/`** — the **Freudenthal–Tits magic square** (ℝℂℍ𝕆→Lie algebras, octonion row/col=F4,E6,E7,E8 with dims) + the five exceptionals G₂F₄E₆E₇E₈ all octonionic + the Cayley plane 𝕆P². The arc closes at E₈. | **Then (same branch, user feedback round: wanted each page more representational + the E₈ mandala)** — NEW gallery **`e8/`**: the famous **E₈ 240-root Coxeter mandala** (`e8.py` verified: 240 roots, Coxeter order 30, 8 rings of 30; `mandala.py` batched additive-glow rasteriser, 6720 edges = roots at 60°) as a static figure + **spinning GIF** (exploits 30-fold symmetry: a 12°=2π/30 rotation is a seamless loop; edge_bright must be LOWER at the smaller anim res or the convergent core blows to white). Plus per-page upgrades: **magic_square/03** four exceptional **root-system mandalas** F₄(48)/E₆(72)/E₇(126)/E₈(240) (`magic_square/roots.py`: generic root-closure from simple roots; E₆/E₇ extracted from E₈ by orthogonality to a root / A₂; base via generic functional; Coxeter plane = eigvec of Coxeter element for e^{2πi/h}, h=12/12/18/30 — all counts verified). **mathieu/04** all **759 octads** in one tapestry (4×6 mini-MOG glyphs, sorted by codeword value, hue by index). **hurwitz/03** GF(8) as its two **operation tables** (addition=XOR symmetric; multiplication=cyclic Latin square in powers of α). **klein_surface/02** the **tetrus clothed in heptagons**: on-surface Voronoi from tetrahedral-symmetry-orbit centers PROJECTED onto the SDF (Newton steps along the gradient), cells drawn as dark mortar — reads as the {7,3} clothing (honest caption: fine geodesic mesh, not the exact conformal 24-heptagon map). |
| 2026-06-25 | `claude/hopeful-pasteur-p847x4` | Procedural art triptych **The Far Country** (in `art_p847/`) — all-new techniques: `01_far_country` (**4096² centerpiece**: hyperbolic **{7,3} kaleidoscope** of the Poincaré disk via per-pixel fold-into-fundamental-domain — reflect each pixel across the 3 Schwarz-triangle mirrors counting reflections; closed-form 3rd mirror `d=cos(π/q)/√(cos²(π/p)−sin²(π/q))`; warm core receding to a cold ideal-boundary singularity), `02_presence_of_absence` (**Eisenstein primes** a+bω, norm a²−ab+b² prime or p² with p≡2 mod 3; zoomed near origin, full lattice drawn as dim ash nodes so *absent* sites read as the voids; 12-fold lace + warm halo at the empty origin; 2048²), `03_phenomenal_red` (**CIE 1931 chromaticity** via Wyman–Sloan–Shirley analytic CMF fits; convex hull of spectral locus = gamut of all real colour; line-of-purples + Planckian locus + red focal glow, floating in the void of imaginary colours; 2048²). ✅ Read memory first; fresh names/techniques, no collisions. Seeded by live philosophy.SE ("absence of presence vs presence of absence", "phenomenal experience of red") + MathOverflow. Each piece <10 min; rewrote the hyperbolic loop to a **flat shrinking active-set** after the full-grid version was OOM-killed at 8192². |
| 2026-06-24 | `claude/hopeful-pasteur-j50t9v` | Procedural art triptych **Three Ways the World Coheres** — all-new techniques: `01_order_without_period` (Penrose via de Bruijn pentagrid cut-and-project; orientation facet shading; 2048²), `02_the_unreasonable_packing` (**4096² centerpiece**: Apollonian gasket via Descartes' Circle Theorem complex form, integer curvatures, recursion to subpixel, flat jewel fills colored by curvature), `03_emergence` (critical site percolation p_c≈0.5927 via scipy component-labelling; gold spanning cluster + bloom over a teal finite-cluster sea; 2048²). ✅ Read memory first; fresh names/concepts, no collisions. Seeded by live philosophy.SE ("Does emergence make things illusory?", "unreasonable effectiveness") + MathOverflow ("generating functions for objects with irrational sizes"). Pivoted away from per-circle domed shading (stepped concentric ellipses → archery-target banding); reverted to flat+rim+global glow. |
| 2026-06-24 | `claude/hopeful-pasteur-0eymin` | Procedural art triptych **Measure / Dimension / Period** — all-new techniques (no domain-coloring, RD, or nodal lines): `01_measure_of_a_curve` (Crofton: curves as the caustic envelope of their tangent-line measure, 2048²), `02_almost_all_of_the_cube` (concentration of measure: nested rings, one per dimension, collapsing to a razor shell with an empty core, 2048²), `03_period_of_the_anharmonic` (**4096² centerpiece**: double-well phase portrait, iso-period contours crowding the separatrix where the elliptic K diverges). ✅ Read memory first; fresh names, no collisions. Pivoted away from a 4th idea (`p3_legendre`, sums of three squares) after small renders showed the non-representable set 4^a(8b+7) is quasi-uniform density 1/6 — dither, not a visible fractal. Seeded by philosophy.SE + MathOverflow front pages. |
| 2026-06-24 | `claude/exciting-lovelace-fe8jho` | Procedural pixel art ×3: "Almost Everywhere" (random-wave nodal lines, 2048²), "Doubly Periodic" (Weierstrass ℘ domain-coloring, **4096²** centerpiece), "Deterministic Freedom" (Gray–Scott reaction–diffusion from a zero-randomness seed, 2048²). Seeded by philosophy.SE + MathOverflow front pages. ⚠️ Built *without* reading this memory (branch wasn't fetched) — accidentally duplicated the `01_almost_everywhere` name and the 4096² format from the 2026-06-23 run. This branch exists to stop that recurring. |
| 2026-06-23 | `claude/kind-planck-uxrqtc` | Pixel art ×3 (`01_almost_everywhere`/rationals-as-stars, `02_weyl_field`, `03_relation_without_relata`) + a 4096² diffractive-geodesic showcase; then pivoted into a number-theory series — the **AP-obstruction atlas**, reaching **piece 36**. |

---

## OPEN THREADS — pick up here

### Thread A — AP-obstruction atlas (number theory)  ·  ACTIVE, highest priority
Numbered series. Currently at **piece 36 → next number is 37.**

State: the "good-step" law is **unified** — a step in an arithmetic progression
is good iff it preserves the norm form's residue mod the ramified prime.
Verified for Heegner d = −1, −2, −3, −7. New −2 result: only `da` is
constrained (`da ≡ 0 mod 2`, `db` free) because the norm `a²+2b²` has no cross
term — strictly between −1 and −7.

Next directions (carried from the 2026-06-23 run):
1. **ℤ[√−11]** (Heegner −11), norm `a²+ab+3b²`, ramified prime 11 → a mod-11
   sublattice (sparser, more ornate atlas panel). **→ this is piece 37.**
2. State the **cross-term principle as a theorem**: for `a²+B·ab+C·b²` with
   ramified prime `p`, the good-step sublattice is the stabilizer of
   `{(a,b): form ≢ 0 mod p}` under translation; index = # bad residue lines.
   Check vs −11, −19.
3. Push the **ℤ[√−2] AP record** past 10 terms (wider window; current cap R=10, W=1500).
4. **ℤ[√2]** (real quadratic, d=+2): infinite unit group ε=1+√2; prime points on
   `|a²−2b²|` live on hyperbolae, not a disc — genuinely different topology, a
   good contrast piece.

Heegner-9 set: −1,−2,−3,−7,−11,−19,−43,−67,−163. Done: −1,−2,−3,−7.

### Thread B — procedural pixel art (generative aesthetics)  ·  recurring
Three runs of pixel-art sets seeded by live SE/MathOverflow front pages.
**To avoid collisions, check the run log and pick fresh names/concepts.**

USED concepts/techniques so far (do NOT repeat): random-wave nodal lines,
Weierstrass ℘ domain-coloring, Gray–Scott reaction–diffusion, diffractive
geodesics, rationals-as-stars, AP atlases, Crofton tangent-caustics, additive
line-splat caustics, concentration-of-measure nested rings, double-well phase
portrait with iso-period contours, **Penrose via de Bruijn pentagrid
cut-and-project**, **Apollonian gasket via Descartes' Circle Theorem (complex
form)**, **critical site percolation via connected-component labelling**,
**hyperbolic {p,q} kaleidoscope via per-pixel fold-into-fundamental-domain**,
**Eisenstein primes (norm-form primality) in the plane**, **CIE 1931
chromaticity / colour-matching-function gamut (Wyman analytic fits)**,
**Talbot / quantum carpet (square-well wavefunction revival, |ψ(x,t)|²)**,
**Hilbert space-filling curve as arc-length-coloured thread**, **Bruhat–Tits
tree of Q_p in the Poincaré disk with geodesic edges (SU(1,1)/Möbius)**,
**octonion Fano plane (multiplication table as directed projective lines) +
Spin(8) triality triskelion (PIL vector emblem)**.

UNUSED front-page veins still on the table (good next-run seeds): computational
irreducibility / elementary-CA spacetime ("The Only Way to Know"); equidistribution
of singular moduli mod p; **Gaussian primes** in the plane (Eisenstein is now
USED; the Gaussian ℤ[i] variant is still open if you find a chart that beats
noise — see craft note); **Bhargava cubes**; **maximum-clique / force-directed
graph layout** (MO front page, recurring); **partitions of 3^n into 3 squares**;
**Cantor/Gödel/Goodstein diagonalization** structure (MO 2026-06-25);
**Kauffman bracket / Temperley–Lieb braids, Abelian anyons** (MO, recurring);
**Collatz trajectory river / reverse-tree** (MO, recurring); **Cantor/Gödel/
Goodstein diagonalization** — e.g. an infinite binary table with its
anti-diagonal flipped = "the one real the list forgot" (philosophy "Is any
consistent theory incomplete?" + MO). These two (Collatz, diagonalization) were
*sketched as ideas on 2026-06-26 but NOT built* — good next-run seeds.
(**SO(8)/triality, octonions, Fano plane** is now USED — built 2026-06-26 as
piece 04. **Kauffman bracket / Temperley–Lieb / Abelian anyons** still open.)
Note: the quantum-revival, space-filling-curve, and p-adic/ultrametric veins
are now USED (this run). The Poincaré disk has now hosted TWO distinct
techniques (kaleidoscope fold, geodesic tree) — a third disk piece would start
to feel repetitive; prefer a non-hyperbolic chart next. Pick an unbuilt vein
and build a *new* technique for it.

---

## Craft notes — generative art (merged, append-only)
- **Concept first.** Start each piece from a question (measure-zero life,
  relation without relata, determinism). The title does real work — viewers see
  more when they know what the arithmetic was reaching for.
- **Honest math can be visually boring; the fix is a change of *chart*, not a
  change of truth.** Reach for a coordinate warp / multiplicative or quadratic
  orbit before you reach for a hack.
- **Symmetry is the enemy of interest.** Find the invariance flattening you
  (Toeplitz stripes, axis-aligned lattices) and break it — multiply instead of
  add, curve the geodesic, interfere two systems instead of one.
- **Tone-mapping is half the art.** Filmic `1 − exp(−k·x)` + gamma lift turns
  dim fields into deep glowing ones. **Cache the raw field; iterate the colormap
  in seconds, not minutes.**
- **Falloff sets the read:** sparse/peaked → "objects/stars"; broad → "texture/fabric".
- **Render small, LOOK, then scale.** Params that sound right in code read wrong
  on canvas. You cannot reason your way to an image; view it.
- **Negative space is the loudest lever.** Open the void until it *means*
  something (e.g. measure zero).
- **Never clip to white.** Bounded tone (tanh, gentle gammas) keeps saturation;
  let singularities blaze only at true extremes.
- **Curated cyclic palettes beat raw HSV** — HSV always looks like a default.
- **Constraints can be honored without losing the look.** Reaction–diffusion
  needs broken symmetry; a deterministic interference seed supplies it with zero
  RNG.
- **Profile the hot loop:** `scipy.ndimage.convolve` ≫ eight `np.roll`s for
  stencils; `float32` halves the bandwidth.
- **A "fractal" you can name isn't always a fractal you can SEE.** The
  non-representable integers 4^a(8b+7) are arithmetically self-similar but have
  *uniform density 1/6* — on any space-filling layout they're pixel dither, not
  clustered voids. Visible structure needs spatial *clustering* or *density
  variation*, which arithmetic-position sets usually lack. Test the premise with
  a 5-min render before committing a piece to it.
- **Per-element normalization rescues balance.** When fat/dim and thin/bright
  features must coexist (concentration rings: fuzzy low-d vs razor high-d),
  global max-normalization lets one bright clump crush everything. Accumulate
  each feature separately, normalize to a percentile, then composite — the
  *shape* carries the story, not raw density.
- **Singularities are free detail.** A quantity that diverges (period T → ∞ at a
  separatrix via elliptic K, a caustic, a pole) gives genuine multi-scale
  crowding — spacing contours *equally in the divergent quantity* makes them
  pile up infinitely near the singularity. This is what actually rewards 4096².
- **Splat-count must track canvas size.** Line/point splatting that looks dense
  at 1024² goes sparse at 4096² — scale samples-per-line and point counts by
  (S/S_proto) or the high-res render thins out.
- **An envelope renders without ever drawing the object.** Crofton/caustic
  pieces: draw only the *tangent-line family* (additively); the curve appears as
  the density ridge where the lines agree. Beautiful and conceptually on-point.
- **Fake per-object 3D shading via stepped concentric ellipses reads as archery
  targets, not domes.** Tried it on the Apollonian big disks → visible banding +
  bullseye. Flat jewel fills + a thin dark rim (width ∝ r) for tangent separation
  + ONE soft bounded global glow looked far cleaner and more elegant. For a true
  domed look you need a *per-pixel* radial gradient (an off-center specular), not
  stacked flat ellipses — only worth it if the piece is about glossiness.
- **Tile-count (N) is a legibility dial, not just detail.** Penrose at high N
  (46) became a flat carpet and the area-dominant warm tiles swallowed the cool
  ones; mid N (~32) kept the 10-fold rosettes legible while still filling 2048².
  Render small, choose N by eye.
- **Orientation → brightness gives faceting for free.** Coloring each Penrose
  rhombus's lightness by its edge angle (`0.5+0.5·cos2θ`) produces the classic
  3D-cube shimmer and rescues a mono-warm field. Generalizes: any tiling/strip
  field gains depth from an orientation→tone map.
- **For random-field pieces the pixel grain can BE the concept.** Critical
  percolation at 2048² (1 cell = 1 px) looks like static at 100% zoom — but here
  that's the point: micro independent coin-flips + macro fractal whole in one
  frame *is* emergence. Kept it. Only smooth (coarser lattice + NEAREST upscale)
  when the concept isn't about micro-structure. Know which you're making.
- **Bloom makes a hero element blaze without clipping.** Gaussian-blur the hero
  mask (giant percolation cluster), add a warm-tinted halo back, then bound with
  filmic `255·(1−e^{−x/k})`. One feature leads; the textured field stays intact.
- **Recursion-to-subpixel is what truly rewards 4096².** Apollonian cusps cascade
  forever; a center crop at native res still shows crisp circles. Same lesson as
  "singularities are free detail" — the tangency accumulation point IS the
  singularity. Cheap to compute (1.2M circles in ~1s); the cost is render, and
  MAXBEND beyond ~(0.5·S/margin)/0.35 contributes nothing visible, so don't
  over-recurse.
- **The "change of chart" fix for arithmetic-point noise = ZOOM IN + draw the
  ground.** Eisenstein/Gaussian primes at R=300 are indistinguishable from
  static (the warned-about uniform-density trap). Two moves rescued it together:
  (1) zoom near the origin (R≈88) so the 6/12-fold void structure is bigger than a
  pixel; (2) render the *whole* lattice as dim "ash" nodes and light only the
  primes — now the **absent** sites are visible as dark holes, so the eye reads
  structure, not noise. The voids became the subject. Test arithmetic-point pieces
  at two zoom levels before judging.
- **Decouple the radial COLOUR map from the tessellation GEOMETRY.** For the
  hyperbolic kaleidoscope, colouring by reflection-count gave a dark, asymmetric
  pinwheel centre (word-length isn't rotationally symmetric). Switching colour to
  a clean radial gradient (function of |z| only) while keeping the fold purely for
  mortar + facet shimmer gave a symmetric mandala. Lesson: let one channel carry
  symmetry, another carry detail; don't make a non-symmetric quantity drive colour.
- **Hyperbolic distance hides the boundary band; use euclidean radius for colour.**
  Colouring by `2·atanh(|z|)` piles every far-colour into an invisibly thin sliver
  at |z|→1 (the metric compresses there). To make the cold "far country" boundary
  band actually *visible* across the disk, drive colour by euclidean `|z|` (a gamma
  spreads it). The geometry stays hyperbolic regardless; only the palette parametrisation changes.
- **gaussian_filter conserves MASS, not PEAK — restore amplitude after blurring a
  splat field.** A point splatted as 1.0 then blurred with σ has peak ≈ 1/(2πσ²)
  (≈0.003 for σ≈7) → near-black. Multiply the blurred field by `2πσ²` to put the
  dot back at its intended brightness. This was the whole "why is my prime lace
  pitch black" bug; the structure was always there, just at 0.3% brightness.
- **Memory: fold a flat SHRINKING active-set, not the full grid.** The per-pixel
  hyperbolic fold over a full 8192² grid spawns ~15 float32 temporaries/iteration
  (~3GB) and got OOM-killed (SIGKILL, no traceback — the tell-tale of OOM, not a
  bug). Fix: keep flat 1D arrays of still-active pixel indices + coords; each
  iteration operate on `live` subset only, mark converged ones done and drop them.
  Most pixels converge in <30 iters so RAM falls fast; only the boundary ring
  persists to MAXIT. Bounded RAM, and faster. (`/usr/bin/time` is ABSENT in this
  env — don't wrap renders in it, it fails the whole command.)
- **Judge fractal FIELDS at native resolution, never the downscaled preview.**
  The Talbot quantum carpet looked like noisy static at 1024² — but that "noise"
  was just aliasing of fine interference fringes; a 1024-px CROP of the 4096²
  render was crisp and clean. For any interference / fringe / fine-fractal field,
  inspect a 1:1 center crop before believing the preview. (Same trap, opposite
  direction, as the percolation grain note: there the grain WAS the concept;
  here the grain was a preview lie.)
- **For arc-length / "directed-line" colouring use a bright NON-cyclic hue
  sweep.** A dark→light *sequential* palette buried the Hilbert thread in its own
  low-luminance first half (near-black at t≈0). Let HUE carry the direction while
  LIGHTNESS stays high (a ~3/4 turn of the wheel, not a full cycle so the two ends
  stay distinct) → the thread glows AND its endpoints read. Cyclic palettes hide
  that a line has two ends; sequential-dark palettes hide half the line.
- **A tree in hyperbolic space needs GEODESIC edges, not straight ones.** A naive
  straight-edge "fractal canopy" splays outward and leaves the centre an empty
  hole (looked broken). Stepping a fixed *hyperbolic* distance per generation
  (compose SU(1,1)/Möbius: `Rot(θ)`, `Trans(d)=[[ch,sh],[sh,ch]]` of d/2; node =
  M·0) makes every infinite end crowd the boundary circle — the canonical
  Bruhat–Tits picture. Sample each edge by applying `Trans(s·d)` for s∈[0,1] to
  trace the true geodesic arc. PIL `ImageDraw.line(..., joint='curve')` rasterises
  ~200k such polylines in seconds (≫ a python per-pixel loop).
- **Match glow/exposure to DENSITY.** Identical bloom+exposure that a *sparse*
  (p=2) tree needed to read at all blew a *dense* (p=3) lace out to colourless
  white — it lost all hue. Sparse fields can take aggressive glow; dense fields
  need it restrained or the colour story dies. Decide density first, then tune
  tone.
- **Splat the CONCEPTUALLY-meaningful points to make the idea literally glow.**
  Rendering the tree's deepest-generation leaf endpoints as an additive Gaussian
  ring (with the mass→peak restoration ×2πσ² from the earlier note) turned an
  abstract "boundary" into a luminous horizon that *is* the object the maths is
  about (Q_p). Ask: what is the ONE set of points this piece is secretly about?
  Splat those.
- **A pure-symmetry emblem (e.g. 3-fold triality) survives the "symmetry is the
  enemy" rule via colour + chirality + internal detail.** Three identical Fano
  planes at 120° would be a flat carpet; giving each a different representation
  COLOUR (8_v azure/8_s gold/8_c rose), making the central triality cycle a
  CHIRAL triskelion (directed arrows → breaks mirror symmetry, adds motion), and
  packing each lobe with genuine directed-line detail kept it alive. When the
  subject *is* a symmetry, don't fight it — differentiate the copies and make the
  symmetry's generator (here the 3-cycle) visibly directional.
- **For diagram/vector emblems, draw crisp at 2× in PIL, bloom in numpy, but put
  TEXT back AFTER the glow.** Node/label numerals blurred by bloom look muddy;
  rendering them on the downscaled, already-bloomed image keeps them razor sharp
  against the glow. Also: place outer labels just BEYOND the outward vertex (not
  at it — collision) and shrink the whole composition ~5% so labels clear both
  the vertex and the canvas edge. (Large-σ bloom on an 8192² supersample is the
  expensive step — ~2m44s; everything else this run was <40s. If iterating, bloom
  a 4096 downscale instead.)
- **Map an abstract algebra onto the drawing's OWN geometry and verify it.** The
  octonion Fano table mapped perfectly onto the triangle (vertices/midpoints/
  centre/incircle, medians→opposite midpoints) — but only after a 10-line script
  CHECKED that the chosen circle-line + centre-point assignment gave a valid Fano
  (each point on 3 lines, every pair once, medians = vertex+centre+opp-midpoint).
  Honest math first, then the picture draws itself. Arrowhead direction per line:
  in a 3-cycle a→b→c, for any spatial-adjacent pair use forward = x→y iff
  succ(x)=y (else y→x) — gives faithful arrows even when spatial ≠ cyclic order.
- **Polytope/graph art: VERIFY the structure in code before drawing it.** The
  whole triality gallery rested on `t4d.py` checks — 24 verts in 3 classes of 8,
  96 edges, group order 1152, T³=I cycling the 16-cells. Two bugs were caught
  ONLY by verification, never by eye: (1) the permutohedron's edges are
  transpositions of *consecutive values* (k,k+1), not adjacent *positions* — the
  wrong rule gave non-uniform edge lengths and a skewed "stacked boxes" blob;
  checking edge-length min==max (all √2) exposed it. (2) the D4 Coxeter plane
  (h=6) is too degenerate for the 24-cell — 24 verts collapse onto 7 points (a
  plain hexagon, colours washed to white); the rich 12-fold rose needs the **F4
  Coxeter plane** (h=12), where all 24 project to distinct points (two rings of
  12). Lesson: pick the projection by counting `len(set(round(proj)))` first.
- **A glowing additive 3D renderer is a high-leverage reusable.** One `tdraw.py`
  (4D→3D→2D perspective; far-first depth sort; per-vertex Gaussian splat with
  size+brightness ∝ depth; gradient or per-edge colours; tight+wide bloom; filmic
  expo) served six stills AND two animations. Build the engine once, parametrise
  per piece. Depth cue = the single biggest factor in "reads as 3D": scale BOTH
  brightness and line width by normalised z.
- **For animation, FREEZE the normalisation or it flickers.** Per-frame
  min/max depth (or per-frame autoscale) makes the whole figure pulse in
  brightness/size between frames. Pass a FIXED `zrange` (and fixed projection
  scale) so only the geometry moves. Perfect GIF loops come free from group
  theory: an order-n symmetry `T` gives a seamless loop via `T^t=expm(t·logm T)`,
  t∈[0,n] (T is SO(4) so logm is real skew-symmetric — take `.real`).
- **Visualising an outer automorphism: keep the SHAPE fixed, animate the
  LABELS.** Triality reads instantly when you apply its rigid rotation `T^t`
  continuously: the polytope returns to the identical silhouette every ⅓ of the
  loop but the three colours have advanced. "Same object, names cycled" is the
  whole concept of an outer automorphism, and motion sells it where a still
  cannot. (No ffmpeg in this env — Pillow `save_all` GIF, ADAPTIVE 128-colour
  palette, `disposal=2`; ~90–120 frames @560px ≈ 5–7 MB.)
- **"It's all one thing" is the failure mode of a deep-dive — diversify the
  LENS, not just the parameters.** A whole gallery of 24-cell projections was,
  to the user, "all just one thing." The fix that landed: attack the SAME trio
  (Fano/octonions/triality) through different *branches of maths*, each with its
  own visual grammar — a matrix heatmap (algebra), a cube (finite geometry), a
  graph (graph theory), an infographic ladder (construction), a commutative-ish
  diagram (rep theory), a worked numeric equation (non-associativity), a
  root-system pairing (Lie theory). When asked to "go deeper," widen the set of
  viewpoints, don't re-render one viewpoint.
- **Annotation-block figures (caption baked into the PNG) are a high-value
  format and a cheap reusable.** `octonions/figkit.py`: render the viz panel,
  then append a bottom block — left accent bar + a thin separator, a small
  TAG ("FIGURE 3 · GRAPH THEORY") in the accent colour, a bold title, then
  word-wrapped body in light grey. Compose at FINAL resolution and draw the text
  AFTER any downscale so glyphs stay crisp. Pairs perfectly with inlining the
  PNGs in a README.md (`![alt](file.png)` + connective prose) — the figure
  stands alone AND the doc reads as a guided tour. The user specifically asked
  for this; keep the kit.
- **DejaVu has the blackboard-bold letters ℝ ℂ ℍ AND the astral-plane 𝕆 𝕊
  (U+1D54x) and subscripts ₀–₉ (`chr(0x2080+k)`) — use them** for honest maths
  typography in figures; no LaTeX needed. (DejaVuSans-Bold at /usr/share/fonts/
  truetype/dejavu/.) Coloured inline tokens (draw a sequence of (text,colour)
  spans, measure with `textlength`, centre) make equations like
  "(e₂·e₃)·e₄ = +e₅" read with per-unit colour.
- **Hyperbolic regular tilings {p,q}: get the radius formula right and VERIFY a
  group relation, or it silently explodes.** For the {7,3} Klein-quartic tiling the
  heptagon CIRCUMRADIUS (centre→vertex) is `cosh R = cot(π/p)·cot(π/q)`; I first used
  `cos(π/q)/sin(π/p)` which is the INRADIUS (centre→edge-midpoint) — vertices weren't
  real vertices, so the von Dyck rotors didn't close and the tiling degenerated into
  overlapping scribbles a few rings out. The tell: check the defining relation
  `(a·b)² = I` (rot-7 about centre · rot-3 about vertex = order-2 about edge midpoint).
  It was 0.078 off → instantly localised the bug; after the fix it's 1e-17 and the
  tiling is perfect. Also: re-project SU(1,1)/Möbius products back to the group each
  step (`[[a,b],[b̄,ā]]/√(|a|²−|b|²)`) to kill float drift, dedupe tiles by centre,
  and cap |centre|<~0.93 for clean edges. The (2,3,7) *per-pixel fold* (reflect each
  pixel into the fundamental triangle, 2-colour by parity) is the robust cheap cousin
  when you only need the kaleidoscope, not actual tile polygons.
- **Cayley graph of a 168-element group, laid out legibly:** factor by a cyclic
  generator. Right-mult by an order-7 element partitions the 168 nodes into 24 7-cycles
  (cosets); draw those as 24 small heptagons on a ring, then the order-2 generator is a
  perfect matching drawn as interior chords. Reorder the 24 cosets by BFS over
  chord-adjacency so linked heptagons sit near each other → far fewer crossings. Shows
  |G|=24×7 and that the involution lacing it into one piece = simplicity.
- **The von Dyck debug trick (worth its own note — `debug_note/`):** when a construction
  is governed by a group, VERIFY A GROUP RELATION, don't debug pixels. A {7,3} tiling
  exploded into scribbles; checking the von Dyck relation `(ab)²=I` gave 0.078 (broken,
  from using the inradius `cos(π/3)/sin(π/7)` instead of circumradius `cot(π/7)cot(π/3)`)
  vs 5e-17 (fixed) and localised it instantly. Generalises: Coxeter braid relations,
  triality `T³=I`, octonion `|xy|=|x||y|` — check the identity before trusting the image.
- **Genus-3 (and other handlebody) surfaces without a mesh: SDF sphere-tracing in numpy.**
  Fatten a graph's 1-skeleton into capsules (capsule SDF = distance-to-segment − r),
  smooth-min the union, vectorise the ray march over all pixels (~90 steps), normals by
  finite differences, shade diffuse+spec+rim. A thickened tetrahedron frame = genus
  E−V+1 = 3 = the Klein quartic's 'tetrus'. ~67s at 1100²; pick the camera angle so 2–3
  holes show (looking toward an edge) or genus reads as one hole.
- **Build finite codes/designs from a textbook construction and VERIFY the invariant.**
  Golay [24,12,8]: a QR-bordered matrix gave the WRONG code (min wt 7, odd weights);
  the reliable route is the [23,12] cyclic code from its generator polynomial
  `x^11+x^10+x^6+x^5+x^4+x^2+1` + a parity bit. Confirm by the weight distribution
  {0:1,8:759,12:2576,16:759,24:1} and by spot-checking S(5,8,24) (random 5-sets in
  exactly one octad). Same lesson as von Dyck: a known invariant is a cheap, decisive test.
- **DejaVu has ℝℂℍ ℕℙℚℤ (BMP) and 𝕆𝕊𝔽 + subscripts/superscripts, but NOT fraktur
  (𝔰𝔬𝔲𝔭) nor math-bold (𝐏) — those render as tofu.** For Lie algebras in figures use
  ascii/group names (so(3), SU(6), F₄, E₈) with unicode sub/superscripts, not 𝔰𝔬/𝔢₈.
- **A multi-gallery deep-dive needs a top-level index (`GALLERY.md`) with one inline hero
  image per gallery + the narrative thread.** Markdown image-links `[![alt](hero.png)](dir/README.md)`
  turn the repo browser into a guided tour; pick each gallery's most iconic figure as its thumbnail.
- **The E₈ (and general exceptional) root mandala recipe — reusable (`e8/`, `magic_square/roots.py`):**
  generate roots by Weyl-closure from simple roots; the Coxeter element C = product of simple
  reflections; the COXETER PLANE = real+imag parts of C's eigenvector for eigenvalue e^{2πi/h}
  (h = Coxeter number: G₂6, F₄12, E₆12, E₇18, E₈30); project roots onto it → the famous rings
  (E₈ = 8 rings of 30). Draw edges between roots at 60° (r·s=1 for simply-laced; nearest-neighbour
  distance for F₄). Get E₆/E₇ as sub-root-systems of E₈ by orthogonality (E₇ = roots ⟂ a fixed
  root → 126; E₆ = roots ⟂ an A₂ pair → 72), then find a base via a generic linear functional.
- **Animating a highly-symmetric figure: rotate only into its symmetry period for a seamless loop.**
  The E₈ mandala has 30-fold symmetry, so animating the 2D rotation over just 2π/30 (12°) loops
  perfectly — endless spin from 60 frames. (A rigid 2D spin of the Coxeter projection is honest;
  projecting C^t onto the Coxeter plane is the SAME rigid spin since u,t are that eigenplane.)
  Watch exposure: additive glow that's balanced at the still's resolution over-accumulates at the
  smaller animation resolution — lower edge_bright (~0.22 vs 0.42) so the convergent core doesn't
  blow to white. Edge LINE WIDTH should scale with the supersample factor or the web vanishes when
  a high-res render is downscaled for viewing.
- **Tiling an embedded surface (the tetrus) without the exact conformal map:** project a few
  symmetry-orbit seed points onto the SDF surface (Newton steps `p -= sdf(p)·∇sdf/|∇sdf|²`),
  take their symmetry-group orbit for an even, SYMMETRIC center set (~200), then per surface
  pixel do an on-surface Voronoi: nearest & 2nd-nearest center, draw mortar where √d2−√d1 is
  small, tint by cell. Reads as a heptagonal/hexagonal tiling clothing the shape. Caption it
  honestly as a geodesic mesh, not the exact {7,3}. (Heavy: the W²×N distance tensor — 1100²×216
  ≈ 2 GB and ~2 min; fine for a one-off.) A few big cells on a TUBE surface become ugly 'staves';
  use many small cells for a true tiled look.
- **Make the page representational, not just diagrammatic (user's recurring ask):** show the
  mathematical OBJECT, not only a labelled box. Lie algebras → their root systems; a finite field
  → its addition & multiplication tables; a design → all its blocks at once; a surface → its
  actual tiled body. A table of names plus one picture of the real object beats either alone.
- **A textbook diagram becomes art via void + saturation-weighting + a hero.** The
  raw CIE chromaticity fill looked like a colour-science figure. Floating it in a
  deep void (the "imaginary colours"), weighting brightness by chromatic
  saturation so pure hues blaze and the achromatic centre recedes, and adding one
  focal glow (the red tip) + one conceptual wire (the glowing line-of-purples =
  colours with no wavelength) turned it into a piece. The honest physics stayed;
  the art was in what to dim and what to make blaze.

---

## Tech / environment notes
- python3 + numpy + scipy + Pillow (+ matplotlib if needed) — `pip install` fresh
  each session; no venv committed. (matplotlib was absent in the 2026-06-24 env.)
- **WebFetch is BLOCKED** for `philosophy.stackexchange.com` and
  `mathoverflow.net`. Workaround — curl the Stack Exchange API via Bash:
  `curl -s "https://api.stackexchange.com/2.3/questions?order=desc&sort=hot&site=philosophy&pagesize=30"`
  (`sort=hot` for the philosophy front page, `sort=activity` for MathOverflow's).
- AP search: rolling-AND with explicit edge-zeroing (`np.roll`, then blank the
  wrapped border).
- ℤ[√−2] embedding: `z = a + b√−2 ↦ (a, b·√2)`.
- Art rendering: dark field, additive Gaussian splats for bloom, filmic tone map
  then gamma; supersample ×2 then LANCZOS downscale.

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
