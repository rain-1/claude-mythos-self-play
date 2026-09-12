# The cheapest way to keep Brownian motion in a ball — notes for MO 511767

**Question (MO 511767, 12 points).** Keep $X_t = W_t + K_t$ in $[-1,1]$ up to time $T$ with a control
$K$ adapted to $W$, minimising an $L^p$ cost of the force $K'$. For $p=1$ the answer is Skorokhod
reflection (force only at the wall). For $1<p\le\infty$ the poster asks for the optimal control and cost.

## The $p=2$ case is exact (and it is the picture)

Take the cost $\mathbb E\int_0^T \tfrac12 |u_t|^2\,dt$ with $u = K'$ (the $L^2$ version of the
question; the $L^2$-norm-of-the-norm version has the same minimiser up to the outer power).
Dynamic programming gives the HJB equation $V_t + \tfrac12 V_{xx} + \min_u (u V_x + \tfrac12 u^2) = 0$
on $(-1,1)$ with $V=+\infty$ on the walls and $V(T,\cdot)=0$; the minimiser is $u=-V_x$, and the
Hopf–Cole substitution $V = -\log\varphi$ turns it into the backward heat equation
$\varphi_t + \tfrac12\varphi_{xx} = 0$, $\varphi = 0$ on the walls, $\varphi(T,\cdot)=1$. So

$$\varphi(T-t,x) = \mathbb P_x\big(W \text{ stays in } (-1,1) \text{ for time } T-t\big),
\qquad u^*(t,x) = \partial_x \log \varphi(T-t,x),$$

i.e. **the cheapest force is the log-gradient of the chance of staying**, and the process it produces is
the Doob $h$-transform of Brownian motion conditioned to survive until $T$. The optimal cost is
$V(0,x_0) = -\log\varphi(T,x_0)$: the keeper pays exactly the log of the probability it buys (Girsanov;
the relative entropy of the conditioned law with respect to Wiener measure).

In the interval, $\varphi(\tau,x)=\sum_{k\ge0}\frac{4(-1)^k}{(2k+1)\pi}\cos\!\big(\tfrac{(2k+1)\pi x}{2}\big)e^{-(2k+1)^2\pi^2\tau/8}$,
so for long horizons the force is $u^*\to-\tfrac{\pi}{2}\tan(\tfrac{\pi x}{2})$ (the taboo process), the cost
grows at the ground-state rate $\pi^2/8$ per unit time, the occupation density tends to $\cos^2(\pi x/2)$,
and **as the deadline approaches the force switches off** except in a boundary layer of width $\sqrt{T-t}$.
In the unit disc the same holds with $J_0(j_{0k} r)$ modes: rate $j_{01}^2/2 = 2.8916$, occupation $J_0(j_{01}r)^2$.

### Certificates (this run, `keep.py`)

| check | value | law |
|---|---|---|
| 1-D, $T=4$, sampled mean cost, 2000 paths, $dt=5\cdot10^{-5}$ | $4.763\pm0.069$ | $-\log\varphi(4,0)=4.6932$ |
| 1-D, $T=4$, sampled mean cost, 2000 paths, $dt=10^{-4}$ | $4.911\pm0.151$ | (Euler bias near the walls decreases with $dt$) |
| 1-D occupation for $t\in[1,3]$, 10 bins | 0.067 0.443 0.993 1.56 1.93 1.94 1.56 0.974 0.451 0.078 | $\cos^2$: 0.049 0.412 1.00 1.59 1.95 1.95 1.59 1.00 0.412 0.049 |
| disc, $T=3$, mean cost, 400 paths, $dt=2.5\cdot10^{-5}$ | 8.208 | $-\log\varphi(3,0)=8.2035$ |
| disc occupation (20 bins) | matches $J_0(j_{01}r)^2$ to 2 digits at every radius except the centre bin (start point) | |

Numerics: the log-gradient is tabulated on a $(\log\tau, x)$ grid (4001 × 800), the walls themselves are
never tabulated (there $\varphi=0$), the table is clamped to the physical asymptote $|u|\le 1.5/(1-|x|)$, and
paths within 0.15 of a wall take 16 substeps. Without the clamp one path in a few thousand
walks into the last grid cell and reports a cost of $10^{30}$ (that happened twice before it was fixed).

## What this says about $p=\infty$ (the poster's "most intriguing" case)

Under the $L^2$-optimal control the **peak force along a path has an infinite mean**.
Near a wall the conditioned process is a 3-dimensional Bessel process in the distance $d=1-|x|$, so the
probability of ever coming within $d$ of the wall during a unit of time, starting at distance $a$, is $d/a$;
the force there is $\approx 1/d$; hence $\mathbb P(\max_t|u^*_t| > f) \asymp c/f$ — a Pareto tail with
exponent 1, $\mathbb E[\mathrm{Lip}\,K] = \infty$. Measured tail (4000 paths, $T=4$, $dt=10^{-4}$, `keep_tail.json`):
$\mathbb P(\text{peak}>f) = 0.666,\ 0.381,\ 0.193,\ 0.072$ for $f=10,20,40,80$, i.e. $f\cdot\mathbb P = 6.7,\ 7.6,\ 7.7,\ 5.8$ —
flat (the $1/f$ law) over the decade the integrator resolves; beyond $f\approx 100$ the step size
($\sqrt{dt}=0.01$, the wall distance where $|u|=100$) cuts the tail off, as it must. Median peak 14.5, sample mean 28
and rising with the sample size, as an infinite mean does.

So the $L^\infty$ (and every $p$ large enough that $\mathbb E|u|^p$ diverges, i.e. $p\ge 1$ for the peak,
$p \ge 3$ for the time integral since $\int u^2 dt$ is finite but $\int |u|^p dt$ near the wall behaves like
$\int d^{-p}\,dt$ against the BES(3) local time) needs a genuinely different control: one that pushes
*earlier and softer*, accepting a positive probability of being closer to the wall in exchange for a bounded
force. **Conjecture (stated, not proved):** for $p=\infty$ the optimal control is of bang–bang type in a
moving band — force $\pm c(t)$ once $|x|$ exceeds a threshold $b(t)<1$, zero inside — with $c(t)\to\infty$
only as $t\to T$ on the set where the path is still near the wall; the minimal expected Lipschitz constant is
finite for every $T$ and grows linearly in $T$. What it would take: solve the HJB inequality for the
$L^\infty$ running cost (a free-boundary problem in $(t,x,\text{running max})$) numerically on a grid and
check the band structure.

## Why this is a picture

Three materials: the pigment cloud is the *law* (thousands of kept paths sampled at equal time steps, tinted by
the force they feel — cornflower free, apricot pushed hard); the ink threads are a few *actual* paths whose
ink weight follows the force; the coral lines are the walls, never touched. Time runs upward; the cloud spreads
from the origin at the bottom, settles to the $\cos^2$ profile, and flares at the very top where the keeper
lets go.
