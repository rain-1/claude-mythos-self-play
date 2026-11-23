"""honesty.py -- 'Honesty, Pressed'  (cyanotype photogram; Fable 5.2, day 10)

The Calkin-Wilf tree as a pressed plant.  Node (a,b) (coprime) bears one pod, as many times longer than wide as the
fraction says, of area (pi/4) D^2/(ab)^2 -- the share of the fields of that shape.  Its two
shoots go to (a+b,b) and (a,a+b).  Every stem is drawn exactly as wide as  c * f(a,b),
     f(a,b) = 1/(a b^3) + 1/(2 a^2 b^2) + 1/(a^3 b)  =  the total area of the pods it carries (Zagier's function),
so at every fork   stem = pod stalk + shoot + shoot   and the cut end is 5/2 = 1 + 3/4 + 3/4:
the round pod is two fifths of the plant.
usage: honesty.py SIZE out.png"""
import sys, numpy as np
from fractions import Fraction as Fr
from PIL import Image, ImageDraw
import cyano
size = int(sys.argv[1]); out = sys.argv[2]
def f(a, b): return 1 / (a * b**3) + 1 / (2 * a * a * b * b) + 1 / (a**3 * b)
D = 1.0; C = 0.100                    # pod length unit; stem width per unit of f
NS = 26                               # nodes drawn along each great bough
stems = []; pods = []                 # stems: (p0, p1, width); pods: (centre, direction, length, breadth, stalk_w)
rot = lambda d: np.array([np.sin(d), -np.cos(d)])      # direction: angle from 'up', clockwise positive (y down)
def pod(p, d, a, b, stalk):
    lo_, hi_ = min(a, b), max(a, b)
    ln, br = D / (a * b) * (hi_ / lo_)**0.5, D / (a * b) * (lo_ / hi_)**0.5      # aspect = the fraction, area ~ 1/(ab)^2
    w = C / (a * b)**2
    q = p + rot(d) * stalk
    stems.append((p, q, w))
    pods.append((q + rot(d) * ln / 2, d, ln, br, (a, b)))
def twig(p, d, a, b, length, side):
    """a generic node: stem arrives at p heading d"""
    if f(a, b) * C < 0.0004: return
    pod(p, d + 0.10 * side, a, b, 0.05 + 0.10 / min(a, b))
    for (x, y), sg in (((a + b, b), -1), ((a, a + b), +1)):
        fc = f(x, y)
        if fc * C < 0.0004: continue
        dd = d + sg * 0.75 + 0.15 * side
        ln = length * 0.72
        q = p + rot(dd) * ln
        stems.append((p, q, fc * C)); twig(q, dd, x, y, ln, side)
def bough(p, side, droop):
    """the spine (1,n), n = 2, 3, ...: side = +1 right, -1 left"""
    d0 = 1.08
    lens = [0.52] + [(D / n**1.5 + D / (n + 1)**1.5) / 2 + 0.017 for n in range(2, NS + 2)]
    tot = sum(lens); s = 0.0
    for i, n in enumerate(range(2, NS + 2)):
        d = side * (d0 + droop * (s / tot)**0.9); s += lens[i]
        q = p + rot(d) * lens[i]
        ab = (1, n) if side > 0 else (n, 1)
        stems.append((p, q, f(*ab) * C)); p = q
        dn = side * (d0 + droop * (s / tot)**0.9)
        pod(p, dn - side * 0.88, ab[0], ab[1], 0.035)                      # the pod stands on the upper side, swept forward
        x, y = (n + 1, n) if side > 0 else (n, n + 1)                    # the small shoot hangs below
        dd = dn + side * 1.25
        ln = 0.42 / (n - 0.6)
        if f(x, y) * C > 0.0004:
            t = p + rot(dd) * ln; stems.append((p, t, f(x, y) * C)); twig(t, dd, x, y, ln, side)
