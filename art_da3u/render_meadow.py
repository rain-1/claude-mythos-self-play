"""Hero: a meadow of pinwheels photographed by one rolling shutter (rows read top->bottom)."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from paint import SORBET, WHEEL, paint_pinwheel, paint_hub, smooth_cov
OUT = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = int(sys.argv[2]) if len(sys.argv) > 2 else 2
name = sys.argv[3] if len(sys.argv) > 3 else f'meadow_{OUT}.png'
W = H = OUT*SS
u = OUT/1024.0                                # design units: 1024-wide canvas
rng = np.random.default_rng(7)
y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
def lerp(a, b, t): return a + (b - a)*t
# --- sky: periwinkle-white top -> rose -> peach -> butter at the horizon
top = np.array([0.80, 0.86, 0.99]); mid = np.array([0.99, 0.88, 0.92]); low = np.array([1.0, 0.93, 0.80])
hz = 0.70
t1 = np.clip(y/0.45, 0, 1)[..., None]; t2 = np.clip((y - 0.45)/(hz - 0.45), 0, 1)[..., None]
img = np.where(y[..., None] < 0.45, lerp(top, mid, t1**1.2), lerp(mid, low, t2))
img = np.broadcast_to(img.astype(np.float32), (H, W, 3)).copy()
# soft clouds
cl = np.zeros((H, W), np.float32)
for cx, cy, sc in [(180, 170, 1.0), (760, 120, 1.3), (520, 300, 0.8), (930, 330, 0.7), (80, 380, 0.6)]:
    for _ in range(14):
        ox, oy, rr = rng.normal(0, 55*sc), rng.normal(0, 12*sc), rng.uniform(22, 48)*sc
        x0, x1 = max(0, int((cx + ox - 4*rr)*u*SS)), min(W, int((cx + ox + 4*rr)*u*SS))
        y0, y1 = max(0, int((cy + oy - 3*rr)*u*SS)), min(H, int((cy + oy + 3*rr)*u*SS))
        Xl = (np.arange(x0, x1, dtype=np.float32)/(u*SS))[None, :]; Yl = (np.arange(y0, y1, dtype=np.float32)/(u*SS))[:, None]
        cl[y0:y1, x0:x1] += np.exp(-(((Xl - cx - ox)/rr)**2 + ((Yl - cy - oy)/(rr*0.62))**2))
cl = 1 - np.exp(-1.6*cl)
img = img*(1 - 0.75*cl[..., None]) + 0.75*cl[..., None]*np.array([1.0, 0.995, 0.99], np.float32)
del cl
# --- hills (back to front), each carrying its own pinwheels
def hill(base, amp, ph, f):
    xx = np.linspace(0, 1, W)
    return (base + amp*(0.55*np.sin(2*np.pi*(f*xx + ph)) + 0.3*np.sin(2*np.pi*(2.3*f*xx + 1.7*ph)) + 0.15*np.sin(2*np.pi*(5.1*f*xx + 0.3))))
hills = [(0.705, 0.018, 0.2, 0.9, np.array([0.80, 0.85, 0.97]), np.array([0.86, 0.90, 0.98]), 0.45),
         (0.745, 0.026, 0.55, 0.7, np.array([0.72, 0.90, 0.88]), np.array([0.82, 0.94, 0.90]), 0.30),
         (0.795, 0.032, 0.05, 0.6, np.array([0.72, 0.92, 0.74]), np.array([0.84, 0.96, 0.80]), 0.15),
         (0.835, 0.03, 0.8, 0.5, np.array([0.78, 0.94, 0.64]), np.array([0.90, 0.98, 0.74]), 0.0)]
pal = {'wheel': ['strawberry', 'peach', 'butter', 'mint', 'sky', 'lilac', 'bubblegum'],
       'wheel2': ['coral', 'butter', 'lime', 'sky', 'periwinkle', 'bubblegum', 'peach'],
       'wheel3': ['mint', 'sky', 'periwinkle', 'lilac', 'bubblegum', 'strawberry', 'peach']}
# (x, stick height above crest (design px), R, N, k, phase, palette) per hill layer
LAY = [
 [(70, 34, 13, 6, 40.0, 0.3, 'wheel'), (190, 40, 15, 5, 3.0, 1.1, 'wheel2'), (330, 30, 12, 7, 60.0, 0.5, 'wheel3'),
  (470, 38, 14, 6, 0.5, 2.0, 'wheel'), (585, 34, 13, 5, 25.0, 0.9, 'wheel2'), (800, 36, 14, 6, 12.0, 0.0, 'wheel3'), (950, 30, 12, 7, 80.0, 1.3, 'wheel')],
 [(120, 70, 27, 5, 18.0, 0.4, 'wheel3'), (395, 80, 30, 6, 1.2, 1.7, 'wheel'), (880, 74, 29, 7, 8.0, 0.2, 'wheel2'), (1000, 60, 24, 5, 35.0, 2.0, 'wheel')],
 [(70, 120, 50, 6, 0.6, 2.4, 'wheel3'), (918, 170, 98, 7, 6.5, 0.7, 'wheel3')],
 [(250, 300, 128, 5, 0.12, 0.9, 'wheel2'), (590, 430, 262, 6, 1.45, 0.25, 'wheel')],
]
skyc = np.array([0.93, 0.92, 0.97])
def region(x0, x1, y0, y1):
    x0, x1 = max(0, int(x0)), min(W, int(x1)); y0, y1 = max(0, int(y0)), min(H, int(y1))
    Y, X = np.mgrid[y0:y1, x0:x1].astype(float)
    return img[y0:y1, x0:x1], X, Y
def stick(cx, cy, R, bottom, fade):
    w = max(1.6, R*0.05)*u*SS
    sub, X, Y = region(cx*u*SS - w - 4, cx*u*SS + w + 4, cy*u*SS, bottom*u*SS)
    d = w - np.abs(X - cx*u*SS)
    a = np.clip(d + 0.5, 0, 1)
    stripe = ((Y + (X - cx*u*SS))/(w*3.2)) % 1.0 < 0.5
    col = np.where(stripe[..., None], np.array([1.0, 0.99, 0.97]), SORBET['strawberry']*0.3 + 0.7)
    sh = (0.80 + 0.2*np.cos(np.clip((X - cx*u*SS)/w, -1, 1)*1.3))[..., None]
    col = col*sh*(1 - fade) + skyc*fade
    sub[:] = sub*(1 - a[..., None]) + col*a[..., None]
def pinwheel(cx, cy, R, N, k, ph, pn, fade):
    Rp = R*u*SS
    sub, X, Y = region(cx*u*SS - Rp - 8, cx*u*SS + Rp + 8, cy*u*SS - Rp - 8, cy*u*SS + Rp + 8)
    cols = [SORBET[pal[pn][i % 7]]*(1 - fade) + skyc*fade for i in range(N)]
    ink = max(0.9, 1.5*u*SS*min(1, R/60))
    paint_pinwheel(sub, X, Y, cx*u*SS, cy*u*SS, Rp, N, k, H, cols, phase=ph, ink=ink)
    paint_hub(sub, X, Y, cx*u*SS, cy*u*SS, Rp*0.075, SORBET['butter']*(1 - fade) + skyc*fade, ink=ink)
    if 2*np.pi*k*R/1024 > 1 and R > 200:                      # the ignition circle e = 1:  r* = H/(2 pi k)
        rs = 1024/(2*np.pi*k)*u*SS
        r = np.hypot(X - cx*u*SS, Y - cy*u*SS); ang = np.arctan2(Y - cy*u*SS, X - cx*u*SS)
        dash = np.clip((np.sin(ang*36) + 0.25)*3, 0, 1)
        a = np.clip(1 - np.abs(r - rs)/(1.6*u*SS), 0, 1)*dash
        sub[:] = sub*(1 - 0.9*a[..., None]) + SORBET['coral']*0.9*a[..., None]
Yp = np.arange(H, dtype=np.float32)[:, None]
for (base, amp, ph, f, c0, c1, fade), lay in zip(hills, LAY):
    ht = hill(base, amp, ph, f)*H
    d = Yp - ht[None, :]
    a = np.clip(d + 0.5, 0, 1)
    tt = np.clip(d/(0.25*H), 0, 1)[..., None]
    col = lerp(c1.astype(np.float32), c0.astype(np.float32), tt**0.7) + 0.05*np.exp(-np.maximum(d, 0)/(5*u*SS))[..., None]
    img *= (1 - a[..., None]); img += np.clip(col, 0, 1)*a[..., None]
    del d, a, tt, col
    for (x, hgt, R, N, k, phs, pn) in sorted(lay, key=lambda p: p[2]):
        crest = ht[min(W - 1, int(x*u*SS))]/(u*SS)
        foot = crest + (8 if fade > 0 else 1024 - crest)
        stick(x, crest - hgt, R, foot, fade)
        pinwheel(x, crest - hgt, R, N, k, phs, pn, fade)
# tiny meadow flowers on the front hill, denser and larger toward the viewer
ht = hill(*hills[-1][:4])
for i in range(260):
    fx = rng.uniform(0, 1024); q = rng.uniform(0, 1)**0.8
    crest = ht[min(W - 1, int(fx*u*SS))]*1024
    fy = crest + 10 + (1024 - crest - 10)*q
    if fy > 918: continue
    rr = (1.1 + 2.6*((fy - crest)/(918 - crest)))*u*SS
    sub, X, Y = region(fx*u*SS - rr*3, fx*u*SS + rr*3, fy*u*SS - rr*3, fy*u*SS + rr*3)
    c = SORBET[['bubblegum', 'butter', 'sky', 'lilac', 'peach', 'strawberry'][i % 6]]
    for qq in range(5):
        a0 = 2*np.pi*qq/5 + fx
        px, py = fx*u*SS + rr*np.cos(a0), fy*u*SS + rr*0.8*np.sin(a0)
        d = rr*0.8 - np.hypot(X - px, (Y - py)/0.8)
        a = np.clip(d + 0.5, 0, 1)[..., None]
        sub[:] = sub*(1 - a) + (c*0.8 + 0.2)*a
    d = rr*0.5 - np.hypot(X - fx*u*SS, Y - fy*u*SS)
    a = np.clip(d + 0.5, 0, 1)[..., None]
    sub[:] = sub*(1 - a) + np.array([1, 0.96, 0.75])*a
# morning mist at the foot of the meadow: the caption band
yy = np.linspace(0, 1024, H, dtype=np.float32)[:, None, None]
m = np.clip((yy - 880)/70, 0, 1); m = m*m*(3 - 2*m)
img *= (1 - 0.86*m); img += 0.86*m*np.array([0.985, 0.985, 0.975], np.float32)
im = Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8))
if SS > 1: im = im.resize((OUT, OUT), Image.LANCZOS)
from paint import caption
caption(im, 34*u, 940*u, [('The Meadow, Read Top to Bottom', 'b', 30),
   ('one rolling shutter reads row y at time y/H, so every blade obeys Kepler\'s equation  \u03c6 \u2212 e sin \u03c6 = M,  e = 2\u03c0kr/H', 'i', 15.5),
   ('coral dashes: the ignition circle e = 1.  Inside it every blade is still one blade; outside, the motion keeps its own time.', 'i', 15.5)], scale=u)
im.save(name)
print('saved', name)
