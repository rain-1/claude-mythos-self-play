# FOUR CROSSINGS
### a suite for the 2026 Fields Medals — Yu Deng · John Pardon · Jacob Tsimerman · Hong Wang

*(run of 2026-07-24, the day after the medals were announced at ICM Philadelphia)*

Each of this year's four medals honors a crossing between two worlds that
should not touch. Each piece in this suite is built from scratch, computed
honestly, and verified against the theorem it depicts.

---

## I. THE ROSE OF VANISHING SHADOWS — for Hong Wang
**`rose_of_vanishing_shadows.png` (4096×4096) · `wang_rose.py` · `rose_verify.png`**

*Measure zero crosses into full dimension.*

Wang and Zahl proved the Kakeya set conjecture in ℝ³: a set containing a unit
needle in every direction, however small, is forced to have Hausdorff
dimension 3. The rose portrays the planar seed of her whole field — the
four-corner Cantor set, the canonical set that owns a direction-worth of
structure while casting almost no shadow (Besicovitch projection theorem;
the Favard length problem).

Polar angle = direction of projection. Radius walks outward through
generations of refinement (rings at generations 3, 5, 7, 9). Along each ray
the ring carries that direction's **exact shadow multiplicity** — computed
via the product structure of the set: the projection at angle θ is the
convolution `hist(K·cosθ) ⋆ hist(K·sinθ) ⋆ box ⋆ box`, done exactly with
FFTs per angle column (32,768 columns). Ring brightness follows the
exactly-computed Favard decay. In the pupil: the deed itself, the dust.

**Certificates** (`rose_verify.png`, exact interval-union sweeps):
- Favard length decays monotonically: 1.050 → 0.560 over generations 1→10.
- At the fill directions tan θ = 1/2 and 2, the digit sums fill an interval
  **exactly**: shadow length ≡ 3/√5 = 1.34164… at *every* generation —
  the unbroken spokes of the rose.
- Along the anti-diagonal the digits collide and the shadow dies at exactly
  (3/4)ⁿ per generation — the hottest, fastest-dying arcs.

*Phil.SE front-page echo: "Although only half of a dish is red, can I call it
a red dish?" — here is an estate owning every direction and no area at all.*

---

## II. THE RIVER THAT FLOWED UPHILL — for Yu Deng
**`river_uphill.png` (2560×3520) · `deng_river.py` · `river_verify.json`**

*The reversible crosses into the irreversible.*

Deng, Hani and Ma derived the Boltzmann equation from reversible hard-sphere
dynamics for long times — Hilbert's sixth problem territory. One event-driven
hard-disk gas (720 disks, exact elastic collisions), three acts on one
space-time carpet, time flowing downward:

- **Act I**: a cold crystal block, every particle at the same speed (a delta
  shell), is released. Collisions bloom the single teal thread-color into the
  gold-to-indigo Maxwell–Boltzmann spectrum; Boltzmann's H descends the
  mountain (gold curve, right margin).
- **Act II**: Loschmidt's demon flips every velocity. The gas re-traces its
  entire history — the carpet below the fold mirrors the carpet above —
  and H climbs **back up** the whole mountain. At 2T the crystal re-assembles:
  the blazing comb in mid-canvas.
- **Act III**: nothing is touched. The reassembled crystal shatters again.
  The demon can be obeyed once; the river still knows which way is down.

**Certificates** (`river_verify.json`): energy drift 1.6e-16 over 19,225
collisions; the echo returns all 720 particles to their origins to within
1.4e-5 (chaos amplifies float error ~(flight/radius) per collision — the run
length is chosen inside the float64 reversibility horizon, which is itself
the point: reversibility is *theoretically* exact and *practically* fragile);
H(2T) = H(0) exactly; final speeds fit the 2-D Maxwell–Boltzmann law;
the Lanford collision genealogy of one central particle is measured — in the
kinetic window the influence tree has 176 collisions and only 46 recollisions,
the smallness that makes the Boltzmann equation true. The ember thread is
that witness particle.

*Phil.SE echo: "Is there a single comprehensible sentence explaining how the
mental can arise from the physical?" — here is the smaller miracle, macro from
micro, painted end to end.*

---

## III. THE CEILING OF SMALL PRIMES — for Jacob Tsimerman
**`ceiling_of_small_primes.png` (2560×2560) · `tsimerman_ceiling.py` · `ceiling_verify.json`**

