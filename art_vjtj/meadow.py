"""The meadow: one blade of grass per n.  Arc length along the blade is log(1+k) (k = time in the
recurrence), the lean of the blade is the logarithm of the offset c_k = T(n,k) - k, so a blade
bends exactly where a gcd fires and by how much the offset grew.  Bead at each firing, seed head at
the tip = a(n).  silver: n prime (nothing ever fires, a(n)=n);  gold: a(n) prime and PROVED prime by
the window lemma;  green gold: prime, window too short to prove it;  cinnabar: composite."""
import sys, json, numpy as np
from math import gcd, log, sin, cos, pi
from sympy import isprime
from makie import *

def history(n):
    m = n + 1; T = 1; ev = []
    for k in range(0, n - 1):
        g = gcd(T, m * k + 1)
        if g > 1: ev.append((k, g, T - k))
        T += g
    c = T - (n - 1); a = m * c - 1
    last = ev[-1][0] if ev else -1
    W = n - 2 - last
    return dict(n=n, ev=ev, c=c, a=a, prime=isprime(a), cert=(W + 1) ** 2 > a, nprime=isprime(n))

def blade(h, N, Lmax, thmax, nseg=90):
    """returns arrays (dx, dy) relative to the root, per-vertex time s, and bead positions."""
    n = h['n']
    stot = log(n)
    s = np.linspace(0, stot, nseg)
    # lean target as a step function of s
    th = np.zeros(nseg)
    for (k, g, c) in h['ev']:
        cnew = c + g - 1
        th[s >= log(1 + k)] = thmax * min(1.0, log(cnew) / log(3.0 * N)) ** 0.8
    # smooth the kinks into bends
    sig = 0.22 / (s[1] - s[0])
    from scipy.ndimage import gaussian_filter1d
    th = gaussian_filter1d(th, sig, mode='nearest')
    scale = Lmax / log(N)
    ds = np.diff(s, prepend=0) * scale
    dx = np.cumsum(np.sin(th) * ds); dy = -np.cumsum(np.cos(th) * ds)
    beads = []
    for (k, g, c) in h['ev']:
        i = np.searchsorted(s, log(1 + k))
        i = min(i, nseg - 1)
        beads.append((dx[i], dy[i], g))
    return dx, dy, th, beads

