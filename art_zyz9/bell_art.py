"""THE CAGE OF CORRELATIONS - CHSH plane (S, S'), square in circle in diamond."""
import numpy as np, sys, time
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from artkit import filmic, to_img, wide_bloom, hist_eq

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
SS = 2 if FINAL >= 2048 else 1
S = FINAL * SS
rs = S / 2560.0
rng = np.random.default_rng(2882)
LIM = 4.42
NSAMP = int(6e8) if FINAL >= 2048 else int(8e7)

t0 = time.time()
SF = S//2                     # fog grid at half res, upsampled later
def to_px(u): return (u + LIM)/(2*LIM)*SF

# ---------- quantum fog: singlet, uniform planar measurement angles ----------
histQ = np.zeros((SF, SF), np.float64)
CH = int(2e7)
done = 0
while done < NSAMP:
    n = min(CH, NSAMP-done); done += n
    a1, a2, b1, b2 = rng.uniform(0, 2*np.pi, (4, n))
    E11 = -np.cos(a1-b1); E12 = -np.cos(a1-b2); E21 = -np.cos(a2-b1); E22 = -np.cos(a2-b2)
    Sv  = E11+E12+E21-E22; Sp = E11-E12+E21+E22
    ix = (to_px(Sv)).astype(np.int32); iy = (to_px(Sp)).astype(np.int32)
    ok = (ix>=0)&(ix<SF)&(iy>=0)&(iy<SF)
    np.add.at(histQ, (iy[ok], ix[ok]), 1.0)
rmax = 0.0
# quick radius certificate on last chunk
rmax = np.sqrt(Sv**2+Sp**2).max()
print("sampled quantum %.1fs  max radius (last chunk) %.5f  vs 2sqrt2=%.5f" % (time.time()-t0, rmax, 2*np.sqrt(2)))

