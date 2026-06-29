"""Midnight Sun, Archipelago — the low golden sun over the Stockholm skargard:
calm Baltic water with a shimmering sun-glitter path, low island silhouettes
with a pine tree-line, a Falu-red cottage, under the pale midsummer-night sky.
"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
import vista as V

W = int(sys.argv[1]) if len(sys.argv)>1 else 2560
H = int(sys.argv[2]) if len(sys.argv)>2 else 1440
seed = int(sys.argv[3]) if len(sys.argv)>3 else 3
outp = sys.argv[4] if len(sys.argv)>4 else "midnight_sun.png"
rng = np.random.default_rng(seed)
yy, xx, ny, nx = V.grid(H, W)
img = np.zeros((H, W, 3))
hy = 0.60                      # horizon (fraction)
sun_x, sun_y = 0.63*W, (hy-0.035)*H
sun_r = 0.030*H

# ---- sky ----
sky_t = np.clip(ny/hy, 0, 1)
sky = V.lerp_color(sky_t, [
    (0.00, ( 58, 72,128)),    # lavender-blue zenith
    (0.40, (120,112,156)),    # mauve
    (0.68, (224,150,140)),    # warm rose
    (0.86, (255,188,132)),    # peach
    (1.00, (255,224,168)),    # gold at the waterline
])
img[ny < hy] = sky[ny < hy]

# sun + glow (sky side)
sun_d = np.sqrt((xx-sun_x)**2 + (yy-sun_y)**2)
glow = np.exp(-(sun_d/(0.30*H))**2)*0.55 + np.exp(-(sun_d/(0.10*H))**2)*0.8
disc = np.clip(1-(sun_d/sun_r), 0, 1)
sky_mask = (ny < hy)[...,None]
img += (glow[...,None]*np.array([1.0,0.86,0.6]))*sky_mask
img += disc[...,None]*np.array([1.0,0.96,0.85])

# ---- water (below horizon): reflected sky + ripples + sun glitter ----
wt = np.clip((ny-hy)/(1-hy), 0, 1)                     # 0 at horizon, 1 bottom
water = V.lerp_color(wt, [
    (0.00, (240,200,150)),    # warm reflection at horizon
    (0.18, (150,120,140)),
    (0.45, ( 56, 70,110)),
    (1.00, ( 18, 30, 58)),
])
# horizontal ripple shimmer, stronger far (near horizon)
ripple = (0.5+0.5*np.sin(yy*0.25 + V.vnoise((H,W),3,seed+1)*12))
ripple = 1 + 0.18*ripple*np.clip((0.5-wt),0,1)
water *= ripple[...,None]
# sun glitter column under the sun
gw = (0.012 + 0.10*wt)*W
glit = np.exp(-((xx-sun_x)/gw)**2)
shim = np.clip(V.vnoise((H,W),(1.2,6),seed+2)-0.45,0,1)*np.clip((0.6+0.4*np.sin(yy*0.6)),0,1)
glitter = glit*shim* (0.6+0.6*np.clip(1-wt,0,1))
water_mask = (ny>=hy)[...,None]
img = np.where(water_mask, water, img)
img += (glitter[...,None]*np.array([1.0,0.85,0.55])*1.3)*water_mask

# ---- islands (low silhouettes with pine tree-line) ----
def island(x0, x1, peak, treeh, base_col, s):
    span = (xx>=x0*W)&(xx<=x1*W)
    u = np.clip((xx-x0*W)/((x1-x0)*W), 0, 1)
    hump = np.sin(np.pi*np.clip(u,0,1))**0.7
    # pine tree-line: jagged high-freq subtracted from the top
    tline = V.noise1d(W, 1.2, s)[np.clip(xx.astype(int),0,W-1)]
    spikes = (V.noise1d(W, 0.6, s+1)[np.clip(xx.astype(int),0,W-1)]>0.55)*1.0
    top = hy - (peak*hump) + (0.5-tline)*treeh*0.5 - spikes*treeh*hump*0.5
    land = span & (ny>=top) & (ny<hy)
    img[land] = np.array(base_col)/255
    # reflection in water (dim, mirrored about horizon, slight blur via ripple)
    refl_top = hy + (hy-top)
    rmask = span & (ny>=hy) & (ny<=refl_top) & (ny<hy+0.10)
    img[rmask] = (np.array(base_col)/255)*0.5 + img[rmask]*0.5
    return top
top = island(0.02, 0.34, 0.060, 0.030, (24,30,34), seed+10)
island(0.40, 0.72, 0.040, 0.022, (20,26,30), seed+20)
island(0.78, 1.02, 0.085, 0.038, (16,22,26), seed+30)

# Falu-red cottage glow on the left island
cx_c, cy_c = 0.20*W, (hy-0.028)*H
img += V.glow_point(yy,xx, cx_c, cy_c, 0.006*H, (0.85,0.18,0.12), 1.1)
img += V.glow_point(yy,xx, cx_c+6, cy_c-3, 0.0018*H, (1.0,0.85,0.55), 1.3)  # lit window
# its reflection
img += V.glow_point(yy,xx, cx_c, hy*H+(hy*H-cy_c)+8, 0.006*H, (0.7,0.16,0.10), 0.5)

# ---- a few high pale stars (midsummer night barely shows them) ----
img = V.add_stars(img, H, W, ny, 120, seed+5, ymax=0.42, amp=0.4)

# ---- bloom + tone ----
bright = np.clip(img.max(axis=2)-0.5,0,1)
img += V.bloom(bright,[ (0.01*H,0.10),(0.04*H,0.05) ])[...,None]*np.array([1.0,0.9,0.7])
img = V.tonemap(img, k=1.15, gamma=0.94)
pim = V.to_pil(img)
V.caption(pim, H, "MIDNIGHT SUN", "the archipelago at midnight  ·  midsommar  ·  Sverige 2026")
pim.save(outp); print("saved", outp, pim.size)
