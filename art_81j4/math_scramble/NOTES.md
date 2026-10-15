# Z×Z-scrambling (MathOverflow 516046)

Question: is there f: Z×Z → Z such that for every k, the maps
h_k(z)=f(z,k) (rows), v_k(z)=f(k,z) (columns) and the diagonal maps d_k are bijections Z → Z?

**Answer: yes, and there is a fully explicit example** (§2). There is also a soft existence proof (§1), and it works for any finite set of directions.

## 0. The two readings of d_k

* **Literal reading**, d_k(z)=f(z+k,z+k). This is z ↦ f(z,z) shifted by k, so the condition only asks that the
  main diagonal z ↦ f(z,z) is a bijection. Any solution of the intended version (taken at k=0) satisfies it, so the
  answer is yes here too. For example, §2 gives f(z,z)=z+g(z)=h(z), which is a bijection.
* **Intended reading**, d_k(z)=f(z+k,z). Every diagonal {x−y=k} must be a bijection onto Z. The rest of these notes
  use this reading. The bonus case adds anti-diagonals {x+y=k}.

## 1. Existence by back-and-forth

Fix a finite set D of directions (for example rows, columns, diagonals and anti-diagonals). A *line* is a translate of one of these
directions. Two facts are used:

(a) two distinct lines meet in at most one cell;
(b) every cell lies on exactly |D| lines.

A *partial scrambling* is a finite partial map p: Z² ⇀ Z that is injective on every line.

Enumerate all requirements in one ω-sequence (there are countably many):

* C_c: "cell c receives a value", one for each c ∈ Z²;
* V_{L,v}: "value v occurs on line L", one for each line L and each v ∈ Z.

Start with p_0 = ∅ and meet the n-th requirement at step n.

**Cell step (C_c).** If c already has a value, do nothing. Otherwise c lies on |D| lines, and each of them carries only finitely many values of p.
So some v ∈ Z is unused on all of them. Set p(c)=v. Injectivity holds on the lines through c, and no other line changes.

**Value step (V_{L,v}).** If v already occurs on L, do nothing. Otherwise call a cell c ∈ L *bad* if it already has a value,
or if some line L' ≠ L through c already contains v. Only finitely many cells are bad:

* dom(p) is finite.
* v occurs at finitely many cells u. For each such u and each of the |D|−1 other directions there is one line
  through u in that direction, and by (a) it meets L in at most one cell.

L is infinite, so it has a good cell c. Set p(c)=v. Then v is new on L by assumption and new on every other line through c
because c is good, so p stays injective on every line.

Let f = ⋃ p_n. Every C_c is met, so f is total. Every finite stage is injective on lines, so f is too. Every V_{L,v} is met,
so f is surjective on every line. Hence every line map is a bijection. ∎

Remarks.
* The key point is that a finite partial assignment blocks only finitely many values at a cell and finitely many cells
  on a line. This is where finitely many directions is needed. With *all* rational slopes, every cell of L would
  be collinear with an existing v-cell, and the value step would fail.
* `backforth.py` implements exactly this construction. It interleaves cell steps in spiral order with value
  steps (F,k,v) enumerated by max(|k|,|v|), and it checks the invariant. 20 000 rounds
  give about 21 000 cells, injective on every line. The value-placing cells stay within about 135 of the origin (about 100 with anti-diagonals).

## 2. An explicit solution

**Reduction.** Try f(x,y) = x + g(y). Then

* row y=k: x ↦ x+g(k) is a translation, so a bijection;
* column x=k: y ↦ k+g(y) is a bijection ⇔ g is a bijection;
* diagonal x−y=k: y ↦ f(y+k,y) = k + (y+g(y)) is a bijection ⇔ h(y)=y+g(y) is a bijection.

So it is enough to find a **complete mapping (orthomorphism) of Z**: a permutation g with y+g(y) also a permutation.

Linear maps fail. f=ax+by needs a,b,a+b ∈ {±1}, which is impossible. Likewise g(y)=cy needs c, 1+c ∈ {±1}.

Piecewise-affine maps on residue classes (RCWA maps) work. A computer search (`rcwa_search.py`) over
g(mt+r) = a_r t + b_r found **no solution with modulus m ≤ 4** (for |a_r| ≤ 12). It found these solutions with **m = 5**:

```
y = 5t + r      g(y)        h(y) = y + g(y)
r = 0           4t          9t
r = 1           4t + 2      9t + 3
r = 2          −8t + 5     −3t + 7
r = 3           4t + 3      9t + 6
r = 4          −8t + 1     −3t + 5
```

* Images of g: 0, 2, 3 (mod 4) and 5, 1 (mod 8). This is an exact cover of Z, so g is a bijection.
* Images of h: 0, 3, 6 (mod 9) and 1, 2 (mod 3). This is an exact cover of Z, so h is a bijection.

So

  **f(x,y) = x + g(y), with g as above, is a Z×Z-scrambling** for rows, columns and diagonals. (Proof: the two exact
covers above. Also checked numerically in `explicit.py`.)

A small modulus is needed. In general an RCWA g with slopes a_r/m is a bijection only if Σ 1/|a_r| = 1, and h is a bijection only if
Σ 1/|m+a_r| = 1. Here 1/4+1/4+1/8+1/4+1/8 = 1 and 1/9+1/9+1/3+1/9+1/3 = 1.

