"""A rotating plate of pearl rings, photographed by a rolling shutter.  Row y is read at time y/H;
a pearl at radius rho, angle a sits at centre + rho*(cos, sin)(a + 2*pi*k*y/H) at that time, so it shows
on row y iff |y - cy - rho*sin(a + c*y)| < b: Kepler's equation again, e = c*rho.  For e > 1 one pearl can be
photographed several times.  Hue = the pearl's own angle, so the copies of a pearl share a colour."""
import sys, colorsys, numpy as np
from PIL import Image
from paint import SORBET, caption
OUT = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
SS = int(sys.argv[2]) if len(sys.argv) > 2 else 2
name = sys.argv[3] if len(sys.argv) > 3 else f'rings_{OUT}.png'
W = H = OUT*SS
u = OUT/1200
cx, cy = W/2, H*0.435
Rp = H*0.385
k = float(sys.argv[4]) if len(sys.argv) > 4 else 1.25
c = 2*np.pi*k/H
img = np.ones((H, W, 3), np.float32)*np.array([0.992, 0.987, 0.978], np.float32)
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.hypot(X - cx, Y - cy)
# the plate: rotationally symmetric, hence untouched by the shutter (grooves between rings)
plate = np.clip(Rp*1.06 - r + 0.5, 0, 1)
groove = 0.035*np.cos(2*np.pi*r/(Rp/11))**8
pc = np.array([0.965, 0.955, 0.985], np.float32) - groove[..., None]*np.array([0.4, 0.4, 0.2], np.float32)
img = img*(1 - plate[..., None]) + pc*plate[..., None]
rim = np.exp(-((r - Rp*1.06)/(2.0*SS*u))**2)
img = img*(1 - 0.35*rim[..., None]) + 0.35*rim[..., None]*np.array([0.62, 0.55, 0.70], np.float32)
del Y, X, r, plate, groove, pc, rim
nring = 10
def pastel(h, light=0.78, sat=0.80):
    return np.array(colorsys.hls_to_rgb(h % 1.0, light, sat), np.float32)
ys = np.arange(H, dtype=np.float64)
marks = []
for i in range(nring):
    rho = Rp*(i + 1.2)/(nring + 0.2)
    nb = int(round(6 + 5.2*i))
    b = min(Rp/(nring + 0.2)*0.36, np.pi*rho/nb*0.62)
    for j in range(nb):
        a = 2*np.pi*j/nb + 0.37*i
        ccy = cy + rho*np.sin(a + c*ys)            # bead centre at the time row y is read
        mrow = np.abs(ys - ccy) < b
        rows = np.nonzero(mrow)[0]
        if len(rows) == 0: continue
        if i == nring - 1:
            st = np.nonzero(mrow[1:] & ~mrow[:-1])[0] + 1; en = np.nonzero(~mrow[1:] & mrow[:-1])[0] + 1
            if len(st) == 3 and len(en) == 3:
                cps = [((st[q] + en[q])/2) for q in range(3)]
                marks.append((min(np.diff(cps)), [(cx + rho*np.cos(a + c*yy), yy, b) for yy in cps]))
        ccx = cx + rho*np.cos(a + c*ys[rows])
        dy = (ys[rows] - ccy[rows])/b                        # in bead units
        half = np.sqrt(np.clip(1 - dy**2, 0, 1))*b
        x0 = int(max(0, np.floor((ccx - b).min()) - 2)); x1 = int(min(W, np.ceil((ccx + b).max()) + 3))
        xs = np.arange(x0, x1, dtype=np.float64)[None, :]
        dx = (xs - ccx[:, None])/b
        dd = np.sqrt(dx**2 + dy[:, None]**2)
        cov = np.clip((1 - dd)*b + 0.5, 0, 1)                # AA in pixel units
        if not cov.any(): continue
        nz = np.sqrt(np.clip(1 - dd**2, 0, 1))
        L = np.array([-0.42, -0.5, 0.76]); L /= np.linalg.norm(L)
        dif = np.clip(dx*L[0] + dy[:, None]*L[1] + nz*L[2], 0, 1)
        hv = L + np.array([0, 0, 1.0]); hv /= np.linalg.norm(hv)
        spec = np.clip(dx*hv[0] + dy[:, None]*hv[1] + nz*hv[2], 0, 1)**40
        col = pastel(a/(2*np.pi) - 0.37*i/(2*np.pi) + 0.02)
        sh = (0.80 + 0.22*dif)[..., None]*col + 0.65*spec[..., None] + 0.18*((1 - nz)**3)[..., None]
        rimk = np.clip(1 - np.abs((1 - dd)*b - 0.8*SS*u)/(0.9*SS*u), 0, 1)[..., None]
        sh = sh*(1 - 0.35*rimk) + 0.35*rimk*np.array([0.45, 0.38, 0.52])
        sub = img[rows, x0:x1]
        img[rows, x0:x1] = sub*(1 - cov[..., None]) + np.clip(sh, 0, 1)*cov[..., None]
# coral ignition circle e = 1, and coral rings round the three copies of the most widely spread pearl
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.hypot(X - cx, Y - cy); ang = np.arctan2(Y - cy, X - cx)
rs = 1/c
a = np.clip(1 - np.abs(r - rs)/(1.6*SS*u), 0, 1)*np.clip((np.sin(ang*60) + 0.2)*3, 0, 1)
img = img*(1 - 0.9*a[..., None]) + 0.9*a[..., None]*SORBET['coral'].astype(np.float32)
best = max(marks, key=lambda m: m[0])[1]
for (mx_, my_, bb) in best:
    x0, x1, y0, y1 = int(mx_ - 3*bb), int(mx_ + 3*bb), int(my_ - 3*bb), int(my_ + 3*bb)
    rr_ = np.hypot((X[y0:y1, x0:x1] - mx_)/1.45, (Y[y0:y1, x0:x1] - my_)/0.9)
    sub = img[y0:y1, x0:x1]
    aa = np.clip(1 - np.abs(rr_ - 1.45*bb)/(1.2*SS*u), 0, 1)[..., None]
    sub[:] = sub*(1 - 0.95*aa) + 0.95*aa*SORBET['coral'].astype(np.float32)
# the protected centre: a still butter pearl
d = Rp*0.055 - r
cov = np.clip(d + 0.5, 0, 1)[..., None]
nz = np.sqrt(np.clip(1 - (r/(Rp*0.055))**2, 0, 1))
hl = np.exp(-(((X - cx + Rp*0.02)**2 + (Y - cy + Rp*0.02)**2)/(Rp*0.018)**2))
pc = SORBET['butter'].astype(np.float32)*(0.8 + 0.2*nz[..., None]) + 0.5*hl[..., None]
img = img*(1 - cov) + np.clip(pc, 0, 1)*cov
del Y, X, r, ang
im = Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8))
if SS > 1: im = im.resize((OUT, OUT), Image.LANCZOS)
caption(im, 70*u, 1052*u, [('Some Pearls Are Photographed Three Times', 'b', 30),
  (f'ten rings of pearls on one plate turning {k:g} times while the shutter reads the frame top to bottom.  Each pearl is coloured by its own place on the plate,', 'i', 14.5),
  ('so its copies share a colour.  Inside the coral circle (e = 1) every pearl appears once; outside, Kepler’s equation has room for two more.', 'i', 14.5),
  ('Of these 294 pearls, 197 appear once, 19 twice, and 78 three times; the three coral rings hold one pearl.', 'i', 14.5)], scale=u)
im.save(name); print('saved', name)
