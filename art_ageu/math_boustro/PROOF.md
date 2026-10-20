# MO 516177: two interleaved boustrophedon triangles

## Statement (exact offsets)

Let c(0), c(1), c(2), ... be arbitrary (from any commutative ring containing Q, or just integers),
and set C(x) = Σ_{n≥0} c(n) xⁿ/n!. Define, for 1 ≤ k ≤ n:

* T1(1,1) = c(1), T2(1,1) = c(0);
* for n ≥ 2:
  T1(n,1) = c(n), T1(n,k) = T1(n,k−1) + T2(n−1,k−1) for 2 ≤ k ≤ n;
  T2(n,n) = T1(n−1,n−1), T2(n,k) = T2(n,k+1) + T1(n−1,k) for n−1 ≥ k ≥ 1.

(This is exactly the PARI `list3`; the question's case is c ≡ 1, i.e. C = eˣ, with T2(1,1)=1.
The "UPD" is c(0)=1, i.e. C = 1 + Σ_{n≥1} c(n)xⁿ/n!.)

**Theorem.** For every n ≥ 1,

    T1(n,n) = n! [xⁿ] C(x)·sec x,        T2(n,1) = n! [xⁿ] C(x)·tan x.

For C = eˣ: T1(n,n) = A003701(n) = 1, 2, 4, 12, 36, 152, ... (n = 1, 2, ...), i.e. `Vec(serlaplace(exp(x)/cos(x)-1))`,
and T2(n,1) = A009739(n) = 1, 2, 5, 12, 41, 142, ... (n = 1, 2, ...), i.e. `Vec(serlaplace(exp(x)*tan(x)))`.
This is the conjecture, with its stated generalisation (and even with c(0) ≠ 1).

## Proof

All series are formal power series over Q; write S = sec x, Θ = tan x, so S′ = SΘ, Θ′ = S².

### Step 1: the standard boustrophedon (Millar–Sloane–Young 1996)

**Lemma.** Given a₀, a₁, ..., define T(N,0) = a_N and T(N,k) = T(N,k−1) + T(N−1,N−k) (1 ≤ k ≤ N), and b_N = T(N,N).
Then B(x) = (S + Θ)·A(x), where A, B are the EGFs of (a_N), (b_N).

*Proof (self-contained).* Put G(x,y) = Σ_{i,j≥0} T(i+j,i) xⁱ yʲ/(i! j!). The coefficient of xⁱyʲ/(i!j!) in
∂ₓG is T(i+j+1,i+1), in ∂ᵧG it is T(i+j+1,i), and the recurrence (with N=i+j+1, k=i+1) says
T(N,i+1) − T(N,i) = T(N−1, j) = coefficient of xⁱyʲ/(i!j!) in G(y,x). Hence

    (∂ₓ − ∂ᵧ) G(x,y) = G(y,x),     G(0,y) = A(y),     G(x,0) = B(x).          (1)

Conversely, (1)'s first two equations determine all coefficients of G by induction on i+j
(T(N,0) is given and T(N,i+1) = T(N,i) + T(N−1,j)), so (1) has a unique solution.
Let s = x+y, t = x−y, P(y) = A(y)/(cos(y/2) − sin(y/2)) (invertible: constant term 1), and

    G*(x,y) = P(x+y)·(cos(t/2) + sin(t/2)).

Since ∂ₓ−∂ᵧ kills functions of s and acts as 2∂_t on functions of t,
(∂ₓ−∂ᵧ)G* = P(s)(cos(t/2) − sin(t/2)) = G*(y,x) (swapping x,y sends t ↦ −t).
Also G*(0,y) = P(y)(cos(y/2) − sin(y/2)) = A(y). By uniqueness G = G*, so
B(x) = G(x,0) = A(x)·(cos(x/2)+sin(x/2))/(cos(x/2)−sin(x/2)) = A(x)(1+sin x)/cos x = (S+Θ)A. ∎

(This is the MSY theorem; the closed form of G is checked coefficientwise in `check.py`.)

### Step 2: the two triangles are two interleaved standard boustrophedons

T1-row n uses only T2-row n−1, and T2-row n uses only T1-row n−1 (its boundary value T1(n−1,n−1) included).
So the rows split into two independent *chains*:

* chain P: T1-rows with n odd and T2-rows with n even;
* chain Q: T1-rows with n even and T2-rows with n odd.

In a chain, row n (length n) is read along its arrow — T1 left→right, T2 right→left — and given index N = n−1:

    T(N,i) = T1(n, i+1)   (T1-row),        T(N,i) = T2(n, n−i)   (T2-row),   0 ≤ i ≤ N.

