#!/usr/bin/env python3
"""
03 — Phenomenal Red
The CIE 1931 chromaticity diagram, built from the Wyman-Sloan-Shirley (JCGT 2013)
multi-lobe Gaussian analytic fits to the colour-matching functions x_bar, y_bar,
z_bar. The spectral locus (pure monochromatic light) is the glowing horseshoe;
its convex hull is the gamut of EVERY physically possible colour -- every spectrum
maps somewhere inside (metamers: infinitely many spectra to each point). Outside
that hull lie the "imaginary colours" no light can be: the void, the explanatory
gap. The sRGB triangle (what a screen can show) and the Planckian locus (the
colours of heated matter, where a poker first glows RED) are drawn within.

philosophy.SE: "The phenomenal experience of red and physicalism." The physics of
red is a point on this map; the redness is not on the map at all.
"""
import sys, numpy as np
from PIL import Image
from scipy.spatial import ConvexHull
from scipy.ndimage import gaussian_filter

S   = int(sys.argv[1]) if len(sys.argv) > 1 else 512
OUT = sys.argv[2] if len(sys.argv) > 2 else "03_phenomenal_red.png"
SS  = 2
N   = S * SS

# --- CIE 1931 colour-matching functions (Wyman et al. analytic fits) -------
def _g(x, mu, s1, s2):
    s = np.where(x < mu, s1, s2)
    return np.exp(-0.5 * ((x - mu) / s) ** 2)

def cie_xyz(lam):
    xb = (1.056*_g(lam, 599.8, 37.9, 31.0)
          + 0.362*_g(lam, 442.0, 16.0, 26.7)
          - 0.065*_g(lam, 501.1, 20.4, 26.2))
    yb = (0.821*_g(lam, 568.8, 46.9, 40.5)
          + 0.286*_g(lam, 530.9, 16.3, 31.1))
    zb = (1.217*_g(lam, 437.0, 11.8, 36.0)
          + 0.681*_g(lam, 459.0, 26.0, 13.8))
    return xb, yb, zb

LAM = np.arange(360.0, 780.0 + 0.25, 0.25)
Xb, Yb, Zb = cie_xyz(LAM)

# spectral locus in chromaticity coords
denom = Xb + Yb + Zb
loc_x = Xb / denom
loc_y = Yb / denom
# trim to the visible loop (≈400–700nm) so the hull is the classic horseshoe
sel = (LAM >= 400) & (LAM <= 700)
lx, ly, llam = loc_x[sel], loc_y[sel], LAM[sel]

# --- XYZ -> linear sRGB (D65) ---------------------------------------------
M = np.array([[ 3.2406, -1.5372, -0.4986],
              [-0.9689,  1.8758,  0.0415],
              [ 0.0557, -0.2040,  1.0570]], np.float64)
def xy_to_srgb(x, y, Yl=1.0):
    X = x / np.maximum(y, 1e-9) * Yl
    Z = (1 - x - y) / np.maximum(y, 1e-9) * Yl
    rgb = np.einsum('ij,...j->...i', M, np.stack([X, Yl*np.ones_like(x), Z], -1))
    return rgb

# --- raster grid in chromaticity space ------------------------------------
x0, x1, y0, y1 = -0.02, 0.78, -0.02, 0.86
xs = np.linspace(x0, x1, N)
ys = np.linspace(y1, y0, N)               # top row = high y
CX, CY = np.meshgrid(xs, ys)

# inside = convex hull of the spectral locus (all physically realisable colour)
pts = np.column_stack([lx, ly])
hull = ConvexHull(pts)
inside = np.ones((N, N), bool)
for eq in hull.equations:                  # a*x + b*y + c <= 0 inside
    inside &= (eq[0]*CX + eq[1]*CY + eq[2]) <= 1e-9

# --- colour every realisable chromaticity ---------------------------------
rgb = xy_to_srgb(CX, CY, 1.0)             # linear sRGB, may be out of gamut
mn = rgb.min(axis=2, keepdims=True)
oog = (-np.minimum(mn[..., 0], 0.0))      # how far outside the sRGB gamut

# clip negatives (hue-preserving-ish) for VIVID colour, then normalise to a
# constant max channel so every hue blazes at full saturation
rgb_ingamut = np.clip(rgb, 0, None)
mx = rgb_ingamut.max(axis=2, keepdims=True)
rgb_n = np.clip(rgb_ingamut / np.maximum(mx, 1e-9), 0, 1)
disp = rgb_n ** (1/2.2)

# weight brightness by chromatic saturation: pure phenomenal hues at the
# spectral rim blaze; the achromatic white heart recedes (but does not vanish)
sat = 1.0 - rgb_n.min(axis=2)
lumw = (0.48 + 0.52*sat**0.6)

img = np.zeros((N, N, 3), np.float32)
img[inside] = (disp[inside] * lumw[inside, None]) * 255.0

# the screen literally cannot show colours outside the sRGB triangle; let that
# honest boundary be *felt* as a faint cooling, not a milky wash
fade = np.clip(oog * 1.6, 0, 1.0)
img *= (1.0 - fade[..., None]*0.18)

# --- spectral locus rim: a luminous monochromatic edge --------------------
def to_px(x, y):
    ii = (x - x0)/(x1 - x0) * (N-1)
    jj = (y1 - y)/(y1 - y0) * (N-1)
    return ii, jj
