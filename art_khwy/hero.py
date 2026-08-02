"""HERO 4096x4096 — 'One Thread Through Every Meeting'
Five verified champion polygons: n=5 (10), 7 (18=21-3), 9 (33=36-3),
11 (55, center), 13 (78). Full-circuit worlds get an unbroken gold
thread through every crossing; the mod-8-obstructed worlds show their
three closed doors as cold cyan ghosts."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from polylib import forced_graph, drop_triangle_graph, crossings, vid
from rendlib import Canvas, save

S = 4096
GOLD   = np.array([1.00, 0.74, 0.30])
COPPER = np.array([0.98, 0.45, 0.20])
CREAM  = np.array([1.00, 0.92, 0.66])
STEEL  = np.array([0.42, 0.52, 0.72])
ICE    = np.array([0.55, 0.85, 1.00])
BG     = (0.0012, 0.0014, 0.0030)

def cycle_order(edges):
    nbr = {}
    for u, v in edges:
        nbr.setdefault(u, []).append(v); nbr.setdefault(v, []).append(u)
    v0 = next(iter(nbr)); cyc = [v0]; prev = None; v = v0
    while True:
        a, b = nbr[v]; nxt = a if a != prev else b
        if nxt == v0: break
        cyc.append(nxt); prev, v = v, nxt
    return cyc

def thread_color(t):
    w1 = 0.5 + 0.5*np.cos(2*np.pi*t)
    w2 = 0.5 + 0.5*np.cos(2*np.pi*t - 2*np.pi/3)
    w3 = 0.5 + 0.5*np.cos(2*np.pi*t - 4*np.pi/3)
    s = w1 + w2 + w3
    return (w1[:,None]*GOLD + w2[:,None]*COPPER + w3[:,None]*CREAM) / s[:,None]

def medallion(cv, n, mode, cx, cy, R, rs=1.0):
    if mode == "full":
        theta = np.load(f"hero_n{n}_theta.npy"); r = np.load(f"hero_n{n}_r.npy")
        comps, edges, _ = forced_graph(theta, r)
        tri = None
    else:
        theta = np.load(f"hero18_n{n}_theta.npy"); r = np.load(f"hero18_n{n}_r.npy")
        tri = tuple(np.load(f"hero18_n{n}_tri.npy"))
        comps, edges = drop_triangle_graph(theta, r, tri)
    assert len(comps) == 1
    X, Y, T = crossings(theta, r)
    iu = np.triu_indices(n, 1)
    px, py = X[iu], Y[iu]
    # normalize: center on used-vertex centroid, scale 97th pct radius
    used = set()
    for u, v in edges: used.add(u); used.add(v)
    P = {}
    for i in range(n):
        for j in range(i+1, n):
            P[i*n+j] = np.array([X[i,j], Y[i,j]])
    UP = np.array([P[u] for u in used])
    c0 = UP.mean(0)
    rad = np.linalg.norm(UP - c0, axis=1)
    sc = 0.93 * R / rad.max()
    def w2s(p):
        q = (p - c0) * sc
        return np.array([cx + q[0], cy - q[1]])
    # 1. arrangement lines, clipped to disc 1.06R
    ct, st = np.cos(theta), np.sin(theta)
    Rclip = 1.06 * R
    A_, B_ = [], []
    for i in range(n):
        # local-frame line: points p with ct*px+st*py = r ; transform to screen
        p0 = np.array([ct[i]*r[i], st[i]*r[i]])
        dv = np.array([-st[i], ct[i]])
        s0 = w2s(p0); s1 = w2s(p0 + dv)
        d = s1 - s0; d /= np.linalg.norm(d)
        rel = np.array([cx, cy]) - s0
        tproj = rel @ d
        closest = s0 + tproj * d
        dist = np.linalg.norm(closest - np.array([cx, cy]))
        if dist >= Rclip: continue
        half = np.sqrt(Rclip**2 - dist**2)
        A_.append(closest - d*half); B_.append(closest + d*half)
    cv.segments(np.array(A_), np.array(B_), STEEL, width=1.1*rs,
                amp=0.075, step=0.5)
    # 2. the thread
    cyc = cycle_order(edges)
    k = len(cyc)
    pts = np.array([w2s(P[v]) for v in cyc])
    A = pts
    B = np.roll(pts, -1, axis=0)
    t = (np.arange(k) + 0.5) / k
    cols = thread_color(t)
    cv.segments(A, B, GOLD, width=1.9*rs, amp=2.3, step=0.4,
                color_per=cols)
    # 3. corner beads
    cv.stars(pts[:,0], pts[:,1], CREAM, sigma=2.4*rs, amp=6.0*rs*rs)
    # 4. ghost doors (drop mode)
    if tri is not None:
        gh = [P[vid(a, b, n)] for a, b in
              [(tri[0],tri[1]), (tri[1],tri[2]), (tri[0],tri[2])]]
        gp = np.array([w2s(g) for g in gh])
        # ghost triangle whisper
        cv.segments(gp, np.roll(gp, -1, axis=0), ICE, width=1.0*rs, amp=0.24)
        cv.stars(gp[:,0], gp[:,1], ICE, sigma=3.2*rs, amp=6.0)
        cv.stars(gp[:,0], gp[:,1], ICE, sigma=12.0*rs, amp=2.6)
    return len(cyc)

cv = Canvas(S, S, BG)
# subtle radial field
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
rr = np.sqrt((xx-S/2)**2 + (yy-S/2)**2) / (S/2)
cv.buf += (0.003 * np.exp(-rr*rr*1.4))[..., None] * np.array([0.5,0.6,0.9], np.float32)
del xx, yy, rr

k5  = medallion(cv, 5,  "full", 660,  855, 430, rs=0.92)
k7  = medallion(cv, 7,  "drop", 3436, 855, 430, rs=0.92)
k11 = medallion(cv, 11, "full", 2048, 2040, 1010, rs=1.35)
k9  = medallion(cv, 9,  "drop", 660,  3230, 430, rs=0.92)
k13 = medallion(cv, 13, "full", 3436, 3230, 430, rs=0.92)
print("sides:", k5, k7, k9, k11, k13)

cv.bloom(sigmas=(5, 16, 48), gains=(0.48, 0.28, 0.15), thresh=0.45)
img = cv.tonemap(k=1.75, gamma=2.1)

# ---- annotations (after bloom) ----
pil = Image.fromarray(img)
d = ImageDraw.Draw(pil)
FP = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def F(sz): return ImageFont.truetype(FP, sz)
def ctext(x, y, s, sz, col, anchor="mm"):
    d.text((x, y), s, font=F(sz), fill=col, anchor=anchor)

warm = (238, 209, 156); dim = (132, 140, 165); ice = (150, 208, 235)
ctext(2048, 150, "O N E   T H R E A D   T H R O U G H   E V E R Y   M E E T I N G", 74, warm)
ctext(2048, 250, "simple polygons drawn on n lines, using every pairwise crossing once   ·   MO 513798", 40, dim)

ctext(660, 1370, "n = 5   —   the 10-gon, complete", 42, warm)
ctext(660, 1428, "5 ≡ 5 (mod 8): the full circuit is permitted", 33, dim)
ctext(3436, 1370, "n = 7   —   the 18-gon,  21 − 3", 42, warm)
ctext(3436, 1428, "7 ≡ 7 (mod 8): parity closes three doors", 33, ice)
ctext(660, 3745, "n = 9   —   the 33-gon,  36 − 3", 42, warm)
ctext(660, 3803, "9 ≡ 1 (mod 8): parity closes three doors", 33, ice)
ctext(3436, 3745, "n = 13   —   the 78-gon, complete", 42, warm)
ctext(3436, 3803, "13 ≡ 5 (mod 8): the full circuit is permitted", 33, dim)
ctext(2048, 3210, "n = 11   —   the 55-gon: one simple polygon through all 55 crossings of 11 lines", 46, warm)

ctext(2048, 3925, "THEOREM (this work): on each line the polygon's sides are forced — consecutive crossings pair (1,2)(3,4)…; the union is always a", 34, dim)
ctext(2048, 3977, "non-crossing 2-regular graph, and its cycle count C obeys  C ≡ ⌊(n+1)/4⌋ (mod 2)  across ALL simple arrangements  (flip-invariance +", 34, dim)
ctext(2048, 4029, "regular-fan orbit count).  The bound n(n−1)/2 is attainable iff n ≡ 3, 5 (mod 8); otherwise max = n(n−1)/2 − 3, attained here.", 34, dim)

pil.save("hero_4096.png")
print("saved hero_4096.png")
