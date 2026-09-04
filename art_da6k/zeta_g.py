"""zeta_g.py — the lacunary zeta of the binary-partition sequence (MO 514874).

  a(m) = A000123(m) = number of partitions of 2m into powers of 2:  a(0)=1, a(m)=a(m-1)+a(m//2)
  g(n) = a(n+1) - (n+2)  :  1, 2, 5, 8, 13, 18, 27, 36, 49, 62, 81, 100, 125, 150, ...
  Z(s) = sum_{n>=1} g(n)^{-s}          (converges for Re s > 0 since g grows like exp(c log^2 n))

Engines:
  gseq(N)                  -> g(1..N) as Python ints
  Zval(s, N)               -> Z(s) truncated at N terms (vectorised over s)
  newton_zero(s0)          -> polish a zero
  torus_min(sigma, ...)    -> min over the prime torus of |Z_theta(sigma)|  (Bohr's possible worlds)
  scan_zeros(sig, T, dt)   -> zeros near the line Re s = sig up to height T
"""
import numpy as np
from math import log, pi
import sys, json, time

def aseq(M):
    a = [1] * (M + 1)
    for m in range(1, M + 1):
        a[m] = a[m - 1] + a[m // 2]
    return a

def gseq(N):
    a = aseq(N + 2)
    return [a[n + 1] - (n + 2) for n in range(1, N + 1)]

def factor(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f

def Zval(s, N=600, g=None):
    """Z(s) = sum g(n)^{-s}, s complex scalar or array. Uses float64 logs."""
    if g is None:
        g = gseq(N)
    lg = np.array([log(x) for x in g], dtype=np.float64)
    s = np.asarray(s, dtype=np.complex128)
    return np.exp(-np.multiply.outer(s, lg)).sum(axis=-1)

def Zderiv(s, N=600, g=None, k=1):
    if g is None:
        g = gseq(N)
    lg = np.array([log(x) for x in g], dtype=np.float64)
    s = np.asarray(s, dtype=np.complex128)
    return ((-lg) ** k * np.exp(-np.multiply.outer(s, lg))).sum(axis=-1)

def newton_zero(s0, N=600, g=None, it=40):
    if g is None:
        g = gseq(N)
    s = complex(s0)
    for _ in range(it):
        z = Zval(s, g=g); dz = Zderiv(s, g=g)
        step = z / dz
        s = s - step
        if abs(step) < 1e-15:
            break
    return s, abs(Zval(s, g=g))

def tail_bound(sigma, N, g):
    """crude: sum_{n>N} g(n)^{-sigma} using g(n) >= n^6/3057647616 (answer's bound, n>=77)
    plus the explicit terms up to len(g)."""
    lg = np.array([log(x) for x in g[N:]], dtype=np.float64)
    explicit = np.exp(-sigma * lg).sum()
    M = len(g)
    # integral tail beyond M with g(n) >= n^6/C
    C = 3057647616.0
    rest = C ** sigma * (M ** (1 - 6 * sigma)) / (6 * sigma - 1) if 6 * sigma > 1 else np.inf
    return explicit + rest

# ---------------- Bohr's torus: possible worlds ----------------
def torus_setup(N, g=None):
    """exponent matrix V (N x P): v_p(g(n)); primes list."""
    if g is None:
        g = gseq(N)
    facs = [factor(x) for x in g[:N]]
    primes = sorted({p for f in facs for p in f})
    pidx = {p: i for i, p in enumerate(primes)}
    V = np.zeros((N, len(primes)), dtype=np.float64)
    for n, f in enumerate(facs):
        for p, e in f.items():
            V[n, pidx[p]] = e
    return primes, V

def torus_value(theta, sigma, V, lg):
    r = np.exp(-sigma * lg)
    ph = V @ theta
    return (r * np.exp(-1j * ph)).sum()

def torus_min(sigma, V, lg, restarts=60, seed=0, theta0=None):
    """min_theta |Z_theta(sigma)|^2 by L-BFGS with random restarts; returns (min|Z|, theta)."""
    from scipy.optimize import minimize
    rng = np.random.default_rng(seed)
    r = np.exp(-sigma * lg)
    def fg(theta):
        ph = V @ theta
        e = np.exp(-1j * ph)
        z = (r * e).sum()
        f = (z.conj() * z).real
        # d/dtheta_p of z = sum_n r_n (-i V[n,p]) e_n
        dz = -1j * (V * (r * e)[:, None]).sum(axis=0)
        grad = 2 * (z.conj() * dz).real
        return f, grad
    best = (np.inf, None)
    starts = []
    if theta0 is not None:
        starts.append(theta0)
    starts.append(np.full(V.shape[1], pi))          # the Liouville world: all primes at pi
    for _ in range(restarts):
        th = rng.uniform(0, 2 * pi, V.shape[1])
        th[0] = pi + rng.normal(0, 0.3)               # 2 wants to point at -1
        starts.append(th)
    for th in starts:
        res = minimize(fg, th, jac=True, method='L-BFGS-B', options=dict(maxiter=400))
        if res.fun < best[0]:
            best = (res.fun, res.x)
    return np.sqrt(best[0]), best[1]

# ---------------- the actual line: zero scan ----------------
def scan_zeros(sig, T, dt=0.01, N=400, g=None, thresh=0.12, t0=0.0, chunk=2_000_000):
    """find zeros near Re s = sig for t in [t0, T]: local minima of |Z| below thresh, then Newton."""
    if g is None:
        g = gseq(N)
    lg = np.array([log(x) for x in g], dtype=np.float64)
    r = np.exp(-sig * lg).astype(np.float64)
    zeros = []
    t = t0
    while t < T:
        tt = t + dt * np.arange(min(chunk, int((T - t) / dt) + 1), dtype=np.float64)
        # Z = sum r_n exp(-i t lg_n) -- chunked over terms to bound memory
        acc = np.zeros(len(tt), dtype=np.complex128)
        for k in range(0, len(lg), 64):
            acc += (r[k:k + 64][None, :] * np.exp(-1j * np.outer(tt, lg[k:k + 64]))).sum(axis=1)
        m = np.abs(acc)
        loc = np.where((m[1:-1] < m[:-2]) & (m[1:-1] <= m[2:]) & (m[1:-1] < thresh))[0] + 1
        for i in loc:
            s0 = complex(sig, tt[i])
            s, res = newton_zero(s0, g=g, it=60)
            if res < 1e-10 and s.real > -0.05 and abs(s.imag - tt[i]) < 5:
                zeros.append((s.real, s.imag))
        t = tt[-1] + dt
    # dedupe
    out = []
    for z in sorted(zeros, key=lambda q: q[1]):
        if not out or abs(out[-1][1] - z[1]) > 1e-6 or abs(out[-1][0] - z[0]) > 1e-6:
            out.append(z)
    return out

if __name__ == '__main__':
    g = gseq(3000)
    print('g[:14] =', g[:14])
    for n in (50, 100, 200, 400, 800, 1600, 3000):
        print(f'g({n}) has {len(str(g[n-1]))} digits')
    # (a) the accepted answer's zero
    s, res = newton_zero(0.90542105477 + 13.64871096899j, g=g)
    print('answer zero polished:', s, '|Z| =', res)
    # the term chain at that zero
    lg = np.array([log(x) for x in g[:400]])
    terms = np.exp(-s * lg)
    print('first 12 terms at the zero:', np.round(terms[:12], 4))
    print('partial sums |.|:', np.round(np.abs(np.cumsum(terms))[:20], 4))
    # triangle-inequality abscissa
    for sg in (1.06, 1.07, 1.073, 1.08):
        print('sigma', sg, 'sum_{n>=2} g^-sigma =', np.exp(-sg * np.array([log(x) for x in g[1:]])).sum())
