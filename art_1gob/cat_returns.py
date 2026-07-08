"""Piece II — The Cat That Returns.
Arnold's cat map (x,y) -> (x+y, x+2y) mod N on a 512^2 pixel torus is a
permutation of finite order: 384 for N=512.  The seed image scrambles into
apparent noise, throws up phantom-lattice resurrections whenever A^t ≡ I
(mod a divisor of N), and at t=384 returns EXACTLY.  Apparent forgetting;
arithmetic memory.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
from kit import filmic, bloom, save

N = 512
A = np.array([[1,1],[1,2]])

# ---------- order + interesting times ----------
def matpow_mod(t):
    M = np.eye(2, dtype=np.int64); B = A.astype(np.int64).copy(); e = t
    while e:
        if e & 1: M = (M @ B) % N
        B = (B @ B) % N; e >>= 1
    return M
order = 1
M = A % N
while not (M == np.eye(2, dtype=np.int64)).all():
    M = (M @ A) % N; order += 1
print("order of A mod", N, "=", order)
assert (matpow_mod(order) == np.eye(2, dtype=np.int64)).all()

# ---------- seed glyph ----------
def seed_glyph():
    Y, X = np.mgrid[0:N,0:N].astype(np.float32)
    img = np.zeros((N,N,3), np.float32)
    img += np.array([0.030,0.033,0.055])[None,None,:]
    cx, cy = 265, 245
    r = np.hypot(X-cx, Y-cy)
    disc = np.clip(1-(r/150)**2, 0, 1)**0.8
    bite = np.clip(1-(np.hypot(X-cx-62, Y-cy-46)/150)**2, 0, 1)**0.8
    crescent = np.clip(disc-1.15*bite, 0, 1)
    img += np.array([1.00,0.72,0.28])[None,None,:]*crescent[...,None]*1.15
    ring = np.exp(-0.5*((r-198)/5.0)**2)
    img += np.array([0.25,0.75,0.72])[None,None,:]*ring[...,None]*0.9
    star = 1.3*np.exp(-((X-352)**2+(Y-150)**2)/(2*7**2)) \
         + 0.5*np.exp(-((X-352)**2+(Y-150)**2)/(2*20**2))
    img += np.array([1.0,0.92,0.75])[None,None,:]*star[...,None]
    dot = np.exp(-((X-150)**2+(Y-368)**2)/(2*10**2))
    img += np.array([0.85,0.30,0.25])[None,None,:]*dot[...,None]*0.9
    return np.clip(img, 0, 1)
seed = seed_glyph()

# ---------- iterate: frame at time t via coordinate transform ----------
ys, xs = np.mgrid[0:N,0:N]
def frame(t):
    M = matpow_mod(t)
    # forward map phi(v)=Av; image_t(v) = seed(A^{-t} v) -> equivalently
    # image_t(A^t u) = seed(u); build by scatter = gather with inverse power
    Minv = matpow_mod(order - (t % order)) if t % order else np.eye(2,dtype=np.int64)
    u = (Minv @ np.stack([xs.ravel(), ys.ravel()])) % N
    return seed[u[1], u[0]].reshape(N,N,3)

L0 = seed.mean(2); L0z = L0 - L0.mean()
den = (L0z*L0z).sum()
corr = np.zeros(order+1)
for t in range(order+1):
    Lt = frame(t).mean(2)
    corr[t] = (((Lt-Lt.mean())*L0z).sum())/den
top = np.argsort(corr[1:order])[::-1][:14]+1
print("top correlation times:", sorted(top.tolist()), corr[sorted(top.tolist())].round(3))
np.save('proto/cat_corr.npy', corr)

# frames to show (chronology of forgetting and return)
# verify the phantom mechanism (von Dyck discipline)
def matpow_mod_m(t, m):
    M = np.eye(2, dtype=np.int64); B = A.astype(np.int64) % m; e = t
    while e:
        if e & 1: M = (M @ B) % m
        B = (B @ B) % m; e >>= 1
    return M
for tt, mm in ((24,32),(48,64),(96,128),(192,256)):
    assert (matpow_mod_m(tt, mm) == np.eye(2,dtype=np.int64)).all(), f"A^{tt} != I mod {mm}"
print("verified phantom ladder: A^24=I(32) A^48=I(64) A^96=I(128) A^192=I(256)")
TIMES = [0, 1, 2, 3, 6, 24, 48, 96, 192, 288, 383, 384]
print("display times:", TIMES, "corr:", corr[TIMES].round(3))

# ---------- layout ----------
Sc = 2560
COLS, ROWS = 4, 3
TS = 512
MX = (Sc - COLS*TS)//(COLS+1)     # h margin
top0 = 170
MY = 76
canvas = np.zeros((Sc, Sc, 3), np.float32)
yy = np.linspace(0,1,Sc)[:,None]
for c,v in enumerate((0.024,0.026,0.045)): canvas[...,c] = v*(0.7+0.3*yy)

tiles_pos = []
for i,t in enumerate(TIMES):
    rr, cc = divmod(i, COLS)
    y0 = top0 + rr*(TS+MY+34)
    x0 = MX + cc*(TS+MX)
    f = frame(t)
    canvas[y0:y0+TS, x0:x0+TS] = f
    tiles_pos.append((t, x0, y0))
    # border glow ∝ correlation
    cval = corr[t]
    bcol = np.array([1.0,0.75,0.32])*max(cval,0.06) + np.array([0.25,0.35,0.5])*0.25
    bw = 3
    canvas[y0-bw:y0, x0-bw:x0+TS+bw] += bcol*0.8
    canvas[y0+TS:y0+TS+bw, x0-bw:x0+TS+bw] += bcol*0.8
    canvas[y0-bw:y0+TS+bw, x0-bw:x0] += bcol*0.8
    canvas[y0-bw:y0+TS+bw, x0+TS:x0+TS+bw] += bcol*0.8

# ---------- sparkline: the resurrection comb ----------
sy0 = top0 + 3*(TS+MY+34) + 26
sh  = 240
sx0, sx1 = MX, Sc-MX
ts_ = np.arange(order+1)
px = sx0 + (sx1-sx0)*ts_/order
cl = np.clip(corr, 0, 1)**0.35
comb = np.zeros((Sc, Sc), np.float32)
for t in range(order+1):
    xpx = int(px[t]); h = int(cl[t]*sh)
    if h > 0: comb[sy0+sh-h:sy0+sh, xpx] += 1.0
comb = gaussian_filter(comb, 1.2)
canvas += np.array([0.95,0.70,0.30])[None,None,:]*np.minimum(comb,1.4)[...,None]*1.5
# baseline
canvas[sy0+sh:sy0+sh+2, sx0:sx1] += np.array([0.4,0.5,0.6])*0.5
# markers under displayed times
for t,_,_ in tiles_pos:
    xpx = int(sx0+(sx1-sx0)*t/order)
    canvas[sy0+sh+6:sy0+sh+18, xpx-1:xpx+2] += np.array([0.3,0.8,0.75])*0.9

img = Image.fromarray((np.clip(filmic(bloom(canvas, 0.75, 5, 0.4), 1.35, 0.92),0,1)*255+0.5).astype(np.uint8))
# ---------- text ----------
d = ImageDraw.Draw(img)
f_big  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 44)
f_med  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 30)
f_sml  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 24)
GOLD=(232,196,120); GREY=(120,135,160); TEAL=(96,190,180)
d.text((MX, 42), "THE CAT THAT RETURNS", font=f_big, fill=GOLD)
d.text((MX, 100), "x ↦ Ax (mod 512),  A = [[1,1],[1,2]]   —   A^384 ≡ I : every scramble is a promise", font=f_sml, fill=GREY)
for t,x0,y0 in tiles_pos:
    lab = f"t = {t}"
    if t == 384: lab = "t = 384 = 0"
    d.text((x0+2, y0+TS+8), lab, font=f_med, fill=GOLD if corr[t]>0.5 else GREY)
d.text((sx0, sy0+sh+28), "correlation with the seed, t = 0 … 384", font=f_sml, fill=GREY)
d.text((sx0, sy0+sh+64), "phantom ladder: A^24 ≡ I (mod 32) · A^48 ≡ I (mod 64) · A^96 ≡ I (mod 128) · A^192 ≡ I (mod 256) — the lattice remembers in layers", font=f_sml, fill=TEAL)
img.save('proto/II_cat_proto.png', optimize=True)
print("saved proto/II_cat_proto.png", img.size)
