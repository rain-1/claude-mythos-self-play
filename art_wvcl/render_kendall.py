"""render_kendall.py — 'Every Triangle on One Globe': Kendall's shape sphere tiled with triangle glyphs.
Each glyph is the triangle whose shape is that point of the sphere; pigment by its largest angle.
Ink: equator (collinear), three meridians (isosceles), three circles (right-angled).
Coral: 500 triangles thrown at random by a Gaussian — they land uniformly (Kendall 1984); a strip of
twelve of them as thrown, below.
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import kendall as K
from pastel import Sheet, PIG, absorb, lowfreq, noise, polyline_density, text_density, finish, wrap, discs_density

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
NGLY = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
OUT = sys.argv[3] if len(sys.argv) > 3 else f'kendall_{SIZE}.png'
SS = 2
W = H = SIZE * SS
rs = SIZE / 1024.0 * SS
rng = np.random.default_rng(5)

# view: tilt the pole toward the viewer, turn a little so the meridians are not edge-on
Rv = K.rot_about([1, 0, 0], np.radians(40)) @ K.rot_about([0, 1, 0], np.radians(22))
Rs = 0.355 * H
cx, cy = 0.5 * W, 0.44 * H
LIGHT = np.array([-0.5, 0.6, 0.62]); LIGHT /= np.linalg.norm(LIGHT)


def view(P):
    """world (sphere) -> view coords (x right, y up, z toward viewer)"""
    return np.asarray(P, float) @ Rv.T


def to_px(V):
    return np.c_[cx + Rs * V[..., 0], cy - Rs * V[..., 1]]


WALK = ['mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush', 'apricot']


def tint_of(amax):
    """largest angle in [pi/3, pi] -> absorbance rgb along the walk"""
    t = np.clip((amax - np.pi / 3) / (2 * np.pi / 3), 0, 0.999) * (len(WALK) - 1)
    i0 = int(np.floor(t)); f = t - i0
    return (1 - f) * absorb(PIG[WALK[i0]]) + f * absorb(PIG[WALK[i0 + 1]])


def main():
    t0 = time.time()
    sheet = Sheet(W, H, seed=3)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # the sphere's body: grazing light, pale
    dx = (xx - cx) / Rs; dy = -(yy - cy) / Rs
    r2 = dx * dx + dy * dy
    inside = r2 <= 1.0
    nz = np.sqrt(np.clip(1 - r2, 0, 1))
    ndotl = np.clip(dx * LIGHT[0] + dy * LIGHT[1] + nz * LIGHT[2], 0, 1)
    body = (0.05 + 0.24 * (1 - ndotl)) * inside
    rim = np.exp(-((np.sqrt(r2) - 1) / 0.03) ** 2) * inside
    sheet.wash(gaussian_filter(body, 1.0 * rs), 'paperblue')
    sheet.wash(body * 0.35, 'lavender')
    sheet.wash(gaussian_filter(rim, 1.5 * rs) * 0.10, 'ink')
    del dx, dy, r2, nz, ndotl, body, rim
    # glyph lattice
    P = K.fibonacci_sphere(NGLY)
    V = view(P)
    vis = V[:, 2] > 0.02
    P, V = P[vis], V[vis]
    spacing = np.sqrt(4 * np.pi / NGLY)
    gsize = 1.30 * spacing          # glyph scale (pre-shape norm 1 puts vertices at RMS radius 0.58)
    # jitter in the tangent plane so the lattice's spiral grain does not show

    zeta = K.inv_stereo(P)
    # tangent frames: east = pole x p, north = p x east
    e1 = np.cross(np.broadcast_to(K.POLE, P.shape), P)
    n1 = np.linalg.norm(e1, axis=1); bad = n1 < 1e-6
    e1[bad] = np.array([1.0, 0, 0]); n1[bad] = 1
    e1 /= n1[:, None]; e2 = np.cross(P, e1)
    jit = rng.uniform(-0.22, 0.22, (len(P), 2)) * spacing
    P = P + jit[:, :1] * e1 + jit[:, 1:] * e2
    P /= np.linalg.norm(P, axis=1)[:, None]
    V = view(P); zeta = K.inv_stereo(P)
    e1 = np.cross(np.broadcast_to(K.POLE, P.shape), P)
    n1 = np.linalg.norm(e1, axis=1); bad = n1 < 1e-6
    e1[bad] = np.array([1.0, 0, 0]); n1[bad] = 1
    e1 /= n1[:, None]; e2 = np.cross(P, e1)
    nb = 16
    bins = [[] for _ in range(nb)]
    outl = Image.new('F', (W, H), 0.0); dro = ImageDraw.Draw(outl)
    amaxs = []
    for i in range(len(P)):
        z = K.triangle_of(zeta[i])
        a = K.angles(z); am = a.max(); amaxs.append(am)
        # longest side east, apex up, longest side = 0.92 spacing
        sides = [abs(z[(k + 1) % 3] - z[k]) for k in range(3)]
        k = int(np.argmax(sides)); u = z[(k + 1) % 3] - z[k]
        z = z * np.conj(u) / abs(u) / abs(u) * 1.18 * spacing / gsize
        z = z - z.mean()
        if z[(k + 2) % 3].imag < 0:
            z = np.conj(z)
        # orientation of the representative: base z1 z2 along east
        pts3 = P[i][None] + gsize * (z.real[:, None] * e1[i][None] + z.imag[:, None] * e2[i][None])
        Q = to_px(view(pts3))
        b = int(np.clip((am - np.pi / 3) / (2 * np.pi / 3), 0, 0.999) * nb)
        bins[b].append([tuple(q) for q in Q])
        dro.polygon([tuple(q) for q in Q], outline=1.0, width=max(1, int(round(0.7 * rs))))
    print('glyphs', len(P), time.time() - t0)
    for b in range(nb):
        if not bins[b]:
            continue
        im = Image.new('F', (W, H), 0.0); d = ImageDraw.Draw(im)
        for poly in bins[b]:
            d.polygon(poly, fill=1.0)
        dens = np.asarray(im, np.float32)
        am = np.pi / 3 + (b + 0.5) / nb * (2 * np.pi / 3)
        sheet.A += (1.05 * dens)[..., None] * tint_of(am)[None, None, :]
        del dens, im
    sheet.wash(np.asarray(outl, np.float32) * 0.30, 'ink')
    print('glyphs painted', time.time() - t0)
    # ink curves on the sphere (visible parts crisp, hidden parts ghosted)
    def curve(P3, width, weight, ghost=0.08):
        V3 = view(P3); Q = to_px(V3)
        front = V3[:, 2] > 0
        dens_f = np.zeros((H, W), np.float32); dens_b = np.zeros((H, W), np.float32)
        # split into runs
        idx = np.where(np.diff(front.astype(int)) != 0)[0] + 1
        runs = np.split(np.arange(len(Q)), idx)
        for r in runs:
            if len(r) < 2:
                continue
            if front[r[0]]:
                dens_f += polyline_density(W, H, Q[r], width)
            else:
                dens_b += polyline_density(W, H, Q[r], width)
        sheet.wash(np.clip(dens_f, 0, 1) * weight, 'ink')
        sheet.wash(np.clip(dens_b, 0, 1) * weight * ghost, 'ink')
    eq = K.great_circle_meridian(0)          # placeholder; equator built below
    t = np.linspace(0, 2 * np.pi, 3000)
    equator = np.stack([np.cos(t), 0 * t, np.sin(t)], -1)
    curve(equator, 2.0 * rs, 0.75)
    for lon in (0, np.pi / 3, 2 * np.pi / 3):
        curve(K.great_circle_meridian(lon, 3000), 1.3 * rs, 0.55)
    # right-angle circles: |zeta| = 1/sqrt3 around zeta = 0, i.e. around (0,0,-1), angular radius acos(-1/2 ... )
    # cap Z < -1/2 about (0,0,-1): cos(angle) = 1/2
    for lon in (0, 2 * np.pi / 3, 4 * np.pi / 3):
        cen = np.array([-np.sin(lon), 0.0, -np.cos(lon)])   # (0,0,-1) rotated about the pole axis
        curve(K.small_circle(cen, 0.5, 3000), 1.3 * rs, 0.55)
    # coral: Gaussian triangles land uniformly
    NG = 500
    zz = rng.standard_normal((NG, 3)) + 1j * rng.standard_normal((NG, 3))
    zg = K.shape_zeta(zz[:, 0], zz[:, 1], zz[:, 2])
    Pg = K.stereo(zg); Vg = view(Pg)
    fr = Vg[:, 2] > 0
    Qg = to_px(Vg[fr])
    dots = discs_density(W, H, Qg[:, 0], Qg[:, 1], np.full(len(Qg), 2.2 * rs), np.ones(len(Qg)), sigma=0.6 * rs)
    sheet.wash(np.clip(dots, 0, 1) * 0.95, 'coral')
    halo = discs_density(W, H, Qg[:, 0], Qg[:, 1], np.full(len(Qg), 5.5 * rs), np.ones(len(Qg)), sigma=3 * rs)
    sheet.wash(np.clip(halo, 0, 1) * 0.06, "coral")
    # the pole: equilateral
    Vp = view(K.POLE[None])[0]
    if Vp[2] > 0:
        Qp = to_px(Vp[None])[0]
        star = np.exp(-(((xx - Qp[0]) ** 2 + (yy - Qp[1]) ** 2) / (4.5 * rs) ** 2))
        sheet.wash(star * 0.6, 'ink')
    # strip: twelve of the thrown triangles, as thrown
    ns = 12
    cellw = 0.078 * W
    x0 = 0.5 * W - 0.5 * cellw * ns
    ysr = 0.855 * H
    strip = np.zeros((H, W), np.float32); stripc = np.zeros((H, W), np.float32)
    for j in range(ns):
        z = zz[j]; z = z - z.mean(); z = z / (abs(z).max() + 1e-9)
        Q = np.c_[x0 + (j + 0.5) * cellw + z.real * 0.34 * cellw, ysr - z.imag * 0.34 * cellw]
        strip += polyline_density(W, H, Q, 1.1 * rs, closed=True)
        if fr[j]:
            stripc += discs_density(W, H, [Q[:, 0].mean()], [Q[:, 1].mean()], [2.2 * rs], [1.0], sigma=0.5 * rs)
    sheet.wash(np.clip(strip, 0, 1) * 0.6, 'ink')
    sheet.wash(np.clip(stripc, 0, 1) * 0.9, 'coral')
    # caption
    sheet.caption_strip(0.90, 0.985, 0.5)
    title = 'Every Triangle on One Globe'
    sub = ('Take away where a triangle is, how big it is and which way it faces, and what is left is one point of this '
           'sphere (Kendall 1984): equilateral at the pole, flat along the equator, isosceles on three meridians, '
           'right-angled on three circles that each enclose a quarter of the surface. Coral: five hundred triangles '
           'thrown at random — they land evenly, so three random points are obtuse exactly three times in four.')
    lines = wrap(sub, 10.5 * rs, 'italic', 0.84 * W)
    items = [(title, W / 2, 0.918 * H, 26 * rs, 'serif_bold', 'mm')]
    for i, ln in enumerate(lines):
        items.append((ln, W / 2, 0.947 * H + i * 13.0 * rs, 10.5 * rs, 'italic', 'mm'))
    sheet.wash(text_density(W, H, items) * 0.92, 'ink')
    img = sheet.develop()
    finish(img, (SIZE, SIZE), OUT)
    amaxs = np.array(amaxs)
    cert = dict(glyphs_visible=int(len(P)), glyph_obtuse_fraction=float((amaxs > np.pi / 2).mean()),
                gaussian=K.certify(np.random.default_rng(0)))
    json.dump(cert, open(OUT.replace('.png', '_cert.json'), 'w'), indent=1)
    print(json.dumps(cert)); print('done', time.time() - t0)


if __name__ == '__main__':
    main()
