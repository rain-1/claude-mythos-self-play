# render_hatbox.py — Archimedes' hatbox theorem (MO 283109): a sphere in its glass cylinder, painted in bands of
# equal HEIGHT that therefore have equal AREA, the same bands continued on the cylinder (Lambert's equal-area
# projection is the horizontal push outward), uniform sugar on the sphere, and one tilted slab of the same
# thickness glazed in coral: every slab of thickness h has area 2*pi*R*h whichever way it faces.
# Anti-aliasing by jittered passes (memory stays ~1 frame).   usage: render_hatbox.py W out.png [NB] [passes]
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from sorbet import Sheet, PIG, absorb, wheel_tint, text_mask, text_w, discs
W = int(sys.argv[1]); out = sys.argv[2]; H = int(W * 1.25)
NB = int(sys.argv[3]) if len(sys.argv) > 3 else 10
PASSES = int(sys.argv[4]) if len(sys.argv) > 4 else 4
CY = 0.455                                                   # screen row of the optical axis
el = np.deg2rad(17.0); az = np.deg2rad(-28.0)
cam = 7.2 * np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
tgt = np.array([0, 0, -0.02])
fwd = (tgt - cam) / np.linalg.norm(tgt - cam)
right = np.cross(fwd, [0, 0, 1]); right /= np.linalg.norm(right)
up = np.cross(right, fwd)
fov = 0.250
O = cam
cdir = cam / np.linalg.norm(cam)
L = 0.30 * cdir - 0.80 * right + 0.85 * np.array([0, 0, 1.0]); L /= np.linalg.norm(L)
h = 2.0 / NB
tilt = np.deg2rad(52)
nt = np.cos(tilt) * np.array([0, 0, 1.0]) + np.sin(tilt) * right; nt /= np.linalg.norm(nt)
c0 = 0.05
tints = [np.array(wheel_tint(0.86 * (i + 0.5) / NB)) for i in range(NB)]
TA = np.stack([absorb(tuple(t)) for t in tints]).astype(np.float32)
lc = np.array([0.10, -0.05, 1.42]); ln = np.array([0.20, -0.12, 1.0]); ln /= np.linalg.norm(ln)
def band_index(z): return np.clip(np.nan_to_num((1 - z) / 2 * NB).astype(int), 0, NB - 1)
def proj_pt(p):
    rel = p - cam
    x = rel @ right; y = rel @ up; f = rel @ fwd
    return (x / f / fov) * (W / 2) + W / 2, -(y / f / fov) * (W / 2) + H * CY, f
def trace(jx, jy):
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (xs + jx - W / 2) / (W / 2) * fov
    v = -(ys + jy - H * CY) / (W / 2) * fov
    D = fwd[None, None, :] + u[..., None] * right + v[..., None] * up
    D = (D / np.linalg.norm(D, axis=-1, keepdims=True)).astype(np.float32)
    out = {}
    # sphere
    b = D @ O; c = O @ O - 1.0; disc = b * b - c
    hitS = disc > 0
    tS = np.where(hitS, -b - np.sqrt(np.maximum(disc, 0)), 1e6)
    P = O + tS[..., None] * D; N = P
    # cylinder
    a2 = D[..., 0] ** 2 + D[..., 1] ** 2
    b2 = O[0] * D[..., 0] + O[1] * D[..., 1]
    c2 = O[0] ** 2 + O[1] ** 2 - 1.0
    d2 = b2 * b2 - a2 * c2
    sq = np.sqrt(np.maximum(d2, 0))
    t1 = (-b2 - sq) / a2; t2 = (-b2 + sq) / a2
    z1 = O[2] + t1 * D[..., 2]; z2 = O[2] + t2 * D[..., 2]
    front = (d2 > 0) & (np.abs(z1) <= 1)
    back = (d2 > 0) & (np.abs(z2) <= 1) & ~(hitS & (tS < t2))
    # ground
    dz = np.minimum(D[..., 2], -1e-4)
    tg = np.where(D[..., 2] < -1e-4, (-1.0 - O[2]) / dz, 1e3)
    G = O + tg[..., None] * D
    ground = (D[..., 2] < -1e-4) & ~hitS
    bb = G @ L; cc = (G * G).sum(-1) - 1.0; dd = bb * bb - cc
    out['shadow'] = (np.clip(np.sqrt(np.maximum(dd, 0)) * 1.6, 0, 1) * (bb < 0) * ground).astype(np.float32)
    r_contact = np.hypot(G[..., 0], G[..., 1])
    A = (np.exp(-(r_contact / 0.22) ** 2) * ground * ~front)[..., None] * absorb('periwinkle') * 0.35
    # sphere shading
    z = P[..., 2]; bi = band_index(z)
    lam = np.clip(N @ L, 0, 1)
    Hh = L - D; Hh /= np.linalg.norm(Hh, axis=-1, keepdims=True)
    spec = np.clip((N * Hh).sum(-1), 0, 1) ** 60
    dens = 0.62 + 1.15 * (1 - lam) ** 1.25
    sph = dens[..., None] * TA[bi] * np.where(bi % 2 == 0, 1.0, 0.82)[..., None]
    zf = (1 - z) / 2 * NB
    sep = np.exp(-((zf - np.round(zf)) / 0.035) ** 2) * hitS * (np.abs(z) < 0.999)
    proj = P @ nt
    slab = np.clip((np.minimum(proj - c0, c0 + h - proj)) / 0.012 + 0.5, 0, 1)
    coral_d = absorb('coral')[None, None, :] * (0.55 + 1.1 * (1 - lam) ** 1.25)[..., None]
    sph = sph * (1 - slab[..., None]) + slab[..., None] * coral_d
    seam = np.exp(-(np.minimum(np.abs(proj - c0), np.abs(proj - c0 - h)) / 0.006) ** 2) * hitS
    A = A + np.where(hitS[..., None], np.nan_to_num(sph), 0)
    # glass shell
    def shell(t, zc, mask, strength):
        Pc = O + t[..., None] * D
        nrm = np.stack([Pc[..., 0], Pc[..., 1], np.zeros_like(t)], -1)
        cosi = np.abs((nrm * D).sum(-1))
        fres = 0.04 + 0.96 * (1 - cosi) ** 5
        path = 1 / np.maximum(cosi, 0.08)
        bi2 = band_index(zc)
        tint = TA[bi2] * (path * 0.15 * strength)[..., None] * np.where(bi2 % 2 == 0, 1.0, 0.7)[..., None]
        return tint * mask[..., None], fres * mask
    tf, ff = shell(t1, z1, front, 1.0)
    tb, fb = shell(t2, z2, back, 0.8)
    A = A + tf + tb
    # lid
    den = D @ ln
    tl = ((lc - O) @ ln) / np.where(np.abs(den) < 1e-6, 1e-6, den)
    Pl = O + tl[..., None] * D
    rl = np.linalg.norm(Pl - lc, axis=-1)
    lid = (rl <= 1.06) & (tl > 0)
    cosl = np.abs(den)
    A = A + (lid * (0.10 / np.maximum(cosl, 0.1)))[..., None] * absorb('lilac')
    lid_f = lid * (0.04 + 0.96 * (1 - cosl) ** 5)
    A = A + (np.exp(-((rl - 1.06) / 0.012) ** 2) * (tl > 0))[..., None] * absorb('lilac') * 0.6
    out['A'] = A.astype(np.float32)
    out['spec'] = (spec * hitS).astype(np.float32)
    out['glass'] = (ff + fb * 0.6 + lid_f).astype(np.float32)
    out['seam'] = seam.astype(np.float32)
    out['sep'] = (sep * (1 - slab)).astype(np.float32)
    return out
