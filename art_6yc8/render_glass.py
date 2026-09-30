"""render_glass.py — m cylinders of sorbet glass touching a pearl ball (MO 156008).

Each ray collects the chord length through every (infinite) glass cylinder up to the ball;
transmission = exp(-sum absorbance_j * length_j * fade), where fade dissolves the bars into
the paper far from the ball.  The ball is opaque pearl, lit by a soft key light whose shadow
rays pass through the same glass (tinted shadows), plus sky ambient with occlusion by glass
thickness.  Glass edges get a thin fresnel line; contact points a coral glint.
usage: render_glass.py config size out.png [cam_x cam_y cam_z] [--dark]
"""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from render_cyl import load, contacts, normalize

# glass absorbance per unit length (per channel) — sorbet hues
def absorb(t):
    return -np.log(np.array(t, np.float32))
_G0 = [absorb(c) for c in [(1.00, 0.55, 0.66), (1.00, 0.86, 0.45), (0.55, 0.92, 0.72),
                             (0.55, 0.78, 1.00), (0.78, 0.62, 1.00), (1.00, 0.68, 0.50),
                             (1.00, 0.62, 0.90)]]
_ORD = [int(v) for v in next((a[4:] for a in sys.argv if a.startswith('ord=')), '0,1,2,3,4,5,6').split(',')]
GLASS = [_G0[i] for i in _ORD]

FROST = float(next((a[6:] for a in sys.argv if a.startswith('frost=')), 0.28))
KEY = None
DARK = '--dark' in sys.argv
INDIGO = np.array([0.030, 0.028, 0.075], np.float32)
SHEEN = float(next((a[6:] for a in sys.argv if a.startswith('sheen=')), 1.0))
BACK = float(next((a[5:] for a in sys.argv if a.startswith('back=')), 7.0))
WALL = float(next((a[5:] for a in sys.argv if a.startswith('wall=')), 1.0))
KL = [float(v) for v in next((a[3:] for a in sys.argv if a.startswith('kl=')), '0.6,-0.5,0.2').split(',')]

def cyl_interval(o, d, P, u, r):
    w = o - P
    du = d @ u if d.ndim == 1 else np.einsum('...i,i', d, u)
    wu = np.einsum('...i,i', w, u)
    a = np.maximum(1 - du * du, 1e-12)
    b = np.einsum('...i,...i', w, d) - wu * du
    c = np.einsum('...i,...i', w, w) - wu * wu - r * r
    disc = b * b - a * c
    sq = np.sqrt(np.maximum(disc, 0))
    t0 = (-b - sq) / a; t1 = (-b + sq) / a
    ok = disc > 0
    return np.where(ok, t0, np.inf), np.where(ok, t1, -np.inf)

def sphere_t(o, d):
    b = np.einsum('...i,...i', o, d); c = np.einsum('...i,...i', o, o) - 1
    disc = b * b - c
    t = -b - np.sqrt(np.maximum(disc, 0))
    return np.where((disc > 0) & (t > 1e-4), t, np.inf)

def glass_path(o, d, tstop, P, U, r, fadeL, dens, H=None):
    """returns (..., 3) absorbance and (...,) edge weight [and specular sheen if H given]"""
    A = np.zeros(o.shape, np.float32); edge = np.zeros(o.shape[:-1], np.float32)
    sheen = np.zeros(o.shape[:-1], np.float32)
    frost = np.zeros(o.shape, np.float32); fa = np.zeros(o.shape[:-1], np.float32)
    emit = np.zeros(o.shape, np.float32)
    for j in range(len(P)):
        t0, t1 = cyl_interval(o, d, P[j], U[j], r)
        t0c = np.maximum(t0, 0); t1c = np.minimum(t1, tstop)
        L = np.clip(t1c - t0c, 0, None)
        tm = np.where(L > 0, (t0c + t1c) / 2, 0.0)
        mid = o + d * tm[..., None]
        fade = np.exp(-(np.einsum('...i,...i', mid, mid) / fadeL ** 2))
        A += (dens * L * fade)[..., None] * GLASS[j % len(GLASS)]
        emit += (dens * L * fade)[..., None] * np.exp(-GLASS[j % len(GLASS)] * 1.6)
        # silhouette: chord short relative to diameter => near the glass edge
        full = np.where(np.isfinite(t0), np.clip(t1 - t0, 0, None), 0.0)
        e = np.exp(-(full / (0.16 * r)) ** 2) * (full > 0) * fade
        edge += e
        if H is not None:
            front = np.isfinite(t0) & (t0 > 0) & (t0 < tstop)
            pe = o + d * np.where(front, t0, 0)[..., None] - P[j]
            nrm = pe - np.einsum('...i,i', pe, U[j])[..., None] * U[j]
            nrm = nrm / (np.linalg.norm(nrm, axis=-1, keepdims=True) + 1e-9)
            cs = np.clip(np.einsum('...i,...i', nrm, H), 0, 1)
            fr = (1 - np.clip(-np.einsum('...i,...i', nrm, d), 0, 1)) ** 4
            sheen += front * fade * SHEEN * (0.55 * cs ** 90 + 0.10 * cs ** 8 + 0.30 * fr)
            lam = np.clip(np.einsum('...i,...i', nrm, KEY), 0, 1)
            a = FROST * front * fade
            tint = np.exp(-GLASS[j % len(GLASS)] * 1.25)
            frost += a[..., None] * tint * (0.62 + 0.45 * lam[..., None])
            fa += a
    if H is not None:
        fa = np.clip(fa, 0, 0.9)
        return A, edge, sheen, frost, fa, emit
    return A, edge

