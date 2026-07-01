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
| 2026-07-01 | `claude/beautiful-heisenberg-4zx43y` | Procedural triptych **Exceptions to the Rule** (unifying thread = *the object at the edge of what a rule allows — the largest, the rarest, the unlistable*) in `art_4zx4/`, **three NEW techniques across three visual grammars**: `01_the_corner` (**4096-wide hero**: the **MOVING-SOFA problem** — Moser 1966; Gerver's sofa area **2.2195** conjectured 1992, **PROVEN optimal by Baek 2024**. Did NOT hard-code Gerver: defined sofa = **∩ of a width-1 L-corridor over all rotations θ∈[0,π/2]**, parametrised by the inner-corner path c(θ) (arm-swap symmetry ⇒ sofa symmetric about y-axis ⇒ free the path only on [0,π/4], mirror cx→−cx), and **MAXIMISED the intersection area by coordinate ascent** (13 ctrl pts/300² grid → 25 ctrl/520² grid → **area 2.172**, within 2% of the proven optimum; `sofa_optimise.py`+`sofa_path.npy`). The emergent silhouette is unmistakably Gerver's "telephone-handset" (long body + semicircular BITE scooped underneath, carved where the corridor's inner corner sweeps). Rendered as the **ENVELOPE of the motion**: every position of the two corridor walls splatted additively (inner walls → the bright **bite caustic** fan of cusps = the corner carving the bite; outer walls → a dim swept **dome**), gold sofa fill on top, cool caustic strictly masked OUTSIDE the sofa. Mask needs many angles (nt=1100) or the bite scallops; soft-alpha edge. ~4½min @4096. VERIFIED area), `02_more_sums` (2400×1500: **MSTD — More Sums Than Differences**. Because `a+b=b+a` collides but `a−b≠b−a`, almost every set has `|A−A|>|A+A|`; <1 in 2000 random subsets of [0,32) break it. Classic minimal counterexample **{0,2,3,4,7,11,12,14}**: `|A+A|=26 > |A−A|=25` (verified). Drawn as an **arc LOOM**: each pair {a,b} a semicircle with **apex over the sum (a+b)/2, radius = the difference (b−a)/2**, colour by |diff|, faint mirror below → a woven mandorla; a **gold sum-comb** (26 teeth, mult=height) above the line and a **rose difference-comb** (25, symmetric) below carry the count. 11s), `03_the_list_forgot` (2048²: **Cantor's DIAGONAL argument**, the reals are uncountable. The "list" is the infinite **Walsh–Hadamard array** `T[n,k]=parity(popcount(n&k))` — exact, orthogonal, self-similar (recursive nested squares), cool blue. Its main **diagonal == the Thue–Morse sequence** (verified); Cantor's **flip** of it blazes **gold** across the field and repeats as a bit-strip below — VERIFIED it equals no row. 2s). ✅ Read memory first; fresh names/techniques, **no collisions**; all NON-disk (extremal filled shape + caustic / arithmetic arc-loom / binary field). Seeded by **live MathOverflow** ('intuition behind sets with **more sums than differences**' → 02; 'minimum dimensionality of a space capable of **representing its own structure**' → the self-reference/diagonal 03) + **Philosophy.SE** (self-representation / 'is an object merely its relations' / Solomonoff cluster). **Diagonalization was an OPEN SEED listed unbuilt ~5 runs — now DONE.** ALSO-RANS brainstormed-unbuilt (next-run seeds): **Kakeya/Besicovitch needle set** (measure-zero, a segment in every direction — the extremal-area COUSIN of the sofa; Perron tree), **quandle knot colourings** (MO front page), **six-vertex/square-ice arctic curve**, **near-integer coincidences e^{π√163}**. PNGs 1.7/0.72/0.66 MB. |
| 2026-07-01 | `claude/beautiful-heisenberg-4zx43y` | **(same branch, follow-up — user: 'those were not artistic enough, too plain and mechanical. and you already did cantors diagonalization. try more?')** IMPORTANT AESTHETIC FEEDBACK. Made a painterly REMAKE triptych **Caustics — The Fold, Three Ways** in `art_4zx4b/` (one idea — the **fold/cusp catastrophe**, where a smooth map's arrival-density diverges — in optics/chaos/disorder; **brightness IS the density in all three, NO solid fills**): `01_caustics` (**4096² hero**: **optical caustics** — parallel light refracts through a smooth random water surface h(x,y); a vertical ray deflects by ∇h and lands at (x,y)+s·∇h; **~49M rays GATHERED** (bilinear splat, chunked) so brightness = caustic density, unbounded at the folds. **Chromatic dispersion** = per-channel refraction (×1.03/1.0/0.97 — SUBTLE! ×1.10 looked like broken-3D-glasses RGB glitch). Deep-navy water + teal→gold→white caustic ramp; keep dark POOLS (subtract ~0.35× the mean flux so only the focused excess blazes). ~1min), `02_attractor` (2048²: **de Jong strange attractor** x'=sin(a y)−cos(b x), y'=sin(c x)−cos(d y), (a,b,c,d)=(1.4,−2.3,2.4,−2.1); **~3.4×10⁸ iterations** run as MANY parallel orbits in lockstep (ensemble-as-numpy-axis), brightness = the **invariant measure**; indigo→rose→amber→gold→white silk ramp × l^0.62 falloff + bloom → a luminous draped veil), `03_branched` (2048²: **BRANCHED FLOW** — a parallel ray SHEET launched into a weak smooth Gaussian-random potential V (rms ε≈0.014, corr-length ℓ≈24); d²r/dt²=−∇V, accumulate ray density → the flux collapses onto **branching caustic filaments**; electric-blue palette, fade the uniform launch edge, subtract the smooth base so branches pop). Theme through-line: rays/orbits/particles refuse to stay a crowd — they fold onto caustics at every scale (Thom: fold+cusp are the only stable singularities of a planar map). Left the earlier `art_4zx4/` in place (history). PNGs 18/3.5/3.3 MB. |
| 2026-06-30 | `claude/beautiful-heisenberg-vq6jkh` | **(same branch, follow-up #6 — user: 'more?')** Added **Volume V** to `permutations/` → **18 verified lenses** total; this volume opens the **representation-theory / algebra** pillar. `15_characters` — **the S₁₄ CHARACTER TABLE** (`characters.py`): full 135×135 table of χ^λ(μ) (rows=irreps, cols=classes, both indexed by partitions) via the **Murnaghan–Nakayama** rim-hook rule (implemented on the **abacus/β-set**: move a bead down by k, sign=(−1)^#beads-jumped; `lru_cache`d). VERIFIED dims χ^λ(1ⁿ)==hook-length f^λ AND row orthogonality Σ_μ|C_μ|χ^λχ^ν=n!δ (0 violations, n≤8). Drawn as a signed-log diverging heatmap (gold +, teal −, dark 0); the bright identity column = the dimensions. `16_young_lattice` — **YOUNG'S LATTICE / the differential poset**: every partition as a tiny Young diagram, edge=add-a-box, fanning from ∅; #upward-paths-to-λ = f^λ (VERIFIED ==hook_dim), nodes tinted by f^λ; DU−UD=I ⇒ Σ(f^λ)²=n!. `17_jdt` — **JEU DE TAQUIN** (`jdt.py`): a skew tableau rectified by hole-slides shown as an 8-panel comic; VERIFIED rectification == RSK insertion-tableau of the reading word (0/400 random skew) and slide-order independent (the plactic/Knuth structure). `18_foata` — **FOATA's second fundamental transformation** (`foata.py`): the compartment cyclic-shift map; VERIFIED `inv(foata(σ))==maj(σ)` on all S₁..S₇ (a bijection), drawn as 720 level-preserving threads (maj→inv) forming the shared Mahonian bell. PNGs ~0.3-1.2 MB. |
| 2026-06-30 | `claude/beautiful-heisenberg-vq6jkh` | **(same branch, follow-up #5 — user: 'Go for it!!!')** Added **Volume IV** to `permutations/` → **14 verified lenses** total. `12_great_circles` — **THE ARCHIMEDEAN SPHERE LIFT** (`greatcircle.py`): the deepest sorting-network fact (AHRV conj. → Dauvergne thm). Each wire's trajectory is a SINE curve `h(t)=a cos t+b sin t` (a=h0 fixed by the start, b least-squares; VERIFIED median R²=0.99 on the smoothed trajectories), and every sine is the z-projection of a GREAT CIRCLE `cos t·u + sin t·v` (proj onto fixed axis = R sin(t+φ)). LIFT each real trajectory to its great circle: build orthonormal u,v with `u·ẑ=a, v·ẑ=b` (closed form: u=(s cosα,s sinα,a), s=√(1−a²); v from P=−ab/s, perp=√((1−a²−b²)/(1−a²)) — needs a²+b²≤1, clamp), azimuth α spread → a sphere woven of rainbow great circles. VERIFIED lifts are exact great circles (|C|=1 and planar-through-origin to 1e-16). `13_fomin` — **Fomin GROWTH DIAGRAMS** (`fomin.py`): RSK's 3rd face. Grid of corner-partitions grown by 4 LOCAL rules from the SW corners + the cross (∅ at lower-left → RSK shape at top-right). Rule incl. special cases: both-grew-different→union(componentwise max); both-grew-same-row-k→add box in row k+1; cross (only when λ=ρ=μ)→add box row 0. VERIFIED top-right == RSK shape on all S₁..S₇. Drawn as a lattice of little Young diagrams coloured by size. `14_typeB` — **type-B permutohedron = hyperoctahedral group B₃** (signed permutations): 48 signed-perm matrices on a generic point = great rhombicuboctahedron, 72 edges 3-coloured by Coxeter generator (2 transpositions + 1 sign-flip), V−E+F=48−72+26=2 (VERIFIED). To Fig-2's S₄ truncated octahedron as B₃ is to S₄. PNGs ~0.4-1 MB. |
| 2026-06-30 | `claude/beautiful-heisenberg-vq6jkh` | **(same branch, follow-up #4 — user: 'study more permutation theory, what do you want to investigate')** Added **Volume III** to `permutations/` (3 figures tying Sₙ to geometry / determinants / order), bringing the gallery to **11 verified lenses**: `09_viennot` — **Viennot's 'light and shadows' geometric form of RSK** (`viennot.py`): plot points (i,σ(i)), a SW light casts each point's NE-quadrant shadow, the merged-shadow boundaries are the **shadow lines** (#lines = LIS = first-row length of P). MY ALGORITHM (verified): repeatedly peel the **SW-minimal antichain** (Pareto-min: no q with q.x<p.x AND q.y<p.y) as one shadow line; row entry = **min-y on each line**; recurse on the lines' **NE inner corners** `(x_{i+1},y_i)` for the next rows. VERIFIED `viennot_P == rsk_P` on ALL of S₁..S₇ (5913/5913) + random n=39. Rendered as nested rainbow staircases. `10_lgv` — **Lindström–Gessel–Viennot non-intersecting paths** (`lgv.py`): VERIFIED the LGV determinant (det of single-path counts) == brute-force count of non-intersecting families (=10) on a small case; the signed det IS a sum over permutations (intersecting families cancel in sign-pairs). Render = ~28 'vicious walkers' (non-colliding ±1 paths, fixed ends) sampled by **corner-flip heat-bath Glauber** (validity asserted: ±1 steps, strictly ordered, endpoints fixed) → a glowing Tracy-Widom-edged band; explicitly the SAME non-intersecting-paths picture as the main set's lozenge/plane-partition tilings. `11_bruhat` — **strong Bruhat order on S₄** Hasse diagram: cover = a single value-transposition (ANY two positions) that raises inversions by exactly 1; **gold** edges = adjacent swaps (= weak order = the permutohedron of fig 02), **violet** = the extra long-range strong-order relations; rank sizes = **Mahonian 1,3,5,6,5,3,1** (verified), self-dual; barycentric poset layout. PNGs ~0.5-1.2 MB. |
| 2026-06-30 | `claude/beautiful-heisenberg-vq6jkh` | **(same branch, follow-up #3 — user: 'go deeper into permutations')** Added **Volume II** to `permutations/` (3 deeper verified figures): `06_sorting_network` — **the crown jewel I'd deferred: a UNIFORM random sorting network (AHRV sine curves), sampled EXACTLY**. Resolved the earlier 'MCMC too slow' block by implementing the **Edelman–Greene bijection** (`eg.py`): forward (reduced word of w₀ → SYT of staircase) + **inverse** (the key was the reverse reverse-bump rule — SPECIAL case triggers iff the up-bumped value `v` is ALREADY in the row → then `x=v-1`, row unchanged; else NORMAL replace largest-`<v`). VERIFIED forward bijects (counts 2/16/768 for S₃/₄/₅, all P=P₀) and forward∘inverse = identity on EVERY reduced word of S₄ and S₅ (0 mismatches). Sample a **uniform staircase SYT via the GNW hook walk** → inverse-EG → uniform reduced word (uniformity checked on S₄: all 16 words ±6%). Render: heavily smooth each wire's trajectory (`gaussian_filter1d σ≈0.013·L`) to reveal the **sine curves**, 6 highlighted white over a dim rainbow woven mesh (n=120). `07_patterns` — **uniform 231-avoiding permutation** (= Knuth stack-sortable; counted by **Catalan**, verified 1,2,5,14,42,132,429) sampled exactly-uniformly via the recursive decomposition **σ = L·max·R** with split `P(k)=C_k C_{n-1-k}/C_n` (exact **big-int** Catalan; iterative stack); the n=3000 matrix shows the class's **permuton limit = a Brownian-wandering diagonal** (vs uniform = white noise). `08_eulerian` — the **Eulerian triangle** A(n,k)=#perms with k descents, recurrence `(k+1)A(n-1,k)+(n-k)A(n-1,k-1)` (verified rows sum to n!, symmetric), drawn as a glowing per-row-normalised pyramid with a bright central ridge at k≈(n-1)/2. README now 'Eight lenses (Vol I + II)'. PNGs ~0.5–1.5 MB. |
| 2026-06-30 | `claude/beautiful-heisenberg-vq6jkh` | **(same branch, follow-up #2 — user: 'make the Singular Staircase more artistic, it feels mechanical' + 'a whole series digging deep into permutation theory')** (1) **REIMAGINED `04_singular_staircase`** from a neon curve-on-a-grid into a painterly **atmospheric dusk RIDGELINE**: the IFS chaos-game measure glows warm rose→amber→gold as the curve over a soft `?`-warped **nebula veil** (vectorised `Q_vec`, verified to machine precision), a valley lit beneath the curve's **EXACT analytic profile** `(1−?(x))·H` (gap-free), warm 'lanterns' at the simplest rationals. (2) **NEW deep-dive gallery `permutations/` — 'The Anatomy of a Shuffle', 5 verified figures, each its own visual grammar, reusing a fresh `figkit.py` annotation-block kit + inlined in README**: `01_cycles` (random-permutation cycle decomposition as chords `i→σ(i)` GROUPED into contiguous arcs so the **Poisson–Dirichlet** cycle-length partition is visible; giant cycle = **Golomb–Dickman** ≈62.4%, mean #cycles = `H_n`; both verified), `02_permutohedron` (**S₄ Cayley graph = truncated octahedron**, 24 verts/36 edges 3-coloured by adjacent-transposition generator = weak Bruhat order; Helmert projection of perms-as-coordinates), `03_rsk` (**RSK** bijection σ↔(P,Q) verified inset + **longest increasing subsequence** gold chain via patience sorting; Ulam/BDJ `2√n`, links to piece 05), `04_mahonian` (**inversion distribution = q-factorial `[n]_q!` coefficients** by convolution → **Gaussian CLT**, mean n(n-1)/4), `05_mallows` (**Mallows measure** `∝q^{inv}` sampled EXACTLY via independent geometric **Lehmer digits**; one dial q: diagonal band ↔ uniform ↔ anti-diagonal). Built+verified `sortnet.py` (reduced words of w₀, braid/commutation moves) but **deliberately did NOT ship a 'uniform random sorting network'**: the braid–commutation MCMC mixes far too slowly (n=30 still combed after 30M moves) and exact uniform needs Edelman–Greene + random staircase SYT — left honest-for-a-future-run. PNGs ~0.1–1.5 MB each. |
| 2026-06-30 | `claude/beautiful-heisenberg-vq6jkh` | **(same branch, follow-up — user asked for two carried-forward also-rans)** Added TWO companion pieces to `art_vq6j/` extending **The Edge of the Possible** toward *limit shapes & singular measures*: `04_singular_staircase` (2048²: the **Minkowski question-mark `?(x)`** — Conway's slippery devil's staircase; maps each continued fraction `[0;a₁,a₂,…]`→binary `0.0…01…10…` (runs of aᵢ bits), Stern–Brocot tree→dyadic tree; continuous, strictly increasing, derivative **0 a.e.** = alive only on a measure-zero set. KEY technique = the graph is the **attractor of a 2-map IFS** `L(x,y)=(x/(1+x),y/2)`, `R(x,y)=(1/(2−x),(1+y)/2)` — VERIFIED to land on `?` to 1e-13 and ?(1/φ)=2/3, ?(1/3)=1/4, ?(√2−1)=2/5 exact; rendered by a **VECTORISED chaos game** (ensemble-as-numpy-axis, ~250M points, batched), additive **bilinear** splat so brightness IS the singular Stern–Brocot measure; hue sweeps with height; nested **Stern–Brocot boxes** (Farey-width×dyadic-height) drawn behind make the self-similarity literal. Perf note: `np.add.at` BEATS `np.bincount(minlength=W²)` here — bincount reallocates a 16.7M-bin array every call → 10× slower at W=4096), `05_limit_shape` (2048×1073 wide: the **Logan–Shepp / Vershik–Kerov limit shape** of a **Plancherel-random Young diagram** — sample a uniform random permutation, **RSK row-insertion** (bisect per row) → shape; prob ∝ (dimλ)²/n!. Drawn **Russian convention** (cells = diamonds, content `j−i` → colour bands), with the smooth limit curve `Ω(u)=(2/π)(u·arcsin(u/2)+√(4−u²))`, |u|≤2 overlaid in gold — VERIFIED bulk `max|φ−Ω|`: 0.057→0.019→0.010 for n=2k→20k→100k. Composition shows CONVERGENCE: the hero tiled diagram (n≈5200) + jagged boundaries of smaller n (110,900) fluctuating around the fixed gold Ω = 'random object, deterministic shape'. Direct cousin of 02's arctic ellipse). Both verified-in-code before drawing; README extended with a Coda + story coda; PNGs 0.12/0.58 MB. |
| 2026-06-29 | `claude/beautiful-heisenberg-vq6jkh` | Procedural triptych **The Edge of the Possible** (unifying thread = *a hard boundary a system produces on its own when pushed to its limit*) in `art_vq6j/`, **three NEW techniques across three visual grammars**: `01_edge_of_chaos` (**4096² centerpiece**: the **Markus–Lyapunov fractal** — forced logistic map `xₙ₊₁=rₙxₙ(1−xₙ)` with `rₙ` cycling the periodic word **`BBBBBBAAAAAA`** over (a,b)∈[2.5,4]²; per-pixel **Lyapunov exponent** λ=⟨ln|rₙ(1−2xₙ)|⟩, 900 iters after 600 transient, SSAA2, ~6½min. λ<0 stable→silken **gold drapery** (brightness=−λ depth); λ>0 chaos recedes to navy void EXCEPT a thin band of **small-positive λ just inside the chaos** lit as a **frothy cyan coastline** = the filigree where order barely loses. 'Zircon City': period-doubling pagoda skylines + self-similar ship-rigging + central radiant star where 4 stability lobes meet. KEY palette move = show structure in BOTH regimes: deep chaos dark, near-boundary chaos glows via sharp `exp(−(λ/w)²)`. Filigree aliases hard → SSAA essential), `02_arctic_ellipse` (2048²: **uniform random lozenge tiling of a hexagon a×b×c=300×216×198 = boxed plane partition**, the 3-D dimer cousin of last run's arctic circle. Sampled **exactly-uniform in the limit by VECTORISED checkerboard Glauber** on the height function — same-parity cells are independent given the other parity, so a whole colour class updates in ONE numpy op; 60k sweeps, mixing verified by the **plateau of flippable-site density** (NOT vol-fraction, which hits 0.5 instantly and lies). 3 rhombus orientations = 3 cube-face dirs → glowing isometric heap; **3 frozen corners** (solid single-orientation: gold tops / teal+blue walls) vs a disordered **temperate sea**, boundary = the tilted **arctic ELLIPSE** (Cohn–Larsen–Propp inscribed ellipse). Frozen fraction is affine-invariant `1−π/(2√3)≈9.3%` so corner caps stay small whatever a,b,c — asymmetry only TILTS the ellipse), `03_restrict_the_possible` (2048²: **Hadwiger–Nelson chromatic number of the plane**, 5≤χ≤7. Upper bound χ≤7 = a stained-glass **hexagonal 7-colouring**, colour `=(q−2r) mod 7` = the **Eisenstein norm-7 sublattice** (min same-colour dist √7·s); `(q+2r)`, the textbook neighbour-separating map-colouring, FAILS for unit distance — VERIFIED by Monte-Carlo, (q−2r) gives **0 violations / 200k random unit-distance pairs**, valid spacing s∈(0.671,0.866). Lower bound χ≥4 = the **Moser spindle** (7 verts, 11 unit edges) overlaid luminous, **chromatic number verified =4 by exhaustive backtracking** (a 4-col exists, no 3-col); caption cites de Grey 2018 χ≥5. Deep-jewel desaturated palette + leaded grout + warm halo behind the proof so it sits with the moody gold pair). ✅ Read memory first; fresh names/techniques, no collisions; all NON-disk (a dynamics parameter-plane, a 3-D combinatorial tiling, a euclidean colouring+graph). Seeded by **live MathOverflow** ('no entire f with Re/Im opposite sign when |z−w|=1'→chromatic number of the plane; 'density of good approx of torus rotations'; 'min triangle of disjoint unit-square centres') + **Philosophy.SE** ('Is there a limit to the complexity of the universe?'; 'Why do philosophers restrict the realm of the possible?'; 'Is Infinity a Continuum of distinct Boundaries?'). Renders: lyap 4096²≈6½min, lozenge 60k-sweep+draw≈90s, chromatic 2048²<10s. PNGs 16/5.1/1.4 MB. |
| 2026-06-29 | `claude/beautiful-heisenberg-z70k0h` | Procedural triptych **The Frozen and the Free** (unifying thread = *locked/determined order vs free/disordered flux, with the **rationals** drawing the boundary*) in `art_z70k/`, **three NEW techniques across three different visual grammars**: `01_forbidden_roots` (**4096² centerpiece**: the **Littlewood-roots fractal** — plot **all roots of all 2²⁴≈16.8M degree-24 polynomials with coefficients ±1** (~400M roots). VECTORISED via **stacked companion-matrix eigenvalues**: build each chunk's companions as a real `(chunk,d,d)` array and call `np.linalg.eigvals` on the STACK (LAPACK loops in C) — d=24, 16.8M polys ≈ **30 min**; chunk ~65k to bound RAM, real float64 companion halves memory. **Bilinear (anti-aliased) splat** + conjugate symmetry. The roots crowd a luminous unit-circle annulus fringed by a **dragon-curve filigree**; the SUBJECT is the **apophatic** part — black **HOLES punched at the roots of unity** (z=±1 big voids, 6th/8th-root eyes), each ringed by a **bright halo** where roots pile against a forbidden zone. 4-fold + inversion symmetry (z→−z, z→z̄, z→1/z). **HISTOGRAM-EQUALISE the log-density** (rank→[0,1]) so the faint filigree, the bright ridge AND the halo-voids all read at once — plain log+filmic clips the bulk to white. Real roots pile on the exact Im=0 row → a seam; fix by splatting the conjugate only where |Im|>ε and smoothing the centre rows), `02_arctic_circle` (2048²: **uniform random domino tiling of the Aztec diamond order N=1024** by the **Elkies–Kuperberg–Larsen–Propp domino-shuffling** algorithm, coloured by the 4 domino orientations → 4 **solid frozen crystalline corners** vs a **free temperate 4-colour shimmer**, split by the **Arctic Circle** radius N/√2; 1 cell=1px grain = the disorder. Convention n/s = HORIZONTAL dominoes sliding up/down, e/w = VERTICAL sliding right/left; delete bad (n,n,s,s)/(e,w,e,w), slide, fill empty 2×2 blocks by fair coin (s,s,n,n)/(w,e,w,e). **KEY BUG**: after each slide the empty cells are disjoint 2×2 blocks but **NOT all on one (px,py) coset** (same-sum-parity blocks overlap diagonally) → a simultaneous/parity fill corrupts; must fill **GREEDILY in boundary-first (row,col) scan order** with an O(1) recheck (vectorised `np.where` candidate-find + short python loop), likewise for delete. VERIFIED a full perfect tiling at every order + arctic radius + pure-colour corners = the correctness proof; N=1024 ≈ 3.5 min), `03_arnold_tongues` (2048²: **rotation number W of the sine circle map** x→x+Ω−(K/2π)sin2πx over the (Ω,K) plane, iterating the LIFTED map ~6000× (vectorised over all pixels). **Mode-locked rational tongues** (Stern–Brocot/Farey order) = **frozen wedges** detected by small `|∇W|` vs the **free quasiperiodic sea**; wedges hang from each rational, widen to the **critical line K=1** then fray into chaos. **CENTERED-BRIGHTNESS palette** (dark navy at the dominating ends W=0/1 so the 0/1,1/1 tongues recede; bright gold at the 1/2 heart) + dim sea so the Farey cascade is the subject; frame K∈[0,1.3]. At K=1 the tongues fill the line save a **measure-zero** Cantor dust — "are we dead almost everywhere"). ✅ Read memory first; fresh names/techniques, no collisions; all NON-disk (a ℂ point-cloud fractal, a combinatorial tiling, a parameter-plane field). Seeded by **live MathOverflow** ("Density of good approximations of irrational torus rotations"→Arnold/rotation; "p-adic valuation of ∏Φ_q(k)" cyclotomics→roots of unity; "Apophatic mathematics"→the forbidden holes) + **Philosophy.SE** ("Are we dead almost everywhere?"→measure-zero free set; "If there is no randomness, what is freedom?"→frozen vs free; "Why restrict the realm of the possible?"). ALSO-RANS listed (unbuilt, next-run seeds): **large countable ordinals** as a nested ε₀ comb (apophatic/Gödel); **Minkowski ?(x)** singular staircase (Stern–Brocot, measure-zero); **boxed plane partition / glowing-cube lozenge tiling** (3D dimer cousin of the arctic circle, has its own arctic ellipse). Renders: roots eig-build 4096² ≈ 30 min, aztec N=1024 ≈ 3.5 min, arnold 2048² ≈ 16 min. PNGs 17.8/0.6/0.6 MB. |
| 2026-06-28 | `claude/beautiful-heisenberg-oua4xf` | Procedural triptych **What Cannot Be Avoided** (unifying thread = *inevitable structure* — patterns that must appear no matter how free the input; **two conjectures bracketing one theorem**) in `art_oua4/`, **three NEW techniques across three different visual grammars**: `01_everything_falls_to_one` (**4096² centerpiece**: the **Collatz reverse-tree as a luminous feather/plume**. For the first **150,000** integers, take each forward trajectory `n→n/2`(even)`/3n+1`(odd)`→…→1`, REVERSE it (root=1→leaf=n), and draw it as a parity-bent polyline: turn **+ae=0.070** on an even node, **−ao=0.110** on an odd node, fixed step. **All 150k threads share the origin = the number 1**; rendered by **additive bilinear splatting** so overlap=brightness → the shared trunk blazes white-gold (the convergence point) and lone hailstone paths stay faint teal; **PCA-aligned to stand vertical** (rotate geometry −51°, tip at bottom), filmic teal→gold ramp + bloomed convergence tip. The bend ANGLES are the whole composition dial: ratio ~0.64 stands it as an upright plume, too-equal angles curl it into rings, ratio~0.5 hooks it into a scythe — render small and sweep), `02_only_three_distances` (2048²: the **Steinhaus three-distance theorem** as **polar growth-rings**. radius=time n outward, angle=position x on the circle `[0,1)` the **golden rotation** acts on; ring n = the circle partitioned by `{kα mod 1 : k≤n}`, arcs coloured by **gap-length class** (verified **exactly 3 classes at every n**) — gold=smallest, teal=mid, violet=largest. The gold knits into **Fibonacci spiral arms** (=why phyllotaxis uses the golden angle) and the **concentric reorganization rings** are where a new smallest gap is born, always at a Fibonacci n; glowing seed at centre = the origin 0), `03_a_square_in_every_loop` (2048²: the **Toeplitz inscribed-square conjecture** — a wild **star-shaped radial Jordan curve** r(θ) containing **SEVEN inscribed squares**, found honestly: a square's 4 corners must lie on the curve so the two corner-defects `|C|−r(∠C)`, `|D|−r(∠D)` must vanish together; locate by **sign-change intersection** on a (θ₁,θ₂) grid, refine by **2-D Newton to 1e-10**; additive glow render with the **28 contact pegs blazing** as the conceptually-meaningful points; seed 34 of a harmonic-curve search gives 7). **Then (same branch, user asked for listed backup idea #4) a 4th piece** `04_the_weight_of_the_simplest_explanation` (2048², flagged "promoted backup, by request"): **Solomonoff's universal distribution m(x) over binary strings, MEASURED via the Coding Theorem Method** — sample **12,000,000 random (5-state,2-symbol) Turing machines** (2 seeds × 2M × 3 batches), run each on a blank tape (T=800, tape W=384), tally outputs of the **5.07M that HALT** (≈42%/batch halt, ~51% escape the tape ≈ the >24-cell-output discards, ~7% loop). Output freq D(x)≈m(x), `K(x)≈−log₂(D(x)/N)`; **563 distinct outputs**, textbook Occam: `01`/`10` K≈2.75, `010` K≈4.0, `11` K≈4.36, … Drawn as a **skyline**: each string a tower at `x=`its binary fraction `0.b₁b₂…`, **height=log m(x)=−K(x)** → a few blazing GOLD skyscrapers (simplest) over a teal forest of the complex many; self-similar comb tallest at simple dyadic fractions, top towers labelled bitstring+K after downscale. **KEY: the TM sim is fully VECTORISED — millions of machines stepped in LOCKSTEP as NumPy [K]-arrays** (per-machine tables `wr/mv/nx[K,n,2]` indexed by `(state,sym)`; tape[K,W],head[K],state[K]; halt=next==n, escape=head∉[0,W); outputs tallied by packed `(len<<32)|val` int64 key + `np.unique`) → 12M machines in ~16 min (~160s/2M-batch); a per-machine Python loop would be hopeless. **Then (same branch, user asked for the two open angles I'd listed in this memory) TWO more pieces** `05_the_busy_beaver_garden` (2048²: **a 7×7 quilt of 49 small-(5,2)-TM space-times** — time down, tape across, teal=marked cell, GOLD=head worldline; curated from ~1.5M random machines by **gzip-density of the space-time (Kolmogorov-flavoured complexity)** and **sorted trivial→complex** so the garden runs from a lone gold diagonal through sweeping triangles & ruled stripes to dense textures. Caption is honest: these RUN 300 steps (mostly don't halt); the real Busy-Beaver champions can't fit — BB(5)=**47,176,870 steps** and BB is **uncomputable**. KEY LESSON: random (5,2) TMs in ≤300 steps are overwhelmingly TRIVIAL — solid triangles (sweeps) & stripes (periodic); nested/Sierpinski fractals are very rare, and selecting by *direction-changes* finds boring solid wedges. gzip-density is the right richness axis, but the WINNING move was to **SPAN the full complexity range and sort by it** (drop near-empty bottom 18% + pure-noise top), turning "most are dull, few are rich" into the composition itself — a gradient quilt — rather than hunting the rare jewel) and `06_programs_are_bitstrings` (2048²: **Binary Lambda Calculus** — twelve fundamental λ-terms as **Tromp lambda diagrams** (blue bar=abstraction λ, gold link=application, white vertical=variable→its binding bar) with their **actual BLC bitstrings** (gold/teal cells) and prior weight **2⁻ⁿ**, sorted by program length: `I`=`0010`(4b), `0`,`K`, Church 1/2/3/4, `S`=`00000001011110100111010`(23b), `succ`,`plus`, `Y`(30b), `Ω`(18b, never halts). Built a VERIFIED engine `blc.py` (de Bruijn terms; BLC `Var i→1ⁱ⁺¹0`, `Lam→00·`, `App→01··`; encode/decode round-trip; normal-order β-reduction checked: `plus 2 1⇒3`, `succ c2⇒c3`) + `blc_diagram.py` (the abstraction-bar/variable/application-link layout via an "add-bar-on-top, push-down, open-variables-rise-to-binders" recursion; verified by eye that I/K/S/Church match canonical Tromp diagrams). This is the PUREST Solomonoff substrate: a program literally IS a bitstring weighted 2⁻ᵖ, no measurement needed). **Then (same branch, user asked "why are the BBs all triangles?" then "hunt!") a 7th piece** `07_the_rare_ones` (2048²: **the hunt for NON-triangular TMs**). The why: a TM head moves ≤1 cell/step so the touched region is a **discrete light-cone = triangle**, and the gold diagonal IS the head; the interior fills because random tiny machines almost always **DRIFT** one way laying a periodic trail (solid/striped triangle). To break the triangle you must find machines that DON'T drift — gate on **CONFINEMENT `steps/width ≥ 3`** (head revisits each column ≥3×; this kills every drift-triangle in one stroke), then rank survivors by gzip-incompressibility. ~1.2M machines × 700 steps, wide tape; the confined survivors are **tall tapering SPIRES** (width 23–55, confinement up to 30×) with the head's **gold ZIGZAG worldline** carving notched/striped/counter structure — the ones that actually COMPUTE rather than smear; their gzip-density 0.34–0.46 ≫ the random sample's 0.17. PRESENTATION LESSON: confined machines are intrinsically tall-thin; square tiles make invisible slivers — show them as a **COLONNADE of full-height vertical specimens** (embrace the aspect → a forest of luminous obelisks). Biased selection (the rare exceptions), framed as companion to 05's typical-case quilt. PNG 0.93 MB. README intro + per-piece sections extended; PNGs 0.30/0.14 MB. ✅ Read memory first; fresh names/techniques, no collisions; all NON-disk (a thread plume, a polar field, a euclidean curve+web, a spectral skyline, a TM-spacetime quilt, lambda diagrams, a TM-spacetime colonnade). Seeded by **live MathOverflow** ("Convergence in a simpler Collatz variant"→Collatz; "Density of good approximations of irrational torus rotations"→three-gap; "Does every Jordan curve have an approximation with a large inscribed square?"→Toeplitz — all THREE were open-thread seeds AND live front-page hits) + **Philosophy.SE** (determinism/"prefer a coincidence with a known mechanism"/unreasonable-effectiveness → the inevitability thread). Renders: feather build 4096² ≈ 73s (150k polylines), gap ≈ 40s, square ≈ 20s. PNGs 4.5/2.7/0.5 MB. |
| 2026-06-27 | `claude/beautiful-heisenberg-kvrz78` | Procedural triptych **The Order of Coexistence** (Leibniz: space = "the order of coexistences"; unifying thread = *nearness without merging* — things that approach, crowd, depend on each other yet never collapse together) in `art_kvrz/`, **three NEW techniques across three different visual grammars**: `01_the_only_coincidence` (**4096² centerpiece**: **Dyson Brownian motion** — an `N×N` GUE Hermitian matrix **started at H=0 so all N eigenvalues coincide at one point**, then driven by an **Ornstein–Uhlenbeck matrix flow** (`H←H−θ·dt·H+√(2θ·dt)·GUE`, stationary law = unit GUE); eigenvalues `λᵢ(t)=eigvalsh(H)/√N` obey Dyson's **logarithmic level repulsion** → they **fan out of the single origin into the Wigner semicircle and NEVER cross again**; N=36, T=1100, θ=1, τ=6, seed 7; rendered as glowing **non-crossing threads** smoothed per-path along time, jewel palette by eigenvalue rank, filmic bloom — the fan-from-one-point composition tells the whole story), `02_circles_that_only_kiss` (2600×1456: the complete **modular picture** — **Ford circles** (horocycles, WARM) `p/q↦` circle at `(p/q,0)` radius `1/(2q²)`, tangent iff `|ps−qr|=1` (Farey neighbours) and **never overlapping**, + **recursive Farey tessellation** (geodesic semicircle arches, COOL) by mediant subdivision; colour = **Stern–Brocot depth** = Σ continued-fraction quotients; every rational <1 named once = the **bijection ℕ↔ℚ**, infinitely many circles+arches piling into a glowing **cusp over each rational** on the axis), `03_a_world_made_of_neighbours` (2048²: **emergent geometry from pure relation** — sample a **Fibonacci sphere**, build the **kNN(8) adjacency graph**, **DISCARD all coordinates**, then recover the orb from the **graph Laplacian's 3 lowest non-trivial eigenvectors** (Laplacian eigenmaps — for a sphere these ARE the linear harmonics; recovered-radius CV≈0.04 verified); drawn as a glowing geodesic **wireframe globe** woven from its own edges, **anti-aliased bilinear edge splatting** + **back-dimming (∝depth^1.6)** so it reads as solid, vertices tinted by one harmonic = monadology/relational space made literal). ✅ Read memory first; fresh names/techniques, no collisions; all NON-disk (a time-thread field, an upper-half-plane packing, a 3-D network) honouring "prefer non-disk". Seeded by **live MathOverflow** ("Spectrum of sum over a conjugacy class in Sₙ tends to Wigner/Gaussian" → Dyson; "How nice can a bijection ℕ↔ℚ be?" → Ford/Farey) + **Philosophy.SE** (the **monadology / emergent-spacetime** cluster, "Nothing and a Thing" → relational sphere). Renders: Dyson 4096² ≈ 2min, Farey 2600 ≈ 8s, sphere 2048² ≈ 16s. PNGs 13/0.7/3.4 MB (all well under limits). |
| 2026-06-27 | `claude/beautiful-heisenberg-v6o5fn` | Procedural triptych **What the Loop Remembers** (a *monodromy* thread — what a path keeps, or refuses to keep, on returning) in `art_v6o5/`, **three NEW techniques across three different visual grammars**: `01_the_braid_that_remembers` (**4096² centerpiece**: the **(20,12) torus link = a closed braid / Abelian-anyon world-lines**, closure of `(σ1…σ19)^12`, **gcd(20,12)=4 components** each a `T(5,3)` knot; the over/under weave — the thing the **Kauffman bracket** remembers — falls out of honest 3-D torus geometry via a **painter's-algorithm depth sort** of per-strand point splats; glossy glass-rod tubes from an **off-centre specular** across each cross-section; restrained density-matched bloom + saturation boost so strands stay jewel-toned, not white), `02_a_house_that_forgets_every_loop` (2048²: **Bing's house with two rooms** — *contractible yet non-collapsible* 2-complex — assembled from **thin-slab box-SDFs** (two chimneys threading the wrong rooms, holed top/bottom/middle walls, two connecting fins), **vectorised numpy SDF sphere-trace on a shrinking active set**, cut-away dollhouse camera; amber=upper-access tube, teal=lower-access tube), `03_the_tamed_logarithm` (2048²: the **Bloch–Wigner dilogarithm** `D(z)=Im Li₂(z)+arg(1−z)log|z|`, the single-valued combination that **cancels Li₂'s monodromy**; complex `Li₂` via inversion/reflection reduction to a fast series, **functional equations verified to 1e-16**, `D(i)=Catalan`; level sets equally spaced in **ideal-hyperbolic-tetrahedron volume** → they crowd to the two cusps, warm/cool by sign across the **zero-river of the real axis** = "presence of an absence"). ✅ Read memory first; fresh names/techniques, no collisions; avoided a 3rd Poincaré-disk piece (used a torus, a 3-D solid, and a euclidean relief — all non-disk). Seeded by **live MathOverflow** ("Kauffman bracket for Abelian anyons", "Bing's house with two rooms is contractible", Lewin dilogarithm) + **Philosophy.SE** ("absence of presence vs presence of absence", "restrict the realm of the possible"). Renders: dilog <45s; bing ~9min @4096-internal (SDF tracer is the heavy one); braid ~9min @8192-internal, **peak ~8.5GB on the 16GB box — fine** (this env has more RAM than the OOM-killed one in the uh5/p847 notes). **Then (same branch, user loved the set and asked for two of the listed backup ideas) TWO more pieces** (both flagged "promoted from the original six by request"): `04_the_only_way_to_know` (2048²: **Rule 30 XOR light-cone = computational irreducibility made visible** — evolve two random space-times differing in ONE bit, XOR them; the divergence fills a discrete **light cone**, right edge ruler-straight at the speed limit, **left edge a fractal sub-light front**, over the dim teal irreducible Rule-30 substrate. Simulate `Wsim=2W+64` so the periodic `np.roll` boundary never wraps into the cropped frame), `05_the_cube_that_composes_to_one` (2048² annotated plate: **Bhargava's cube → three quadratic forms → Gauss composition = identity, via Conway topographs**. Cube `(-1,-1,-1,2,0,1,2,2)`, disc **−23**, forms `(1,1,6),(2,1,3),(2,-1,3)` = the whole **C₃ class group**, `1·g·g²=1` **verified by Dirichlet composition** in `bhargava_core.py`; each form drawn as its Conway topograph = a glowing radial **trivalent value-tree** (`topograph.py`, faces=primitive vectors, parallelogram law `Q(u+v)+Q(u−v)=2Q(u)+2Q(v)`, warm well → cool rim), assembled with a 3-D labelled cube + caption block). |
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
Spin(8) triality triskelion (PIL vector emblem)**, **(p,q) torus link / closed
braid as depth-sorted woven glossy tubes (Abelian-anyon world-lines, Kauffman
bracket)**, **Bing's house with two rooms as thin-slab box-SDF sphere-trace
(contractible non-collapsible 2-complex)**, **Bloch–Wigner dilogarithm as a
real single-valued relief with level-sets-by-volume (tamed monodromy)**,
**Rule 30 XOR light-cone (computational irreducibility = damage cone over the CA
substrate)**, **Bhargava cube → 3 quadratic forms → Gauss composition, drawn as
Conway topographs (radial trivalent value-trees)**, **Dyson Brownian motion =
non-crossing eigenvalue threads of an OU-driven GUE matrix started at H=0 (random-
matrix level repulsion, Wigner semicircle)**, **Ford circles + recursive Farey
tessellation = the modular picture (rationals as kissing horocycles, depth-coloured,
bijection ℕ↔ℚ)**, **spectral / Laplacian-eigenmap graph embedding = geometry recovered
from pure kNN adjacency (emergent relational space, Leibniz monadology)**,
**Collatz reverse-tree as a parity-bent additive-thread plume converging to one
glowing point (the number 1)**, **Steinhaus three-distance theorem as polar
growth-rings of the golden rotation (Fibonacci spiral arms, gap-class colour)**,
**Toeplitz inscribed squares in a star-shaped Jordan curve via corner-defect
zero-intersection + 2-D Newton (contact pegs splatted)**, **Littlewood /
sign-polynomial roots in ℂ via stacked companion-matrix eigenvalues (the
dragon-fractal of all ±1-coeff polynomials; holes at roots of unity, density
histogram-equalised)**, **Aztec-diamond uniform random domino tiling via
EKLP domino-shuffling (the arctic circle; 4-domino-type colour, frozen corners
vs free temperate)**, **Arnold tongues / sine-circle-map mode-locking via a
rotation-number field over the (Ω,K) plane (Farey wedges, devil's staircase,
lockedness = small |∇W|)**.

**Markus–Lyapunov fractal (Lyapunov exponent of a periodically-forced logistic map over the (a,b) parameter plane; the order/chaos boundary, with the filigree = the small-positive-λ coastline just inside chaos)**, **boxed plane partition / uniform lozenge tiling of a hexagon via vectorised checkerboard Glauber on the height function (the arctic ELLIPSE; 3-D dimer cousin of the arctic circle; glowing isometric cube-heap)**, **Hadwiger–Nelson chromatic number of the plane (stained-glass hexagonal 7-colouring via the Eisenstein norm-7 sublattice (q−2r mod 7) + the Moser spindle unit-distance graph, verified χ=4)**.

**Minkowski question-mark `?(x)` / Conway's slippery devil's staircase, rendered as the attractor of a 2-map IFS via a vectorised chaos game (brightness = the singular Stern–Brocot measure) over nested Stern–Brocot boxes**, **Logan–Shepp / Vershik–Kerov limit shape of a Plancherel-random Young diagram (RSK from a random permutation, Russian convention, with the verified limit curve Ω overlaid; the random-object→deterministic-shape convergence shown via several n)**.

**permutation CYCLE structure as a grouped-arc chord diagram (Poisson–Dirichlet / GEM partition, Golomb–Dickman giant cycle)**, **the permutohedron = Sₙ Cayley graph / weak Bruhat order as a glowing 3-D polytope (truncated octahedron for S₄)**, **RSK + longest increasing subsequence (patience sorting, Ulam 2√n)**, **the Mahonian inversion distribution via q-factorial coefficients (→ Gaussian)**, **the Mallows measure q^{inv} permutation matrix sampled by geometric Lehmer digits (order↔disorder dial)**.

**uniform random SORTING NETWORK = AHRV sine curves, sampled EXACTLY via uniform staircase SYT (GNW hook walk) + the verified Edelman–Greene bijection (reduced word ↔ staircase SYT)**, **pattern avoidance: uniform 231-avoiding (Catalan / stack-sortable) permutation via the recursive σ=L·max·R decomposition → permuton limit shape**, **the Eulerian triangle (descents) as a glowing recurrence-built pyramid**.

**Viennot's shadow-line / 'light and shadows' geometric construction of RSK (verified == RSK on S₁..S₇)**, **Lindström–Gessel–Viennot non-intersecting lattice paths / vicious walkers (LGV determinant verified; corner-flip Glauber; Tracy-Widom band)**, **the strong Bruhat order Hasse diagram (graded by inversions, weak-vs-strong edges, Mahonian ranks)**.

**the Archimedean great-circle SPHERE lift of a sorting network (AHRV/Dauvergne — trajectories=sine curves=shadows of great circles, lifted & verified exact)**, **Fomin growth diagrams (RSK via local rules on a grid of Young diagrams; verified == RSK on S₁..S₇)**, **the type-B permutohedron / hyperoctahedral group B₃ (signed permutations = great rhombicuboctahedron)**.

**the Sₙ CHARACTER TABLE via Murnaghan–Nakayama (signed-log heatmap; dims=hook-length, orthogonality verified)**, **Young's lattice / the differential poset (partitions as nodes, paths=f^λ)**, **jeu de taquin rectification (=RSK insertion tableau; the plactic monoid)**, **Foata's second fundamental transformation (inv∘foata=maj; inversions≅major index)**.

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
piece 04. **Kauffman bracket / Abelian anyons** is now USED — built 2026-06-27
as the torus-link closed braid; the *Temperley–Lieb cup/cap state-sum* angle is
still open if you want the bracket as a planar-diagram recursion rather than a
woven link.) **Bhargava cubes** are now USED — built 2026-06-27 (same branch, by
request) as `05`, Gauss-composition drawn via three Conway **topographs** (radial
trivalent value-trees, NON-disk — the planar layout worked well). **Rule 30 / CA
spacetime** is now USED — built 2026-06-27 (same branch, by request) as `04`, the
XOR light-cone. **Bing's house** is now USED. **Force-directed/spectral graph layout** is now USED — built 2026-06-27 as `03`
(Laplacian eigenmaps recovering a sphere from kNN adjacency; the *force-directed
spring* variant and *non-sphere* manifolds — torus needs 4 eigvecs + angle
extraction, genus-2, an emergent-spacetime Wolfram-hypergraph rewrite — are still
open). **Random-matrix theory** is now USED (Dyson BM); the *static* GUE/GOE
eigenvalue cloud + semicircle, **Dyson gas / Coulomb log-gas equilibrium**, and
**Montgomery pair-correlation / zeta zeros vs GUE** are still open. The
**rationals/continued-fractions** vein now has Ford+Farey; still open there:
**Stern–Brocot binary tree** drawn as a mediant tree, **Minkowski ?(x)** singular
staircase. **Three-distance theorem / phyllotaxis** is now USED (2026-06-28, polar
growth-rings; the *flat Vogel sunflower coloured by gap-class* and the *unrolled
Sturmian staircase strip* variants are still open — both prototyped this run). **Collatz**
is now USED (2026-06-28, reverse-tree feather; the *(steps-remaining, log2 value)
drainage-river* layout was prototyped but read as stipple — abandoned for the botanical
bend-tree; a true *radial/Reingold-Tilford tree layout* of the reverse graph is still
open). **Inscribed-square problem** is now USED (2026-06-28, Toeplitz squares in a Jordan
curve; the *inscribed-rectangles of every aspect ratio* (Greene–Lobb) continuum is still
open). Still open: Cantor/Gödel diagonalization, singular moduli mod p, Gaussian primes
(with a chart), Temperley–Lieb cup/cap state-sum, other CA (Rule 110, Lyapunov),
real-quadratic indefinite topographs (with RIVERS, not just definite wells),
**near-integer coincidences / almost-integers e^{π√163}** (brainstormed, not built).
**Solomonoff / algorithmic probability** is now USED (2026-06-28, by request — three pieces:
04 the universal distribution m(x) measured via the Coding Theorem Method from 12M vectorised
small Turing machines (complexity skyline); 05 the **Busy-Beaver garden** (gzip-curated 7×7
quilt of small-TM space-times); 06 **binary lambda calculus** (Tromp lambda diagrams of 12
verified λ-terms + their BLC bitstrings, prior 2⁻ᵖ). Still open in this vein: a SINGLE
β-reduction-as-spacetime piece (one λ-term normalising, term-size or the diagram morphing
over reduction steps — `blc.py` already has the reducer+sequence); the actual *BLC
self-interpreter* as a hero diagram (need the exact published term — I avoided it to not
ship a wrong one); and a *genuinely nested/fractal* TM found by targeted search rather than
random sampling, e.g. an XOR/Rule-90-like (5,2) machine.)
Note: the quantum-revival, space-filling-curve, and p-adic/ultrametric veins
are now USED (this run). The Poincaré disk has now hosted TWO distinct
techniques (kaleidoscope fold, geodesic tree) — a third disk piece would start
to feel repetitive; prefer a non-hyperbolic chart next. Pick an unbuilt vein
and build a *new* technique for it.
Note (2026-06-29 run #2, `vq6jkh`): **Markus–Lyapunov fractal**, **boxed plane partition / lozenge tiling (arctic ELLIPSE) via checkerboard Glauber**, and **Hadwiger–Nelson chromatic number of the plane (7-colouring + Moser spindle)** are now USED. Still-open cousins worth a future run: other Lyapunov words / a deep ZOOM into the filigree coastline; the **cube grove / steeply-tilted** boxed partition or an explicit arctic-ellipse OVERLAY; the **six-vertex model / square ice** (the other 2-D arctic phenomenon) and the **rhombus-tiling 'cube grove'**; for χ(plane) the **Golomb graph**, the **Golomb/de Grey ≥5 graph**, or the 7-colouring animated as a sliding sub-lattice. Two ideas brainstormed-but-unbuilt this run (good next seeds): **Gerver's moving sofa** (largest area through an L-corridor = envelope of the rotating corridor) and the **VKLS / Logan–Shepp–Vershik–Kerov limit shape of a random Young diagram (Plancherel)** — both are 'limit/extremal shape' cousins of the arctic ellipse. Also still brainstormed-unbuilt: **Minkowski ?(x)** singular staircase.

Note (2026-06-30 follow-up, same `vq6jkh` branch): **Minkowski ?(x)** and the **VKLS / Logan–Shepp–Vershik–Kerov random-Young-diagram limit shape** are now USED (pieces 04/05). Still-open *limit-shape / singular* cousins: **Gerver's moving sofa** (still unbuilt), the **arctic ellipse with the actual cube cells / a steep 'cube grove'**, **Conway's box ?⁻¹ / a `?(x)`-WARPED Farey net or image**, the **Pólya/uniform random partition limit shape** (different ensemble → a different curve than Plancherel), the **six-vertex / square-ice arctic curve**, and **TASEP / corner-growth (the same KPZ limit shape as a height function evolving)**.

Note (2026-06-30 follow-up #2): NEW **`permutations/` gallery** thread is now active (Sₙ deep-dive: cycles, permutohedron, RSK/LIS, Mahonian, Mallows — all USED). **DONE in Vol II (2026-06-30 #3): uniform sorting network (AHRV, via Edelman–Greene — `eg.py` has verified forward+inverse + hook-walk SYT), pattern avoidance / Catalan, descents / Eulerian.** Still OPEN for a future permutation run: the **plactic monoid / jeu de taquin** (RSK's deeper structure), **Foata's bijection** (maj ↔ inv, 'the second fundamental transform'), **Mallows at the q=1−β/n scaling limit** (the actual smooth limit-shape curve, not just a band), the **sorting network's half-time permutation matrix / the great-circle 3-D sphere lift** (AHRV's deeper conjecture-now-theorem), **oscillating tableaux / the RSK growth-diagram local rules (Fomin)**. DONE in Vol III (2026-06-30 #4): **Viennot light/shadow RSK** (`viennot.py`), **LGV non-intersecting paths** (`lgv.py`), **strong Bruhat order**. Still OPEN after that: the **plactic monoid / jeu de taquin & Knuth equivalence**, **Foata's bijection (maj↔inv)**, the **Mallows q=1−β/n scaling-limit curve**, the **sorting-network great-circle SPHERE lift (Dauvergne)**, **Fomin growth diagrams / local rules**, **affine / type-B,D Coxeter analogues (signed permutations, the hyperoctahedral group)**, and **the cycle-type ↔ conjugacy-class / character-table heatmap of Sₙ**. Reusables now: `sortnet.py`,`eg.py`,`patterns.py`,`cycles.py`,`viennot.py`,`lgv.py`,`figkit.py`. DONE in Vol IV (2026-06-30 #5): **great-circle sphere lift** (`greatcircle.py`), **Fomin growth diagrams** (`fomin.py`), **type-B permutohedron** (`render_14`). STILL OPEN after four volumes (the gallery is now 14 figures — consider it rich; only revisit if asked): the **plactic monoid / jeu de taquin & Knuth equivalence**, **Foata's bijection (maj↔inv)**, the **Mallows q=1−β/n scaling-limit curve**, **affine/type-D Coxeter analogues**, the **Sₙ character table / conjugacy-class heatmap**, and the **Schützenberger involution / evacuation**. Reusables now also include `greatcircle.py`, `fomin.py`. DONE in Vol V (2026-06-30 #6): **Sₙ character table** (`characters.py`: Murnaghan–Nakayama on the abacus), **Young's lattice** (`render_16`), **jeu de taquin** (`jdt.py`), **Foata's bijection** (`foata.py`). The `permutations/` gallery is now **18 figures across Volumes I–V** — treat it as COMPLETE; only extend if explicitly asked. The few remaining classical threads if ever needed: **Schützenberger promotion/evacuation** (a natural GIF — cyclic sieving), the **Mallows q=1−β/n scaling-limit curve**, **affine/type-D Coxeter analogues**, and the **q,t-symmetry of the joint (maj,inv) distribution**.
Note (2026-06-29 run): **Littlewood/sign-polynomial roots**, the **Aztec-diamond
arctic circle (domino shuffling)**, and **Arnold tongues (circle-map mode-locking)**
are now USED. Still-open cousins worth a future run: the **Newman {0,1}** and
**Borwein {−1,0,1}** root variants + a deep ZOOM on the dragon filigree near a root
of unity; the **boxed plane partition / lozenge "stacked-cube" tiling** (3-D dimer
cousin of the arctic circle, with its own arctic *ellipse*) — fully NEW; the **1-D
devil's-staircase curve** of the circle map drawn as a glowing self-similar
staircase, and the **Mandelbrot-period bulbs** (the disk version of mode-locking).
Three ALSO-RANS brainstormed-but-unbuilt this run (good next seeds): **large
countable ordinals** as a nested ε₀ "comb of combs" (apophatic + Gödel/diagonal
thread); **Minkowski ?(x)** singular staircase (Stern–Brocot, derivative 0 a.e. but
strictly increasing = "alive on a measure-zero set"); the lozenge boxed-plane-partition
above. Still open from before: Cantor/Gödel diagonalization, singular moduli mod p,
Gaussian primes (with a chart), Temperley–Lieb cup/cap state-sum, other CA
(Rule 110, Lyapunov), real-quadratic indefinite topographs (with RIVERS),
near-integer coincidences e^{π√163}, Stern–Brocot mediant tree, Montgomery
pair-correlation / zeta zeros vs GUE, Greene–Lobb inscribed rectangles.

Note (2026-07-01 run, `4zx43y`): new theme **"Exceptions to the Rule"** (extremal /
rare / unlistable objects). Now USED: the **moving-sofa problem** (Gerver, via
∩-of-rotating-corridor + area-maximising motion + wall-envelope caustic),
**MSTD / more-sums-than-differences sets** (the arc-loom: pair→semicircle,
apex=sum, radius=difference), and — finally — **Cantor/Turing DIAGONALIZATION**
(the long-open seed; done on the Walsh–Hadamard array, diagonal=Thue–Morse,
flip=the escaped real). Still-open COUSINS worth a next run: the **Kakeya /
Besicovitch needle set** (measure-zero set containing a unit segment in every
direction — the *minimum*-area cousin of the sofa's *maximum*; Perron-tree
sprouting-triangle construction, would pair beautifully with the sofa), the
sofa's **half-time / continuous MOTION as a GIF** (the shape rounding the
corner), a **2-D MSTD set / the Patterson-autocorrelation (crystallography, A−A
is always centrosymmetric by Friedel)** angle, and using a different **structured
enumeration** for a diagonal piece (Sturmian/Stern–Brocot rows — but compute bits
with INTEGER arithmetic, NOT float doubling, which dies after ~52 bits). Still
open from before: singular moduli mod p, Gaussian primes (chart), Temperley–Lieb
state-sum, Rule-110/other CA, indefinite topographs with RIVERS, near-integer
e^{π√163}, Stern–Brocot mediant tree, Montgomery/zeta-vs-GUE, Greene–Lobb
inscribed rectangles, six-vertex/square-ice arctic curve, quandle knot colourings.

Note (2026-07-01 follow-up, same `4zx43y`, after "too plain/mechanical" feedback):
now USED — **optical CAUSTICS** (gather millions of refracted rays; brightness =
caustic density), **de Jong STRANGE ATTRACTOR** (brightness = invariant measure),
**BRANCHED FLOW** (parallel rays through weak random potential). These are the
new *painterly* register — density-field pieces where "brightness IS a measure."
Cousins still open in this luminous vein (good next-run seeds, likely to please):
**Lichtenberg / dielectric-breakdown lightning** (branched *filaments*, different
grammar — needs iterated Laplace solves), **DLA coral**, **Pearcey/Airy CUSP
diffraction catastrophe** (the WAVE-optics dressing of the cusp — colour by phase;
computable fast via per-column FFT of exp(i(t⁴+X t²))), **caustics of a single
water droplet / lens (the rainbow/Airy caustic)**, a **flow-field via LIC** (brushed
directional light), other **strange attractors** (Clifford/Thomas/Aizawa, incl. 3-D
volumetric), and **KAKEYA/Besicovitch** rendered as a luminous fan of needles.
The old flat-fill/diagram register (`art_4zx4/`) is deprecated for hero use.

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
- **Woven strands/knots: get the over/under from a DEPTH SORT, never from solving
  crossings.** Sample every strand as 3-D points (on a torus, a braid embedding,
  whatever), rotate+project to screen with a depth value, sort ALL points by depth
  and paint far→near with soft-alpha disk splats. The entire weave/occlusion — the
  thing a knot invariant "remembers" — emerges for free; painter's algorithm IS the
  Reidemeister bookkeeping. Two gotchas: (1) the GLOW buffer must use `np.maximum`,
  not `+=`, or the dense overlapping splats of a single fat tube pile up to white;
  (2) splat spacing must stay ≪ tube radius at the final res (scale sample count by
  W) or the tube beads. ~38k splats at 8192² ≈ 9 min, peak ~8.5 GB.
- **A flat tube becomes glossy glass via an OFF-CENTRE specular across its
  cross-section.** Per splat, project the pixel onto the tube's screen-space
  PERPENDICULAR (u∈[−1,1] across the rod; tangent = `np.gradient` of the per-strand
  screen path, computed BEFORE the global depth sort and carried per point). Body =
  a cos term darkened on the side away from the light; specular = a bright line at
  `u≈±0.42·sign(lightside)·√(1−u²)`. Same lesson as the Apollonian note ("a domed
  look needs a per-pixel radial gradient, not stacked ellipses") but for a 1-D
  cross-section — cheap and transforms matte rods into candy-glass.
- **Multi-component torus link: components = gcd(p,q), each a T(p/g,q/g); SPREAD the
  palette across the wheel (`PALETTE[c·(len//g)]`).** Indexing colour by raw
  component id clustered g=3,4 into adjacent all-warm hues (looked monochrome). Open
  knots stay traceable (T(12,8)=4 trefoils, T(20,12)=4×T(5,3) read as "anyons you
  can't comb apart"); very dense ones (T(20,8)) read as one woven mass — pick by how
  much you want to follow individual strands. **Density-matched bloom, re-confirmed
  hard:** the first weave blew to pure white; the fix was bloom amps cut ~3×
  (0.42→0.15), `k` 1.45→1.05, AND a +1.28 saturation boost so strands stay jewel-toned.
- **Cut-away interior (Bing's house, any dollhouse): frontal + slightly-elevated
  camera + a z-clip beats a 3⁄4 angle.** A side camera lets the near wall occlude
  the interior; intersect the SDF with `z ≤ z_clip` to remove the front wall and
  look nearly straight in. A tube viewed face-on always shows a flat wall — so
  depth-separate the two chimneys in z, give each its own warm/cool material, and
  bias the camera to reveal at least one OPEN END (the amber tube opening up into
  the upper room is what makes it read as a tube, not a panel). Dim the enclosing
  shell (low material + low key) so the coloured interior is the subject.
- **Build a 2-complex from thin-slab box-SDFs and punch openings with `max(d,−hole)`.**
  Bing's house = 5 outer walls (front omitted = the cut-away) + a middle floor +
  two open square tubes (4 thin slabs each, no caps) + two connecting fins; holes in
  the top/bottom/middle walls let each chimney pierce through. Material per primitive
  via `argmin` over the distance stack. Vectorise the sphere-trace over all rays on a
  SHRINKING active set (drop converged/escaped indices each step) — ~160 steps with a
  0.92 step factor so thin walls aren't overshot. Heavier than splat renderers
  (~9 min @4096-internal).
- **When a complex function has MONODROMY, render its single-valued cousin as a real
  scalar field, not a domain-colouring.** Naive `|Li₂|` domain colour is seamful;
  the **Bloch–Wigner** combination `D(z)=Im Li₂(z)+arg(1−z)log|z|` is single-valued
  and real, so it draws as a clean glowing contour landscape with no branch cuts to
  hide. (General move: modulus of a modular form, Bloch–Wigner, etc.) Compute complex
  `Li₂` by reducing `|z|>1` (inversion) and `Re z>½` (reflection) to a fast series with
  the principal-log corrections, and **VERIFY the functional equations**
  (`D(z)=−D(1/z)=−D(1−z)`, `D(i)=Catalan`) before trusting the picture — same
  check-the-invariant discipline as von Dyck / Golay.
- **Iso-contour width bug worth remembering: `np.gradient` is PER-PIXEL.** A
  constant-screen-width contour is `line_dist_px = |D mod Δ|·Δ / |∇D_perpixel|`, then
  `exp(−(line_dist_px/width)²)`, width≈`0.9·supersample`. My first dilog had INVISIBLE
  contours because I converted to pixels and then divided by the world cell size again
  (double unit conversion). Spacing contours equally in the quantity that diverges (here
  volume, → the gradient blows up at the cusps) crowds them infinitely near the
  singularity = free multi-scale detail (same family as "singularities are free detail").
- **A CA / difference-pattern piece reads BEST at ~2048², not 4096² — the grain IS
  the concept and must stay ~1px at viewing size.** Rule 30's XOR light-cone is
  gorgeous at 1024–2048² (you see the fractal grain), but at 4096² the cells are so
  fine that any whole-image view downscales them to FLAT colour blocks — the
  irreducibility you're trying to show averages away. Render high-entropy fields at
  the resolution where one cell ≈ one screen pixel. Bonus: noise barely compresses,
  so a 4096² CA PNG balloons (>32 MB — it blew past the image-attachment limit and
  couldn't be viewed); 2048² is both the right scale and a sane file size. (Mirror
  of the percolation note "the grain CAN be the concept" — but only at the matching
  resolution.)
- **For a wrap-free CA light cone, simulate WIDER than you crop.** `np.roll` is
  periodic; a perturbation cone reaching the array edge wraps around and fills the
  frame (looked like the whole image diverged). Fix: simulate `Wsim = 2*W + pad`,
  flip the bit at `Wsim//2`, crop the centre `W` columns. The cone (speed 1) then
  never reaches the boundary within `T=W` steps, giving the clean triangle. Rule 30's
  divergence front is genuinely asymmetric — one edge rides the light-speed limit
  (ruler-straight), the other is a fractal sub-light front — which is the whole point;
  don't "fix" the jagged edge.
- **Conway topograph as a radial trivalent tree (NON-disk, honours "prefer non-disk"):**
  faces = primitive vectors ±(p,q), value `Q(p,q)`; grow the dual tree from the form's
  well — a central vertex with 3 faces `(1,0),(0,1),(1,1)` and three edges at 120°,
  each vertex sprouting two children at the FORWARD direction ±60° (the three edges at
  any vertex are 120° apart, so children leave at `ang±60`), lengths `*=0.62` per gen so
  it fills a disc as a self-similar canopy. New face beyond an edge = `Fa±Fb` (the apex
  NOT already present), value by the **parallelogram law** `Q(u+v)+Q(u−v)=2Q(u)+2Q(v)`.
  Colour edges by `min(face value)` on a log warm→cool ramp → a luminous well cooling to
  the fractal rim. Place the small integer VALUES as text AFTER bloom+downscale (crisp),
  only for faces with value below a cap and inside the frame. Definite forms (D<0) give
  symmetric wells; indefinite (D>0) would give rivers — a good future variant.
- **Verify a class-group identity by composition, not by faith (Bhargava/Gauss).** To
  draw "three forms compose to the identity," IMPLEMENT Dirichlet composition and CHECK
  it: reduce each form (definite reduction `-a<b<=a<=c`, with a hard iteration cap — my
  first reduce_def infinite-looped and hung the whole search; ALWAYS cap while-True loops
  in number-theory code), compose via "represent one form with leading coeff coprime to
  the other's (complete (x,y) to an SL₂ basis), then CRT the middle coefficient." Test on
  a KNOWN group first (D=−23 is C₃: `g·g·g = 1`) before trusting it on the cube. Then
  search small cubes for one whose three forms are primitive, share a discriminant, are
  DISTINCT, and compose to 1 — D=−23 cube `(-1,-1,-1,2,0,1,2,2)` gives the whole C₃ group,
  the cleanest possible example. (Same "check the invariant" discipline as von Dyck/Golay.)
- **A "promoted backup idea" is a cheap, high-value follow-up when the user loves a set.**
  Both `04` and `05` came from the *six-idea brainstorm* I listed but didn't build; the
  user picked two from that list. Lesson: always list the also-rans (the 6 ideas, the
  unbuilt sketches) explicitly in the reply AND in memory — they're the warm-start for
  the next request, and the user reads them.
- **A degenerate INITIAL CONDITION turns an abstract field into a story with a focal
  point.** Dyson BM started from the stationary GUE just looked like pretty parallel
  "Joy Division" waves; starting from **H=0 (all eigenvalues coincident)** makes them
  **fan out of a single luminous origin** — instant narrative (emergence + a bright
  focal point) and it literally embodies the concept ("the only place they meet is the
  beginning"). General move: ask what the *initial/boundary* condition could be that
  makes the process visibly BEGIN somewhere.
- **Brownian threads are Hölder-½ (inherently jagged at every scale); SMOOTH each path
  along time, don't fight the simulation.** `gaussian_filter1d` over each eigenvalue
  thread (≈6 steps) gives elegant traceable ribbons while the macro repulsion / non-
  crossing / semicircle envelope survive untouched. Also: **fewer threads read better**
  — N≈36 eigenvalues are individually followable (you SEE them bend away from each other
  and never cross); N≈120 collapses to TV static. The Wigner-semicircle envelope (sparse
  edges, dense middle) appears for free from the spacing.
- **When a structure is intrinsically SPARSE + MONOCHROME, draw its DUAL/complement in a
  second colour to fill the frame and add a palette.** Ford circles alone have huge
  dynamic range (radius `1/(2q²)`) → any view is a few big gold rings + empty interiors,
  reads monochrome. Overlaying the **Farey geodesic tessellation** (the arches the
  tangencies cut, in COOL blue) fills the whole upper half-plane and gives warm/cool
  two-colour richness — the circles and the arches are duals of the same modular object.
  Lesson: don't brute-force a sparse field brighter; add the complementary structure.
- **For "emergent geometry from adjacency" the SAMPLING must be near-uniform (blue-noise
  / Fibonacci), not uniform-random.** Random (Poisson) points on a manifold clump and
  leave voids → the kNN graph has **long bridging edges** that, after Laplacian eigenmap,
  read as **radial spikes** and a lumpy recovered shape (radius CV 0.08, edge p99/median
  ~3×). A **Fibonacci-sphere + tiny jitter** sampling gives a regular graph → clean round
  recovery (CV 0.04, p99/median ~1.7×). Diagnose by edge-length percentiles & recovered-
  radius CV before rendering. Also: the **sphere** is the honest clean demo (its 3 lowest
  non-trivial Laplacian eigenvectors ARE the linear coordinates → raw 3-eigvec embedding
  is a sphere, no reconstruction hacks); a **torus** needs 4 eigvecs + angle extraction
  (the minor angle only shows up at eigvecs 5,6, corr ~0.7) so it's messier — pick the
  manifold whose spectrum embeds cleanly in the dimension you're drawing.
- **Anti-aliased line art from numpy: BILINEAR (sub-pixel 4-neighbour) splatting.**
  Point-splatting edge samples to integer pixels gives a dotted, crawly mesh; distributing
  each sample to its 4 surrounding pixels by fractional `(1−fx,fx)×(1−fy,fy)` weights gives
  clean glowing threads. Sample count per edge must scale with its pixel length (use a
  percentile of segment lengths) so lines stay continuous at any resolution. For a 3-D
  wireframe to read as a SOLID, **back-dim** edges/nodes by `(depth^1.6)` (far side fades)
  — cheap depth cue, no z-buffer needed. (Reusable kit: `fib_sphere`, `knn_graph`,
  `embed` (normalized-Laplacian eigsh), `bilin_add`, depth-cued additive render in
  `art_kvrz/03_*.py`.)
- **Gaussian-ring distance-field is the resolution-independent way to draw a circle/arc.**
  For both Ford circles and Farey arches: `exp(−((dist_to_centre − r)/w)²)` over a bbox,
  capping `w` at ~2px so even huge circles are hairline rings (NOT `w∝r`, which fattens
  big circles into washes that bury the colour). Mask an arch to the upper half-plane by
  clipping the bbox at the axis row. Scales perfectly to any S (no per-pixel angle loop).

- **A discrete process plotted as POINTS reads as stipple; plot it as continuous bent
  THREADS to get an image.** My first Collatz attempt plotted each trajectory's `(steps-
  remaining, log2 value)` vertices and bilinear-splatted them → a dead dot-grid (the nodes
  are quantised; no lines connect them). The fix that made it sing: the **botanical bend-
  tree** — walk each REVERSED trajectory (root=1 outward) as a fixed-step polyline that
  turns a little per element (parity → left/right), additively splat the whole polyline.
  Now overlap=brightness, the shared tail blazes, and the thing becomes organic. Lesson:
  for "many trajectories of an iterated map," draw flowing curves, not scatter points.
- **For a bend-encoded fractal tree, the two TURN ANGLES are the entire composition — sweep
  them, don't reason.** Collatz feather: even-bend `ae`, odd-bend `ao`. The shape is wildly
  sensitive: equal-ish small angles **curl every trajectory into closed rings** (a tangled
  ball); ratio `ae/ao≈0.5` **hooks it into a scythe**; ratio `≈0.6–0.65` (e.g. 0.070/0.110)
  **stands it up as an upright plume/feather**. The net drift per trajectory ≈ `E·ae−O·ao`
  (E,O = #even,#odd steps); ≈0 spreads it, >0 curls it. You cannot eyeball this — render a
  6-tile contact sheet at N=20k/520px and PICK. (Same family as the Penrose-N and
  bloom-density dials: a parameter that *sounds* like detail is actually legibility.)
- **A one-sided / curved point-cloud won't centre by bbox — frame it by PCA on the BRIGHT
  pixels.** The feather's long faint outlier filaments (large-n trajectories travel far)
  dominate the bounding box and flatten/lean the composition. Fix: rasterise once at the
  natural orientation, compute the **brightness-weighted covariance** of `log1p(acc)`, take
  the **major eigenvector → rotate geometry so it's vertical**, then translate to centre the
  **brightness-weighted centroid** (NOT the bbox centre; they differ a lot when faint wisps
  trail off one side). Re-bake the rotation+shift into the high-res build. Turned a
  lopsided comet into a centred quill.
- **Convergence-to-a-point IS the story and the focal glow — splat nothing extra, let
  overlap do it.** 150k Collatz threads literally share the origin (=1); additive
  accumulation makes that one pixel the brightest thing on the canvas for free, and a 2-σ
  bloom on the raw `acc` turns it into a blazing white-gold spine. The composition ("a
  fountain rising from one point / everything falling to one") and the brightness peak are
  the same fact. Ask of any iterated-map piece: *what single point do they all touch?* —
  put it where the eye lands.
- **Three-distance theorem reads best as POLAR growth-rings, not a flat sunflower or a
  Sturmian strip.** Prototyped all three: the **Vogel sunflower coloured by gap-class** is
  pretty but disk-shaped and "just a 3-colour sunflower"; the **unrolled `(x=nα mod1, y=n)`
  staircase** is rigorous but a garish busy comb. The winner: **radius=time n, angle=position
  on the circle**, each ring partitioned into ≤3 colours of gap-arc (per-pixel `searchsorted`
  into the sorted breakpoints). You get the **Fibonacci spiral arms** (gold=smallest gap) AND
  the **concentric phase-transition rings** (where a new gap length is born) in one image —
  the subdivision history and the circle the rotation lives on, unified. Fill the centre
  (small r0) so the first 1→2→3 subdivisions show; glow a seed dot at the origin.
- **"On a star-shaped curve, on-curve = `|p| = r(∠p)`" turns inscribed-figure hunting into
  cheap root-finding.** For the Toeplitz inscribed square: parametrise the Jordan curve as
  radial `r(θ)` (force star-shaped: `r>0` with bounded harmonics). A square from side A→B has
  its other two corners `C=B+i(B−A)`, `D=A+i(B−A)`; the **signed defects** `|C|−r(∠C)` and
  `|D|−r(∠D)` both vanish iff it's inscribed. Find candidates as **cells where both defect
  fields sign-change** on an (θ₁,θ₂) grid, polish with **2-D Newton (J by finite diff) to
  1e-10**, dedup by (centre,side). A curve hosts an odd number (generically); a 9-harmonic
  curve search over seeds gives 1/3/5/7 — pick a 7 for a rich nested web. Same "verify the
  invariant" discipline as von Dyck/Golay: the squares are real to float precision, not eyeballed.
- **Splat the CONTACT POINTS (pegs) to make a containment theorem glow.** The inscribed-
  square piece is *about* where the squares touch the loop; rendering those 28 vertices as
  bright Gaussian pegs (brighter than the square edges, which are brighter than the curve)
  gives the read hierarchy **loop > pegs > square-web** and makes the abstract "4 points on
  the curve" literal and luminous. (Cousin of the Q_p horizon-splat and the Eisenstein
  ash-nodes: find the set the piece is secretly about, and light exactly that.)
- **Line/web art at SS>1 loses thin-line brightness to the downscale — fatten + scale by SS.**
  A 1px additive line carries ~constant energy, but a 2× LANCZOS downscale halves its peak,
  so a render that looked great at SS=1/700px went to invisible threads + dominant pegs at
  SS=2/2048². Fix: **`gaussian_filter` the line buffers by ~0.7·SS** (fatten to survive) AND
  **multiply line energy by ~SS** before tone-mapping. Big Gaussian splats (pegs, blooms)
  are unaffected; only hairline strokes need this. (Restates "splat-count/brightness must
  track canvas size" for the downscale direction specifically.)

- **Simulate millions of tiny machines by VECTORISING ACROSS machines, not across time.**
  To measure algorithmic probability (Coding Theorem Method) you need to run *millions* of
  small Turing machines — hopeless one-at-a-time in Python. Instead keep the whole
  population as NumPy arrays and step them in **lockstep**: `tape[K,W]`, `head[K]`,
  `state[K]`, and per-machine transition tables `wr/mv/nx[K,n,2]`. One simulation step =
  a handful of fancy-index ops over length-K arrays: `sym=tape[arange(K),head]`,
  `w=wr[arange(K),state,sym]`, write, `head+=mv[...]`, `state=nx[...]`, mask halted
  (next-state==n) and escaped (head∉[0,W)). 12M (5,2) machines × 800 steps ran in ~16 min
  (~160s per 2M batch); a per-machine loop would be ~100× slower. This "data-parallel over
  independent instances" trick generalises to ANY swarm of small dynamical systems (CA
  rules, L-systems, ODE ensembles) — make the ensemble axis the NumPy axis.
- **Tally variable-length outputs with a packed integer key + `np.unique`, not a Python
  loop.** Each halted machine's output = tape over the visited cell-range (faithful: keeps
  internal/edge zeros); cap length at Lmax, gather an aligned `[M,Lmax]` window by
  `idx=lo[:,None]+arange(Lmax)`, zero positions past the true length, then encode each row
  as `key=(length<<32)|Σ bit·2^i` (int64) and `np.unique(keys,return_counts=True)`.
  Accumulate the counts into a `Counter` across batches/seeds. Vectorised, exact, mergeable.
- **Embed strings on the interval by their BINARY FRACTION `0.b₁b₂…` so prefixes align and
  simple strings cluster.** For any "distribution over bitstrings" picture, position string
  `s` at `x=Σ sᵢ2^{−i}∈[0,1)`. Then a string and its extensions stack at the same x (prefix
  tree → vertical alignment), and low-complexity strings land on simple dyadic/rational x →
  the image gets a **self-similar comb** with tall features at `1/2,1/4,3/4,1/3,…` and a
  near-mirror symmetry (bit-complement ≈ `x→1−x`, similar K). Avoids the "arithmetic points
  look like noise" trap because complexity now correlates with horizontal position.
- **For a heavy-tailed distribution, make HEIGHT = log(weight) = −K and you get a skyline,
  not a single spike.** Plotting m(x) linearly, one bar (the simplest string) dwarfs
  everything. Plotting `log m(x)` (= −K up to a constant) spreads the orders of magnitude
  into a readable city of towers: a few gold giants (simple) over a teal forest (complex).
  Label only the tallest ~10 (bitstring + K), AFTER the downscale, with a min-spacing guard
  so labels don't collide — same "text after bloom/resize stays crisp" rule as the diagram
  emblems. The labels are what make it read as *computation/complexity* rather than a music
  equalizer; without them the comb is ambiguous.
- **When "most are dull, a few are rich," SORT BY the richness and make the gradient the
  composition — don't hunt the rare jewel.** A garden of random small-TM space-times: the
  prize (nested/Sierpinski fractals) is genuinely RARE; random (5,2) machines in ≤300 steps
  are ~all solid triangles (monotone sweeps) or vertical stripes (periodic counters).
  Selecting by *direction-changes* picked maximally-bouncy SOLID wedges (boring). Selecting
  the gzip MID-band still clustered on near-identical stripes. What worked: compute a
  complexity score per machine (**gzip-density of the bit-packed space-time** = a cheap
  Kolmogorov proxy), **span the whole range and SORT by it** (drop only the near-empty
  bottom and the pure-noise top), so the tiles read trivial→complex as a deliberate
  gradient. The honest message ("a few bits of program, unbounded unknowable behaviour;
  most do almost nothing") becomes the layout instead of a failed search for the one
  beautiful machine. (Mirror of the Occam skyline: there too, the heavy-tailed truth IS the
  picture.)
- **The triangle is the DEFAULT, and the way to escape it is to gate on CONFINEMENT, not
  complexity.** "Why are all the TM space-times triangles?" — because a head moves ≤1
  cell/step, so the touched region is a discrete light-cone (a triangle) and the diagonal
  edge IS the head's worldline; a random tiny machine almost always just DRIFTS one way
  laying a periodic trail, filling that triangle solid or striped. gzip-complexity does NOT
  separate these out (a chaotically-writing drifter is still a triangle). The decisive
  filter is **`steps/width ≥ 3`** — the head must revisit each column several times, which
  only a non-drifting (bouncing/confined) machine does. That single gate kills every
  drift-triangle; rank the confined survivors by gzip-incompressibility to drop the
  period-2 twitchers. The confined ones are tapering **spires** (counters/sweepers) with a
  zigzag worldline — the machines that actually compute. (General: when a whole population
  shares a silhouette set by a CONSERVATION LAW (here: head speed ≤1 → causal cone), don't
  filter on texture — filter on the dynamical quantity that the interesting cases violate,
  here sub-linear width growth.)
- **Match the LAYOUT to the data's intrinsic aspect — don't cram tall-thin things into
  square tiles.** The confined TMs are intrinsically tall-and-narrow (width ~30, height
  ~700). Forced into square grid cells they become invisible 1-px slivers. Shown instead as
  a **colonnade of full-height vertical specimens** (each scaled to canvas height, packed
  side by side) they read as a forest of luminous obelisks and the internal zigzag/banding
  is legible. Inspect a few specimens at full size FIRST to learn the natural aspect, then
  design the layout around it. (Pairs with the earlier "render small, LOOK, then scale".)
- **For TM-spacetime tiles: simulate in a tape too WIDE to escape, fixed window, NEAREST
  upscale.** Bounded tape → only short halters survive (the long busy-beavers roam off and
  are discarded) → boring. Instead set `W=2T+pad` so no head can escape in `T` steps, run a
  fixed `T` (don't require halting), and show the visited-column crop. Record the head
  worldline (a gold thread) — it's what reads the tile as a *machine*, not a CA. Tiles are
  tall (time≫width); letterbox each into a square cell on the dark field (varying aspect =
  informative). NEAREST upscale keeps cells crisp.
- **Lambda diagrams (Tromp) are very renderable and a perfect BLC visual — but VERIFY the
  engine and the layout on I/K/S first.** A λ-term draws as: abstraction = horizontal BAR,
  variable = vertical line up to its binding bar, application = horizontal LINK joining the
  two spines. Clean recursion: `Lam` adds a bar at the top and pushes the body down, capping
  open variables whose de-Bruijn "levels-to-rise" hits 0 (others pass through, decremented);
  `App` places f|a side by side and links their leftmost spines at the bottom. Build a
  verified `blc.py` first (de Bruijn `Var i→1ⁱ⁺¹0`, `Lam→00·`, `App→01··`; encode/decode
  round-trip; normal-order β with shift/subst — TEST `plus 2 1⇒3`, and that `enc(S)` is the
  canonical `00000001011110100111010`), THEN the layout, and eyeball that I (one bar+hang),
  K (two bars, var from the top one), S, and the Church numerals match the canonical
  pictures. Same check-the-invariant discipline as von Dyck/Golay. Sorting the gallery by
  `|enc(term)|` makes "longer program = smaller 2⁻ᵖ prior" the visible axis.
- **A "promoted backup idea" keeps paying off — and the also-rans list IS the warm-start.**
  Third run in a row where the user picked an idea from the explicitly-listed six-idea
  brainstorm (here #4, Solomonoff). Always enumerate the also-rans in the reply AND in this
  memory; they are the cheapest high-value next request. (This run's still-unbuilt backups:
  Cantor diagonalization, near-integer coincidences — carried forward above.)

- **Vectorise ROOTS of millions of polynomials by stacking companion matrices.** To
  draw the Littlewood-roots fractal you need every root of every ±1-coeff polynomial —
  hopeless one np.roots-call at a time. Instead build each chunk's companion matrices
  as ONE real `(chunk, d, d)` array and call `np.linalg.eigvals` on the STACK (LAPACK
  loops the eigensolve in C). d=24, 2²⁴≈16.8M polys ≈ 30 min; chunk ~65k to bound RAM,
  a REAL float64 companion halves memory vs complex. Splat roots with **bilinear**
  (4-neighbour) weights for anti-aliasing. (Same "make the ensemble axis the NumPy axis"
  trick as the lockstep-TM swarm.)
- **For a field with HUGE density dynamic range, HISTOGRAM-EQUALISE the log-density.**
  Littlewood roots crowd the unit circle ~100× over the faint dragon filigree; plain
  log+filmic clips the bulk to flat white and buries the lacework. Rank-transform the
  nonzero `log1p(acc)` to [0,1] (argsort→ranks/N) → the filigree, the bright ridge AND
  the halo-ringed voids all read at once. The single most important tone-map move when
  one region dominates. (Cousin of "per-element normalization rescues balance".)
- **The apophatic move: the SUBJECT can be where points CANNOT go.** Littlewood roots
  avoid neighbourhoods of the roots of unity → black HOLES (with bright pile-up halos
  where roots crowd against the forbidden zone) ARE the composition. Light the absence.
  (Family: Eisenstein ash-nodes, the Q_p horizon splat, the dilog zero-river — find the
  set the piece is secretly about, here the *forbidden* set, and make it the read.)
- **Conjugate/real-axis SEAM in a complex-plane splat:** real roots all land on the
  exact Im=0 pixel row → a bright scan-line. Fix at source (splat the conjugate copy
  only where |Im|>ε so real roots are counted once) AND/OR in tone (replace the centre
  1–2 rows with the average of rows ±2). Generic for any field with a reflection axis.
- **Domino shuffling (Aztec diamond / arctic circle) — get the fill ORDER right.**
  Convention (pywonderland): n/s = HORIZONTAL dominoes sliding up/down, e/w = VERTICAL
  sliding right/left; delete bad blocks (n,n,s,s)/(e,w,e,w), slide, fill empty 2×2
  blocks by a fair coin (s,s,n,n)/(w,e,w,e). **KEY BUG that cost the most time:** after
  each slide the empty cells form disjoint 2×2 blocks but **NOT all on one (px,py)
  sublattice coset** (fixing only the *sum* parity still lets same-parity blocks overlap
  diagonally), so a simultaneous/parity-masked vectorised fill CORRUPTS the tiling. The
  reference fills greedily boundary-first for exactly this reason. Fix: vectorised
  candidate-find (`np.where(empty & in_diamond)`) + a short python loop over candidates
  in (row,col) scan order with an **O(1) recheck** (skip if the 4 cells are no longer
  empty) — replicates the reference, stays fast (N=1024 ≈ 3.5 min). Same for delete.
- **VERIFY a combinatorial sampler by its invariants, not by eye** (von-Dyck discipline):
  a *perfect* tiling at every order (each in-diamond cell covered exactly once by a
  paired domino, nothing outside) + the **arctic circle at radius N/√2** + **pure-colour
  frozen corners** are three independent checks that the shuffle is correct AND uniform.
  Don't trust "0 empty cells" alone — that misses overlapping/inconsistent dominoes;
  reconstruct the actual domino pairs and check coverage==1.
- **Colour a tiling by local TYPE to expose a phase transition.** 4 domino orientations
  → 4 colours: solid single-colour region = frozen/ordered (the corners), multi-colour
  static = free/disordered (the temperate disc). The pure-corner-vs-muddy-centre contrast
  IS the order/disorder story; keep 1 cell = 1 px (the grain is the disorder, like the
  critical-percolation note). The arctic boundary at 1:1 is a fluctuating KPZ-scale front,
  not a clean circle — that's honest and beautiful, don't smooth it.
- **Arnold tongues: rotation number as a field; lockedness = small |∇W|.** Iterate the
  LIFTED (un-modded) sine circle map ~6000× (≥1000 transient; high-q tongues lock slowly
  so need many iters), W=(x_N−x_0)/N, vectorised over the whole (Ω,K) plane. Mode-locked
  tongues are flat plateaus → a SHARP gate on `exp(−(|∇W|·S/0.3)^1.3)` makes even thin
  high-q tongues glow against a dark "free" quasiperiodic sea.
- **A parameter-plane dominated by a few huge features → CENTERED-BRIGHTNESS palette.**
  The Arnold plane is swamped by the 0/1, 1/2, 1/1 tongues. Make the palette DARK at the
  dominating ends (W=0,1 → navy, recede into the void) and BRIGHT at the feature you want
  as the heart (W=1/2 → gold) so the subtle Stern–Brocot/Farey cascade becomes the
  subject. Frame K∈[0,1.3]: the wedges hang from the rationals, widen to criticality
  K=1, then fray into chaos above → the order visibly dissolving. (The Ω↔1−Ω symmetry
  makes [0,0.5] a lossless half, but the full symmetric fan composes better; the narrow
  K-band [0.5,1.03] turns the wedges into a flat barcode — keep the full K range so they
  read as WEDGES emerging from points.) Family: "histogram-equalise / per-element
  normalize when dynamic range is huge" + "symmetry is the enemy → differentiate".

- **Lyapunov / any two-regime field: make the palette show structure in BOTH regimes, and glow the boundary, not the bulk.** The Markus–Lyapunov fractal's beauty (the "Zircon City" filigree) lives in a thin band of **small-positive λ just inside the chaotic region** — order barely losing. A naive 2-colour map (gold stable / flat blue chaos) reads as a poster; the fix was: stable→an amber→gold→cream depth ramp by `−λ`; deep chaos→recede to near-black navy (`exp(−λ·k)`); and a SEPARATE sharp coastline glow `exp(−(λ/0.085)²)` that lights ONLY the near-boundary chaos cyan-white. Same family as "singularities are free detail" and "histogram-equalise huge dynamic range": find the sub-region that carries the story and give it its own tone channel. Lyapunov boundaries alias badly (fine fringe) → SSAA×2 is essential, exactly like the Talbot-carpet note.
- **Sample a uniform dimer/lozenge tiling (or any monotone height surface) by VECTORISED CHECKERBOARD Glauber.** A boxed plane partition is a monotone array `h[i,j]∈[0,c]` (weakly decreasing both ways); the validity of a ±1 flip at (i,j) depends only on its 4 neighbours, so all cells of one (i+j)-parity are mutually independent given the other parity → update a whole colour class in ONE numpy step (propose ±1, accept if it keeps monotonicity & bounds; symmetric proposal → uniform stationary law). Tens of thousands of sweeps in seconds; no per-site Python loop, no companion to CFTP needed for a visually-typical sample. (Same 'make the ensemble axis the numpy axis' trick as the lockstep-TM swarm and stacked-companion eigvals.) The 3 rhombus orientations = the 3 cube-face directions, drawn as filled parallelograms with a per-orientation colour + height shading → the isometric cube-heap reads as 3-D for free ('orientation→brightness gives faceting').
- **Verify Glauber mixing with a LOCAL observable that climbs from the init, not a CONSERVED global average.** The plane-partition volume fraction hits its equilibrium 0.5 after ~200 sweeps and stays there — it tells you NOTHING about whether the local texture (the arctic boundary, the fluctuations) has mixed from the smooth linear-ramp start. The honest diagnostic is the **density of flippable sites** (local min/max of the surface): it rises 0.41→0.51 and *plateaus* (here ~12k–30k sweeps at N=200, ~N² scaling), which is the real mixing time. General rule: to test a sampler, watch a quantity the init gets WRONG, not one it gets right by symmetry. The arctic-ellipse location (Cohn–Larsen–Propp inscribed ellipse) + the affine-invariant frozen fraction `1−π/(2√3)≈9.3%` are the independent correctness checks (von-Dyck discipline), cousins of last run's 'arctic circle at N/√2'.
- **A 'colouring'/sub-lattice formula must be the RIGHT one — check the invariant by Monte-Carlo.** The hexagonal 7-colouring for the chromatic-number-of-the-plane upper bound is `(q−2r) mod 7` (the **Eisenstein norm-7 sublattice**, min same-colour distance √7·s), NOT the textbook `(q+2r) mod 7` that merely makes neighbouring hexagons differ (map-colouring) — the latter puts same-colour points only ~1.7s apart and FAILS unit distance. Both look identical as a tiling; the difference is invisible to the eye. I caught it by sampling 200k random pairs at exactly unit distance and counting same-colour collisions: `(q+2r)` ~24k violations, `(q−2r)` exactly **0** for spacing s∈(0.671,0.866). Same lesson as von Dyck/Golay: a known invariant (here 'no unit-distance monochrome pair') is a cheap, decisive test — run it before drawing. (The Moser spindle's χ=4 is likewise verified by exhaustive backtracking — a 4-colouring exists, no 3-colouring — before it's drawn as 'the proof'.)
- **Triptych cohesion: deepen/desaturate the one outlier-bright panel; judge on a contact sheet, never in isolation.** The chromatic-plane panel was born candy-bright (a rainbow 7-colouring) and clashed with the moody gold Lyapunov + cube-heap pair. A small desaturate-14%-toward-luma + drop value to 0.74 + stronger vignette turned it into deep backlit-cathedral stained glass that sits with the set, while the white proof still pops. Build the 3-up contact sheet and look at the SET; a panel that's lovely alone can break the room.

- **Render a FUNCTION GRAPH (or any IFS attractor) by a vectorised chaos game; brightness then encodes the invariant MEASURE for free.** The Minkowski `?` graph is the attractor of two contraction maps `L(x,y)=(x/(1+x),y/2)`, `R(x,y)=(1/(2−x),(1+y)/2)` (derived from `?(x/(1+x))=?(x)/2` + central symmetry; VERIFY they land on the function to 1e-13 and that ?(1/φ)=2/3 etc. before trusting it). Run tens of thousands of chains in lockstep as numpy arrays (ensemble-as-axis), pick L/R per step by a random mask, and additive-**bilinear**-splat every post-burn point. The points trace the curve and pile up where the IFS invariant measure concentrates → brightness = the singular Stern–Brocot measure itself (histogram-equalise it, huge dynamic range). To give a lone curve BODY without clutter, draw the self-similar substrate behind it (nested Stern–Brocot boxes: each box holds an affine copy of the whole) — shows WHY it's self-similar. PERF: for splat accumulation `np.add.at(flat, idx, w)` BEATS `np.bincount(idx,w,minlength=W*W)` when W is large — bincount allocates+zeros a fresh W²-length array every call (134 MB at W=4096) and was ~10× slower; add.at is in-place. (bincount wins only when you batch all points into one call.)
- **Sample a Plancherel-random partition by RSK on a random permutation; get the SHAPE with bisect, no full tableau needed.** Row-insertion: for each value, `bisect_right` the row, append if it's the max else replace (bump) and carry the bumped value to the next row; the row lengths ARE the Young-diagram shape (Plancherel-distributed). O(n^{3/2})-ish, fine for n=10⁵ in pure Python. The Russian-convention boundary `φ(u)` (|φ'|=1) has down-steps exactly at contents `{λ_i − i}` — VERIFY by rescaling `(u,φ)/√n` and checking `max|φ−Ω|→0` on the BULK `|u|<1.8` (0.057→0.019→0.010 for n=2k→20k→100k; the corner region |u|≈2 keeps O(n^{-1/3}) Tracy–Widom edge fluctuations, so don't measure error there — it hides the convergence). `Ω(u)=(2/π)(u·arcsin(u/2)+√(4−u²))`, |u|≤2 else |u|.
- **To SHOW a limit-shape / law-of-large-numbers theorem, render several sample sizes converging onto the smooth law — the small-n JAGGEDNESS is the subject.** One big sample alone hugs the limit so tightly the randomness is invisible (n=2·10⁵ ?graph or Young diagram looks deterministic). Overlay the jagged boundaries of several *smaller* n (visibly rough, fluctuating around the curve) plus the bold smooth limit (Ω) → the eye reads 'random & different every time → one fixed shape'. Rescaled profiles all enclose the SAME area, so they don't nest — they wiggle around the limit with amplitude shrinking in n. (Make the discrete object legible too: draw the actual diamond CELLS coloured by content so it reads as a Young diagram, not just a curve.) Cousin of the arctic-circle/ellipse 'the grain is the disorder' note.

- **Rescue a 'mechanical'-looking plot by making it ATMOSPHERIC, and derive any fill-boundary from the EXACT function, not from the splat.** The first Minkowski `?` piece read as a neon curve on graph-paper; the painterly version that landed: a vertical dawn/dusk gradient + a heavily-blurred `?`-warped 'nebula' veil so the field isn't flat black, the chaos-game measure as a warm rose→gold glowing RIDGELINE with multi-scale bloom, and a valley lit BELOW the curve. KEY BUG: I first built the 'below the curve' mask from the topmost-nonzero pixel per column of the sparse chaos-game splat → at steep risers some columns had gaps → ugly dark 'stalactites'. Fix: the curve is an exact known function, so compute the profile analytically (`row = (1−?(x))·H`) — gap-free. General: when you know the curve in closed form, never reverse-engineer it from a noisy raster.
- **A permutation cycle/chord diagram only shows structure if you GROUP each cycle into a contiguous arc.** Plotting chords `i→σ(i)` with `i` in natural order for a random σ gives a structureless uniform haze (random chords). Re-order the circle so each cycle's elements are contiguous (cycles sorted by size) → each cycle becomes its own woven lens, and the ARC LENGTHS directly display the Poisson–Dirichlet cycle-length partition (the giant Golomb–Dickman cycle as a huge bundle). Colour by cycle; sort within each arc by value for varied internal chords.
- **Glowing 3-D wireframe (Cayley graph / polytope): normalise EDGES by a percentile, THEN add vertices; and scale samples-per-edge to pixel length.** Adding bright vertex blobs before a `max`-normalise crushes the edges to near-black (the vertices own the max). Order: splat edges → `acc/=percentile(99.5)` → clip → add vertex glows → bloom. And a fixed sample count per segment dots long edges — use `npts ∝ edge pixel length`. (Same 'splat-count must track size' family.) The permutohedron of S₄ falls out of placing perms at their own coordinates and projecting the sum=const hyperplane with a Helmert orthonormal basis; edges = adjacent transpositions, 3-coloured by generator.
- **Mallows / any q^{statistic} ensemble: sample EXACTLY via independent digits, and use a CONSTANT q (not 1−β/n) for a visible band.** Mallows `P(σ)∝q^{inv}` = independent Lehmer digits with `P(c_i=k)∝q^k` (geometric); inv=Σc_i. The diagonal-band limit shape has half-width ~`1/(1−q)`, so `q=1−3.5/n` (≈0.998) gives width ~n/3.5 = almost the whole matrix (looks uniform!). Use a constant like q=0.985 for a crisp band. The exact inversion COUNTS are the q-factorial `[n]_q!` coefficients (numpy convolution of blocks `ones(i)`), Gaussian in the limit (Mahonian CLT).
- **Know when NOT to ship: uniform random sorting networks need Edelman–Greene, not MCMC.** The gorgeous AHRV sine-curve sorting network requires a UNIFORM reduced word of w₀; the braid+commutation random walk is uniform-stationary but mixes far too slowly (n=30 still visibly 'combed' toward the canonical word after 30M moves — the letter-histogram stays skewed). Exact uniform = sample a uniform staircase-shape SYT (hook walk) then apply inverse Edelman–Greene. Rather than present a biased sample as uniform, I documented the gap and left it for a future run. Honest math first (the von-Dyck/Golay discipline applied to SAMPLING, not just structure).
- **`figkit.py` annotation-block kit travels well across galleries.** Accent bar + small TAG ('FIGURE 3 · RSK') + bold title + word-wrapped body, composed at final resolution with text drawn AFTER any downscale. Number figures in NARRATIVE order (and keep filename N == 'FIGURE N' — easy to desync when you reorder; re-render after editing the label, don't just sed the script).

- **The Edelman–Greene bijection, implemented and VERIFIED, unlocks exact uniform sorting networks (the AHRV sine curves).** Forward EG (reduced word of w₀ → SYT of staircase) is RSK-like with one twist: inserting x into a row, if the smallest entry `b>x` equals `x+1` AND `x` is already in the row, you bump `x+1` and leave the row UNCHANGED (this is what creates the repeated values in the insertion tableau P₀[i][j]=i+j+1); otherwise replace `b` by `x` and bump `b`. The INVERSE (reverse-bump a value `v` UP a row) — the rule I'd failed to get before — is: **SPECIAL iff `v` is already in the row** (forward special kept a copy of `v=x+1`) → recover `x=v-1`, row unchanged; else NORMAL → replace the largest entry `<v` with `v`, carry that entry up. VERIFY by exhaustive forward∘inverse round-trip on ALL reduced words of S₄ (16) and S₅ (768) — 0 mismatches — before trusting it (von-Dyck/Golay discipline). Then: uniform staircase SYT by the **GNW hook walk** (pick a uniform cell, random-walk within its hook to a corner, place the largest unused label, delete, repeat) → inverse-EG → a uniform reduced word in O(N·n). This is the RIGHT answer to 'the braid/commutation MCMC mixes too slowly' from the previous run.
- **To make AHRV sine curves visible, SMOOTH each trajectory hard and highlight a few wires over a dim mesh.** A uniform sorting network's wire path is a jagged ±1 staircase; the sine-curve LIMIT only reads after `gaussian_filter1d` along time with σ≈0.01–0.015·L. Draw all n wires as a dim rainbow woven mesh (colour by start slot), then overlay ~6 evenly-spaced wires bright/white at higher sample density — those read unmistakably as sine curves. (The uniform sample is statistically homogeneous — no 'comb' — which is itself the proof the sampler is right, vs the MCMC's persistent canonical-word bias.)
- **Sample uniform pattern-avoiders by the recursive class structure + exact big-int counts.** 231-avoiding (= stack-sortable) permutations decompose as σ = L·(max)·R where L is on the k SMALLEST values and R on the rest (231-avoidance forces all-of-L < all-of-R), both avoiders → choose the split `k` with probability `C_k·C_{n-1-k}/C_n`. Python big ints make the exact Catalan ratios trivial (no overflow); do it iteratively with a task stack to avoid deep recursion. VERIFY by brute-counting Av(231) for small n == Catalan, and that the sampler only emits avoiders + roughly uniformly. The n→large matrix shows the permuton limit shape (231: a Brownian-wandering diagonal) — a clean 'structure vs white-noise' contrast against the uniform/Mallows-q=1 matrix. (Big-int Catalan for n=3000 is slow, ~2 min — fine for a one-off; drop n if iterating.)

- **Viennot's shadow-line construction of RSK — implemented & verified, a third route into RSK (after row-insertion and growth diagrams).** Plot (i,σ(i)); the construction: repeatedly peel the **SW-Pareto-minimal** points (no other point both-smaller) as a 'shadow line' (these form a decreasing run, sorted by x → y descending); the **first row of P = the min-y of each line**; the new point set for the next rows = the lines' **NE inner corners** `(x_{next}, y_{cur})` between consecutive points. #lines at the top level = LIS (Schensted). VERIFY by `viennot_P == rsk_P` exhaustively on S₁..S₇ before drawing (it was 0/5913). Renders beautifully as nested rainbow L-staircases (the 'light from the lower-left' picture).
- **Lindström–Gessel–Viennot: verify the determinant==count on a tiny case, then draw the paths.** The lemma (non-intersecting path families count = det of single-path-count matrix) is a one-line brute-force check at n=3 (det 10 == enumerated families). To DRAW a uniform non-intersecting family (vicious walkers: n ±1 paths, strictly ordered at every column, endpoints fixed), use **corner-flip heat-bath Glauber**: at an interior local extremum `x[k,t-1]==x[k,t+1]=v`, set `x[k,t]` uniformly among `{v-1,v+1}` that stay strictly between the neighbours `x[k±1,t]` — symmetric → uniform. Assert ±1 steps + strict ordering + fixed endpoints after mixing. It's the same height-function / corner-flip dynamics as the lozenge tilings (non-intersecting paths ARE the de Bruijn lines of a tiling) — a clean way to UNIFY a gallery with the main set.
- **Drawing a graded poset (Bruhat/Hasse): rank = the grading on y, barycentric sweeps for x, and colour edges by a meaningful attribute.** Strong Bruhat cover on Sₙ = a single transposition of two VALUES (any two positions) that raises inversions by exactly 1 (the '+1' makes it a cover). Lay out by rank (=inversions), then iterate `x ← mean(neighbour x)` + re-spread-evenly per rank to cut crossings. Colour adjacent-transposition edges (the weak order / permutohedron) differently from the long-range strong-order edges — instantly shows weak ⊂ strong. Verify rank sizes = the Mahonian numbers (1,3,5,6,5,3,1 for S₄). Label nodes with one-line notation on small dark plates so text survives the glow.

- **Lift the sorting-network sine curves to an honest sphere of great circles.** A sine `h(t)=a cos t+b sin t` is exactly the projection of the great circle `cos t·u+sin t·v` onto ẑ when `u·ẑ=a, v·ẑ=b`. Given a fitted (a,b) per wire, build the orthonormal pair in closed form: `u=(s cosα, s sinα, a)` with `s=√(1−a²)`; for v solve `v·ẑ=b, v·u=0, |v|=1` → `(vx,vy)=P·ŵ+perp·ŵ⊥` with `P=−ab/s`, `perp=√((1−a²−b²)/(1−a²))` (real iff a²+b²≤1; clamp). Spread the azimuths α_i for a woven 'armillary' sphere. VERIFY the lifts are genuine great circles (|C|=1 and C·(u×v)=0 to 1e-16) and report the sine-fit R² (median ~0.99 on smoothed trajectories) — that R² IS the AHRV theorem made measurable. A beautiful capstone: the random object is the shadow of a perfectly classical one.
- **DEBUG NOTE — a separable Gaussian blur smears ONE bad/over-bright pixel into a full CROSS, not a blob.** The type-B render kept showing 2 vertical + 1 horizontal full-frame white lines. Edges-only and vertices-only were clean; the lines appeared only AFTER the additive bloom and TRACKED the camera rotation. Cause: a tiny cluster of maximally-bright overlapping edges/vertex at one (row,col); the separable `gaussian_filter` convolves along rows THEN columns, so an over-unity spike bleeds across its entire row and column → a bright cross that clipping turns white. Tells: the artifact is axis-aligned, full-frame, and crosses at a point. Fixes that worked: drop to crisp **PIL `ImageDraw` line/ellipse drawing at 2× supersample, depth-sorted (far→near)** with only a gentle single blur — no unbounded accumulation. (Cheaper partial fixes: normalize by a higher percentile, lower bloom gain, or `np.maximum` instead of `+=`; but for clean polytope wireframes PIL drawing is the robust default — same lesson as the glow-buffer-`maximum` note for dense splats.)
- **Fomin growth diagrams = the cleanest code-route to RSK (no insertion/bumping).** Mark the permutation as crosses; grow corner-partitions by a 4-case LOCAL rule on (μ=SW, λ=W, ρ=S, cross?): equal+no-cross→μ; one side grew→that side; both grew differently→componentwise-max union; both grew in the same row k→add a box in row k+1; cross (only when all equal)→add a box in row 0. Top-right corner = RSK shape (VERIFY == row-insertion on S₁..S₇). Renders as a lattice of small Young diagrams swelling ∅→full toward the NE — a lovely 'third face of RSK' beside insertion and Viennot's shadows.

- **Murnaghan–Nakayama on the abacus = a clean, cached character-table engine.** Represent a partition λ by its β-set (first-column hook lengths) `β_i=λ_i+(m−1−i)` with m=n beads. χ^λ(α): peel the largest cycle-part k by moving each bead from position bp to bp−k when that slot is empty; the rim-hook's height = #beads strictly between bp−k and bp, contributing sign (−1)^height; recurse on α minus that part. `lru_cache` on (β-tuple, α-tuple). VERIFY the table two independent ways before drawing: dims χ^λ(1ⁿ)==hook-length f^λ, and row orthogonality Σ_μ (n!/z_μ) χ^λ(μ)χ^ν(μ)=n!·δ (z_μ=∏ i^{m_i} m_i!). Render as a signed-log diverging heatmap (sign·log1p|χ|) so the huge dimension column and the tiny ±1s both read. n=14 → a 135×135 jewel.
- **A whole family of Sₙ structures renders beautifully as 'tiny-Young-diagram' node/grid art.** Young's lattice (partitions, edge=add-box, fan from ∅, #paths=f^λ verified by the same DP as the hook formula), Fomin growth diagrams, and the character-table axes all key off partitions; drawing each node/cell as a small filled Young diagram (box size = cell/max(part,#rows)) tinted by an invariant (f^λ, |λ|) makes the abstract poset legible and gorgeous. Differential-poset identity DU−UD=I ⇒ Σ(f^λ)²=n!, the same thing RSK proves bijectively — a nice through-line to cite across figures.
- **Verify a bijection/algorithm against its theorem BEFORE drawing — it makes the caption honest and catches bugs.** This volume: jeu-de-taquin rectification == RSK-P of the reading word (0/400 random skew tableaux) and slide-order independent; Foata's compartment cyclic-shift transform `inv(foata(σ))==maj(σ)` on all S₁..S₇ (and a bijection). Foata visual that worked: stack all n! permutations by statistic value and draw each σ as a thread from its maj-level to the inv-level of foata(σ) — since the map preserves the level, every thread runs HORIZONTAL and the shared band IS the Mahonian bell (equidistribution made into one picture). General: when a result says 'two statistics are equidistributed via an explicit bijection', draw the bijection as a level-preserving flow.

- **DON'T hard-code the answer to an extremal problem — OPTIMISE for it, and let the shape EMERGE (moving sofa).** Gerver's sofa is a horror to transcribe (18 analytic pieces, transcendental constants). Instead: define sofa = **∩ of the rotating width-1 L-corridor over θ∈[0,π/2]** on a grid, parametrise the corridor's INNER-CORNER PATH c(θ), and **coordinate-ascent the area**. Two passes (13→25 control points, 300²→520² grids) reach 2.172, within 2% of the proven optimum 2.2195, and the silhouette that FALLS OUT is unmistakably Gerver's telephone-handset (bite and all). The optimisation IS the verification (area is the objective). Exploit the arm-swap symmetry: sofa symmetric about the y-axis ⇒ free the path only on [0,π/4] and mirror `cx→−cx` (halves DOF, guarantees a symmetric sofa). Membership test: corner-frame `q=R(−θ)(p−c)+(1,1)`, then `p∈corridor ⇔ q∈L` with `L = {0≤v≤1,u≤1} ∪ {0≤u≤1,v≤1}`.
- **"The envelope renders the object" applied to a MOVING shape: splat every position of the boundary, and the caustic where they agree IS the answer's edge (sofa).** Splat the two corridor walls at every θ (bilinear line splat, additive). The INNER walls (rays from the pivoting corner) pile into a **bright caustic fan of cusps** that literally carves the sofa's bite — the corner-in-motion made luminous; the OUTER walls sweep a dim **dome**. Then draw the gold shape ON TOP and **strictly mask the caustic to OUTSIDE the shape** (the concave bite is outside, so it survives and glows). Two gotchas: (1) an intersection-over-DISCRETE-angles mask **scallops** at a cusp — needs many angles (nt≈1100 @4096) + a soft-alpha edge, not just more blur; (2) the outer-wall band leaves boxy rectangles below the shape — kill with a vertical fade (dome lives high) + an elliptic vignette toward the bite.
- **The razor-margin phenomenon (MSTD) is annotation-carried, not visually dramatic — pick a distinct GRAMMAR and let a specimen be beautiful.** |A+A|>|A−A| happens by margin 1 and in <0.05% of sets; a population scatter (|A+A|,|A−A|) collapses to a thin diagonal sliver (both sizes ≈ max for dense sets) — NOT worth rendering. What worked: one gorgeous **arc-loom** of the classic set (each pair {a,b} → semicircle, **apex=sum (a+b)/2, radius=difference (b−a)/2** — so apex-columns ARE the sums, radii ARE the differences; a faint mirror below makes a mandorla), plus a **gold sum-comb** and **rose difference-comb** to carry the exact 26-vs-25 count, and the caption states the rule. Keeping it as a THIRD grammar (arithmetic arcs) beside a filled shape and a binary field is what earned its place — diversify the lens, not the parameters.
- **AESTHETIC FEEDBACK (2026-07-01, important): a whole triptych was rejected as "too plain and mechanical."** The rejected pieces (`art_4zx4/`) leaned on FLAT FILLS (a solid gold sofa, a solid blue grid) and DIAGRAMMATIC elements (labelled combs, a literal binary table) on black — technically verified, conceptually clean, but they read as *figures*, not *art*. The fix that landed (`art_4zx4b/`): choose subjects that are **made of light and flow**, and render so that **brightness IS a density/measure — never a solid region**. Density fields (rays gathered on a floor, an attractor's invariant measure, ray-density through disorder) are intrinsically painterly: soft, multi-scale, glowing, with real negative space. Rule of thumb going forward: if a piece has a large area of ONE flat colour, or reads as a labelled diagram, it will feel mechanical — convert the subject to an accumulation/measure and let the light draw itself. (This restates the old "rescue a mechanical plot by making it ATMOSPHERIC" note but as a SUBJECT-CHOICE rule, not just a tone-map fix.)
- **"Gather" caustics: brightness = arrival density of a folded ray-map (optics / dynamics / disorder are the SAME picture).** For optical caustics: smooth random height h(x,y) (sum of ~11 wave octaves, mixed big+fine freqs), deflect each vertical ray by ∇h, land at (x,y)+s·∇h, bilinear-splat ~49M rays (chunk the surface rows to bound RAM at 4096²). Brightness diverges on the folds = the caustic net; cusps are the bright points. Keep DARK POOLS by subtracting ~0.32–0.35× the mean flux before the log (else it milks out to a uniform wash — the #1 failure mode). **Chromatic dispersion must be TINY** (per-channel refraction ×1.03/1.0/0.97); ×1.10 gave a broken-3D-glasses RGB-misregistration glitch, not a caustic rainbow. Same gather+subtract-baseline recipe makes **branched flow** (parallel ray sheet through a weak Gaussian-random potential V, ε≈0.014·, ℓ≈24; integrate d²r/dt²=−∇V; branches = focused filaments) and a **strange-attractor** silk (brightness = invariant measure of a de Jong map, ~3×10⁸ iterations as parallel orbits in lockstep). A luminance→palette RAMP (teal→gold→white for water; indigo→rose→gold→white for the attractor; blue→cyan→white for branches) + bloom on the brightest cores is what turns a grey density into painterly light; multiply the ramp by density^~0.6 so sparse regions fall to dark.
- **Diagonalization wants a STRUCTURED, EXACT enumeration or it's just a noisy checkerboard — the Walsh–Hadamard array is the one.** `T[n,k]=parity(popcount(n&k))` is integer-exact, orthogonal, and **self-similar (recursive nested squares)** — reads as a fractal, not noise, and rewards resolution. Bonus: its main **diagonal is exactly the Thue–Morse sequence**, so Cantor's **flip** of the diagonal is a meaningful escaped real (draw it blazing gold across the field + repeat it as a bit-strip below; VERIFY it equals no row). WARNING that killed 3 other candidates: extracting binary digits by **repeated float doubling dies after ~52 bits** (float64 mantissa) → the right half of every 'digits of x' field goes solid black. Use integer/bit arithmetic (popcount, Pascal-mod-2) or an exact recurrence; never `x*=2;bit=x>=1;x-=bit` past ~50 columns.

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
