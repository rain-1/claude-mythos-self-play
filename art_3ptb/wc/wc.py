"""wc.py — a small watercolour engine on cold-press paper.

Washes are Beer–Lambert glazes (absorbance adds), each with
  * a wobbly wet edge (signed distance + fractal noise),
  * edge darkening (pigment carried to the drying rim),
  * flow mottling and gravity pooling,
  * granulation (pigment settles in the valleys of the paper),
and optional wet-in-wet blending of two pigments and cauliflower blooms.
Pencil strokes are splatted points, blurred, and caught on the paper's peaks.
All sizes are in pixels of a canvas of width W; `s = W/4096` scales them.
"""
import numpy as np
from scipy import ndimage as ndi


def fnoise(H, W, scale, rng, aniso=1.0):
    """Gaussian-filtered white noise with correlation length ~scale px, std 1."""
    z = rng.standard_normal((H, W)).astype(np.float32)
    fy = np.fft.fftfreq(H).astype(np.float32)[:, None]
    fx = np.fft.rfftfreq(W).astype(np.float32)[None, :]
    g = np.exp(-(2 * np.pi * scale) ** 2 * (fx ** 2 * aniso + fy ** 2 / aniso) / 2)
    out = np.fft.irfft2(np.fft.rfft2(z) * g, s=(H, W)).astype(np.float32)
    out /= out.std() + 1e-9
    return out


def fbm(H, W, scale, rng, octaves=4, gain=0.55):
    acc = np.zeros((H, W), np.float32)
    a, tot = 1.0, 0.0
    for o in range(octaves):
        acc += a * fnoise(H, W, scale / 2 ** o, rng)
        tot += a * a
        a *= gain
    return acc / np.sqrt(tot)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def pigment(rgb):
    """Absorbance per unit density so that density 1 on white looks like rgb."""
    c = np.clip(np.asarray(rgb, np.float32), 1e-3, 1)
    return -np.log(c)


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