**Anti-diagonals.** With f=x+g(y), the anti-diagonal x+y=k gives z ↦ k + (g(w) − w) with w=k−z. So g must also make g−id a
bijection, i.e. g must be a *strong* complete mapping. The m=5 example fails this condition. A strong complete mapping of Z exists by the 1-D
version of §1. I did **not** find a strong RCWA one: `rcwa_strong.py` (|a_r| ≤ 40, all moduli dividing 2520) finds none with modulus m ≤ 4. The m=5 case did not finish within the time budget. For all four directions,
existence comes from §1 and from the spiral greedy of §3 (empirically).

## 3. Spiral greedy fills (`greedy.c`)

Cells are filled ring by ring in spiral order around the origin. Each cell gets the integer of smallest |v| (ties: 0,1,−1,2,−2,…)
that is not yet used on any constrained line through it. In spiral order, the values in [−R,R]² depend only on that square,
so a finite run gives exactly the restriction of a well-defined infinite f. Saved arrays (int64, index [y+R, x+R], R=255):

* `f_window.npy`: rows+cols+diagonals (the question's constraints)
* `f_rc.npy`: rows+cols only
* `f_rcda.npy`: rows+cols+diagonals+anti-diagonals

Larger runs use R=1500 (`g*_big.bin`). The fill is injective on its constrained lines by construction. The real question is surjectivity.

### (i) rows+cols+diagonals greedy is NOT a scrambling
Every 0 lands on the anti-diagonal x+y=0, i.e. f(−y,y)=0 (checked for all |y| ≤ 1500).
Take row y with |y| ≤ 1500. Its only 0 is at (−y,y). So a cell (y+k, y) on diagonal k with k odd can never be 0, even in the
infinite fill. In particular **diagonal x−y=1 has no 0 at any cell with |y| ≤ 1500.**
Other small values are also permanently missing from central diagonals: diagonal 2 lacks ±1, diagonal 3 lacks −1,0,1, diagonal 6 lacks
−3,−2,1,2,3. The missing sets are the same at R=255 and R=1500.
So the pure greedy does not solve the problem, and the value-placing steps of §1 are needed. Growth: max|f| on ring r ≈ 1.49 r.

### (ii) rows+cols greedy: a dyadic, nim-like closed form
max|f| on ring r is **exactly 2^{⌊log₂ r⌋+1}** (r ≥ 1, checked up to r=1500). Zeros lie exactly on x=y.
Write σ(v) = 2v−1 (v>0), −2v (v≤0), so σ: Z → N is 0,1,−1,2,−2,… ↦ 0,1,2,3,4,…. Set X=x−1, Y=y−1, K = X xor Y
(two's complement) and j = ⌊log₂ K⌋. Then on the two same-sign quadrants (x,y ≥ 1 or x,y ≤ 0):

  σ(f(x,y)) = 0 if K=0; otherwise 2^{j+1}+K if "up", else 2^{j+2}−1−K,

where "up" means X>Y in the positive quadrant and X<Y in the negative quadrant. This matches all 4 503 001 such cells of the R=1500
window (`rc_formula.py`). The mixed-sign quadrants are not a function of (K, order) alone. They are probably the same
dyadic structure with a different encoding; I did not pin this down.

### (iii) rows+cols+diagonals+anti-diagonals greedy looks fine
Every value |v| ≤ 200 occurs on every line with |k| ≤ 50 in all four families (R=1500). Every |v| ≤ 100 shows up within distance
about 206 of the centre on each of those lines. Zeros are spread out (2113 of the 3001 central rows have their 0 inside the window), not
on a line. Growth: max|f| on ring r ≈ 1.57 r.

## 4. Conjectures (labelled as such)

**Conjecture A (rows+cols spiral greedy).** For the spiral-greedy fill with only row and column constraints, the
formula in §3(ii) holds on both same-sign quadrants for all x,y. The maximum of |f| on ring r is exactly 2^{⌊log₂ r⌋+1}.
(Evidence: exact agreement on 4.5 M cells and on all rings ≤ 1500.)

**Conjecture B (zeros of the rcd greedy).** In the rows+cols+diagonals spiral greedy, f(−y,y)=0 for all y. Consequently every odd
diagonal omits 0, so this greedy is not a scrambling. (Checked for |y| ≤ 1500.)

Open question (not claimed): is the rows+cols+diagonals+anti-diagonals spiral greedy a genuine scrambling? The data say "probably".
Is there an RCWA strong complete mapping of Z, giving an explicit 4-direction example?

## 5. Files
* `greedy.c`: spiral greedy (`./greedy R mode out.bin`, mode 0=rc, 1=rcd, 2=rcda). Prints max|f| per ring (`ring*.txt`).
* `analyze.py`, `missing.py`, `cov.py`, `zeros.py`, `nim.py`, `rc_formula.py`: analyses quoted above.
* `explicit.py`: the explicit f = x + g(y) and its verification.
* `backforth.py`: the §1 construction run for finitely many rounds.
* `rcwa_search.py`, `rcwa_search2.py`, `rcwa_strong.py`: searches for RCWA (strong) complete mappings.
