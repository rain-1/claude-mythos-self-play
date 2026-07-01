"""
01 — THE LARGEST THING THAT TURNS THE CORNER     (hero, 4096^2)
================================================================
The moving-sofa problem (Leo Moser, 1966): what is the largest area a rigid
shape can have and still slide around a right-angled corner in a width-1
hallway? Gerver's sofa (1992, area 2.2195...) was finally PROVEN optimal by
Jineon Baek in 2024 — a 58-year-old question closed.

We do not assume the answer. We treat the corridor as a rigid L that rotates
through 90 degrees relative to the sofa, and define
        sofa  =  the set of points inside the corridor at EVERY rotation.
We then OPTIMISE the corridor's motion (the path of its inner corner) to
maximise that intersection's area. Coordinate ascent finds area 2.172 — within
2% of Gerver's proven optimum — and the silhouette that emerges is unmistakably
his "telephone-handset": a long body with a semicircular bite scooped out
underneath, exactly where the hallway's inner corner sweeps through.

The picture is the ENVELOPE of the motion: every position of the two corridor
walls, splatted additively. Where the walls agree they pile into a caustic —
and the brightest caustic, the fan of cusps under the body, is the inner corner
itself carving the bite. The sofa is what all those blades leave untouched.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_erosion

# ---- the optimised corridor motion (inner-corner path, half by symmetry) ----
cxh, cyh = np.load(__file__.replace('01_the_corner.py', 'sofa_path.npy'))
nc = len(cxh); ctrl_t = np.linspace(0, np.pi/4, nc)

def expand(nt):
    th = np.linspace(0, np.pi/2, nt); cx = np.zeros(nt); cy = np.zeros(nt)
    for i, t in enumerate(th):
        if t <= np.pi/4:
            cx[i] = np.interp(t, ctrl_t, cxh); cy[i] = np.interp(t, ctrl_t, cyh)
        else:
            tm = np.pi/2 - t
            cx[i] = -np.interp(tm, ctrl_t, cxh); cy[i] = np.interp(tm, ctrl_t, cyh)
    return th, cx, cy

S = 4096
x0, x1 = -2.5, 2.5
y0, y1 = -0.78, 1.26
H = int(S*(y1-y0)/(x1-x0))
def w2p(x, y):
    return (x-x0)/(x1-x0)*S, (y1-y)/(y1-y0)*H

# ---- the sofa: intersection of the corridor over all rotations ----
print("building sofa mask...")
nt = 1100; th, cx, cy = expand(nt)
xs = np.linspace(x0, x1, S); ys = np.linspace(y1, y0, H)
X, Y = np.meshgrid(xs, ys)
inside = np.ones((H, S), bool)
for i in range(nt):
    ct, st = np.cos(-th[i]), np.sin(-th[i])
    dx = X - cx[i]; dy = Y - cy[i]
    u = ct*dx - st*dy + 1.0; v = st*dx + ct*dy + 1.0
    inside &= (((v >= 0)&(v <= 1)&(u <= 1)) | ((u >= 0)&(u <= 1)&(v <= 1)))
area = inside.sum()*(xs[1]-xs[0])*(ys[1]-ys[0])
print(f"   rendered sofa area = {area:.4f}   (Gerver optimum 2.2195)")

# ---- additive bilinear line splat ----
def splat_seg(buf, p0, p1, bright):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    L = np.hypot(*(p1-p0)); n = max(2, int(L*1.3))
    ts = np.linspace(0, 1, n); pts = p0*(1-ts[:, None]) + p1*ts[:, None]
    fx = pts[:, 0]; fy = pts[:, 1]
    ix = np.floor(fx).astype(int); iy = np.floor(fy).astype(int)
    dx = fx-ix; dy = fy-iy
    for ox in (0, 1):
        for oy in (0, 1):
            wx = (1-dx) if ox == 0 else dx; wy = (1-dy) if oy == 0 else dy
            xx = ix+ox; yy = iy+oy
            m = (xx >= 0)&(xx < buf.shape[1])&(yy >= 0)&(yy < buf.shape[0])
            np.add.at(buf, (yy[m], xx[m]), bright*wx[m]*wy[m])

# ---- the envelope: every position of the two corridor walls ----
print("splatting the wall envelope...")
nt2 = 900; th2, cx2, cy2 = expand(nt2)
inner = np.zeros((H, S)); outer = np.zeros((H, S))
for i in range(nt2):
    c = np.array([cx2[i], cy2[i]]); t = th2[i]
    dA = np.array([-np.cos(t), -np.sin(t)]); dB = np.array([np.sin(t), -np.cos(t)])
    for d in (dA, dB):                                   # inner walls -> bite caustic
        splat_seg(inner, w2p(*c), w2p(*(c+d*1.30)), 0.5)
    baseA = c + np.array([np.sin(t), -np.cos(t)])        # outer walls -> dome
    baseB = c + np.array([-np.cos(t), -np.sin(t)])
    splat_seg(outer, w2p(*(baseA-dA*0.3)), w2p(*(baseA+dA*3.2)), 0.22)
    splat_seg(outer, w2p(*(baseB-dB*0.3)), w2p(*(baseB+dB*3.2)), 0.22)

# fade in above the base; outer (dome) lives high, inner (blades+bite) reaches lower
vign = np.exp(-(((X)/2.3)**2 + ((Y-0.45)/0.95)**2))      # keep dome+bite, drop side boxes
vf_inner = np.clip((Y-0.00)/0.16, 0, 1)
vf_outer = np.clip((Y-0.34)/0.22, 0, 1)                   # dome only -> no low side boxes
inner *= vf_inner*np.clip(vign*1.7, 0, 1)
outer *= vf_outer*vign
inner = gaussian_filter(inner, 0.8); outer = gaussian_filter(outer, 0.9)
inner /= np.percentile(inner[inner > 0], 99.7)+1e-9
outer /= np.percentile(outer[outer > 0], 99.5)+1e-9
inner = np.clip(inner, 0, 1); outer = np.clip(outer, 0, 1)
outside = gaussian_filter((~inside).astype(float), 1.6)
inner *= outside; outer *= outside

# ---- compose ----
print("composing...")
img = np.empty((H, S, 3)); img[:] = np.array([0.020, 0.026, 0.052])
img[..., 0] += outer*0.08 + inner*0.46
img[..., 1] += outer*0.16 + inner*0.71
img[..., 2] += outer*0.31 + inner*1.06
grad = np.clip((Y-y0)/(y1-y0), 0, 1)
core = np.exp(-(((X)/2.0)**2 + ((Y-0.04)/0.7)**2))
warm = np.stack([np.full((H, S), 0.99),
                 0.55+0.20*grad+0.13*core,
                 0.15+0.10*grad+0.11*core], -1)
alpha = gaussian_filter(inside.astype(float), 1.1)[..., None]   # anti-alias the edge
img = warm*alpha + img*(1-alpha)
rim = inside & ~binary_erosion(inside, iterations=max(2, S//900))
rimb = gaussian_filter(rim.astype(float), 0.0017*S); rimb /= rimb.max()+1e-9
for ch, a in enumerate((1.0, 0.82, 0.40)):
    img[..., ch] += rimb*a*0.9
# inner-corner trajectory thread
path = np.zeros((H, S))
for i in range(nt2-1):
    splat_seg(path, w2p(cx2[i], cy2[i]), w2p(cx2[i+1], cy2[i+1]), 1.0)
path = gaussian_filter(path, 0.0011*S); path /= path.max()+1e-9; path *= outside
for ch, a in enumerate((0.88, 0.94, 0.74)):
    img[..., ch] += path*a*0.55

img = 1 - np.exp(-np.clip(img, 0, None)*1.28)
img = np.clip(img, 0, 1)**0.92
Image.fromarray((img*255).astype(np.uint8)).save(
    __file__.replace('01_the_corner.py', '01_the_corner.png'))
print("saved 01_the_corner.png", H, "x", S)
