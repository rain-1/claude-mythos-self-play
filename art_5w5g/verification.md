# HELD — verification dossier

Run 2026-07-29, branch `claude/magical-faraday-5w5gjc`.
Everything below is computed from scratch in this directory; no results are
quoted from literature except the MO questions themselves.

## The question (MO 513668, live, open)

> For what n can coins of radius 1/2, 1/3, …, 1/n (at least one of each, no
> other kind) be held rigidly in a circular tray of radius 1?

Poster (Dan): n = 2, 3, 4 work; suspects impossible for n ≥ 5; shows a
"perfect fit" {½,½,⅓,¼,¼,⅙,⅙,⅐} that misses the 1/5, and a near-miss where a
coin of radius 0.99991…/4 would be needed.

## 1. The exact rim-angle arithmetic (engine.py)

A coin of radius a=1/p tangent to the tray sits with center at distance
1−a. Two tangent rim coins of radii a=1/p, b=1/q subtend the central angle

    cos θ(p,q) = ((1−a)² + (1−b)² − (a+b)²) / (2(1−a)(1−b))  — ALWAYS RATIONAL.

Table (curvatures 2..9, cosines):

|     | 2    | 3   | 4    | 5    | 6     | 7     | 8     | 9     |
|-----|------|-----|------|------|-------|-------|-------|-------|
| 2   | −1   | 0   | 1/3  | 1/2  | 3/5   | 2/3   | 5/7   | 3/4   |
| 3   |      | 1/2 | 2/3  | 3/4  | 4/5   | 5/6   | 6/7   | 7/8   |
| 4   |      |     | 7/9  | 5/6  | 13/15 | 8/9   | 19/21 | 11/12 |
| 5   |      |     |      | 7/8  | 9/10  | 11/12 | 13/14 | 15/16 |
| 6   |      |     |      |      | 23/25 | 14/15 | 33/35 | 19/20 |
| 7   |      |     |      |      |       | 17/18 | 20/21 | 23/24 |
| 8   |      |     |      |      |       |       | 27/28 | 31/32 |
| 9   |      |     |      |      |       |       |       | 35/36 |

Coincidences that drive everything: θ(2,3)=π/2, θ(2,5)=θ(3,3)=π/3,
θ(2,6)=arccos(3/5), θ(3,6)=arccos(4/5) (the 3-4-5 triangle!),
θ(3,7)=θ(4,5), θ(2,9)=θ(3,5), θ(3,9)=θ(5,5), θ(4,9)=θ(5,7).

**Closure certificate.** A rim ring [p₁…p_k] closes exactly iff
Σθ = 2π iff the product of unit complexes Π(c_j + i·s_j) equals 1, with
s_j = √(1−c_j²). Each factor lives in ℚ(i, √d_j) (d_j = squarefree kernel);
we multiply out EXACTLY in the tower ℚ(i, √2, √3, …) (`TowerElt`) and test
== 1. This is a proof, not a numeric check, for every positive result below.

**Rigidity certificate** (`is_rigid`). Unilateral contact system
(tray: concave constraint; coin–coin: convex strut). Test:
1. LP: no strict first-order flex (maximize the minimum constraint growth,
   orthogonal to the global rotation).
2. Self-stress support via per-contact LPs; strict ω > 0 on the stressed core;
   prestress stability: the stress-corrected second-order form
   Q(v) = −Σ ω_c vᵀH_c v is positive definite on the core's first-order flex
   space (Connelly–Whiteley prestress stability; the tray's concavity is what
   blocks the rim-sliding flexes at second order).
3. Unloaded coins: iterative wedge-pinning — a coin is pinned if its contact
   normals to pinned neighbors/tray positively span ℝ².
All three known configurations (and every court in the art) pass; a floppy
control (5-arc of thirds) correctly FAILS at step 1.

## 2. The Galois obstruction and the complete rim-ring census

For each radical class d, the Galois conjugation √d → −√d inverts exactly the
class-d factors of the closure product; invariance forces

    Σ (angles in class d) ≡ 0  (mod π)   — for every d > 1 separately,

and the class-1 (rational-sine) part must solve an exact unit equation in
ℚ(i) — where (3+4i)/5 = (2+i)/(2−i) and (4+3i)/5 = i(2−i)/(2+i) force
**#θ(2,6) = #θ(3,6)** by unique factorization in ℤ[i].

