"""cyano.py -- a cyanotype (sun print / photogram) engine.   Fable 5.2, day 5.

The process is simulated, not the look:
  1. paper            : cotton rag with a grain
  2. coat             : sensitiser brushed on in horizontal strokes (ragged ends, streaks)
  3. lay objects      : each object is a TRANSMISSION mask (1 = clear, 0 = opaque) at a height
                        above the paper; height turns into penumbra (Gaussian blur)
  4. expose(weight)   : dose += weight * product of transmissions; several exposures add
  5. develop          : density = coat * curve(dose); Prussian blue ramp; wash stains, dust
  6. pencil caption in the margin, one red stamp

All lengths are in units of S = size/1024 so a 1024 proof and a 4096 print agree.
"""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

PAPER = np.array([0.960, 0.945, 0.905], np.float32)
RAMP_X = np.array([0.0, 0.12, 0.30, 0.50, 0.70, 0.86, 1.0], np.float32)
RAMP = np.array([[0.960, 0.945, 0.905],
                 [0.800, 0.880, 0.905],
                 [0.520, 0.720, 0.840],
                 [0.235, 0.500, 0.720],
                 [0.085, 0.300, 0.560],
                 [0.040, 0.190, 0.455],
                 [0.026, 0.105, 0.320]], np.float32)
SERIF_I = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'


