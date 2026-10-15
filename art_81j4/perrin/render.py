# render.py — a pastel Perrin plate: strobed paths of pollen grains in a microscope field, atoms only in the loupe.
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter
FONT = '/usr/share/fonts/truetype/liberation/'
HUES = [(1.0, 0.55, 0.62), (1.0, 0.70, 0.45), (0.98, 0.80, 0.30), (0.60, 0.85, 0.40), (0.35, 0.82, 0.68),
        (0.40, 0.70, 0.98), (0.55, 0.58, 0.98), (0.75, 0.55, 0.95), (0.98, 0.55, 0.85), (0.98, 0.62, 0.50),
        (0.45, 0.80, 0.90), (0.85, 0.75, 0.40)]
INK = np.array([0.36, 0.30, 0.40])
def lerp(a, b, t): return tuple(np.array(a) * (1 - t) + np.array(b) * t)
def render(npz, out, W=3200, every_t=16.0, loupe_grain=None, title=None, sub=None, sub2=None, tmax=None, ss=2, field=0.415, seed=0, shift=(0.0, 0.0), loupe=None):
    d = np.load(npz); traj = d['traj']; L = float(d['L']); dt = float(d['dt']); x = d['x']; rad = d['rad']
    nsmall = int((rad == 0.5).sum()); M = traj.shape[1]
    if tmax: traj = traj[:int(tmax / dt) + 1]
    S = W * ss; cx, cy = 0.535 * S, 0.47 * S; Rf = field * S * 2      # field diameter in px = 2*Rf... Rf = radius
    Rf = field * S
    sc = 2 * Rf / (L * 0.98)                 # box spans the field
    off = traj[0] - (traj[0] % L)            # unwrap: start each trail at its wrapped position
    sh = np.array(shift); T = traj - off[None] - sh
    nimg = np.round((T.mean(0) - L / 2) / L); T = T - nimg[None] * L   # the periodic image nearest the field centre
    X = (x - sh) % L
    def P(p): return (cx + (p[0] - L / 2) * sc, cy - (p[1] - L / 2) * sc)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); r = np.hypot(xx - cx, yy - cy) / Rf
    # paper outside: soft lavender; field: luminous cream with a cool rim
    img = np.zeros((S, S, 3), np.float32)
    out_c = np.array([0.93, 0.91, 0.96]); fc = np.array([1.0, 0.995, 0.975]); rim = np.array([0.86, 0.88, 0.99])
    t = np.clip((r - 0.55) / 0.45, 0, 1) ** 2
    inside = (r < 1)[..., None]
    fld = fc[None, None] * (1 - t[..., None]) + rim[None, None] * t[..., None]
    img[:] = np.where(inside, fld, out_c[None, None])
    # eyepiece ring: a pale brass bevel
    ring = np.exp(-((r - 1.0) * Rf / (0.012 * S)) ** 2)
    img = img * (1 - 0.35 * ring[..., None]) + 0.35 * ring[..., None] * np.array([0.98, 0.86, 0.62])
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)); dr = ImageDraw.Draw(im, 'RGBA')
    # graticule
    step = 10 * sc; n = int(Rf / step) + 1
    layer = Image.new('RGBA', (S, S), (0, 0, 0, 0)); dl = ImageDraw.Draw(layer, 'RGBA')
    for k in range(-n, n + 1):
        for (a, b) in [((cx + k * step, 0), (cx + k * step, S)), ((0, cy + k * step), (S, cy + k * step))]:
            dl.line([a, b], fill=(120, 105, 150, 30), width=max(1, int(1.6 * ss)))
    mask = Image.new('L', (S, S), 0); ImageDraw.Draw(mask).ellipse([cx - Rf, cy - Rf, cx + Rf, cy + Rf], fill=255)
    k = max(1, int(round(every_t / dt))); idx = np.arange(0, len(T), k)
    lw = int(5.0 * ss * W / 3200); dotr = 6.5 * ss * W / 3200
    for g in range(M):
        h = np.array(HUES[g % len(HUES)]); pts = [P(T[i, g]) for i in idx]
        n_ = len(pts)
        # shadow
        for i in range(n_ - 1):
            a, b = pts[i], pts[i + 1]; dl.line([(a[0] + 3 * ss, a[1] + 4 * ss), (b[0] + 3 * ss, b[1] + 4 * ss)], fill=(120, 110, 170, 40), width=lw + 2 * ss)
        for i in range(n_ - 1):
            u = i / max(1, n_ - 2); c = lerp(h * 0.55 + 0.45, h * 0.92, u)
            dl.line([pts[i], pts[i + 1]], fill=tuple(int(255 * v) for v in c) + (235,), width=lw)
        for i in range(n_):
            u = i / max(1, n_ - 1); c = lerp(h * 0.55 + 0.45, h * 0.92, u); p = pts[i]
            dl.ellipse([p[0] - dotr, p[1] - dotr, p[0] + dotr, p[1] + dotr], fill=(255, 255, 255, 255), outline=tuple(int(255 * v) for v in c) + (255,), width=int(2.6 * ss))
    # grains at their final positions: translucent pollen with spines
    for g in range(M):
        R = rad[nsmall + g] * sc; p = P(T[-1, g]); h = np.array(HUES[g % len(HUES)])
        draw_pollen(layer, p, R, h, ss, seed + g)
    im = Image.composite(Image.alpha_composite(im.convert('RGBA'), layer).convert('RGB'), im, mask)
    if loupe is not None: draw_loupe(im, loupe, T, X, rad, nsmall, L, P, sc, ss, S, idx)
    return im, dict(P=P, sc=sc, T=T, x=x, rad=rad, nsmall=nsmall, L=L, off=off, S=S, Rf=Rf)
