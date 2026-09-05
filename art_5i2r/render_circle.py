"""render_circle.py — 'The Leaf Told in a Circle' (2560²).
The same hexagonal packing of the leaf, repacked as the maximal packing of the unit disc
(boundary coins are horocycles) — Thurston's discrete Riemann map, Rodin–Sullivan 1987.
Certificate: centres vs the exact conformal map (MFS) of the carrier-offset leaf; tangencies.
"""
import numpy as np, json, sys, time
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import pastel as P
from cpack import hex_mesh, pack, layout, euclid_circles
from cpack_rect import Leaf, Offset, ExactMap
from render_page import coin_tints, draw_coins

INK = P.PIG['ink']


def build_disc(h, region):
    mesh = hex_mesh(region, h)
    W, bd, edges = mesh['W'], mesh['boundary'], mesh['edges']
    r, th, it = pack(mesh, verbose=False, maxit=40000)
    v0 = int(np.argmin(np.abs(W)))
    nb = np.concatenate([edges[edges[:, 0] == v0][:, 1], edges[edges[:, 1] == v0][:, 0]])
    v1 = int(nb[np.argmax((W[nb] - W[v0]).real)])
    z, placed = layout(mesh, r, v0, v1)
    assert placed.all()
    C, R, hs = euclid_circles(mesh, r, z)
    rc = Offset(region, 0.5 * h); ex = ExactMap(rc)
    fin = ~bd & rc.inside(W)
    zex = ex(W[fin])
    err = np.abs(C[fin] - zex)
    d = np.abs(C[edges[:, 0]] - C[edges[:, 1]]); s = R[edges[:, 0]] + R[edges[:, 1]]
    cert = dict(h=h, V=int(len(W)), boundary=int(bd.sum()), euler=int(mesh['euler']), iters=int(it),
                max_angle_err=float(np.abs(th[~bd] - 2 * np.pi).max()), max_tangency_rel=float(np.abs(d - s).max() / s.min()),
                horocycle_spread=float(hs), mfs_boundary_resid=ex.bdry_resid,
                map_err_mean=float(err.mean()), map_err_max=float(err.max()), map_err_median=float(np.median(err)))
    return dict(mesh=mesh, r=r, z=z, C=C, R=R, cert=cert, region=region, region_c=rc, ex=ex)


def render(pk, S=2560, SS=2, out='circle_2560.png', seed=9, rows_every=4, row_dir=1):
    t0 = time.time()
    Wd, Hd = S * SS, S * SS
    sh = P.Sheet(Wd, Hd, seed=seed)
    mesh, C, R, region, rc, ex = pk['mesh'], pk['C'], pk['R'], pk['region'], pk['region_c'], pk['ex']
    W, bd = mesh['W'], mesh['boundary']; h = mesh['h']
    absorb = coin_tints(W, region)
    dirs = {0: 1.0, 1: np.exp(1j * np.pi / 3), 2: np.exp(2j * np.pi / 3)}
    e = dirs[row_dir]; nrm = 1j * e
    mrow = np.round((W * np.conj(nrm)).real / (h * np.sqrt(3) / 2)).astype(int)
    absorb = absorb * np.where((mrow % rows_every) == 0, 1.45, 1.0)[:, None]
    cx, cy = 0.5 * Wd, 0.465 * Hd
    Rd = 0.36 * Wd
    px = lambda q: (cx + Rd * np.real(q), cy - Rd * np.imag(q))
    X, Y = px(C)
    A, I = draw_coins(Wd, Hd, X, Y, R * Rd, absorb, SS)
    g = P.noise(Hd, Wd, 1.6, seed + 11)
    A *= (1 + 0.15 * g)[..., None]
    tot = A.sum(-1); b = gaussian_filter(tot, 1.2 * SS)
    gy, gx = np.gradient(b); edge = np.hypot(gx, gy)
    nz = edge[edge > 0]
    if nz.size:
        edge /= (np.percentile(nz, 99) + 1e-9)
    A *= (1 + 0.30 * np.clip(edge, 0, 1))[..., None]
    A = gaussian_filter(A, [0.5 * SS, 0.5 * SS, 0])
    sh.A += A; del A
    sh.wash(gaussian_filter(I, 0.45 * SS) * 0.85, INK)
    # ghost of the leaf behind, same centre, same scale (unit disc radius = Rd): outline + faint hex rings
    gh = Image.new('F', (Wd, Hd), 0.0); dg = ImageDraw.Draw(gh)
    bdry = region.boundary(3000); bx, by = px(bdry)
    dg.line(list(zip(bx.tolist(), by.tolist())) + [(float(bx[0]), float(by[0]))], fill=1.0, width=int(round(1.3 * SS)), joint='curve')
    sx, sy = px(W); rs = 0.5 * h * Rd
    for k in range(len(W)):
        dg.ellipse([sx[k] - rs, sy[k] - rs, sx[k] + rs, sy[k] + rs], outline=1.0, width=max(1, int(round(0.5 * SS))))
    gd = gaussian_filter(np.asarray(gh, np.float32), 0.6 * SS)
    rr = np.hypot(np.arange(Wd)[None, :] - cx, np.arange(Hd)[:, None] - cy) / Rd
    under = np.clip((1.01 - rr) / 0.03, 0, 1)
    gd *= (0.34 - 0.26 * under)
    sh.wash(gd, INK)
    # coral rows: exact images of the drawn rows
    rows_im = Image.new('F', (Wd, Hd), 0.0); dr = ImageDraw.Draw(rows_im)
    spacing = h * np.sqrt(3) / 2; ts = np.linspace(-1.8, 1.8, 700); nrow = 0
    for m in range(-70, 71):
        if m % rows_every:
            continue
        line = m * spacing * nrm + ts * e
        idx = np.where(rc.inside(line))[0]
        if len(idx) < 6:
            continue
        for run in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):
            if len(run) < 6:
                continue
            q = ex(line[run][::3]); x2, y2 = px(q)
            dr.line(list(zip(x2.tolist(), y2.tolist())), fill=1.0, width=int(round(1.0 * SS)), joint='curve')
            nrow += 1
    sh.wash(gaussian_filter(np.asarray(rows_im, np.float32), 0.55 * SS) * 1.25, 'coral')
    c = pk['cert']
    sh.caption_strip(0.905, 0.99, 0.55)
    items = [("The Leaf Told in a Circle", 0.5 * Wd, 0.925 * Hd, int(0.032 * Wd), 'serif_bold', 'mm'),
             ("The same coins again, now with the rim coins swelling to touch the circle; the ghost behind is the leaf they came from.",
              0.5 * Wd, 0.955 * Hd, int(0.0115 * Wd), 'italic', 'mm'),
             (f"Thurston's discrete Riemann map: {c['V']} coins, tangencies to {c['max_tangency_rel']:.0e}; the coral rows are the exact map, and the coins miss it by {c['map_err_median']:.3f} on average (Rodin–Sullivan).",
              0.5 * Wd, 0.975 * Hd, int(0.0115 * Wd), 'italic', 'mm')]
    sh.wash(P.text_density(Wd, Hd, items) * 1.1, INK)
    img = sh.develop()
    P.finish(img, (S, S), out)
    json.dump(c, open(out.replace('.png', '_cert.json'), 'w'), indent=1)
    print(f'render {out} rows={nrow} {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    out = sys.argv[3] if len(sys.argv) > 3 else f'proto_circle_{S}.png'
    pk = build_disc(h, Leaf())
    print(json.dumps(pk['cert']))
    render(pk, S=S, out=out)