def fbm(shape, cell, rng, octaves=3, aniso=(1.0, 1.0)):
    """smooth noise in [-1,1]; cell = feature size in px; aniso stretches (y, x)."""
    H, W = shape; out = np.zeros(shape, np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        cy = max(1.0, cell * aniso[0] / 2 ** o); cx = max(1.0, cell * aniso[1] / 2 ** o)
        h = int(np.ceil(H / cy)) + 3; w = int(np.ceil(W / cx)) + 3
        g = rng.standard_normal((h, w)).astype(np.float32)
        z = ndi.zoom(g, (H / (h - 3) , W / (w - 3)), order=3)[:H, :W]
        if z.shape != (H, W):
            z = np.pad(z, ((0, H - z.shape[0]), (0, W - z.shape[1])), mode='edge')
        out += amp * z; tot += amp; amp *= 0.5
    return out / tot / 0.8


class Sheet:
    def __init__(self, size=1024, seed=0, ss=2, coat_box=(0.085, 0.07, 0.915, 0.845)):
        self.n = size; self.S = size / 1024.0; self.ss = ss
        self.rng = np.random.default_rng(seed)
        self.dose = np.zeros((size, size), np.float32)
        self.T = np.ones((size, size), np.float32)      # transmission of what lies on the paper now
        boxes = coat_box if isinstance(coat_box[0], (tuple, list)) else [coat_box]
        self.coat = None
        for b in boxes:
            c = self._coat(b)
            self.coat = c if self.coat is None else np.maximum(self.coat, c)
        self.box = boxes[0]
        streak = fbm((size, size), 9 * self.S, self.rng, octaves=3, aniso=(1.0, 40.0))
        blotch = fbm((size, size), 260 * self.S, self.rng, octaves=3)
        self.thick = (0.985 + 0.085 * streak + 0.10 * blotch).astype(np.float32)
        self.pencil = np.zeros((size, size), np.float32)
        self.red = np.zeros((size, size), np.float32)

    # ---------- drawing helpers -------------------------------------------------------
    def canvas(self):
        """a supersampled 8-bit canvas; draw WHITE = object; returns (img, draw, scale)"""
        N = self.n * self.ss
        im = Image.new('L', (N, N), 0)
        return im, ImageDraw.Draw(im), float(self.ss)

    def to_mask(self, im):
        if im.size[0] != self.n:
            im = im.resize((self.n, self.n), Image.LANCZOS)
        return np.asarray(im, np.float32) / 255.0

    def lay(self, mask, opacity=0.96, height=0.0, halo=0.0, lift=None):
        """put an object on the paper.  mask in [0,1]; opacity = how much light it stops;
        height (in S px) = penumbra; halo = fuzz of loose fibres;
        lift = optional field in [0,1]: where 1 the object stands off the paper (extra blur)."""
        m = mask
        if height > 0:
            m = ndi.gaussian_filter(m, height * self.S)
        if lift is not None:
            soft = ndi.gaussian_filter(mask, (height + 5.0) * self.S)
            m = m * (1 - lift) + soft * lift
        t = 1.0 - opacity * m
        if halo > 0:
            t *= 1.0 - halo * np.clip(ndi.gaussian_filter(mask, 2.2 * self.S) * 1.6, 0, 1)
        self.T *= np.clip(t, 0, 1)

    def lay_transmission(self, t):
        self.T *= t

    def expose(self, weight=1.0, clear=True):
        self.dose += weight * self.T
        if clear:
            self.T = np.ones_like(self.T)

    # ---------- the coat ---------------------------------------------------------------
    def _coat(self, box):
        n, S, rng = self.n, self.S, self.rng
        x0, y0, x1, y1 = [v * n for v in box]
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
        # stroke bands
        band = 46 * S
        nb = int(np.ceil(n / band)) + 2
        offL = rng.normal(0, 13 * S, nb); offR = rng.normal(0, 13 * S, nb)
        bi = np.clip((np.arange(n) / band).astype(int), 0, nb - 1)
        # bristle noise: fine in y, long in x
        bristle = fbm((n, n), 5 * S, rng, octaves=2, aniso=(1.0, 14.0))
        rowL = offL[bi] + ndi.gaussian_filter1d(rng.normal(0, 30 * S, n), 2.0 * S) * 0.30
        rowR = offR[bi] + ndi.gaussian_filter1d(rng.normal(0, 30 * S, n), 2.0 * S) * 0.30
        soft = 9 * S
        left = (xx - (x0 + rowL[:, None]) + bristle * 11 * S) / soft
        right = ((x1 + rowR[:, None]) - xx + bristle * 11 * S) / soft
        wav_t = ndi.gaussian_filter1d(rng.normal(0, 26 * S, n), 30 * S) * 3.0
        wav_b = ndi.gaussian_filter1d(rng.normal(0, 26 * S, n), 30 * S) * 3.0
        fine = fbm((n, n), 7 * S, rng, octaves=2, aniso=(1.0, 6.0))
        top = (yy - (y0 + wav_t[None, :]) + fine * 7 * S) / (5 * S)
        bot = ((y1 + wav_b[None, :]) - yy + fine * 7 * S) / (5 * S)
        c = np.clip(np.minimum(np.minimum(left, right), np.minimum(top, bot)), 0, 1)
        c = c * c * (3 - 2 * c)
        # dry-brush streaks near the stroke ends
        d_end = np.minimum(xx - x0, x1 - xx)
        dry = np.clip(1 - d_end / (70 * S), 0, 1)
        c *= 1 - dry * np.clip(0.55 * bristle + 0.12, 0, 0.6)
        # thickness of the coat: streaks + blotches
        return c.astype(np.float32)

    # ---------- develop ----------------------------------------------------------------
    def develop(self, gamma=1.15, k=3.4, dust=1.0, stains=1.0):
        n, S, rng = self.n, self.S, self.rng
        D = np.clip(self.dose, 0, 1.2)
        dens = (1 - np.exp(-k * D ** gamma)) / (1 - np.exp(-k))
        dens = np.clip(dens * self.coat * self.thick, 0, 1.08)
        # paper grain: blue pools in the valleys, the peaks rub pale
        g1 = fbm((n, n), 2.6 * S, rng, octaves=2)
        g2 = fbm((n, n), 9 * S, rng, octaves=2)
        grain = 0.65 * g1 + 0.35 * g2
        dens = dens * (1 + 0.085 * grain) - 0.012 * np.clip(grain, 0, 1) * (dens > 0.5)
        # wash: a soft tide mark just inside the edge of the coat, blue bleeding a hair outside
        edge = ndi.gaussian_filter(self.coat, 5 * S)
        tide = np.clip(self.coat - ndi.gaussian_filter(self.coat, 16 * S), 0, 1)
        dens = dens * (1 + 0.10 * stains * tide)
        bleed = np.clip(ndi.gaussian_filter(dens, 3.5 * S) - dens, 0, 1) * (self.coat < 0.5)
        dens = dens + 0.35 * bleed
        # dust and hairs that lay on the paper during the exposure: small pale specks
        if dust > 0:
            nd = int(70 * dust)
            sp = np.zeros((n, n), np.float32)
            ys = rng.integers(0, n, nd); xs = rng.integers(0, n, nd)
            sp[ys, xs] = rng.uniform(0.5, 1.0, nd)
            sp = ndi.gaussian_filter(sp, 1.1 * S) * (2 * np.pi * (1.1 * S) ** 2)
            dens *= 1 - 0.75 * np.clip(sp, 0, 1)
            # a few darker flecks of undissolved salt
            fl = np.zeros((n, n), np.float32)
            ys = rng.integers(0, n, nd // 2); xs = rng.integers(0, n, nd // 2)
            fl[ys, xs] = 1
            fl = ndi.gaussian_filter(fl, 0.9 * S) * (2 * np.pi * (0.9 * S) ** 2)
            dens += 0.10 * np.clip(fl, 0, 1) * self.coat
        dens = np.clip(dens, 0, 1)
        rgb = np.empty((n, n, 3), np.float32)
        for ch in range(3):
            rgb[..., ch] = np.interp(dens, RAMP_X, RAMP[:, ch])
        # paper tone and tooth
        tooth = 1 + 0.018 * grain + 0.012 * fbm((n, n), 300 * S, rng, octaves=2)
        rgb *= tooth[..., None]
        # faint foxing-free warm vignette of an old sheet
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n - 0.5
        vig = 1 - 0.035 * np.clip((xx ** 2 + yy ** 2) * 2.2, 0, 1)
        rgb *= vig[..., None]
        # pencil
        if self.pencil.max() > 0:
            p = self.pencil * (0.78 + 0.22 * np.clip(g1 * 1.5, -1, 1))
            p = np.clip(p, 0, 1)[..., None]
            rgb = rgb * (1 - 0.80 * p) + np.array([0.27, 0.27, 0.30], np.float32) * 0.80 * p
        if self.red.max() > 0:
            r = np.clip(self.red * (0.80 + 0.25 * g2), 0, 1)[..., None]
            rgb = rgb * (1 - 0.85 * r) + rgb * np.array([0.80, 0.22, 0.16], np.float32) * 0.85 * r
        self.rgb = np.clip(rgb, 0, 1)
        return self.rgb

    # ---------- margin --------------------------------------------------------------
    def text(self, s, xy, size, italic=True, anchor='mm', layer='pencil', font=None, spacing=0):
        """xy in fractions of the sheet, size in S px"""
        N = self.n
        im = Image.new('L', (N, N), 0); d = ImageDraw.Draw(im)
        f = ImageFont.truetype(font or (SERIF_I if italic else SERIF), int(round(size * self.S)))
        if spacing:
            # letter-spaced capitals
            x, y = xy[0] * N, xy[1] * N
            w = sum(d.textlength(ch, font=f) + spacing * self.S for ch in s) - spacing * self.S
            x -= w / 2
            for ch in s:
                d.text((x, y), ch, fill=255, font=f, anchor='lm'); x += d.textlength(ch, font=f) + spacing * self.S
        else:
            d.text((xy[0] * N, xy[1] * N), s, fill=255, font=f, anchor=anchor)
        a = np.asarray(im, np.float32) / 255.0
        if layer == 'mask':
            return a
        if layer == 'pencil':
            self.pencil = np.maximum(self.pencil, a)
        else:
            self.red = np.maximum(self.red, a)

    def stamp(self, mask):
        self.red = np.maximum(self.red, mask)

    def save(self, path):
        Image.fromarray((self.rgb * 255 + 0.5).astype(np.uint8)).save(path)


# ---------- objects ----------------------------------------------------------------------
def chaikin(P, closed=True, it=3):
    P = np.asarray(P, float)
    for _ in range(it):
        Q = np.roll(P, -1, axis=0) if closed else P[1:]
        A = P if closed else P[:-1]
        a = 0.75 * A + 0.25 * Q; b = 0.25 * A + 0.75 * Q
        P = np.empty((2 * len(a), 2)); P[0::2] = a; P[1::2] = b
    return P


def resample(P, step, closed=True):
    if closed: P = np.vstack([P, P[:1]])
    d = np.hypot(*np.diff(P, axis=0).T); s = np.concatenate([[0], np.cumsum(d)])
    t = np.arange(0, s[-1], step)
    return np.stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])], 1)


