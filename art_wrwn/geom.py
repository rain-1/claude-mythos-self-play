"""geom.py — the motion of an assembly round the corner, in the corridor's frame.

Corridor frame: inner corner at (0,0), outer corner at (w,w); arm 1 is {0<=Y<=w, X<=w} (runs to X=-inf),
arm 2 is {0<=X<=w, Y<=w} (runs to Y=-inf).  The canonical motion keeps the assembly pressed against BOTH
outer walls X=w and Y=w while it turns (Lemma 1: if any motion exists, this one does).
"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'math_corner'))
from corner import verts, width, profiles

class Motion:
    def __init__(self, P, N=7200):
        self.P = np.asarray(P, float).reshape(-1, 3); self.n = len(self.P)
        self.V = verts(self.P)                      # (n,4,2)
        self.w, i, l, self.sw = width(self.P, N)
        self.t0 = 2 * np.pi * i / N; self.t1 = self.t0 + 2 * np.pi * l / N
        self.N = N
        self.area = self.n / self.w ** 2
    def frame(self, t, V=None):
        """vertices in the corridor frame at turning angle t (pressed to both outer walls)"""
        V = self.V if V is None else V
        c, s = np.cos(t), np.sin(t)
        X = c * self.V[..., 0] + s * self.V[..., 1]; Y = -s * self.V[..., 0] + c * self.V[..., 1]
        hx, hy = X.max(), Y.max()
        if V is not self.V:
            Xo = c * V[..., 0] + s * V[..., 1]; Yo = -s * V[..., 0] + c * V[..., 1]
        else: Xo, Yo = X, Y
        out = np.stack([Xo - hx + self.w, Yo - hy + self.w], -1)
        if self.sw: out = out[..., ::-1]            # arc ran from arm 2 to arm 1: mirror so that it always starts in arm 1
        return out
    def pose(self, tau, slide=2.0, V=None):
        """tau in [-1,2]: [-1,0] slide in along arm 1, [0,1] turn, [1,2] slide out along arm 2"""
        if tau < 0:
            F = self.frame(self.t0, V).copy(); F[..., 0] += tau * slide * self.w; return F
        if tau > 1:
            F = self.frame(self.t1, V).copy(); F[..., 1] -= (tau - 1) * slide * self.w; return F
        return self.frame(self.t0 + tau * (self.t1 - self.t0), V)
    def hull_mask(self, res=900, K=721, pad=0.25):
        """in the ASSEMBLY's frame: fraction of the turn during which each point is inside the corridor.
        returns (frac, extent) ; frac==1 is the largest sofa that can follow this very motion."""
        V = self.V.reshape(-1, 2); lo = V.min(0) - pad * self.w - 0.3; hi = V.max(0) + pad * self.w + 0.3
        span = max(hi - lo); mid = (lo + hi) / 2; lo = mid - span / 2; hi = mid + span / 2
        xs = np.linspace(lo[0], hi[0], res); ys = np.linspace(lo[1], hi[1], res)
        gx, gy = np.meshgrid(xs, ys)
        acc = np.zeros((res, res), np.float32)
        for t in np.linspace(self.t0, self.t1, K):
            c, s = np.cos(t), np.sin(t)
            X = c * self.V[..., 0] + s * self.V[..., 1]; Y = -s * self.V[..., 0] + c * self.V[..., 1]
            hx, hy = X.max(), Y.max()
            A = c * gx + s * gy - hx + self.w; B = -s * gx + c * gy - hy + self.w
            acc += ((A <= self.w) & (B <= self.w) & ((A >= 0) | (B >= 0)))
        return acc / K, (lo, hi)

def load(n, d=None):
    d = d or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'math_corner')
    return np.array(json.load(open(os.path.join(d, f'best_{n}.json')))['P']).reshape(-1, 3)

if __name__ == '__main__':
    from PIL import Image, ImageDraw
    n = int(sys.argv[1]); M = Motion(load(n))
    print('n', n, 'w', M.w, 'area', M.area, 'arc deg', np.degrees(M.t0), np.degrees(M.t1), 'sw', M.sw)
    S = 900; im = Image.new('RGB', (2 * S, S), 'white'); d = ImageDraw.Draw(im)
    sc = S / (3.6 * M.w); T = lambda p: (S - 40 + (p[0] - M.w) * sc, 40 + (M.w - p[1]) * sc)
    d.line([T((-9, M.w)), T((M.w, M.w)), T((M.w, -9))], fill='black', width=3)
    d.line([T((-9, 0)), T((0, 0)), T((0, -9))], fill='black', width=3)
    for k, tau in enumerate(np.linspace(-0.5, 1.5, 13)):
        F = M.pose(tau); col = (int(40 + 200 * k / 12), 80, int(240 - 200 * k / 12))
        for q in F: d.polygon([T(p) for p in q], outline=col)
    fr, (lo, hi) = M.hull_mask(res=S)
    g = (255 * (1 - fr[::-1] ** 3)).astype(np.uint8); im.paste(Image.fromarray(g).convert('RGB'), (S, 0))
    T2 = lambda p: (S + (p[0] - lo[0]) / (hi[0] - lo[0]) * S, S - (p[1] - lo[1]) / (hi[1] - lo[1]) * S)
    for q in M.V: d.polygon([T2(p) for p in q], outline='red')
    print('hull area / w^2 =', (fr > 0.9999).mean() * (hi[0] - lo[0]) ** 2 / M.w ** 2)
    im.save(f'/tmp/claude-0/-home-user-claude-mythos-self-play/19660c75-8f09-51f4-b133-e6d6ba4d5b2f/scratchpad/diag_{n}.png')
