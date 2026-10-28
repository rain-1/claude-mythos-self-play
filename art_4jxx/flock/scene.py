"""Pastel dawn lake with a murmuration.  python3 scene.py cfg.json out.png

The flock is drawn as Beer-Lambert ink: absorbance ∝ number of birds on the
line of sight.  The 3-D density is uniform (volume-preserving flow), so every
dark seam is the sheet seen edge-on — the shape is made by where we stand.
"""
import sys, json, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

def smooth(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

def lerpc(stops, t):
    t = np.clip(t, 0, 1)
    xs = np.array([s[0] for s in stops]); cs = np.array([s[1] for s in stops], float)
    out = np.empty(t.shape + (3,))
    for c in range(3): out[..., c] = np.interp(t, xs, cs[:, c])
    return out

def fbm1(x, seed, oct=5):
    rng = np.random.default_rng(seed); v = np.zeros_like(x); a = 1.0
    for o in range(oct):
        f = 2 ** o; ph = rng.uniform(0, 100)
        g = rng.normal(size=int(f * 8 + 4))
        xi = (x * f * 8 + ph) % (len(g) - 1)
        i = xi.astype(int); fr = smooth(xi - i)
        v += a * (g[i] * (1 - fr) + g[i + 1] * fr); a *= 0.5
    return v

def value_noise2(H, W, cell, seed):
    rng = np.random.default_rng(seed)
    gh, gw = H // cell + 3, W // cell + 3
    g = rng.normal(size=(gh, gw))
    return ndi.zoom(g, cell, order=3)[:H, :W]

class Cam:
    def __init__(s, W, H, fov, hor, cam_h):
        s.W, s.H = W, H; s.f = W / 2 / np.tan(np.radians(fov) / 2)
        s.cx = W / 2; s.cy = hor * H; s.h = cam_h
    def proj(s, P):            # P: world (x right, y up rel. eye, z forward)
        return s.cx + s.f * P[:, 0] / P[:, 2], s.cy - s.f * P[:, 1] / P[:, 2]

def sky(cfg, H, W, cam, yy):
    # elevation-like parameter: 0 at horizon, 1 at top
    e = (cam.cy - yy) / cam.cy
    stops = [(0.0, cfg["sky_h"]), (0.10, cfg["sky_1"]), (0.32, cfg["sky_2"]), (0.65, cfg["sky_3"]), (1.0, cfg["sky_top"])]
    return lerpc(stops, e)

def render(cfg, out):
    W = H = cfg["size"]; S = W / 1024
    ss = cfg.get("ss", 2)
    cam = Cam(W, H, cfg["fov"], cfg["horizon"], cfg["cam_h"])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # ---------------- sky (full frame, as if no water) ----------------
    skyimg = sky(cfg, H, W, cam, yy)
    # sun glow
    sx, sy = cfg["sun"][0] * W, cfg["sun"][1] * H
    d = np.hypot(xx - sx, (yy - sy) * 1.0) / W
    glow = 0.55 * np.exp(-(d / 0.035) ** 2) + 0.35 * np.exp(-d / 0.09) + 0.18 * np.exp(-d / 0.3)
    sunc = np.array(cfg["sun_col"])
    skyimg = skyimg + glow[..., None] * (sunc - skyimg) * 0.9
    disc = smooth((0.010 - d) / 0.0015)
    skyimg = skyimg * (1 - disc[..., None]) + disc[..., None] * np.array([1.0, 0.995, 0.97])
    # stratus clouds: long thin streaks, lit from below on their sun side
    for ci, cl in enumerate(cfg["clouds"]):
        cyp, thick, x0, x1, col, a = cl
        cyp *= H; thick *= H
        edge = cyp + thick * (0.8 * fbm1(xx[0] / W * 0.8, 100 + ci, 3))
        n2 = value_noise2(H, W, int(40 * S), 7 + ci) * 0.25
        prof = np.exp(-(((yy - edge) / thick) ** 2) * 2.5) * (1 + n2)
        span = smooth((xx / W - x0) / 0.08) * smooth((x1 - xx / W) / 0.08)
        al = np.clip(prof * span * a, 0, 0.85)
        skyimg = skyimg * (1 - al[..., None]) + al[..., None] * np.array(col)
    # ---------------- far shore hills ----------------
    land = np.zeros((H, W), bool)
    hills_img = skyimg.copy()
    for hi, hl in enumerate(cfg["hills"]):
        hgt, rough, col, haze = hl
        ridge = 0.5 + 0.35 * fbm1(xx[0] / W * rough * 0.35, 30 + hi, 4)
        trees = np.abs(fbm1(xx[0] / W * rough * 1.6, 60 + hi, 3)) * 0.14
        top = cam.cy - hgt * H * np.clip(ndi.gaussian_filter1d(ridge + trees, 1.5 * S), 0.15, 1.3)
        m = (yy >= top[None, :]) & (yy <= cam.cy + 0.5)
        c = np.array(col) * (1 - haze) + skyimg[int(cam.cy) - 2, :, :][None] * haze
        mist = smooth((yy - top[None, :]) / (0.03 * H))[..., None]
        cc = c * (0.85 + 0.15 * (1 - mist)) + mist * 0.12 * (np.array(cfg["sky_h"]) - c)
        hills_img = np.where(m[..., None], cc, hills_img)
        land |= m
    # low mist at the shoreline
    mistband = np.exp(-((yy - cam.cy) / (0.012 * H)) ** 2)[..., None] * 0.55
    hills_img = hills_img * (1 - mistband) + mistband * np.array(cfg["sky_h"])
    above = hills_img
    # ---------------- flock ----------------
    flocks = cfg["flocks"]
    Hs, Ws = H * ss, W * ss
    A_up = np.zeros((Hs, Ws), np.float32); A_dn = np.zeros((Hs, Ws), np.float32)
    C_up = [np.zeros((Hs, Ws), np.float32) for _ in range(3)]; C_dn = [np.zeros((Hs, Ws), np.float32) for _ in range(3)]
    for fl in flocks:
        P = np.load(fl["file"]).astype(np.float64)
        P -= np.median(P, 0)
        rng = np.random.default_rng(fl.get("rot_seed", 0))
        ax, ay, az = np.radians(fl["rot"])
        Rx = np.array([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]])
        Ry = np.array([[np.cos(ay), 0, np.sin(ay)], [0, 1, 0], [-np.sin(ay), 0, np.cos(ay)]])
        Rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
        yw = np.radians(fl.get("yaw", 0.0))
        Ryw = np.array([[np.cos(yw), 0, np.sin(yw)], [0, 1, 0], [-np.sin(yw), 0, np.cos(yw)]])
        Q = P @ (Ryw @ Rz @ Ry @ Rx).T * fl["scale"] + np.array(fl["pos"])
        Q[:, 2] = np.maximum(Q[:, 2], 10)
        ink = np.array(fl["ink"]); hazec = np.array(fl.get("haze_col", cfg["sky_2"]))
        for refl, A, C in ((False, A_up, C_up), (True, A_dn, C_dn)):
            R = Q.copy()
            if refl: R[:, 1] = -2 * cam.h - R[:, 1]
            u, v = cam.proj(R)
            u *= ss; v *= ss
            # bird footprint grows when near; weight = ink per bird
            w = fl["ink_w"] * (W * ss / 2048) ** 2 * (3e5 / len(R)) * (fl["pos"][2] / R[:, 2]) ** 2
            hz = np.clip((R[:, 2] - fl.get("haze_z0", 300)) / fl.get("haze_z1", 3000), 0, 0.8)
            col = ink[None] * (1 - hz[:, None]) + hazec[None] * hz[:, None]
            i0 = np.floor(u).astype(np.int64); j0 = np.floor(v).astype(np.int64)
            fu = u - i0; fv = v - j0
            for di, dj, ww in ((0, 0, (1 - fu) * (1 - fv)), (1, 0, fu * (1 - fv)), (0, 1, (1 - fu) * fv), (1, 1, fu * fv)):
                ii = i0 + di; jj = j0 + dj
                ok = (ii >= 0) & (ii < Ws) & (jj >= 0) & (jj < Hs)
                idx = jj[ok] * Ws + ii[ok]; wk = (ww * w)[ok]
                A.ravel()[:] += np.bincount(idx, wk, Hs * Ws).astype(np.float32)
                for c in range(3):
                    C[c].ravel()[:] += np.bincount(idx, wk * col[ok, c], Hs * Ws).astype(np.float32)
    def down(a):
        if ss == 1: return a
        sh = (H, ss, W, ss) + a.shape[2:]
        return a.reshape(sh).mean(axis=(1, 3))
    def inkover(base, A, C, blur):
        C = np.stack(C, -1)
        if blur:
            A = ndi.gaussian_filter(A, blur * ss)
            C = np.stack([ndi.gaussian_filter(C[..., c], blur * ss) for c in range(3)], -1)
        A = down(A); C = down(C)
        Cn = C / np.maximum(A, 1e-6)[..., None]
        deep = np.array(cfg.get("ink_deep", [0.36, 0.28, 0.48]))
        m = smooth((A - cfg.get("deep_a0", 1.0)) / cfg.get("deep_a1", 3.0))[..., None] * cfg.get("deep_mix", 0.8)
        Cn = Cn * (1 - m) + deep * m
        al = (1 - np.exp(-A * cfg["ink_k"])) * cfg["ink_max"]
        return base * (1 - al[..., None]) + al[..., None] * Cn, al
    above, al_up = inkover(above, A_up, C_up, 0.35)
    # ---------------- water ----------------
    water = yy > cam.cy
    # mirror image of 'above' about the horizon, with ripples
    rows = yy - cam.cy
    depth = np.maximum(rows, 0.5) / (H - cam.cy)            # 0 far .. 1 near
    n1 = value_noise2(H, W, int(3 * S), 41)
    rip = fbm1(xx[0] / W * 1.0, 5)[None, :] * 0.2
    n1 = ndi.gaussian_filter(value_noise2(H, W, int(6 * S), 41), (0.5 * S, 6 * S))
    wave = (np.sin(rows / (0.5 * S + 5 * S * depth) + n1 * 3.0 + rip * 6)
            + 0.4 * ndi.gaussian_filter(value_noise2(H, W, int(5 * S), 42), (0.3 * S, 8 * S)))
    amp_y = (0.6 + 9.0 * depth ** 1.5) * S * cfg["ripple"]
    amp_x = (0.3 + 2.5 * depth) * S * cfg["ripple"]
    my = cam.cy - rows + wave * amp_y
    mx = xx + np.cos(rows / (2.3 * S) + n1 * 3) * amp_x
    def sample(img, X, Y):
        return np.stack([ndi.map_coordinates(img[..., c], [Y, X], order=1, mode="nearest") for c in range(3)], -1)
    # the downward (reflected) flock is its own render: flock reflection = mirror render
    refl_base = above.copy()
    # replace the flock in the mirrored base by its true reflection render
    refl_base = refl_base * (1 - al_up[..., None]) + al_up[..., None] * hills_img   # remove up-flock
    refl_full = refl_base.copy()
    # flip the true reflected flock into the 'above' coordinate frame
    A_dn_f = A_dn; C_dn_f = C_dn
    tmp, al_dn = inkover(np.zeros_like(above), A_dn_f, C_dn_f, 0.35)
    # tmp holds al*col at reflected positions (in water rows) -> mirror to sky rows
    Hc = int(round(cam.cy))
    def mirror(a):
        out = np.zeros_like(a)
        n = min(Hc, H - Hc)
        out[Hc - n:Hc] = a[Hc:Hc + n][::-1]
        return out
    tmpm = mirror(tmp); alm = mirror(al_dn)
    refl_full = refl_full * (1 - alm[..., None]) + tmpm
    R = sample(refl_full, mx, my)
    # fresnel-ish: far water mirrors, near water shows more water colour
    fres = 0.92 - 0.42 * depth ** 0.8
    wcol = np.array(cfg["water"])
    wimg = R * fres[..., None] + wcol * (1 - fres[..., None])
    # sun glitter path
    gl = np.exp(-((xx - sx) / (W * (0.02 + 0.10 * depth))) ** 2) * np.clip(wave - 0.9, 0, None) ** 2
    wimg = wimg + gl[..., None] * cfg["glitter"] * (np.array([1, 0.98, 0.9]) - wimg)
    img = np.where(water[..., None], wimg, above)
    # soften the horizon line
    hb = np.exp(-((yy - cam.cy) / (0.0018 * H)) ** 2)[..., None] * 0.5
    img = img * (1 - hb) + hb * np.array(cfg["sky_h"])
    img = foreground(cfg, img, cam, W, H, S)
    # grain + tone
    g = np.random.default_rng(3).normal(size=(H, W)).astype(np.float32) * 0.006
    img = np.clip(img + g[..., None], 0, 1)
    Image.fromarray((img ** (1 / cfg.get("gamma", 1.0)) * 255 + 0.5).astype(np.uint8)).save(out)
    print("saved", out)

