"""Stillness — a Swedish forest lake at dawn: a dense spruce treeline mirrored
in a glass-calm lake, low mist over the water, pale dawn sky.
"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
import vista as V

W = int(sys.argv[1]) if len(sys.argv)>1 else 2560
H = int(sys.argv[2]) if len(sys.argv)>2 else 1440
seed = int(sys.argv[3]) if len(sys.argv)>3 else 5
outp = sys.argv[4] if len(sys.argv)>4 else "forest_lake.png"
rng = np.random.default_rng(seed)
yy, xx, ny, nx = V.grid(H, W)
img = np.zeros((H, W, 3))
hy = 0.50                       # waterline

# ---- sky (pale Nordic dawn) ----
sky_t = np.clip(ny/hy, 0, 1)
sky = V.lerp_color(sky_t, [
    (0.00, ( 92,116,156)),    # cool blue
    (0.45, (168,176,196)),    # pale grey-blue
    (0.74, (226,206,200)),    # cream
    (1.00, (244,214,186)),    # warm rose at the treeline
])
img[:] = sky
# soft low sun glow behind the trees
sgx, sgy = 0.40*W, hy*H
img += np.exp(-(((xx-sgx)/(0.34*W))**2 + ((yy-sgy)/(0.12*H))**2))[...,None]*np.array([1.0,0.85,0.66])*0.45

# ---- spruce treeline silhouette ----
base = hy
top = np.full(W, base)
xcoord = np.arange(W)
ntrees = 520
for _ in range(ntrees):
    c = rng.integers(-20, W+20)
    h = (0.03 + 0.085*rng.random()**1.6)        # tree height (fraction)
    wdt = (0.004 + 0.012*rng.random())*W
    cont = base - h*np.clip(1 - np.abs(xcoord-c)/wdt, 0, 1)
    top = np.minimum(top, cont)
# back haze band of distant forest (lower, softer)
backhaze = base - (0.02 + 0.01*V.noise1d(W, 8, seed+9))
top = np.minimum(top, backhaze)
top_px = (top*H)
forest_col = np.array([14, 26, 24])/255
forest_mask = (ny >= top_px[None,:]/H) & (ny < hy)
# slight tonal variation in the forest (depth)
fvar = 0.7 + 0.5*V.vnoise((H,W),(6,3),seed+3)
img[forest_mask] = (forest_col*fvar[...,None])[forest_mask]

# ---- reflection (mirror sky+forest about waterline, dim + ripple) ----
img_up = img.copy()
ripple_amp = (8.0*(W/2560))
disp = (ripple_amp*np.sin(yy*0.18 + V.vnoise((H,W),(2,2),seed+4)*9)
        * np.clip((ny-hy)/(1-hy),0,1))
src_y = np.clip((2*hy*H - yy).astype(int), 0, H-1)
src_x = np.clip((xx + disp).astype(int), 0, W-1)
refl = img_up[src_y, src_x]
# dim & cool the reflection, fade to dark deep water
depth = np.clip((ny-hy)/(1-hy),0,1)
refl = refl*(0.62 - 0.30*depth)[...,None] + np.array([10,16,30])/255*(0.4*depth)[...,None]
water_mask = (ny>=hy)
img[water_mask] = refl[water_mask]

# ---- mist over the water + at the treeline ----
mist = np.exp(-((ny-hy)/0.018)**2)                       # tight band at waterline
mist += 0.5*np.exp(-((ny-(hy-0.01))/0.05)**2)*V.fbm((H,W),40,3,seed+6)
mist = mist*(0.5+0.6*V.fbm((H,W),90,3,seed+7))
img += np.clip(mist,0,1)[...,None]*np.array([0.86,0.84,0.86])*0.55

# faint reflected sun shimmer on the water under the glow
img += (np.exp(-((xx-sgx)/(0.16*W))**2)*np.clip(depth,0,1)*np.exp(-depth*2.2))[...,None]\
       *np.array([1.0,0.85,0.7])*0.35

# ---- bloom + tone ----
bright = np.clip(img.max(axis=2)-0.6,0,1)
img += V.bloom(bright,[(0.02*H,0.06)])[...,None]*np.array([1.0,0.92,0.8])
img = V.tonemap(img, k=1.12, gamma=0.95)
pim = V.to_pil(img)
V.caption(pim, H, "STILLNESS", "a forest lake at dawn  ·  spegelblankt  ·  Sverige 2026")
pim.save(outp); print("saved", outp, pim.size)
