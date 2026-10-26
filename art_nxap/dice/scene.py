"""Build tracer arrays from a list of dice."""
import numpy as np, math
from PIL import Image, ImageDraw, ImageFont
from geom import *
import sim

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'

SORBET = {
 'strawberry': (0.98, 0.62, 0.68), 'coral': (1.0, 0.62, 0.55), 'peach': (1.0, 0.78, 0.62),
 'butter': (1.0, 0.92, 0.58), 'lime': (0.82, 0.95, 0.60), 'mint': (0.64, 0.94, 0.80),
 'sky': (0.62, 0.84, 1.0), 'periwinkle': (0.70, 0.74, 1.0), 'lilac': (0.84, 0.72, 1.0),
 'bubblegum': (1.0, 0.68, 0.88), 'rose': (1.0, 0.75, 0.80),
}


def atlas(nmax, S=160):
    A = np.zeros((nmax + 1, S, S), np.float32)
    f = ImageFont.truetype(FONT, int(S * 0.62))
    for k in range(1, nmax + 1):
        im = Image.new('L', (S * 2, S * 2), 0)
        d = ImageDraw.Draw(im)
        s = str(k) + ('.' if k in (6, 9) else '')
        bb = d.textbbox((0, 0), s, font=f)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        d.text((S - w / 2 - bb[0], S - h / 2 - bb[1]), s, font=f, fill=255)
        im = im.resize((S, S), Image.LANCZOS)
        A[k] = np.asarray(im, np.float32) / 255.0
    return A


def face_frame(V, f, N):
    P = V[f]
    c = P.mean(0)
    # inradius-ish: min distance from c to the edge lines
    rmin = 1e9
    for k in range(len(f)):
        a, b = P[k], P[(k + 1) % len(f)]
        e = (b - a) / np.linalg.norm(b - a)
        w = c - a
        rmin = min(rmin, np.linalg.norm(w - (w @ e) * e))
    return c, rmin


def pose_die(V, F, seed, e=0.5, mu=0.4, ws=12.0, rec_every=0):
    """throw the die (deterministic sim), return rotated body vertices (centroid origin, resting) + record."""
    Vb, Nb, Ii = sim.prepare(V, F)
    rng = np.random.default_rng(seed)
    u = rng.random(9)
    q0 = sim.rand_quat(u[0], u[1], u[2])
    rec = np.zeros((40000, 7))
    f, t, n = sim.throw(Vb, Nb, Ii, np.array([0, 0, 3.0]), q0, np.array([1.0 * (2*u[4]-1), 1.0 * (2*u[5]-1), 0]),
                        ws * (2 * u[6:9] - 1), e, mu, 2e-4, 15.0, max(rec_every, 1), rec)
    x = rec[n - 1, :3]; q = rec[n - 1, 3:]
    R = sim.qrot(q)
    return Vb, R, x, f, rec[:n]


class Scene:
    def __init__(self):
        self.PL = []; self.OB = []; self.GL = []
        self.nmax = 20

    def add(self, Vb, F, R, pos, tint, strength=1.0, ink=(0.98, 0.97, 0.96), numbers=True, gscale=0.62, labels=None):
        Vw = Vb @ R.T + np.asarray(pos)
        N, d = planes(Vw, F)
        s = len(self.PL)
        cen = Vw.mean(0) if False else (np.asarray(pos))
        rad = np.linalg.norm(Vw - cen, axis=1).max() * 1.001
        sig = [-math.log(max(c, 1e-3)) * strength for c in tint]
        self.OB.append([s, len(F), *cen, rad, *sig, *ink])
        up_w = R @ np.array([0, 0, 1.0])
        for i, f in enumerate(F):
            self.PL.append([*N[i], d[i]])
            if not numbers:
                self.GL.append([-1] + [0] * 9); continue
            c, rin = face_frame(Vw, f, N[i])
            # glyph v-axis: along die axis projected on face, else toward first vertex
            v = up_w - (up_w @ N[i]) * N[i]
            if np.linalg.norm(v) < 0.3:
                v = Vw[f[0]] - c; v -= (v @ N[i]) * N[i]
            v /= np.linalg.norm(v)
            u = np.cross(v, N[i])
            hs = rin * gscale
            lab = (i + 1) if labels is None else labels[i]
            self.GL.append([lab, *c, *(u / hs), *(v / hs)])

    def arrays(self):
        return (np.array(self.PL, float), np.array(self.OB, float), np.array(self.GL, float),
                atlas(self.nmax))


def camera(eye, tgt, fovx_deg, aperture=0.0, focus=None):
    eye = np.asarray(eye, float); tgt = np.asarray(tgt, float)
    f = tgt - eye; fd = np.linalg.norm(f); f /= fd
    r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return np.array([*eye, *f, *r, *u, math.tan(math.radians(fovx_deg) / 2), aperture, focus or fd])


def sun_env(az_deg, el_deg, sun_rad=(3.2, 3.0, 2.7), horizon=(1.0, 0.86, 0.86), zenith=(0.72, 0.80, 1.0),
            box=(-2.4, -1.4, 0.35, 0.9), box_L=1.6, sun_ang=0.05, sun_disc_L=None):
    a = math.radians(az_deg); e = math.radians(el_deg)
    s = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    disc = sun_disc_L if sun_disc_L is not None else [c / (math.pi * sun_ang ** 2) * 0.05 for c in sun_rad]
    EN = np.array([*s, math.cos(sun_ang), *disc, *horizon, *zenith, *box, box_L], float)
    return EN, s


def tonemap(img, white=1.25, expo=1.0, sat=1.0):
    x = img * expo
    L = 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]
    Ld = L * (1 + L / white ** 2) / (1 + L)
    y = x * (Ld / np.maximum(L, 1e-9))[..., None]
    m = y.mean(-1, keepdims=True)
    y = m + (y - m) * sat
    y = np.clip(y, 0, 1)
    y = np.where(y <= 0.0031308, 12.92 * y, 1.055 * y ** (1 / 2.4) - 0.055)
    return (np.clip(y, 0, 1) * 255 + np.random.random(y.shape)).clip(0, 255).astype(np.uint8)
