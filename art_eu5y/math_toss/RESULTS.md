# Tossprints and ribbon Schur functions (MO 516996) — what I found on 2026-11-22

**In one paragraph.** Equal ribbon Schur functions always give equal tossprints (proved, via a product
formula for stair polynomials). The extra coincidences come from writing the stair's corner set as
a direct sum T ⊕ U and turning T over (proved to preserve the tossprint; BTvW's moves are the special
case where U is an initial piece of the stair). This reproduces every exhaustive count up to n = 32
and gives 535,276 at n = 100, where the asker reports 535,284. The lengths with a discrepancy are
conjecturally exactly n = r·a·b with r ≥ 2, a, b ≥ 3, n ≠ 18 (matches the asker's 29 values ≤ 100).

**The question.** Toss a coin N times (1 = heads, 0 = tails). For every stretch of the string write
the pair (number of 0s, number of 1s) on a slip and drop it in a bag; the bag is the *tossprint*.
a(N) = number of distinct tossprints. The asker observed a(N) = R(N+1) for N ≤ 22, where R(n) is the
number of distinct ribbon Schur functions with n cells (OEIS A120421), and then small differences at
N+1 = 24, 27, 30, 32, 36, 40, 42, 45, 48, 50, 54, … ; a commenter observed that equal ribbons seem
to give equal tossprints. No answer was posted when I read it.

Everything below is stated for n = N + 1, the number of *corners* of the lattice stair
p_0 = (0,0), p_k = p_{k−1} + (1,0) if the k-th toss is 0, + (0,1) if it is 1.
The tossprint is the multiset {p_j − p_i : i < j}.

## 1. The dictionary (proved)

Put P_w(x,y) = Σ_k x^{a_k} y^{b_k} over the corners (a_k, b_k). Then

    P_w(x,y) · P_w(1/x,1/y) = n + Σ_{i<j} (x^d + x^{−d}),   d = p_j − p_i,

so **two strings have the same tossprint iff P_w P̄_w = P_v P̄_v** (P̄(x,y) = P(1/x,1/y)). On the
torus |x| = |y| = 1 this says |P_w| = |P_v|: the tossprint is the diffraction intensity of the stair
and equal tossprints are *homometric* stairs (the phase problem of crystallography).

A ribbon with n cells is a composition α of n, i.e. a string of n − 1 bits (0 = next cell in the same
row, 1 = start a new row). Billera–Thomas–van Willigenburg's product is, on strings,

    α ∘ β  =  β s_1 β s_2 β … s_{a−1} β          (s = the string of α, a = |α| corners),

and their theorem says r_α = r_β iff β is obtained from α by reversing some factors of the
factorisation of α into ∘-irreducibles.

**Lemma 1 (product formula).** Let β have b corners and end at D = (h, v), h + v = b − 1. Then

    P_{α∘β}(x,y) = P_α(X, Y) · P_β(x,y),      X = x^{h+1} y^v,   Y = x^h y^{v+1}.

*Proof.* The i-th copy of β starts at Σ_{k≤i} (D + e_{s_k}) = i·D + q_i, where q_i is the i-th corner
of α and |q_i| = i. The map q ↦ q + |q|·D is linear and sends (1,0) ↦ (h+1, v), (0,1) ↦ (h, v+1). ∎

Reversing a stair turns P into (monomial)·P̄. So reversing α or β in α∘β flips one factor of a
product and leaves P P̄ alone.

**Corollary 1.** Equal ribbon Schur functions ⇒ equal tossprints; hence a(N) ≤ R(N+1) for all N.
(This proves the commenters' observation.)

## 2. The new move: a stutter (proved)

The proof of Lemma 1 never used that the copies of β are equal — only that they all end at the
same D. And if the outer string is itself a product γ∘α, the factor P_α survives as long as the
inner blocks are constant along each copy of α:

**Theorem 1 (stutter move).** Let γ have r corners, α have a corners, and let β_1, …, β_r be strings
with b corners each and *the same number of 1s*. Write

    w = (γ∘α) ∘ (β_1^a, β_2^a, …, β_r^a)
      = [α∘β_1] t_1 [α∘β_2] t_2 … t_{r−1} [α∘β_r]            (t = the string of γ).

Then P_w(x,y) = P_α(X,Y) · Q(x,y) with Q = Σ_k (monomial)_k · P_{β_k}, and therefore replacing α by
any α′ with the same tossprint (for instance α reversed) does not change the tossprint of w.

In words: *a stair of r flights; every flight is the same pattern α of landings; the treads between
landings may be cut differently in different flights, as long as each tread-block rises and runs the
same. Turn the landing pattern over in all flights at once: the bag does not notice.*
When all β_k are equal this is the BTvW move "reverse the middle factor of γ∘α∘β". When they are not,
w is in general ∘-irreducible and the move is invisible to ribbon Schur functions.

**The first example** (n = 24 = 2·3·4, r = 2, a = 3, b = 4): α = 10, β_1 = 110, β_2 = 101,

    w  = 110 1 110 0 110 · 1 · 101 1 101 0 101 = 11011100110110111010101
    w′ = 110 0 110 1 110 · 1 · 101 0 101 1 101 = 11001101110110101011101

Both are ∘-irreducible, w′ ≠ reverse(w), and both have the same 276 slips. Here
P_w = A·Q, P_w′ = Ā·Q·(monomial) with A = 1 + Y + XY, X = x²y², Y = xy³. These two stairs are the
two slopes of the valley, the two bead chains and the two fingerprints.

Why n = 18 = 2·3·3 gives nothing: b = 3 leaves only β ∈ {01, 10}; with r = 2 the pair must be
(01, 10) or (10, 01), Q is then centrally symmetric, and flipping α is the same as reversing w.

## 3. The stutter is not everything: n = 32, and the general move (proved)

I first conjectured that reversal + stutter moves generate tossprint equivalence. Exhaustive search
at n = 32 **refuted** that: 240 classes larger than {w, reverse w}, of which 8 are not reached by
stutter moves. The smallest:

    w = 1010101 1 0110011 · 1 · 1011101 0 0111011
    v = 1011101 0 0111011 · 1 · 1010101 1 0110011        (the two halves change places)

Each half is a small stutter word over the same two tread blocks 101, 011, but with *different*
landing patterns: P_half1 = (1 + x²y²)·Q, P_half2 = (1 + xy³)·Q with the common
Q = P_101 + x³y⁵·P_011. So P_w = Q·G with G = (1 + x²y²) + x^c(1 + xy³): here both factors are
"multi-stairs", and the landing pattern itself stutters. The right statement is two-sided:

**Theorem 2 (direct-sum flip).** Let S be the corner set of a stair w. Suppose S = T ⊕ U (every
corner is t + u for exactly one pair; equivalently P_w = P_T·P_U with 0/1 polynomials), and suppose
(−T) ⊕ U, translated to start at the origin, is the corner set of a stair w′. Then w and w′ have the
same tossprint. *(Immediate from §1: P_w′ = monomial · P̄_T · P_U.)*

BTvW's moves are the case "U is an initial segment of the stair"; the stutter move is the case
"T is a dilated stair". All decompositions of a given stair can be listed quickly:

**Lemma 2 (smallest uncovered corner).** In a decomposition S = T ⊕ U with 0 ∈ T ∩ U, both T and U
are subsets of S, and the first corner (in stair order) not yet written as t + u with known t, u is
a new element of T or a new element of U. *(If s = t + u with t, u ≠ 0 then t and u are earlier
corners, hence already known, hence s is already covered.)*

**Lemma 3 (same cuts in every layer).** Cut U into maximal runs of consecutive corners
U = X_1 ∪ … ∪ X_r. Then every translate X_k + t is a run of consecutive corners of S, and the stair
visits the r·|T| runs in an order that is increasing in k and in t. *(Two corners of a stair at
unit distance are consecutive, and translation preserves unit distance.)*

`dsum.py` implements Lemma 2; `gen.cpp` enumerates **all** triples (w, T, U) with n corners in which
neither T nor U is centrally symmetric and U is not an initial segment (0.1 s for n = 36, a few
minutes for n = 100).

## 4. What the computer says

Exhaustive (`toss.cpp`, `toss2.cpp`: every binary string, 64/128-bit additive hash of the bag,
classes re-checked exactly), against the two theories (`verify.py`, `count2.py`: stutter moves;
`dsum.py`, `gen.cpp` + `count3.py`: direct-sum flips):

| n = N+1 | a(N) (exhaustive) | R(n) − a(N) found | stutter moves only | direct-sum flips | classes not explained by flips |
|---|---|---|---|---|---|
| ≤ 23 | = R(n) | 0 | 0 | 0 | 0 |
| 24 | 4,196,192 | 8 | 8 | 8 | 0 of 160 |
| 25, 26 | = R(n) | 0 | 0 | 0 | 0 |
| 27 | 33,558,279 | 12 | 12 | 12 | 0 of 247 |
| 28, 29 | = R(n) | 0 | 0 | 0 | 0 |
| 30 | 268,451,198 | 42 | 42 | 42 | 0 of 642 |
| 32 | 1,073,774,352 | 24 | 16 | 24 | 0 of 240 |

(Every n ≤ 30 and n = 32 was run exhaustively — `small.log`, `r30.log`, `r32.log`; only n = 31, a
prime, was skipped. The asker's own 8 and 12 at N = 23, 26 are reproduced.)

Predictions beyond brute force (direct-sum flips; in brackets what stutters alone give):

| n | 36 | 40 | 42 | 45 | 48 | 50 | 54 | 56 | 60 | 63 | 64 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R(n) − a(n−1) | 366 [360] | 174 [132] | 804 [804] | 962 [962] | 4862 [4520] | 252 [252] | 17,868 [17,814] | 2636 [1832] | 63,340 [62,612] | 34,524 | 11,892 |

**The one published number I could test.** The asker reports R − a = **535,284** at N = 99 (n = 100).
Stutter moves alone give 516,632. Direct-sum flips give **535,276**: 2,221,648 flips between
1,087,280 ribbon classes, falling into 552,004 components. That is all but 8 of the asker's
difference, at a length where 2^99 strings rule out any direct check. I do not know where the last
8 come from: a third mechanism that first appears somewhere in 33 ≤ n ≤ 100 (for instance a factor
of P_w with coefficients outside {0, 1}), or a slip on one of the two sides. I am not hiding it.

Negative checks: `gen` finds no flip between different ribbon classes for n = 16, 18, 20, 28, 44, 52
(for n = 18 it finds 16 flips, all inside ribbon classes).

## 5. Conjectures

**Conjecture A′ (replaces my refuted Conjecture A).** Two binary strings have the same tossprint iff
one is reached from the other by reversal and direct-sum flips (Theorem 2). True for every n ≤ 30 and for
n = 32 (exhaustive); at n = 100 it accounts for 535,276 of the reported 535,284.
The honest status is "true or very nearly true".

**Conjecture B (the asker's second question).** a(N) ≠ R(N+1) exactly when n = N + 1 = r·a·b with
r ≥ 2, a ≥ 3, b ≥ 3 and n ≠ 18; that is, when n is **not** a prime, a product of two primes, 4p, 8,
16 or 18. For n ≤ 100 this gives 24, 27, 30, 32, 36, 40, 42, 45, 48, 50, 54, 56, 60, 63, 64, 66, 70,
72, 75, 78, 80, 81, 84, 88, 90, 96, 98, 99, 100 — the asker's table, entry for entry (29 values).

**Proposition (the "if" half of B, for n ≤ 400).** For each of the 168 such n ≤ 400, `witness.py`
builds a stutter pair (α = 0…01, β_1 = 0…01, β_k = 0…010; for b = 3 use 01, …, 01, 10 with r ≥ 3)
and checks that the two words have the same tossprint and lie in different BTvW classes. So
a(n−1) < R(n) there. The "only if" half is known only from the tables (n ≤ 100).

**Remark (why coincidences are rare).** A new coincidence needs three nested scales with the middle
one asymmetric and the inner one varying with the outer; there are about 2^{r+a+rb} such strings
among 2^{rab}.

## 6. Not done
- A proof of Conjecture A′ — what is missing is exactly: "if P_w = A·B in ℤ[x,y] and Ā·B is a stair
  polynomial, then A and B can be taken with 0/1 coefficients". The 8 missing classes at n = 100
  may be a counterexample to this.
- A closed formula for a(N) (a unique-factorisation theory for direct-sum decompositions of
  stairs, in the spirit of BTvW §3–4; Lemma 3 is the first step).
- Exhaustive n = 36 (2^35 strings; about a day with an incremental hash) to test 366.
- Posting to MO 516996. Theorem 1/2, Corollary 1, the two examples and the 535,276 are answer-ready.
