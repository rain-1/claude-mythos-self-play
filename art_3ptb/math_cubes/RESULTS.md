# Integers as sums of 6 cubes of non-constant linear polynomials (MO 516220)

Problem: write n = Σ_{i=1..6} (A_i x + B_i)^3 identically in x, with A_i ≠ 0. This holds exactly when
ΣA³ = ΣA²B = ΣAB² = 0 and ΣB³ = n. Sign is free because (−f)³ = −f³.
Height H = max |A_i|, |B_i|.

## 1. Literature (checked quickly)
- **A. Choudhry, "Expressing an integer as a sum of cubes of polynomials", arXiv:2311.07325 (2023).**
  - Every integer is a sum of **five** cubes of polynomials in Z[t]. The proof uses six identities, one per class
    n mod 6, built from 6r = (r+1)³+(r−1)³−2r³ by adding (−6t+j)³ and solving for r. The polynomials there have
    degree 3, not degree 1.
  - Four cubes: the paper covers p³+q³ and 2(p⁶−q⁶). The 2(p⁶−q⁶) case is a **linear** identity:
    (pt−q²)³+(−pt−q²)³+(qt+p²)³+(−qt+p²)³ = 2(p⁶−q⁶), for example 126.
  - Open in that paper: which integers are sums of four polynomial cubes, for instance 3 and 4.
- Werebrusow (1908): (1+6t³)³+(1−6t³)³+(−6t²)³ = 2.
- Mahler (1936): (9t⁴)³+(3t−9t⁴)³+(1−9t³)³ = 1.
- Mordell, J. London Math. Soc. 17 (1942) is the reference for those two identities. Apart from a³ and 2a³, no
  integer is known to be a sum of three polynomial cubes.
- Demjanenko (1966): every n ≢ ±4 (mod 9) is a sum of four integer cubes. Ryley (1825): every rational is a sum of
  three rational cubes. Vaserstein, Math. Comp. 56 (1991): sums of cubes in polynomial rings.
- I found no published result about **linear** polynomials or about 6 cubes. As far as I can tell, the MO question
  (F(3) ≤ 6 for linear polynomials) is open in print.

## 2. Computation (single core, C at -O2)
- `gen.c` searches all 6-tuples exhaustively by meet-in-the-middle (3+3 split, keyed on (ΣA³,ΣA²B,ΣAB²)). It covers
  every height H ≤ 14 and every |n| ≤ 5000, so **H(n) is exact whenever it is ≤ 14**.
- `paired.c` searches the paired form exhaustively for H ≤ 52 (with H ≤ 40 for |n| ≤ 5000).
  - The form is n = Σ_k [(A_k x+u_k)³ − (A_k x+v_k)³].
  - Write s = u−v and S = u+v. The conditions are Σ s_k A_k² = 0 and Σ s_k A_k S_k = 0, and
    **n = (Σ s_k³ − 3 s₁s₂ φ²/(s₃A₃²))/4** with φ = S₁A₂ − S₂A₁.
  - For fixed (A,s) the admissible S lie in a plane, and n depends only on φ: the x-shift S ↦ S+jA is the only
    other freedom.
  - This turns the search into a 1-parameter loop.
- `assemble.py` verifies every stored representation by exact expansion.
- Outputs:
  - `reps.json`: 861 values n with |n| ≤ 500, each with its minimal-height representation, as [[A,B],…].
  - `height.json`: H(n) for every n found with |n| ≤ 5000.
  - `paired_flag.json`: whether the best representation is in paired form.

### Key numbers
- **Small n:**
  - H = 3 suffices for ±1, ±2, ±3, ±7, ±8.
    Example: 1 = (x+1)³−(x−2)³+(2x−2)³−(2x+1)³+(3x)³−(3x−1)³.
  - Other small heights: H(9) = H(12) = H(30) = 2, H(6) = 5, H(10) = 9.
  - H(4) = 29: 4 = (21x−11)³−(21x−28)³+(27x−29)³−(27x+20)³+(28x+19)³−(28x−17)³.
- **No representation found** for these n with 0 < n ≤ 100: 5, 14, 23, 25, 31, 32, 38, 40, 41, 66, 67, 73, 88, 95.
  "Not found" means no general representation with H ≤ 14 and no paired one with H ≤ 52.
  - |n| ≤ 500: 70 positive n missing, plus their negatives.
  - |n| ≤ 2000: 314 positive n missing.
  - **n = 5 is the smallest unresolved case.**
- **Where the gaps fall:** the missing n sit overwhelmingly in classes 3, 4, 5, 6 mod 9, mostly 4 and 5.
  - Missing count by class mod 9 (n ≤ 2000): 0:3, 1:13, 2:10, 3:55, 4:89, 5:82, 6:46, 7:10, 8:6.
  - Mean H is highest for n ≡ 5, 13 mod 18, which are the **odd** n ≡ ±4 mod 9.
