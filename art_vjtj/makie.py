"""makie.py — a small lacquer-and-gold (maki-e) engine.  Fable 5.2, day 2.

The look is three things:
  * a black urushi ground that is not flat: a slow sheen, a warm undertone, a few polishing hairs;
  * METAL that is either sprinkled (dust: independent flakes, each with its own facet brightness,
    density is the drawing) or laid (leaf: a solid mask shaded as a low relief with a burnished
    highlight and a darker foot);
  * shell (raden): shards with thin-film colours, cracked along a Voronoi net.
Everything is composited "over" in linear light, ground first, then dust, leaf, shell, red.

    P = Panel(4096, seed=1, ss=2)
    m = P.mask(lambda d, S: d.line(...))        # PIL drawing at ss scale -> float mask at size
    P.dust(density, KIN); P.leaf(m, KIN, height=6); P.raden(m2); P.finish().save(...)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

KIN = np.array([1.00, 0.66, 0.17])      # yellow gold
AOKIN = np.array([0.70, 0.78, 0.36])    # green gold (gold-silver alloy)
GIN = np.array([0.66, 0.72, 0.80])      # silver
AKAGANE = np.array([0.95, 0.52, 0.30])  # copper gold
SHU = np.array([0.86, 0.13, 0.07])      # cinnabar
URUSHI = np.array([0.0030, 0.0024, 0.0034])

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"


def blur(a, s):
    return ndi.gaussian_filter(a, s, mode="nearest") if s > 0 else a


class Panel:
    def __init__(self, size=1024, seed=0, ss=2, ground=URUSHI, sheen=1.0):
        self.S = size
        self.ss = ss
        self.rng = np.random.default_rng(seed)
        S = size
        y, x = np.mgrid[0:S, 0:S].astype(np.float32) / S
        self.x, self.y = x, y
        img = np.empty((S, S, 3), np.float32)
        img[:] = ground
        # slow sheen: a broad soft reflection of a window, upper left, bluish, and a warm one low right
        sh = np.exp(-(((x - 0.22) * 0.9 + (y - 0.10) * 0.5) ** 2) / 0.05) * np.exp(-((y - 0.15) ** 2) / 0.25)
        img += sheen * 0.007 * sh[..., None] * np.array([0.75, 0.85, 1.0], np.float32)
        wm = np.exp(-((x - 0.85) ** 2 + (y - 0.95) ** 2) / 0.18)
        img += sheen * 0.003 * wm[..., None] * np.array([1.0, 0.55, 0.35], np.float32)
        # low-frequency unevenness of the polish
        n = blur(self.rng.standard_normal((S // 16 + 2, S // 16 + 2)).astype(np.float32), 2.0)
        n = np.asarray(Image.fromarray(n).resize((S, S), Image.BICUBIC))
        img *= (1 + 0.35 * n / (np.abs(n).max() + 1e-9))[..., None]
        self.img = np.clip(img, 0, None)
        self.glow = np.zeros((S, S, 3), np.float32)

    # ---------- masks ----------
    def mask(self, fn):
        """fn(draw, scale): draw white on a black 'L' canvas of side S*ss. Returns float mask SxS."""
        Sb = self.S * self.ss
        im = Image.new("L", (Sb, Sb), 0)
        fn(ImageDraw.Draw(im), self.ss)
        if self.ss > 1:
            im = im.resize((self.S, self.S), Image.LANCZOS)
        return np.clip(np.asarray(im, np.float32) / 255.0, 0, 1)

    def text_mask(self, items):
        """items: list of (x, y, string, px, italic, anchor) in panel pixels."""
        def fn(d, s):
            for (tx, ty, st, px, it, anc) in items:
                f = ImageFont.truetype(SERIF_I if it else SERIF, int(px * s))
                d.text((tx * s, ty * s), st, font=f, fill=255, anchor=anc)
        return self.mask(fn)

    # ---------- metal ----------
    def over(self, colour, alpha):
        a = np.clip(alpha, 0, 1)[..., None]
        self.img = self.img * (1 - a) + np.asarray(colour, np.float32) * a

    def dust(self, density, metal=KIN, grain=0.7, sparkle=0.06, gain=1.0, glow=0.25):
        """Sprinkled powder. density in [0,1] = fraction of pixels carrying a flake."""
        S = self.S
        r = self.rng.random((S, S), dtype=np.float32)
        hit = (r < np.clip(density, 0, 1)).astype(np.float32)
        # facet brightness: most flakes are dull, a few face the light
        f = self.rng.random((S, S), dtype=np.float32)
        br = 0.28 + 0.55 * f ** 2
        sp = (self.rng.random((S, S), dtype=np.float32) < sparkle).astype(np.float32)
        br = br + sp * (0.9 + 1.6 * self.rng.random((S, S), dtype=np.float32))
        v = blur(hit * br, grain) * (1.0 + 2 * np.pi * grain ** 2) * 0.62 * gain
        a = np.clip(blur(hit, grain) * (1.0 + 2 * np.pi * grain ** 2), 0, 1)
        col = np.asarray(metal, np.float32)
        tint = col[None, None, :] * v[..., None]
        # brightest flakes go white-hot
        hot = np.clip(v - 0.9, 0, None)[..., None]
        tint = tint + hot * 0.6
        self.img = self.img * (1 - a[..., None] * 0.9) + tint
        if glow:
            self.glow += tint * glow

    def leaf(self, m, metal=KIN, height=4.0, light=(-0.55, -0.75), burnish=0.35, tone=1.0,
             edge_dust=0.0, glow=0.35, texture=None):
        """Laid metal shaded as a low relief. m: float mask; height: relief radius in px."""
        S = self.S
        h = blur(m, height) * m                   # rounded pillow
        gy, gx = np.gradient(blur(h, 0.8))
        k = height * 1.6
        nx, ny = -gx * k, -gy * k
        nz = 1.0 / np.sqrt(1 + nx * nx + ny * ny)
        lx, ly = light
        lz = 0.55
        ln = (lx * lx + ly * ly + lz * lz) ** 0.5
        lam = np.clip((nx * nz * lx + ny * nz * ly + nz * lz) / ln, 0, 1)
        # specular around the half vector (viewer on the z axis)
        hx, hy, hz = lx / ln, ly / ln, lz / ln + 1.0
        hn = (hx * hx + hy * hy + hz * hz) ** 0.5
        spec = np.clip((nx * nz * hx + ny * nz * hy + nz * hz) / hn, 0, 1) ** 40
        if texture is None:
            # burnishing streaks: anisotropic noise
            t = self.rng.standard_normal((S, S)).astype(np.float32)
            t = ndi.gaussian_filter(t, (0.6, 5.0))
            t = t / (t.std() + 1e-9)
            texture = t
        base = (0.50 + 0.55 * lam) * (1 + 0.07 * texture) * tone
        col = np.asarray(metal, np.float32)
        c = col[None, None, :] * base[..., None] + (burnish * spec)[..., None] * (0.6 * col + 0.4)
        a = np.clip(m, 0, 1)
        self.img = self.img * (1 - a[..., None]) + c * a[..., None]
        if edge_dust > 0:
            halo = np.clip(blur(m, height * 2.5) - m, 0, 1) * edge_dust
            self.dust(halo, metal, grain=0.6, glow=0.0)
        if glow:
            self.glow += c * a[..., None] * glow

    def raden(self, m, cell=28.0, hue0=0.0, sat=0.55, val=0.95, crack=0.9, palette=None, shade=None):
        """Mother-of-pearl inlay: Voronoi shards, each with a thin-film colour drifting across it."""
        S = self.S
        rng = self.rng
        ys, xs = np.nonzero(m > 0.02)
        if len(ys) == 0:
            return
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        H, W = y1 - y0, x1 - x0
        n = max(6, int(H * W / (cell * cell)))
        py, px = rng.random(n) * H, rng.random(n) * W
        from scipy.spatial import cKDTree
        tree = cKDTree(np.c_[py, px])
        yy, xx = np.mgrid[0:H, 0:W]
        d, idx = tree.query(np.c_[yy.ravel(), xx.ravel()], k=2)
        edge = (d[:, 1] - d[:, 0]).reshape(H, W)
        cid = idx[:, 0].reshape(H, W)
        # thin-film phase: per-shard offset + per-shard gradient direction
        ph0 = rng.random(n)
        ang = rng.random(n) * 2 * np.pi
        fr = (0.4 + 0.9 * rng.random(n)) / cell
        ph = ph0[cid] + fr[cid] * ((xx - px[cid]) * np.cos(ang[cid]) + (yy - py[cid]) * np.sin(ang[cid])) * 0.35
        ph = ph + hue0
        if palette is None:
            # abalone: pink, pale gold, sea green, sky, violet
            palette = np.array([[1.00, 0.72, 0.86], [1.00, 0.93, 0.74], [0.62, 0.96, 0.82],
                                [0.62, 0.84, 1.00], [0.80, 0.72, 1.00]], np.float32)
        K = len(palette)
        t = (ph % 1.0) * K
        i0 = np.floor(t).astype(int) % K
        w = (t - np.floor(t))[..., None]
        w = w * w * (3 - 2 * w)
        col = palette[i0] * (1 - w) + palette[(i0 + 1) % K] * w
        lum = (0.55 + 0.40 * rng.random(n) ** 1.5 + 0.35 * (rng.random(n) < 0.10))[cid]
        # fine lamellar shimmer
        sh = ndi.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), (0.7, 3.0))
        sh = sh / (sh.std() + 1e-9)
        col = col * (val * lum * (1 + 0.06 * sh))[..., None]
        grey = col.mean(-1, keepdims=True)
        col = grey + (col - grey) * (sat / 0.55)
        ck = np.clip(edge / 1.1, 0, 1) ** 0.7
        col = col * (1 - crack * (1 - ck))[..., None]
        if shade is not None:
            col = col * shade[y0:y1, x0:x1][..., None]
        a = m[y0:y1, x0:x1][..., None]
        self.img[y0:y1, x0:x1] = self.img[y0:y1, x0:x1] * (1 - a) + col * a
        self.glow[y0:y1, x0:x1] += col * a * 0.45

    # ---------- finish ----------
    def finish(self, bloom=(3.0, 14.0), bloom_gain=(0.22, 0.10), vignette=0.35, gamma=2.2, expo=1.0):
        S = self.S
        img = self.img.copy()
        for s, g in zip(bloom, bloom_gain):
            sc = S / 1024.0
            b = np.stack([blur(self.glow[..., c], s * sc) for c in range(3)], -1)
            img += g * b
        x, y = self.x - 0.5, self.y - 0.5
        v = 1 - vignette * np.clip((x * x + y * y) / 0.5, 0, 1) ** 1.5
        img *= v[..., None] * expo
        # soft shoulder so gold never clips to flat yellow
        img = 1 - np.exp(-1.25 * img)
        img = img / (1 - np.exp(-1.25))
        img = np.clip(img, 0, 1) ** (1 / gamma)
        d = (self.rng.random((S, S, 1), dtype=np.float32) - 0.5) / 255.0
        return Image.fromarray((np.clip(img + d, 0, 1) * 255 + 0.5).astype(np.uint8))