def draw_cord(draw, P, w, ss, ply=True, fill=255, phase=0.0):
    """a plied thread along the polyline P (px); w = diameter (px).  Drawn as overlapping
    slanted ellipses so the edge is scalloped like twisted yarn."""
    P = np.asarray(P) * ss; w = w * ss
    step = 0.42 * w
    Q = resample(P, step, closed=False)
    if len(Q) < 2: return
    tan = np.gradient(Q, axis=0); tan /= np.maximum(np.hypot(tan[:, 0], tan[:, 1]), 1e-9)[:, None]
    if not ply:
        draw.line([tuple(p) for p in Q], fill=fill, width=int(round(w)), joint='curve'); return
    draw.line([tuple(p) for p in Q], fill=fill, width=max(1, int(round(w * 0.62))), joint='curve')
    ang0 = np.deg2rad(34)
    a = 0.80 * w; b = 0.36 * w
    th = np.linspace(0, 2 * np.pi, 14, endpoint=False)
    ex = a * np.cos(th); ey = b * np.sin(th)
    for i, (p, t) in enumerate(zip(Q, tan)):
        ang = np.arctan2(t[1], t[0]) + ang0
        c, s = np.cos(ang), np.sin(ang)
        off = 0.10 * w * np.sin(i * 1.7 + phase)
        cx = p[0] - t[1] * off; cy = p[1] + t[0] * off
        pts = [(cx + c * x - s * y, cy + s * x + c * y) for x, y in zip(ex, ey)]
        draw.polygon(pts, fill=fill)


