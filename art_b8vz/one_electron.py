"""one_electron.py — Wheeler's one-electron universe (Phil.SE 142304 'One particle universe').

A single worldline: the zero set of G(x,t) = (x − ½) + A·n(x,t) on a strip, n a smooth Gaussian random
field.  The component that crosses the strip from the past edge to the future edge is THE electron;
oriented past→future, its forward-in-time stretches are electrons (warm), its backward stretches are
positrons (cool), and its turning points are pair creations (∪, local minima of t) and annihilations
(∩, local maxima) — coral.  Every horizontal 'now' cuts it in (#e) − (#p) = 1 points.
Closed components are vacuum bubbles (a pair made and unmade), drawn faint.
usage: one_electron.py S out.png [key=val]
"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from skimage.measure import find_contours
from sorbet import Sheet, PIG, absorb, lines, discs, text_mask, finish, text_w

ARG = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))


def field(N, seed, scale, A):
    rng = np.random.default_rng(seed)
    n = gaussian_filter(rng.standard_normal((N, N)), scale * N, mode='wrap')
    n /= n.std()
    x = np.linspace(0, 1, N)[None, :]
    return (x - 0.5) + A * n          # rows = t (row 0 = t=0 = bottom after flip), cols = x


def components(G):
    N = G.shape[0]
    cs = find_contours(G, 0.0)
    out = []
    for c in cs:
        t, x = c[:, 0] / (N - 1), c[:, 1] / (N - 1)
        span = (t.min() < 0.002) and (t.max() > 0.998)
        closed = np.hypot(t[0] - t[-1], x[0] - x[-1]) < 1e-6
        out.append((x, t, span, closed))
    return out


def main():
    S, out = int(sys.argv[1]), sys.argv[2]
    N = P('N', 1400)
    seed = P('seed', 3)
    G = field(N, seed, P('scale', 0.035), P('A', 0.22))
    comps = components(G)
    span = [c for c in comps if c[2]]
    print('components', len(comps), 'spanning', len(span), 'closed', sum(c[3] for c in comps))
    if not span:
        return
    x, t, _, _ = max(span, key=lambda c: len(c[0]))
    if t[0] > t[-1]:
        x, t = x[::-1], t[::-1]
    # map to canvas: margin, t up
    m = P('margin', 0.07); top = P('top', 0.04); bot = P('bot', 0.13)
    X = lambda x: S * (m + (1 - 2 * m) * x)
    Y = lambda t: S * (1 - bot - (1 - bot - top) * t)
    px, py = X(x), Y(t)
    dt = np.gradient(t)
    fwd = gaussian_filter(dt, 2) > 0
    # turning points
    s = np.sign(gaussian_filter(dt, 2))
    turn = np.nonzero(s[1:] * s[:-1] < 0)[0]
    sh = Sheet(S, S, seed=7)
    lw = S * P('lw', 0.0035)
    # split into runs
    runs = []
    st = 0
    for i in range(1, len(x)):
        if fwd[i] != fwd[st] or i == len(x) - 1:
            runs.append((st, i + 1, fwd[st])); st = i
    # bubbles
    bub = [c for c in comps if c[3] and len(c[0]) > 30]
    bl = [np.stack([X(c[0]), Y(c[1])], 1) for c in bub]
    if bl:
        db = lines(S, S, bl, lw * 0.6, sigma=S / 2600)
        sh.wash(gaussian_filter(db, S / 160) * 1.2 + db * 0.25, 'lilac')
    warm = [np.stack([px[a:b], py[a:b]], 1) for a, b, f in runs if f]
    cool = [np.stack([px[a:b], py[a:b]], 1) for a, b, f in runs if not f]
    dw = lines(S, S, warm, lw, sigma=S / 2200); dc = lines(S, S, cool, lw, sigma=S / 2200)
    sh.wash(gaussian_filter(dw, S / 90) * P('halo', 5.0), 'peach')
    sh.wash(gaussian_filter(dc, S / 90) * P('halo', 5.0), 'sky')
    sh.wash(gaussian_filter(dw, S / 300) * 1.4, 'strawberry')
    sh.wash(gaussian_filter(dc, S / 300) * 1.4, 'periwinkle')
    sh.wash(dw * 0.9, 'strawberry'); sh.wash(dc * 0.9, 'periwinkle')
    # coral turning points
    cx, cy = px[turn], py[turn]
    dd = discs(S, S, cx, cy, np.full(len(cx), lw * 2.2), sigma=S / 2600)
    sh.lighten(np.clip(gaussian_filter(dd, S / 400) * 3, 0, 1), 0.85)
    sh.wash(dd * 1.6, 'coral')
    img = sh.develop(dmax=1.8)
    finish(img, S, out)
    print('turns', len(turn))


if __name__ == '__main__':
    main()
