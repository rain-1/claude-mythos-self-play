"""eigenmode.py — the strange eigenmode of a chaotic stirring (Pierrehumbert 1994).

Alternating sine flow on the torus [0, 2π)², one period = two half-periods:
    half 1:  x -> x + A sin(y + φ1)         (a shear in x that depends on y)
    half 2:  y -> y + A sin(x + φ2)         (a shear in y that depends on x)
Each half-period shear is applied to a passive scalar θ(x, y) EXACTLY in Fourier space along the sheared
axis (a row-wise phase shift), then diffusion exp(-κ k² τ) is applied spectrally.  With κ > 0 the
advection–diffusion operator over one period is compact; its leading eigenfunction — the strange
eigenmode — is the pattern every initial θ converges to (up to amplitude), decaying at the rate of the
leading eigenvalue.  Certificates: the variance decay becomes exactly geometric with a fixed ratio;
two different initial inks reach correlation |c| → 1 after normalisation.
"""
import numpy as np


class SineFlow:
    def __init__(self, n=1024, A=1.0, kappa=1e-4, phases=(0.0, 0.0), tau=1.0):
        self.n, self.A, self.kappa, self.tau = n, A, kappa, tau
        self.phi1, self.phi2 = phases
        self.k = np.fft.fftfreq(n, d=1.0 / n)               # integer wavenumbers
        self.kx = self.k[None, :]; self.ky = self.k[:, None]
        self.x = 2 * np.pi * np.arange(n) / n
        # diffusion over one half-period (tau/2)
        k2 = self.kx ** 2 + self.ky ** 2
        self.diff = np.exp(-kappa * k2 * tau / 2).astype(np.float64)

    def shear_x(self, th, delta):
        """θ(x, y) -> θ(x - δ(y), y)  (advect by +δ in x), exact spectral shift per row"""
        F = np.fft.fft(th, axis=1)
        F *= np.exp(-1j * self.kx * delta[:, None])
        return np.fft.ifft(F, axis=1)

    def shear_y(self, th, delta):
        F = np.fft.fft(th, axis=0)
        F *= np.exp(-1j * self.ky * delta[None, :])
        return np.fft.ifft(F, axis=0)

    def diffuse(self, F):
        return F * self.diff

    def period(self, th):
        """one full period, real-valued in and out (θ is kept as complex spectrum internally)"""
        dx = self.A * self.tau / 2 * np.sin(self.x + self.phi1)      # shift in x for each row y
        dy = self.A * self.tau / 2 * np.sin(self.x + self.phi2)      # shift in y for each column x
        th = self.shear_x(th, dx)
        th = np.fft.ifft2(self.diffuse(np.fft.fft2(th)))
        th = self.shear_y(th, dy)
        th = np.fft.ifft2(self.diffuse(np.fft.fft2(th)))
        return th.real

    def run(self, th0, nper, callback=None):
        th = np.asarray(th0, float)
        hist = []
        for p in range(nper):
            th = self.period(th)
            th -= th.mean()
            v = float(np.sqrt((th ** 2).mean()))
            hist.append(v)
            if callback:
                callback(p, th, v)
        return th, np.array(hist)


def initial(kind, n, seed=0):
    x = 2 * np.pi * np.arange(n) / n
    X, Y = np.meshgrid(x, x)
    if kind == 'sinx':
        return np.sin(X)
    if kind == 'siny':
        return np.sin(Y)
    if kind == 'blob':
        return np.exp(-((np.cos(X) - 1) ** 2 + (np.cos(Y) - 1) ** 2) / 0.4) - 0.0
    if kind == 'noise':
        rng = np.random.default_rng(seed)
        F = np.fft.fft2(rng.standard_normal((n, n)))
        k = np.fft.fftfreq(n, 1.0 / n); k2 = k[None, :] ** 2 + k[:, None] ** 2
        F *= np.exp(-k2 / 8.0)
        return np.fft.ifft2(F).real
    raise ValueError(kind)


if __name__ == '__main__':
    import time
    n = 512
    for A in (1.0, 1.5, 2.0):
        fl = SineFlow(n, A=A, kappa=2e-4, phases=(0.7, 1.9))
        t0 = time.time()
        a, ha = fl.run(initial('sinx', n), 40)
        b, hb = fl.run(initial('blob', n), 40)
        ratios = ha[1:] / ha[:-1]
        c = (a * b).mean() / np.sqrt((a * a).mean() * (b * b).mean())
        print(f'A={A}: {time.time()-t0:.1f}s  decay ratios last 5: {np.round(ratios[-5:], 4)}  corr(sinx, blob) = {c:+.5f}')
