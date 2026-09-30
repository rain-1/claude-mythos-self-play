"""render_cyl.py — six unit cylinders touching a unit ball (MO 156008), ray-traced in sorbet.

Analytic ray/sphere and ray/infinite-cylinder intersections; soft key light (jittered shadow
rays), hemisphere ambient occlusion, a faint pastel bounce, depth fog into luminous paper so
the infinite cylinders dissolve.  Contact points (ball-cylinder, cylinder-cylinder) get a
coral glint: they are the whole problem.
usage: render_cyl.py config size out.png [ao_samples]
"""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

def normalize(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)

def burr():
    P = [(0, 0, 2), (0, 0, -2), (2, 0, 0), (-2, 0, 0), (0, 2, 0), (0, -2, 0)]
    U = [(1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1)]
    return np.array(P, float), np.array(U, float), 1.0

def load(name):
    if name == 'burr':
        return burr()
    import cylopt
    x = np.load(name); m = (len(x) - 1) // 4
    P, U, r = cylopt.axes(x, m)
    s = 1.0   # keep the ball unit, cylinders radius r
    return P, U, r

# sorbet albedos (linear-ish rgb)
ALB = [(1.00, 0.62, 0.70), (1.00, 0.78, 0.62), (1.00, 0.92, 0.60), (0.70, 0.93, 0.78),
       (0.64, 0.84, 1.00), (0.80, 0.72, 1.00), (1.00, 0.70, 0.90)]
BALL = (0.99, 0.97, 0.96)

def hit_sphere(o, d, R=1.0):
    b = np.einsum('...i,...i', o, d); c = np.einsum('...i,...i', o, o) - R * R
    disc = b * b - c
    t = -b - np.sqrt(np.maximum(disc, 0))
    t2 = -b + np.sqrt(np.maximum(disc, 0))
    t = np.where(t > 1e-4, t, t2)
    return np.where((disc > 0) & (t > 1e-4), t, np.inf)

def hit_cyl(o, d, P, u, r):
    w = o - P
    du = np.einsum('...i,i', d, u); wu = np.einsum('...i,i', w, u)
    a = 1 - du * du
    b = np.einsum('...i,...i', w, d) - wu * du
    c = np.einsum('...i,...i', w, w) - wu * wu - r * r
    disc = b * b - a * c
    sq = np.sqrt(np.maximum(disc, 0))
    a = np.maximum(a, 1e-12)
    t = (-b - sq) / a; t2 = (-b + sq) / a
    t = np.where(t > 1e-4, t, t2)
    return np.where((disc > 0) & (t > 1e-4), t, np.inf)

def trace(o, d, P, U, r):
    T = [hit_sphere(o, d)] + [hit_cyl(o, d, P[j], U[j], r) for j in range(len(P))]
    T = np.stack(T, 0)
    idx = np.argmin(T, 0); t = np.min(T, 0)
    return t, idx

def occluded(o, d, P, U, r, tmax=np.inf):
    t, _ = trace(o, d, P, U, r)
    return t < tmax

