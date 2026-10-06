"""grin.py — three gradient-index marbles traced in closed form (Opus 5.5, 2026-10-06).

All three lenses have refractive index 1 at the rim, so light enters with no bend and no
reflection; inside, the ray equation is exactly solvable (unit ball, entry point P, unit
inward direction d):

  LUNEBURG   n² = 2 − r²        ray = harmonic ellipse x(σ) = P cosσ + d sinσ
             exit point d, exit direction −P            (parallel light -> one point)
  FISH-EYE   n = 2/(1+r²)       ray = circle through P and −P   (Maxwell 1854)
             exit point −P, exit direction 2(d·P)P − d  (every point -> its antipode)
  EATON      n² = 2/r − 1       ray = Kepler ellipse a = 1, focus at the centre
             exit point 2(P·d)d − P, exit direction −d  (every ray -> back home)

Beer–Lambert tint uses the exact geometric arc length (elliptic integrals / circular arc).
A thin clear coat (Schlick, n=1.5) gives the marbles a skin; the table is a sorbet gingham
lit by a photon-mapped sun so the lens caustics/shadows are real.
"""
import numpy as np
from scipy.special import ellipe

GL_X, GL_W = np.polynomial.legendre.leggauss(16)


def nrm(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-15)


def dot(a, b):
    return np.einsum('...i,...i->...', a, b)


def lens_map(kind, P, d):
    """unit-ball coords. returns exit point X, exit dir D, geometric arc length L"""
    pd = dot(P, d)[..., None]
    if kind == 'lune':
        X = d.copy(); D = -P.copy()
        s = (GL_X + 1) * np.pi / 4                       # sigma in [0, pi/2]
        f = np.sqrt(np.clip(1 - pd * np.sin(2 * s)[None, :], 0, None))
        L = (f * GL_W[None, :]).sum(-1) * np.pi / 4
    elif kind == 'fish':
        X = -P.copy(); D = 2 * pd * P - d
        th = np.arccos(np.clip(-pd[..., 0], -1, 1))
        L = np.where(th > 1e-6, 2 * th / np.maximum(np.sin(th), 1e-9), 2.0)
    elif kind == 'eaton':
        X = 2 * pd * d - P; D = -d.copy()
        b2 = np.clip(1 - pd[..., 0] ** 2, 0, 1)          # impact parameter squared
        L = 2 * ellipe(np.clip(1 - b2, 0, 1))
    else:   # plain clear glass sphere, no bend (for comparison)
        X = P - 2 * pd * d; D = d.copy(); L = -2 * pd[..., 0]
    return X, nrm(D), L


def hit_sphere(o, d, c, r):
    oc = o - c
    b = dot(oc, d); cc = dot(oc, oc) - r * r
    disc = b * b - cc
    t = -b - np.sqrt(np.maximum(disc, 0))
    return np.where((disc > 0) & (t > 1e-6), t, np.inf)


