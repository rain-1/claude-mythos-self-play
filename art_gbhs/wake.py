"""wake.py — steady linear free-surface response to a moving pressure patch (Kelvin ship wave).

Units: g = U = 1, so the transverse wavelength is 2*pi and lengths are in U^2/g.
Linearised deep-water potential flow in the frame of the source (stream of speed 1 along
the unit vector u = (cos a, sin a)); Rayleigh damping mu selects the downstream waves and
lets them fade before the periodic box wraps.

    eta_hat(k) = - p_hat(k) * k / ( k + tau*k^3 - (k.u)^2 + 2 i mu (k.u) )

tau = sigma*g/(rho*U^4) is the capillary parameter (0 for the pure Kelvin pattern).
The pressure patch is a Gaussian of size a = 1/Fr^2 (Froude number based on the patch).

Certificates (all computed from the FIELD, none assumed):
  * Kelvin's crest curves  x = A cos t (1 + sin^2 t),  y = A sin t cos^2 t,  A = 2 pi n - c
    (one phase constant c fitted for the whole family) must ride the ridges of eta;
  * the cusp half-angle arcsin(1/3) = 19.47 deg emerges from the amplitude profile RMS(psi);
  * the angle of loudest amplitude (Rabaud–Moisy 2013) is measured per Froude number.
"""
import numpy as np
import scipy.fft as sfft
from scipy.ndimage import map_coordinates, gaussian_filter1d

KELVIN_DEG = np.degrees(np.arcsin(1.0 / 3.0))          # 19.4712...


def solve(N, L, a=0.25, tau=0.0, mu=0.02, alpha=0.0, src=(0.15, 0.5), Ny=None, Ly=None, workers=4):
    """eta on an N x Ny grid covering [0,L) x [0,Ly); source at fraction src of the box.
    alpha = heading of the stream (waves trail in direction (cos alpha, sin alpha))."""
    Ny = Ny or N
    Ly = Ly or L
    dx, dy = L / N, Ly / Ny
    kx = 2 * np.pi * sfft.fftfreq(N, d=dx).astype(np.float32)
    ky = 2 * np.pi * sfft.fftfreq(Ny, d=dy).astype(np.float32)
    KX, KY = np.meshgrid(kx, ky)                   # (Ny, N)
    k = np.hypot(KX, KY)
    ku = KX * np.cos(alpha) + KY * np.sin(alpha)
    x0, y0 = src[0] * L, src[1] * Ly
    # Gaussian pressure patch p = exp(-r^2/(2a^2)), transform 2 pi a^2 exp(-a^2 k^2/2) * phase
    phat = (2 * np.pi * a * a) * np.exp(-0.5 * (a * k) ** 2) * np.exp(-1j * (KX * x0 + KY * y0))
    den = k + tau * k ** 3 - ku ** 2 + 2j * mu * ku
    den[0, 0] = 1.0
    ehat = -phat * k / den
    ehat[0, 0] = 0.0
    del phat, den, k, ku, KX, KY
    eta = sfft.ifft2(ehat.astype(np.complex64), workers=workers).real * (1.0 / (dx * dy))
    return eta.astype(np.float32), (x0, y0)


def crest_curve(A, t):
    """Kelvin crest curve with parameter A (= phase/1); t in (-pi/2, pi/2)."""
    return A * np.cos(t) * (1 + np.sin(t) ** 2), A * np.sin(t) * np.cos(t) ** 2


def to_grid(xw, yw, x0, y0, alpha, dx, dy):
    """wave coordinates (downstream, lateral) -> grid indices (col, row)"""
    X = x0 + xw * np.cos(alpha) - yw * np.sin(alpha)
    Y = y0 + xw * np.sin(alpha) + yw * np.cos(alpha)
    return X / dx, Y / dy


def sample(eta, col, row):
    return map_coordinates(eta, [row, col], order=1, mode='constant', cval=0.0)


def fit_phase(eta, x0, y0, alpha, dx, dy, nmin=3, nmax=25, nt=400):
    """find the phase constant c such that curves A = 2 pi n - c ride the ridges: maximise
    the mean of eta over the family (normalised by the local RMS). Returns c, contrast."""
    t = np.linspace(-1.2, 1.2, nt)
    best = None
    for c in np.linspace(0, 2 * np.pi, 180, endpoint=False):
        s = 0.0; w = 0.0
        for n in range(nmin, nmax + 1):
            xw, yw = crest_curve(2 * np.pi * n - c, t)
            col, row = to_grid(xw, yw, x0, y0, alpha, dx, dy)
            v = sample(eta, col, row)
            s += v.sum(); w += len(v)
        m = s / w
        if best is None or m > best[1]:
            best = (c, m)
    c, m = best
    # contrast: mean on the fitted crests / RMS of the field in the same region
    rms = 0.0; cnt = 0
    for n in range(nmin, nmax + 1):
        xw, yw = crest_curve(2 * np.pi * n - c, t)
        for sh in np.linspace(-np.pi, np.pi, 24, endpoint=False):
            xs, ys = crest_curve(2 * np.pi * n - c + sh, t)
            col, row = to_grid(xs, ys, x0, y0, alpha, dx, dy)
            v = sample(eta, col, row); rms += (v ** 2).sum(); cnt += len(v)
    rms = np.sqrt(rms / cnt)
    return c, m, rms


def angle_profile(eta, x0, y0, alpha, dx, dy, r1, r2, psis=np.linspace(0, 40, 401), nr=1500):
    """RMS of eta along rays of angle psi (deg) from the downstream axis, r in [r1, r2]"""
    r = np.linspace(r1, r2, nr)
    out = []
    for p in psis:
        pr = np.radians(p)
        xw, yw = r * np.cos(pr), r * np.sin(pr)
        col, row = to_grid(xw, yw, x0, y0, alpha, dx, dy)
        v = sample(eta, col, row)
        out.append(np.sqrt(np.mean(v ** 2)))
    return psis, np.array(out)


def wedge_from_profile(psis, prof, frac=0.5):
    """angle of loudest amplitude and the outer edge of the wedge, defined as the angle beyond
    the peak where the RMS has fallen to `frac` of the peak (the Airy tail of the caustic)."""
    sm = gaussian_filter1d(prof, 2.0)
    ip = int(np.argmax(sm))
    peak = psis[ip]
    after = np.where(sm[ip:] < frac * sm[ip])[0]
    edge = psis[ip + after[0]] if len(after) else np.nan
    return peak, edge, sm


if __name__ == '__main__':
    import time, json, sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    L = 200.0
    t0 = time.time()
    eta, (x0, y0) = solve(N, L, a=0.25, mu=0.02)
    print(f'solve {N}^2 in {time.time()-t0:.1f}s, |eta|max {np.abs(eta).max():.3g}')
    dx = L / N
    c, m, rms = fit_phase(eta, x0, y0, 0.0, dx, dx)
    print(f'phase c = {c:.3f}, crest mean/rms = {m/rms:.3f}')
    psis, prof = angle_profile(eta, x0, y0, 0.0, dx, dx, 60, 150)
    peak, edge, sm = wedge_from_profile(psis, prof)
    print(f'peak angle {peak:.2f} deg, half-amplitude edge {edge:.2f} deg (Kelvin {KELVIN_DEG:.2f})')
    for p in (10, 15, 18, 19.5, 21, 23, 25, 30):
        print(f'   psi={p:5.1f}  rms={np.interp(p, psis, prof):.4g}')
