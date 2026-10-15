# Cayley's formula from the exponential formula (MO 516050)

Setup: G(x,y) = sum_{n>=0} x^n/n! (1+y)^{C(n,2)},  C(x,y) = log G = sum_{n,e} c_{n,e} x^n y^e / n!.
By the exponential formula c_{n,e} = #connected graphs on [n] with e edges. We want c_{n,n-1} = n^{n-2}.

## 1. The explicit alternating sum

Expanding log(1+F) = sum_k (-1)^{k-1} F^k / k with F = G - 1 and taking n! [x^n y^{n-1}]:

    A(n) = sum_{k>=1} (-1)^{k-1}/k  sum_{b_1+...+b_k = n, b_i>=1}  n!/(b_1!...b_k!) * binom( sum_i C(b_i,2), n-1 )

(sum over compositions of n). Grouping by set partitions pi of [n] instead:

    A(n) = sum_{pi partition of [n]} (-1)^{|pi|-1} (|pi|-1)!  binom( sum_{B in pi} C(|B|,2), n-1 ).

Replacing n-1 by n gives B(n), the count of connected unicyclic graphs.

Exact integer check (`verify.py`, uses Fractions; both forms agree):

| n | A(n) = n^{n-2} | B(n) (unicyclic) = A057500(n) |
|---|---|---|
| 1 | 1 | 0 |
| 2 | 1 | 0 |
| 3 | 3 | 1 |
| 4 | 16 | 15 |
| 5 | 125 | 222 |
| 6 | 1296 | 3660 |
| 7 | 16807 | 68295 |
| 8 | 262144 | 1436568 |
| 9 | 4782969 | 33779340 |
| 10 | 100000000 | 880107840 |
| 11 | 2357947691 | 25201854045 |
| 12 | 61917364224 | 787368574080 |
| 13 | 1792160394037 | 26667815195274 |
| 14 | 56693912375296 | 973672928417280 |

All match n^{n-2}, and the B column matches the OEIS b-file https://oeis.org/A057500/b057500.txt for n = 1..14.

I found no direct way (an involution or closed-form manipulation) to evaluate the alternating sum. The argument below avoids that by finding a differential equation the right-hand side satisfies.

## 2. A short argument using only the right-hand side

**Step 1 (an identity for G).** Each term satisfies (1+y) d/dy (1+y)^{C(n,2)} = C(n,2)(1+y)^{C(n,2)}, and C(n,2) x^n = (x^2/2) d^2/dx^2 x^n. So

    (1+y) G_y = (x^2/2) G_xx.

**Step 2 (move to C = log G).** G_y = C_y G and G_xx = (C_xx + C_x^2) G, so

    (1+y) C_y = (x^2/2) (C_xx + C_x^2).                                  (PDE)

**Step 3 (compare coefficients).** Take the coefficient of x^n y^e / n! on both sides:

    (e+1) c_{n,e+1} = (C(n,2) - e) c_{n,e} + (1/2) sum_{k=1}^{n-1} C(n,k) k(n-k) sum_{a+b=e} c_{k,a} c_{n-k,b}.     (*)

Setting y = 0 gives log G(x,0) = log e^x = x, so c_{n,0} = [n=1].

**Step 4 (nothing below n-1 edges).** By induction on n, then on e, (*) gives c_{n,e} = 0 for e < n-1. The convolution term needs a >= k-1 and b >= n-k-1, so it is zero unless e >= n-2. (This also follows from the left-hand side: a connected graph has at least n-1 edges.)

**Step 5 (the tree recurrence).** Put e = n-2 in (*). The first term on the right vanishes because c_{n,n-2} = 0. With t_n := c_{n,n-1}:

    (n-1) t_n = (1/2) sum_{k=1}^{n-1} C(n,k) k t_k (n-k) t_{n-k},   t_1 = 1.

This is the "delete an edge from a tree" double count. It is the recurrence of Shukla, arXiv:0908.2324, here derived from the right-hand side alone. In EGF form, with T(u) = sum t_n u^n/n!, it reads

    u T' - T = (u^2/2) T'^2.

**Step 6 (solve).** Differentiate and divide by u to get T'' = T'^2 + u T' T''. Put R = uT' (so r_n = n t_n). Then

    R' = R / (u(1-R)),

so (R e^{-R} / u)' = e^{-R}(R'(1-R) u - R)/u^2 = 0. A formal power series with zero derivative is constant, and R = u + O(u^2), so

    R = u e^R.

Lagrange inversion gives r_n = n! (1/n)[w^{n-1}] e^{nw} = n^{n-1}, hence t_n = n^{n-2}.

