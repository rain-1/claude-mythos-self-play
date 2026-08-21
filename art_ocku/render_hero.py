#!/usr/bin/env python3
"""THE PINWHEEL OF FATES — destiny-deviation field of the chameleon cyclic
chain (MO 514406) on the population simplex.

hue  = direction of the state's secret lean (which fate it whispers toward)
light= log-magnitude of the lean, terraced by decades (the amnesia of the bulk)
silk = nodal curves where one fate's lean crosses zero (three spiral families)
wash = expected absorption time (the price in days)
"""
import numpy as np, sys, time
from scipy.ndimage import gaussian_filter, map_coordinates, binary_dilation
import artlib

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS   = int(sys.argv[2]) if len(sys.argv) > 2 else 1
NPZ  = sys.argv[3] if len(sys.argv) > 3 else 'field400.npz'
OUT  = sys.argv[4] if len(sys.argv) > 4 else 'hero_prev.png'
S = SIZE * SS
rs = S / 2048.0          # proto-normalized scale factor

# ---------------- data ----------------
d = np.load(NPZ)
M = int(d['M']); states = d['states']; PR = d['PR']; PG = d['PG']
ET = d['ET'] if 'ET' in d.files else None
FR = np.full((M+1, M+1), np.nan); FG = np.full((M+1, M+1), np.nan)
FT = np.full((M+1, M+1), np.nan)
FR[states[:,0], states[:,1]] = PR
FG[states[:,0], states[:,1]] = PG
if ET is not None: FT[states[:,0], states[:,1]] = ET
for k in range(M+1):
    FR[0, k] = 0.0; FG[0, k] = 0.0            # r=0: blue wins
    FR[k, 0] = 0.0; FG[k, 0] = 1.0            # b=0: green wins
    if 0 <= M-k: FR[k, M-k] = 1.0; FG[k, M-k] = 0.0   # g=0: red wins
FR[M,0]=1.0; FG[M,0]=0.0; FR[0,M]=0.0; FG[0,M]=0.0; FR[0,0]=0.0; FG[0,0]=1.0
if ET is not None:
    C2 = M*(M-1)/2.0
    H = np.zeros(M+1)
    for j in range(1, M): H[j] = H[j-1] + C2/(j*(M-j))
    for k in range(M+1):
        FT[k,0] = H[min(k,M-1)]; FT[0,k] = H[min(k,M-1)]
        if 0 <= M-k: FT[k,M-k] = H[min(M-k,M-1)]
# fill NaN band near hypotenuse for clean bilinear stencils
for F in (FR, FG, FT):
    nan = np.isnan(F)
    for _ in range(3):
        f0 = np.nan_to_num(F, nan=0.0)
        w  = (~np.isnan(F)).astype(np.float64)
        num = (np.roll(f0,1,0)+np.roll(f0,-1,0)+np.roll(f0,1,1)+np.roll(f0,-1,1))
        den = (np.roll(w,1,0)+np.roll(w,-1,0)+np.roll(w,1,1)+np.roll(w,-1,1))
        fill = np.where((den>0)&np.isnan(F), num/np.maximum(den,1), np.nan)
        F[np.isnan(F)] = fill[np.isnan(F)]

# ---------------- geometry ----------------
cx, cy = S*0.5, S*0.535
Rtri = S*0.462
ang0 = -np.pi/2                     # red apex up
vR = np.array([cx + Rtri*np.cos(ang0),          cy + Rtri*np.sin(ang0)])
vG = np.array([cx + Rtri*np.cos(ang0+2*np.pi/3), cy + Rtri*np.sin(ang0+2*np.pi/3)])
vB = np.array([cx + Rtri*np.cos(ang0-2*np.pi/3), cy + Rtri*np.sin(ang0-2*np.pi/3)])
# affine: pixel -> barycentric
T = np.array([[vR[0]-vB[0], vG[0]-vB[0]],[vR[1]-vB[1], vG[1]-vB[1]]])
Tinv = np.linalg.inv(T)
ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
px = xs - np.float32(vB[0]); py = ys - np.float32(vB[1])
del xs, ys
aR = np.float32(Tinv[0,0])*px + np.float32(Tinv[0,1])*py
aG = np.float32(Tinv[1,0])*px + np.float32(Tinv[1,1])*py
del px, py
aB = 1.0 - aR - aG
inside = (aR >= 0) & (aG >= 0) & (aB >= 0)
rr = np.clip(aR*M, 0, M); bb = np.clip(aB*M, 0, M)
del aR, aG, aB
coords = np.array([rr[inside], bb[inside]])
del rr, bb
fr = map_coordinates(FR, coords, order=1, mode='nearest')
fg = map_coordinates(FG, coords, order=1, mode='nearest')
fb = 1.0 - fr - fg
ft = map_coordinates(FT, coords, order=1, mode='nearest') if ET is not None else None

# ---------------- deviation ----------------
DR = fr - 1/3; DG = fg - 1/3; DB = fb - 1/3
mag = np.sqrt(DR*DR + DG*DG + DB*DB)
e1 = np.array([1,-0.5,-0.5])/np.sqrt(1.5); e2 = np.array([0,1,-1])/np.sqrt(2)
u = DR*e1[0] + DG*e1[1] + DB*e1[2]
v = DR*e2[0] + DG*e2[1] + DB*e2[2]
ang = np.arctan2(v, u)

