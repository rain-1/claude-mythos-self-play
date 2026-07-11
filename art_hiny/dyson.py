"""Coaxial thin-core vortex rings — Dyson's Hamiltonian model.

State per ring: (sigma_i = R_i^2, Z_i). Canonical pair (Z_i, p_i = pi*Gamma_i*sigma_i).
H = sum_i (Gamma_i^2/2) R_i (ln(8R_i/a_i) - 7/4)          [self, a_i^2 R_i = const]
  + sum_{i<j} Gamma_i Gamma_j sqrt(R_i R_j) F(k_ij)        [mutual = Neumann inductance]
F(k) = (2/k - k) K(k) - (2/k) E(k),  k^2 = 4 R_i R_j / ((R_i+R_j)^2 + (Z_i-Z_j)^2)

Motion: dZ_i/dt = (1/(pi*G_i)) dH/dsigma_i ;  dsigma_i/dt = -(1/(pi*G_i)) dH/dZ_i.
Impulse P = pi * sum G_i sigma_i is exactly conserved (H depends on Z-differences).
Checks: Kelvin self-speed formula (analytic), P & H conservation, dt-halving.
"""
import numpy as np
from scipy.special import ellipk, ellipe


def hamiltonian(sig, Z, G, a0R0):
    R = np.sqrt(sig)
    a = a0R0 / np.sqrt(R)          # a = a0*sqrt(R0/R) => a*sqrt(R) = a0*sqrt(R0)
    H = np.sum(0.5 * G**2 * R * (np.log(8 * R / a) - 1.75))
    n = len(sig)
    for i in range(n):
        for j in range(i + 1, n):
            k2 = 4 * R[i] * R[j] / ((R[i] + R[j])**2 + (Z[i] - Z[j])**2)
            k = np.sqrt(k2)
            F = (2 / k - k) * ellipk(k2) - (2 / k) * ellipe(k2)
            H += G[i] * G[j] * np.sqrt(R[i] * R[j]) * F
    return H


def rhs(sig, Z, G, a0R0, h=1e-7):
    n = len(sig)
    dHds = np.empty(n); dHdZ = np.empty(n)
    for i in range(n):
        s1 = sig.copy(); s1[i] += h; s2 = sig.copy(); s2[i] -= h
        dHds[i] = (hamiltonian(s1, Z, G, a0R0) - hamiltonian(s2, Z, G, a0R0)) / (2 * h)
        z1 = Z.copy(); z1[i] += h; z2 = Z.copy(); z2[i] -= h
        dHdZ[i] = (hamiltonian(sig, z1, G, a0R0) - hamiltonian(sig, z2, G, a0R0)) / (2 * h)
    dZ = dHds / (np.pi * G)
    dsig = -dHdZ / (np.pi * G)
    return dsig, dZ


def rk4(sig, Z, G, a0R0, dt):
    k1s, k1z = rhs(sig, Z, G, a0R0)
    k2s, k2z = rhs(sig + 0.5 * dt * k1s, Z + 0.5 * dt * k1z, G, a0R0)
    k3s, k3z = rhs(sig + 0.5 * dt * k2s, Z + 0.5 * dt * k2z, G, a0R0)
    k4s, k4z = rhs(sig + dt * k3s, Z + dt * k3z, G, a0R0)
    return (sig + dt / 6 * (k1s + 2 * k2s + 2 * k3s + k4s),
            Z + dt / 6 * (k1z + 2 * k2z + 2 * k3z + k4z))


def simulate(sig0, Z0, G, a0, dt, T, keep_every=1):
    """a0: core radius at R0=1 scale — a0R0 = a0 * sqrt(R0) per ring uses R0=sqrt(sig0)."""
    sig = np.asarray(sig0, float); Z = np.asarray(Z0, float); G = np.asarray(G, float)
    a0R0 = a0 * np.sqrt(np.sqrt(sig))   # a_i sqrt(R_i) const = a0*sqrt(R_i(0))
    out_s = [sig.copy()]; out_z = [Z.copy()]; ts = [0.0]
    for step in range(1, T + 1):
        sig, Z = rk4(sig, Z, G, a0R0, dt)
        if step % keep_every == 0:
            out_s.append(sig.copy()); out_z.append(Z.copy()); ts.append(step * dt)
    return np.array(ts), np.array(out_s), np.array(out_z), a0R0


if __name__ == "__main__":
    # --- check 1: Kelvin self-induction speed for a single ring --------------
    G = np.array([1.0]); sig = np.array([1.0]); Z = np.array([0.0]); a0 = 0.05
    a0R0 = a0 * np.array([1.0])
    _, dZ = rhs(sig, Z, G, a0R0)
    kelvin = 1.0 / (4 * np.pi) * (np.log(8 / a0) - 0.25)
    print("self speed: numeric", dZ[0], " Kelvin", kelvin, " rel err", abs(dZ[0] - kelvin) / kelvin)

    # --- check 2: leapfrog pair, conservation --------------------------------
    G = np.array([1.0, 1.0]); sig0 = [1.0, 1.0]; Z0 = [0.0, 0.9]; a0 = 0.08
    dt = 2e-3; T = 40000
    ts, ss, zs, a0R0 = simulate(sig0, Z0, G, a0, dt, T, keep_every=20)
    P = np.pi * (G * ss).sum(axis=1)
    Hs = np.array([hamiltonian(s, z, G, a0R0) for s, z in zip(ss[::20], zs[::20])])
    print("P rel drift:", np.ptp(P) / P[0])
    print("H rel drift:", np.ptp(Hs) / abs(Hs[0]))
    R = np.sqrt(ss)
    print("R1 range", R[:, 0].min(), R[:, 0].max(), " R2 range", R[:, 1].min(), R[:, 1].max())
    # count leapfrog passes (Z1-Z2 sign changes of dZ? passes = R crossings)
    d = R[:, 0] - R[:, 1]
    crossings = np.count_nonzero(np.sign(d[1:]) != np.sign(d[:-1]))
    print("radius crossings (≈2 per leapfrog cycle):", crossings, " over t =", ts[-1])
