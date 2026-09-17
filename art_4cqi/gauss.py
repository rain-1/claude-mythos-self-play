"""gauss.py — Gauss's 1834/1839 fragment: the conformal map of the interior of an ellipse onto the unit disc,
    w = sqrt(k) * sn( (2K/pi) * arcsin z , k ),
ellipse with foci +-1 and semi-axes cosh c, sinh c, where c = pi K'/(4K) (nome q = e^{-4c} = ((a-b)/(a+b))^2).
Complex sn from the real Jacobi functions by the addition formula.  Certificates: |w| = 1 on the boundary,
w(0) = 0, w real on the real axis, and the harmonic measure of the two tips beyond the foci.
"""
import numpy as np
from scipy.special import ellipj, ellipk
from scipy.optimize import brentq

def modulus_for_ratio(ba):
    """b/a = tanh c;  K'/K = 4c/pi  ->  m = k^2"""
    c = np.arctanh(ba)
    target = 4 * c / np.pi
    f = lambda m: ellipk(1 - m) / ellipk(m) - target
    m = brentq(f, 1e-12, 1 - 1e-15, xtol=1e-15)
    return m, c

def sn_complex(u, m):
    x, y = u.real, u.imag
    s, c, d, _ = ellipj(x, m)
    s1, c1, d1, _ = ellipj(y, 1 - m)
    den = c1 ** 2 + m * s ** 2 * s1 ** 2
    return (s * d1 + 1j * c * d * s1 * c1) / den

def ellipse_map(z, ba):
    m, c = modulus_for_ratio(ba)
    K = ellipk(m)
    u = (2 * K / np.pi) * np.arcsin(z.astype(np.complex128))
    return np.sqrt(np.sqrt(m)) * sn_complex(u, m), m, c

if __name__ == '__main__':
    import json
    out = {}
    for ba in [0.9, 0.8, 0.6, 0.45, 0.3, 0.2, 0.12]:
        m, c = modulus_for_ratio(ba)
        a, b = np.cosh(c), np.sinh(c)
        t = np.linspace(0, 2 * np.pi, 4001)
        zb = a * np.cos(t) + 1j * b * np.sin(t)
        w, _, _ = ellipse_map(zb, ba)
        err = np.abs(np.abs(w) - 1).max()
        w0, _, _ = ellipse_map(np.array([0.0 + 0j]), ba)
        # image angle of the boundary point above the focus x = 1
        yf = b * np.sqrt(1 - 1 / a ** 2)
        wf, _, _ = ellipse_map(np.array([1 + 1j * yf]), ba)
        thf = np.angle(wf[0])
        # the tip beyond the foci: fraction of the ellipse's area vs of the circle (harmonic measure from the centre)
        # area of the ellipse beyond x = 1: integral
        xs = np.linspace(1, a, 20001)
        area_tip = 2 * np.trapezoid(b * np.sqrt(np.clip(1 - xs ** 2 / a ** 2, 0, None)), xs)
        area = np.pi * a * b
        # arc length fraction of the boundary beyond the focus
        tt = np.linspace(0, 2 * np.pi, 200001)
        dl = np.hypot(-a * np.sin(tt), b * np.cos(tt))
        xt = a * np.cos(tt)
        arc_tip = np.trapezoid(dl * (xt > 1), tt) / np.trapezoid(dl, tt)
        rec = dict(ba=ba, m=float(m), k=float(np.sqrt(m)), c=float(c), a=float(a), b=float(b), boundary_err=float(err),
                   w0=float(abs(w0[0])), tip_harmonic_measure=float(thf / np.pi), tip_area_fraction=float(area_tip / area),
                   tip_arc_fraction=float(arc_tip))
        out[str(ba)] = rec
        print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in rec.items()})
    json.dump(out, open('cert_gauss.json', 'w'), indent=1)

def certify(ba, n=4000, h=1e-6):
    """winding number of w around the boundary (must be 1: one zero, degree one -> bijective) and the
    Cauchy–Riemann residual at random interior points"""
    m, c = modulus_for_ratio(ba)
    a, b = np.cosh(c), np.sinh(c)
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    zb = 0.999 * (a * np.cos(t) + 1j * b * np.sin(t))
    w, _, _ = ellipse_map(zb, ba)
    wind = np.sum(np.angle(np.roll(w, -1) / w)) / (2 * np.pi)
    rng = np.random.default_rng(1)
    u = rng.random(2000) * 2 * np.pi; s = np.sqrt(rng.random(2000)) * 0.98
    z = s * (a * np.cos(u) + 1j * b * np.sin(u))
    wx = (ellipse_map(z + h, ba)[0] - ellipse_map(z - h, ba)[0]) / (2 * h)
    wy = (ellipse_map(z + 1j * h, ba)[0] - ellipse_map(z - 1j * h, ba)[0]) / (2 * h)
    cr = np.abs(wy - 1j * wx) / (np.abs(wx) + 1e-300)
    wb, _, _ = ellipse_map(a * np.cos(t) + 1j * b * np.sin(t), ba)
    return dict(ba=ba, winding=float(wind), cr_max=float(cr.max()), cr_median=float(np.median(cr)),
                boundary_modulus_err=float(np.abs(np.abs(wb) - 1).max()), min_abs_deriv=float(np.abs(wx).min()), max_abs_deriv=float(np.abs(wx).max()))