Alternatively, check directly that t_n = n^{n-2} satisfies the recurrence. This is Abel's identity sum_k C(n,k) k^{k-1}(n-k)^{n-k-1} = 2(n-1) n^{n-2} (checked for n < 30 in `pde_check.py`).

**Why this counts as "easy".** It uses only the shape of the right-hand side (Step 1 is a one-line identity), the exponent n-1 is forced (Step 4), and the final step is a separable first-order ODE plus standard Lagrange inversion. The extraction at x^n y^{n-1} is done through (*) rather than through the alternating sum. Steps 1–5 and the agreement of every coefficient c_{n,e} with (*) were checked by computer: (*) for n <= 10, the PDE for C up to x^11 (`pde_check.py`).

**The same thing as a scaling limit** (the question's "x = X/t" idea). Let W(u,y) := y C(u/y, y) = sum_n u^n/n! sum_e c_{n,e} y^{e-n+1}. By Step 4 this is a power series in y with W(u,0) = T(u). The PDE becomes

    (1+y)(u W_u - W + y W_y) = (u^2/2)(y W_uu + W_u^2),

and setting y = 0 gives Step 5's ODE. Flajolet, Salvy and Schaeffer make this scaling analytic: they take Q(z,q) = -q log G(-z/q, -q) for q -> 0+ and apply the saddle-point method to an integral representation. That is rigorous but much heavier than the formal ODE above.

## 3. The inversion-enumerator route

Gessel and Wang (depth-first search) show sum over connected graphs on [n] of q^{e-n+1} = I_n(1+q), the Mallows–Riordan inversion enumerator. FSS state this as U(z,1+q) = Q(z,-q). So [y^{n-1}] C_n(y) = I_n(1) = #trees.

That only re-proves "coefficient = number of trees", which the left-hand side of the exponential formula already says. Getting n^{n-2} still needs the generating function of I_n, so I don't think this route answers the question as asked.

## 4. Observation: the higher orders (Wright's hierarchy)

Write W = sum_{j>=0} y^j V_j, where V_0 = T and V_j is the EGF of connected graphs with excess e - n = j - 1. Comparing powers of y in the scaled PDE gives, for j >= 1, a *linear* first-order ODE:

    u(1-R) V_j' + (j-1) V_j = (u^2/2)(V_{j-1}'' + sum_{a+b=j, 1<=a,b<=j-1} V_a' V_b') - u V_{j-1}' - (j-2) V_{j-1}.

This is essentially Wright's differential recurrence. For j = 1 it gives U' = R^3 / (2u(1-R)^2), whose solution is

    U = (1/2) log(1/(1-R)) - R/2 - R^2/4.

That is Rényi's unicyclic formula, and it matches A057500 for n <= 14. The next excess (e = n+1) is R^4(6-R)/(24(1-R)^3), Wright's formula; it matches the computed c_{n,n+1} for n <= 11.

All of this is consistent with the literature. I am not claiming anything new; the only novelty is the presentation, which goes straight from the (1+y)∂_y = (x^2/2)∂_x^2 identity to Cayley's formula.

## References (links checked)
- P. Flajolet, B. Salvy, G. Schaeffer, *Airy phenomena and analytic combinatorics of connected graphs*, Electron. J. Combin. 11(1) (2004) #R34. https://www.combinatorics.org/ojs/index.php/eljc/article/view/v11i1r34. Uses exactly C = log(1 + sum (1+q)^{C(n,2)} z^n/n!), the scaling Q(z,q) = -q log H, and the saddle-point method. Cites Gessel–Wang for U(z,1+q) = Q(z,-q).
- A. B. Shukla, *A short proof of Cayley's tree formula*, arXiv:0908.2324. https://arxiv.org/abs/0908.2324. The recurrence from Step 5.
- C. L. Mallows, J. Riordan, *The inversion enumerator for labeled trees*, Bull. AMS 74 (1968) 92–94. https://www.ams.org/bull/1968-74-01/S0002-9904-1968-11888-9/
- I. Gessel, D. L. Wang, *Depth-first search as a combinatorial correspondence*, JCTA 26 (1979) 308–313. Cited via FSS; I did not open it.
- S. Janson, D. E. Knuth, T. Łuczak, B. Pittel, *The birth of the giant component*, RSA 4 (1993). Cited via FSS for Wright's equations; I did not open it.
- OEIS A057500: https://oeis.org/A057500
- I could not open the MathOverflow page itself (mathoverflow.net is blocked for the fetch tool), so I have not seen its existing answers.

## Files
- `verify.py`: exact A(n), B(n) via compositions and set partitions; checks (*) and that c_{n,e} = 0 for e < n-1.
- `pde_check.py`: sympy check of the PDE, the tree ODE, the Abel identity, the unicyclic formula and the excess-1 formula.
