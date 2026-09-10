"""snow_sheet.py — 'The Alphabet of the Cloud': six crystals, one parameter set (β = 2, α = 0.1, θ = 0.05,
κ = 0.02, μ = 0.05, γ = 5e-4), six vapour densities.  Each is the letter the hero's cloud writes at that
density.  Pigment cool→warm with ρ; ink isochrones every 1/24 of the growth; outline; label per cell.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter, distance_transform_edt
sys.path.insert(0, '.')
from snowio import load, axial_to_cart
from pastel import Sheet, PIG, text_density, ink_from_distance, finish, text_width

PIGS = ['aqua', 'cornflower', 'lavender', 'orchid', 'blush', 'apricot']


def render(prefixes, rhos, N=401, FINAL=1024, SS=2, tag='proto_sheet', caption=True, iso_n=24, iso_w=0.45, iso_d=0.55,
           edge_w=0.8, edge_d=0.9, pig_d=1.1, mass_min=0.5, mass_pow=0.6, blur=0.6, gran=0.12, cell_fill=0.86):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    ncol, nrow = 3, 2
    top, bottom = 0.05 * H, (0.86 if caption else 0.98) * H
    cw = W / ncol; ch = (bottom - top) / nrow
    cell = int(min(cw, ch) * 0.98)
    sheet = Sheet(W, H, seed=19)
    ink_iso = np.zeros((H, W), np.float32); ink_edge = np.zeros((H, W), np.float32)
    labels = []
    cert = []
    for k, (pre, rho) in enumerate(zip(prefixes, rhos)):
        t, c, b, d = load(pre, N)
        cry = t >= 0; R = (N - 1) // 2
        I, J = np.nonzero(cry)
        rad = float(np.hypot((I - R) + (J - R) / 2.0, (J - R) * np.sqrt(3) / 2.0).max())
        p = cell_fill * cell / (2 * rad)
        T = axial_to_cart(t.astype(np.float32), p, cell, order=0, cval=-1.0)
        inside = T >= 0
        ins = inside.astype(np.float32)
        Tf = gaussian_filter(np.where(inside, T, 0).astype(np.float32), 1.0 * rs) / np.maximum(gaussian_filter(ins, 1.0 * rs), 1e-3)
        gy, gx = np.gradient(Tf); slow = np.hypot(gx, gy) * inside
        s85 = np.percentile(slow[inside], 85) if inside.sum() > 100 else 1.0
        mass = mass_min + (1 - mass_min) * np.clip(slow / max(s85, 1e-9), 0, 1) ** mass_pow
        col, row = k % ncol, k // ncol
        x0 = int(col * cw + (cw - cell) / 2); y0 = int(top + row * ch + (ch - cell) / 2)
        f = np.zeros((H, W), np.float32)
        f[y0:y0 + cell, x0:x0 + cell] = gaussian_filter(ins * mass, blur * rs)
        sheet.wash(f * pig_d, PIGS[k], granulate=gran, seed=70 + k)
        # isochrones
        dt = T.max() / iso_n
        band = np.where(inside, np.floor(Tf / dt), -1)
        e = np.zeros((cell, cell), bool)
        for dy, dx in ((0, 1), (1, 0)):
            a_ = band[:cell - dy, :cell - dx]; b_ = band[dy:, dx:]
            e[:cell - dy, :cell - dx] |= (a_ != b_) & (a_ >= 0) & (b_ >= 0)
        ink_iso[y0:y0 + cell, x0:x0 + cell] = ink_from_distance(distance_transform_edt(~e), iso_w * rs)
        d_in = distance_transform_edt(inside); d_out = distance_transform_edt(~inside)
        ink_edge[y0:y0 + cell, x0:x0 + cell] = ink_from_distance(np.where(inside, d_in, d_out) - 0.5, edge_w * rs)
        labels.append((f'ρ = {rho:.2f}', x0 + cell / 2, y0 + cell * 0.985, 0.020 * H, 'italic', 'ms'))
        cert.append(dict(rho=rho, cells=int(cry.sum()), steps=int(t.max()), radius=rad))
        print(k, cert[-1], f'{time.time()-t0:.0f}s')
    sheet.wash(ink_iso * iso_d, 'ink'); sheet.wash(ink_edge * edge_d, 'ink')
    sheet.wash(text_density(W, H, labels) * 1.5, 'ink')
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'The Alphabet of the Cloud'
        sub = ("Six crystals, one law, six vapour densities: plate, sectored plate, six petals, dendrite, fern, and broad petals again. "
               "The hero's cloud is written in these six letters. Rings every 1/24 of the growth; all grown exactly twelvefold.")
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
    S = '/tmp/claude-0/-home-user-claude-mythos-self-play/38c33a52-2f72-54f9-891a-930f8e1e4306/scratchpad/'
    rhos = [0.55, 0.65, 0.75, 0.85, 0.95, 1.05]
    kw = {}
    for a in sys.argv[1:]:
        k, v = a.split('=', 1)
        try:
            kw[k] = eval(v)
        except Exception:
            kw[k] = v
    render([S + f'sh{r}' for r in rhos], rhos, **kw)