NOISE = 8e-12
LOGLO, LOGHI = -10.4, np.log10(0.9)
l = np.clip(np.log10(np.maximum(mag, 1e-15)), LOGLO, LOGHI)
Lbase = ((l - LOGLO)/(LOGHI - LOGLO))**1.75
# decade terracing: soft crest at each 1/3-decade line
tp = l*3.0
fpart = tp - np.floor(tp)
crest = np.exp(-((fpart-0.5)**2)/(2*0.10**2))
Lum = Lbase*(0.78 + 0.34*crest)
if ft is not None:
    w = (ft/np.nanmax(ft))**0.35
    Lum *= (0.78 + 0.30*w)
Lum[mag < NOISE] *= 0.25

# ---------------- palette ----------------
anch_ang = np.array([-2*np.pi/3, -np.pi/3, 0.0, np.pi/3, 2*np.pi/3, np.pi])
anch_col = np.array([
    [0.30, 0.58, 1.00],   # azure  (B)
    [0.72, 0.35, 0.95],   # violet (B->R)
    [1.00, 0.36, 0.16],   # ember  (R)
    [1.00, 0.80, 0.25],   # gold   (R->G)
    [0.30, 0.98, 0.48],   # jade   (G)
    [0.15, 0.85, 0.85],   # teal   (G->B)
])
def palette(a):
    a = (a + np.pi) % (2*np.pi) - np.pi
    seg = (a - (-2*np.pi/3)) / (np.pi/3)        # position in units of pi/3 from azure
    seg = (seg % 6.0)
    i0 = np.floor(seg).astype(int) % 6
    i1 = (i0 + 1) % 6
    t = seg - np.floor(seg)
    t = t*t*(3-2*t)
    return anch_col[i0]*(1-t)[:,None] + anch_col[i1]*t[:,None]
cols = palette(ang)
fade = np.clip((l - LOGLO)/(LOGHI - LOGLO), 0, 1)[:,None]
ash = np.array([0.42, 0.47, 0.55])
cols = cols*(0.25+0.75*fade) + ash*(1-fade)*0.28

buf = artlib.canvas(S)
rgb = cols * Lum[:,None]
flat = np.zeros((S*S, 3), np.float32)
flat[np.flatnonzero(inside.ravel())] = rgb
buf += flat.reshape(S, S, 3) * 0.85

# ---------------- nodal silk threads ----------------
full = np.zeros((3, S, S), np.float32)
for i, DD in enumerate((DR, DG, DB)):
    tmp = np.zeros(S*S, np.float32); tmp[np.flatnonzero(inside.ravel())] = DD
    full[i] = tmp.reshape(S, S)
magf = np.zeros(S*S, np.float32); magf[np.flatnonzero(inside.ravel())] = mag
magf = magf.reshape(S, S)
thread_cols = np.array([[1.0,0.55,0.35],[0.5,1.0,0.6],[0.45,0.7,1.0]])
ink = np.zeros((S, S, 3), np.float32)
for i in range(3):
    F = full[i]
    sx = (np.sign(F[:, :-1]) != np.sign(F[:, 1:])) & inside[:, :-1] & inside[:, 1:]
    sy = (np.sign(F[:-1, :]) != np.sign(F[1:, :])) & inside[:-1, :] & inside[1:, :]
    zc = np.zeros((S, S), bool)
    zc[:, :-1] |= sx; zc[:-1, :] |= sy
    zc &= magf > NOISE*3
    layer = zc.astype(np.float32)
    layer = gaussian_filter(layer, 0.7*max(rs,0.5))
    for c in range(3):
        ink[:,:,c] += layer * thread_cols[i][c]
buf += ink * (0.95 * (0.35+0.65*rs))

# ---------------- edge rims ----------------
# r=0 edge (vG..vB): blue wins -> azure; b=0 (vR..vG): green wins -> jade; g=0 (vR..vB): red wins -> ember
for (p0, p1, cc) in ((vG, vB, [0.30,0.58,1.00]), (vR, vG, [0.30,0.98,0.48]), (vR, vB, [1.00,0.36,0.16])):
    artlib.polyline(buf, np.vstack([p0, p1]), cc, amp=0.05*rs, step=0.6)

# still point: (M/3,M/3,M/3), perfect ignorance
ctr = (vR + vG + vB)/3.0
artlib.star(buf, ctr[0], ctr[1], [0.82,0.86,0.95], amp=1.4*rs*rs, rad=5.5*rs)

# ---------------- vertex stars ----------------
for vv, cc in ((vR,[1,0.42,0.2]),(vG,[0.32,1,0.5]),(vB,[0.35,0.62,1])):
    artlib.star(buf, vv[0], vv[1], cc, amp=5.0*rs*rs, rad=10*rs)

artlib.bloom(buf, sigmas=(2*max(rs,0.5), 8*rs, 26*rs), weights=(1.0, 0.32, 0.16))
img = artlib.tonemap(buf, k=1.25, gamma=0.92)
if SS > 1:
    from PIL import Image
    im = Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((SIZE,SIZE), Image.LANCZOS)
    img = np.asarray(im).astype(np.float32)/255.0
try:
    ann = open('hero_annotation.txt').read().strip().split('\n')
except FileNotFoundError:
    ann = []
if ann:
    F = SIZE
    texts = []
    y0 = F*0.878
    texts.append((F*0.5, y0, ann[0], int(F*0.021), (0.93,0.90,0.82), True, 'mm'))
    for i, line in enumerate(ann[1:]):
        texts.append((F*0.5, y0 + F*0.026 + i*F*0.0118, line, int(F*0.0078), (0.58,0.60,0.66), False, 'mm'))
    img = artlib.bake_text(img, texts, F)
artlib.save(img, OUT)
print("saved", OUT, flush=True)