class Sheet:
    def __init__(self, H, W, seed=1, paper=(0.993, 0.986, 0.972), tooth=1.0):
        self.H, self.W = H, W
        self.s = W / 4096
        s = self.s
        self.rng = np.random.default_rng(seed)
        r = self.rng
        self.paper = np.array(paper, np.float32)
        # cold-press paper height: bumps of two sizes + a faint felt direction
        h = 0.65 * fnoise(H, W, 5.0 * s * tooth, r) + 0.28 * fnoise(H, W, 13 * s * tooth, r) \
            + 0.15 * fnoise(H, W, 2.0 * s * tooth, r, aniso=2.5)
        self.h = h / h.std()
        # noise bank, reused by washes through random rolls
        self.n_edge = fbm(H, W, 40 * s, r, octaves=5)      # wet-edge wobble
        self.n_fine = fnoise(H, W, 4 * s, r)               # rim roughness
        self.n_flow = fbm(H, W, 120 * s, r, octaves=4)     # mottling
        self.n_bloom = fbm(H, W, 30 * s, r, octaves=5)     # cauliflower
        self.A = np.zeros((H, W, 3), np.float32)           # absorbance
        self.G = np.zeros((H, W), np.float32)              # graphite

    def _roll(self, f, box):
        y0, y1, x0, x1 = box
        dy, dx = self.rng.integers(0, self.H), self.rng.integers(0, self.W)
        ys = (np.arange(y0, y1) + dy) % self.H
        xs = (np.arange(x0, x1) + dx) % self.W
        return f[np.ix_(ys, xs)]

    # ---------------------------------------------------------------- washes
    def wash(self, sd, box, K, dens=0.35, edge=0.55, edge_w=5.0, wobble=6.0,
             mottle=0.22, gran=0.35, pool=0.0, pool_dir=(0.0, 1.0), K2=None,
             mix=None, bloom=0.0, soft=0.0, alpha=None):
        """sd: signed distance (px, <0 inside) on the crop `box`=(y0,y1,x0,x1).
        K, K2: pigment absorbance vectors; mix: field in [0,1] (K→K2).
        soft>0: wet-in-wet edge (blurred, no rim)."""
        s = self.s
        y0, y1, x0, x1 = box
        y0, x0 = max(y0, 0), max(x0, 0)
        y1, x1 = min(y1, self.H), min(x1, self.W)
        oy, ox = y0 - box[0], x0 - box[2]
        sd = sd[oy:oy + (y1 - y0), ox:ox + (x1 - x0)]
        if mix is not None and np.ndim(mix) == 2:
            mix = mix[oy:oy + (y1 - y0), ox:ox + (x1 - x0)]
        bx = (y0, y1, x0, x1)
        ne = self._roll(self.n_edge, bx)
        nf = self._roll(self.n_fine, bx)
        sdw = sd + wobble * s * ne + 0.9 * s * nf
        if soft > 0:
            cov = 1 / (1 + np.exp(np.clip(sdw / (soft * s), -30, 30)))
            rim = 0.0
        else:
            cov = np.clip(0.5 - sdw, 0, 1)
            inside = np.maximum(-sdw, 0)
            rim = edge * np.exp(-inside / (edge_w * s)) + 0.35 * edge * np.exp(-inside / (edge_w * s * 6))
        h = self.h[y0:y1, x0:x1]
        nfl = self._roll(self.n_flow, bx)
        d = dens * (1 + mottle * nfl)
        if pool:
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            t = (yy - yy.mean()) * pool_dir[1] + (xx - xx.mean()) * pool_dir[0]
            t /= max(np.abs(t).max(), 1)
            d = d * (1 + pool * t)
        if bloom:
            nb = self._roll(self.n_bloom, bx)
            # a backrun: pigment pushed out of a blob, piled on its ragged front
            front = nb - 0.9
            d = d * (1 - bloom * smoothstep(-0.05, 0.25, front)) + \
                bloom * 0.9 * dens * np.exp(-(front / 0.07) ** 2)
        d = (d + rim) * (1 + gran * np.clip(-h, -1.5, 2.5) * 0.5)
        d = np.maximum(d, 0) * cov
        if alpha is not None:
            d = d * alpha[oy:oy + (y1 - y0), ox:ox + (x1 - x0)]
        if K2 is None:
            self.A[y0:y1, x0:x1] += d[..., None] * K[None, None, :]
        else:
            m = mix[..., None] if np.ndim(mix) == 2 else mix
            Kf = K[None, None, :] * (1 - m) + K2[None, None, :] * m
            self.A[y0:y1, x0:x1] += d[..., None] * Kf

    def wash_poly(self, pts, K, pad=40, **kw):
        sd, box = poly_sd(pts, self.H, self.W, pad=int(pad * self.s) + 8)
        if sd is None:
            return
        if 'mix_fn' in kw:
            fn = kw.pop('mix_fn')
            yy, xx = np.mgrid[box[0]:box[1], box[2]:box[3]].astype(np.float32)
            kw['mix'] = fn(xx, yy, box)
        self.wash(sd, box, K, **kw)

    # ---------------------------------------------------------------- pencil
    def stroke(self, pts, weight=1.0, step=0.5):
        """Polyline (N,2) in px → graphite deposit (splat), blurred at finish."""
        pts = np.asarray(pts, np.float64)
        seg = np.diff(pts, axis=0)
        L = np.hypot(seg[:, 0], seg[:, 1])
        n = np.maximum((L / step).astype(int), 1)
        P = [pts[:-1][i] + seg[i] * (np.arange(n[i])[:, None] / n[i]) for i in range(len(seg))]
        P = np.concatenate(P + [pts[-1:]])
        # hand tremor: slow perpendicular wander + pressure variation
        t = np.arange(len(P))
        rng = self.rng
        ph = rng.uniform(0, 6.28, 3)
        wob = 0.35 * self.s * (np.sin(t * 0.004 + ph[0]) + 0.5 * np.sin(t * 0.011 + ph[1]))
        tang = np.gradient(P, axis=0)
        tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-9
        P = P + np.stack([-tang[:, 1], tang[:, 0]], 1) * wob[:, None]
        pr = weight * (0.8 + 0.2 * np.sin(t * 0.0023 + ph[2])) * step
        x, y = P[:, 0], P[:, 1]
        ix, iy = np.floor(x).astype(int), np.floor(y).astype(int)
        fx, fy = x - ix, y - iy
        for dx, dy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                          (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
            X, Y = ix + dx, iy + dy
            ok = (X >= 0) & (X < self.W) & (Y >= 0) & (Y < self.H)
            np.add.at(self.G, (Y[ok], X[ok]), (w * pr)[ok])

    def circle(self, cx, cy, r, weight=1.0, a0=0, a1=2 * np.pi, overshoot=0.0):
        n = max(int(abs(a1 - a0) * r / 1.5), 16)
        a = np.linspace(a0 - overshoot, a1 + overshoot, n)
        self.stroke(np.stack([cx + r * np.cos(a), cy + r * np.sin(a)], 1), weight)

    def line(self, p, q, weight=1.0, over=0.0):
        p, q = np.asarray(p, float), np.asarray(q, float)
        d = q - p
        d /= np.linalg.norm(d) + 1e-12
        self.stroke(np.array([p - d * over, q + d * over]), weight)

    def splatter(self, cx, cy, spread, K, n=40, rmax=6.0, dens=0.5):
        """flicked droplets: small discs, more and smaller further out"""
        r = self.rng
        for i in range(n):
            d = spread * r.random() ** 0.7
            a = r.uniform(0, 2 * np.pi)
            rr = rmax * self.s * (0.25 + 0.75 * r.random()) * (1 - 0.6 * d / spread)
            sd, box = disc_sd(cx + d * np.cos(a), cy + d * np.sin(a), rr, self.H, self.W, pad=int(4 * self.s) + 3)
            self.wash(sd, box, K, dens=dens, edge=0.5, edge_w=1.0, wobble=0.6, mottle=0.1, gran=0.2)

    def halo(self, cx, cy, r, K, dens=0.05):
        """a very pale wet-in-wet underwash"""
        sd, box = disc_sd(cx, cy, r, self.H, self.W, pad=int(60 * self.s))
        self.wash(sd, box, K, dens=dens, soft=40, wobble=60, mottle=0.35, gran=0.2)

    def text(self, xy, s, size, font='/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf',
             weight=1.0, anchor='la', color=None, dens=0.5):
        """pencil text (color=None) or a painted text wash (color=K)"""
        from PIL import Image, ImageDraw, ImageFont
        f = ImageFont.truetype(font, int(size))
        im = Image.new('L', (self.W, self.H), 0)
        ImageDraw.Draw(im).text(xy, s, font=f, fill=255, anchor=anchor)
        m = np.asarray(im, np.float32) / 255
        if color is None:
            self.G += m * weight * 1.4
        else:
            self.A += (m * dens)[..., None] * color[None, None, :]

    # ---------------------------------------------------------------- finish
    def finish(self, graphite=(0.36, 0.34, 0.42), pencil_sigma=0.75, light=0.025):
        s = self.s
        G = ndi.gaussian_filter(self.G, pencil_sigma * max(s, 0.5))
        G = 1 - np.exp(-0.9 * G)
        catch = np.clip(0.55 + 0.35 * self.h, 0.1, 1.2)        # graphite on peaks
        Ag = (G * catch)[..., None] * pigment(graphite)[None, None, :] * 1.3
        gy, gx = np.gradient(ndi.gaussian_filter(self.h, 1.2 * s))
        shade = 1 + light * (gx - gy) / (np.abs(gx - gy).std() + 1e-6) * 0.5
        rgb = self.paper[None, None, :] * np.exp(-(self.A + Ag)) * shade[..., None]
        return np.clip(rgb, 0, 1)


def to8(rgb, rng=None):
    rng = rng or np.random.default_rng(0)
    x = rgb * 255 + rng.uniform(-0.5, 0.5, rgb.shape)
    return np.clip(x + 0.5, 0, 255).astype(np.uint8)


def poly_sd(pts, H, W, pad=20):
    """Exact signed distance (px) of a simple polygon on a crop around it."""
    pts = np.asarray(pts, np.float64)
    x0 = int(np.floor(pts[:, 0].min())) - pad
    x1 = int(np.ceil(pts[:, 0].max())) + pad
    y0 = int(np.floor(pts[:, 1].min())) - pad
    y1 = int(np.ceil(pts[:, 1].max())) + pad
    if x1 <= 0 or y1 <= 0 or x0 >= W or y0 >= H:
        return None, None
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    xx += 0.5
    yy += 0.5
    dmin = np.full(xx.shape, np.inf, np.float32)
    inside = np.zeros(xx.shape, bool)
    n = len(pts)
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        L2 = ex * ex + ey * ey + 1e-12
        t = np.clip(((xx - ax) * ex + (yy - ay) * ey) / L2, 0, 1)
        dx, dy = xx - ax - t * ex, yy - ay - t * ey
        dmin = np.minimum(dmin, dx * dx + dy * dy)
        cond = ((ay > yy) != (by > yy)) & (xx < (bx - ax) * (yy - ay) / (by - ay + 1e-12) + ax)
        inside ^= cond
    sd = np.sqrt(dmin)
    sd[inside] *= -1
    return sd, (y0, y1, x0, x1)


def winding(pts, box):
    """winding number of a closed polygon on the pixel centres of box"""
    y0, y1, x0, x1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float64) + 0.5
    w = np.zeros(xx.shape)
    n = len(pts)
    for i in range(n):
        ax, ay = pts[i] ; bx, by = pts[(i + 1) % n]
        a = np.arctan2(ay - yy, ax - xx); b = np.arctan2(by - yy, bx - xx)
        w += (b - a + np.pi) % (2 * np.pi) - np.pi
    return np.rint(w / (2 * np.pi)).astype(int)


def mask_sd(mask):
    """signed distance (px, <0 inside) of a boolean mask"""
    return (ndi.distance_transform_edt(~mask) - ndi.distance_transform_edt(mask)
            + np.where(mask, 0.5, -0.5)).astype(np.float32)


def disc_sd(cx, cy, r, H, W, pad=20):
    x0, x1 = int(cx - r) - pad, int(cx + r) + pad
    y0, y1 = int(cy - r) - pad, int(cy + r) + pad
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    return np.hypot(xx + 0.5 - cx, yy + 0.5 - cy) - r, (y0, y1, x0, x1)