def foreground(cfg, img, cam, W, H, S):
    """Reeds (soft, out of focus) and a little jetty with one watcher."""
    fg = cfg.get("fg", {})
    rng = np.random.default_rng(fg.get("seed", 9))
    SS = 2
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    refl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dr2 = ImageDraw.Draw(refl)
    def C(c, a=255): return tuple(int(255 * x) for x in c) + (a,)
    base_y = H * fg.get("reed_base", 0.93)
    for clump in fg.get("reeds", []):
        cx0, spread, n, hmax, col = clump
        for k in range(n):
            x = (cx0 + rng.normal() * spread) * W
            by = base_y + rng.uniform(-0.01, 0.04) * H
            h = hmax * H * rng.uniform(0.45, 1.0)
            bend = rng.normal() * 0.05 * h
            wdt = max(1.0, rng.uniform(1.2, 2.4) * S)
            pts = []
            for t in np.linspace(0, 1, 24):
                pts.append(((x + bend * t ** 2) * SS, (by - h * t) * SS))
            cc = np.array(col) * rng.uniform(0.93, 1.05)
            dr.line(pts, fill=C(np.clip(cc, 0, 1)), width=int(wdt * SS))
            rp = [(px, 2 * by * SS - py) for px, py in pts]
            dr2.line(rp, fill=C(np.clip(cc, 0, 1), 110), width=int(wdt * SS))
            if rng.random() < 0.33:   # cattail head
                hx, hy = pts[-5]; L = 0.035 * H * SS; r = 2.6 * S * SS
                dr.rounded_rectangle([hx - r, hy - L * 0.2, hx + r, hy + L * 0.8], radius=r, fill=C(np.clip(cc * 0.92 + 0.02, 0, 1)))
            if rng.random() < 0.5:    # a long leaf
                t0 = rng.uniform(0.15, 0.5); side = rng.choice([-1, 1])
                lp = []
                for t in np.linspace(0, 1, 18):
                    lp.append(((x + side * h * 0.35 * t + bend * t0 ** 2) * SS, (by - h * (t0 + 0.55 * t - 0.45 * t * t)) * SS))
                dr.line(lp, fill=C(np.clip(cc * 1.03, 0, 1)), width=int(wdt * 1.4 * SS))
    lay = lay.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(fg.get("reed_blur", 1.2) * S))
    refl = refl.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3 * S))
    out = img.copy()
    for L in (refl, lay):
        a = np.asarray(L).astype(np.float32) / 255
        out = out * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    # a few stragglers close enough to see their wings
    st = fg.get("strays")
    if st:
        SS2 = 3
        L2 = Image.new("RGBA", (W * SS2, H * SS2), (0, 0, 0, 0)); d2 = ImageDraw.Draw(L2)
        r2 = np.random.default_rng(st.get("seed", 4))
        for k in range(st["n"]):
            x = (st["cx"] + r2.normal() * st["sx"]) * W; y = (st["cy"] + r2.normal() * st["sy"]) * H
            sz = st["size"] * S * r2.uniform(0.5, 1.2); ph = r2.uniform(-0.6, 0.9)
            lw = max(1, int(sz * 0.16 * SS2))
            for side in (-1, 1):
                pts = []
                for t in np.linspace(0, 1, 9):
                    pts.append(((x + side * sz * t) * SS2, (y - sz * (0.55 * ph * np.sin(np.pi * t * 0.9) + 0.35 * t * t * ph)) * SS2))
                d2.line(pts, fill=C(st["col"]), width=lw, joint="curve")
            d2.ellipse([(x - sz * 0.12) * SS2, (y - sz * 0.1) * SS2, (x + sz * 0.12) * SS2, (y + sz * 0.14) * SS2], fill=C(st["col"]))
        L2 = L2.resize((W, H), Image.LANCZOS)
        a = np.asarray(L2).astype(np.float32) / 255
        out = out * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    # jetty + watcher
    j = fg.get("jetty")
    if j:
        out = jetty(out, j, W, H, S, cam)
    return out