- **Paired versus general:** the minimal representation is usually paired. Some exceptions where the best one is not
  paired: ±18, ±20, ±44, ±45, ±55, ±190.

## 3. Structure and what I can prove
**(a) Necessary congruence conditions.** Since b³ ≡ b mod 2 and mod 3, and ΣA²B = 0:
- If every A_i is prime to 3, then 3 | n. More precisely n ≡ Σ_{3|A_i} B_i (mod 3).
- If every A_i is odd, then n is even. More precisely n ≡ Σ_{A_i even} B_i (mod 2).
- Mod 9: f(x)³ mod 9 depends only on f(x) mod 3, so Σ_i χ(A_i x+B_i) ≡ n (mod 9) for x = 0, 1, 2, where χ takes
  the values 0, 1, −1. That sum lies in [−6, 6].
  - So for n ≡ 4 (mod 9) each of the three sums must be 4 or −5. That forces at least one A_i ≡ 0 (mod 3), and
    either at least four of them, or five of the six values ≡ 2 (mod 3) at some x.
- Together these explain why **odd n ≡ ±4 (mod 9)** (5, 13, 23, 31, 41, …) need both an even A and A's divisible
  by 3, and so have large heights. These are **not** obstructions, since n = 4, 13 and 22 are found.

**(b) No simple linear-parameter families.**
- Setup: a family n = α + 3βt with fixed A_i is the same thing as a ternary identity
  Σ(A_i x + B_i y + w_i z)³ = αy³ + 3βy²z.
- Paired form with fixed A and s: the quadratic form above restricted to its plane has rank 1. So n can only grow
  quadratically along such a family, as n = K + cφ²; it can never be linear in a parameter.
- Small ternary identities: an exhaustive search over |A|, |B|, |C| ≤ 4 (`tern.c`) finds **none**.
- How they can be built: the pairs (A_i, w_i) must themselves represent 0, that is Σ(A_i x + w_i z)³ ≡ 0. On the
  admissible B's, Σ B_i²(A_i x + w_i z) = λ(B)²·ℓ₀ for a fixed linear form ℓ₀ (observed in every case).
  - Changing variables so that ℓ₀ ∝ z produces genuine families (`fam.c`, `famsearch2.py`).
  - These have large moduli. 541 families are verified in `families.json`.

**(c) Theorems proved here (identities verified symbolically for all integers t):**
- **Every n ≡ 63 (mod 126)** is a sum of 6 cubes of non-constant linear polynomials:
  Σ_i (A_i x + B_i + w_i t)³ = 63 + 126t,
  - A = (247, 104, 1, −152, −232, −58)
  - B = (−12, 15, 20, −3, 13, −18)
  - w = (−16, −7, 0, 10, 15, 4)
  - α = 63 and β = 42, as listed in `families.json`.
- **Every n ≡ 42 or 168 (mod 210)**, by two families sharing the same A and w (see `families.json`).
- Further classes, also in `families.json`:
  - n ≡ 210 (mod 420)
  - n ≡ 0 (mod 504)
  - n ≡ 336 or 504 (mod 840)
  - n ≡ 567 (mod 1134)
- **Even n with a three-cube condition:** n = 2(u³+v³+w³) whenever p²u+q²v+r²w = 0 has a solution with p, q, r all
  nonzero:
  Σ_{±}[(±pt+u)³+(±qt+v)³+(±rt+w)³] = 2(u³+v³+w³).
  This generalizes Choudhry's 2(p⁶−q⁶).
- I could **not** cover all residue classes, so F(3) ≤ 6 is **not proved** here.

## 4. Conjecture
Every integer n is a sum of 6 cubes of non-constant linear polynomials in Z[x], and in fact a paired one. H(n) grows
slowly but unevenly. It is largest for odd n ≡ ±4 (mod 9), where the representation must use A_i ≡ 0 (mod 3) and an
even A_i at the same time. n = 5 is the first value to settle; it is out of reach at height ≤ 52 in paired form and
≤ 14 in general.
A proof would most plausibly come from Choudhry-style families whose A_i depend polynomially on a parameter, rather
than from families with constant A_i, which (b) shows are rigid.

## Files
- `gen.c`, `paired.c`: the general and paired searches.
- `tern.c`, `fam.c`, `fam2.c`, `famsearch2.py`, `famlib.py`, `families_verify.py`: the family searches and their
  verification.
- `assemble.py`: builds the JSON outputs.
- `g_H*.txt`, `p_H*.txt`: raw search output.
- `zeros*.txt`: representations of 0, used by the family search.