def draw_pollen(layer, p, R, h, ss, seed, shadow=1.0):
    """a smooth translucent resin grain (Perrin used gamboge): soft shadow, glassy body, bright rim, specular"""
    d = ImageDraw.Draw(layer, 'RGBA'); h = np.array(h)
    for i in range(12 if shadow > 0 else 0):   # soft shadow, offset down-right
        t = i / 11; rr = R * (1.08 - 0.25 * t)
        d.ellipse([p[0] + 0.18 * R - rr, p[1] + 0.24 * R - rr, p[0] + 0.18 * R + rr, p[1] + 0.24 * R + rr], fill=(120, 110, 175, int(9 * shadow)))
    N = 36
    for i in range(N):
        t = i / (N - 1); rr = R * (1 - 0.9 * t); ox, oy = 0.18 * R * t, 0.2 * R * t   # glass: brighter towards lower-right (focused light)
        c = 1 - (1 - h) * (0.95 - 0.6 * t ** 1.3)
        d.ellipse([p[0] + ox - rr, p[1] + oy - rr, p[0] + ox + rr, p[1] + oy + rr], fill=tuple(int(255 * min(1, v)) for v in c) + (int(150 + 100 * t),))
    w = max(2, int(R * 0.06))
    d.ellipse([p[0] - R, p[1] - R, p[0] + R, p[1] + R], outline=tuple(int(255 * v) for v in h * 0.75) + (200,), width=w)
    for i in range(8):   # specular highlight, upper left
        t = i / 7; rr = R * (0.22 - 0.17 * t); q = (p[0] - 0.42 * R, p[1] - 0.42 * R)
        d.ellipse([q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr], fill=(255, 255, 255, int(40 + 25 * t)))
