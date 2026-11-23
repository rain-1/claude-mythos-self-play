# Two fifths — notes on MO 164092, ∏ (p²−1)/(p²+1) = 2/5

Everything here is elementary; what is proved, what is only computed and what is conjecture is marked.

## 1. Three readings of the same number (proved, all by Euler products)

* **Land.** Cut the square of side ζ(2) by lines at the partial sums of Σ1/n², both ways. Field (m,n) is
  1/m² × 1/n², area 1/(mn)². The square fields have area ζ(4), so they are ζ(4)/ζ(2)² = **2/5** of the land.
* **Shapes.** Fields (ka,kb), gcd(a,b)=1, are similar; the shape a:b holds (2/5)/(ab)² of the land, hence
  Σ_{gcd(a,b)=1} 1/(ab)² = 5/2 = ∏ (p²+1)/(p²−1).
* **Signs.** With λ the Liouville function, Σ_{gcd(a,b)=1} λ(ab)/(ab)² = ∏ (p²−1)/(p²+1) = 2/5, because
  n ↦ 2^ω(n) and n ↦ λ(n)2^ω(n) are Dirichlet inverses. So the two sums are reciprocal, and
  fields with λ(mn)=+1 hold (1 + (2/5)²)/2 = **29/50** of the land (20/50 square + **9/50**), fields with λ(mn)=−1 hold **21/50**.
  In general: (even share) − (odd share) = (square share)².
* Same for three numbers: of all boxes 1/l² × 1/m² × 1/n², cubes are 8/35 of the volume, boxes with exactly
  two equal sides 18/35, the rest 9/35. With exponent 4: squares are 6/7; exponent 6: 691/715.
* As a probability: pick m, n independently with P(n) ∝ 1/n². P(m = n) = 2/5, P(m/n = a/b) = (2/5)/(ab)²,
  P(gcd = g) = (90/π⁴)/g⁴.

`check.py` confirms each number numerically.

## 2. Zagier's function is the width of a branch (proved)

f(a,b) = 1/(ab³) + 1/(2a²b²) + 1/(a³b) satisfies f(a,b) − f(a+b,b) − f(a,a+b) = 1/(ab)² (this is the
identity in Zagier's proof of 2ζ(2)² = 5ζ(4), quoted in the MO answers). Since f → 0 along the tree,

> **f(a,b) = the total of 1/(mn)² over (a,b) and all its descendants in the Calkin–Wilf tree**
> (children (a+b,b) and (a,a+b)); i.e. over all pairs from which Euclid's subtraction algorithm passes through (a,b).

So a tree whose branches obey Leonardo's rule (branch = leaf + two shoots) has trunk 5/2 = 1 + 3/4 + 3/4,
and for two zeta(2)-random integers **the probability that Euclid's algorithm passes through the ratio a:b is
the rational number (2/5)·f(a,b)**: 3/10 for 1:2, 23/135 for 1:3, 4/135 for 2:3, 83/16875 for 3:5.
(`check.py`: subtree sums by brute force agree to 6 digits.)

## 3. Where the telescoping stops (computed; conjecture)

`telescope.py` solves the linear system for a homogeneous f = Σ c_j /(m^j n^(2s−j)) with
f(m,n) − f(m+n,n) − f(m,m+n) = 1/(mn)^s:

| s | solution | Σ c_j |
|---|---|---|
| 2 | 1/(mn³) + 1/(2m²n²) + 1/(m³n) | 5/2 |
| 3 | none | |
| 4 | 1/(3m³n⁵) + 1/(2m⁴n⁴) + 1/(3m⁵n³) | 7/6 = ζ(4)²/ζ(8) |
| 5, 6, 7 | none | |

So with exponent 4 the branch widths are again rational (f₄(1,3) = 29/1458, …; `subtree6.py 4` agrees to 19 digits).
At s = 6 the trunk is still rational, 715/691, and so is the first branch (12/691, by symmetry), but there is no
homogeneous f, and numerically (`rational6.py`, 31 digits)

    F₆(1,3) = 0.001718430530656794678700859648…,   F₆(3,2) = 0.0000227055040754773907636844903…

have no rational form with denominator below ~10¹⁵ (no large partial quotient in 37 terms), and no integer
relation with 1, ζ(3)ζ(9)/ζ(12), ζ(5)ζ(7)/ζ(12) with coefficients below 10⁷.

**Conjecture.** For s = 6 the Calkin–Wilf subtree sums F₆(a,b), (a,b) ∉ {(1,1),(1,2),(2,1)}, are irrational.
The homogeneous equation f(m,n) = f(m+n,n) + f(m,n+m) in degree −2s is Lewis's three-term equation, and weight
12 = 2s is where the first cusp form lives, so the natural guess is that the new constant is a period of Δ.
Not tested against L(Δ,k). (s = 8, 10 not run.)

## 4. The prime shell (proved, plus one computation)

(p²−1)/(p²+1) = cos θ_p with tan(θ_p/2) = 1/p: the angle of the right triangle (p²−1, 2p, p²+1).
Projecting a unit segment onto a line turned by θ₂, then θ₃, θ₅, … leaves ∏ cos θ_p = 2/5. The feet of the
perpendiculars are rational points; they spiral inwards onto the circle of radius 2/5 without reaching it, and
since Σθ_p diverges (like 2 log log p + 0.4208) the spiral turns for ever. `turn.py` (sieve, long double):

| turn | first prime at which it is complete | index | radius there |
|---|---|---|---|
| ¼ | 3 | 2 | 0.48 |
| ½ | 43 | 14 | 0.403479… |
| ¾ | 5119 | 685 | 0.400016… |
| 1 | 141,634,651 | 7,999,137 | 0.4000000003 |

The second turn ends near e^433.9 ≈ 10¹⁸⁸ (from the asymptotic, not computed).
Remark: this gives nothing new about *why* the limit is rational; it is a picture of the product, not a proof.
