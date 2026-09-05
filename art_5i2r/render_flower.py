"""render_flower.py — 'The Flower Told in Circles' (hero).
The maximal packing in the disc, each coin tinted by where it came from in the flower;
coral threads = the EXACT conformal images of the flower's hex rows (the centres hug them);
the flower itself as a ghost behind the disc.
"""
import numpy as np, json, sys, time
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import pastel as P
from cpack import build, Flower

INK = P.PIG['ink']


def render(pack, S=1024, SS=2, out='proto_flower.png', ghost=True, threads=True, caption=True, seed=3):
    t0 = time.time()
    Wd = S * SS; Hd = S * SS
    sh = P.Sheet(Wd, Hd, seed=seed)
    mesh, C, R = pack['mesh'], pack['C'], pack['R']
    W, bd, edges = mesh['W'], mesh['boundary'], mesh['edges']
    fl = pack['flower']
    h = mesh['h']
    cx, cy = 0.5 * Wd, 0.485 * Hd
    Rd = 0.385 * Wd                      # unit disc radius in px
    px = lambda z: (cx + Rd * np.real(z), cy - Rd * np.imag(z))

    # ---- pigment per coin: hue = source angle, density = source radius (petals darkest)
    ang = np.angle(W) / (2 * np.pi)
    i0, i1, t = P.hue_to_pigments(ang + 0.05)
    rad = np.abs(W) / np.abs(fl.boundary()).max()
    dens = 0.30 + 0.75 * rad ** 1.6
    absorb = np.zeros((len(W), 3), np.float32)
    for k in range(len(W)):
        tint = P.mix_tint(P.CYCLE[i0[k]], P.CYCLE[i1[k]], float(t[k]))
        absorb[k] = dens[k] * P.absorb(tint)
    # ---- fills: three channel images
    chans = [Image.new('F', (Wd, Hd), 0.0) for _ in range(3)]
    drs = [ImageDraw.Draw(im) for im in chans]
    ink = Image.new('F', (Wd, Hd), 0.0); dink = ImageDraw.Draw(ink)
    order = np.argsort(-R)               # big first (no overlaps anyway)
    X, Y = px(C)
    Rp = R * Rd
    gap = 0.045                          # paper gap between coin and its outline
    for k in order:
        r = Rp[k]
        if r < 0.6:
            continue
        rf = r * (1 - gap)
        for c in range(3):
            drs[c].ellipse([X[k] - rf, Y[k] - rf, X[k] + rf, Y[k] + rf], fill=float(absorb[k, c]))
        if r > 1.8 * SS:
            wline = max(1.0, 0.035 * r + 0.35 * SS)
            dink.ellipse([X[k] - r, Y[k] - r, X[k] + r, Y[k] + r], outline=1.0, width=int(round(wline)))
    A = np.stack([np.asarray(im, np.float32) for im in chans], axis=-1)
    del chans
    # granulation + soft edge (pigment pooling at the coin rims)
    g = P.noise(Hd, Wd, 1.6, seed + 11)
    A *= (1 + 0.16 * g)[..., None]
    tot = A.sum(-1)
    b = gaussian_filter(tot, 1.2 * SS)
    gy, gx = np.gradient(b)
    edge = np.hypot(gx, gy)
    edge /= (np.percentile(edge[edge > 0], 99) + 1e-9) if (edge > 0).any() else 1
    A *= (1 + 0.35 * np.clip(edge, 0, 1))[..., None]
    A = gaussian_filter(A, [0.5 * SS, 0.5 * SS, 0])
    sh.A += A
    del A
    # ---- ghost of the flower behind: outline + faint hex rings of the SOURCE packing
    if ghost:
        bdry = fl.boundary(3000)
        gx_, gy_ = px(bdry)
        pts = list(zip(gx_.tolist(), gy_.tolist()))
        ghost_im = Image.new('F', (Wd, Hd), 0.0); dg = ImageDraw.Draw(ghost_im)
        dg.line(pts + [pts[0]], fill=1.0, width=int(round(1.1 * SS)), joint='curve')
        rs = 0.5 * h * Rd
        sx, sy = px(W)
        for k in range(len(W)):
            if abs(C[k]) > 0 and np.abs(W[k]) < 0.0:
                continue
            dg.ellipse([sx[k] - rs, sy[k] - rs, sx[k] + rs, sy[k] + rs], outline=1.0, width=max(1, int(round(0.5 * SS))))
        gd = np.asarray(ghost_im, np.float32)
        gd = gaussian_filter(gd, 0.6 * SS)
        # ghost is faint everywhere, and even fainter under the disc
        rr = np.hypot(np.arange(Wd)[None, :] - cx, np.arange(Hd)[:, None] - cy) / Rd
        under = np.clip((1.02 - rr) / 0.04, 0, 1)
        gd *= (0.30 - 0.20 * under)
        sh.wash(gd, INK)
    # ---- coral threads: exact conformal images of the hex rows (three directions, every 3rd row)
    if threads:
        th_im = Image.new('F', (Wd, Hd), 0.0); dt = ImageDraw.Draw(th_im)
        e1 = 1.0; e2 = np.exp(1j * np.pi / 3); e3 = np.exp(2j * np.pi / 3)
        bdry = fl.boundary(4000)
        for e in (e1, e2, e3):
            n = e * 1j                     # normal direction
            for m in range(-40, 41, 3):
                off = m * h * np.sqrt(3) / 2 * n    # rows are spaced h*sqrt3/2 apart
                ts = np.linspace(-1.8, 1.8, 900)
                line = off + ts * e
                ins = fl.inside(line)
                if ins.sum() < 5:
                    continue
                # split into runs of inside points
                idx = np.where(ins)[0]
                runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
                for run in runs:
                    if len(run) < 5:
                        continue
                    zz = fl.inverse(line[run])
                    ok = ~np.isnan(zz)
                    zz = zz[ok]
                    xx, yy = px(zz)
                    dt.line(list(zip(xx.tolist(), yy.tolist())), fill=1.0, width=int(round(1.0 * SS)), joint='curve')
        td = np.asarray(th_im, np.float32)
        td = gaussian_filter(td, 0.55 * SS)
        sh.wash(td * 1.35, 'coral')
    # ---- caption
    if caption:
        sh.caption_strip(0.905, 0.985, 0.55)
        items = [("The Flower Told in Circles", 0.5 * Wd, 0.925 * Hd, int(0.030 * Wd), 'serif_bold', 'mm'),
                 ("Every coin of the flower keeps its six neighbours and is told again inside the circle; "
                  "the coral threads are the true Riemann map, and the coins agree with them.",
                  0.5 * Wd, 0.960 * Hd, int(0.0125 * Wd), 'italic', 'mm')]
        txt = P.text_density(Wd, Hd, items)
        sh.wash(txt * 1.1, INK)
    img = sh.develop()
    P.finish(img, (S, S), out)
    print(f'render {out} {time.time()-t0:.0f}s')


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.06
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    out = sys.argv[3] if len(sys.argv) > 3 else f'proto_flower_{S}.png'
    pack = build(h, verbose=False)
    print(json.dumps({k: pack['cert'][k] for k in ('V', 'map_err_max', 'map_err_mean', 'max_tangency_rel', 'iters')}))
    render(pack, S=S, SS=2, out=out)
