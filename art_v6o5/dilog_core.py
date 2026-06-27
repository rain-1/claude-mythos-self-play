"""Complex dilogarithm Li_2 and the single-valued Bloch-Wigner function D(z).

Li_2 computed by series after reducing the argument into the disk |z|<=1 with
Re z <= 1/2, accumulating the closed-form corrections from the standard
functional equations (principal branch logs). The Bloch-Wigner combination

    D(z) = Im Li_2(z) + arg(1-z) * log|z|

is real-analytic and single-valued on C\{0,1}; it is the volume of the ideal
hyperbolic tetrahedron with cross-ratio z, and satisfies the anharmonic
symmetries D(z) = -D(1/z) = -D(1-z) and the five-term relation.
"""
import numpy as np

PI2_6 = np.pi**2 / 6.0


def _li2_series(z, N=45):
    # sum_{k=1}^N z^k / k^2 , vectorised, valid for |z|<=1
    z = np.asarray(z, dtype=np.complex128)
    s = np.zeros_like(z)
    zp = np.ones_like(z)
    for k in range(1, N + 1):
        zp = zp * z
        s += zp / (k * k)
    return s


def _li2_disk(z):
    """Li_2 for |z| <= 1, using reflection for Re z > 1/2 to speed convergence."""
    z = np.asarray(z, dtype=np.complex128)
    out = np.empty_like(z)
    hi = z.real > 0.5
    lo = ~hi
    if lo.any():
        out[lo] = _li2_series(z[lo])
    if hi.any():
        w = z[hi]
        # Li2(w) = pi^2/6 - ln(w) ln(1-w) - Li2(1-w)
        out[hi] = PI2_6 - np.log(w) * np.log1p(-w) - _li2_series(1.0 - w)
    return out


def li2(z):
    """Principal-branch complex dilogarithm on all of C (away from [1,inf))."""
    z = np.asarray(z, dtype=np.complex128)
    out = np.empty_like(z)
    inside = np.abs(z) <= 1.0
    outside = ~inside
    if inside.any():
        out[inside] = _li2_disk(z[inside])
    if outside.any():
        w = z[outside]
        # Li2(w) = -Li2(1/w) - pi^2/6 - 0.5 ln(-w)^2
        out[outside] = -_li2_disk(1.0 / w) - PI2_6 - 0.5 * np.log(-w) ** 2
    return out


def bloch_wigner(z):
    """Single-valued Bloch-Wigner dilogarithm D(z), real-valued."""
    z = np.asarray(z, dtype=np.complex128)
    D = np.imag(li2(z)) + np.angle(1.0 - z) * np.log(np.abs(z) + 1e-300)
    # D(0)=D(1)=0 by definition; kill any nan at the punctures
    D = np.where(np.isfinite(D), D, 0.0)
    return D


if __name__ == "__main__":
    import math
    # checks
    G = 0.915965594177219  # Catalan
    print("D(i)        =", float(bloch_wigner(np.array([1j]))[0]), " expect", G)
    mx = float(bloch_wigner(np.array([np.exp(1j*math.pi/3)]))[0])
    print("D(e^{ipi/3})=", mx, " expect Cl_2(pi/3)~1.0149416")
    # antisymmetry / inversion: D(z) = -D(1/z), -D(1-z)
    zs = np.array([0.3+0.7j, -1.2+0.4j, 2.0-1.5j, 0.9+0.05j])
    print("max|D(z)+D(1/z)| =", float(np.max(np.abs(bloch_wigner(zs)+bloch_wigner(1/zs)))))
    print("max|D(z)+D(1-z)| =", float(np.max(np.abs(bloch_wigner(zs)+bloch_wigner(1-zs)))))
    print("Li2(1) real =", float(li2(np.array([1.0+0j]))[0].real), "expect", PI2_6)