jit = [(0.25, 0.25), (-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0, 0), (0.5, 0), (0, 0.5), (-0.5, 0), (0, -0.5)][:PASSES]
acc = None
for (jx, jy) in jit:
    o = trace(jx, jy)
    acc = o if acc is None else {k: acc[k] + o[k] for k in acc}
    print('pass', jx, jy, flush=True)
acc = {k: v / len(jit) for k, v in acc.items()}
sh = Sheet(W, H, seed=5)
sh.A += acc['A']
sh.A += gaussian_filter(acc['shadow'], 18 * W / 1600)[..., None] * absorb('periwinkle')[None, None] * 0.45
# cylinder rims
im = Image.new('F', (W * 2, H * 2), 0.0); dr = ImageDraw.Draw(im)
th = np.linspace(0, 2 * np.pi, 6000)
for zc in (1.0, -1.0):
    Pr = np.stack([np.cos(th), np.sin(th), np.full_like(th, zc)], 1)
    px, py, f = proj_pt(Pr)
    dr.line(list(zip(px * 2, py * 2)), fill=1.0, width=max(2, int(3 * 2 * W / 1600)))
rim = np.asarray(im, np.float32).reshape(H, 2, W, 2).mean(axis=(1, 3))
sh.A += gaussian_filter(rim, 0.8)[..., None] * absorb('periwinkle') * 0.5
# sugar
M = 520
k = np.arange(M) + 0.5
zz = 1 - 2 * k / M; ph = np.pi * (1 + 5 ** 0.5) * k
pts = np.stack([np.sqrt(1 - zz ** 2) * np.cos(ph), np.sqrt(1 - zz ** 2) * np.sin(ph), zz], 1)
visible = (pts * (cam - pts)).sum(1) > 0.02
vx, vy, _ = proj_pt(pts[visible])
pr = W / 650
sh.lighten(np.clip(discs(W, H, vx, vy, np.full(len(vx), pr * 1.25), sigma=0.5), 0, 1), 0.85)
sh.wash(discs(W, H, vx + pr * 0.2, vy + pr * 0.3, np.full(len(vx), pr * 0.8), sigma=0.5), 'plum', 0.35)
sh.lighten(np.clip(acc['spec'] * 1.2, 0, 1), 0.9)
sh.lighten(np.clip(acc['sep'] * 0.8, 0, 1), 0.55)
sh.lighten(np.clip(acc['seam'] * 0.9, 0, 1), 0.8)
sh.lighten(np.clip(acc['glass'] * 1.4, 0, 1), 0.85)
# caption
y0 = 0.855 * H
items = [('Every Slab Weighs the Same', W / 2, y0, 0.042 * W, 'serif_bold', 'mm'),
         ('a sphere in its cylinder, painted in ten bands of equal height — so of equal area, 2πRh each, as Archimedes proved', W / 2, y0 + 0.042 * W, 0.0175 * W, 'italic', 'mm'),
         ('the bands carry on, unchanged, round the glass: push each point straight out and no area is lost · 520 grains of uniform sugar, 52 to a band ·', W / 2, y0 + 0.070 * W, 0.0138 * W, 'italic', 'mm'),
         ('coral: one tilted slab of the same thickness, same area — and only the sphere can do this for every slab (Ghomi–Howard–Lai, MO 283109)', W / 2, y0 + 0.092 * W, 0.0138 * W, 'italic', 'mm')]
sh.wash(text_mask(W, H, items), 'ink', 2.6)
img = sh.develop(dmax=2.4)
img.save(out)
