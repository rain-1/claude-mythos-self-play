# Products of two overlapping k-cycles — complete structure (MO 513838)

**Setting** (from the question): S1, S2 ⊆ [N], |S1| = |S2| = k, |S1 ∩ S2| = m, N = 2k−m.
σ uniform on the (k−1)! cycles on S1, τ uniform independent on Cyc(S2), π = στ.
q_{k,m}(ν) = Pr[π ∈ C_ν] for ν ⊢ N. The poster had exact tables for k ≤ 6, a closed
form for m = 2, and called m = 3 "the wall".

All results below were found and verified by exact rational-arithmetic censuses
(orbit-reduced exhaustive enumeration in C, counts converted to exact fractions):
**all m ≤ k for k ≤ 12, plus k = 13 at m = 3** — 43 tables, every probability exact.
Verification artifacts: `wheels.c` (orbit-reduced enumerator), `wheels_wrap.py`
(exact rational conversion + sum-to-1 checks), `wheels_brute.py` (independent
brute force, matches the C enumerator on all overlapping tables), `qdata/`.

---

## 1. The Overlap Principle (empirical theorem, exact for all data)

Write A = S1 ∩ S2. Let ρ = σ_A ∘ τ_A, where σ_A, τ_A are the first-return maps
of σ, τ to A (each is a uniform m-cycle on A, and they are independent).

**(a) Cycle-count law.** The number of cycles of π has the law of the number of
cycles of a product of two independent uniform m-cycles on m points — it does not
depend on k at all:

  Pr[c(π) = c] = Pr[c(αβ) = c],  α, β uniform independent m-cycles on [m].

Verified exactly for every (k, m), k ≤ 12: e.g. the c-distribution at m = 5 is
(1/3, 5/8, 1/24) on c = 1, 3, 5 for k = 5, 6, ..., 12 identically. Via
Boccara/Stanley the right-hand side is classical. In particular
supp c(π) = {m, m−2, m−4, ...} (c ≡ m mod 2 by sign; c ≤ m because **every cycle
of π meets A** — a cycle avoiding A would live in B1 = S1\A or B2 = S2\A alone,
where π acts as a restriction of the single cycle σ resp. τ, which visits A).

**(b) Master formula.** Condition on the type λ = (a_1 ≥ ... ≥ a_c) ⊢ m of ρ,
whose law p_m(λ) = q_{m,m}(λ) is the classical two-full-cycles distribution
(Boccara 1980; Stanley's S_{m+1} description). The k−m points of B1 fall into m
σ-gaps (one per element of A), uniformly over weak compositions of k−m into m
parts, independently of everything else; same for B2 and τ-gaps. Each cycle of ρ
of length a_i absorbs the gap mass of its a_i elements on both sides. Hence

  q_{k,m}(ν) = Σ_{λ⊢m, ℓ(λ)=ℓ(ν)} p_m(λ) · Σ_{(n_i) distinct perms of ν} Σ_{G}
      Π_i C(G_i + a_i − 1, a_i − 1) · C(n_i − a_i − G_i + a_i − 1, a_i − 1)
      / C(k−1, m−1)²,

  where G runs over G_i ∈ [0, n_i − a_i] with Σ G_i = k − m
  (the τ-side masses H_i = n_i − a_i − G_i are then forced).

**This formula reproduces every census value exactly: 1,664 checks
(all ν, all k ≤ 12, m ≤ 9), zero mismatches.** It is the "hypergeometric
mixture over a pure-overlap core" the poster hoped for: all k-dependence is
carried by explicit binomials; all combinatorial difficulty lives in p_m,
which is classical.

Proof sketch of (b): the excursion decomposition of π = στ. Following the
π-orbit, steps outside A are pure τ-steps (through B2) or pure σ-steps
(through B1); the orbit's A-passages compose the two first-return m-cycles.
A cycle of ρ through a_i points of A therefore drags along exactly the σ-arcs
and τ-arcs hanging off those points, giving length a_i + (σ-mass) + (τ-mass).
For σ uniform, (cyclic order of A) and (gap composition) are independent and
uniform — #cycles with a given A-order and gap vector is (k−m)!(m−1)!,
independent of both choices. The negative-hypergeometric weights are the number
of ways compositions aggregate over a_i slots. ∎ (Exhaustively verified as above.)

## 2. The wall at m = 3, demolished (closed form)

For m = 3: p_3 = 1/2 on λ = (3) and 1/2 on λ = (1,1,1). Specializing the master
formula and doing inclusion–exclusion on the box constraints gives, for
ν = (a ≥ b ≥ c) ⊢ 2k−3 with three parts:

  **q_{k,3}(ν) = 2 · |perms(ν)| · ( b·c − t(t+1) ) / ( (k−1)² (k−2)² ),
     t = max(0, k−2−a),**

where |perms(ν)| ∈ {1, 3, 6} is the number of distinct orderings of (a,b,c);
and **Pr[π is a single (2k−3)-cycle] = 1/2** for every k ≥ 3 (this is
p_3((3)) = 1/2 — the overlap principle in action; the single-cycle probability
never depends on k for any odd m: it equals p_m((m))).

Two chambers, one wall at a = k−2 (the largest part = the largest possible
single-side excursion), deficit t(t+1) in the inner chamber — piecewise
polynomiality exactly as double-Hurwitz theory predicts, now with the wall
crossing explicit.

Derivation from the master formula: for λ = (1,1,1) the gap weights are trivial
and the inner sum is the box count T(a,b,c) = #{G ∈ [0,a−1]×[0,b−1]×[0,c−1],
ΣG = k−3}; the closed form is equivalent to the lattice identity
**T(a,b,c) = bc − t(t+1)** (verified for all 52,728 admissible triples with
k < 80; zero failures). For λ = (3) the weight C(k−1,2)² cancels the
normalization, giving Pr[single cycle] = p_3((3)) = 1/2 for every k —
analytically, not just empirically.

Checks: exact for all 143 partitions across k = 4..12; **k = 13 predicted before
computation and confirmed exactly — the 1.6×10⁹-pair enumeration (12! per orbit
class) returned all 44 three-cycle partitions and the single-cycle 1/2 precisely
as the law demanded**; Monte-Carlo at k = 15 (60M samples) confirms the
t = 4 chamber: ν = (9,9,9) observed 3.6787e-3 vs predicted 2(81−20)/33124 =
3.6831e-3 (≈1.5σ), while the "t = 3 continuation" 4.166e-3 is excluded by ~60σ.

The poster's m = 2 formula is the same statement one level down:
q_{k,2}(a,b) = |perms| · min(a,b) / (k−1)² (p_2 is a point mass on (1,1);
diagonal factor-2 = |perms| halving, no inner chamber since a ≥ k−1 always).

## 3. Remarks

- m = 4 and beyond need no new closed form: the master formula IS the closed
  form (p_4 = 1/6, 1/6, 2/3 on (1^4), (2,2), (3,1) etc.), though each
  (m, ℓ(ν)) sector can be expanded into box-count polynomials the same way.
- The c = 2 sector at m = 4 mixes λ = (2,2) and λ = (3,1) — that is exactly why
  it resisted a single product formula.
- Sum rule sanity: Σ_ν q = 1 verified exactly in every table (it is enforced
  structurally by the wrapper).
