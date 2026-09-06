# Multiple zeros of the moment polynomials Q_n(x) = E[(x+X)^n]  (MO 514900)

**Question (MO 514900).** For a non-degenerate real random variable X with all moments,
must Q_n(x) = E[(x+X)^n] = Σ C(n,k) m_k x^{n−k} have only simple zeros?  The poster found
none among 24 laws and degrees 2 ≤ n ≤ 60.  An answer (score 11) gives one counterexample:
Y ≥ 0 with E Y = 1/3, E Y² = 1, X = ±√Y with a fair sign, so Q_4 = (x²+1)².

**What is added here** (`appell.py`, `appell_double_points.json`): the smallest degree that can
fail is exactly n = 4, and every degree n ≥ 4 fails, with an explicit rational-or-trigonometric
family and the exact location of the double zeros.

## The family

Take X ∈ {−1, 0, 1} with P(X = ±1) = q, P(X = 0) = 1 − 2q, 0 < q ≤ 1/2.  Then

    Q_n(x; q) = q[(x−1)^n + (x+1)^n] + (1−2q) x^n .

Put u = 1/x and f_n(u) = (1+u)^n + (1−u)^n (an even polynomial with real coefficients).
Dividing by q x^n,

    Q_n(x; q) = 0   ⇔   f_n(u) = −(1−2q)/q =: c,   c ∈ (−∞, 0).

So as q runs from 0 to 1/2 the zeros run along the **roads** f_n^{−1}((−∞, 0]) in the u-plane
(inverted to the x-plane), from u = ∞ (x = 0: the constant law, all n zeros at the origin) to
the zeros of f_n on the imaginary axis (x = i cot(π(2j+1)/(2n)), q = 1/2).  A double zero of Q_n
is exactly a point where a road passes through a critical point of f_n:

    f_n'(u) = n[(1+u)^{n−1} − (1−u)^{n−1}] = 0  ⇔  (1+u)/(1−u) = e^{2πik/(n−1)}
                                              ⇔  u = i tan(πk/(n−1)),  k = 1..n−2,

and there  f_n(u) = 2 (−1)^k cos(πk/(n−1))^{1−n}.  This is negative exactly when
(−1)^k cos(πk/(n−1)) < 0 (k odd and k < (n−1)/2, or its mirror n−1−k), giving

**Theorem.**  For every n ≥ 4 and every k with (−1)^k cos(πk/(n−1)) < 0, the law above with

    q_{n,k} = 1 / ( 2 + 2 |cos(πk/(n−1))|^{1−n} )        (always < 1/4)

has Q_n with a double zero at  x = ∓ i cot(πk/(n−1))  (a conjugate pair).  In particular k = 1
works for all n ≥ 4 (it needs 1 < (n−1)/2).  For n ≤ 3 no non-degenerate law has a multiple zero:
normalising m₁ = 0, Q₂ = x² + m₂ has zeros ±i√m₂ and Q₃(±i√m₂) = m₃ ± 2i m₂^{3/2} ≠ 0
(Res(Q₂, Q₃) = 4m₂³ + m₃² > 0).  Multiple zeros of Q_n for n ≥ 4 are never real (the poster's
remark), and in this family they are never higher than double: Q_n''(x₀) ≠ 0 at all 380 points
n ≤ 40 (`verify_exact`, 60-digit evaluation: |Q|, |Q'| < 4e−149, |Q''| ≥ 1.6e−50 — the smallest
|Q''| is the k = 1 point of n = 40 where cot is large).

First cases (exact):

| n | k | q | double zeros | Q_n |
|---|---|---|---|---|
| 4 | 1 | 1/18 | ±i/√3 | (3x²+1)²/9 |
| 5 | 1 | 1/10 | ±i | x (x²+1)² |
| 6 | 1 | 1/(2+2cos⁻⁵(π/5)) = 0.12869 | ±i cot(π/5) = ±1.3764i | — |
| 7 | 1 | 2/(2+2·(2/√3)⁶)=27/182 = 0.14835 | ±i√3 | — |
| 8 | 1, 3 | 0.16260, 1.3507e−5 | ±2.0765i, ±0.2282i | two double pairs at different q |

The n = 4 case is the answer's example rescaled: X = ±√3 w.p. 1/18 each, 0 w.p. 8/9 gives
E[(x+X)⁴] = (x²+1)²; ours is X = ±1 w.p. 1/18, 0 w.p. 8/9, (3x²+1)²/9.

Counting: degree n has exactly **⌊n/4⌋ collision parameters q_{n,k}** (each producing a conjugate
pair of double zeros), so 2⌊n/4⌋ double points; for n = 4..40 that is Σ 2⌊n/4⌋ = 380, all
verified.  For n ≡ 0 mod 4 every zero of Q_n takes part in a collision (n/2 mirror pairs, n/4
values of q, each pair of q-events accounting for 4 zeros); for the other residues the remaining
zeros sit on the imaginary axis from the start (the roads that leave the origin along the axis,
arg u = ±π/2, plus the permanent zero x = 0 when n is odd).

