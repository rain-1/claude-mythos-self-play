"""render_honey.py — where to put the rocks (MO 499431).

Every split of N = 300 rocks into three piles is a point of the triangle.  Rounds remove one rock from a
uniformly random NON-EMPTY pile until one pile is left; colour = the expected size of that last pile (log
scale, honey at the minimum).  The minimum sits at the balanced split — the conjecture.  Plum threads are
single runs of the game (the fly's flights) from a ring of starting splits, ending on the three honey
spokes where only one pile remains.

usage: render_honey.py S out.png [key=val ...]
"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from fieldimg import field_grid, sample
sys.path.insert(0, '..')
from caption import caption, font

ARG = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))

STOPS = [(1.00, 0.84, 0.42), (1.00, 0.70, 0.50), (1.00, 0.56, 0.62), (0.98, 0.62, 0.84),
         (0.80, 0.64, 1.00), (0.62, 0.72, 1.00), (0.54, 0.86, 0.98), (0.56, 0.92, 0.78)]
def ramp(t):
    t = np.clip(t, 0, 1) * (len(STOPS) - 1); i = np.minimum(t.astype(int), len(STOPS) - 2); f = (t - i)[..., None]
    A = np.array(STOPS); return A[i] ** (1 - f) * A[i + 1] ** f


def main():
    S, out = int(sys.argv[1]), sys.argv[2]
    H = P('H', S)
    N = P('N', 300)
    G = field_grid(N)
    scale, cy = P('scale', 0.43), P('cy', 0.50)
    SSs = 2
    v, ins, abc = sample(G, N, S * SSs, scale=scale, cy=cy, order=1)
    # crop to H
    v = v[:H * SSs]; ins = ins[:H * SSs]
    lo, hi = np.log(G[N // 3, N // 3] if N % 3 == 0 else np.nanmin(G)), np.log(N)
    q = (np.log(np.maximum(v, 1e-9)) - lo) / (hi - lo)
    q = np.clip(q, 0, 1) ** P('gam', 0.55)
    nb = P('bands', 28)
    band = np.floor(q * nb) / nb
    frac = q * nb - np.floor(q * nb)
    col = ramp(band + 0.5 / nb)
    # alternate band strength (candy stripes) + soft relief from the continuous field
    stripe = np.where(np.floor(q * nb) % 2 == 0, 1.0, P('alt', 0.80))
    dens = P('dens', 0.85) * stripe
    gy, gx = np.gradient(gaussian_filter(q, 2.0))
    shade = np.clip(1 + P('relief', 900.0) * (gx * -0.6 + gy * -0.8) / (SSs * S / 1000), 0.75, 1.15)
    paper = np.array([0.993, 0.986, 0.978])
    ab = -np.log(col) * dens[..., None]
    rgb = paper * np.exp(-ab) * shade[..., None]
    # thin ink line on every band edge
    edge = np.minimum(frac, 1 - frac) * nb
    gq = np.hypot(*np.gradient(q)) * nb + 1e-9
    d_px = np.minimum(frac, 1 - frac) / gq
    line = np.exp(-(d_px / P('lw', 1.1)) ** 2) * P('ink', 0.18)
    rgb = rgb * (1 - line[..., None]) + np.array([0.36, 0.30, 0.40]) * line[..., None]
    # soft edge feather of the triangle
    from scipy.ndimage import distance_transform_edt
    dist = distance_transform_edt(ins)
    a = np.clip(dist / 2.0, 0, 1)[..., None]
    img = paper * (1 - a) + rgb * a
    # triangle drop shadow
    sh = gaussian_filter(ins.astype(float), 18 * SSs)
    sh = np.roll(np.roll(sh, int(14 * SSs), 0), int(10 * SSs), 1)
    img = np.where(ins[..., None], img, paper * (1 - 0.10 * sh[..., None]))
    im = Image.fromarray((np.clip(img, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8))
    dr = ImageDraw.Draw(im, 'RGBA')
    W2, H2 = im.size
    e = np.array([[np.cos(t), np.sin(t)] for t in np.pi / 2 + 2 * np.pi * np.arange(3) / 3])
    def topix(a, b, c):
        p = (a * e[0] + b * e[1] + c * e[2]) / N
        return ((p[0] * scale + 0.5) * S * SSs, (cy - p[1] * scale) * S * SSs)
    # honey spokes: final states (s,0,0)
    for i in range(3):
        t = [0, 0, 0]; t[i] = N
        x0, y0 = topix(0, 0, 0); x1, y1 = topix(*t)
        dr.line([(x0, y0), (x1, y1)], fill=(236, 176, 60, 120), width=int(5 * SSs * S / 2000))
    # fly flights
    rng = np.random.default_rng(P('seed', 5))
    nf = P('flies', 26)
    for k in range(nf):
        th = 2 * np.pi * (k + 0.5) / nf
        R = P('ring', 0.62)
        # start: point on a ring around the centre, converted to (a,b,c)
        pt = np.array([np.cos(th), np.sin(th)]) * R * 0.5
        M = np.array([[e[0, 0], e[1, 0], e[2, 0]], [e[0, 1], e[1, 1], e[2, 1]], [1, 1, 1]])
        abc = np.linalg.solve(M, np.array([pt[0] * N, pt[1] * N, N]))
        st = np.maximum(np.round(abc).astype(int), 1); st[np.argmax(st)] += N - st.sum()
        path = [tuple(st)]
        s = list(st)
        while sum(1 for x in s if x > 0) > 1:
            nz = [i for i in range(3) if s[i] > 0]; i = nz[rng.integers(len(nz))]; s[i] -= 1; path.append(tuple(s))
        pts = [topix(*p) for p in path]
        hue = np.array(ramp(np.array(k / nf * 0 + 0.75)))
        lw = int(P('flw', 2.2) * SSs * S / 2000)
        dr.line(pts, fill=(98, 80, 112, 150), width=max(1, lw), joint='curve')
        x, y = pts[0]; r = 7 * SSs * S / 2000
        dr.ellipse([x - r, y - r, x + r, y + r], fill=(98, 80, 112, 220))
        x, y = pts[-1]; r = 9 * SSs * S / 2000
        dr.ellipse([x - r, y - r, x + r, y + r], fill=(240, 110, 96, 235))
    im = im.resize((S, H), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32) / 255
    # honey pearl at the balanced split
    cxp, cyp = topix(N / 3, N / 3, N / 3); cxp /= SSs; cyp /= SSs
    r = P('pearl', 0.018) * S
    yy, xx = np.mgrid[0:H, 0:S].astype(np.float32)
    dx, dy = (xx - cxp) / r, (yy - cyp) / r; qq = dx * dx + dy * dy
    inside = np.clip((1 - np.sqrt(qq)) * r, 0, 1)[..., None]
    nz = np.sqrt(np.clip(1 - qq, 0, 1))
    L = np.array([-0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
    lam = np.clip(dx * L[0] + dy * L[1] + nz * L[2], 0, 1)
    Hh = (L + [0, 0, 1]) / np.linalg.norm(L + [0, 0, 1])
    sp = np.clip(dx * Hh[0] + dy * Hh[1] + nz * Hh[2], 0, 1) ** 80
    base = np.array([1.0, 0.76, 0.30])
    pc = base * (0.62 + 0.45 * lam[..., None]) + 0.6 * sp[..., None]
    shd = np.exp(-(((xx - cxp - 0.25 * r) ** 2 + (yy - cyp - 0.35 * r) ** 2) / (1.25 * r) ** 2) ** 2)[..., None]
    arr = arr * (1 - 0.22 * shd)
    arr = arr * (1 - inside) + np.clip(pc, 0, 1) * inside
    im = Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8))
    fs = int(S * 0.026)
    d = ImageDraw.Draw(im)
    # corner labels
    for i, lab in enumerate(['all rocks in pile A', 'all in pile B', 'all in pile C']):
        t = [0, 0, 0]; t[i] = N
        x, y = topix(*t); x /= SSs; y /= SSs
        f = font('i', int(fs * 0.5)); w = d.textlength(lab, font=f)
        off = -fs * 1.0 if i == 0 else fs * 0.45
        d.text((x - w / 2, y + off), lab, font=f, fill=(110, 95, 120))
    caption(im, int(S * 0.955), int(H * P('capy', 0.845)), P('title', 'Where the Fly Should Start'),
            [(f'every way to split {N} rocks into three piles; each round a random non-empty pile loses a rock, until one pile is left', 'i', 0.50),
             ('colour = expected size of the last pile (honey = smallest, at the balanced split) · plum threads = single games, ending on the honey spokes', 'r', 0.40),
             ('MathOverflow 499431 · balanced is optimal in every exact check: K = 3 to N = 500, K = 4 to 200, K = 5 to 60, K = 6 to 40', 'r', 0.40)],
            fs, align='right')
    im.save(out)


if __name__ == '__main__':
    main()
