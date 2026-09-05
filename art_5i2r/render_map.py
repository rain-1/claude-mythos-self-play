"""render_map.py — 'Every Map Is a Handful of Coins' (2560²).
A uniformly random simple planar triangulation (edge-flip Markov chain), one vertex removed, packed as
coins in the disc (Koebe–Andreev–Thurston). Pigment: graph distance from the central coin (rings of the
random metric); density: degree. Coral: one geodesic from the centre to the rim, through coin centres —
a straight line in a random world.
"""
import numpy as np, json, sys, time
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import pastel as P
from randtri import build
from render_page import draw_coins

INK = P.PIG['ink']


def render(n=1200, S=2560, SS=2, out='map_2560.png', seed=3):
    t0 = time.time()
    Pk = build(n, seed=seed, verbose=True)
    mesh, C, R, deg, dcen, v0, A = Pk['mesh'], Pk['C'], Pk['R'], Pk['deg'], Pk['dcen'], Pk['v0'], Pk['adjA']
    bd, edges = mesh['boundary'], mesh['edges']
    V = len(bd)
    Wd, Hd = S * SS, S * SS
    sh = P.Sheet(Wd, Hd, seed=seed + 20)
    cx, cy = 0.5 * Wd, 0.465 * Hd
    Rd = 0.40 * Wd
    X = cx + Rd * C.real; Y = cy - Rd * C.imag
    Rp = R * Rd
    # tints: distance rings -> pigment cycle (stride 1), degree -> density
    dmax = dcen.max()
    absorb = np.zeros((V, 3), np.float32)
    dn = np.clip((deg - 3) / 9.0, 0, 1)
    for v in range(V):
        hue = (0.35 + 0.085 * dcen[v]) % 1.0
        i0, i1, t = P.hue_to_pigments(np.array([hue]))
        tint = P.mix_tint(P.CYCLE[int(i0[0])], P.CYCLE[int(i1[0])], float(t[0]))
        absorb[v] = (0.45 + 0.75 * dn[v]) * P.absorb(tint)
    Am, I = draw_coins(Wd, Hd, X, Y, Rp, absorb, SS, gap=0.05, ink_min=1.4)
    g = P.noise(Hd, Wd, 1.6, seed + 11)
    Am *= (1 + 0.15 * g)[..., None]
    tot = Am.sum(-1); b = gaussian_filter(tot, 1.2 * SS)
    gy, gx = np.gradient(b); edge = np.hypot(gx, gy)
    nz = edge[edge > 0]
    if nz.size:
        edge /= (np.percentile(nz, 99) + 1e-9)
    Am *= (1 + 0.30 * np.clip(edge, 0, 1))[..., None]
    Am = gaussian_filter(Am, [0.5 * SS, 0.5 * SS, 0])
    sh.A += Am; del Am
    sh.wash(gaussian_filter(I, 0.45 * SS) * 0.8, INK)
    # the unit circle as a thin ink ring
    ring = Image.new('F', (Wd, Hd), 0.0); dr = ImageDraw.Draw(ring)
    dr.ellipse([cx - Rd, cy - Rd, cx + Rd, cy + Rd], outline=1.0, width=int(round(1.2 * SS)))
    sh.wash(gaussian_filter(np.asarray(ring, np.float32), 0.6 * SS) * 0.5, INK)
    # coral geodesic: shortest path from v0 to the farthest rim vertex
    from scipy.sparse.csgraph import shortest_path
    D, pred = shortest_path(A, unweighted=True, indices=v0, return_predecessors=True)
    rim = np.where(bd)[0]
    tgt = int(rim[np.argmax(D[rim])])
    path = [tgt]
    while path[-1] != v0:
        path.append(int(pred[path[-1]]))
    path = path[::-1]
    geo = Image.new('F', (Wd, Hd), 0.0); dg = ImageDraw.Draw(geo)
    pts = [(float(X[v]), float(Y[v])) for v in path]
    dg.line(pts, fill=1.0, width=int(round(2.0 * SS)), joint='curve')
    for v in path:
        rr_ = 2.6 * SS
        dg.ellipse([X[v] - rr_, Y[v] - rr_, X[v] + rr_, Y[v] + rr_], fill=1.0)
    sh.wash(gaussian_filter(np.asarray(geo, np.float32), 0.7 * SS) * 2.0, 'coral')
    c = Pk['cert']
    sh.caption_strip(0.905, 0.99, 0.55)
    items = [("Every Map Is a Handful of Coins", 0.5 * Wd, 0.925 * Hd, int(0.032 * Wd), 'serif_bold', 'mm'),
             (f"A uniformly random planar triangulation with {n} vertices ({c['flips']:,} edge flips, {c['acceptance']:.0%} accepted, simple and spherical at every check), one vertex removed and the rest told as coins (Koebe–Andreev–Thurston).",
              0.5 * Wd, 0.955 * Hd, int(0.0108 * Wd), 'italic', 'mm'),
             (f"Pigment = graph distance from the central coin ({int(dmax)} rings), darkness = degree; tangencies to {c['max_tangency_rel']:.0e}; the coral thread is one geodesic of {len(path)-1} steps, a straight line in a random world.",
              0.5 * Wd, 0.975 * Hd, int(0.0108 * Wd), 'italic', 'mm')]
    sh.wash(P.text_density(Wd, Hd, items) * 1.1, INK)
    img = sh.develop()
    P.finish(img, (S, S), out)
    c.update(geodesic_steps=len(path) - 1, distance_max=int(dmax))
    json.dump(c, open(out.replace('.png', '_cert.json'), 'w'), indent=1)
    print(f'render {out} {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    out = sys.argv[3] if len(sys.argv) > 3 else f'proto_map_{S}.png'
    render(n, S=S, out=out)