def main():
    cfg, S, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    cam = np.array([float(x) for x in sys.argv[4:7]]) if len(sys.argv) > 6 else np.array([1.0, 0.8, 0.62])
    P, U, r = load(cfg)
    rng = np.random.default_rng(1)
    f = normalize(cam); dist = float(next((a[5:] for a in sys.argv if a.startswith("dist=")), 26.0)); eye = f * dist; fwd = -f
    up = np.array([0, 0, 1.0])
    right = normalize(np.cross(fwd, up)); upv = np.cross(right, fwd)
    fov = float(dict(a.split('=') for a in sys.argv if a.startswith('fov=')).get('fov=', 0.30)) if False else 0.17
    for a in sys.argv:
        if a.startswith('fov='): fov = float(a[4:])
    key = normalize(np.array([-0.3, 0.2, 1.0]) + 0.5 * f)
    if '--camkey' in sys.argv:
        key = normalize(0.55 * upv - 0.35 * right + 0.75 * f)
    global KEY
    KEY = key
    key2 = normalize(key + np.array(KL))
    paper = np.array([0.994, 0.988, 0.978], np.float32)
    dens, fadeL = float(next((a[5:] for a in sys.argv if a.startswith('dens=')), 0.34)), float(next((a[6:] for a in sys.argv if a.startswith('fadeL=')), 7.5))
    img = np.zeros((S, S, 3), np.float32)
    SS = int(next((a[3:] for a in sys.argv if a.startswith('ss=')), 2))
    ys = np.arange(S)
    for y0 in range(0, S, 96):
        acc = np.zeros((min(96, S - y0), S, 3), np.float32)
        for sy in range(SS):
            for sx in range(SS):
                yy, xx = np.meshgrid(ys[y0:y0 + 96], ys, indexing='ij')
                jx = (sx + rng.random(yy.shape)) / SS; jy = (sy + rng.random(yy.shape)) / SS
                u = (xx + jx) / S * 2 - 1; v = 1 - (yy + jy) / S * 2
                d = normalize(fwd + fov * (u[..., None] * right + v[..., None] * upv))
                o = np.broadcast_to(eye, d.shape)
                tb = sphere_t(o, d)
                hitb = np.isfinite(tb)
                X = o + d * np.where(hitb, tb, 0)[..., None]
                N = normalize(X + 1e-9)
                # ball shading
                base = X + N * 1e-3
                lamsum = np.zeros(tb.shape + (3,), np.float32)
                for s_ in range(4):
                    L = normalize(key + 0.08 * rng.standard_normal(tb.shape + (3,)))
                    lam = np.clip(np.einsum('...i,...i', N, L), 0, 1)
                    Ash, _ = glass_path(base, L, np.full(tb.shape, np.inf), P, U, r, fadeL, dens * 1.6)
                    lamsum += lam[..., None] * np.exp(-Ash)
                lamsum /= 4
                # ambient: sky from above through glass (a few samples)
                amb = np.zeros(tb.shape + (3,), np.float32)
                tmp = np.where(np.abs(N[..., :1]) < 0.9, np.array([1.0, 0, 0]), np.array([0, 1.0, 0]))
                e1 = normalize(np.cross(N, tmp)); e2 = np.cross(N, e1)
                na = 6
                for s_ in range(na):
                    u1 = (s_ + rng.random(tb.shape)) / na; ph = 2 * np.pi * rng.random(tb.shape)
                    D = (np.sqrt(u1) * np.cos(ph))[..., None] * e1 + (np.sqrt(u1) * np.sin(ph))[..., None] * e2 + np.sqrt(1 - u1)[..., None] * N
                    Aa, _ = glass_path(base, D, np.full(tb.shape, np.inf), P, U, r, fadeL, dens * 1.2)
                    amb += np.exp(-Aa) * (0.75 + 0.25 * D[..., 2:3])
                amb /= na
                pearl = np.array([0.985, 0.965, 0.955], np.float32)
                H = normalize(key + f)
                spec = np.clip(np.einsum('...i,i', N, H), 0, 1) ** 60
                ballc = pearl * ((0.18 if DARK else 0.50) * amb + 0.62 * lamsum) + 0.22 * spec[..., None] * lamsum
                # pearl iridescence: faint hue by view angle
                ca = np.clip(np.einsum('...i,...i', N, -d), 0, 1)
                irid = 0.035 * np.stack([np.cos(6 * ca), np.cos(6 * ca + 2.1), np.cos(6 * ca + 4.2)], -1)
                ballc = ballc + irid * (1 - ca)[..., None]
                # backdrop plane (X . f = -BACK) catching tinted glass shadows and the ball's shadow
                den = np.einsum('...i,i', d, f)
                tp = (-BACK - np.einsum('...i,i', o, f)) / np.where(np.abs(den) > 1e-9, den, -1e-9)
                Xp = o + d * tp[..., None]
                shp = np.zeros(tb.shape + (3,), np.float32)
                for s_ in range(3):
                    Ls = normalize(key2 + 0.035 * rng.standard_normal(tb.shape + (3,)))
                    Ap, _ = glass_path(Xp, Ls, np.full(tb.shape, np.inf), P, U, r, fadeL * 1.25, dens * 1.35)
                    blk = np.isfinite(sphere_t(Xp, Ls))
                    shp += np.exp(-Ap) * np.where(blk, 0.80, 1.0)[..., None]
                shp /= 3
                wall = paper * (0.55 + 0.45 * shp)
                if DARK:
                    wall = INDIGO * (0.75 + 0.5 * shp) * (1 + 0.25 * (u[..., None] * 0 + v[..., None]))
                wall = paper * (1 - WALL) + wall * WALL
                behind = np.where(hitb[..., None], ballc, wall)
                A, edge, sh, fr_, fa_, em_ = glass_path(o, d, np.where(hitb, tb, np.inf), P, U, r, fadeL, dens, H)
                if DARK:
                    col = behind * np.exp(-0.5 * A) + 0.55 * (1 - np.exp(-1.1 * em_))
                else:
                    col = behind * np.exp(-A)
                wsum = np.maximum(fa_ / np.maximum(np.clip(fa_, 1e-6, None), 1e-6), 1)
                col = col * (1 - fa_[..., None]) + fr_ * (fa_ / np.maximum(fa_ + 1e-9, np.clip(fa_, 0, 0.9) + 1e-9))[..., None] * np.minimum(1, 0.9 / np.maximum(fa_, 1e-9))[..., None]
                col = col * (1 - 0.22 * np.clip(edge, 0, 1)[..., None])
                col = col + (1 - col) * np.clip(sh, 0, 1)[..., None]
                acc += col
        img[y0:y0 + 96] = acc / (SS * SS)
        print('row', y0, flush=True)
    # coral glints at the contacts
    C = contacts(P, U, r)
    glow = np.zeros((S, S), np.float32)
    for c in C:
        v = c - eye; z = v @ fwd; px = (v @ right) / (z * fov); py = (v @ upv) / (z * fov)
        X, Y = (px + 1) / 2 * S, (1 - py) / 2 * S
        dv = v / np.linalg.norm(v); bq = eye @ dv; disc = bq * bq - (eye @ eye - 1)
        if disc > 0 and (-bq - np.sqrt(disc)) < np.linalg.norm(v) - 1e-3:
            continue                                   # hidden behind the opaque ball
        if 0 <= X < S and 0 <= Y < S:
            glow[int(Y), int(X)] += 1
    sg = S / 700
    glow = np.clip(gaussian_filter(glow, sg) * 2 * np.pi * sg * sg, 0, 1)
    coral = np.array([1.0, 0.42, 0.36], np.float32)
    img = img * (1 - 0.8 * glow[..., None]) + coral * 0.8 * glow[..., None]
    lin = np.clip(img, 0, 1)
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    srgb = srgb * 255 + np.random.default_rng(9).uniform(-0.5, 0.5, srgb.shape)
    Image.fromarray(np.clip(srgb + 0.5, 0, 255).astype(np.uint8)).save(out)
    print('contacts', len(C), 'r', r)

if __name__ == '__main__':
    main()
