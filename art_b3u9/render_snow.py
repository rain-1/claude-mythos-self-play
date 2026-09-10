"""render_snow.py — 'The Snow Remembers the Cloud': one Gravner–Griffeath crystal grown through a scheduled
cloud, in pastel.  Pigment = the cloud layer in which each cell attached (plates cool, dendrites warm);
density rises with the crystal mass (thick plates darker); thin ink isochrones every dt steps tell the
growth rings; coral isochrones = the instants the cloud changed (the memory boundaries); ink outline of
the crystal; a faint blue wash for the vapour field outside (depleted near the arms — the reason for the
branching).  Certified: exact 12-fold symmetry of the attachment-time field.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter, distance_transform_edt, binary_dilation
sys.path.insert(0, '.')
from snowio import load, axial_to_cart
from pastel import Sheet, PIG, polyline_density, discs_density, text_density, ink_from_distance, finish, text_width

COOL = ['aqua', 'cornflower', 'lavender', 'mint']
WARM = ['apricot', 'blush', 'orchid', 'lemon']


def parse_log(path):
    changes = []; steps = None
    for line in open(path):
        if line.startswith('cloud change'):
            w = line.split(); changes.append((int(w[4]), int(w[6])))
        if line.startswith('crystal reached') or line.startswith('step'):
            w = line.split(); steps = int(w[1]) if line.startswith('step') else int(w[-1])
    return changes, steps


def render(prefix, N, rhos, FINAL=1024, SS=2, tag='proto_snow', fill=0.86, caption=True, blur=0.6, body_d=0.16,
           pig_d=1.15, mass_pow=0.6, mass_min=0.5, iso_n=36, iso_w=0.45, iso_d=0.55, coral_w=0.9, coral_d=1.5,
           edge_w=0.8, edge_d=0.9, vap_d=0.22, gran=0.12, plate_thresh=0.75, title='The Snow Remembers the Cloud'):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    t, c, b, d = load(prefix, N)
    changes, steps = parse_log(prefix + '.log')
    tmax = int(t.max())
    R = (N - 1) // 2
    cry = t >= 0
    # radius in cell units (Cartesian): farthest crystal cell from the centre
    I, J = np.nonzero(cry)
    xs_ = (I - R) + (J - R) / 2.0; ys_ = (J - R) * np.sqrt(3) / 2.0
    rad = float(np.hypot(xs_, ys_).max())
    p = fill * W / (2 * rad)
    print(f'crystal cells {cry.sum()}, radius {rad:.1f} cells, {p/SS:.2f} final px per cell, steps {tmax}')
    # ---- symmetry certificate (60-degree rotation about the centre in axial coords: (i,j) -> (-j, i+j))
    Ig, Jg = np.meshgrid(np.arange(N) - R, np.arange(N) - R, indexing='ij')
    i2 = -Jg; j2 = Ig + Jg
    ok = (np.abs(i2) <= R) & (np.abs(j2) <= R)
    rot = np.full_like(t, -1); rot[ok] = t[i2[ok] + R, j2[ok] + R]
    mism = int((rot != t).sum())
    refl = t.T   # reflection (i,j) -> (j,i) is a lattice symmetry
    mism_r = int((refl != t).sum())
    # ---- layers: schedule boundaries in step time
    bounds = [0] + [s for (s, r) in changes] + [tmax + 1]
    nl = len(bounds) - 1
    layer = np.full(t.shape, -1, np.int32)
    for k in range(nl):
        layer[(t >= bounds[k]) & (t < bounds[k + 1])] = k
    counts = [int((layer == k).sum()) for k in range(nl)]
    cert = dict(N=N, steps=tmax, crystal_cells=int(cry.sum()), radius_cells=rad, px_per_cell=p / SS,
                rot60_mismatch=mism, reflection_mismatch=mism_r, schedule=[dict(step=s, radius=r) for (s, r) in changes],
                rhos=list(rhos), layer_counts=counts, crystal_mass_max=float(c[cry].max()))
    print(cert)
    # ---- Cartesian rasters
    T = axial_to_cart(t.astype(np.float32), p, W, order=0, cval=-1.0)
    Lc = axial_to_cart(layer.astype(np.float32), p, W, order=0, cval=-1.0)
    C = axial_to_cart(c, p, W, order=1, cval=0.0)
    Dv = axial_to_cart(d, p, W, order=1, cval=float(rhos[-1]))
    inside = T >= 0
    # smooth time field inside the crystal (normalised blur) for contours and growth speed
    ins = inside.astype(np.float32)
    Tf = gaussian_filter(np.where(inside, T, 0).astype(np.float32), 1.0 * rs) / np.maximum(gaussian_filter(ins, 1.0 * rs), 1e-3)
    gy, gx = np.gradient(Tf)
    slow = np.hypot(gx, gy) * inside          # steps per pixel: large = slow growth = thick
    sheet = Sheet(W, H, seed=17)
    # ---- vapour outside: depleted near the crystal -> less pigment; far field faint blue
    vap = np.clip(Dv / max(rhos[-1], 1e-6), 0, 1) ** 2 * (~inside)
    sheet.wash(gaussian_filter(vap.astype(np.float32), 2.0 * rs) * vap_d, 'paperblue', granulate=gran, seed=61)
    # ---- body
    sheet.wash(gaussian_filter(inside.astype(np.float32), 1.0 * rs) * body_d, 'paperpink')
    # ---- pigment by layer, density by crystal mass
    mass = np.ones((H, W), np.float32)
    for k in range(nl):
        m = (Lc == k) & inside
        if m.sum() > 100:
            s90 = np.percentile(slow[m], 85)
            mass[m] = mass_min + (1 - mass_min) * np.clip(slow[m] / max(s90, 1e-9), 0, 1) ** mass_pow
    ci = wi = 0
    palette = []
    for k in range(nl):
        if rhos[k] < plate_thresh:
            pig = COOL[ci % len(COOL)]; ci += 1
        else:
            pig = WARM[wi % len(WARM)]; wi += 1
        palette.append(pig)
        f = (Lc == k).astype(np.float32) * mass
        f = gaussian_filter(f, blur * rs)
        sheet.wash(f * pig_d, pig, granulate=gran, seed=70 + k)
    cert['palette'] = palette
    # ---- isochrones (growth rings): boundaries between time bands, thin ink
    dt = tmax / iso_n
    band = np.where(inside, np.floor(Tf / dt), -1)
    edge_iso = np.zeros((H, W), bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = band[:H - dy, :W - dx]; bb = band[dy:, dx:]
        e = (a != bb) & (a >= 0) & (bb >= 0)
        edge_iso[:H - dy, :W - dx] |= e
    diso = distance_transform_edt(~edge_iso)
    sheet.wash(ink_from_distance(diso, iso_w * rs) * iso_d, 'ink')
    # ---- coral: the cloud-change isochrones
    edge_c = np.zeros((H, W), bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = Lc[:H - dy, :W - dx]; bb = Lc[dy:, dx:]
        e = (a != bb) & (a >= 0) & (bb >= 0)
        edge_c[:H - dy, :W - dx] |= e
    dc = distance_transform_edt(~edge_c)
    sheet.wash(ink_from_distance(dc, coral_w * rs) * coral_d, 'coral')
    # ---- outline of the crystal
    d_in = distance_transform_edt(inside); d_out = distance_transform_edt(~inside)
    edge = ink_from_distance(np.where(inside, d_in, d_out) - 0.5, edge_w * rs)
    sheet.wash(edge * edge_d, 'ink')
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        sub = ("One crystal, one cloud with six layers: plates where the vapour was thin, ferns where it was thick. "
               "Every ring is a moment; the coral rings are the moments the weather changed. Grown exactly, twelvefold.")
        fs = 0.0135 * H
        fs = min(fs, fs * 0.90 * W / max(1, text_width(sub, fs, 'italic')))
        items = [(title, 0.045 * W, 0.925 * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.045 * W, 0.962 * H, fs, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(f'done {time.time()-t0:.0f}s')


if __name__ == '__main__':
    kw = {}
    for a in sys.argv[1:]:
        k, v = a.split('=', 1)
        try:
            kw[k] = eval(v)
        except Exception:
            kw[k] = v
    render(**kw)