def button(sheet, cx, cy, r, holes=4, rng=None, kind=0):
    """returns a TRANSMISSION field contribution for a button (pearl: translucent with rings)."""
    n = sheet.n
    R = int(r * 1.5) + 4
    x0, y0 = int(cx) - R, int(cy) - R
    yy, xx = np.mgrid[y0:y0 + 2 * R, x0:x0 + 2 * R].astype(np.float32)
    d = np.hypot(xx - cx, yy - cy)
    aa = lambda e: np.clip(e + 0.5, 0, 1)
    disc = aa(r - d)
    # thickness profile: thick rim, dished centre
    t = d / r
    thick = 0.80 + 0.20 * np.clip((t - 0.62) / 0.20, 0, 1) - 0.12 * np.clip((t - 0.9) / 0.1, 0, 1)
    if kind == 1:  # flat shirt button with a groove
        thick = 0.90 - 0.22 * np.exp(-((t - 0.70) / 0.05) ** 2) + 0.08 * np.clip((t - 0.8) / 0.2, 0, 1)
    op = np.clip(thick, 0, 1) * 0.97
    T = 1 - op * disc
    hr = r * (0.105 if holes == 4 else 0.12); hd = r * (0.235 if holes == 4 else 0.22)
    rot = rng.uniform(0, np.pi) if rng is not None else 0.4
    for k in range(holes):
        a = rot + 2 * np.pi * k / holes
        hx, hy = cx + hd * np.cos(a), cy + hd * np.sin(a)
        hole = aa(hr - np.hypot(xx - hx, yy - hy))
        T = T * (1 - hole) + hole
    ys = slice(max(0, y0), min(n, y0 + 2 * R)); xs = slice(max(0, x0), min(n, x0 + 2 * R))
    sub = T[ys.start - y0: ys.stop - y0, xs.start - x0: xs.stop - x0]
    full = np.ones((n, n), np.float32)
    full[ys, xs] = sub
    return full
