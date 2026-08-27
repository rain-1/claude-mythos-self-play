"""MO 514645: quantitative local maximality of the regular odd n-gon in the
Erdos-Herzog-Piranian problem.

Configuration: n planar points, all pairwise distances <= 2.
Objective: log Delta = 2*F, F = sum_{i<j} log|r_i - r_j|.
Regular odd n-gon with diameter 2: R = 1/cos(pi/(2n)); active constraints are
the n "diameter" pairs (i, i + (n±1)/2 mod n).

KKT: grad F = sum over active pairs mu_ij * grad g_ij, g_ij = |ri-rj|^2 - 4.
By symmetry all mu equal; we solve by least squares and verify residual ~ 0
and mu > 0 (strict complementarity).

SOSC: H = Hess F - sum mu_ij Hess g_ij restricted to the critical cone
C = {d : grad g_ij . d = 0 for all active}, modulo the 3-dim isometry space
(2 translations + rotation).  Strict local max (quadratic stability) iff
max eigenvalue of H|_(C mod E(2)) < 0; then c_n = -lambda_max (for log Delta:
multiply by 2 -- we report both conventions).

Also classifies eigenmodes by C_n wavenumber via projection onto Fourier
sectors, giving the dispersion relation lambda(k).
"""
import numpy as np
import json

def build(n):
    R = 1.0 / np.cos(np.pi / (2 * n))
    th = 2 * np.pi * np.arange(n) / n
    P = np.stack([R * np.cos(th), R * np.sin(th)], axis=1)
    return P

def active_pairs(n):
    k1, k2 = (n - 1) // 2, (n + 1) // 2
    pairs = set()
    for i in range(n):
        pairs.add(tuple(sorted((i, (i + k1) % n))))
        pairs.add(tuple(sorted((i, (i + k2) % n))))
    return sorted(pairs)

def grad_F(P):
    n = len(P)
    G = np.zeros_like(P)
    for i in range(n):
        d = P[i] - P
        rho = (d ** 2).sum(1)
        rho[i] = 1.0
        w = d / rho[:, None]
        w[i] = 0
        G[i] = w.sum(0)
    return G

def hess_F(P):
    n = len(P)
    H = np.zeros((2 * n, 2 * n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = P[i] - P[j]
            rho = d @ d
            B = np.eye(2) / rho - 2 * np.outer(d, d) / rho ** 2
            H[2*i:2*i+2, 2*i:2*i+2] += B
            H[2*i:2*i+2, 2*j:2*j+2] -= B
    return H

def analyze(n):
    P = build(n)
    ap = active_pairs(n)
    assert len(ap) == n
    # verify active distances = 2, all others < 2
    D = np.linalg.norm(P[:, None] - P[None, :], axis=2)
    iu = np.triu_indices(n, 1)
    dmax = D[iu].max()
    assert abs(dmax - 2) < 1e-12
    act_set = set(ap)
    for a, b in zip(*iu):
        d = D[a, b]
        if (a, b) in act_set:
            assert abs(d - 2) < 1e-12
        else:
            assert d < 2 - 1e-9, (n, a, b, d)

    G = grad_F(P).ravel()
    # constraint gradients (rows)
    A = np.zeros((len(ap), 2 * n))
    for k, (i, j) in enumerate(ap):
        d = P[i] - P[j]
        A[k, 2*i:2*i+2] = 2 * d
        A[k, 2*j:2*j+2] = -2 * d
    mu, res, rk, _ = np.linalg.lstsq(A.T, G, rcond=None)
    kkt_resid = np.linalg.norm(A.T @ mu - G)
    mu_min, mu_max = mu.min(), mu.max()

    # Lagrangian Hessian
    H = hess_F(P)
    for k, (i, j) in enumerate(ap):
        # Hess g = 2I on (ii),(jj); -2I on (ij),(ji)
        for (a, b, s) in [(i, i, 1), (j, j, 1), (i, j, -1), (j, i, -1)]:
            H[2*a:2*a+2, 2*b:2*b+2] -= mu[k] * 2 * s * np.eye(2)

    # critical cone: null space of A;  isometries: tx, ty, rot
    ns = np.linalg.svd(A)[2][np.linalg.matrix_rank(A):].T  # (2n, dim)
    iso = np.zeros((2 * n, 3))
    iso[0::2, 0] = 1
    iso[1::2, 1] = 1
    iso[0::2, 2] = -P[:, 1]
    iso[1::2, 2] = P[:, 0]
    # isometries lie in the cone (they preserve distances)
    chk = np.linalg.norm(A @ iso, axis=0)
    assert chk.max() < 1e-9, chk
    # orthonormal basis of cone, then quotient out isometries
    Q, _ = np.linalg.qr(ns)
    # project out iso inside the cone
    iso_in = Q @ (Q.T @ iso)
    qi, _ = np.linalg.qr(iso_in)
    M = Q - qi @ (qi.T @ Q)
    # orthonormalize the quotient
    U, s, _ = np.linalg.svd(M, full_matrices=False)
    B = U[:, s > 1e-8]
    Hr = B.T @ H @ B
    ev, evec = np.linalg.eigh(Hr)
    lam_max = ev[-1]
    # wavenumber classification of the top (softest) mode
    modes = B @ evec
    def wavenumber(m):
        z = m[0::2] + 1j * m[1::2]
        # project onto rotational Fourier sectors: displacement field
        # u_j = sum_k c_k e^{i 2pi k j/n} (complex 2-vector amplitudes)
        c = np.fft.fft(z) / n
        c2 = np.fft.fft(z.conj()) / n
        pw = np.abs(c) ** 2 + np.abs(c2) ** 2
        return int(np.argmax(pw)), pw
    ktop, _ = wavenumber(modes[:, -1])
    return dict(n=n, mu=float(mu.mean()), mu_spread=float(mu_max - mu_min),
                kkt_resid=float(kkt_resid),
                cone_dim=int(B.shape[1]), lam_max=float(lam_max),
                c_n_logDelta=float(-2 * lam_max),
                spectrum=[float(x) for x in ev[::-1][:12]],
                k_softest=ktop)

if __name__ == '__main__':
    out = []
    for n in range(5, 44, 2):
        r = analyze(n)
        out.append(r)
        print(f"n={r['n']:3d} mu={r['mu']:+.6f} (spread {r['mu_spread']:.1e}, "
              f"kkt {r['kkt_resid']:.1e}) cone_dim={r['cone_dim']} "
              f"lam_max={r['lam_max']:+.8f} c_n(logD)={r['c_n_logDelta']:+.8f} "
              f"k*={r['k_softest']}")
    with open('ehp_spectrum.json', 'w') as f:
        json.dump(out, f)
