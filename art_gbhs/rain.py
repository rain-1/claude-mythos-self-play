"""rain.py — the Cauchy–Poisson problem for water: rings from a stone, with capillarity.

Real water in millimetres: g = 9810 mm/s^2, sigma/rho = 72000 mm^3/s^2, nu = 1 mm^2/s.
Linear theory, initial dimple eta0 = -A exp(-r^2 / 2b^2), zero initial velocity:

    eta_hat(k, t) = eta0_hat(k) cos(omega(k) t) exp(-2 nu k^2 t),   omega^2 = g k + (sigma/rho) k^3.

Several drops at different positions and ages superpose in Fourier space: ONE inverse FFT.
Group velocity c_g = d omega / d k has a minimum (177.6 mm/s at wavelength 43.6 mm for water):
no disturbance from a drop reaches inside r = c_g,min * t, so every ring system has a calm
heart whose edge is a caustic (the slowest ring is the loudest); capillary ripples run ahead.
"""
import numpy as np
import scipy.fft as sfft
from scipy.optimize import minimize_scalar

G = 9810.0        # mm/s^2
ST = 72000.0      # sigma/rho, mm^3/s^2
NU = 1.0          # mm^2/s


def omega(k):
    return np.sqrt(G * k + ST * k ** 3)


def cg(k):
    return (G + 3 * ST * k ** 2) / (2 * omega(k))


def cg_min():
    r = minimize_scalar(lambda k: cg(k), bounds=(1e-3, 2.0), method='bounded')
    return r.fun, r.x, 2 * np.pi / r.x


def cp_min():
    r = minimize_scalar(lambda k: omega(k) / k, bounds=(1e-3, 2.0), method='bounded')
    return r.fun, r.x, 2 * np.pi / r.x


def solve(N, L, drops, b=3.0, nu=NU, workers=4):
    """drops: list of (x_mm, y_mm, age_s, amplitude[, dimple size b_mm]). Returns eta (N,N) float32 in mm."""
    dx = L / N
    k1 = 2 * np.pi * sfft.fftfreq(N, d=dx).astype(np.float64)
    KX, KY = np.meshgrid(k1, k1)
    k = np.hypot(KX, KY)
    om = omega(k)
    acc = np.zeros((N, N), np.complex128)
    for d in drops:
        x, y, t, A = d[:4]; bb = d[4] if len(d) > 4 else b
        base = -(2 * np.pi * bb * bb) * np.exp(-0.5 * (bb * k) ** 2)     # transform of the dimple (unit depth)
        acc += A * base * np.cos(om * t) * np.exp(-2 * nu * k * k * t) * np.exp(-1j * (KX * x + KY * y))
    eta = sfft.ifft2(acc, workers=workers).real / (dx * dx)
    return eta.astype(np.float32)


def energy(N, L, drops, b=3.0, nu=0.0):
    """potential + kinetic energy (per unit rho) of the linear field, from the spectrum: must be
    constant in time when nu = 0 (the certificate of the solver's dispersion bookkeeping)."""
    dx = L / N
    k1 = 2 * np.pi * sfft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(k1, k1)
    k = np.hypot(KX, KY); om = omega(k)
    out = []
    for d in drops:
        x, y, t, A = d[:4]; bb = d[4] if len(d) > 4 else b
        base = -(2 * np.pi * bb * bb) * np.exp(-0.5 * (bb * k) ** 2)
        eh = A * base * np.cos(om * t) * np.exp(-1j * (KX * x + KY * y))
        # velocity potential at surface: phi_hat = -(omega/k) * eta0_hat * sin(omega t) ... energy density
        # per mode: (g + ST k^2)|eta|^2/2 + (omega^2/k)|eta0 sin|^2 /2 -> both share (g+ST k^2)|eta0|^2/2
        pot = 0.5 * (G + ST * k * k) * np.abs(eh) ** 2
        kin = 0.5 * (G + ST * k * k) * np.abs(A * base * np.sin(om * t)) ** 2
        out.append((pot.sum(), kin.sum(), (pot + kin).sum()))
    return out


if __name__ == '__main__':
    cgm, kg, lg = cg_min(); cpm, kp, lp = cp_min()
    print(f'min group velocity {cgm:.1f} mm/s at wavelength {lg:.1f} mm; min phase velocity {cpm:.1f} mm/s at {lp:.1f} mm')
    N, L = 1024, 600.0
    for t in (0.5, 1.0, 1.5):
        e = energy(N, L, [(300, 300, t, 1.0)])[0]
        print(f't={t}: potential {e[0]:.4g} kinetic {e[1]:.4g} total {e[2]:.6g}')
    eta = solve(N, L, [(300, 300, 1.0, 1.0)], nu=0.0)
    # radial envelope from the centre: where is the inner edge?
    yy, xx = np.mgrid[0:N, 0:N]; r = np.hypot(xx - N / 2, yy - N / 2) * (L / N)
    bins = np.arange(0, 300, 2.0); idx = np.digitize(r, bins)
    prof = np.array([np.sqrt(np.mean(eta[idx == i] ** 2)) if np.any(idx == i) else 0 for i in range(1, len(bins))])
    ipk = np.argmax(prof)
    print(f'loudest ring at r = {bins[ipk]:.0f} mm; c_g,min * t = {cgm * 1.0:.0f} mm')