Per class (curvatures ≤ 9, `class_relations.py`):
- Classes with a single Niven-irrational angle value (√11, √13, √14, √15,
  √17, √19, √23, √29, √31, √34, √35, √39, √41, √47, √55): m·θ ≡ 0 mod π
  forces m = 0. **Unusable — rigorous** (Niven's theorem).
- Class √5 = {θ(2,7)=θ(3,4), θ(4,8)} and class √6 = {θ(2,8), θ(6,6)}:
  PSLQ at 100 dps, coefficients ≤ 10⁶: **no integer relation** → unusable
  (evidence-grade; any future positive would need a relation with
  coefficients > 10⁶).
- Class √2 = {θ(2,4), θ(4,4)}: EXACT relation 2θ(2,4) + θ(4,4) = π
  (double angle, cos 2θ = 2(1/3)²−1 = −7/9) → usable with **#θ24 = 2·#θ44**.
- Class √3 = {π/3 angles θ(2,5), θ(3,3)} ∪ {θ(5,8), θ(8,8)}: EXACT relation
  **2·arccos(13/14) + arccos(47/49) = π/3** (verified in the tower; found by
  PSLQ, residual < 10⁻¹⁰⁰) → usable with #θ58 = 2·#θ88 and
  #π/3-angles + #θ88 ≡ 0 mod 3.
- Class √7 = {θ(2,9)=θ(3,5), θ(9,9)}: EXACT relation
  **4·arccos(3/4) + arccos(31/32) = π** → usable with #θ29 = 4·#θ99.

Hence the only adjacencies that can ever appear in an exact closed rim ring
(K ≤ 9) are

    2-2, 2-3, 2-4, 2-5, 2-6, 3-3, 3-6, 4-4, 5-8, 8-8, 2-9, 9-9.

**Curvature 7 has no usable adjacency at all: a 1/7 coin can never lie on a
closed rim ring.** A 1/5 coin's only sub-8 partner is 1/2, and in [2,5,2] the
two half-coins are 2·½·sin(π/3) = √3/2 < 1 apart — they overlap. Therefore:

> **Theorem (rim rings).** No exact closed rim ring with curvatures ≤ 7
> contains a coin of radius 1/5. In particular no n=5 configuration of the
> rim-ring type exists. (For curvatures ≤ 9 the 1/5 re-enters only through
> the 5-8-8 law; see below.)

**Census (census2.py, DFS over the reduced alphabet + tower certificates +
embedding + rigidity):** for curvatures ≤ 9 there are, up to
rotation/reflection, exactly
- **24 rigid rings** — sizes drawn from {2,3,4,5,6,8} only, including the
  poster's n=3 ring [2,3,3,3,3] and n=4 ring [2,3,2,4,4] (whose closure is
  the double-angle identity 2·arccos(1/3) + arccos(7/9) = π);
- **71 exact-but-flexible rings** — they close exactly and still rattle;
  e.g. [2,2,4,4] (the quarter-coins shimmy in a slack lune) and the entire
  18-coin {5,8} family such as [5,8,8]×6 (the long arch buckles: strict
  first-order flex);
- **21 ghosts** — rings that close exactly in angle but whose coins overlap
  in space, e.g. [2,5,2,5,2,5] and every 2-9 ring: exact arithmetic, no
  geometry.

**The five, held at last:** the rings [2,5,8,8,5,2,5,8,8,5],
[2,3,2,5,8,8,5], [2,3,6,2,5,8,8,5], [2,4,4,2,5,8,8,5],
[2,5,8,8,5,2,6,3,6] are exact, embeddable and RIGID — the first rigid tray
configurations (that we know of) containing 1/5 coins. The 1/5 enters only
clamped as [5,8,8,5] between two half-coins — never in the company
{2,3,4,5} that the question demands.

## 3. The n = 5 sweep (search_jam.py, refine_shore.py)

All 137 multisets over sizes {½,⅓,¼,⅕} (each ≥ 1, area ≤ 0.94π, ≤ 14 coins).
For each: maximize the inflation s of all coins inside the unit tray (SLSQP,
48 random restarts; 400 for the 21 multisets that came within 0.02 of 1).
A rigid n=5 fit must be a local maximum with s = 1 exactly AND rigid.