def draw_loupe(im, g, T, X, rad, nsmall, L, P, sc, ss, S, idx, rho=15.0, at=(0.835, 0.835), RL=0.138):
    c0 = T[-1, g] % L; Rg = rad[nsmall + g]; h = np.array(HUES[g % len(HUES)])
    cx, cy = at[0] * S, at[1] * S; RLp = RL * S; mag = RLp / rho
    # leader: thin plum line from the grain on the plate to the loupe
    d = ImageDraw.Draw(im, 'RGBA'); pg = P(T[-1, g])
    ang = np.arctan2(cy - pg[1], cx - pg[0])
    a = (pg[0] + (Rg * sc + 6 * ss) * np.cos(ang), pg[1] + (Rg * sc + 6 * ss) * np.sin(ang)); b = (cx - RLp * 1.04 * np.cos(ang), cy - RLp * 1.04 * np.sin(ang))
    d.line([a, b], fill=(92, 77, 102, 120), width=int(2.5 * ss))
    # shadow + handle
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh, 'RGBA')
    ha = np.radians(45); h0 = (cx + RLp * 1.05 * np.cos(ha), cy + RLp * 1.05 * np.sin(ha)); h1 = (cx + RLp * 1.75 * np.cos(ha), cy + RLp * 1.75 * np.sin(ha))
    ds.ellipse([cx - RLp * 1.08 + 14 * ss, cy - RLp * 1.08 + 18 * ss, cx + RLp * 1.08 + 14 * ss, cy + RLp * 1.08 + 18 * ss], fill=(110, 100, 160, 70))
    ds.line([(h0[0] + 14 * ss, h0[1] + 18 * ss), (h1[0] + 14 * ss, h1[1] + 18 * ss)], fill=(110, 100, 160, 70), width=int(0.16 * RLp))
    sh = sh.filter(ImageFilter.GaussianBlur(10 * ss)); im.paste(Image.alpha_composite(im.convert('RGBA'), sh).convert('RGB'))
    d = ImageDraw.Draw(im, 'RGBA')
    d.line([h0, h1], fill=(232, 196, 140, 255), width=int(0.16 * RLp)); d.line([h0, h1], fill=(250, 226, 186, 255), width=int(0.07 * RLp))
    # lens content
    lens = Image.new('RGBA', im.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lens, 'RGBA')
    dl.ellipse([cx - RLp, cy - RLp, cx + RLp, cy + RLp], fill=(255, 253, 246, 255))
    def Q(p): v = ((p - c0 + L / 2) % L) - L / 2; return (cx + v[0] * mag, cy - v[1] * mag)
    # grid in the lens (same graticule, magnified)
    step = 10 * mag; g0 = ((c0 - 0.0) % 10)
    for k in range(-3, 4):
        xx = cx + (k * 10 - g0[0]) * mag; yy = cy + (k * 10 - g0[1]) * mag * -1
        dl.line([(xx, cy - RLp), (xx, cy + RLp)], fill=(120, 105, 150, 40), width=int(2 * ss)); dl.line([(cx - RLp, yy), (cx + RLp, yy)], fill=(120, 105, 150, 40), width=int(2 * ss))
    # the last few strobe segments of the grain
    pts = [Q(T[i, g] % L) for i in idx[-4:]]
    for i in range(len(pts) - 1): dl.line([pts[i], pts[i + 1]], fill=tuple(int(255 * v) for v in h * 0.9) + (200,), width=int(9 * ss))
    # atoms: small glassy beads, hue a quiet periwinkle-grey
    rr = 0.5 * mag
    for p in X[:nsmall]:
        v = ((p - c0 + L / 2) % L) - L / 2
        if abs(v[0]) > rho + 1 or abs(v[1]) > rho + 1: continue
        q = (cx + v[0] * mag, cy - v[1] * mag)
        dl.ellipse([q[0] - rr + 3 * ss, q[1] - rr + 4 * ss, q[0] + rr + 3 * ss, q[1] + rr + 4 * ss], fill=(140, 130, 190, 50))
        for j in range(8):
            t = j / 7; r_ = rr * (1 - 0.8 * t); o = -0.25 * rr * t
            c = np.array([0.80, 0.80, 0.93]) * (1 - t) + np.array([1, 1, 1]) * t
            dl.ellipse([q[0] + o - r_, q[1] + o - r_, q[0] + o + r_, q[1] + o + r_], fill=tuple(int(255 * v) for v in c) + (255,))
    draw_pollen(lens, (cx, cy), Rg * mag, h, ss, 99, shadow=0.0)
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).ellipse([cx - RLp, cy - RLp, cx + RLp, cy + RLp], fill=255)
    im.paste(Image.composite(Image.alpha_composite(im.convert('RGBA'), lens).convert('RGB'), im, m))
    d = ImageDraw.Draw(im, 'RGBA')   # brass rim with a highlight
    for w, col in [(0.075, (226, 188, 128, 255)), (0.045, (246, 220, 170, 255)), (0.012, (255, 245, 225, 255))]:
        d.ellipse([cx - RLp * (1 + w / 2), cy - RLp * (1 + w / 2), cx + RLp * (1 + w / 2), cy + RLp * (1 + w / 2)], outline=col, width=int(w * RLp))
    d.arc([cx - RLp * 0.92, cy - RLp * 0.92, cx + RLp * 0.92, cy + RLp * 0.92], 200, 250, fill=(255, 255, 255, 150), width=int(0.03 * RLp))
def final(out='../what_pushed_them.png', W=3200):
    import sys; sys.path.insert(0, '..'); from finish import caption
    im, info = render('prod.npz', None, W=W, ss=2, shift=(20.26, 91.18), loupe=10)
    im = im.resize((W, W), Image.LANCZOS)
    caption(im, [('What Pushed Them', 'title'), ('Was Never Seen', 'title'),
                 ('twelve resin grains in a gas of 20,000 atoms, strobed every 16 time units', 'small'),
                 ('(Perrin 1909): only the zigzags are evident; the loupe shows the rest', 'small')], 150, 3445, scale=W / 4096)
    caption(im, [('FROM THE EVIDENT TO THE HIDDEN  \u00b7  ii', 'small')], 3960, 140, anchor='ra', scale=W / 4096)
    im.save(out, optimize=True)
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'final': final(); sys.exit()
    im, info = render(sys.argv[1], None, W=int(sys.argv[3]) if len(sys.argv) > 3 else 1200, ss=1, shift=(20.26, 91.18), loupe=int(sys.argv[4]) if len(sys.argv) > 4 else None)
    im.save(sys.argv[2])
