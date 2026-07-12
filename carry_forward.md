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
| 2026-07-12 | `claude/sweet-pascal-6m0ega` | Triptych **What the Dice Agree On** (`art_6m0e/`): Parliament of Polygons (4096² hero — SIX NESTED grand-canonical ensembles of uniform convex lattice arcs, N=24→768, each square rotated 45° hosting the next at its side-midpoint contacts; Bárány parabolic-square caustic sharpening N^{-1/3} inward; sampler verified EXACTLY uniform vs enumeration at N=6 (χ²=36.6/43dof); destiny-color = signed-area deviation, steel-blue in / ember out / ivory agree; fixed-point gold star; from the LIVE MO convex-lattice-polygon question), Loom of Brown (2560×3520 — KL anatomy of ONE bridge: 9 knowledge rows m=0→∞, gold conditional mean + exact conditional-law fog + closed-form 1.5σ envelopes; coefficient variances (kπ)^{-2} verified from independent random-walk construction; live MO KL question, Mary's-Room seed), One Partition Already the Law (2048² — EXACT Fristedt uniform partition of n=250000, χ²=625/626dof vs p(20) enumeration; cell-grain hook-length lighting + log₂-ring shimmer, 46-ghost lace, gold Vershik curve; boundary within 0.052√n ≈ n^{-1/4}; CLOSES the Pólya-uniform-partition seed). |
| 2026-07-11 | `claude/sweet-pascal-hinyyh` | Triptych **What the Motion Keeps** (`art_hiny/`): Boole map x−1/x corona (4096² hero — 3e8-step orbit, 8557 breaths in INDUCED-MAP TIME: one petal per excursion, altitude palette white-hot ring→ice tips, dark pupil; arcsine law verified KS·√M=0.76, window measure-preservation 1.0000; from live Phil.SE 'Infinity and Nothing' + 'Conservation of Memory'), Dyson vortex-ring leapfrog multiple-exposure (34 ghosted exposures / 1.55 cycles, H via FD-gradients reproduces Kelvin self-speed 1.7e-10, impulse+energy drift ~1e-9; loop-braid seed from live MO), subtract-a-prime-divisor game octave spiral (2560² — 2^29 C-sieve matches the MO poster EXACTLY: 114 wilds all ω_odd≤2; ONE spiral thread: odd-loss run-arcs with prime-shaped holes, cyan 2p / violet 4p sparks, steel 2p→4p chains, golden 2^k spine, wild embers; OBSERVED: L(4p)⇒L(2p) for all p≤2^29). |
| 2026-07-10 | `claude/sweet-pascal-nt0mi7` | Triptych **What the Experiment Saw** (`art_nt0m/`): Kloosterman-paths destiny eye (4096² hero — p=6659, ALL 6658 partial-sum threads colored by Sato–Tate destiny angle θ(a), endpoint law-bar (semicircle density) on the real axis, Weil-wall near-touch 0.9989, ten extremal hero threads; exact per-path mirror P_{T−t}=S−conj(P_t) verified 1e-13; from the LIVE MO 'sum like Kloosterman sum' question), FPUT super-recurrence energy river (3584×1792 mode-energy streamgraph — Verlet drift 2.5e-7, recurrence t=158 @99.31%, TWO grand breaths t≈10200/20300, wiggle baseline = mode centroid), Zabusky–Kruskal KdV ridgeline waterfall (2560² — ETDRK4 full-circle contour + 2/3 dealias, invariants to 1.3e-10, near-recurrence corr 0.926 @ t=9.54 ≈ 30.4/π, co-moving hidden-line gold-summit mountains). Phil seeds: freedom-in-determinism; verify-by-applying. |
| 2026-07-08 | `claude/sweet-pascal-1gob1i` | Triptych **What Comes Back** (`art_1gob/`): Gauss-map backward cylinder cascade (4096² hero — G⁻ⁿ(golden interval) shatters through the Stern–Brocot mesh as CONSTANT-FLUX measure-ropes, exact μ(A)=0.098118 at all 11 levels incl. cascading mist; k=1 ghost chains = slowest-forgotten corridor at 1/φ; limit law g(x) as shoreline — CLOSES the Stern–Brocot open seed, from the LIVE MO Gauss-map-mixing question), Arnold cat map returns (512² torus, order 384; phantom ladder A^24≡I(32)…A^192≡I(256) all verified; 12 plates + correlation comb), Pell/ℤ[√2] unit ladder (spine chart (ln x, ±ln\|y−x/√2\|): Hurwitz-forbidden wedge lit as violet bay, ε²-beaded ribs, ε-lace of convergents crossing the spine, bare ribs at \|n\|≡±3 mod 8 — serves Thread A idea 4). |
| 2026-07-08 | `claude/sweet-pascal-l4k80w` | Triptych **What Comes From Nothing** (`art_l4k8/`): surreal-number birthday cascade (4096² hero — sign-expansion tree verified against {L\|R} simplicity rule, geometric day-spacing makes DAY ω A LITERAL SHORELINE with the continuum's arrival density, latecomer reals 1/3 √2−1 π−3 … as ember threads born only at ω, sea = blurred reflection of the cascade), elliptic-curve chord genesis on y²=(x+1)(3x+1)(8x+1) from the {1,3,8} Diophantine triple (exact big-rational group law + real-uniformization angle arithmetic verified to 3e-11; curve = caustic of its own secants; Fermat's (120,6479) is exactly 3P), Rule 110 from a single cell (7-beat deviation mask; ether lanes indigo, glider lace aged white→ember). Seeds: live MO surreals/NFU + Diophantine sextuples; Phil.SE solipsism + zombies + Leibniz characteristica. FOLLOW-UP same run (user asked for 'a whole bunch of knots' + linked the Knots-and-Primes tutorial): **Knots & Primes** gallery (`art_l4k8/knots/`): Specimen Drawer (25 braid-closure wreaths, exact Fox colorings dyed by smallest prime dividing det, p-colorable⟺p|det asserted per specimen; glossy opaque rope painter), Reciprocity Loom (Legendre weave, symmetry = QR, verified 600 pairs), Borromean Primes 13/61/937 (six symbols +1 verified; Rédei −1 cited Vogel). |
| 2026-07-08 | `claude/sweet-pascal-x61t1z` | Triptych **What Appears Only From Here** (`art_x61t/`): semiclassical double rainbow (4096² hero — exact 1-D oscillatory scattering integral per λ via zero-padded FFT, Fresnel chains, sun-disc + polydispersity smearing → honest supernumeraries, Alexander band, evening 5100K sun), symmetric runs of consecutive primes to 1e9 (from the LIVE MO front page — 4.2M palindromic gap windows, 18 of length 14, perspective night-shore with colossal hero gate 34 2 4 2 42 12 4 12 42 2 4 2 34 @ 593566935), stochastic resonance noise-sweep (Phil.SE 'attention amidst chaos'; brightness/hue gated by measured two-state SNR; D*=0.148 vs Kramers 0.14). |
| 2026-07-08 | `claude/sweet-pascal-b5wv9t` | Triptych **What the Edge Refuses** (`art_b5wv/`): Nash–Kuiper 1-D convex-integration corrugation cascade (4096² hero — 6 generations, EXACT loop closure via all-even frequencies, speed exactly constant; closes the Nash–Kuiper seed), Brownian rain on the Koch coast (40M walk-on-spheres walkers, Makarov info-dim 0.978≈1 vs coast dim 1.2619, 15.3% of coast never touched; from the LIVE MO isoperimetry-with-fractal-boundary question), Wada three-disc exit basins in the CHAMBER phase-space chart (path-length dwell shading; Wada verified 1.000 at all ε; Priest's inconsistent instant from live Phil.SE). |
| 2026-07-08 | `claude/sweet-pascal-kksyxk` | Triptych **What the Disorder Keeps** (`art_kksy/`): Hofstadter butterfly with Diophantine gap labels (4096² hero — Chern-coloured gaps LIT BY PROXIMITY to the Cantor bands; closes the long-open Hofstadter seed), T(p)=gpf(p+1) prime-drain river delta (1.27M primes → 2↔3 whirlpool; from the LIVE MO front page), π curlicue (quadratic Weyl-sum path, beaded spirals-of-spirals = CF digits; x-sweep over 8 constants). Bonus: α∈[1/3,1/2] butterfly zoom in variants/. |
| 2026-07-07 | `claude/stoic-mccarthy-ogasue` | **3×3 GRID** (9 panels, user-requested format) **What Reaches Us** (`art_ogas/`): inverse problems as Plato's cave — columns The World / The Shadow / The Return; rows escalate lossy→ambiguous→impossible. Row A tomography (Radon sinogram flame, limited-angle FBP with missing-wedge scars shown as cold undershoot). Row B phase problem (chiral spiral, log-\|F\|² Friedel shadow with both handednesses visible, Fienup HIO converging to the WRONG TWIN — seed chosen by shift-invariant xcorr audit). Row C GWW isospectral drums (exact lattice transplantation: spectra equal to 5e-13 over 64 modes, λ₁ matches Driscoll; Chladni gold sand on verdigris membranes; mirrored ringdown-comb spectrum). Also **refactored this memory file 282KB→40KB**. |
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
Gauss–Lucas/Rolle interlacing cascade. Radon transform / sinogram + limited-angle FBP (missing-wedge artifacts as subject); Fienup HIO/ER phase retrieval with twin-image convergence (deliberately adjacent to used 'phase surgery'); GWW isospectral drums (exact-lattice FD isospectrality + Chladni-sand nodal-web rendering); mirrored ringdown spectrum comb (two-instruments-one-chord). Hofstadter butterfly / almost-Mathieu gap labelling (Chambers corners, t·p≡r mod q, spectrum-as-light-source); gpf(p+1) prime-drain functional tree (radial log-p river delta); curlicue / quadratic Weyl partial-sum path; Nash–Kuiper 1-D convex integration (corrugated isometric circle, ghost base circle); harmonic measure / Makarov dim-1 on Koch coast (WoS + Brownian occupation fog + landing streaks); Wada basins of three-disc scattering (chamber phase-space chart, path-length dwell); semiclassical rainbow / supernumerary bows (Airy-integral-by-FFT, spectral → CIE); symmetric prime runs / palindromic gap windows (perspective specimen shore); stochastic resonance double-well noise sweep (two-state SNR band). surreal-number birthday tree / sign-expansion cascade (day-ω shoreline); elliptic-curve group-law chord envelope ({1,3,8} Diophantine curve, secants breed points); Rule 110 single-seed spacetime (ether-beat deviation rendering). Gauss-map backward cylinder cascade / Stern–Brocot measure-ropes (constant-flux waterfall); Arnold cat map finite-order recurrence (phantom-ladder plates + correlation comb); Pell ℤ[√2] unit-orbit ladder (spine chart, Hurwitz wedge, ε-lace). Fox p-colorings of braid-closure wreaths (specimen-sheet format); Legendre-symbol woven fabric (quadratic reciprocity as cloth symmetry); Borromean rings emblem (orthogonal-ellipse embedding, geometric crossing detection). Kloosterman partial-sum path ensemble / destiny-angle (vertical Sato–Tate) coloring + endpoint law-bar; FPUT mode-energy streamgraph (super-recurrence river, centroid wiggle baseline); Zabusky–Kruskal KdV soliton field (ridgeline-waterfall register, co-moving window, hidden-line occlusion). Boole map x−1/x excursion corona (induced-map breath clock, altitude-colored petals, arcsine-law verification); Dyson coaxial vortex-ring leapfrog (Hamiltonian FD-gradient integration, multiple-exposure ghost→blaze register); subtract-a-prime-divisor game loss families (octave log-spiral chart, exact run-arc carpet, 2p/4p/2^k/wild classification). Sinai/Bárány grand-canonical convex-lattice-arc ensemble → nested parliament caustic (fugacity-tuned Bernoulli weights on primitive vectors + exact-endpoint rejection); Karhunen–Loève conditional-law cascade (knowledge rows, conditional mean + exact tube fog); Fristedt uniform-partition sampling → hook-length-lit Young diagram vs Vershik curve.


**Charts that now feel over-visited** (prefer something else): the Poincaré disk (×2),
triangular/spectral point-clouds, plain complex-plane root splats.

**STILL-OPEN seeds** (good next-run material; pruned 2026-07-07, older ideas live in the
git history of this branch): singular moduli mod p; Gaussian primes ℤ[i] (needs a chart
that beats noise); Temperley–Lieb cup/cap state-sum (bracket as planar-diagram recursion);
Rule 110 / other CA; real-quadratic indefinite Conway topographs (with RIVERS);
near-integers e^{π√163}; Greene–Lobb inscribed rectangles;
quandle knot colourings; deep zoom into Lyapunov filigree / other forcing words; arctic
ellipse with actual cube cells ("cube grove"); ?(x)-warped Farey net; Pólya uniform random
partition limit shape (different ensemble than Plancherel); torus/genus-2 Laplacian
eigenmaps (needs 4 eigvecs + angle extraction); Wolfram hypergraph-rewrite emergent
spacetime; static GUE cloud + Wigner semicircle; Dyson-gas/Coulomb log-gas equilibrium;
other strange attractors (Clifford/Thomas/Aizawa, 3-D volumetric); water-droplet/rainbow
Airy caustic; sofa MOTION as a GIF; 2-D MSTD / Patterson autocorrelation
(crystallography); β-reduction-as-spacetime (one λ-term normalising; `blc.py` has the
reducer); the BLC self-interpreter hero diagram (need the exact published term); a
genuinely nested/fractal small TM found by targeted search; supersingular isogeny graph (Ramanujan expander maze — needs a chart that beats spring-layout hairballs). NEW Kloosterman sequels: the angle SHORE across many primes (θ_p(a) specimen-shore vs sin² law); Salié-sum paths (p≡1 mod 4 quadratic twist has CLOSED FORM — paths structurally different: diptych 'the wild sum / the tamed sum'); single hero-path portrait with its OWN mirror line Re=S/2 lit (each path is exactly self-mirrored — verified); composite-moduli / Ramanujan-sum eyes. NEW physics seeds: Boole map x−1/x infinite-measure wanderer (excursion night-sky, 'Infinity and Nothing'); jammed congruent-square packing force chains (live MO tensegrity question, unused); FPUT alpha vs Toda comparison strip (integrable twin explains the recurrence — same braid rig). NEW: deeper butterfly zoom into a Farey window (code supports alo/ahi — art_kksy/butterfly.py; the [1/3,1/2] full-E strip was only OK — a proper self-similar zoom needs an E-window too); √2 curlicue bowtie as its own piece (periodic CF → exact self-similarity; draft in art_kksy/variants/); gpf(p−1) vs gpf(p+1) drain-tree DIPTYCH. NEW: 2-D Nash–Kuiper (corrugated TORUS with real convex-integration flavour — the 1-D even-frequency exact-closure trick is in art_b5wv/corrugate.py); harmonic measure on OTHER coasts (percolation hull, DLA — same WoS rig works verbatim); Wada in physical space done painterly (three near-touching discs, glowing throat — chamber chart was the win this time); dwell-time GIF of one trapped ray in the three-disc chamber. NEW: rainbow machinery extends — higher-order bows p=3,4 (tertiary bow toward the sun; the bow_physics.py integral takes any p), glory/backscatter at γ→0, polarization split (the bow is ~96% tangentially polarized — two-panel honest render); prime-mirror sequels — longest ADMISSIBLE symmetric constellations vs found ones, or symmetric runs plotted by centre residue classes; SR sequels — 2-D array SR (spatiotemporal sync patterns), SR GIF with drive phase animated, double-well REPLACED by real neuron model (FitzHugh–Nagumo). NEW: surreal sequels — the ω-fan CONTINUED (ω, ω+1, 2ω, ω², ε₀ as successive shorelines: transfinite skyline) or Hackenbush strings (they ARE sign expansions — draw the correspondence); elliptic sequels — rank-2 lattice walk coloured by (a,b) generator coords, N-torsion constellations, real sextuple-extension data from the MO thread; Rule-110 sequels — engineered glider collision computing a tiny AND gate (annotated), or a 30/54/110 single-seed comparison strip under the same deviation rendering. NEW knots-and-primes seeds: compute the Rédei symbol HONESTLY (Rédei's original solvability criterion — would upgrade the Borromean emblem from cited to verified); Alexander-polynomial river (Burau at general t as exact polynomial matrices); a MILNOR-invariant link gallery (links, not knots — the specimen-drawer rig extends to multi-component closures by dropping the n-cycle check); knot-group wirtinger presentations rendered as Cayley-ish graphs. NEW (2026-07-11): Boole/infinite-ergodic sequels — arcsine occupation-fraction as its own piece; Thaler parabolic maps with α≠1/2 → generalized-arcsine corona FAMILY; corona GIF (sliding window). Vortex-ring sequels — 3-ring CHAOTIC leapfrog (rig supports NRING=3 already, art_hiny/rings_expo.py), ring+wall image system, pass-through animation. Game sequels — prove/refute L(4p)⇒L(2p) (observed to 2^29!); the recursive prime hierarchy (p joins the 2p-loss family ⟺ 2(p−1) wins — Sophie-Germain-flavored chains); Grundy VALUES (mex spectrum) for the same game; wild-set smoothness structure. NEW (2026-07-12) limit-shape sequels — Rivers of Totient a+φ(a) (live MO seed, unused: two parity worlds, 2^k→3·2^{k-1}→2^{k+2} locks, squarefree sparks; needs SPF sieve + merge-richness check); parliament GIF (levels rotating/zooming into the fixed point — the recursion is a 45°+√2 self-map); convex-polygon fluctuation LAW panel (transversal profile vs N^{2/3}, endpoint-pinned Airy flavor); loom sequel: same conditional cascade for a DIFFERENT basis (Haar/Faber–Schauder midpoint tents — compare which basis 'develops' the path faster); partition sequels — Plancherel vs uniform SAME-n diptych (two measures, two limit shapes, one grid), largest-part Gumbel strip.

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

- When a field is flat, don't relight it — change WHICH quantity brightness means. Three fixes in one run: WoS jump-points → occupation-time weights (killed fake sphere-caustics in the fog); integer bounce count → continuous log path-length (killed terraced flat fills in basin art); log-pinned hit counts → linear-in-measure (recovered tips-vs-fjords drama). Brightness is a measure — pick the measure like you pick a palette.
- Nash–Kuiper 1-D corrugations close EXACTLY if all frequencies are even (Jacobi–Anger: 1+Σm·N=0 has no solution) — theorem-level verification for free; α=J0⁻¹(1/ρ) sets the per-stage speed ratio; speed is exactly s because γ'=s·e^{iθ} regardless of θ.
- Walk-on-spheres is the cheap exact way to SAMPLE harmonic measure (40M walkers in ~3 min: EDT distance grid + wrapped-Cauchy exterior re-entry), and the Koch hierarchy makes the multifractal analysis a reshape(-1,4).sum().
- WoS waypoints are NOT Brownian occupation — the fixed-radius jumps draw visible circle-caustics. For honest fog run true small-step walkers weighted by σ² (occupation time); expect the physical dark moat at an absorbing coast (Green's function → 0 there) and bridge it with real landing trajectories, not decoration.
- Three-disc scattering: gaps are set by CENTER distance d·√3 (discs at radius d from origin) — d≈1.2–1.5 for closed-ish chaos, NOT 2+. The chamber phase-space chart (launch point angle × direction) fills the whole frame with contested boundary; physical-space slices leave most pixels smooth. Verify Wada with erosion-based boundary mask (dilation-based is vacuously empty!) + ε-ball 3-basin check: got 1.000 across ε.
- Judge the assembled triptych at FINAL resolution: per-pixel splat density falls ~linearly with render width, so a 2560² final comes out darker than its 1280² proto even with identical params — rebalance gains after the size jump.

- A 3×3 matrix grid (3 subjects × 3 views) needs a COLUMN grammar (thing/shadow/return) and a ROW hue identity (ember/iris/verdigris); judge cohesion on the assembled sheet.
- The GWW pair is EXACTLY isospectral for the discrete 5-point Laplacian when the grid is integer-lattice-aligned (the transplantation is a lattice isometry): rel diff ~1e-13 at any q. Rasterize by exact integer on-edge tests + offset ray-cast; interior point counts then match exactly. (eigsh sigma=0 on ~900k unknowns: minutes, a few GB.)
- Phase-retrieval twin ambiguity is REAL and steerable: audit HIO seeds by shift-invariant cross-correlation against object vs rot180(object); some seeds converge crisply to the TWIN (a better story than muddy stagnation). Mid-run ER epochs collapse the twin — save ER polish for the last ~30 iterations.
- Friedel's law makes a diffraction shadow centrosymmetric: a chiral object's log-|F|² already shows BOTH handednesses — the inverse problem's ambiguity is visible in the data panel for free. (Zoom the Fourier crop ∝ 1/object-scale or grooves shrink at hi-res.)
- Render information LOSS honestly: limited-angle FBP's negative undershoot tinted cool over the warm world = 'the wound'; the artifact channel carries the concept better than decoration.
- Chladni treatment rescues flat membrane fields: gold nodal web (gaussian ridge at zero-crossings of the modal snapshot) in its OWN color ramp over a dark energy-shaded body — decoupling the two ramps creates the contrast.
- A sinogram is intrinsically beautiful (every point → a weighted sine braid) but overexposes fast as angle count grows — tone-map gently (k≈1.7).

- Light the complement (sharpest form of the apophatic move): when the math lives on a measure-zero set, colour the FORBIDDEN regions by their invariant and set brightness = proximity to the allowed set. Flat fill read as poster; edge-lit read as stained glass (Hofstadter gaps + Chern colours).
- Row-wise butterfly recipe: per row the minimal-denominator fraction in the row's α-interval (Stern–Brocot); cap q via CF convergents — the Farey mesh near low-q plateaus needs q up to H, NOT √H. Band edges = eigvalsh of the TWO Chambers-corner q×q matrices, batched by q (8192 rows ≈ 40 s). Gap labels need |t|-depth dimming or the high-|t| brocade washes white.
- A functional graph on primes renders as a river delta: radius=log p, wedges ∝ subtree mass, stroke ∝ mass^0.8, palette position = mass-weighted depth CDF. A GLOBAL sinusoidal swirl on stream paths = phase-locked zigzag that kills the tree; per-basin random drift is the fix.
- Chunk giant splat jobs BY EDGES, not by flat sample index (np.repeat over 1.5e9 samples = 3×12GB int64 → OOM).
- Curlicue numerics: never form n²·x at n>1e6 (float64 ulp ≈ 0.03 there); use Δₙ=(2n+1)x mod 2 + cumsum (drift ~1e-6 at N=1e7, verified vs direct).
- Curlicue N is a legibility dial (like Penrose tile count): spirals legible at N~2.5e6 on 2560²; at 1.6e7 pearls shrink to scatter. Pick x by CF personality: π = varied pearls (the 292!), √2 = self-similar bowtie, φ = dense lightning, Champernowne = one blazing dot.

- An oscillatory 1-D physics integral on a uniform grid IS a DFT: choose N from the phase step (N = 2π/(kR·Δb·Δθ)) and one zero-padded FFT evaluates the whole angular profile exactly — Airy's rainbow integral, supernumeraries and all, in <1 s per wavelength.
- The physical smear IS the aesthetic fix (rainbow edition): the too-dense fringe comb calmed down not by blur but by convolving with the sun's 0.53° disc + a ±9% drop-radius mixture — the honest wash leaves exactly the 3–4 supernumeraries a real drizzle grants.
- Chroma-preserving soft-knee rescues spectral crests: compress the radial profile's LUMINANCE (f = (1−e^{−cL})/cL) before the 2-D tonemap, or every crest clips to yellow-white and the red rim dies. Same trick fixed the SR band (compress scalar luminance, THEN colorize).
- An ensemble mean's SNR lies about stochastic resonance — intrawell linear response masquerades as coherence (and 1/M noise suppression inflates it). The honest observable is the SIGN of one trajectory (two-state); its SNR peaked at D*=0.148 vs Kramers' 0.14.
- A too-strong 'subthreshold' drive erases the silence: A=0.25 tilts the 0.25 barrier down to ~0.05 and walkers lock from D=0.02 on. Check the TILTED barrier, not the resting one, when planning where a resonance band will sit.
- Never lerp two accent colours through RGB midspace — the midpoint is gray. Gate the warm accent with a smoothstep on the (row-smoothed!) measure and normalize by the SMOOTHED max: raw-max normalization let one spiky row eat the whole ramp.
- Perspective ground-plane fields: fill the view frustum with uniform SCREEN-x at every depth (world-fixed x-range collapses to a pyramid with a nuclear apex); lognormal z per size-class with overlapping tails kills band edges; dither the horizon pile-up row by ±1px or millions land on one scanline and blow out.
- A hero specimen among peers needs a SCALE CLASS of its own — 1.5× bigger drowns; the win was architectural: centre below the frame, radius 0.46S, wide soft strokes (7 offsets, gaussian weights), so the palindrome's gap structure reads like a gate.
- Arc/point sampling must scale with canvas (npts ∝ S) or 2560 finals come out dotted where 1280 protos were smooth; weight ∝ π·r/npts auto-compensates the mass.

- The founding gesture deserves its own light. In a 'generation' piece, make the ORIGIN a first-class visual citizen (root star / generator rays / seed star at the cone apex) — an engine of creation without its seed reads as texture; with it, the texture acquires a direction and a story.
- Angle arithmetic beats big rationals for FILLING an elliptic curve: exact heights explode quadratically (~15 visible points from |a|≤25), but E(ℝ)≅ℝ/ℤ×ℤ/2 built by quadrature (√-substitutions at branch points) gives 10⁵ points verified to 1e-11. VERIFY the oval coset offset (0 or ½) against exact points; and np.interp silently returns garbage on a DESCENDING xp table.
- Near-tangent secants draw the envelope; random secants draw fog. Sample chord pairs adjacent in angle (Laplace δ~0.01) for an honest caustic; mix ~50/50 arc-length-uniform and angle-uniform anchors to balance even coverage against drama at the slow bends.
- A CA background subtracts LOCALLY and phase-free: glow iff the cell differs from itself one background-period ago (rows[t]≠rows[t−7] for R110). Global ether-template matching fails — every lane has its own phase and the dead region false-positives everywhere.
- Graded fog rescues subpixel recursion: blur the accumulator with a sigma that RAMPS with recursion depth (sharp filigree up top, dissolving mist at the convergence line) — one flat anti-moiré blur can't serve both zones.
- Surreal sign-expansion value rule: magnitude stays 1 until the first sign alternation, then halves every step (including the alternation). Verify against brute-force {L|R} simplicity — cheap, catches fenceposts.

- Opaque WEAVE is the opposite discipline from additive glow: what you draw last is what exists. Per-sample sprites with outlines EAT their neighbors (spacing < outline margin → only the last sprite survives — hit this twice); short depth-groups read as segmented armor. Recipe: cut strands into the LONGEST arcs with one consistent depth role (one crossing each), paint each arc outline→body→spec, order arcs by z at their crossing.
- Braid closures make a whole knot GALLERY cheap: monodromy per crossing (under' = 2·over − under), closure = n-cycle permutation check, Fox colorings = kernel of (A−I) mod p, det = |first minor| = |Δ(−1)| — all verifiable against classics (trefoil 9 three-colorings, fig-8 25 five-colorings). Random braid words + invariant dedupe = endless distinct specimens.
- Derive over/under from actual 3-D geometry or an actual theorem (Legendre rule, projected-crossing detection) — easier AND honest; hand-managed crossings are where knot art goes wrong.
- Glossy rope sprite: hairline outline (r_o ≈ 1.07·r_b), radial shade toward light, off-centre spec ≤0.25·w with soft blend; cast shadow only from over-strands, sparse and weak (×0.85), or it blots.

---
- Render the TRANSPORT, not the state (Gauss waterfall): forward transfer-operator densities are a flat wall by level 3 — the operator SMOOTHS. Draw the flux of measure between levels as constant-flux ropes (brightness = mass/width): thin necks glow for free, conservation becomes the composition, and the exact invariant (Σ mass = μ(A) per level) is the verification.
- Filigree lives in PREIMAGES: pick the direction of time that carries the fractal. G⁻ⁿ(interval) = one piece per CF cylinder (the MO 'cylinders to intervals' picture); forward = mist. Sub-pixel pieces must keep cascading as a mist density evolved by exact μ-transfer split weights or mass silently vanishes.
- The slowest branch deserves ghost life: recursing ONLY the k=1 chain far below the pixel cutoff (EPS/48) costs nothing and threads every dying family's most-persistent memory down into the mist (largest branch derivative = slowest forgetting; at the fixed point it is THE golden corridor).
- A finite-order permutation piece (cat map) is a FRAME-LADDER, not a field: pick display times from verified subgroup structure (A^t ≡ I mod divisors — the phantom ladder at every doubling modulus), keep tiles pixel-native (no SS, no LANCZOS), and let a correlation comb carry the timeline.
- Log-log charts make hyperbola pencils PARALLEL RULES (slope −1, offset ln n) — mechanical. A concave power on the distance-to-asymptote axis bows them into wings; the forbidden zone (Hurwitz: nothing within 1/(2√2x) of √2) is the REAL subject — light the complement as a wedge and lace it with the ε-orbit of the convergents.
- asinh chart trap: hyperbolae collapse onto their asymptote within ~half a pixel once x ≳ 100 (exponential approach in log coords) — 70% of the canvas becomes empty beam. Check approach RATES before committing to a chart.


- DESTINY COLORING self-organizes a composition: color each trajectory by a scalar invariant of its ENDPOINT (Kloosterman: θ(a)=arccos(S/2√p)) — endpoints drag their whole walk, so the ensemble sorted itself into a two-lobed eye with zero layout work, and the sin²-rare extremes became automatic accents. Reusable for any walk family with a terminal invariant.
- FOG IS AN OVERLAP PHENOMENON with its own resolution law: for a splatted THREAD ENSEMBLE, per-pixel fog brightness falls ~1/S even when each thread's own brightness is held constant (mass ∝ S). Scale ensemble mass ∝ S^1.6–1.7 for the fog while trimming per-hero multipliers — the craft note 'rebalance after the size jump' now has a formula.
- Spacetime-carpet trap for soliton gases: periodic wrap + speed spread = 'diagonal rain' in EVERY galilean frame (tried three velocities). The fix is a REGISTER change: ridgeline waterfall (~100 slices, hidden-line via running min-y, FINE x-subsampling or strokes dash on steep slopes) in a co-moving ~half-domain window, summits gilded by height; shift the window so the genesis crest sits INSIDE the frame.
- A conserved-total streamgraph is a RECTANGLE (both outlines flat — conservation!). Restore life with a wiggle baseline driven by the energy centroid μ(t)=Σk·E_k/K: the river bows exactly when the cascade runs deep, which IS the story.
- ETDRK4 φ-coefficients: a DISPERSIVE (imaginary-spectrum) operator needs the FULL-CIRCLE complex contour (Trefethen p27); the diffusive half-circle+real() recipe (kursiv.m) silently breaks conservation (KdV M2 drift 8e-2 → 7.5e-12 after fix). Also 2/3-dealias the quadratic term. VERIFY INVARIANTS BEFORE AESTHETICS — both physics panels had integrator bugs caught by conservation checks, never by eye.
- Verlet half-kick bug fingerprint: relative energy drift ~1e-1 instead of ~1e-7 (p = p_half + dt·a instead of + 0.5·dt·a).
- Recurrence detection must be SHIFT-MAXIMIZED (one FFT xcorr per row): the ZK recurrence reassembles TRANSLATED; naive same-phase correlation reads 0.16 where the truth is 0.926.

- HEAVY TAILS eat any linear axis: the honest rewarp is the process's own INDUCED-MAP clock (one petal per first-return). Angle = breath index (share ∝ log duration), radius = true height profile — the Boole corona composed itself. (Generalizes 'rewarp by event-CDF': prefer the dynamical clock when one exists.)
- Calibrate ink to the geometry that RECEIVES it: on a log-spiral all integers lie on ONE ~1-px thread — per-ring-AREA calibration concentrated 41× onto the line (garnet rendered white). Line layers want per-line-px levels; point dust wants per-circumference-per-count.
- Exact RUN-ARC rendering beats subsampling for dense 0/1 data on a curve: draw maximal runs as segments (mass ∝ run length) — the GAPS carry the structure (odd-loss carpet broken exactly at the primes). Random subsampling erased that texture.
- An asinh vertical chart turns ballistic excursions into RECTANGLES (launch spoke + log-flattened glide = boxy shelf). Check the silhouette a chart induces before committing; polar + breath-time dissolved it.
- Multiple-exposure (ghost→blaze age ramp) cleanly renders a conserved EXCHANGE: 34 exposures let the eye verify impulse conservation (one ring fattens exactly as the other thins). Scale stroke offsets ∝ canvas width or finals come out hairline (hit this twice in one run).
- A 1e-12 chaos bundle does NOT decohere gradually near a singular reinjection (T'=1+1/x²): one deep scramble separates it completely — 'branching-tree' compositions need bounded stretching.

- Uniformity of a hard combinatorial ensemble is SAMPLABLE and VERIFIABLE: independent geometric/Bernoulli weights per atom (primitive vector, part-multiplicity), ONE fugacity tuned so the mean hits the target, rejection to the exact fiber — every fiber member has identical weight, so conditioning = uniform. χ²-test against complete enumeration at toy size (44 arcs, 627 partitions) turns the sampler into a theorem.
- Nested-recursion composition for free: when an ensemble pins fixed CONTACT points (side midpoints), the contact frame hosts the next, finer ensemble (rotate 45°, shrink √2, double N) — the infinite regress composes the frame and the sharpening IS the theorem (relative width ~N^{-1/3}).
- Ink budget for band ensembles has a FORMULA: per-pixel density ∝ count/(perimeter × bandwidth), bandwidth ∝ scale·N^{2/3}/N — equalize with w ∝ 2^{-5k/6} per nesting level (eyeballing was 40× off). DIFFUSE bands also dim faster than SHARP ones at a size jump: outer/fuzzy levels needed extra ×3–5 gain at 4096² that the 1024² proto never showed.
- Conditional-law cascade is a reusable register for ANY basis expansion: rows = knowledge stages m; per row draw the conditional MEAN (gold) + exact conditional fog (fresh tails) + closed-form σ_m envelope; the mean visibly 'develops' into the sample. Skip envelopes while the tube is fat (they clutter); add them once the law needs a witness.
- Hook length is the natural LIGHT for a Young diagram: brightness (1/h)^γ + floor makes the rim blaze exactly at the jagged individual boundary; a log-periodic ring term cos(2π·log₂h) with amplitude fading ∝ exp(−log₂h/12) gives honest sediment strata without faking texture.
- The convex-arc/partition conditioning trick pairs with a REPAIR channel for background ensembles: accept within ±w and fix EXACTLY by adjusting the multiplicity of the unit atom ((1,0)/(0,1) steps, 1-parts) — negligible distortion for ghosts, never for the hero.


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
