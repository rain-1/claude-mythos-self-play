"""EHP piece, stage 2: full dispersion data.
For each odd n, compute the cone-restricted Lagrangian spectrum and classify
every eigenmode by C_n wavenumber k (0..n//2, folding k and n-k).
Fit the growth of lambda_max(n).  Also Monte-Carlo validation of the
quadratic law along the softest mode for n=9.
"""
import numpy as np
import json
from ehp_hessian import build, active_pairs, grad_F, hess_F

def full_analysis(n):
    P = build(n)
    ap = active_pairs(n)
    A = np.zeros((len(ap), 2 * n))
    for k, (i, j) in enumerate(ap):
        d = P[i] - P[j]
        A[k, 2*i:2*i+2] = 2 * d
        A[k, 2*j:2*j+2] = -2 * d
    G = grad_F(P).ravel()
    mu = np.linalg.lstsq(A.T, G, rcond=None)[0]
    H = hess_F(P)
    for k, (i, j) in enumerate(ap):
        for (a, b, s) in [(i, i, 1), (j, j, 1), (i, j, -1), (j, i, -1)]:
            H[2*a:2*a+2, 2*b:2*b+2] -= mu[k] * 2 * s * np.eye(2)
    ns = np.linalg.svd(A)[2][np.linalg.matrix_rank(A):].T
    iso = np.zeros((2 * n, 3))
    iso[0::2, 0] = 1; iso[1::2, 1] = 1
    iso[0::2, 2] = -P[:, 1]; iso[1::2, 2] = P[:, 0]
    Q, _ = np.linalg.qr(ns)
    iso_in = Q @ (Q.T @ iso)
    qi, _ = np.linalg.qr(iso_in)
    M = Q - qi @ (qi.T @ Q)
    U, s, _ = np.linalg.svd(M, full_matrices=False)
    B = U[:, s > 1e-8]
    Hr = B.T @ H @ B
    ev, evec = np.linalg.eigh(Hr)
    modes = B @ evec                      # (2n, m) columns
    ks = []
    for c in range(modes.shape[1]):
        z = modes[0::2, c] + 1j * modes[1::2, c]
        pw = np.abs(np.fft.fft(z)) ** 2 + np.abs(np.fft.fft(z.conj())) ** 2
        k = int(np.argmax(pw))
        if k > n // 2:
            k = n - k
        ks.append(k)
    return P, mu, ev, ks, modes

if __name__ == '__main__':
    data = []
    for n in list(range(5, 62, 2)) + [75, 101, 151, 201]:
        P, mu, ev, ks, modes = full_analysis(n)
        data.append(dict(n=n, mu=float(mu.mean()),
                         ev=[float(x) for x in ev],
                         ks=[int(k) for k in ks]))
        print(f"n={n:3d} lam_max={ev[-1]:+.8f} k*={ks[-1]} "
              f"lam_max/n={ev[-1]/n:+.6f}")
    with open('ehp_dispersion.json', 'w') as f:
        json.dump(data, f)

    # fit lambda_max(n) = a*n + b + c/n
    ns = np.array([d['n'] for d in data], float)
    lm = np.array([d['ev'][-1] for d in data])
    X = np.stack([ns, np.ones_like(ns), 1/ns], 1)
    coef, *_ = np.linalg.lstsq(X, lm, rcond=None)
    resid = lm - X @ coef
    print("fit lam_max ~ a n + b + c/n:", coef, "max resid", np.abs(resid).max())
    X2 = np.stack([ns, np.log(ns), np.ones_like(ns), 1/ns], 1)
    coef2, *_ = np.linalg.lstsq(X2, lm, rcond=None)
    resid2 = lm - X2 @ coef2
    print("fit with log term:", coef2, "max resid", np.abs(resid2).max())

    # quadratic-law Monte Carlo validation at n=9, softest mode direction
    n = 9
    P, mu, ev, ks, modes = full_analysis(n)
    soft = modes[:, -1]
    soft /= np.linalg.norm(soft)
    from ehp_hessian import active_pairs as apf
    def logDelta(Q):
        D = np.linalg.norm(Q[:, None] - Q[None, :], axis=2)
        iu = np.triu_indices(n, 1)
        return 2 * np.log(D[iu]).sum(), D[iu].max()
    f0, _ = logDelta(P)
    print("\nquadratic-law check n=9 (softest cone mode, feasible rescale):")
    for eps in [1e-2, 3e-3, 1e-3, 3e-4]:
        Q = P + eps * soft.reshape(-1, 2)
        f1, dmax = logDelta(Q)
        Q2 = Q * (2.0 / dmax)          # rescale into the feasible region
        f2, dmax2 = logDelta(Q2)
        drop = f0 - f2
        print(f"  eps={eps:8.1e}  dmax-2={dmax-2:+.2e}  "
              f"drop={drop:.3e}  drop/eps^2={drop/eps**2:.4f} "
              f"(pred 2*|lam|={-2*ev[-1]:.4f})")