def render(P, U, r, S, ao_n=16, cam_dir=(1.0, 1.0, 1.0), up=(0, 0, 1), fov=0.36, dist=24.0, roll=0.0, seed=0):
    rng = np.random.default_rng(seed)
    f = normalize(np.array(cam_dir, float)); eye = f * dist
    fwd = -f
    right = normalize(np.cross(fwd, np.array(up, float))); upv = np.cross(right, fwd)
    if roll:
        c, s = np.cos(roll), np.sin(roll); right, upv = c * right + s * upv, -s * right + c * upv
    key = normalize(np.array([0.35, -0.25, 1.0]) + 0.6 * f)       # light from above, camera side
    img = np.zeros((S, S, 3), np.float32); alpha = np.zeros((S, S), np.float32)
    depth = np.full((S, S), np.inf, np.float32); ident = np.full((S, S), -1, np.int16)
    ys = np.arange(S)
    for y0 in range(0, S, 128):
        yy, xx = np.meshgrid(ys[y0:y0 + 128], ys, indexing='ij')
        u = (xx + 0.5) / S * 2 - 1; v = 1 - (yy + 0.5) / S * 2
        d = normalize(fwd[None, None] + fov * (u[..., None] * right + v[..., None] * upv))
        o = np.broadcast_to(eye, d.shape).copy()
        t, idx = trace(o, d, P, U, r)
        hit = np.isfinite(t)
        X = o + d * np.where(hit, t, 0)[..., None]
        N = np.zeros_like(X)
        sb = idx == 0
        N[sb] = X[sb]
        for j in range(len(P)):
            m = idx == j + 1
            w = X[m] - P[j]; N[m] = w - (w @ U[j])[:, None] * U[j]
        N = normalize(N + 1e-12)
        # albedo
        A = np.zeros_like(X); A[sb] = BALL
        for j in range(len(P)):
            A[idx == j + 1] = ALB[j % len(ALB)]
        # soft key shadow (jittered light direction)
        base = X + N * 2e-3
        vis = np.zeros(t.shape, np.float32)
        ns = 6
        for s_ in range(ns):
            L = normalize(key[None, None] + 0.10 * rng.standard_normal(t.shape + (3,)))
            lam = np.clip(np.einsum('...i,...i', N, L), 0, 1)
            vis += lam * ~occluded(base, L, P, U, r)
        vis /= ns
        # ambient occlusion: cosine hemisphere samples, limited range
        ao = np.zeros(t.shape, np.float32)
        tmp = normalize(np.where(np.abs(N[..., :1]) < 0.9, np.array([1.0, 0, 0]), np.array([0, 1.0, 0])) - 0 * N)
        e1 = normalize(np.cross(N, tmp)); e2 = np.cross(N, e1)
        for s_ in range(ao_n):
            u1 = (s_ + rng.random(t.shape)) / ao_n; u2 = rng.random(t.shape)
            rr = np.sqrt(u1); ph = 2 * np.pi * u2
            rr, ph = rr[..., None], ph[..., None]
            D = rr * np.cos(ph) * e1 + rr * np.sin(ph) * e2 + np.sqrt(1 - u1)[..., None] * N
            tt, _ = trace(base, D, P, U, r)
            ao += np.clip(tt / 2.5, 0, 1)
        ao /= ao_n
        sky = 0.5 + 0.5 * N[..., 2]
        amb = (0.55 + 0.45 * sky)[..., None] * np.array([1.0, 0.99, 1.02]) * ao[..., None]
        col = A * (0.62 * amb + 0.58 * vis[..., None] * np.array([1.0, 0.985, 0.95]))
        # soft sheen
        H = normalize(key + f)
        spec = np.clip(np.einsum('...i,i', N, H), 0, 1) ** 40 * vis
        col = col + 0.18 * spec[..., None]
        # fresnel-ish rim toward paper white
        rim = (1 - np.clip(-np.einsum('...ij,...ij->...i', N, d), 0, 1)) ** 3
        col = col * (1 - 0.35 * rim[..., None]) + 0.35 * rim[..., None]
        img[y0:y0 + 128] = np.where(hit[..., None], col, 1.0)
        alpha[y0:y0 + 128] = hit
        depth[y0:y0 + 128] = np.where(hit, t, np.inf); ident[y0:y0 + 128] = np.where(hit, idx, -1)
        print('row', y0, flush=True)
    return img, alpha, depth, ident, (eye, fwd, right, upv, fov)

def contacts(P, U, r):
    pts = []
    for j in range(len(P)):                      # ball contact: foot of perpendicular from origin to axis
        w = -P[j]; foot = P[j] + (w @ U[j]) * U[j]
        pts.append(foot / np.linalg.norm(foot))
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            n = np.cross(U[i], U[j])
            if np.linalg.norm(n) < 1e-9: continue
            # closest points of the two axes
            w0 = P[i] - P[j]; a = U[i] @ U[i]; b = U[i] @ U[j]; c = U[j] @ U[j]; dd = U[i] @ w0; e = U[j] @ w0
            den = a * c - b * b; s = (b * e - c * dd) / den; t = (a * e - b * dd) / den
            p1 = P[i] + s * U[i]; p2 = P[j] + t * U[j]
            if np.linalg.norm(p1 - p2) < 2 * r + 1e-6:
                pts.append((p1 + p2) / 2)
    return np.array(pts)

if __name__ == '__main__':
    cfg, S, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    ao_n = int(sys.argv[4]) if len(sys.argv) > 4 else 16
    P, U, r = load(cfg)
    img, alpha, depth, ident, cam = render(P, U, r, S, ao_n)
    eye, fwd, right, upv, fov = cam
    # depth fog into paper: nearest geometry is ~dist-3; fade with distance from the ball
    fin = np.isfinite(depth)
    dn = np.where(fin, depth, 0)
    fog = np.clip((dn - (np.linalg.norm(eye) - 1.0)) / 14.0, 0, 1) ** 1.6
    paper = np.array([0.992, 0.985, 0.975], np.float32)
    img = np.where(fin[..., None], img * (1 - fog[..., None]) + paper * fog[..., None], paper)
    # coral glints at contacts that are visible
    C = contacts(P, U, r)
    glow = np.zeros((S, S), np.float32)
    for c in C:
        v = c - eye; z = v @ fwd; px = (v @ right) / (z * fov); py = (v @ upv) / (z * fov)
        X, Y = (px + 1) / 2 * S, (1 - py) / 2 * S
        ix, iy = int(X), int(Y)
        if 0 <= ix < S and 0 <= iy < S and depth[iy, ix] > z - 0.08:   # not hidden
            glow[iy, ix] += 1
    glow = gaussian_filter(glow, S / 900) * (2 * np.pi * (S / 900) ** 2)
    glow = np.clip(glow, 0, 1)
    coral = np.array([1.0, 0.45, 0.38], np.float32)
    img = img * (1 - 0.85 * glow[..., None]) + coral * 0.85 * glow[..., None]
    np.save(out.replace('.png', '_depth.npy'), np.stack([depth.astype(np.float32), ident.astype(np.float32)]))
    lin = np.clip(img, 0, 1)
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    Image.fromarray((srgb * 255 + 0.5).clip(0, 255).astype(np.uint8)).save(out)
    print('contacts', len(C))