class Scene:
    def __init__(self, balls, sun_dir, sun_rad=0.05, table_z=0.0, tex=None, sky=None):
        self.balls = balls          # list of dict(c, r, kind, absorb(rgb), dens)
        self.sun = nrm(np.asarray(sun_dir, float))      # direction TO the sun
        self.sun_rad = sun_rad
        self.tex = tex
        self.skyf = sky
        self.E = None
        self.ksun, self.kamb = 0.78, 0.30
        self.sun_col = np.array([1.0, 0.97, 0.90]); self.amb_col = np.array([0.80, 0.88, 1.0])

    # ---------- nearest hit ----------
    def nearest(self, o, d, skip=None):
        tb = np.where(d[:, 2] < -1e-9, -o[:, 2] / np.minimum(d[:, 2], -1e-9), np.inf)
        best = tb.copy(); who = np.full(len(o), -1)
        for i, B in enumerate(self.balls):
            t = hit_sphere(o, d, B['c'], B['r'])
            if skip is not None:
                t = np.where(skip == i, np.inf, t)
            m = t < best
            best = np.where(m, t, best); who = np.where(m, i, who)
        return best, who

    # ---------- through one ball ----------
    def through(self, i, X, d):
        B = self.balls[i]
        P = nrm((X - B['c']) / B['r'])
        Xe, De, L = lens_map(B['kind'], P, d)
        T = np.exp(-(B['dens'] * L * B['r'])[:, None] * np.asarray(B['absorb'])[None, :])
        return B['c'] + B['r'] * Xe, De, T, P

    # ---------- photon-mapped sun on the table ----------
    def photon_map(self, ext, res, nph=4_000_000, batches=8, seed=0):
        """ext=(x0,x1,y0,y1). E (res_y,res_x,3) = sun irradiance / unobstructed irradiance."""
        x0, x1, y0, y1 = ext; ny, nx = res
        rng = np.random.default_rng(seed)
        s = self.sun
        u = nrm(np.cross(s, [0, 0, 1.0])); v = np.cross(s, u)
        add = np.zeros((ny, nx, 3)); sub = np.zeros((ny, nx))
        cosi = s[2]
        tex_area = (x1 - x0) / nx * (y1 - y0) / ny
        for bi, B in enumerate(self.balls):
            c, r = B['c'], B['r']
            R = r * 1.001
            for _ in range(batches):
                # uniform on disc of radius R in plane ⟂ s through c, starting far toward the sun
                a = rng.random(nph); ph = rng.random(nph) * 2 * np.pi
                rr = R * np.sqrt(a)
                o = c + 30 * s + (rr * np.cos(ph))[:, None] * u + (rr * np.sin(ph))[:, None] * v
                # soft sun: jitter direction in a cone
                jx, jy = rng.standard_normal((2, nph)) * self.sun_rad * 0.5
                dirn = nrm(-s + jx[:, None] * u + jy[:, None] * v)
                w = np.pi * R * R / nph / batches / tex_area   # flux per photon in units of normal flux / texel
                # where it would land unobstructed
                tl = -o[:, 2] / dirn[:, 2]; pl = o + tl[:, None] * dirn
                # only photons that actually hit THIS ball first are counted here
                t, who = self.nearest(o, dirn)
                mine = who == bi
                ix = ((pl[:, 0] - x0) / (x1 - x0) * nx).astype(int); iy = ((pl[:, 1] - y0) / (y1 - y0) * ny).astype(int)
                ok = mine & (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
                np.add.at(sub, (iy[ok], ix[ok]), w)
                # trace through
                oo, dd = o[mine], dirn[mine]; tt, ww = t[mine], who[mine]
                thr = np.ones((len(oo), 3))
                for depth in range(6):
                    X = oo + tt[:, None] * dd
                    newo = np.empty_like(oo); newd = np.empty_like(dd)
                    for j in np.unique(ww):
                        m = ww == j
                        Xe, De, T, _ = self.through(j, X[m], dd[m])
                        newo[m] = Xe + De * 1e-6; newd[m] = De; thr[m] *= T
                    oo, dd = newo, newd
                    tt, ww = self.nearest(oo, dd, skip=None)
                    land = ww == -1
                    if land.any():
                        pl = oo[land] + tt[land, None] * dd[land]
                        ix = ((pl[:, 0] - x0) / (x1 - x0) * nx).astype(int); iy = ((pl[:, 1] - y0) / (y1 - y0) * ny).astype(int)
                        okl = np.isfinite(tt[land]) & (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
                        for ch in range(3):
                            np.add.at(add[..., ch], (iy[okl], ix[okl]), w * thr[land][okl, ch])
                    keep = ~land
                    oo, dd, tt, ww, thr = oo[keep], dd[keep], tt[keep], ww[keep], thr[keep]
                    if len(oo) == 0:
                        break
        E = cosi - sub[..., None] + add
        self.E = (ext, E / cosi)
        return self.E

    def table_light(self, p):
        """irradiance multiplier at table points p (N,3), rgb"""
        (x0, x1, y0, y1), E = self.E
        ny, nx = E.shape[:2]
        fx = np.clip((p[:, 0] - x0) / (x1 - x0) * nx - 0.5, 0, nx - 1.001)
        fy = np.clip((p[:, 1] - y0) / (y1 - y0) * ny - 0.5, 0, ny - 1.001)
        ix, iy = fx.astype(int), fy.astype(int); ax, ay = (fx - ix)[:, None], (fy - iy)[:, None]
        e = (E[iy, ix] * (1 - ax) * (1 - ay) + E[iy, ix + 1] * ax * (1 - ay)
             + E[iy + 1, ix] * (1 - ax) * ay + E[iy + 1, ix + 1] * ax * ay)
        inside = (p[:, 0] > x0) & (p[:, 0] < x1) & (p[:, 1] > y0) & (p[:, 1] < y1)
        return np.where(inside[:, None], e, 1.0)

    def ambient(self, p):
        a = np.ones(len(p))
        for B in self.balls:
            v = B['c'] - p; dist2 = dot(v, v)
            cos = np.clip(v[:, 2] / np.sqrt(dist2), 0, 1)
            a *= 1 - 0.85 * np.clip(B['r'] ** 2 / dist2, 0, 1) * cos
        return a

    # ---------- camera rays ----------
    def shade(self, o, d, depth=0, maxdepth=7):
        N = len(o)
        col = np.zeros((N, 3))
        t, who = self.nearest(o, d)
        sky = who == -1
        sky &= ~np.isfinite(t)
        col[sky] = self.skyf(d[sky])
        tab = (who == -1) & np.isfinite(t)
        if tab.any():
            p = o[tab] + t[tab, None] * d[tab]
            alb = self.tex(p[:, 0], p[:, 1])
            light = self.ksun * self.table_light(p) * self.sun_col + self.kamb * self.ambient(p)[:, None] * self.amb_col
            # far-field haze into the sky colour
            fog = np.clip((t[tab] - 26) / 40, 0, 1)[:, None]
            col[tab] = (1 - fog) * alb * light + fog * self.skyf(nrm(d[tab] * [1, 1, 0] + [0, 0, 0.02]))
        for i in range(len(self.balls)):
            m = who == i
            if not m.any():
                continue
            X = o[m] + t[m, None] * d[m]
            Xe, De, T, P = self.through(i, X, d[m])
            cosv = np.clip(-dot(P, d[m]), 0, 1)
            F = (0.04 + 0.96 * (1 - cosv) ** 5)[:, None] * self.balls[i].get('coat', 1.0)
            if depth < maxdepth:
                inner = self.shade(Xe + De * 1e-6, De, depth + 1, maxdepth)
            else:
                inner = self.skyf(De)
            if depth < 2:
                R = nrm(d[m] - 2 * dot(d[m], P)[:, None] * P)
                refl = self.shade(X + P * 1e-6 * self.balls[i]['r'], R, maxdepth, maxdepth)
            else:
                refl = self.skyf(nrm(d[m] - 2 * dot(d[m], P)[:, None] * P))
            col[m] = (1 - F) * T * inner + F * refl
        return col


def camera_rays(W, H, eye, look, fov, jitter=(0.5, 0.5), rows=None, up=(0, 0, 1), lens=(0.0, 0.0), focus=None):
    """pinhole, or thin lens: lens=(lu, lv) offset on the aperture (world units), focus = focal distance"""
    f = nrm(np.asarray(look, float) - eye)
    r = nrm(np.cross(f, up)); u = np.cross(r, f)
    y0, y1 = rows if rows else (0, H)
    jj, ii = np.meshgrid(np.arange(W), np.arange(y0, y1))
    sx = ((jj + jitter[0]) / W - 0.5) * 2 * np.tan(fov)
    sy = -((ii + jitter[1]) / W - 0.5 * H / W) * 2 * np.tan(fov)
    d = nrm(f[None, None] + sx[..., None] * r + sy[..., None] * u).reshape(-1, 3)
    o = np.broadcast_to(eye, d.shape).copy()
    if focus is not None and (lens[0] or lens[1]):
        tgt = o + d * (focus / (d @ f))[:, None]          # point on the focal plane
        o = o + lens[0] * r + lens[1] * u
        d = nrm(tgt - o)
    return o, d


def project(pts, W, H, eye, look, fov, up=(0, 0, 1)):
    f = nrm(np.asarray(look, float) - eye)
    r = nrm(np.cross(f, up)); u = np.cross(r, f)
    v = pts - eye
    z = v @ f
    sx = (v @ r) / z / (2 * np.tan(fov)); sy = (v @ u) / z / (2 * np.tan(fov))
    return np.stack([(sx + 0.5) * W, (0.5 * H / W - sy) * W], -1), z