Then T1(n,i+1) = T1(n,i) + T2(n−1,i) reads T(N,i) = T(N,i−1) + T(N−1, N−i) (as T2(n−1,i) = T(N−1,(n−1)−i)), and
T2(n,n−i) = T2(n,n−i+1) + T1(n−1,n−i) reads the same (as T1(n−1,n−i) = T(N−1,n−i−1) = T(N−1,N−i)).
So each chain is a standard boustrophedon (Lemma) with outputs
b_N = T(N,N) = T1(n,n) on T1-rows, T2(n,1) on T2-rows, and inputs

    a_N = c(N+1)                       on T1-rows,
    a_N = T2(n,n) = T1(n−1,n−1) = b_{N−1}  on T2-rows with N ≥ 1,    a₀ = T2(1,1) = c(0) (chain Q).

The self-reference a_N = b_{N−1} is harmless: it only involves earlier outputs, so (a_N) is a well-defined
sequence and the Lemma applies to it.

### Step 3: solving each chain

Write C = C_e + C_o (even/odd parts), and E[·], O[·] for even/odd parts of a series. Note ∫₀ˣ E[F] has
x^N/N!-coefficient b_{N−1} for N odd, and ∫₀ˣ O[F] has it for N even ≥ 2.

*Chain P* (T1-rows ⇔ N even, T2-rows ⇔ N odd): A = E[C′] + ∫E[F] = C_o′ + ∫E[F], and F = (S+Θ)A.
*Chain Q* (T1-rows ⇔ N odd, T2-rows ⇔ N even): A = c(0) + O[C′] + ∫O[F] = c(0) + C_e′ + ∫O[F], F = (S+Θ)A.

Each of these equations F = (S+Θ)(known + ∫(part of F)) has a unique solution in Q[[x]] (the coefficient of x^N
on the right involves only coefficients of F of index < N). Claim: the solution is F = (D(S+Θ))′, with D = C_o
for P and D = C_e for Q. Indeed, for this F, the parity parts are E[F] = (C_o S)′ in chain P and O[F] = (C_e S)′
in chain Q (S even, Θ odd), so ∫E[F] = C_o S (C_o(0)=0) and c(0) + ∫O[F] = C_e S (C_e(0)=c(0)). Thus both
equations reduce to the identity

    (S+Θ)(D′ + D S) = D′(S+Θ) + D(S² + SΘ) = D′(S+Θ) + D(Θ′ + S′) = (D(S+Θ))′.   ✓

### Step 4: reading off

For a T1-row (n = N+1), T1(n,n) = b_N = N![x^N] (D(S+Θ))′ = n! [xⁿ] D(S+Θ). In chain P such n are odd and D = C_o,
in chain Q they are even and D = C_e; in both cases the parity of n makes n![xⁿ] D(S+Θ) = n![xⁿ] D S = n![xⁿ] C S
(the other products have the wrong parity). Precisely: n odd ⇒ [xⁿ]C_o(S+Θ) = [xⁿ]C_oS = [xⁿ]CS;
n even ⇒ [xⁿ]C_e(S+Θ) = [xⁿ]C_eS = [xⁿ]CS. Likewise for a T2-row, T2(n,1) = n![xⁿ] D(S+Θ): n even in P gives
[xⁿ]C_oΘ = [xⁿ]CΘ, n odd in Q gives [xⁿ]C_eΘ = [xⁿ]CΘ. ∎

**Remark.** The proof gives more: in chain P (resp. Q) the whole triangle is the MSY triangle of the input
A = D′ + D·sec x, and the rows of T1/T2 are the Seidel–Entringer rows; e.g. with C = 1 (c(n)=0 for n≥1, c(0)=1),
chain Q has A = sec x, and its rows are Entringer-type rows giving T1(n,n) = E_n for n even, T2(n,1) = E_n for n odd
(Euler zigzag numbers), chain P being identically 0.

## Numerical checks (`python3 check.py`, exact integers / Fractions, < 1 s)

* Python triangles = literal transcription of PARI `list3`, n ≤ 60.
* T1(n,n) = A003701(n), T2(n,1) = A009739(n) for 1 ≤ n ≤ 60 (series computed independently via 1/cos, sin/cos).
* Generalised version: 6 random c (entries up to 10⁶ in absolute value, signs mixed), 3 with c(0)=1 and 3 with random c(0): all pass, n ≤ 60.
* Lemma (MSY) for random a, N ≤ 63; bivariate closed form G = P(x+y)(cos+sin)((x−y)/2) checked coefficientwise for total degree ≤ 14.
* Chain decomposition: for random c, each chain reproduces exactly the standard boustrophedon triangle of its first column;
  the a_N rule; F = (D(sec+tan))′; A = D′ + D sec — all for N < 60.
* Key identity (sec+tan)(C′ + C sec) = (C(sec+tan))′ for random C.

## Art export

`triangles.json`: `T1`, `T2` = rows n = 1..16 (row n has n entries, k = 1..n), c ≡ 1; `order` = 272 triples
[triangle, n, k] in computation order (PARI order: T1(1,1), T2(1,1); then for each n: T2(n,n), T1(n,1..n), T2(n,n−1..1)).
Chain membership: (T1, n odd) ∪ (T2, n even) is chain P, the rest chain Q; each chain is a single boustrophedon path.
