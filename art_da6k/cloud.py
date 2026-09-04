"""cloud.py — the value cloud of Z(sigma+it) in the value plane (Bohr–Jessen picture of MO 514874).

sample_cloud: histogram of Z(sigma+it), t in [0,T], with the phase of the leading term 2^{-it}
              accumulated as a complex mean (hue) — honest pushforward of the t-line.
rims:         outer boundary of the value set on a ladder of sigma via the torus support function
              (max over possible worlds), so the rim through the origin is the zero frontier.
"""
import numpy as np, sys, time, json
from math import log, pi
from zeta_g import gseq, torus_setup

def sample_cloud(sigma, nsamp, T, res, x0, x1, y0, y1, nterms=110, seed=0, chunk=4_194_304, dt=None):
    """quasi-uniform t-grid t_j = t0 + j*dt (dt irrational-ish), powers by an outer-product trick:
    e^{-i t_j lg} = e^{-i t0 lg} * (w^B)^a * w^b,  j = a*B + b."""
    g = gseq(nterms)
    lg = np.array([log(x) for x in g], dtype=np.float64)
    r = np.exp(-sigma * lg)
    if dt is None:
        dt = T / nsamp
    counts = np.zeros(res * res, np.float64)
    cre = np.zeros(res * res, np.float64)
    cim = np.zeros(res * res, np.float64)
    rng = np.random.default_rng(seed)
    done = 0
    t0 = time.time()
    sx = res / (x1 - x0); sy = res / (y1 - y0)
    B = 2048
    tstart = rng.uniform(0, 1000.0)
    while done < nsamp:
        m = min(chunk, nsamp - done)
        A = max(1, m // B); m = A * B
        acc = np.zeros(m, np.complex128)
        hue = None
        for n in range(nterms):
            w = np.exp(-1j * dt * lg[n])
            pb = np.cumprod(np.full(B, w)) / w                      # w^0 .. w^(B-1)
            pa = np.cumprod(np.full(A, w ** B)) / (w ** B)          # (w^B)^0 .. ^(A-1)
            term = np.multiply.outer(pa, pb).ravel() * (r[n] * np.exp(-1j * tstart * lg[n]))
            acc += term
            if n == 1:
                hue = term / r[n]
        ix = np.floor((acc.real - x0) * sx).astype(np.int64)
        iy = np.floor((acc.imag - y0) * sy).astype(np.int64)
        ok = (ix >= 0) & (ix < res) & (iy >= 0) & (iy < res)
        idx = iy[ok] * res + ix[ok]
        counts += np.bincount(idx, minlength=res * res)
        cre += np.bincount(idx, weights=hue.real[ok], minlength=res * res)
        cim += np.bincount(idx, weights=hue.imag[ok], minlength=res * res)
        done += m
        tstart += m * dt
        if (done // chunk) % 8 == 0:
            print(f'  sampled {done/1e6:.0f}M ({time.time()-t0:.0f}s)'); sys.stdout.flush()
    return counts.reshape(res, res), (cre + 1j * cim).reshape(res, res)

def rims(sigmas, ndirs=360, N=120, restarts=6, seed=0):
    """for each sigma: the outer boundary of the value set as a polygon (complex array)."""
    from scipy.optimize import minimize
    g = gseq(N)
    primes, V = torus_setup(N, g)
    lg = np.array([log(x) for x in g[:N]])
    rng = np.random.default_rng(seed)
    out = {}
    for sigma in sigmas:
        r = np.exp(-sigma * lg)
        pts = []
        theta_prev = None
        for k in range(ndirs):
            phi = 2 * pi * k / ndirs
            u = np.exp(-1j * phi)
            def fg(theta):
                e = np.exp(-1j * (V @ theta))
                z = (r * e).sum()
                f = -(u * z).real
                dz = -1j * (V * (r * e)[:, None]).sum(axis=0)
                grad = -(u * dz).real
                return f, grad
            best = (np.inf, None)
            starts = []
            if theta_prev is not None:
                starts.append(theta_prev)
            starts.append(np.full(V.shape[1], -phi))       # every prime term aligned with phi... (locked ones can't)
            for _ in range(restarts):
                starts.append(np.mod(-phi + rng.normal(0, 0.8, V.shape[1]), 2 * pi))
            for th in starts:
                res = minimize(fg, th, jac=True, method='L-BFGS-B', options=dict(maxiter=120))
                if res.fun < best[0]:
                    best = (res.fun, res.x)
            theta_prev = best[1]
            e = np.exp(-1j * (V @ best[1]))
            pts.append(complex((r * e).sum()))
        out[sigma] = np.array(pts)
        print(f'rim sigma={sigma:.4f}: leftmost Re = {min(p.real for p in pts):+.4f}   (origin {"inside" if min(p.real for p in pts) < 0 else "outside"})')
        sys.stdout.flush()
    return out


def rims_fast(sigmas, ndirs=180, N=40, starts=6, iters=400, seed=0):
    """batched projected gradient ascent on the prime torus for the support function in every
    direction at once: rim(sigma) = { argmax_theta Re(e^{-i phi} Z_theta(sigma)) : phi }."""
    g = gseq(N)
    primes, V = torus_setup(N, g)
    lg = np.array([log(x) for x in g[:N]])
    rng = np.random.default_rng(seed)
    P = V.shape[1]
    phis = 2 * pi * np.arange(ndirs) / ndirs
    out = {}
    for sigma in sigmas:
        r = np.exp(-sigma * lg)
        # theta: (ndirs*starts, P)
        th = np.concatenate([np.mod(-phis[:, None] + rng.normal(0, 0.9 * (s > 0), (ndirs, P)), 2 * pi) for s in range(starts)])
        th[:, 0] = np.repeat(np.mod(-phis, 2 * pi), 1)[np.tile(np.arange(ndirs), starts)] + rng.normal(0, 0.05, len(th))
        u = np.exp(-1j * np.tile(phis, starts))
        lr = 0.15
        m1 = np.zeros_like(th); m2 = np.zeros_like(th)
        for it in range(iters):
            e = np.exp(-1j * (th @ V.T))                 # (B, N)
            z = e @ r                                     # (B,)
            dz = -1j * (e * r[None, :]) @ V               # (B, P)
            grad = (u[:, None] * dz).real                 # d/dtheta Re(u z)
            m1 = 0.9 * m1 + 0.1 * grad; m2 = 0.99 * m2 + 0.01 * grad ** 2
            th += lr * m1 / (np.sqrt(m2) + 1e-9)
            if it == iters * 2 // 3:
                lr *= 0.3
        e = np.exp(-1j * (th @ V.T)); z = e @ r
        val = (u * z).real.reshape(starts, ndirs)
        zz = z.reshape(starts, ndirs)
        best = np.argmax(val, axis=0)
        pts = zz[best, np.arange(ndirs)]
        out[sigma] = pts
        print(f'rim sigma={sigma:.4f}: leftmost Re = {pts.real.min():+.4f}  (origin {"inside" if pts.real.min() < 0 else "outside"})')
        sys.stdout.flush()
    return out

if __name__ == '__main__':
    # quick look: rims for a ladder of sigma, save
    sig = [0.80, 0.85, 0.90, 0.95, 1.00, 1.0055, 1.02, 1.05, 1.10, 1.20]
    R = rims_fast(sig, ndirs=240, N=40, starts=6, iters=500)
    json.dump({str(k): [[p.real, p.imag] for p in v] for k, v in R.items()}, open('rims_quick.json', 'w'))
