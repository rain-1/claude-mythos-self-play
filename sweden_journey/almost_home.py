"""Almost Home — the descent at dawn: a sea of clouds lit warm by a low sun,
breaking open over the lights of home, with the flight path coming down to meet
it. A bookend to 'The Long Way Home'.
"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
import vista as V

W = int(sys.argv[1]) if len(sys.argv)>1 else 2560
H = int(sys.argv[2]) if len(sys.argv)>2 else 1440
seed = int(sys.argv[3]) if len(sys.argv)>3 else 4
outp = sys.argv[4] if len(sys.argv)>4 else "almost_home.png"
rng = np.random.default_rng(seed)
yy, xx, ny, nx = V.grid(H, W)
img = np.zeros((H, W, 3))

# ---- dawn sky ----
sky = V.lerp_color(np.clip(ny/0.58,0,1), [
    (0.00, ( 26, 34, 78)),    # deep blue top
    (0.34, ( 58, 70,128)),
    (0.60, (150,120,150)),    # mauve
    (0.82, (240,168,128)),    # rose-gold
    (1.00, (255,206,150)),    # warm at the cloud horizon
])
img[:] = sky
# low sun
sx, sy = 0.70*W, 0.50*H
img += np.exp(-(((xx-sx)/(0.36*W))**2 + ((yy-sy)/(0.16*H))**2))[...,None]*np.array([1.0,0.84,0.6])*0.7
img += np.exp(-(((xx-sx)/(0.06*W))**2 + ((yy-sy)/(0.06*H))**2))[...,None]*np.array([1.0,0.95,0.82])*0.9
img = V.add_stars(img, H, W, ny, 140, seed+1, ymax=0.34, amp=0.35)

# ---- cloud sea (bumpy top below a horizon, lit from the sun side) ----
cb = 0.55                                   # cloud-top baseline
gx = 0.50                                    # where home glows through
bump = V.fbm((1, W), 90, 4, seed+2)[0]*0.085 + V.fbm((1,W),240,3,seed+8)[0]*0.04
ct = cb - bump                               # bumpy cloud-top per column

dens = V.fbm((H,W), 48, 5, seed+3, gain=0.56)        # large soft billows
fine = V.fbm((H,W), 16, 3, seed+13, gain=0.5)
puff = gaussian_filter(np.clip(0.80*dens + 0.20*fine, 0, 1), 1.5)
puff = puff**1.15
inside = ny >= ct[None,:]
# shading: lit from the sun, creases in soft shadow
gy_, gx_ = np.gradient(gaussian_filter(puff, 4.0))
ldx, ldy = (sx/W-0.5), (sy/H-0.5)
nrm = (ldx**2+ldy**2)**0.5; ldx/=nrm; ldy/=nrm
shade = np.clip(0.72 - (gx_*ldx + gy_*ldy)*W*0.013, 0.18, 1.4)
cd = np.clip((ny-cb)/(1-cb),0,1)
cloud_warm = V.lerp_color(1-cd, [(0.0,(118,124,158)),(0.45,(214,198,202)),(1.0,(255,234,208))])
cloud = cloud_warm*(0.42 + 0.85*puff[...,None]*shade[...,None])*(1.0-0.18*cd[...,None])
cloud += np.exp(-(((xx-sx)/(0.5*W))**2))[...,None]*np.array([1.0,0.8,0.55])*0.18*inside[...,None]
cloud += (np.clip(puff-0.72,0,1)**2)[...,None]*np.array([1.0,0.9,0.72])*0.5
img = np.where(inside[...,None], cloud, img)

# ---- home glowing UP through a thin patch in the cloud (soft, no hard edges) ----
gpy = (cb+0.16)*H
patch = np.exp(-(((xx-gx*W)/(0.085*W))**2 + ((yy-gpy)/(0.13*H))**2))   # soft warm bloom
img += patch[...,None]*np.array([1.0,0.62,0.34])*0.9
# city lights twinkling through the thin spot (veiled by cloud -> soft)
nc = 520
cxs = gx*W + rng.standard_normal(nc)*0.05*W
cys = gpy + rng.standard_normal(nc)*0.05*H
clitb = np.zeros((H,W))
for i in range(nc):
    xi, yi = int(cxs[i]), int(cys[i])
    if 0<=xi<W and 0<=yi<H:
        clitb[yi,xi] += 0.4 + rng.random()*1.0
veil = np.exp(-(((xx-gx*W)/(0.075*W))**2 + ((yy-gpy)/(0.11*H))**2))   # only show within the patch
clit = (gaussian_filter(clitb,0.6) + 0.5*gaussian_filter(clitb,2.6)) * (0.35+0.65*veil)
img += clit[...,None]*np.array([1.0,0.76,0.44])*0.9

# ---- descending flight arc toward home ----
P0 = np.array([W*0.06, H*0.20]); ctrl = np.array([W*0.34, H*0.30])
P1 = np.array([gx*W, (cb+0.08)*H])
t = np.linspace(0,1,3000)[:,None]
arc = (1-t)**2*P0 + 2*(1-t)*t*ctrl + t**2*P1
ab = np.zeros((H,W)); dl = np.cumsum(np.r_[0,np.hypot(np.diff(arc[:,0]),np.diff(arc[:,1]))])
db = np.zeros((H,W))
for i in range(arc.shape[0]):
    x,y=arc[i]; xi,yi=int(round(x)),int(round(y))
    if 0<=xi<W and 0<=yi<H:
        ab[yi,xi]+=1.0
        if int(dl[i]/20)%2==0: db[yi,xi]+=1.0
img += (gaussian_filter(ab,1.0)+0.6*gaussian_filter(ab,4.0)+0.3*gaussian_filter(ab,11.0))[...,None]*np.array([1.0,0.86,0.55])*0.5
img += gaussian_filter(db,0.6)[...,None]*np.array([1.0,0.96,0.85])*0.85
pi = int(0.93*(arc.shape[0]-1)); px,py = arc[pi]
img += V.glow_point(yy,xx, px,py, 0.011*H, (1,1,1), 1.4)
img += V.glow_point(yy,xx, px,py, 0.03*H, (1.0,0.9,0.7), 0.6)

# ---- bloom + tone ----
bright = np.clip(img.max(axis=2)-0.55,0,1)
img += V.bloom(bright,[(0.015*H,0.08),(0.05*H,0.04)])[...,None]*np.array([1.0,0.9,0.72])
img = V.tonemap(img, k=1.15, gamma=0.93)
pim = V.to_pil(img)
V.caption(pim, H, "ALMOST HOME", "the descent at dawn  ·  home through the clouds  ·  June 2026")
pim.save(outp); print("saved", outp, pim.size)
