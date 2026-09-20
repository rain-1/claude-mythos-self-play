"""kendall.py — Kendall's shape sphere of triangles.

A labelled triangle (z1, z2, z3) in the plane, with position, size and rotation removed, is the point
zeta = (2 z3 - z1 - z2) / (sqrt(3) (z2 - z1)) of the Riemann sphere (the ratio of the two Helmert
coordinates w2/w1, w1 = (z2 - z1)/sqrt2, w2 = (2 z3 - z1 - z2)/sqrt6).  With the Fubini–Study metric
the shape space is a round sphere (Kendall 1984, radius 1/2; drawn here as the unit sphere by
stereographic projection).  Poles (0, ±1, 0): equilateral (two orientations).  Equator Y = 0:
collinear.  Isosceles: three meridians.  Right-angled at vertex k: three circles |zeta| = 1/sqrt3 and its
120° rotations, each bounding a cap of one quarter of the area — so a Gaussian triangle is obtuse
with probability exactly 3/4 (Kendall's theorem: three iid Gaussian points give a uniform point).
"""
import numpy as np

POLE = np.array([0.0, 1.0, 0.0])


def shape_zeta(z1, z2, z3):
    return (2 * z3 - z1 - z2) / (np.sqrt(3) * (z2 - z1))


def stereo(zeta):
    x, y = zeta.real, zeta.imag
    d = x * x + y * y + 1
    return np.stack([2 * x / d, 2 * y / d, (x * x + y * y - 1) / d], -1)


def inv_stereo(P):
    X, Y, Z = P[..., 0], P[..., 1], P[..., 2]
    return (X + 1j * Y) / (1 - Z)


def triangle_of(zeta):
    """a representative triangle for the shape, centred at the centroid, unit pre-shape norm."""
    z1 = -0.5 + 0j; z2 = 0.5 + 0j; z3 = np.sqrt(3) / 2 * zeta
    z = np.array([z1, z2, z3]); z = z - z.mean()
    z = z / np.sqrt((abs(z) ** 2).sum())
    return z


def angles(z):
    """interior angles of triangle with complex vertices z (3,)"""
    a = []
    for k in range(3):
        u = z[(k + 1) % 3] - z[k]; v = z[(k + 2) % 3] - z[k]
        c = (u * np.conj(v)).real / (abs(u) * abs(v) + 1e-300)
        a.append(np.arccos(np.clip(c, -1, 1)))
    return np.array(a)


def fibonacci_sphere(N):
    i = np.arange(N) + 0.5
    phi = np.arccos(1 - 2 * i / N)
    th = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)], -1)


def rot_about(axis, ang):
    axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


def great_circle_meridian(lon, m=2000):
    """meridian through the poles at longitude lon (in the X–Z plane rotated about the pole axis)"""
    t = np.linspace(0, 2 * np.pi, m)
    P = np.stack([np.sin(t) * np.cos(lon), np.cos(t), np.sin(t) * np.sin(lon)], -1)
    return P


def small_circle(centre, cosang, m=2000):
    """circle of points at angular distance acos(cosang) from centre"""
    c = np.asarray(centre, float); c /= np.linalg.norm(c)
    a = np.cross(c, POLE)
    if np.linalg.norm(a) < 1e-6:
        a = np.cross(c, [1, 0, 0])
    a /= np.linalg.norm(a); b = np.cross(c, a)
    s = np.sqrt(1 - cosang ** 2)
    t = np.linspace(0, 2 * np.pi, m)
    return cosang * c[None] + s * (np.cos(t)[:, None] * a[None] + np.sin(t)[:, None] * b[None])


def certify(rng, n=200000):
    """Kendall's theorem numerically: Gaussian triangles are uniform on the sphere; obtuse 3/4."""
    z = rng.standard_normal((n, 3)) + 1j * rng.standard_normal((n, 3))
    zeta = shape_zeta(z[:, 0], z[:, 1], z[:, 2])
    P = stereo(zeta)
    # uniform on the sphere  <=>  each coordinate uniform on [-1, 1]
    from scipy.stats import kstest
    ks = [kstest(P[:, k], 'uniform', args=(-1, 2)).statistic for k in range(3)]
    # obtuse fraction
    u = z[:, 1] - z[:, 0]; v = z[:, 2] - z[:, 0]; w = z[:, 2] - z[:, 1]
    def ang(p, q):
        return np.arccos(np.clip((p * np.conj(q)).real / (abs(p) * abs(q)), -1, 1))
    A = np.stack([ang(u, v), ang(-u, w), ang(-v, -w)], 1)
    obt = (A.max(1) > np.pi / 2).mean()
    # right-angle-at-3 circle: |zeta| = 1/sqrt3  <=> the right angle at z3
    r = abs(zeta)
    near = np.abs(A[:, 2] - np.pi / 2) < 1e-3
    return dict(ks=ks, obtuse_fraction=float(obt), n=n,
                right_at_3_radius=[float(r[near].min()), float(r[near].max())] if near.any() else None)


if __name__ == '__main__':
    import json
    c = certify(np.random.default_rng(0))
    print(json.dumps(c))