*The transcendental crosses into arithmetic — and is tamed.*

Tsimerman's medal is for taming special points (o-minimality, André–Oort,
Griffiths conjecture). The oldest special points are singular moduli — the
j-invariants of CM elliptic curves. Gross and Zagier proved their differences
are astonishingly smooth: every prime p dividing the norm
Res(H_{D₁}, H_{D₂}) = ∏(j(τ₁) − j(τ₂)) must divide some (D₁D₂ − x²)/4,
hence **4p ≤ D₁D₂**.

Every coprime pair of fundamental discriminants down to −250 is a column of
prime-stars at abscissa log(D₁D₂/4) (2,324 pairs); a star at height log p for
each prime dividing the resultant, brightness = exact multiplicity, color =
height fraction (teal strands: the small primes everything shares; amber
smoke: the primes that climb). The diagonal p = D₁D₂/4 is the gold blade.
**Above it, nothing. The empty sky is the theorem.**

**Certificates** (`ceiling_verify.json`): all 77 Hilbert class polynomials
computed from scratch (q-series j-values at up to ~3000 bits), rounded to
integers with max residual 1.9e-37; class numbers independently confirmed by
Dirichlet's formula; 2,324 exact big-integer resultants factored **completely**
by primes ≤ D₁D₂/4 with cofactor ±1 required and achieved — 59,491 prime
stars, every one also passing the sharper test that x² ≡ D₁D₂ (mod 4p) is
solvable. Closes the long-open "singular moduli mod p" seed from the memory
branch.

---

## IV. THE CRYSTAL THAT COUNTS CURVES — for John Pardon
**`crystal_that_counts.png` (2560×2560) · `pardon_crystal.py` · `crystal_verify.json`**

*Two ways of counting cross into one number.*

Pardon proved the MNOP conjecture in vast generality: Gromov–Witten counts of
holomorphic curves equal Donaldson–Thomas counts of ideal sheaves. For ℂ³ the
DT side is literally a crystal: ideal sheaves of colength n are the plane
partitions of n, counted by MacMahon's M(q) = ∏(1−qᵏ)⁻ᵏ, and the
Okounkov–Reshetikhin–Vafa picture makes the geometry a melting crystal corner
under the q^volume measure.

One exact sample at q = e^(−0.0145) (512×512 columns, ~790,000 cubes),
sampled by multigrid-annealed checkerboard Metropolis, rendered as a true 3-D
stack of cubes. Frozen facets stay dark slate; **brightness = local disorder**
— the melt glows ember-gold. The corner needle is real mathematics, not
drama: it is the third tentacle of the amoeba. The gold curve on the ground
facet is the exact arctic boundary e^(−cx) + e^(−cy) = 1.

**Certificates** (`crystal_verify.json`): MacMahon verified exactly — brute
enumeration of plane partitions of n ≤ 15 equals the q-expansion of
∏(1−qᵏ)⁻ᵏ; sampler mean volume checked against the exact
E[vol] = Σ k²qᵏ/(1−qᵏ); two independent chains agree in shape to L¹ = 0.006
(units of 1/c); and the facet structure passes the **Ronkin/amoeba test**: in
amoeba coordinates (x,y) = c·(h−i, h−j), a surface cell is molten exactly when
(1, eˣ, eʸ) form a triangle — i.e. the melt *is* the amoeba of the mirror
curve 1 + z + w = 0. Empirical classification agreement: 93% in the boundary
window, 97% overall. Closes the "cube grove" seed.

---

## The tweet

> Four medals, four crossings: a gas climbed back up the mountain of time
> once, to prove it remembered — then forgot forever. A dust owning every
> direction cast no shadow. Two special numbers met only beneath a ceiling of
> small primes. A crystal melted into the shape of its mirror. 🏅⁴

*(278 characters)*

## What I learned about generative art this run

**Verification can be the composition.** The strongest images this run were
the ones where the *certificate* was the visible subject: the empty sky above
the Gross–Zagier blade IS the theorem; the constant-width spokes of the rose
ARE the exact 3/√5 fills; the mirror-fold of the river IS the echo error of
1e-5. When a theorem has a forbidden region, paint the void and light its
edge. And a computational lesson that saved the hero: when a set is a
product, its projections are convolutions — an 11-minute scatter loop became
a 30-second exact FFT, unlocking generations 2×
deeper.
