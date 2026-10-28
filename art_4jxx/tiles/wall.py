"""Handmade glazed tile wall.  Each tile = one bit of a ground-state configuration.

render_wall(panels, ...) where panels is a list of dicts:
    {"grid": 0/1 array (h,w), "c0": rgb, "c1": rgb, "x": col0, "y": row0, "coral": bool}
placed on a global tile lattice.  Shading: per-tile pillow height + random tilt
(handmade), glaze pooling darker at the edges, crackle, grout; a soft window
reflected in every tile (environment lookup by reflected direction), so the
window breaks into a thousand slightly-turned pieces.
"""
import numpy as np
from scipy import ndimage as ndi

def smooth(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

def window_env(rx, ry, rz, win):
    """Radiance seen along reflected direction r (z toward the viewer)."""
    # project onto a plane in front of the wall (the room): window rectangle with mullions
    t = 1.0 / np.maximum(rz, 0.05)
    u = rx * t; v = ry * t
    x0, x1, y0, y1 = win["rect"]
    inside = smooth((u - x0) / 0.06) * smooth((x1 - u) / 0.06) * smooth((v - y0) / 0.06) * smooth((y1 - v) / 0.06)
    mx = np.abs(((u - x0) / (x1 - x0) * win["nx"]) % 1 - 0.5)   # mullions
    my = np.abs(((v - y0) / (y1 - y0) * win["ny"]) % 1 - 0.5)
    mull = smooth((0.5 - mx) / 0.04) * smooth((0.5 - my) / 0.04)
    bright = inside * (0.25 + 0.75 * mull)
    room = win["room"] * (0.6 + 0.4 * smooth(0.5 + 0.5 * v))
    return room + bright * win["I"]

def noise_fields(H, W, seed=5):
    rng = np.random.default_rng(seed)
    n1 = ndi.gaussian_filter(rng.normal(size=(H // 4 + 2, W // 4 + 2)).astype(np.float32), 3)[:H // 4 + 1, :W // 4 + 1]
    n1 = ndi.zoom(n1, 4, order=1)[:H, :W]; n1 /= np.std(n1) + 1e-9
    cr = ndi.gaussian_filter(rng.normal(size=(H // 2 + 2, W // 2 + 2)).astype(np.float32), 2.2)[:H // 2 + 1, :W // 2 + 1]
    cr = ndi.zoom(cr, 2, order=1)[:H, :W]; cr /= np.std(cr) + 1e-9
    return n1.astype(np.float32), cr.astype(np.float32)

def render_wall(H, W, tiles_y, tiles_x, colours, coral_mask, seed=1, tile_px=None,
                grout=(0.93, 0.91, 0.90), win=None, light=(-0.45, 0.55, 0.70), gap=0.075,
                y0=0, y1=None, noise=None, ox=0.0, oy=0.0, plaster_col=(0.97, 0.96, 0.95), dots=None):
    """Rows y0..y1 of an H x W image; tile lattice starts at pixel (ox, oy)."""
    """colours: (tiles_y, tiles_x, 3) per-tile glaze colour (or nan for no tile)."""
    rng = np.random.default_rng(seed)
    T = tile_px or W / tiles_x
    y1 = H if y1 is None else y1
    yy, xx = np.mgrid[y0:y1, 0:W].astype(np.float32)
    uy = (yy - oy) / T; ux = (xx - ox) / T
    outside = (uy < 0) | (ux < 0) | (uy >= tiles_y) | (ux >= tiles_x)
    ti = np.clip(np.floor(uy).astype(int), 0, tiles_y - 1); tj = np.clip(np.floor(ux).astype(int), 0, tiles_x - 1)
    fy = uy - ti; fx = ux - tj            # 0..1 inside the tile cell
    # handmade: per-tile jitter of size and tilt
    tilt = rng.normal(size=(tiles_y, tiles_x, 2)) * 0.07
    bulge = rng.uniform(0.6, 1.0, size=(tiles_y, tiles_x))
    sz = 1 - gap + rng.normal(size=(tiles_y, tiles_x, 2)) * 0.008
    off = rng.normal(size=(tiles_y, tiles_x, 2)) * 0.008
    cx = fx - 0.5 - off[ti, tj, 0]; cy = fy - 0.5 - off[ti, tj, 1]
    hx = sz[ti, tj, 0] / 2; hy = sz[ti, tj, 1] / 2
    # rounded-square distance to tile edge (negative inside)
    r = 0.06
    qx = np.abs(cx) - hx + r; qy = np.abs(cy) - hy + r
    sd = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    notile = np.isnan(colours[ti, tj, 0])
    inside = (sd < 0) & ~outside & ~notile
    depth = np.clip(-sd, 0, None)
    # pillow height: rises quickly at the edge then gentle dome
    h = (1 - np.exp(-depth / 0.035)) * 0.06 + bulge[ti, tj] * 0.035 * (1 - (cx / hx) ** 2) * (1 - (cy / hy) ** 2)
    h += tilt[ti, tj, 0] * cx + tilt[ti, tj, 1] * cy
    # glaze ripples (hand-dipped)
    if noise is None: noise = noise_fields(H, W)
    n1 = noise[0][y0:y1]; cr = noise[1][y0:y1]
    h += 0.0018 * n1
    h = np.where(inside, h, -0.02)
    # normals in tile units
    gy, gx = np.gradient(h * T)
    gy[0] = gy[1]; gy[-1] = gy[-2]
    nx, ny, nz = -gx, gy, np.ones_like(h)
    nl = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2); nx /= nl; ny /= nl; nz /= nl
    # glaze colour: pooled darker at edge, lighter on the dome
    base = colours[ti, tj]
    nan = np.isnan(base[..., 0])
    base = np.where(nan[..., None], np.array(grout), base)
    pool = np.exp(-depth / 0.03)[..., None]
    deep = 1 - (1 - base) * 1.35
    col = base * (1 - 0.55 * pool) + np.clip(deep, 0, 1) * 0.55 * pool
    col = col * (1 + 0.035 * n1[..., None])
    # crackle: thin voronoi-ish lines per tile (cheap: thresholded noise ridges)
    crack = smooth(1 - np.abs(cr) / 0.035) * 0.03
    col = col * (1 - crack[..., None])
    # grout texture
    gr = np.array(grout) * (0.97 + 0.03 * n1[..., None])
    plaster = np.array(plaster_col) * (0.994 + 0.006 * n1[..., None])
    col = np.where(inside[..., None], col, np.where((notile | outside)[..., None], plaster, gr))
    if dots is not None:
        dm = dots[ti, tj] & inside
        rr = np.hypot(cx, cy)
        dd = smooth((0.21 - rr) / 0.02) * dm
        col = col * (1 - dd[..., None]) + np.array([0.97, 0.50, 0.44]) * dd[..., None]
    # lighting
    L = np.array(light); L = L / np.linalg.norm(L)
    ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, None)
    # grout is in the shadow of tile edges on the light side
    ao = np.where(inside | notile | outside, 1.0, 0.80 + 0.20 * smooth(-sd / 0.02 - 0.5))
    diff = (0.55 + 0.55 * ndl) * ao
    img = col * diff[..., None]
    # reflection of the window
    if win is not None:
        # view along -z; r = v - 2(n.v)n with v=(0,0,-1) -> r = (2nz nx, 2nz ny, 2nz^2-1)
        rx, ry, rz = 2 * nz * nx, 2 * nz * ny, 2 * nz * nz - 1
        # parallax: tiles at different wall positions see the window at different offsets
        px = (xx / W - 0.5) * win.get("par", 0.6); py = (0.5 - yy / H) * win.get("par", 0.6)
        env = window_env(rx - px * rz, ry - py * rz, rz, win)
        fres = 0.04 + 0.96 * (1 - nz) ** 5
        spec = np.where(inside, (0.06 + fres) * env, 0)
        img = img + spec[..., None] * np.array(win.get("col", (1, 1, 1)))
    # coral frame tiles get a gilt edge
    if coral_mask is not None:
        cm = coral_mask[ti, tj] & inside & (depth < 0.02)
        img = np.where(cm[..., None], img * 0.4 + np.array([0.98, 0.55, 0.47]) * 0.6, img)
    return img