## Degree 4 exactly: skewness 0 and kurtosis 9

A real quartic with a non-real double zero x₀ also has x̄₀ double, so it is the square of a real
quadratic.  Writing Q₄ = (x² + bx + c)² and comparing with Q₄ = x⁴ + 4m₁x³ + 6m₂x² + 4m₃x + m₄
after centering (m₁ = 0) gives b = 0, c = 3m₂, m₃ = 0, m₄ = 9m₂².  Hence

**Theorem (n = 4).**  Q₄(x) = E[(x+X)⁴] has a multiple zero  ⇔  X has skewness 0 and
kurtosis μ₄/μ₂² = 9;  then Q₄ = ((x+μ₁)² + 3μ₂)² with double zeros −μ₁ ± i√(3μ₂).

Check: the answer's law has μ₂ = 1/3, μ₄ = 1 = 9·(1/3)²; ours has μ₂ = μ₄ = 2q = 1/9.  Every
asymmetric three-atom solution found by Newton search (`appell_asym.py`, 6 atom triples × 400
starts) has skewness 0 and kurtosis 9.000 to the printed precision, and for n = 4 exactly ONE
weight vector per atom triple satisfies the two conditions (400 random starts, one solution).
For n = 5 the same factorisation Q₅ = (x−ρ)(x² + bx + c)² forces ρ = 2b and, for a symmetric law,
b = 0, ρ = 0, c = 5μ₂ and the single condition **μ₄ = 5μ₂²** (kurtosis 5; the q = 1/10 law has
μ₂ = 1/5, μ₄ = 1/5).

**Codimension explains the poster's null result.**  A non-real common zero of two real
polynomials is two real conditions on their coefficients (the conjugate is forced along), not
one: multiple zeros of Q_n form a codimension-2 subset of the space of moment sequences, so a
one-parameter family of laws generically never meets it — the 24 laws × 59 degrees could not have
found one by accident.  For symmetric laws one condition (odd moments = 0) is automatic and the set
becomes codimension 1: a one-parameter symmetric family crosses it at isolated parameter values,
which is what the roads picture shows (⌊n/4⌋ crossings per degree for the three-atom family).
For three atoms with general weights the solutions are isolated points of the 2-simplex, and
the double zeros sit OFF the imaginary axis (e.g. atoms {−1,0,1}, n = 6, weights (0.0154, 0.9833,
0.0014) on (1, 0, −1): double zeros at −0.2595 ± 0.3050i).

## What it means for the question

* "Simple zeros for all n" is false already at the smallest possible degree, and false for
  every n ≥ 4, by three-atom symmetric laws with very light tails (q < 1/4).
* The mechanism is generic: the zeros of Q_n(·; q) move continuously with q from the origin to
  the imaginary axis, and a mirror pair (x, −x̄) can only reach the axis by meeting on it — every
  such meeting is a double zero.  So for ANY one-parameter family of laws joining the constant
  law to a law all of whose Q_n-zeros are purely imaginary, double zeros are forced (in degree n
  as soon as the number of off-axis zeros is positive at the start).  This suggests the
  right question is not existence but *frequency*: how large is the set of laws (in the moment
  simplex) with a multiple zero in degree n?  Here it is a codimension-1 set (one real equation:
  the resultant Res(Q_n, Q_{n−1}) = 0 — real, since the resultant is real and a double zero comes
  with its conjugate), so it is a hypersurface that separates the space of laws into chambers
  labelled by how many zeros are on the imaginary axis.

**Conjecture.**  For every n ≥ 4 and every set of m ≥ 3 real atoms, the weight vectors in the
open simplex for which Q_n has a multiple zero form a non-empty set of dimension m − 3 (isolated
points for m = 3, whose number grows with n: 1, 1, 2–3, 3–6 for n = 4, 5, 6, 8 in the search
above), and for n = 4, 5 there is exactly one such weight vector per atom triple.  For n = 4 the
first claim is the theorem (two equations, skewness = 0 and kurtosis = 9, on the (m−1)-simplex;
non-empty because kurtosis ranges over an interval containing 9 whenever m ≥ 3 and the
skewness-0 slice is non-empty).

## Files
* `appell.py` — family, closed forms, 60-digit verification of all 380 double points n ≤ 40, sympy
  proof of the n ≤ 3 case.  * `appell_double_points.json` — the list.
* `appell_asym.py` → `appell_asym.json` — Newton search over asymmetric three-atom laws (atoms
  {0, 1, a}): isolated double-zero laws for every a tried, all with kurtosis 9 at n = 4.
* `render_appell.py` → `appell_2560.png` — the roads for n = 4..14 and the 56 double points in the
  window |x| ≤ 4.6, the pale region where any law on {−1,0,1} can place a zero of degree n
  (0 ∈ conv{(x−1)^n, x^n, (x+1)^n}).
