"""render_doyle.py — 'Nothing Lost in the Spiral' (2560²).
A (p,q) Doyle spiral: the hexagonal packing of the punctured plane that is the discrete exponential.
Every coin sits at a^m b^n with radius k|a^m b^n|; the p arms are the images of the straight rows
m = const under exp, i.e. exact logarithmic spirals — here the translation loses nothing.
Pigment: arm index (mod p) cycles the box; lightness: generation n; coral: ONE arm's exact spiral.
"""
import numpy as np, json, sys, time
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import pastel as P
from doyle import solve, circles, certify

INK = P.PIG['ink']


def render(p=9, q=4, S=2560, SS=2, out='doyle_2560.png', seed=8):
    t0 = time.time()
    sol = solve(p, q)
    cert = certify(sol)
    a, b, k = sol['a'], sol['b'], sol['k']
    Wd, Hd = S * SS, S * SS
    sh = P.Sheet(Wd, Hd, seed=seed)
    cx, cy = 0.5 * Wd, 0.45 * Hd
    Rmax = 0.56 * Wd                     # px for |z| = 1
    rmin = 0.0035
    z, R, M, N = circles(sol, rmin, 1.6, 90)
    rng = np.random.default_rng(seed)
    # which "arm" does a coin belong to: the lattice line through it in the direction with a^p b^q = 1
    # arms are indexed by the residue of a lattice coordinate transverse to the closure vector (p,q):
    # use the integer (q*m - p*n) which is invariant under (m,n) -> (m,n)+(p,q)?  no: we want lines
    # m = const modulo the closure: class = m mod p  (b^n moves along the arm when a^p b^q = 1 => a^p = b^-q)
    arm = np.mod(M, p)
    gen = N + M * (q / p)                # position along the spiral (continuous)
    # pixel coords
    X = cx + Rmax * z.real; Y = cy - Rmax * z.imag
    Rp = R * Rmax
    # tints: arm -> pigment (p arms over the 10-cycle), radius -> density (outer coins pale, inner dense)
    absorb = np.zeros((len(z), 3), np.float32)
    rr = np.abs(z)
    dens = 0.55 + 0.75 * (1 - np.clip((np.log(rr) - np.log(rmin)) / (np.log(1.6) - np.log(rmin)), 0, 1)) ** 1.3
    # painter's unfinished edge: beyond |z| ~ 0.72 coins drop out along an irregular front
    front = 0.72 + 0.10 * np.cos(3 * np.angle(z) + 0.7) + 0.05 * np.sin(7 * np.angle(z))
    keep_p = np.clip(1 - (rr - front) / 0.22, 0, 1)
    keep = rng.random(len(z)) < keep_p
    dens = dens * np.where(rr > front, np.clip(1 - (rr - front) / 0.35, 0.25, 1), 1.0)
    for i in range(len(z)):
        hue = (arm[i] / p + 0.03 * np.log(rr[i])) % 1.0
        i0, i1, t = P.hue_to_pigments(np.array([hue]))
        tint = P.mix_tint(P.CYCLE[int(i0[0])], P.CYCLE[int(i1[0])], float(t[0]))
        absorb[i] = dens[i] * P.absorb(tint)
    chans = [Image.new('F', (Wd, Hd), 0.0) for _ in range(3)]
    drs = [ImageDraw.Draw(im) for im in chans]
    ink = Image.new('F', (Wd, Hd), 0.0); dink = ImageDraw.Draw(ink)
    gap = 0.045
    for i in np.argsort(-Rp):
        r = Rp[i]
        if not keep[i] or r < 0.4 or X[i] < -r or X[i] > Wd + r or Y[i] < -r or Y[i] > Hd + r:
            continue
        rf = r * (1 - gap)
        for c in range(3):
            drs[c].ellipse([X[i] - rf, Y[i] - rf, X[i] + rf, Y[i] + rf], fill=float(absorb[i, c]))
        if r > 1.4 * SS:
            wl = max(1.0, 0.028 * r + 0.3 * SS)
            dink.ellipse([X[i] - r, Y[i] - r, X[i] + r, Y[i] + r], outline=1.0, width=int(round(wl)))
    A = np.stack([np.asarray(im, np.float32) for im in chans], axis=-1); del chans
    g = P.noise(Hd, Wd, 1.6, seed + 11)
    A *= (1 + 0.15 * g)[..., None]
    tot = A.sum(-1); bb = gaussian_filter(tot, 1.2 * SS)
    gy, gx = np.gradient(bb); edge = np.hypot(gx, gy)
    nz = edge[edge > 0]
    if nz.size:
        edge /= (np.percentile(nz, 99) + 1e-9)
    A *= (1 + 0.30 * np.clip(edge, 0, 1))[..., None]
    A = gaussian_filter(A, [0.5 * SS, 0.5 * SS, 0])
    sh.A += A; del A
    sh.wash(gaussian_filter(np.asarray(ink, np.float32), 0.45 * SS) * 0.8, INK)
    # coral: the exact logarithmic spiral of arm 0 — centres a^m b^n with m = 0 mod p... the arm through
    # coin (0,0) in the b-direction: z(t) = b^t, t real (exact log-spiral); also the a-direction arm is a spiral
    sp = Image.new('F', (Wd, Hd), 0.0); ds = ImageDraw.Draw(sp)
    lb = np.log(b); la = np.log(a)
    for (lg, name, wmul) in ((lb, 'b', 1.0),):
        tmax = (np.log(0.82)) / lg.real if lg.real > 0 else (np.log(rmin)) / lg.real
        tmin = (np.log(rmin)) / lg.real if lg.real > 0 else (np.log(0.82)) / lg.real
        ts = np.linspace(min(tmin, tmax), max(tmin, tmax), 4000)
        zz = np.exp(ts * lg)
        xx = cx + Rmax * zz.real; yy = cy - Rmax * zz.imag
        ds.line(list(zip(xx.tolist(), yy.tolist())), fill=1.0, width=int(round(2.6 * SS * wmul)), joint='curve')
    sh.wash(gaussian_filter(np.asarray(sp, np.float32), 0.8 * SS) * 2.2, "coral")
    # caption
    sh.caption_strip(0.905, 0.99, 0.55)
    items = [("Nothing Lost in the Spiral", 0.5 * Wd, 0.925 * Hd, int(0.032 * Wd), 'serif_bold', 'mm'),
             (f"A Doyle spiral of type ({p},{q}): every coin sits at aᵐbⁿ with radius {k:.4f}·|aᵐbⁿ| and touches six others",
              0.5 * Wd, 0.955 * Hd, int(0.0115 * Wd), 'italic', 'mm'),
             (f"({cert['n_circles']} coins checked pairwise, no overlaps). The coral line is the exact spiral bᵗ: the exponential translates a row into a spiral and loses nothing.",
              0.5 * Wd, 0.975 * Hd, int(0.0115 * Wd), 'italic', 'mm')]
    sh.wash(P.text_density(Wd, Hd, items) * 1.1, INK)
    img = sh.develop()
    P.finish(img, (S, S), out)
    cert.update(p=p, q=q, coins_drawn=int(len(z)))
    json.dump(cert, open(out.replace('.png', '_cert.json'), 'w'), indent=1)
    print(f'render {out} coins={len(z)} {time.time()-t0:.0f}s', flush=True)
    return cert


if __name__ == '__main__':
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    q = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    S = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
    out = sys.argv[4] if len(sys.argv) > 4 else f'proto_doyle_{p}_{q}_{S}.png'
    print(render(p, q, S=S, out=out))
