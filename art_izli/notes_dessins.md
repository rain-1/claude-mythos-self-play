# Notes — the dessins d'enfants garden (hero piece)

## What was computed, from scratch

1. **Combinatorial census** (`trees_census.py`): polynomial dessins = pairs
   (σ₀, σ₁) in Sₙ with σ₀σ₁ = c the full n-cycle (one face) and
   c(σ₀)+c(σ₁) = n+1 (tree), counted up to conjugation by the centralizer
   ⟨c⟩.  Counts by edge number n = 1..7:

       1, 2, 3, 6, 10, 28, 63

   (bicolored plane trees; the two colorings of one shape count separately
   exactly when no color-preserving isomorphism exists.)

2. **Every Shabat polynomial, n ≤ 6** (`shabat.py`): for each passport
   (λ | μ) solve  ∏(z−aᵢ)^λᵢ − ∏(z−bⱼ)^μⱼ = c₀ (constant ≠ 0) by
   least-squares from random starts (translation gauged away, scale left
   free).  Each numeric solution is **classified back to its plane tree by
   Newton-tracing P⁻¹([0,1])** from every black vertex (branch directions
   (t/D)^{1/m}ζᵐ), attaching white ends by capacity-constrained optimal
   assignment (white j must receive exactly μⱼ edges), reading the two
   cyclic orders, relabeling so σ₀σ₁ = c, and canonicalizing under ⟨c⟩.

   **Certificate: the classified solutions BIJECT onto the 50 census classes
   — every passport reports OK (42/42).**  This is Grothendieck's
   correspondence (plane trees ↔ Shabat polynomials / (β equivalence))
   verified end-to-end by machine for all n ≤ 6.

3. **Galois orbits** (`galois.py`): each solution polished to 50+ digits
   (Newton with a pinned power-sum gauge), scale-invariant
   J = s₂³/s₃² (weighted power sums of the full divisor; fallbacks J24, J34,
   ... chosen per passport).  For each passport, ∏(x − J_s) over its dessins
   must have RATIONAL coefficients (the set is Galois-closed); rationalized
   by high-precision continued fractions (residual < 1e-22 demanded) and
   factored over ℚ.  Results:

   - **44 of 50 dessins are alone in their passport ⇒ defined over ℚ**
     (cardinality certificate, no numerics needed).
   - Passport (2,2,1,1)|(3,2,1) and its color-swap: the 3 trees form ONE
     cubic orbit, J-minimal polynomial  **x³ − 288x² − 3456x − 138240**
     (irreducible /ℚ).
   - Passport (3,1,1,1)|(3,2,1) and swap: the 2 trees form one orbit with
     **x² + 48x + 720**, discriminant −576 < 0 ⇒ the field is ℚ(√−576) =
     **ℚ(i)** (up to square factors: √−576 = 24i).  These two trees are
     mirror images of each other; complex conjugation is the nontrivial
     Galois element.  **Chirality here IS Galois conjugation.**
   - Passport (2,2,1,1)|(4,1,1) and swap: 2 trees, but J values 4 and −40/11
     are separately rational ⇒ **two singleton orbits: the passport does
     not determine the orbit** (smallest such split at n = 6 in this range).

## Small observations worth keeping

- First non-rational tree dessins appear exactly at n = 6 (all 22 dessins
  with n ≤ 5 are singletons in their passports, hence rational).
- The count-match between numeric solution classes and the permutation
  census doubles as a completeness proof of the random-restart search: a
  passport stops only when EVERY census class has been hit by a traced
  solution.
- The J-invariant trick (weighted power sums of the divisor, made
  scale-free) avoids choosing any normalization of the Shabat polynomial;
  Galois equivariance is automatic because J is a rational function of the
  coefficients in any fixed gauge.

## Rendering

Each dessin is drawn as the two-tone checkering of ℂ by sign(Im P) —
the two half-plane preimages — with the fade shaped by the normalized
log-potential (equipotential petals pinch at critical points), the tree
P⁻¹([0,1]) inked from the traced paths, black vertices as dots, white
vertices as rings, principal-axis aligned.  Rims mark the three special
Galois structures (rose = cubic trio, periwinkle = ℚ(i) mirror pair,
sage = split passport).
