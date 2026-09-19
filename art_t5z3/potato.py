"""potato.py — two smooth convex bodies and the closed curves they share.

MO 363950 ("Curves on potatoes", Winkler's puzzle): given two potatoes, draw a closed curve on each
so that the two curves are identical as space curves. Solution: push one potato through the other;
the surfaces cross in a closed curve that lies on both. This engine builds two star-shaped smooth
convex bodies, sweeps B through A by pure TRANSLATION (so every shared curve is a translate, and the
identity is visible in an orthographic drawing), extracts the intersection loops on A's (theta, phi)
chart, counts their components (regions of the sign field on the sphere minus one), and certifies
convexity by hull deviation.
"""
import numpy as np
from scipy.ndimage import label
from skimage.measure import find_contours


class Body:
    """inside(x) <=> |M x| < rho(M x / |M x|), rho(u) = 1 + sum eps_k exp(-(1 - u.d_k)/w_k)."""

    def __init__(self, axes, bumps, seed=None):
        self.axes = np.asarray(axes, np.float64)          # (a, b, c): the ellipsoid base
        self.M = np.diag(1.0 / self.axes)
        self.Minv = np.diag(self.axes)
        self.bumps = [(np.asarray(d, np.float64) / np.linalg.norm(d), float(e), float(w)) for d, e, w in bumps]

    def rho(self, u):
        """u: (...,3) unit vectors -> radial factor"""
        r = np.ones(u.shape[:-1], np.float64)
        for d, e, w in self.bumps:
            r += e * np.exp(-(1.0 - u @ d) / w)
        return r

    def F(self, x):
        """signed level function: <0 inside, >0 outside. x: (...,3)"""
        y = x @ self.M.T
        n = np.linalg.norm(y, axis=-1)
        n = np.maximum(n, 1e-12)
        u = y / n[..., None]
        return n - self.rho(u)

    def surface(self, u):
        """u: (...,3) unit vectors on the chart sphere -> surface points"""
        return (self.rho(u)[..., None] * u) @ self.Minv.T

    def normal(self, x, h=1e-5):
        """outward unit normal by central differences of F"""
        g = np.empty_like(x)
        for i in range(3):
            e = np.zeros(3); e[i] = h
            g[..., i] = (self.F(x + e) - self.F(x - e)) / (2 * h)
        return g / np.linalg.norm(g, axis=-1, keepdims=True)

    def hull_deviation(self, n=400):
        """convexity certificate: max signed distance of dense surface samples inside their convex hull,
        relative to the mean radius (0 for a convex body; a bump would make it positive)."""
        from scipy.spatial import ConvexHull
        u = fib_sphere(n * n // 4)
        p = self.surface(u)
        hull = ConvexHull(p)
        eq = hull.equations  # (m, 4): a.x + b <= 0 inside
        inside = np.ones(len(p), bool); inside[hull.vertices] = False
        pin = p[inside]
        depth = np.zeros(1)
        if len(pin):
            depth = np.empty(len(pin))
            for s in range(0, len(pin), 512):
                d = pin[s:s + 512] @ eq[:, :3].T + eq[:, 3]
                depth[s:s + 512] = -d.max(axis=1)
        return float(depth.max() / np.mean(np.linalg.norm(p, axis=1))), int(len(hull.vertices)), int(len(p))

    def gauss_curvature_min(self, nth=181, nph=360):
        """min Gaussian curvature over the chart (a second convexity witness: K > 0 everywhere)."""
        th = np.linspace(0.05, np.pi - 0.05, nth); ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
        T, P = np.meshgrid(th, ph, indexing='ij')
        u = sph(T, P)
        x = self.surface(u)
        # first/second fundamental forms by finite differences in the chart
        dT = th[1] - th[0]; dP = ph[1] - ph[0]
        xt = np.gradient(x, dT, axis=0); xp = np.gradient(x, dP, axis=1)
        n = np.cross(xt, xp); n /= np.linalg.norm(n, axis=-1, keepdims=True)
        xtt = np.gradient(xt, dT, axis=0); xtp = np.gradient(xt, dP, axis=1); xpp = np.gradient(xp, dP, axis=1)
        E = (xt * xt).sum(-1); Fm = (xt * xp).sum(-1); G = (xp * xp).sum(-1)
        L = (xtt * n).sum(-1); Mm = (xtp * n).sum(-1); N = (xpp * n).sum(-1)
        K = (L * N - Mm ** 2) / (E * G - Fm ** 2)
        return float(K.min()), float(K.max())


def sph(T, P):
    return np.stack([np.sin(T) * np.cos(P), np.sin(T) * np.sin(P), np.cos(T)], axis=-1)


def fib_sphere(n):
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n
    r = np.sqrt(1 - z * z)
    ph = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([r * np.cos(ph), r * np.sin(ph), z], axis=-1)


class Chart:
    """(theta, phi) chart of a body's surface"""

    def __init__(self, body, nth=768, nph=1536):
        self.body = body
        self.th = np.linspace(0, np.pi, nth)
        self.ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
        T, P = np.meshgrid(self.th, self.ph, indexing='ij')
        self.u = sph(T, P)
        self.x = body.surface(self.u)            # (nth, nph, 3)
        self.n = body.normal(self.x)

    def field(self, other, tau, R=None):
        """F_other evaluated on this surface, with other placed at translation tau (and rotation R)."""
        q = self.x - tau
        if R is not None:
            q = q @ R          # R^T applied: q_body = R^T (x - tau); rows are vectors -> q @ R
        return other.F(q)

    def curves(self, g):
        """zero contours of the field g on the chart -> list of (K,3) 3-D polylines on this surface,
        plus their chart coordinates. The phi seam is closed by one wrapped column."""
        gp = np.concatenate([g, g[:, :1]], axis=1)
        out = []
        for c in find_contours(gp, 0.0):
            ti, pi = c[:, 0], c[:, 1]
            # bilinear interpolation of the surface points (chart is smooth away from the poles)
            i0 = np.clip(np.floor(ti).astype(int), 0, len(self.th) - 2); ft = ti - i0
            j0 = np.floor(pi).astype(int) % len(self.ph); j1 = (j0 + 1) % len(self.ph); fp = pi - np.floor(pi)
            x = self.x
            p = ((1 - ft)[:, None] * ((1 - fp)[:, None] * x[i0, j0] + fp[:, None] * x[i0, j1]) +
                 ft[:, None] * ((1 - fp)[:, None] * x[i0 + 1, j0] + fp[:, None] * x[i0 + 1, j1]))
            nn = self.n
            n = ((1 - ft)[:, None] * ((1 - fp)[:, None] * nn[i0, j0] + fp[:, None] * nn[i0, j1]) +
                 ft[:, None] * ((1 - fp)[:, None] * nn[i0 + 1, j0] + fp[:, None] * nn[i0 + 1, j1]))
            n /= np.linalg.norm(n, axis=-1, keepdims=True)
            out.append((p, n, c))
        return out

    def components(self, g):
        """number of closed curves in the zero set = number of sign regions on the sphere - 1."""
        nreg = 0
        for s in (g > 0, g < 0):
            lab, k = label(s)
            if k == 0:
                continue
            parent = list(range(k + 1))

            def find(a):
                while parent[a] != a:
                    parent[a] = parent[parent[a]]; a = parent[a]
                return a

            def union(a, b):
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[ra] = rb
            # phi seam
            for a, b in zip(lab[:, 0], lab[:, -1]):
                if a and b:
                    union(a, b)
            # poles: the whole row is one point
            for row in (lab[0], lab[-1]):
                nz = row[row > 0]
                for b in nz[1:]:
                    union(nz[0], b)
            nreg += len({find(a) for a in range(1, k + 1)})
        return max(nreg - 1, 0)


def random_rotation(rng):
    q = rng.standard_normal(4); q /= np.linalg.norm(q)
    a, b, c, d = q
    return np.array([[a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
                     [2 * (b * c + a * d), a * a - b * b + c * c - d * d, 2 * (c * d - a * b)],
                     [2 * (b * d - a * c), 2 * (c * d + a * b), a * a - b * b - c * c + d * d]])


# ---- the two potatoes of the run (fixed) ----
def make_bodies():
    A = Body((1.00, 0.86, 0.80), [((0.6, 0.5, 0.6), 0.10, 0.30), ((-0.7, 0.3, -0.5), 0.08, 0.35),
                                  ((0.1, -0.9, 0.3), -0.06, 0.40), ((-0.3, -0.4, 0.8), 0.05, 0.25)])
    B = Body((0.80, 0.66, 0.58), [((0.8, 0.4, 0.4), 0.09, 0.32), ((-0.6, -0.5, 0.6), 0.07, 0.30),
                                  ((0.0, 0.9, -0.4), -0.05, 0.35)])
    return A, B


if __name__ == '__main__':
    import json, time
    A, B = make_bodies()
    t0 = time.time()
    cert = {}
    for name, bd in (('A', A), ('B', B)):
        dev, nv, npts = bd.hull_deviation()
        kmin, kmax = bd.gauss_curvature_min()
        cert[name] = dict(hull_deviation_rel=dev, hull_vertices=nv, samples=npts, K_min=kmin, K_max=kmax)
        print(name, cert[name])
    print('cert in', time.time() - t0)
    json.dump(cert, open('cache/convexity.json', 'w'), indent=1)