Result: the ONLY multiset reaching s = 1 is {½,½,⅓,¼,⅕} — and its s = 1
configurations (64 near-1 local maxima tested in the refined pass) are all
the rigid [2,2]+pocket-⅓ core with the ¼ and ⅕ as loose rattlers — never
rigid as a whole. No fully rigid s = 1 configuration exists anywhere in the
sweep (first pass 137 × 48 restarts; refined pass 21 shortlisted × 400).
Closest approaches (refined, `shore.json`):
- from below: {½,½,⅓,¼,⅕,⅕} at s = 0.9978492…  (deficit 2.15·10⁻³)
- from above: {½,⅓,⅓,⅓,¼,⅕,⅕,⅕} at s = 1.0013838 — fits with slack
  1.38·10⁻³ and therefore rattles forever (the subject of THE RATTLE).

## 4. The healing coin (healing_coin.py)

The poster's near-miss (one coin of radius 0.99991…/4). Reproduced from
their published layout; the active tangency system (14 contacts + rotation
gauge = 15 equations in 15 unknowns) solved by Newton at 140 digits
(residual < 10⁻¹⁴⁰):

    ρ = 0.24997752978402524837391130721213031686347536079402…
    4ρ = 0.99991011913610099349564522884852126745390144317607…

PSLQ (140 dps): ρ is a root of the **irreducible degree-8** integer polynomial

    6258424889841 x⁸ − 9111878379514 x⁷ + 31260552368584 x⁶
    + 1825775790476 x⁵ − 1243601902583 x⁴ − 6749840461835 x³
    − 7350004829076 x² − 1190956301534 x + 858349265837 = 0

(residual 5·10⁻¹⁰⁷; the plausible degree-4 relation that PSLQ offers at 60
digits is spurious — it fails at 140). The coin that would heal the court is
algebraic of degree 8: **no coin of radius 1/n can ever stand in its place.**

## 5. The poster's perfect fit {½,½,⅓,¼,¼,⅙,⅙,⅐}

Found independently by the jam search: s_max = 1.000000000000 (twelve digits),
21 contacts, RIGID (prestress-stable core + wedged fills), and every one of
the 21 contacts carries strictly positive stress (min ω/max ω = 0.17). The
two ⅙ coins sit in the two (−1,2,3)-Descartes pockets — (−1)+2+3+6 satisfies
the Descartes identity exactly; the ⅐ touches BOTH halves and BOTH quarters —
four tangency constraints on three unknowns (x, y, and the closure of the
ring), an over-determined exact coincidence: the deep reason this court
exists at all.

## 6. The envelope criterion (skin.py, MO 513505)

For C(t), r(t): v=|C′|, w=r′/v, q=√(1−w²), the envelope branches are
γ_± = C + r(−wT ± qN) with signed curvature (vκ ± w′/q)/|L_±|,
L_± = ±vq − rΩ_±. Verified: envelope points satisfy F = F_t = 0 to 10⁻¹⁶;
the closed-form curvature matches finite differences to ~10⁻⁸ (median);
the convex family has Ω_± > 0 everywhere (0 sign flips — certified convex);
the torn family has 2 and 4 sign flips and 4+4 genuine L=0 cusps.

## 7. The rattle (rattle.py)

Multiset {½,⅓,¼,¼,⅕×7} (closest floppy fit): hard-disk MCMC at s=1 from the
jammed configuration, Procrustes rotation gauge; a strict first-order flex
certificate at the s=1 max-contact configuration; per-coin wander clouds and
their areas in `rattle_stats.json`. The gold skeleton in the render is the
same coin set jammed in the tray shrunk by the slack factor — the world in
which they would be held.

## Reproduction

    python3 engine.py            # angle table + certificates for known configs
    python3 class_relations.py   # the Galois/Niven/PSLQ class analysis
    python3 census2.py           # complete K<=9 rim-ring census
    python3 search_jam.py n5     # the 137-multiset sweep (slow)
    python3 refine_shore.py      # 400-restart refinement of the shore
    python3 healing_coin.py      # the degree-8 healing coin
    python3 prepare_courts.py    # court catalogue for the renders
    python3 hero.py / skin.py / rattle.py [proto]
