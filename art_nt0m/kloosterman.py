"""Kloosterman paths — the freedom of the middle of the sum.

For prime p and each a in (Z/p)*, the path t -> (1/sqrt p) sum_{x=1}^{t} e((a x + xbar)/p)
wanders the plane like a random walk, yet is totally determined; its endpoint is
forced onto the real axis inside Weil's bound [-2,2] (after /sqrt p).
Each thread is colored by its DESTINY, the angle theta(a) = arccos(S/2sqrt p):
gold = S near +2sqrt p, ice = near -2sqrt p, violet/indigo = the sin^2 crowd.
The endpoints are splatted as pegs on the real axis: the law-bar all freedom obeys.

Usage: python3 kloosterman.py <p> <size> <outname>
"""
import sys
import numpy as np
from scipy.ndimage import gaussian_filter
from common import splat_rgb, filmic, bloom, save, lerp_palette

STOPS = [
    (0.00, (1.00, 0.84, 0.40)),   # theta ~ 0 : gold blaze
    (0.20, (0.82, 0.50, 0.26)),   # amber
    (0.42, (0.45, 0.25, 0.66)),   # violet crowd
    (0.58, (0.20, 0.30, 0.78)),   # indigo crowd
    (0.80, (0.22, 0.56, 0.64)),   # teal
    (1.00, (0.58, 0.90, 1.00)),   # theta ~ pi : ice
]


def render(p=4093, S=1280, out=None):
    H = W = S
    acc = np.zeros((H, W, 3), dtype=np.float32)
    pegs = np.zeros((H, W, 3), dtype=np.float32)

    R = 2.45
    cx, cy = 0.0, 0.0
    scale = S / (2 * R)
    mass = 80.0 * S / 1280.0

    inv = np.array([pow(x, p - 2, p) for x in range(1, p)], dtype=np.int64)
    xg = np.arange(1, p, dtype=np.int64)
    a_all = np.arange(1, p, dtype=np.int64)

    # ---- pass 0: endpoints for every a (cheap: full sums via one pass) ----
    ends = np.empty(p - 1)
    for i in range(0, p - 1, 512):
        a = a_all[i:i + 512][:, None]
        ph = (a * xg[None, :] + inv[None, :]) % p
        ends[i:i + 512] = np.exp((2j * np.pi / p) * ph).sum(axis=1).real
    ends /= np.sqrt(p)
    theta_all = np.arccos(np.clip(ends / 2.0, -1, 1))
    heroes_gold = a_all[np.argsort(theta_all)[:5]]
    heroes_ice = a_all[np.argsort(theta_all)[-5:]]
    hero_set = set(heroes_gold.tolist()) | set(heroes_ice.tolist())
    print("Weil max |S|/2sqrt(p) =", np.abs(ends).max() / 2.0)
    print("gold heroes a =", heroes_gold, " thetas:", theta_all[heroes_gold - 1])
    print("ice  heroes a =", heroes_ice, " thetas:", theta_all[heroes_ice - 1])

    step_px = scale / np.sqrt(p)
    m = max(2, int(np.ceil(step_px * 1.6)))
    T = p - 1
    f = ((np.arange(m) + 0.5) / m).astype(np.float32)
    tramp = (0.33 + 1.05 * (np.arange(T, dtype=np.float32) + 1) / T)  # time-ramp

    for i in range(0, p - 1, 256):
        a = a_all[i:i + 256][:, None]
        ph = (a * xg[None, :] + inv[None, :]) % p
        Pv = np.cumsum(np.exp((2j * np.pi / p) * ph), axis=1) / np.sqrt(p)
        n_a = Pv.shape[0]
        th = theta_all[i:i + 256][:n_a]
        col = lerp_palette((th / np.pi).astype(np.float32), STOPS)

        V = np.concatenate([np.zeros((n_a, 1), dtype=Pv.dtype), Pv], axis=1)
        A, B = V[:, :-1], V[:, 1:]
        Z = A[:, :, None] + (B - A)[:, :, None] * f[None, None, :]
        xs = ((Z.real - (cx - R)) * scale).astype(np.float32).ravel()
        ys = ((Z.imag - (cy - R)) * scale).astype(np.float32).ravel()
        wt = (tramp[None, :, None] * np.ones((n_a, 1, m), np.float32)).reshape(n_a, -1)
        w = (col[:, None, :] * wt[:, :, None]).reshape(-1, 3) * (mass / (T * m))
        splat_rgb(acc, xs, ys, w.astype(np.float32), W, H)

        # endpoint pegs (in path color, whitened)
        ex = ((Pv[:, -1].real - (cx - R)) * scale).astype(np.float32)
        ey = ((Pv[:, -1].imag - (cy - R)) * scale).astype(np.float32)
        pw = (0.6 * col + 0.4) * (0.42 * S / 1280.0)
        splat_rgb(pegs, ex, ey, pw.astype(np.float32), W, H)
        if (i // 256) % 4 == 0:
            print("fog chunk", i, flush=True)

    # ---- hero threads: extremal destinies, crisp and bright ----
    mh = m * 3
    fh = ((np.arange(mh) + 0.5) / mh).astype(np.float32)
    for a_hero in sorted(hero_set):
        ph = (a_hero * xg + inv) % p
        Pv = np.cumsum(np.exp((2j * np.pi / p) * ph)) / np.sqrt(p)
        th = theta_all[a_hero - 1]
        col = lerp_palette(np.array([th / np.pi], dtype=np.float32), STOPS)[0]
        col = 0.75 * col + 0.25  # whiten a touch
        V = np.concatenate([[0], Pv])
        A, B = V[:-1], V[1:]
        Z = (A[:, None] + (B - A)[:, None] * fh[None, :]).ravel()
        xs = ((Z.real - (cx - R)) * scale).astype(np.float32)
        ys = ((Z.imag - (cy - R)) * scale).astype(np.float32)
        w = np.tile(col.astype(np.float32), (xs.size, 1)) * (mass * 26.0 / (T * mh))
        splat_rgb(acc, xs, ys, w, W, H)
        # blazing endpoint peg for the hero (near-Weil landings touch the wall)
        epx = np.full(9, (Pv[-1].real - (cx - R)) * scale, dtype=np.float32)
        epy = np.full(9, (Pv[-1].imag - (cy - R)) * scale, dtype=np.float32)
        rng_ = np.random.default_rng(int(a_hero))
        epx += rng_.normal(0, 0.7 * S / 1280.0, 9).astype(np.float32)
        epy += rng_.normal(0, 0.7 * S / 1280.0, 9).astype(np.float32)
        epw = np.tile((0.55 * col + 0.45).astype(np.float32), (9, 1)) * (0.55 * S / 1280.0 / 9)
        splat_rgb(acc, epx, epy, epw, W, H)

    # law-bar glow: blur pegs slightly, add
    for c in range(3):
        pegs[..., c] = gaussian_filter(pegs[..., c], 1.0 * S / 1280.0)
    acc += pegs

    img = filmic(acc, k=0.92, gamma=0.85)
    img = bloom(img, thresh=0.62)
    save(img, out or ("variants/kloo_eye_%d_%d.png" % (p, S)))


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 4093
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 1280
    out = sys.argv[3] if len(sys.argv) > 3 else None
    render(p, S, out)
