"""render_kb1d.py — 'The Part That Will Not Agree' : the Kuramoto–Battogtokh ring chimera as a
space–time carpet.  x = position on the ring (horizontal), t = time (upward), pigment = phase,
density = locked (full) vs drifting (pale + confetti beads), ink = isophase wavefronts in the
locked arc, coral = the mean-frequency profile (the arch) with the plateau = the locked arc."""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image, ImageDraw
sys.path.insert(0, '.')
from pastel import Sheet, PIG, CYCLE, absorb, polyline_density, text_density, finish, lowfreq, draw_lines_density

def render(npz='kb1d_512.npz', FINAL=2560, SS=2, tag='kb', caption=True, rows=None, window=60.0, dt=0.025, beads=False):
    t0 = time.time()
    d = np.load(npz)
    x = d['x']; carpet = d['carpet']; freq = d['freq']
    N = len(x); T_rows = carpet.shape[0]
    # locked plateau = histogram mode of the mean frequency
    h, e = np.histogram(freq, bins=400); k = np.argmax(h); Om = 0.5 * (e[k] + e[k + 1])
    dev = np.abs(freq - Om); locked = dev < 0.005
    # roll the ring so the locked arc is centred
    idx = np.arange(N); c = np.angle(np.sum(locked * np.exp(2j * np.pi * idx / N)))
    shift = int(round(N / 2 - c / (2 * np.pi) * N)) % N
    carpet = np.roll(carpet, shift, axis=1); freq = np.roll(freq, shift); locked = np.roll(locked, shift); dev = np.roll(dev, shift)
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    # image area: full width, rows 0.05H..0.86H ; time upward
    y0, y1 = int(0.045 * H), int(0.865 * H)
    Himg = y1 - y0
    nwin = int(window / dt)
    carpet = carpet[-nwin:]; T_rows = carpet.shape[0]
    nrows = rows or min(T_rows, Himg)
    sel = np.linspace(0, T_rows - 1, nrows).astype(int)
    th = carpet[sel][::-1]                      # latest time at the top
    fx = W / N; fy = Himg / nrows
    cs = zoom(np.cos(th), (fy, fx), order=1)[:Himg, :W]; sn = zoom(np.sin(th), (fy, fx), order=1)[:Himg, :W]
    ph = np.arctan2(sn, cs)
    lock_row = np.clip(1 - dev / 0.02, 0, 1) ** 0.6
    lockW = zoom(lock_row, fx, order=1)[:W]
    sheet = Sheet(W, H, seed=11)
    hue = (ph + np.pi) / (2 * np.pi); hh = np.mod(hue, 1.0) * len(CYCLE)
    i0 = np.floor(hh).astype(np.int8); tt = (hh - np.floor(hh)).astype(np.float32)
    # unfinished edge top/bottom (irregular)
    yy = np.arange(Himg, dtype=np.float32)[:, None] / Himg
    front = lowfreq(1, W, max(8, W // 12), 3)[0] * 0.03
    edge = np.clip((yy - 0.02 - front[None, :]) / 0.05, 0, 1) * np.clip((0.98 + front[None, :] - yy) / 0.05, 0, 1)
    base = (0.82 + 0.55 * lockW[None, :] ** 1.3) * edge
    for i, name in enumerate(CYCLE):
        wgt = np.where(i0 == i, 1 - tt, 0) + np.where(((i0 + 1) % len(CYCLE)) == i, tt, 0)
        dens = np.zeros((H, W), np.float32); dens[y0:y1] = base * wgt
        sheet.wash(dens, name, granulate=0.15, seed=30 + i)
    print(f'washes {time.time()-t0:.0f}s', flush=True)
    # confetti beads for drifting oscillators: one bead per oscillator per bead-row
    drift_cols = np.where(dev > 0.02)[0]
    if beads and len(drift_cols):
        im = {name: Image.new('F', (W, H), 0.0) for name in CYCLE}
        dr = {name: ImageDraw.Draw(im[name]) for name in CYCLE}
        pitch = max(fx, 3.0 * rs)
        nb_rows = int(Himg / pitch)
        rng = np.random.default_rng(5)
        rad = 0.36 * pitch
        rsel = np.linspace(0, nrows - 1, nb_rows).astype(int)
        for r_i, r in enumerate(rsel):
            yb = y0 + (r_i + 0.5) * pitch
            for cidx in drift_cols:
                xb = (cidx + 0.5) * fx + rng.uniform(-0.3, 0.3) * fx
                yj = yb + rng.uniform(-0.3, 0.3) * pitch
                kk = int(np.floor(np.mod((th[r, cidx] + np.pi) / (2 * np.pi), 1.0) * len(CYCLE))) % len(CYCLE)
                dr[CYCLE[kk]].ellipse([xb - rad, yj - rad, xb + rad, yj + rad], fill=1.0)
        for name in CYCLE:
            arr = np.asarray(im[name], np.float32)
            if arr.max() > 0:
                e2 = np.zeros((H, W), np.float32); e2[y0:y1] = edge
                sheet.wash(gaussian_filter(arr, 0.35 * rs) * 0.95 * e2, name)
        print(f'beads {time.time()-t0:.0f}s', flush=True)
    # ink wavefronts in the locked arc
    gy, gx = np.gradient(cs); gy2, gx2 = np.gradient(sn)
    gm = np.sqrt(gx ** 2 + gy ** 2 + gx2 ** 2 + gy2 ** 2) + 1e-6
    ink = np.zeros((Himg, W), np.float32)
    for kk in range(3):
        th0 = -np.pi + 2 * np.pi * (kk + 0.5) / 3
        s_ = np.sin(ph - th0); c_ = np.cos(ph - th0)
        ink += np.exp(-((np.abs(s_) / gm) / (1.2 * rs)) ** 2) * (c_ > 0)
    ink = np.clip(ink, 0, 1) * np.clip((lockW[None, :] - 0.5) / 0.3, 0, 1) * edge
    full = np.zeros((H, W), np.float32); full[y0:y1] = ink
    sheet.wash(full * 0.7, 'ink')
    del gx, gy, gx2, gy2, gm
    # the arch: mean frequency profile below the carpet (coral), plateau = locked arc
    ya, yb_ = int(0.875 * H), int(0.915 * H)
    fmin, fmax = freq.min(), freq.max()
    ys = yb_ - (freq - fmin) / (fmax - fmin + 1e-9) * (yb_ - ya)
    pts = np.stack([(np.arange(N) + 0.5) * fx, ys], 1)
    arch = polyline_density(W, H, pts, 2.4 * rs, weight=1.0)
    sheet.wash(np.clip(gaussian_filter(arch, 0.6 * rs), 0, 1) * 1.5, 'coral')
    # baseline (Ω) hairline + locked-arc boundaries as coral verticals through the carpet
    yl, xl = np.ogrid[:H, :W]
    base_y = yb_ - (Om - fmin) / (fmax - fmin + 1e-9) * (yb_ - ya)
    sheet.wash((np.exp(-((yl - base_y) / (0.8 * rs)) ** 2) * (xl >= 0)).astype(np.float32) * 0.35, 'ink')
    # arc boundaries
    lk = locked.astype(int); bd = np.where(np.diff(lk) != 0)[0]
    vert = np.zeros((H, W), np.float32)
    for b in bd:
        xb = (b + 1) * fx
        vert += np.exp(-((xl - xb) / (1.0 * rs)) ** 2) * ((yl >= y0) & (yl <= yb_))
    sheet.wash(np.clip(vert, 0, 1) * 0.9, 'coral')
    if caption:
        sheet.caption_strip(0.925, 0.995, 0.5)
        ts_ = 0.030 * W; is_ = 0.0125 * W
        items = [('The Part That Will Not Agree', W * 0.5, H * 0.945, ts_, 'serif_bold', 'mm'),
                 (f'{N} identical oscillators on a ring, each coupled to its neighbours with a phase lag (Kuramoto–Battogtokh 2002): time runs upward for {window:.0f} units, after {d["carpet"].shape[0]*dt + 2200:.0f} of settling.',
                  W * 0.5, H * 0.9705, is_, 'italic', 'mm'),
                 (f'The {100*locked.mean():.0f}% between the coral lines lock to one frequency (the plateau of the coral arch, Ω = {Om:.3f}); the rest never do — same units, same rule, no difference between them.',
                  W * 0.5, H * 0.986, is_, 'italic', 'mm')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    cert = dict(npz=npz, N=int(N), Omega_plateau=float(Om), locked_fraction=float(locked.mean()),
                drifting_fraction=float(np.mean(dev > 0.05)), freq_min=float(fmin), freq_max=float(fmax),
                kappa=4.0, alpha=1.457, window=float(window), freq_window=float(d['carpet'].shape[0] * dt))
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(json.dumps(cert), f'done {time.time()-t0:.0f}s')

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--npz', default='kb1d_512.npz')
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--tag', default='proto_kb')
    a = ap.parse_args()
    render(a.npz, FINAL=a.final, SS=a.ss, tag=a.tag)