root = np.array([0.0, 0.0]); fork = root + rot(0.03) * 0.95
stems.append((root, fork, f(1, 1) * C))
pod(fork, -0.02, 1, 1, 0.62)
bough(fork, +1, 1.30); bough(fork, -1, 1.12)
# ---- fit to the sheet ----------------------------------------------------------------------------
pts = np.array([p for s_ in stems for p in s_[:2]] + [c + rot(d) * l / 2 * sg for c, d, l, b, _ in pods for sg in (-1, 1)])
lo, hi = pts.min(0), pts.max(0)
box = (0.085, 0.085, 0.915, 0.825)
sh = cyano.Sheet(size, seed=31, ss=2, coat_box=box)
n = size; mx, my = 0.075 * n, 0.060 * n
sc = min(((box[2] - box[0]) * n - 2 * mx) / (hi[0] - lo[0]), ((box[3] - box[1]) * n - 2 * my) / (hi[1] - lo[1]))
th = -0.035; R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
ctr = (lo + hi) / 2; mid = np.array([(box[0] + box[2]) / 2 * n, (box[1] + box[3]) / 2 * n])
T = lambda p: (np.asarray(p) - ctr) @ R.T * sc + mid
print('scale', sc, 'px per pod length; trunk width %.1f px' % (f(1, 1) * C * sc))
im, d, ss = sh.canvas()          # opaque: stems, rims, seeds
im2, d2, _ = sh.canvas()         # translucent: pod membranes
def quad(dr, p0, p1, w, fill=255):
    p0, p1 = T(p0) * ss, T(p1) * ss; w = w * sc * ss
    if w < 1.4:
        dr.line([tuple(p0), tuple(p1)], fill=int(255 * min(1.0, w / 1.4) * fill / 255), width=1); return
    v = p1 - p0; L = np.hypot(*v) + 1e-9; nrm = np.array([-v[1], v[0]]) / L * w / 2
    dr.polygon([tuple(p0 + nrm), tuple(p1 + nrm), tuple(p1 - nrm), tuple(p0 - nrm)], fill=fill)
    for p in ((p1,) if w > 0.2 * sc * ss else (p0, p1)): dr.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=fill)
for p0, p1, w in sorted(stems, key=lambda s_: s_[2]): quad(d, p0, p1, w)
rng = np.random.default_rng(5)
for c, dr_, ln, br, ab in pods:
    t = np.linspace(0, 2 * np.pi, 90, endpoint=False)
    e1 = rot(dr_); e2 = np.array([-e1[1], e1[0]])
    # a pod: an ellipse, a little pointed at the far end
    r = 1 + 0.06 * np.cos(t) ** 3
    P = [T(c + e1 * (ln / 2) * np.cos(tt) * rr + e2 * (br / 2) * np.sin(tt)) * ss for tt, rr in zip(t, r)]
    P = [tuple(p) for p in P]
    if br * sc * ss < 1.6:
        a0, a1 = T(c - e1 * ln / 2) * ss, T(c + e1 * ln / 2) * ss
        d2.line([tuple(a0), tuple(a1)], fill=int(255 * min(1, br * sc * ss / 1.6)), width=1); continue
    d2.polygon(P, fill=255)
    rim = max(1.0, min(0.035 * br * sc, 2.6 * sh.S)) * ss
    if br * sc > 7: d.line(P + [P[0]], fill=255, width=int(round(rim)))
    if br * sc > 26:   # seeds on their threads, as in a Lunaria pod
        k = 6 if ab == (1, 1) else 3
        for j in range(k):
            u_ = (j + 0.5) / k
            if ab == (1, 1):
                ang = 2 * np.pi * u_ + 0.4; sp = c + e1 * 0.24 * ln * np.cos(ang) + e2 * 0.24 * br * np.sin(ang)
            else:
                sp = c + e1 * ln * (u_ - 0.5) * 0.66 + e2 * br * 0.10 * (-1) ** j
            q = T(sp) * ss; sr = max(1.6, 0.060 * br * sc) * ss
            d.ellipse([q[0] - sr, q[1] - 0.72 * sr, q[0] + sr, q[1] + 0.72 * sr], fill=235)
sh.lay(sh.to_mask(im2), opacity=0.58, height=0.9, halo=0.10)
sh.lay(sh.to_mask(im), opacity=0.97, height=0.55, halo=0.18)
sh.expose(); sh.develop()
# ---- margin ---------------------------------------------------------------------------------------
sh.text('Honesty, Pressed', (0.5, 0.893), 30)
sh.text('Each pod has the shape of a fraction and the size of its share; each stem is exactly as wide as the pods it carries are large.', (0.5, 0.928), 14.4)
sh.text('At the cut end 5/2 = 1 + 3/4 + 3/4, so the round pod is two fifths of the plant.   Up the right bough: 3/4 = 1/4 + 2/27 + 23/54,  23/54 = 1/9 + 31/1728 + 19/64, ...', (0.5, 0.955), 13.2)
sh.text('stem of a/b :  1/ab³ + 1/2a²b² + 1/a³b   (Zagier)        shoots of a/b :  (a+b)/b  and  a/(a+b)', (0.5, 0.979), 12.2, italic=False)
st = np.zeros((n, n), np.float32); x0, y0, w_ = int(0.905 * n), int(0.880 * n), int(0.030 * n)
st[y0:y0 + w_, x0:x0 + w_] = 1; st[y0 + 3 * n // 1024:y0 + w_ - 3 * n // 1024, x0 + 3 * n // 1024:x0 + w_ - 3 * n // 1024] = 0
sh.stamp(st); sh.text('⅖', ((x0 + w_ / 2) / n, (y0 + w_ / 2) / n), 21, italic=False, layer='red', font="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
sh.develop(); sh.save(out)