# ---------- local fog: product states ----------
histL = np.zeros((SF, SF), np.float64)
done = 0
while done < NSAMP//2:
    n = min(CH, NSAMP//2-done); done += n
    a1, a2, b1, b2, al, be = rng.uniform(0, 2*np.pi, (6, n))
    A1 = np.cos(a1-al); A2 = np.cos(a2-al); B1 = np.cos(b1-be); B2 = np.cos(b2-be)
    Sv = A1*B1+A1*B2+A2*B1-A2*B2; Sp = A1*B1-A1*B2+A2*B1+A2*B2
    ix = (to_px(Sv)).astype(np.int32); iy = (to_px(Sp)).astype(np.int32)
    ok = (ix>=0)&(ix<SF)&(iy>=0)&(iy<SF)
    np.add.at(histL, (iy[ok], ix[ok]), 1.0)
print("sampled local %.1fs  |S|max %.5f (<=2)" % (time.time()-t0, np.abs(Sv).max()))

# ---------- tone ----------
from scipy.ndimage import zoom
def fogtone(h):
    lin = h/ (np.percentile(h[h>0], 99.3) if (h>0).any() else 1.0)
    knee = (1 - np.exp(-1.8*lin))/1.8*1.55
    logv = hist_eq(np.log1p(h).astype(np.float32))**1.7
    v = 0.55*knee + 0.45*logv
    return zoom(v.astype(np.float32), S/h.shape[0], order=1)[:S,:S]
fq = fogtone(histQ); fl = fogtone(histL)

yy, xx = np.mgrid[0:S,0:S].astype(np.float32)
Su = xx/S*2*LIM - LIM; Sp = yy/S*2*LIM - LIM
inside_sq = (np.abs(Su) <= 2) & (np.abs(Sp) <= 2)

rgb = np.zeros((S,S,3), np.float32)
# quantum fog: cool violet inside the classical cage, ember outside (nonlocal light)
C_in  = np.array([0.36,0.42,0.78])
C_out = np.array([1.00,0.55,0.20])
w_in = inside_sq.astype(np.float32); w_out = 1-w_in
rgb += (0.85*fq*w_in)[...,None]*C_in[None,None,:]
rgb += (1.05*fq*w_out)[...,None]*C_out[None,None,:]
# local fog: steel blue, subtle
rgb += (0.62*fl)[...,None]*np.array([0.30,0.58,0.66])[None,None,:]

# ---------- cages ----------
def line_glow(d, w, amp): return amp*np.exp(-(d/w)**2)
# classical square
dsq = np.minimum(np.minimum(np.abs(Su-2), np.abs(Su+2)), np.minimum(np.abs(Sp-2), np.abs(Sp+2)))
sqmask = (np.abs(Su) <= 2.02) & (np.abs(Sp) <= 2.02)
dedge = np.where(sqmask, np.minimum(np.minimum(np.abs(Su-2), np.abs(Su+2)), np.minimum(np.abs(Sp-2), np.abs(Sp+2))), 
                 np.hypot(np.maximum(np.abs(Su)-2,0), np.maximum(np.abs(Sp)-2,0)))
rgb += line_glow(dedge, 0.012, 0.55)[...,None]*np.array([0.45,0.75,0.85])[None,None,:]
# Tsirelson circle
rr = np.hypot(Su, Sp)
rgb += line_glow(rr - 2*np.sqrt(2), 0.014, 0.95)[...,None]*np.array([1.0,0.82,0.45])[None,None,:]
# NS diamond
dd = np.abs(np.abs(Su)+np.abs(Sp) - 4)
rgb += line_glow(dd, 0.012, 0.38)[...,None]*np.array([0.55,0.60,0.75])[None,None,:]
# kiss stars at (+-2,+-2)
star = np.zeros((S,S), np.float32)
def to_pxF(u): return (u + LIM)/(2*LIM)*S
for sx in (-2,2):
    for sy in (-2,2):
        dx = xx-to_pxF(sx); dy = yy-to_pxF(sy)
        d2 = dx**2 + dy**2
        star += np.exp(-d2/(2*(3.4*rs)**2)) + 0.5*np.exp(-d2/(2*(10*rs)**2))
        # 4-fold diffraction spikes aligned with the diagonals (the caustic directions)
        u = (dx+dy)/np.sqrt(2); v = (dx-dy)/np.sqrt(2)
        star += 0.5*np.exp(-(np.abs(u)/(1.1*rs))**2)*np.exp(-(np.abs(v)/(34*rs))**2)
        star += 0.5*np.exp(-(np.abs(v)/(1.1*rs))**2)*np.exp(-(np.abs(u)/(34*rs))**2)
rgb += star[...,None]*np.array([0.95,0.92,0.80])[None,None,:]*0.9

# bloom
bl = wide_bloom(np.maximum(rgb.max(-1)-0.7,0).astype(np.float32), 18*rs)
rgb += bl[...,None]*np.array([0.9,0.8,0.6])[None,None,:]*0.4

out = filmic(np.nan_to_num(rgb), 1.35)**0.94
img = to_img(out)

# footer
W = img.size[0]; FH = int(0.075*W)
dr = ImageDraw.Draw(img, 'RGBA')
dr.rectangle([0, W-FH, W, W], fill=(4,6,10,214))
try:
    fs = max(9, int(0.0093*W))
    fm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", fs)
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", fs)
except OSError: fm = fb = ImageFont.load_default()
pad = int(0.016*W); ly = W-FH+pad
for txt, fnt, col in [
  ("THE CAGE OF CORRELATIONS", fb, (238,205,140)),
  ("S = E11+E12+E21-E22 and S' = E11-E12+E21+E22.  Local worlds: the square |S|,|S'| <= 2.  One entangled pair: the disc S^2+S'^2 <= 8.", fm, (176,188,210)),
  ("No-signaling: the diamond |S|+|S'| <= 4.  All three cages pass through the same four gates (+-2,+-2), Fog = measure of reach.", fm, (176,188,210)),
]:
    dr.text((pad, ly), txt, font=fnt, fill=col); ly += int(fs*1.6)

if SS > 1: img = img.resize((FINAL,FINAL), Image.LANCZOS)
img.save("cage_proto.png" if FINAL < 2048 else "cage.png")
print("saved %.1fs" % (time.time()-t0))
