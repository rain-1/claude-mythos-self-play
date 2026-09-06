"""render_chimera.py — 'The Part That Will Not Agree' : a spiral-wave chimera in pastel.

Pigment = phase of each oscillator (10-pigment cycle); pigment density = how much the
neighbourhood agrees (|Z|); the incoherent core is drawn as confetti beads, one per oscillator;
ink = three wavefronts (isophase lines) where the field is coherent; coral = the rim of the
incoherent core (time-averaged local order below half its far-field value); painter's unfinished
edge toward the paper.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter, zoom, map_coordinates
from skimage import measure
from PIL import Image, ImageDraw
sys.path.insert(0, '.')
from pastel import Sheet, PIG, CYCLE, absorb, polyline_density, text_density, finish, lowfreq, noise

def render(npz, FINAL=1024, SS=2, tag='proto_chimera', caption=True, title='The Part That Will Not Agree',
           frac=0.92, core_level=0.5, seed=3):
    t0 = time.time()
    d = np.load(npz)
    theta = d['theta']; Z = d['Z']
    N = theta.shape[0]
    args = json.loads(str(d['args'])) if 'args' in d else {}
    Rbar = d['Rbar'] if 'Rbar' in d else np.abs(Z)
    omega = d['omega'] if 'omega' in d else None
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    # window: central `frac` of the domain fills the canvas
    n0 = int(round(N * (1 - frac) / 2)); n1 = N - n0
    sub = slice(n0, n1)
    th = theta[sub, sub]; R = np.abs(Z)[sub, sub]; Rb = Rbar[sub, sub]
    M = th.shape[0]
    # coherence = frequency locking when the mean-frequency field is available:
    # locked oscillators share the collective frequency Ω; drifting ones do not.
    if omega is not None:
        om = omega[sub, sub]
        Om = np.median(om)
        dev = np.abs(om - Om)
        tol = max(0.02 * np.abs(Om), 5 * np.percentile(dev, 50))
        lock_small = np.clip(1 - dev / tol, 0, 1) ** 0.5            # 1 locked … 0 drifting
        print(f'Ω = {Om:.4f}, tol {tol:.4f}, drifting fraction {np.mean(dev > tol):.3f}')
    else:
        Om = None; tol = None
        lock_small = np.clip(Rb / np.percentile(Rb, 90), 0, 1)
    f = W / M                      # canvas px per oscillator
    # smooth upsample of the phase via (cos, sin)
    c = zoom(np.cos(th), f, order=1)[:H, :W]; s = zoom(np.sin(th), f, order=1)[:H, :W]
    ph = np.arctan2(s, c)
    Rfar = np.percentile(Rb, 90)
    cnorm = np.clip(zoom(lock_small.astype(np.float32), f, order=1)[:H, :W], 0, 1)
    print(f'grid {N} -> window {M}, px/osc {f:.2f}, Rfar {Rfar:.3f}  {time.time()-t0:.0f}s', flush=True)
    # unfinished edge: irregular fade to paper
    yy, xx = np.mgrid[:H, :W].astype(np.float32)
    rr = np.hypot(xx - W / 2, yy - H / 2) / (W / 2)
    front = 0.80 + 0.10 * lowfreq(H, W, max(8, W // 10), seed + 5)
    edge = np.clip(1 - (rr - front) / 0.16, 0, 1) ** 1.5
    del xx, yy
    sheet = Sheet(W, H, seed=seed)
    # --- pigment wash by phase, density by coherence (coherent arms full, core pale)
    hue = (ph + np.pi) / (2 * np.pi)
    hh = np.mod(hue, 1.0) * len(CYCLE)
    i0 = np.floor(hh).astype(np.int8); tt = (hh - np.floor(hh)).astype(np.float32)
    base = (0.22 + 0.95 * cnorm ** 1.4) * edge
    for i, name in enumerate(CYCLE):
        wgt = np.where(i0 == i, 1 - tt, 0) + np.where(((i0 + 1) % len(CYCLE)) == i, tt, 0)
        dens = (base * wgt).astype(np.float32)
        sheet.wash(dens, name, granulate=0.18, seed=20 + i)
    print(f'washes done {time.time()-t0:.0f}s', flush=True)
    # --- the core: confetti beads, one per drifting oscillator
    core_mask_small = lock_small < core_level
    ii, jj = np.where(core_mask_small)
    if len(ii):
        im = {name: Image.new('F', (W, H), 0.0) for name in CYCLE}
        dr = {name: ImageDraw.Draw(im[name]) for name in CYCLE}
        rad = 0.40 * f
        hue_s = (th + np.pi) / (2 * np.pi)
        rng = np.random.default_rng(seed)
        jit = rng.uniform(-0.28, 0.28, (len(ii), 2)) * f
        for (a, b), (jx, jy) in zip(zip(ii, jj), jit):
            x = (b + 0.5) * f + jx; y = (a + 0.5) * f + jy
            k = int(np.floor(np.mod(hue_s[a, b], 1.0) * len(CYCLE))) % len(CYCLE)
            dr[CYCLE[k]].ellipse([x - rad, y - rad, x + rad, y + rad], fill=1.0)
        for name in CYCLE:
            arr = np.asarray(im[name], np.float32)
            if arr.max() > 0:
                sheet.wash(gaussian_filter(arr, 0.35 * rs) * 1.05 * edge, name)
        del im, dr
        print(f'{len(ii)} core beads  {time.time()-t0:.0f}s', flush=True)
    # --- ink: three wavefronts where coherent
    gy, gx = np.gradient(c); gy2, gx2 = np.gradient(s)
    gradmag = np.sqrt(gx ** 2 + gy ** 2 + gx2 ** 2 + gy2 ** 2) + 1e-6      # |∇θ| per px
    wpx = 1.3 * rs
    ink = np.zeros((H, W), np.float32)
    for k in range(3):
        th0 = -np.pi + 2 * np.pi * (k + 0.5) / 3
        sn = np.sin(ph - th0); cs = np.cos(ph - th0)
        dist = np.abs(sn) / gradmag
        ink += np.exp(-(dist / wpx) ** 2) * (cs > 0)
    ink = np.clip(ink, 0, 1) * np.clip((cnorm - 0.45) / 0.25, 0, 1) * edge
    sheet.wash(ink * 0.75, 'ink')
    del gx, gy, gx2, gy2, gradmag
    print(f'ink done {time.time()-t0:.0f}s', flush=True)
    # --- coral: rim of the incoherent core (time-averaged order below core_level × far value)
    cs_small = gaussian_filter(lock_small.astype(np.float32), 1.0)
    conts = measure.find_contours(cs_small, core_level)
    rim = np.zeros((H, W), np.float32)
    ncore = 0
    for cc in conts:
        if len(cc) < 30: continue
        pts = np.stack([(cc[:, 1] + 0.5) * f, (cc[:, 0] + 0.5) * f], 1)
        rim += polyline_density(W, H, pts, 2.4 * rs, weight=1.0, closed=True)
        ncore += 1
    rim = np.clip(gaussian_filter(rim, 0.7 * rs), 0, 1) * edge
    sheet.wash(rim * 1.5, 'coral')
    core_frac = float(core_mask_small.mean())
    if caption:
        sheet.caption_strip(0.905, 0.985, 0.5)
        ts_ = 0.030 * W; is_ = 0.0125 * W
        al = args.get('alpha', None); alpha_s = f'{al:.2f}' if al else '?'
        items = [(title, W * 0.5, H * 0.925, ts_, 'serif_bold', 'mm'),
                 (f'{M*M:,} identical phase oscillators, each coupled to its neighbourhood with a lag α = {alpha_s}: the arms lock into one rotating spiral wave,',
                  W * 0.5, H * 0.954, is_, 'italic', 'mm'),
                 (f'the {100*core_frac:.1f}% inside the coral rim never agree on a phase. Pigment: phase.  Density: how much a neighbourhood agrees.  Ink: three wavefronts.',
                  W * 0.5, H * 0.972, is_, 'italic', 'mm')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    cert = dict(npz=npz, args=args, grid=N, window=M, Rfar=float(Rfar), core_level=core_level,
                Omega=(float(Om) if Om is not None else None), freq_tol=(float(tol) if tol is not None else None),
                core_fraction=core_frac, core_components=ncore, beads=int(len(ii)))
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(json.dumps(cert), f'done {time.time()-t0:.0f}s')

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('npz')
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--tag', default='proto_chimera')
    ap.add_argument('--frac', type=float, default=0.92)
    ap.add_argument('--level', type=float, default=0.5)
    a = ap.parse_args()
    render(a.npz, FINAL=a.final, SS=a.ss, tag=a.tag, frac=a.frac, core_level=a.level)
