"""02 - Everything Comes Home: the Collatz coral.

The Collatz map T(n)=n/2 (even), 3n+1 (odd) is conjectured to send EVERY
positive integer to 1. We grow the conjecture in reverse: for each n we take
its forward orbit n -> ... -> 1, reverse it so it starts at the common root 1,
and walk it as a path that bends one way on an even number and the other way
on an odd number. Shared orbit-tails (everyone passes through ...->4->2->1)
overlap into a bright trunk; the divergent histories fan out as branches.
A river drawn from its mouth: every drop, conjecturally, came home.
"""
import numpy as np
import artkit as ak


def collatz_seq(n):
    s = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        s.append(n)
    return s


def _densify(a, K):
    """linearly interpolate K-1 points between each consecutive pair."""
    if K <= 1 or len(a) < 2:
        return a
    t = np.linspace(0, 1, K, endpoint=False)
    seg = a[:-1, None] + (a[1:, None] - a[:-1, None]) * t[None, :]
    return np.append(seg.ravel(), a[-1])


def build(M=60000, da_even=0.10, da_odd=-0.28, L=1.0, subsamp=3):
    """Walk every reversed orbit for n in 2..M. Returns (x,y,depth) arrays
    of all step vertices (concatenated), densified within each path."""
    xs, ys, deps = [], [], []
    for n in range(2, M + 1):
        seq = collatz_seq(n)
        seq.reverse()                       # now starts at 1
        ang = np.pi / 2                      # grow upward
        x = 0.0; y = 0.0
        m = len(seq)
        px = np.empty(m); py = np.empty(m)
        for i, v in enumerate(seq):
            px[i] = x; py[i] = y
            ang += da_even if (v % 2 == 0) else da_odd
            x += L * np.cos(ang); y += L * np.sin(ang)
        dd = np.arange(m, dtype=np.float32)
        xs.append(_densify(px, subsamp))
        ys.append(_densify(py, subsamp))
        deps.append(_densify(dd, subsamp))
    return (np.concatenate(xs), np.concatenate(ys), np.concatenate(deps))


def cyclic(stops, n=1024):
    cols = np.array([[int(s[i:i+2], 16) / 255 for i in (0, 2, 4)] for s in stops])
    t = np.linspace(0, 1, len(cols)); tt = np.linspace(0, 1, n)
    return np.stack([np.interp(tt, t, cols[:, c]) for c in range(3)], 1)


def render(M=60000, S=2048, da_even=0.10, da_odd=-0.28, L=1.0, fname="proto_collatz.png",
           expo_k=1.4, sat=1.25, gamma=1/2.0, bloom_amp=1.0, weight=0.06,
           rot_deg=0.0, subsamp=3):
    x, y, dep = build(M, da_even, da_odd, L, subsamp)
    # rotate whole thing for composition
    if rot_deg:
        a = np.radians(rot_deg)
        x, y = x*np.cos(a) - y*np.sin(a), x*np.sin(a) + y*np.cos(a)
    # fit to canvas with margin
    pad = 0.06
    x0, x1 = x.min(), x.max(); y0, y1 = y.min(), y.max()
    w = x1 - x0; h = y1 - y0
    scale = (S * (1 - 2 * pad)) / max(w, h)
    px = (x - x0) * scale + (S - (w) * scale) / 2
    py = (y - y0) * scale + (S - (h) * scale) / 2
    py = S - 1 - py                          # flip so it grows up
    ix = np.round(px).astype(np.int32); iy = np.round(py).astype(np.int32)
    ok = (ix >= 0) & (ix < S) & (iy >= 0) & (iy < S)
    ix, iy = ix[ok], iy[ok]
    depth = dep[ok].astype(np.float32)

    # colour by depth from root (home warm -> far tips cool)
    pal = cyclic(["fff0c0", "ffd24a", "ff7a3c", "ef4d6b", "b148d8",
                  "5a6cf0", "23a6c8", "1b2a6b"])
    dn = depth / (depth.max() + 1e-9)
    col = pal[np.clip((dn * 1023).astype(int), 0, 1023)]

    canvas = np.zeros((S, S, 3), np.float32)
    np.add.at(canvas, (iy, ix), col * weight)
    canvas = ak.bloom(canvas, sigmas=(1.5, 5, 14),
                      amps=(0.16*bloom_amp, 0.10*bloom_amp, 0.06*bloom_amp))
    rgb = ak.filmic(canvas, k=expo_k)
    luma = (0.2126*rgb[..., 0]+0.7152*rgb[..., 1]+0.0722*rgb[..., 2])[..., None]
    rgb = np.clip(luma + (rgb - luma) * sat, 0, 1)
    rgb = ak.gamma(rgb, gamma)
    ak.save(rgb, fname)
    print("wrote", fname, "verts", len(ix))


if __name__ == "__main__":
    render(M=20000, S=1200, fname="proto_collatz.png")
