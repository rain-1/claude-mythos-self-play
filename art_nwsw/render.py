"""Gelato-pizza renderer: a top-down height field with soft shadows.
Cloth with sparse sorbet polka dots, porcelain plates, glossy sorbet slices with
waffle-cone crusts and sprinkles.  Everything in pixel units; float32 throughout."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, map_coordinates

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_M = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)

# sorbet wheel (Opus 5.5 box), cyclic
WHEEL = [hexc(c) for c in ["#ff8fa3", "#ffb38a", "#ffd98a", "#d9ef8b", "#9fe3c0",
                           "#8fd3f4", "#9fb4ff", "#c7a4ff", "#f5a3e0"]]
CORAL = hexc("#ff6f61")
PLUM = hexc("#5c4d66")

def wheel(t, sat=1.0):
    t = (t % 1.0) * len(WHEEL)
    i = int(np.floor(t)) % len(WHEEL); j = (i + 1) % len(WHEEL); f = t - np.floor(t)
    c = (WHEEL[i] ** (1 - f)) * (WHEEL[j] ** f)          # geometric interpolation
    return 1 - (1 - c) * sat

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)


class Canvas:
    def __init__(self, W, H, seed=1):
        self.W, self.H = W, H
        self.h = np.zeros((H, W), np.float32)          # height (px)
        self.alb = np.ones((H, W, 3), np.float32)      # albedo
        self.gloss = np.zeros((H, W), np.float32)      # specular strength
        self.shin = np.full((H, W), 20, np.float32)    # shininess
        self.trans = np.zeros((H, W), np.float32)      # translucency (soft subsurface light)
        self.rng = np.random.default_rng(seed)
        self.exposure = 1.04
        self.translucency = 0.72
        self.window = True

    # ---------------- cloth ----------------
    def cloth(self, dot_r, spacing, base="#fbf8f4", tint=0.38, palette=None, seed=3):
        W, H = self.W, self.H
        rng = np.random.default_rng(seed)
        self.alb[:] = hexc(base)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        weave = 0.006 * (np.sin(xx * 1.9) * np.sin(yy * 1.9)) + 0.004 * rng.standard_normal((H, W)).astype(np.float32)
        self.alb *= (1 + weave)[..., None]
        pal = palette or WHEEL
        dx = spacing; dy = spacing * np.sqrt(3) / 2
        j = 0
        for row in range(-1, int(H / dy) + 2):
            off = (row % 2) * dx / 2
            for col in range(-1, int(W / dx) + 2):
                cx = col * dx + off + rng.normal(0, 0.02 * dx); cy = row * dy + rng.normal(0, 0.02 * dx)
                c = pal[(row * 3 + col * 5) % len(pal)]
                c = 1 - (1 - c) * tint
                x0, x1 = int(max(0, cx - dot_r - 2)), int(min(W, cx + dot_r + 3))
                y0, y1 = int(max(0, cy - dot_r - 2)), int(min(H, cy + dot_r + 3))
                if x0 >= x1 or y0 >= y1: continue
                d = np.hypot(xx[y0:y1, x0:x1] - cx, yy[y0:y1, x0:x1] - cy)
                a = np.clip(dot_r - d + 0.5, 0, 1)[..., None]
                self.alb[y0:y1, x0:x1] = self.alb[y0:y1, x0:x1] * (1 - a) + c * a * self.alb[y0:y1, x0:x1] / hexc(base)
                j += 1
        self.h += 0.25 * gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 1.5)

    # ---------------- plate ----------------
    def plate(self, cx, cy, Rw, Ro, base_h=10.0, rim_h=34.0, band="#c7a4ff"):
        """Porcelain plate: flat well radius Rw, rim up to Ro."""
        pad = int(Ro + 4)
        x0, x1 = int(max(0, cx - pad)), int(min(self.W, cx + pad))
        y0, y1 = int(max(0, cy - pad)), int(min(self.H, cy + pad))
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        rho = np.hypot(xx - cx, yy - cy)
        w = Ro - Rw
        t = (rho - Rw) / w
        # profile: well flat, steep-ish rise, rounded top near t=0.35, gentle fall to a rolled lip
        rise = smoothstep(0.0, 0.32, t) * rim_h
        fall = smoothstep(0.45, 1.0, t) * rim_h * 0.42
        prof = base_h + rise - fall
        lip = np.clip((Ro - rho) / 3.0, 0, 1)
        hp = np.where(rho <= Rw, base_h, prof) * lip
        a = np.clip(Ro - rho + 0.5, 0, 1)
        sl = (slice(y0, y1), slice(x0, x1))
        self.h[sl] = self.h[sl] * (1 - a) + hp * a
        porc = hexc("#fdfcff")
        bandc = 1 - (1 - hexc(band)) * 0.55
        al = np.broadcast_to(porc, rho.shape + (3,)).copy()
        bt = np.abs(rho - (Rw + 0.80 * w)) < 0.018 * w
        bt2 = np.abs(rho - (Rw + 0.86 * w)) < 0.006 * w
        al[bt | bt2] = bandc
        self.alb[sl] = self.alb[sl] * (1 - a[..., None]) + al * a[..., None]
        self.gloss[sl] = self.gloss[sl] * (1 - a) + 0.55 * a
        self.shin[sl] = np.where(a > 0.5, 60, self.shin[sl])
        self.plate_info = (cx, cy, Rw, Ro, base_h)

    # ---------------- slice ----------------
    def slice(self, ax, ay, th, ph, R, color, base_h, T=14.0, bevel=5.0, gap=1.3,
              crust=0.075, sprinkles=0, sp_seed=0, crust_col="#f9e2b4", outline=None):
        """Sector of radius R (px) with apex (ax, ay), centre direction th, half-angle ph."""
        ex = [ax, ax + R * np.cos(th - ph), ax + R * np.cos(th + ph), ax + R * np.cos(th)]
        ey = [ay, ay + R * np.sin(th - ph), ay + R * np.sin(th + ph), ay + R * np.sin(th)]
        # include arc extremes
        for ang in np.linspace(th - ph, th + ph, 9):
            ex.append(ax + R * np.cos(ang)); ey.append(ay + R * np.sin(ang))
        x0, x1 = int(max(0, min(ex) - 8)), int(min(self.W, max(ex) + 9))
        y0, y1 = int(max(0, min(ey) - 8)), int(min(self.H, max(ey) + 9))
        if x0 >= x1 or y0 >= y1: return
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        u = xx - ax; v = yy - ay
        c, s = np.cos(th), np.sin(th)
        lx = u * c + v * s; ly = -u * s + v * c                     # local frame, axis = +x
        rho = np.hypot(lx, ly)
        # signed distances (positive inside)
        d_arc = R - rho
        # edges: upper edge line through apex at angle +ph; inside means below it
        d_up = lx * np.sin(ph) - ly * np.cos(ph)
        d_lo = lx * np.sin(ph) + ly * np.cos(ph)
        sd = np.minimum(np.minimum(d_arc, d_up), d_lo) - gap
        cov = np.clip(sd + 0.5, 0, 1)
        if cov.max() <= 0: return
        # height profile: body + crust ridge
        body = T * smoothstep(-0.5, bevel, sd)
        cw = crust * R
        tc = np.clip((d_arc - gap) / cw, 0, 1)                       # 0 at rim, 1 inside crust boundary
        ridge = 7.0 * np.sin(np.pi * np.clip(tc, 0, 1)) ** 0.8 * (tc < 1)
        ridge *= smoothstep(-0.5, bevel, sd)
        hh = base_h + body + ridge
        # albedo
        col = np.broadcast_to(color, rho.shape + (3,)).copy()
        r01 = np.clip(rho / R, 0, 1)
        col *= (0.96 + 0.06 * r01)[..., None]                        # a touch lighter toward the crust
        # soften crust boundary over 1.5 px
        cb = np.clip((cw - (d_arc - gap)) / 1.5 + 0.5, 0, 1)
        cc = hexc(crust_col)
        # waffle crosshatch on the crust
        ang = np.arctan2(ly, lx)
        pa = rho / (cw * 0.5); pb = ang * R / (cw * 0.5)
        wav = 0.5 + 0.5 * np.cos(np.pi * (pa + pb)) * np.cos(np.pi * (pa - pb))
        wav = np.clip(wav * 1.6 - 0.3, 0, 1)
        crustc = cc[None, None, :] * (0.93 + 0.07 * wav)[..., None]
        col = col * (1 - cb[..., None]) + crustc * cb[..., None]
        hh = hh + cb * 1.6 * (wav - 0.5)
        sl = (slice(y0, y1), slice(x0, x1))
        self.h[sl] = self.h[sl] * (1 - cov) + hh * cov
        self.alb[sl] = self.alb[sl] * (1 - cov[..., None]) + col * cov[..., None]
        self.gloss[sl] = self.gloss[sl] * (1 - cov) + (0.75 * (1 - cb) + 0.05 * cb) * cov
        self.shin[sl] = np.where(cov > 0.5, 70 * (1 - cb) + 12 * cb, self.shin[sl])
        self.trans[sl] = self.trans[sl] * (1 - cov) + self.translucency * (1 - 0.6 * cb) * cov
        if outline is not None:
            ring = np.clip(1.0 - np.abs(sd + 2.5) / 2.2, 0, 1) * (sd > -4)
            oc = hexc(outline) if isinstance(outline, str) else outline
            self.alb[sl] = self.alb[sl] * (1 - ring[..., None]) + oc * ring[..., None]
        # sprinkles
        if sprinkles:
            rng = np.random.default_rng(sp_seed)
            area = ph * R * R
            n = int(sprinkles * area / 1e4)
            pal = [hexc("#ffffff"), hexc("#ff8fa3"), hexc("#ffd98a"), hexc("#9fe3c0"), hexc("#8fd3f4"), hexc("#c7a4ff")]
            L = 0.013 * R + 6; Wd = 0.0045 * R + 2.2
            for k in range(n):
                rr = R * np.sqrt(rng.uniform(0.02, (1 - crust - 0.03) ** 2))
                aa = rng.uniform(-ph, ph)
                if rr * np.sin(ph - abs(aa)) < L * 0.7 + gap + 2: continue
                px = ax + rr * np.cos(th + aa); py = ay + rr * np.sin(th + aa)
                self.sprinkle(px, py, rng.uniform(0, np.pi), L, Wd, pal[rng.integers(len(pal))])

    def sprinkle(self, px, py, a, L, Wd, col):
        r = L / 2 + Wd + 2
        x0, x1 = int(max(0, px - r)), int(min(self.W, px + r + 1))
        y0, y1 = int(max(0, py - r)), int(min(self.H, py + r + 1))
        if x0 >= x1 or y0 >= y1: return
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        u = xx - px; v = yy - py
        t = np.clip(u * np.cos(a) + v * np.sin(a), -L / 2, L / 2)
        d = np.hypot(u - t * np.cos(a), v - t * np.sin(a))
        cov = np.clip(Wd / 2 - d + 0.5, 0, 1)
        prof = np.sqrt(np.clip(1 - (d / (Wd / 2 + 0.01)) ** 2, 0, 1)) * Wd * 0.55
        sl = (slice(y0, y1), slice(x0, x1))
        self.h[sl] += prof * cov
        self.alb[sl] = self.alb[sl] * (1 - cov[..., None]) + col * cov[..., None]
        self.gloss[sl] = np.maximum(self.gloss[sl], 0.5 * cov)

    def bead(self, px, py, rad, col, height=8.0):
        r = rad + 3
        x0, x1 = int(max(0, px - r)), int(min(self.W, px + r + 1))
        y0, y1 = int(max(0, py - r)), int(min(self.H, py + r + 1))
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = np.hypot(xx - px, yy - py)
        cov = np.clip(rad - d + 0.5, 0, 1)
        prof = np.sqrt(np.clip(1 - (d / rad) ** 2, 0, 1)) * height
        sl = (slice(y0, y1), slice(x0, x1))
        self.h[sl] = np.maximum(self.h[sl], self.h[sl] + prof * cov)
        self.alb[sl] = self.alb[sl] * (1 - cov[..., None]) + col * cov[..., None]
        self.gloss[sl] = np.maximum(self.gloss[sl], 0.9 * cov)
        self.shin[sl] = np.where(cov > 0.5, 90, self.shin[sl])

    # ---------------- light ----------------
    def shade(self, light_az=np.radians(225), light_el=np.radians(38), shadow_len=260, soft=0.10,
              shadow_col="#9fa8e8", shadow_strength=0.42, ao_strength=0.5):
        H, W = self.H, self.W
        h = self.h
        gy, gx = np.gradient(gaussian_filter(h, 0.7))
        n = np.stack([-gx, -gy, np.ones_like(h)], -1)
        n /= np.linalg.norm(n, axis=-1, keepdims=True)
        # light: azimuth measured in image coords (x right, y down); 225deg = from top-left
        lx, ly = np.cos(light_az), np.sin(light_az)
        L = np.array([lx * np.cos(light_el), ly * np.cos(light_el), np.sin(light_el)], np.float32)
        diff = np.clip(n @ L, 0, 1)
        # soft shadows by height-field march toward the light, on a half-res grid
        f = 2
        hs = h[::f, ::f]
        occ = np.zeros_like(hs)
        tanE = np.tan(light_el)
        steps = np.unique(np.geomspace(1, shadow_len / f, 48).astype(int))
        yy, xx = np.mgrid[0:hs.shape[0], 0:hs.shape[1]].astype(np.float32)
        for k in steps:
            dx, dy = lx * k, ly * k
            hk = map_coordinates(hs, [yy + dy, xx + dx], order=1, mode='nearest')
            rise = hk - hs - k * f * tanE
            occ = np.maximum(occ, np.clip(rise / (1.0 + soft * k * f), 0, 1))
        occ = np.asarray(Image.fromarray(occ).resize((W, H), Image.BILINEAR))
        occ = gaussian_filter(occ, 1.0)
        # ambient occlusion from local height deficit
        ao = np.clip((gaussian_filter(h, 6) - h) / 8.0, 0, 1) * 0.6 + np.clip((gaussian_filter(h, 22) - h) / 20.0, 0, 1) * 0.4
        sky = 0.62 + 0.38 * n[..., 2]
        shc = hexc(shadow_col)
        lit2 = 0.50 * sky + 0.62 * diff * (1 - shadow_strength * occ)
        # translucent materials: light diffuses inside, so blend toward a blurred light field
        soft_l = gaussian_filter(0.50 + 0.62 * np.sin(light_el) * (1 - shadow_strength * occ), 4)
        lit2 = lit2 * (1 - self.trans) + np.maximum(soft_l, lit2) * self.trans
        lit = lit2[..., None]
        tintsh = 1 - (1 - shc) * (shadow_strength * 0.9 * occ)[..., None]
        col = self.alb * lit * tintsh * (1 - ao_strength * ao * (1 - 0.8 * self.trans))[..., None]
        # specular (view from +z)
        Hv = L + np.array([0, 0, 1], np.float32); Hv /= np.linalg.norm(Hv)
        spec = np.clip(n @ Hv, 0, 1) ** self.shin * self.gloss * (1 - occ)
        lit_flat = 0.50 + 0.62 * np.sin(light_el)
        col = col * (self.exposure / lit_flat) + 0.55 * spec[..., None]
        # soft shoulder: linear to 0.82, then exponential approach to 1
        if self.window:
            yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
            g = ((xx_ / W) + (yy_ / H)) / 2.0                         # 0 at top-left, 1 bottom-right
            warm = np.array([1.025, 1.005, 0.975], np.float32); cool = np.array([0.975, 0.99, 1.03], np.float32)
            col = col * (warm * (1 - g)[..., None] + cool * g[..., None])
        k0 = 0.82
        col = np.where(col < k0, col, k0 + (1 - k0) * (1 - np.exp(-(col - k0) / (1 - k0))))
        self.img = np.clip(col, 0, 1)
        return self.img

    def save(self, path, down=1):
        im = Image.fromarray((np.clip(self.img, 0, 1) ** (1 / 1.0) * 255 + 0.5).astype(np.uint8))
        if down > 1:
            im = im.resize((self.W // down, self.H // down), Image.LANCZOS)
        im.save(path)
        return im


def caption(im, lines, x, y, sizes, fonts, colors, gap=1.25):
    d = ImageDraw.Draw(im)
    for text, sz, fnt, colr in zip(lines, sizes, fonts, colors):
        F = ImageFont.truetype(fnt, sz)
        d.text((x, y), text, font=F, fill=tuple(int(255 * c) for c in colr))
        y += int(sz * gap)
    return y


def _capsule_sd(xx, yy, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
    return np.hypot(xx - x0 - t * dx, yy - y0 - t * dy)

def cutter(cv, cx, cy, ang, Rb, handle_col="#9fe3c0", hub_col="#b9a6f0", base=0.0):
    """A pizza wheel lying on the cloth: blade centred (cx,cy), handle along angle ang."""
    k = Rb / 150
    ux, uy = np.cos(ang), np.sin(ang)
    hx0, hy0 = cx + ux * Rb * 1.55, cy + uy * Rb * 1.55
    hx1, hy1 = cx + ux * Rb * 4.4, cy + uy * Rb * 4.4
    pad = Rb * 4.9
    x0, x1 = int(max(0, cx - pad)), int(min(cv.W, cx + pad))
    y0, y1 = int(max(0, cy - pad)), int(min(cv.H, cy + pad))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    sl = (slice(y0, y1), slice(x0, x1))
    def put(hh, cov, col, gloss, shin, trans=0.0):
        cv.h[sl] = cv.h[sl] * (1 - cov) + hh * cov
        cv.alb[sl] = cv.alb[sl] * (1 - cov[..., None]) + col * cov[..., None]
        cv.gloss[sl] = cv.gloss[sl] * (1 - cov) + gloss * cov
        cv.shin[sl] = np.where(cov > 0.5, shin, cv.shin[sl])
        cv.trans[sl] = cv.trans[sl] * (1 - cov) + trans * cov
    # fork (two arms) from the hub to the handle
    for sgn in (-1, 1):
        px, py = -uy * sgn * Rb * 0.16, ux * sgn * Rb * 0.16
        d = _capsule_sd(xx, yy, cx + px, cy + py, hx0 + px * 0.5, hy0 + py * 0.5)
        w = 0.085 * Rb
        cov = np.clip(w - d + 0.5, 0, 1)
        hh = base + 14 * k + np.sqrt(np.clip(1 - (d / w) ** 2, 0, 1)) * 6 * k
        put(hh, cov, hexc("#e9e6f5"), 0.9, 120)
    # blade
    d = np.hypot(xx - cx, yy - cy)
    cov = np.clip(Rb - d + 0.5, 0, 1)
    edge = np.clip((Rb - d) / (0.16 * Rb), 0, 1)
    hh = base + 6 * k + 5 * k * np.sqrt(edge)
    ring = 0.5 + 0.5 * np.cos(d / Rb * 40)            # faint brushed rings
    col = hexc("#eeeaf8")[None, None, :] * (0.97 + 0.03 * ring)[..., None]
    bev = np.clip(1 - np.abs(d - 0.90 * Rb) / (0.035 * Rb), 0, 1)
    col = col * (1 - 0.10 * bev)[..., None] + hexc("#ffffff") * 0.0
    put(hh, cov, col, 0.95, 140)
    # hub cap
    cov = np.clip(0.26 * Rb - d + 0.5, 0, 1)
    hh = base + 11 * k + np.sqrt(np.clip(1 - (d / (0.26 * Rb)) ** 2, 0, 1)) * 12 * k
    put(hh, cov, hexc(hub_col), 0.8, 90, 0.3)
    # handle
    d = _capsule_sd(xx, yy, hx0, hy0, hx1, hy1)
    w = 0.30 * Rb
    cov = np.clip(w - d + 0.5, 0, 1)
    hh = base + np.sqrt(np.clip(1 - (d / w) ** 2, 0, 1)) * 40 * k
    # ferrule band near the fork end
    tpar = ((xx - hx0) * ux + (yy - hy0) * uy) / (Rb * 2.85)
    col = np.broadcast_to(hexc(handle_col), d.shape + (3,)).copy()
    band = (tpar > 0.0) & (tpar < 0.09)
    col[band] = hexc("#f5f3fb")
    put(hh, cov, col, 0.75, 70, 0.35)
