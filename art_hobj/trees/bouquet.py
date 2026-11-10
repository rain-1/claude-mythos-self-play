"""Six seed-heads: uniformly random functions f on n points with f^k constant, k = 1..6,
drawn as compound umbels (root = the fixed point).  Boltzmann sampler for T_k = x exp(T_{k-1})."""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
sys.setrecursionlimit(10000)
rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 7)

def Tvals(x, k):
    T = [x]; dT = [1.0]
    for j in range(1, k + 1):
        e = math.exp(T[-1]); T.append(x * e); dT.append(e * (1 + x * dT[-2] if False else 1 + x * dT[-1]))
    return T, dT
def mean_size(x, k):
    T, dT = Tvals(x, k); return x * dT[k] / T[k]
def solve_x(k, n):
    lo, hi = 1e-6, float(n)
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        try: m = mean_size(mid, k)
        except OverflowError: m = 1e300
        if m > n: hi = mid
        else: lo = mid
    return lo
def sample(k, n):
    x = solve_x(k, n); T, _ = Tvals(x, k)
    def gen(j, budget):
        if j == 0: return []
        ch = []
        for _ in range(rng.poisson(T[j - 1])):
            budget[0] -= 1
            if budget[0] < 0: raise OverflowError
            ch.append(gen(j - 1, budget))
        return ch
    tries = 0
    while True:
        tries += 1
        try: t = gen(k, [n - 1])
        except OverflowError: continue
        if size(t) == n and height(t) == k: return t, tries
def size(t): return 1 + sum(size(c) for c in t)
def height(t): return 0 if not t else 1 + max(height(c) for c in t)

DEPTH = [(250,108,102),(255,214,110),(255,170,128),(255,140,170),(204,150,240),(140,160,250),(120,205,245)]
STEM = [(126,190,120),(150,205,130),(170,214,150),(186,222,170),(200,228,186),(210,232,200),(216,236,210)]