def jetty(img, j, W, H, S, cam):
    SS = 3
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    rl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dr2 = ImageDraw.Draw(rl)
    def C(c, a=255): return tuple(int(255 * x) for x in c) + (a,)
    # jetty in world: x from x0..x1 (width), z from z0..z1, deck height dh above water
    x0, x1, z0, z1, dh = j["x0"], j["x1"], j["z0"], j["z1"], j["deck"]
    def P(x, y, z):   # y relative to water
        return (cam.cx + cam.f * x / z) * SS, (cam.cy - cam.f * (y - cam.h) / z) * SS
    def PR(x, y, z):
        return (cam.cx + cam.f * x / z) * SS, (cam.cy - cam.f * (-y - cam.h) / z) * SS
    wood, wood_d, post = j["wood"], j["wood_d"], j["post"]
    # posts
    for z in np.linspace(z0, z1, j.get("nposts", 7)):
        for x in (x0, x1):
            w2 = 0.09
            q = [P(x - w2, -0.3, z), P(x + w2, -0.3, z), P(x + w2, dh, z), P(x - w2, dh, z)]
            dr.polygon(q, fill=C(post))
            q2 = [PR(x - w2, 0, z), PR(x + w2, 0, z), PR(x + w2, dh, z), PR(x - w2, dh, z)]
            dr2.polygon(q2, fill=C(post, 120))
    # deck underlay (gaps read darker)
    dr.polygon([P(x0, dh, z0), P(x1, dh, z0), P(x1, dh, z1), P(x0, dh, z1)], fill=C(wood_d))
    # deck planks
    nz = j.get("planks", 40)
    zs = np.linspace(z0, z1, nz + 1)
    for k in range(nz):
        za, zb = zs[k], zs[k + 1] - (zs[1] - zs[0]) * 0.12
        col = np.array(wood) * (0.96 + 0.06 * ((k * 7919) % 13) / 13)
        dr.polygon([P(x0, dh, za), P(x1, dh, za), P(x1, dh, zb), P(x0, dh, zb)], fill=C(np.clip(col, 0, 1)))
    # deck side fascia
    dr.polygon([P(x0, dh, z0), P(x0, dh - 0.12, z0), P(x0, dh - 0.12, z1), P(x0, dh, z1)], fill=C(wood_d))
    dr2.polygon([PR(x0, dh, z0), PR(x0, dh - 0.12, z0), PR(x0, dh - 0.12, z1), PR(x0, dh, z1)], fill=C(wood_d, 120))
    # the watcher: standing near the end, looking up toward the flock
    wx, wz = j["who"]
    def ell(cx, cy, rx, ry, col, d=dr):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=C(col))
    fx, fy = P(wx, dh, wz)
    sc = cam.f / wz * SS            # px per metre
    coat, scarf, skin, hair, legs = j["coat"], j["scarf"], j["skin"], j["hair"], j["legs"]
    # legs
    for dx in (-0.09, 0.09):
        dr.rounded_rectangle([fx + (dx - 0.055) * sc, fy - 0.85 * sc, fx + (dx + 0.055) * sc, fy], radius=0.04 * sc, fill=C(legs))
    # coat (a-line)
    dr.polygon([(fx - 0.2 * sc, fy - 1.42 * sc), (fx + 0.2 * sc, fy - 1.42 * sc), (fx + 0.33 * sc, fy - 0.72 * sc), (fx - 0.33 * sc, fy - 0.72 * sc)], fill=C(coat))
    dr.rounded_rectangle([fx - 0.23 * sc, fy - 1.5 * sc, fx + 0.23 * sc, fy - 1.2 * sc], radius=0.1 * sc, fill=C(coat))
    # arm raised, pointing at the flock
    ax0, ay0 = fx + 0.17 * sc, fy - 1.40 * sc
    ang = np.radians(j.get("point", 58))
    ax1, ay1 = ax0 + 0.62 * sc * np.cos(ang), ay0 - 0.62 * sc * np.sin(ang)
    dr.line([(ax0, ay0), (ax1, ay1)], fill=C(coat), width=int(0.11 * sc))
    ell(ax1, ay1, 0.055 * sc, 0.055 * sc, skin)
    # head tilted back
    ell(fx + 0.02 * sc, fy - 1.66 * sc, 0.13 * sc, 0.14 * sc, skin)
    dr.chord([fx - 0.12 * sc, fy - 1.82 * sc, fx + 0.15 * sc, fy - 1.54 * sc], 160, 360, fill=C(hair))
    ell(fx - 0.10 * sc, fy - 1.67 * sc, 0.07 * sc, 0.09 * sc, hair)
    # scarf
    dr.rounded_rectangle([fx - 0.17 * sc, fy - 1.54 * sc, fx + 0.17 * sc, fy - 1.44 * sc], radius=0.04 * sc, fill=C(scarf))
    dr.polygon([(fx - 0.12 * sc, fy - 1.48 * sc), (fx - 0.04 * sc, fy - 1.48 * sc), (fx - 0.16 * sc, fy - 1.12 * sc), (fx - 0.24 * sc, fy - 1.16 * sc)], fill=C(scarf))
    # reflection of the watcher (rough: mirrored silhouette)
    rx0, ry0 = PR(wx, dh, wz)
    dr2.polygon([(rx0 - 0.3 * sc, ry0 + 0.72 * sc), (rx0 + 0.3 * sc, ry0 + 0.72 * sc), (rx0 + 0.2 * sc, ry0 + 1.45 * sc), (rx0 - 0.2 * sc, ry0 + 1.45 * sc)], fill=C(coat, 100))
    lay = lay.resize((W, H), Image.LANCZOS)
    rl = rl.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.5 * S))
    out = img
    for L in (rl, lay):
        a = np.asarray(L).astype(np.float32) / 255
        out = out * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    return out

if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1]))
    if len(sys.argv) > 3: cfg["size"] = int(sys.argv[3])
    render(cfg, sys.argv[2])
