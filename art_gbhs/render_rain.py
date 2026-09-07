"""render_rain.py — 'The Rings That Never Came Home' : rain on a pond, exact linear water waves.

Each drop's rings computed in real millimetres (gravity + surface tension + viscosity), all
drops in one Fourier transform. Crests warm, troughs cool; coral hairline = the circle
r = c_g,min · t of each drop (the calm heart's edge: nothing from the drop is inside it, and
the slowest ring is the loudest); coral bead = where the drop fell.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter
sys.path.insert(0, '.')
import rain
from pastel import Sheet, PIG, polyline_density, discs_density, text_density, finish, ink_from_distance


def make_drops(seed=11, n=6, L=1000.0, tmax=1.5, tmin=0.2):
    rng = np.random.default_rng(seed)
    drops = []
    for i in range(n):
        x, y = rng.uniform(0.12 * L, 0.88 * L, 2)
        t = rng.uniform(tmin, tmax)
        bb = float(rng.choice([2.5, 3.5, 5.0, 7.0]))
        A = rng.uniform(0.7, 1.3) * (3.0 / bb) ** 1.5
        drops.append((float(x), float(y), float(t), float(A), bb))
    return drops


def render(FINAL=1024, SS=2, L=1000.0, seed=11, n=6, b=3.0, tag='rain', caption=True, warm='apricot', cool='cornflower',
           warm2='lemon', cool2='lavender', dens_amp=2.0, knee=1.0, tmax=1.5, drops=None):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    drops = drops or make_drops(seed, n, L, tmax)
    eta = rain.solve(W, L, drops, b=b)
    print(f'field {W}^2 in {time.time()-t0:.1f}s, |eta|max {np.abs(eta).max():.3g} mm')
    cgm, kg, lg = rain.cg_min()
    # ---- certificate: energy constancy (nu = 0) for the drop set, and the loudest-ring radius per drop
    E = rain.energy(1024, L, drops, b=b)
    cert = dict(L_mm=L, N=W, drops=drops, b_mm=b, cg_min=float(cgm), lambda_cg_min=float(lg),
                cp_min=float(rain.cp_min()[0]), energy_total_per_drop=[float(e[2]) for e in E])
    print(json.dumps({k: v for k, v in cert.items() if k != 'drops'}, indent=1))
    dx = L / W
    # ---- pigment: sign -> warm/cool; local wavelength (gradient/amplitude ratio) -> second pigment
    s = np.percentile(np.abs(eta), 99.3)
    amp = np.abs(eta) / s
    dens = dens_amp * np.tanh(amp * knee).astype(np.float32)
    # short-wave weight: |grad eta| / |eta| smoothed ~ k ; capillary ripples have k > 0.3/mm
    sm = gaussian_filter(np.abs(eta), 3 * rs) + 1e-6 * s
    gy, gx = np.gradient(eta)
    kk = gaussian_filter(np.hypot(gx, gy), 3 * rs) / (sm * dx)
    del gx, gy, sm
    w2 = np.clip((kk - 0.12) / 0.35, 0, 1).astype(np.float32)   # 0 gravity .. 1 capillary
    del kk
    pos = eta > 0
    sheet = Sheet(W, H, seed=seed)
    for i, (name, m, wgt) in enumerate([(warm, pos, 1 - w2), (warm2, pos, w2), (cool, ~pos, 1 - w2), (cool2, ~pos, w2)]):
        sheet.wash(dens * m * wgt, name, granulate=0.25, seed=40 + i)
    del dens, w2, amp
    # ---- coral: calm-heart circles and drop beads
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ring = np.zeros((H, W), np.float32)
    xs, ys, rr, ws = [], [], [], []
    for d in drops:
        x, y, t = d[:3]
        cx, cy = x / dx, y / dx
        r = cgm * t / dx
        d = np.abs(np.hypot(xx - cx, yy - cy) - r)
        ring += ink_from_distance(d, 0.8 * rs)
        xs.append(cx); ys.append(cy); rr.append(3.0 * rs); ws.append(1.0)
    del xx, yy
    sheet.wash(np.clip(ring, 0, 1) * 0.75, 'coral')
    sheet.wash(discs_density(W, H, xs, ys, rr, ws, sigma=0.6 * rs) * 1.5, 'coral')
    # ---- caption
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'The Rings That Never Came Home'
        sub = (f'{len(drops)} drops on real water, one Fourier transform. Nothing travels slower than {cgm:.0f} mm/s: '
               f'each drop keeps a calm heart (coral), and the slowest ring is the loudest.')
        items = [(title, 0.045 * W, 0.925 * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.045 * W, 0.962 * H, 0.0138 * H, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    out = f'{tag}_{FINAL}.png'
    finish(img, (FINAL, FINAL), out)
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(f'done {time.time()-t0:.0f}s')


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--L', type=float, default=1000.0)
    ap.add_argument('--seed', type=int, default=11)
    ap.add_argument('--n', type=int, default=6)
    ap.add_argument('--tmax', type=float, default=1.5)
    ap.add_argument('--tag', default='proto_rain')
    ap.add_argument('--nocap', action='store_true')
    ap.add_argument('--warm', default='apricot'); ap.add_argument('--cool', default='cornflower')
    ap.add_argument('--warm2', default='lemon'); ap.add_argument('--cool2', default='lavender')
    ap.add_argument('--dens', type=float, default=2.0)
    a = ap.parse_args()
    render(FINAL=a.final, SS=a.ss, L=a.L, seed=a.seed, n=a.n, tag=a.tag, caption=not a.nocap,
           warm=a.warm, cool=a.cool, warm2=a.warm2, cool2=a.cool2, dens_amp=a.dens, tmax=a.tmax)