def draw_head(t, k, Rpx, ss=3):
    """returns RGBA tile (side 2.5*Rpx)."""
    W = int(2.5 * Rpx * ss); im = Image.new('RGBA', (W, W), (255, 255, 255, 0)); d = ImageDraw.Draw(im)
    rho = 0.66; w = [rho ** j for j in range(k)]; ell = [Rpx * ss * x / sum(w) for x in w]
    segs = []; dots = []
    def lay(node, x, y, a0, a1, dep):
        sz = [size(c) for c in node]; tot = sum(sz)
        # children sorted so big subtrees interleave with small ones
        order = np.argsort(sz)[::-1]; arr = [None] * len(node); lo, hi = 0, len(node) - 1
        seq = list(order[::2]) + list(order[1::2][::-1])
        a = a0
        span = a1 - a0
        if dep > 0: span = min(span, 1.9)                 # umbels never open past ~110 degrees
        mid = (a0 + a1) / 2; a = mid - span / 2
        for ci in seq:
            c = node[ci]; da = span * sz[ci] / tot; th = a + da / 2
            L = ell[dep] * (0.90 + 0.2 * rng.random()) * (1.0 if node[ci] else 0.93)
            x2 = x + L * math.cos(th); y2 = y + L * math.sin(th)
            segs.append((dep, x, y, x2, y2))
            if c: lay(c, x2, y2, th - max(da, 0.5 * span / max(len(node), 1) + 0.25) / 2 - 0.25, th + max(da, 0.25) / 2 + 0.25, dep + 1)
            else: dots.append((dep + 1, x2, y2))
            a += da
    r0 = rng.random() * 6.28
    lay(t, W / 2, W / 2, r0, r0 + 2 * math.pi, 0)
    for dep, x, y, x2, y2 in sorted(segs, key=lambda s: -s[0]):
        thin = min(1.0, (36.0 / max(len(t), 1)) ** 0.5) if dep == 0 else 1.0
        wd = max(int(round(ss * Rpx / 300 * (3.0 * 0.62 ** dep * thin + 0.75))), 1)
        d.line((x, y, x2, y2), fill=STEM[dep + (2 if (dep == 0 and thin < 0.5) else 0)] + (235,), width=wd)
    for dep, x, y in dots:
        r = ss * Rpx / 300 * (4.6 if k > 1 else 3.6)
        c = DEPTH[dep]
        d.ellipse((x - r*1.9, y - r*1.9, x + r*1.9, y + r*1.9), fill=c + (46,))
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (255,))
        d.ellipse((x - r * 0.55, y - r * 0.6, x - r * 0.05, y - r * 0.1), fill=(255, 255, 255, 150))
    r = ss * Rpx / 300 * 9
    d.ellipse((W/2 - r, W/2 - r, W/2 + r, W/2 + r), fill=DEPTH[0] + (255,))
    d.ellipse((W/2 - r*0.55, W/2 - r*0.6, W/2 - r*0.05, W/2 - r*0.1), fill=(255, 255, 255, 170))
    return im.resize((W // ss, W // ss), Image.LANCZOS)

def font(name, sz): return ImageFont.truetype(f'/usr/share/fonts/truetype/{name}', int(sz))

if __name__ == '__main__':
    S = int(sys.argv[1]); n = int(sys.argv[2]); out = sys.argv[4] if len(sys.argv) > 4 else '../out/proto_bouquet.png'
    yy, xx = np.mgrid[0:S, 0:S] / S
    sky = np.empty((S, S, 3)); top = np.array([0.90, 0.95, 1.0]); bot = np.array([1.0, 0.965, 0.93])
    g = np.clip(yy / 0.9, 0, 1)[..., None] ** 1.3; sky[:] = top * (1 - g) + bot * g
    sky += np.random.default_rng(1).normal(0, 0.004, (S, S, 1))
    im = Image.fromarray((np.clip(sky, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    R = 0.132 * S
    xs = [0.150, 0.290, 0.430, 0.570, 0.710, 0.850]; ys = [0.50, 0.20, 0.53, 0.22, 0.50, 0.19]
    pos = list(zip(xs, ys)); R = 0.122 * S
    base = (0.50 * S, 0.885 * S)
    trees = []
    for k in range(1, 7):
        t, tries = sample(k, n); print('k', k, 'tries', tries, flush=True); trees.append(t)
    skyim = im.copy()
    for k in sorted(range(1, 7), key=lambda k: pos[k - 1][1]):          # back (high) to front (low)
        px, py = pos[k - 1]
        # haze disc: this head sits in front of the earlier stems
        hz = Image.new('L', im.size, 0); ImageDraw.Draw(hz).ellipse((px * S - R * 1.08, py * S - R * 1.08, px * S + R * 1.08, py * S + R * 1.08), fill=215)
        hz = hz.filter(ImageFilter.GaussianBlur(R * 0.10)); im.paste(skyim, (0, 0), hz)
        d = ImageDraw.Draw(im, 'RGBA')
        P0 = np.array([px * S, py * S]); P3 = np.array([base[0] + (px - 0.5) * 0.085 * S, base[1]])
        if py < 0.35: P1 = np.array([px * S, 0.60 * S]); P2 = np.array([px * S + (0.5 - px) * 0.25 * S, 0.76 * S])
        else: P1 = np.array([px * S + (0.5 - px) * 0.10 * S, 0.70 * S]); P2 = np.array([P3[0] + (px - 0.5) * 0.16 * S, 0.80 * S])
        ts = np.linspace(0, 1.10, 400)[:, None]
        C = (1 - ts) ** 3 * P0 + 3 * ts * (1 - ts) ** 2 * P1 + 3 * ts ** 2 * (1 - ts) * P2 + ts ** 3 * P3
        w = max(int(S / 330), 2)
        d.line([tuple(p) for p in C], fill=(120, 184, 118, 255), width=w, joint='curve')
        d.line([tuple(p - np.array([w * 0.3, 0])) for p in C], fill=(176, 222, 160, 255), width=max(w // 3, 1), joint='curve')
        tile = draw_head(trees[k - 1], k, R)
        sh = Image.new('RGBA', tile.size, (150, 140, 200, 0)); sh.putalpha(tile.getchannel('A').filter(ImageFilter.GaussianBlur(S / 300)).point(lambda v: v * 0.30))
        x = int(px * S - tile.size[0] / 2); y = int(py * S - tile.size[1] / 2)
        for layer, off in ((sh, (int(S / 250), int(S / 180))), (tile, (0, 0))):
            xx_, yy_ = x + off[0], y + off[1]
            im.alpha_composite(layer, (max(xx_, 0), max(yy_, 0)), (max(-xx_, 0), max(-yy_, 0)))
        d = ImageDraw.Draw(im, 'RGBA')
        ly = py * S + R * 1.22
        d.text((px * S - 0.052 * S, ly - 0.012 * S), f'k = {k}', font=font('liberation/LiberationSerif-Italic.ttf', 0.021 * S), fill=(92, 77, 102, 255), anchor='mm')
    # twine tie at the base: a small striped band
    bx, by = base; tw = 0.040 * S; th_ = 0.013 * S; q = 4
    band = Image.new('RGBA', (int(2 * tw * q), int(2 * th_ * q)), (255, 250, 244, 255)); db = ImageDraw.Draw(band)
    for i in range(-4, 30):
        x0_ = i * th_ * q * 0.8
        db.polygon([(x0_, 2 * th_ * q), (x0_ + th_ * q * 0.4, 2 * th_ * q), (x0_ + th_ * q * 1.4, 0), (x0_ + th_ * q, 0)], fill=(250, 108, 102, 255))
    yy2 = np.linspace(-1, 1, band.size[1])[:, None]; shade = (0.80 + 0.20 * np.sqrt(np.clip(1 - yy2 ** 2, 0, 1)))
    arr = np.asarray(band).astype(float); arr[..., :3] *= shade[..., None]; band = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    mk = Image.new('L', band.size, 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, band.size[0] - 1, band.size[1] - 1), radius=int(th_ * q), fill=255)
    band.putalpha(mk); band = band.resize((int(2 * tw), int(2 * th_)), Image.LANCZOS)
    bsh = Image.new('RGBA', band.size, (150, 140, 200, 0)); bsh.putalpha(band.getchannel('A').point(lambda v: v * 0.35))
    im.alpha_composite(bsh.filter(ImageFilter.GaussianBlur(S / 500)), (int(bx - tw + S / 400), int(by - th_ + S / 250)))
    im.alpha_composite(band, (int(bx - tw), int(by - th_)))
    d = ImageDraw.Draw(im, 'RGBA')
    ink = (92, 77, 102, 255)
    d.text((0.055 * S, 0.885 * S), 'Six Ways to Arrive at One', font=font('liberation/LiberationSerif-Bold.ttf', 0.033 * S), fill=ink)
    d.text((0.055 * S, 0.929 * S), f'Six uniformly random maps f on {n} points with f\u1d4f constant:', font=font('liberation/LiberationSerif-Italic.ttf', 0.0175 * S), fill=ink)
    d.text((0.055 * S, 0.953 * S), 'every point reaches the coral one in at most k steps.', font=font('liberation/LiberationSerif-Italic.ttf', 0.0175 * S), fill=ink)
    mono = font('dejavu/DejaVuSansMono.ttf', 0.0108 * S); g2 = (132, 118, 146, 255)
    for i, line in enumerate(['how many such maps on 10 points?', 'k=1 10          k=4 354 648 160', 'k=2 2 936 080   k=5 660 253 600', 'k=3 90 466 480  k=9 10⁹ (Cayley)', 'blossom colour = steps from home']):
        d.text((0.68 * S, 0.885 * S + i * 0.0185 * S), line, font=mono, fill=g2)
    im.convert('RGB').save(out); print('saved', out)
