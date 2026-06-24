"""Piece 3 — "The Period of the Anharmonic" (elliptic integral K).

Seeded by MathOverflow's front-page identity for the quartic oscillator's
period, T/T0 = (2k/pi) K(k^2 - 1). We take the double-well potential
    V(x) = -1/2 x^2 + 1/4 x^4   (minima at x = +-1, barrier top V(0)=0),
energy  E(x,p) = 1/2 p^2 + V(x).  Orbits are level sets of E. The PERIOD of an
orbit, T(E) = 2 * Integral dx / sqrt(2(E - V)) between turning points, is an
elliptic integral that DIVERGES logarithmically as E -> 0 (the separatrix):
oscillations grow infinitely slow near the figure-eight. We draw iso-period
contours equally spaced in period; because T blows up at the separatrix, the
contours crowd into an ever-finer nest there — the visible signature of the
K(k^2-1) singularity.
"""
import sys, numpy as np
sys.path.insert(0, "src")
import render as R


def V(x):
    return -0.5 * x * x + 0.25 * x ** 4


def period_table(Emin, Emax, nE=20000, m=20000):
    """Numerically tabulate period T(E) for the double well.
    For E<0 the motion is libration inside one well (right well, x>0);
    for E>0 it is large oscillation over both wells. Turning points are roots
    of V(x)=E. We integrate with the sin-substitution that tames the
    sqrt singularity at the turning points."""
    # sample E densely near the separatrix (E=0) where T diverges; tanh-style
    # clustering toward 0 from both sides.
    u = np.linspace(-1, 1, nE)
    Es = np.sign(u) * (np.abs(u) ** 3) * max(abs(Emin), Emax)
    Es = np.clip(Es, Emin + 1e-7, Emax)
    Es = np.unique(Es)
    T = np.empty_like(Es)
    # Gauss-like nodes on (-pi/2, pi/2) for x = mid + amp*sin(theta)
    theta = (np.arange(m) + 0.5) / m * np.pi - np.pi / 2
    s = np.sin(theta)
    dtheta = np.pi / m
    for i, E in enumerate(Es):
        if E < 0:
            # right well: turning points x1,x2 are the two positive roots of
            # x^4/4 - x^2/2 - E = 0  ->  x^2 = 1 +- sqrt(1+4E)
            disc = np.sqrt(1.0 + 4.0 * E)
            x2 = np.sqrt(1.0 + disc)          # outer
            x1 = np.sqrt(1.0 - disc)          # inner
        else:
            x2 = np.sqrt(1.0 + np.sqrt(1.0 + 4.0 * E))
            x1 = -x2                          # symmetric over both wells
        mid = 0.5 * (x1 + x2); amp = 0.5 * (x2 - x1)
        x = mid + amp * s
        rad = 2.0 * (E - V(x))
        rad = np.clip(rad, 1e-12, None)
        # dx = amp*cos(theta) dtheta ; integrand dx/sqrt(rad)
        integ = amp * np.cos(theta) / np.sqrt(rad)
        half = np.sum(integ) * dtheta
        T[i] = 2.0 * half
    return Es, T


def main(S=1400, out="out/p3_anharmonic.png", down=512, supersample=1,
         band_div=6.0):
    SS = S * supersample
    win = 1.9
    xs = np.linspace(-win, win, SS, dtype=np.float32)
    ps = np.linspace(-win, win, SS, dtype=np.float32)
    X, P = np.meshgrid(xs, ps)
    E = (0.5 * P * P + V(X)).astype(np.float32)
    del X  # only sign of X needed later; recompute cheaply via xs broadcast

    Emin = -0.25
    Emax = float(E.max())
    Es, T = period_table(Emin, Emax)
    Tfield = np.interp(np.clip(E, Emin, Emax), Es, T).astype(np.float32)

    # contour phase equally spaced in PERIOD -> crowds at separatrix
    phase = Tfield / band_div
    band = np.abs(np.sin(np.pi * phase))            # 0 at contour lines
    lines = (1.0 - band ** 0.18).astype(np.float32)  # crisp contour lines
    del band, phase

    # region: over-barrier sea (E>=0), else left/right well by sign of x
    signx = np.sign(xs)[None, :]                     # broadcast over rows
    region = np.where(E >= 0, 0, np.where(signx < 0, 1, 2)).astype(np.int8)

    # base color from a period colormap; contour lines glow on top
    tcol = np.clip((Tfield - T.min()) /
                   (np.percentile(T, 99) - T.min()), 0, 1).astype(np.float32)
    base = (R.apply_lut(tcol, R.palette_lut(R.PAL_ICE, 2048)) * 0.22).astype(np.float32)
    del tcol, Tfield, E

    cols = {0: np.array([0.55, 0.78, 1.00], np.float32),   # sea - cool
            1: np.array([1.00, 0.55, 0.30], np.float32),   # left well - warm
            2: np.array([0.55, 1.00, 0.75], np.float32)}   # right well - green
    rgb = base
    for rv, c in cols.items():
        msk = region == rv
        rgb[msk] += c * (lines[msk][:, None] * 0.95)
    rgb = np.clip(rgb, 0, 1)
    R.save(rgb, out, downscale_to=down)
    print("wrote", out, "Tmax", round(float(T.max()), 2),
          "Tmin", round(float(T.min()), 2))


if __name__ == "__main__":
    main()