rim = np.zeros((N, N), np.float32)
ri, rj = to_px(lx, ly)
# densify the locus polyline and splat
tt = np.linspace(0, 1, len(lx)*40)
ri_d = np.interp(tt, np.linspace(0,1,len(lx)), ri)
rj_d = np.interp(tt, np.linspace(0,1,len(lx)), rj)
lam_d = np.interp(tt, np.linspace(0,1,len(lx)), llam)
rim_rgb = np.zeros((N, N, 3), np.float32)
# colour the rim by the true monochromatic colour at that wavelength
mxy = xy_to_srgb(np.interp(tt, np.linspace(0,1,len(lx)), lx),
                 np.interp(tt, np.linspace(0,1,len(lx)), ly))
mxy = np.clip(mxy - np.minimum(mxy.min(axis=1, keepdims=True), 0), 0, None)
mxy = mxy / np.maximum(mxy.max(axis=1, keepdims=True), 1e-9)
ii = np.clip(np.round(ri_d).astype(int), 0, N-1)
jj = np.clip(np.round(rj_d).astype(int), 0, N-1)
np.add.at(rim_rgb, (jj, ii), (mxy**(1/2.2)).astype(np.float32))
rim_glow = gaussian_filter(rim_rgb, sigma=(SS*1.1, SS*1.1, 0))
rim_glow /= (rim_glow.max() + 1e-9)
img += rim_glow * 255.0 * 1.1

# --- Planckian (blackbody) locus: colours of heated matter ----------------
h, c, kB = 6.626e-34, 2.998e8, 1.381e-23
lam_m = LAM * 1e-9
def planck_xy(T):
    B = (2*h*c**2) / (lam_m**5) / (np.exp(h*c/(lam_m*kB*T)) - 1.0)
    X = np.trapezoid(B*Xb, LAM); Y = np.trapezoid(B*Yb, LAM); Z = np.trapezoid(B*Zb, LAM)
    s = X+Y+Z
    return X/s, Y/s
Ts = np.linspace(1000, 12000, 400)
pxy = np.array([planck_xy(T) for T in Ts])
pi, pj = to_px(pxy[:,0], pxy[:,1])
plk = np.zeros((N, N), np.float32)
ii = np.clip(np.round(pi).astype(int), 0, N-1)
jj = np.clip(np.round(pj).astype(int), 0, N-1)
np.add.at(plk, (jj, ii), 1.0)
plk = gaussian_filter(plk, sigma=SS*0.7)
plk /= (plk.max()+1e-9)
img += plk[..., None] * np.array([255, 250, 235], np.float32) * 0.55

# --- sRGB primaries triangle (what a screen can show) ---------------------
prim = np.array([[0.64, 0.33], [0.30, 0.60], [0.15, 0.06], [0.64, 0.33]])
tri = np.zeros((N, N), np.float32)
for k in range(3):
    a, b = prim[k], prim[k+1]
    seg = np.linspace(0, 1, 400)
    sx = a[0] + seg*(b[0]-a[0]); sy = a[1] + seg*(b[1]-a[1])
    si, sj = to_px(sx, sy)
    ii = np.clip(np.round(si).astype(int), 0, N-1)
    jj = np.clip(np.round(sj).astype(int), 0, N-1)
    np.add.at(tri, (jj, ii), 1.0)
tri = gaussian_filter(tri, sigma=SS*0.5); tri /= (tri.max()+1e-9)
img += tri[..., None] * np.array([20, 22, 28], np.float32)  # faint dark engraving

# --- line of purples: colours with NO wavelength, purely phenomenal --------
# the bottom hull edge joins 400nm (violet) to 700nm (red); no single light is
# purple -- these hues are constructed by the eye. Give them a soft glow.
v_xy = (lx[0], ly[0]); r_xy = (lx[-1], ly[-1])
seg = np.linspace(0, 1, 600)
sx = v_xy[0] + seg*(r_xy[0]-v_xy[0]); sy = v_xy[1] + seg*(r_xy[1]-v_xy[1])
si, sj = to_px(sx, sy)
purp = np.zeros((N, N), np.float32)
ii = np.clip(np.round(si).astype(int), 0, N-1)
jj = np.clip(np.round(sj).astype(int), 0, N-1)
np.add.at(purp, (jj, ii), 1.0)
purp = gaussian_filter(purp, sigma=SS*1.4); purp /= (purp.max()+1e-9)
img += purp[..., None] * np.array([150, 40, 170], np.float32) * 0.9

# --- phenomenal RED: a focal bloom at the long-wave spectral tip -----------
# the redness the title points at; physics puts it here, ~700nm, bottom-right
red_xy = (lx[-1], ly[-1])
rxi, ryj = to_px(*red_xy)
yyg, xxg = np.mgrid[0:N, 0:N]
rg = np.exp(-(((xxg-rxi)**2 + (yyg-ryj)**2)/(2*(SS*26.0)**2)))
img += rg[..., None] * np.array([120, 18, 22], np.float32)

# --- compose on a deep void (the imaginary colours / explanatory gap) ------
bg = np.array([6, 6, 9], np.float32)
out = np.where(inside[..., None] | (rim_glow.sum(-1, keepdims=True) > 0.02), img, bg)
out = np.maximum(out, bg)

# filmic, no clip to white
out = 255.0*(1.0 - np.exp(-out/200.0))
out = np.clip(out, 0, 255).astype(np.uint8)

im = Image.fromarray(out, "RGB")
if SS > 1:
    im = im.resize((S, S), Image.LANCZOS)
im.save(OUT)
print("saved", OUT, im.size, "hull verts", len(hull.vertices))