def render(size=1024, N=640, out='meadow.png', seed=3, ss=2, title=True):
    u = size / 1024.0
    P = Panel(size, seed=seed, ss=ss)
    rng = np.random.default_rng(seed)
    x0, x1 = 0.05 * size, 0.75 * size
    yg = 0.835 * size
    Lmax = 0.57 * size
    H = [history(n) for n in range(2, N + 1)]
    xs = {h['n']: x0 + (x1 - x0) * (h['n'] - 2) / (N - 2) for h in H}
    sp = (x1 - x0) / (N - 2)
    PHI = 0.6180339887
    zs = {h['n']: (h['n'] * PHI) % 1.0 for h in H}          # depth in the meadow, 0 = front
    ygs = {n: yg - 0.055 * size * z for n, z in zs.items()}
    scl = {n: 1.0 - 0.22 * z for n, z in zs.items()}
    cls = lambda h: 'red' if not h['prime'] else ('gin' if h['nprime'] else ('kin' if h['cert'] else 'ao'))
    geo = {h['n']: blade(h, N, Lmax * scl[h['n']], 1.9) for h in H}

    # ---- moon (shell) ----
    mx, my, mr = 0.665 * size, 0.235 * size, 0.135 * size
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    rr = np.hypot(xx - mx, yy - my)
    moon = np.clip((mr - rr) / (1.2 * u) + 0.5, 0, 1)
    lit = 0.62 + 0.55 * np.clip(1 - np.hypot(xx - (mx - 0.45 * mr), yy - (my - 0.45 * mr)) / (1.9 * mr), 0, 1)
    P.raden(moon, cell=12 * u, sat=0.62, val=1.0, crack=0.5, shade=lit.astype(np.float32))
    ring = np.clip(1 - np.abs(rr - mr - 2.2 * u) / (1.3 * u), 0, 1)
    P.leaf(ring, KIN, height=1.2 * u, glow=0.2)
    # ---- mist bands (kasumi) of sprinkled gold ----
    def band(yc, xc, wx, wy, dens, metal):
        d = np.exp(-((yy - yc) / wy) ** 2) * (1 / (1 + np.exp(-(wx - np.abs(xx - xc)) / (0.05 * size))))
        # ragged ends
        P.dust(dens * d, metal, grain=0.42 * max(1, u ** 0.5), sparkle=0.05, gain=0.6)
    band(0.30 * size, 0.40 * size, 0.30 * size, 0.012 * size, 0.16, KIN)
    band(0.335 * size, 0.24 * size, 0.20 * size, 0.008 * size, 0.12, AOKIN)
    band(0.175 * size, 0.30 * size, 0.16 * size, 0.009 * size, 0.10, GIN)
    band(0.205 * size, 0.47 * size, 0.14 * size, 0.006 * size, 0.12, KIN)
    band(0.47 * size, 0.30 * size, 0.22 * size, 0.011 * size, 0.14, KIN)
    band(0.505 * size, 0.16 * size, 0.12 * size, 0.007 * size, 0.10, GIN)
    # ---- earth: nashiji, dense at the ground line ----
    earth = np.where(yy > yg, np.exp(-(yy - yg) / (0.05 * size)) * 0.30 + 0.02, 0.30 * np.clip(1 - (yg - yy) / (0.075 * size), 0, 1) ** 2)
    earth *= np.clip((0.93 * size - yy) / (0.02 * size), 0, 1)
    from scipy.ndimage import gaussian_filter
    und = gaussian_filter(rng.standard_normal((size, size)).astype(np.float32), (0.012 * size, 0.06 * size))
    und = und / und.std()
    P.dust(earth * np.clip(1 + 0.55 * und, 0.15, 2.2), KIN, grain=0.42 * max(1, u ** 0.5), sparkle=0.07, gain=0.6)
    P.dust(earth * 0.008 * (yy > yg - 0.02 * size), KIN, grain=1.0 * u ** 0.5, sparkle=0.4, gain=0.5)
    P.dust(earth * 0.003 * (yy > yg - 0.02 * size), GIN, grain=1.2 * u ** 0.5, sparkle=0.4, gain=0.4)

    # ---- blades ----
    order = sorted(range(2, N + 1), key=lambda n: -zs[n])
    wbase = float(np.clip(0.26 * sp, 1.1 * u, 3.2 * u))
    def draw_class(which, part):
        def fn(d, s):
            for n in order:
                h = H[n - 2]
                if cls(h) != which: continue
                dx, dy, th, beads = geo[n]
                X = (xs[n] + dx) * s; Y = (ygs[n] + dy) * s; q = scl[n]
                m = len(X)
                if part == 'blade':
                    w0 = {'gin': 0.85, 'red': 1.7}.get(which, 1.0) * wbase * q * s
                    for i in range(m - 1):
                        t = i / (m - 1)
                        w = max(1, int(round(w0 * (1 - 0.72 * t))))
                        d.line([(X[i], Y[i]), (X[i + 1], Y[i + 1])], fill=int(255 * min(1.0, 0.12 + t / 0.10)), width=w)
                elif part == 'bead':
                    for (bx, by, g) in beads:
                        r = min(1.0 + 0.42 * log(g), 3.4) * wbase * q * s * 0.75
                        cx, cy = (xs[n] + bx) * s, (ygs[n] + by) * s
                        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
                elif part == 'head':
                    # seed head: a teardrop along the final direction
                    t = th[-1]; L = (4.5 + 1.0 * log(h['a'])) * wbase * q * s * (1.7 if which == 'red' else 1.0); wd = L * 0.24
                    if which == 'gin': L *= 0.55; wd *= 0.6
                    ux, uy = sin(t), -cos(t)
                    px, py = X[-1], Y[-1]
                    pts = []
                    for a in np.linspace(0, 2 * pi, 28):
                        f = 0.5 - 0.5 * cos(a)          # 0 at base .. 1 at tip
                        wloc = wd * sin(a) * (1 - 0.55 * f)
                        pts.append((px + ux * L * f - uy * wloc, py + uy * L * f + ux * wloc))
                    d.polygon(pts, fill=255)
        return P.mask(fn)
    for which, metal, tone in [('gin', GIN, 0.8), ('kin', KIN, 0.80), ('ao', AOKIN, 0.85), ('red', SHU, 1.0)]:
        mb = draw_class(which, 'blade')
        # blades rise out of the dust: fade the bottom 2%
        fade = 1.0
        P.leaf(mb * fade, metal, height=1.3 * u, tone=tone, burnish=0.25, glow=0.22)
        mh = draw_class(which, 'head')
        P.leaf(mh, metal, height=2.2 * u, tone=tone * 1.08, burnish=0.6, glow=1.6 if which == 'red' else 0.5)
        mbead = draw_class(which, 'bead')
        P.leaf(mbead, metal if which != 'gin' else GIN, height=1.6 * u, tone=tone * 1.15, burnish=0.8, glow=0.55)
    if title:
        tm = P.text_mask([
            (0.055 * size, 0.948 * size, "The Meadow of the Rare Red Seed", 21 * u, False, "ls"),
            (0.055 * size, 0.972 * size, "one blade for each n from 2 to %d; it bends where a common factor is found, and its seed is a(n)" % N, 12.5 * u, True, "ls"),
            (0.945 * size, 0.948 * size, "silver: n is prime, nothing bends \u00b7 gold: a(n) proved prime by its last straight stretch", 11 * u, True, "rs"),
            (0.945 * size, 0.972 * size, "green gold: prime, stretch too short to prove it \u00b7 red: composite (n = 4, 12, 172)", 11 * u, True, "rs")])
        P.leaf(tm, AOKIN, height=0.8 * u, tone=0.8, burnish=0.1, glow=0.1)
    P.finish().save(out)
    st = {k: sum(1 for h in H if cls(h) == k) for k in ['gin', 'kin', 'ao', 'red']}
    print(out, st, [h['n'] for h in H if cls(h) == 'red'])

if __name__ == '__main__':
    size = int(sys.argv[1]); N = int(sys.argv[2]); out = sys.argv[3]
    render(size, N, out)
