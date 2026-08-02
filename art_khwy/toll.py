"""PIECE 3 (2560²) — 'The Toll of Twenty-Two'   (AP-obstruction atlas, piece 38)
S = { n = x² + xy + 3y² }  (norm form of Z[(1+√−11)/2], disc −11, h = 1).
Eleven channels = residues mod 11: five alive (quadratic residues), five
forbidden forever, one half-alive (≡0). Terrain = true density from the
4×10⁹ census (hist11.txt). Equal-gap runs of consecutive elements:
l=3 at 3 (gap 1), l=4 at 33,092,159 (gap 22 = 2·11), l=5 nowhere ≤ 4×10⁹.
Inset: the l=4 site, linear, with its three 22-arcs. Ghost rail: the
d=−1 country (piece 37) where l=6 already falls by 28M."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rendlib import Canvas

S = 2560; SS = 2
W = H = S * SS
cv = Canvas(W, H, (0.0012, 0.0014, 0.0030))

GOLD = np.array([1.00, 0.76, 0.34]); CREAM = np.array([1.0, 0.93, 0.70])
STEEL = np.array([0.40, 0.52, 0.76]); ICE = np.array([0.55, 0.85, 1.00])
EMBER = np.array([0.95, 0.50, 0.20])

hist = np.loadtxt("hist11.txt")     # (11, 512), bin b = floor(48 log10 n)
LX1 = 9.62                           # log10 4e9 + margin
def x2px(lg): return 90*SS + lg / LX1 * (W - 180*SS)

# ---- main channels ----
CT, CB = 0.105*H, 0.565*H
ch_h = (CB - CT) / 11
order = list(range(11))
alive = {0,1,3,4,5,9}
bins = np.arange(512) / 48.0                  # log10 n at bin left edge
binw = (10**((np.arange(512)+1)/48) - 10**(np.arange(512)/48))  # integers per bin
dens = hist / np.maximum(binw, 1)[None, :]    # empirical density
dmax = dens[1:2, 60:].max()

for row, res in enumerate(order):
    yc = CT + (row + 0.5) * ch_h
    if res in alive:
        # terrain band: brightness = density (relative), soft vertical profile
        val = np.clip(dens[res] / dmax, 0, 1.35)[None, :]
        xs = x2px(bins)
        # paint as horizontal gradient strip with gaussian vertical profile
        yy = np.arange(int(yc - ch_h*0.42), int(yc + ch_h*0.42))
        prof = np.exp(-0.5*((yy - yc)/(ch_h*0.235))**2)[:, None]
        # resample density to pixel columns
        colx = np.arange(int(x2px(0)), int(x2px(9.602)))
        lgs = (colx - 90*SS) / (W - 180*SS) * LX1
        dv = np.interp(lgs, bins + 1/96., dens[res] / dmax)
        dv = np.clip(dv, 0, 1.4) ** 0.85
        dv[lgs < 3.2] *= np.clip((lgs[lgs < 3.2] - 2.6) / 0.6, 0, 1) ** 2
        col = (GOLD*0.75 + CREAM*0.25) if res != 0 else (GOLD*0.45 + STEEL*0.55)
        patch = (prof * dv[None, :])[:, :, None] * col[None, None, :]
        cv.buf[yy[0]:yy[-1]+1, colx[0]:colx[-1]+1] += 0.34 * patch.astype(np.float32)
    else:
        # forbidden channel: cold whisper
        yy = np.arange(int(yc - ch_h*0.30), int(yc + ch_h*0.30))
        prof = np.exp(-0.5*((yy - yc)/(ch_h*0.16))**2)[:, None]
        colx = np.arange(int(x2px(0)), int(x2px(9.602)))
        cv.buf[yy[0]:yy[-1]+1, colx[0]:colx[-1]+1] += \
            (0.007 * prof)[:, :, None] * ICE[None, None, :].astype(np.float32)

# small-n beads (n <= 1500): the granular shore
def in_S_small(n):
    import math
    y = 0
    while 11*y*y <= 4*n:
        d = y*y - 4*(3*y*y - n)
        if d >= 0:
            s = math.isqrt(d)
            if s*s == d and (-y+s) % 2 == 0: return True
        y += 1
    return False
sm = [n for n in range(1, 1501) if in_S_small(n)]
for n in sm:
    res = n % 11
    row = order.index(res)
    yc = CT + (row + 0.5) * ch_h
    cv.stars(np.array([x2px(np.log10(n))]), np.array([yc]),
             np.array([1.0, 0.85, 0.50]), sigma=1.9*SS, amp=3.6)

# ---- record beacons ----
def beacon(lg, label_y_off, amp=1.0):
    px = x2px(lg)
    cv.segments(np.array([[px, CT-14*SS]]), np.array([[px, CB+14*SS]]),
                GOLD, width=1.3*SS, amp=0.14*amp, step=0.7)
    cv.stars(np.array([px]), np.array([CT-22*SS]), GOLD, sigma=3.2*SS, amp=2.2*amp)
beacon(np.log10(3), 0)
beacon(np.log10(33092159), 0)
# l=5: the open channel exits the frame right (apophatic)
px5 = x2px(9.602)
cv.segments(np.array([[px5, CT-14*SS]]), np.array([[px5, CB+14*SS]]),
            ICE, width=1.4*SS, amp=0.10, step=0.7)

# ---- ghost rail: the d=-1 country (piece 37 data) ----
RY = 0.615*H
cv.segments(np.array([[x2px(0), RY]]), np.array([[x2px(9.602), RY]]),
            STEEL, width=1.0*SS, amp=0.06, step=0.8)
for lg, l in [(np.log10(757), 4), (np.log10(2989), 5), (np.log10(28059605), 6)]:
    cv.stars(np.array([x2px(lg)]), np.array([RY]), STEEL, sigma=2.8*SS, amp=7.0)

# ---- inset: the l=4 site, linear window ----
IX0, IX1 = 0.10*W, 0.90*W
IY0, IY1 = 0.685*H, 0.895*H
fr = np.array([[IX0, IY0], [IX1, IY0], [IX1, IY1], [IX0, IY1]])
cv.segments(fr, np.roll(fr, -1, axis=0), np.array([0.60, 0.68, 0.85]),
            width=1.0*SS, amp=0.16, step=0.8)
N0, N1 = 33092159 - 75, 33092225 + 75
els = [33092101, 33092117, 33092123, 33092139, 33092140, 33092148, 33092151,
       33092156, 33092159, 33092181, 33092203, 33092225, 33092228, 33092229,
       33092233, 33092236, 33092239, 33092240, 33092244, 33092247, 33092249,
       33092260, 33092272, 33092288, 33092295]      # sympy-verified list
els = [e for e in els if N0 <= e <= N1]
run = {33092159, 33092181, 33092203, 33092225}
base_y = (IY0 + IY1)/2 + 0.055*H
def n2px(n): return IX0 + (n - N0) / (N1 - N0) * (IX1 - IX0)
# baseline
cv.segments(np.array([[IX0+8*SS, base_y]]), np.array([[IX1-8*SS, base_y]]),
            STEEL, width=1.0*SS, amp=0.55, step=0.8)
for e in els:
    px = n2px(e)
    if e in run:
        cv.stars(np.array([px]), np.array([base_y]), GOLD, sigma=3.6*SS, amp=9.0)
        cv.stars(np.array([px]), np.array([base_y]), CREAM, sigma=1.7*SS, amp=5.0)
    else:
        cv.stars(np.array([px]), np.array([base_y]), STEEL, sigma=2.3*SS, amp=5.5)
# the three 22-arcs
rl = sorted(run)
for a, b in zip(rl, rl[1:]):
    pa, pb = n2px(a), n2px(b)
    tt = np.linspace(0, np.pi, 60)
    xs = pa + (pb - pa) * (1 - np.cos(tt)) / 2
    ys = base_y - np.sin(tt) * 0.062*H
    A = np.stack([xs[:-1], ys[:-1]], 1); B = np.stack([xs[1:], ys[1:]], 1)
    cv.segments(A, B, GOLD, width=1.3*SS, amp=0.85, step=0.5)

cv.bloom(sigmas=(4*SS, 13*SS, 40*SS), gains=(0.42, 0.25, 0.13), thresh=0.38)
img = cv.tonemap(k=1.9, gamma=2.1)
pil = Image.fromarray(img).resize((S, S), Image.LANCZOS)
d = ImageDraw.Draw(pil)
FP = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def Fnt(sz): return ImageFont.truetype(FP, sz)
warm = (240, 212, 158); dim = (135, 142, 168); ice = (155, 210, 238)
stee = (150, 165, 200)
d.text((S//2, 70), "T H E   T O L L   O F   T W E N T Y - T W O",
       font=Fnt(52), fill=warm, anchor="mm")
d.text((S//2, 126),
       "S = { x² + xy + 3y² }  ·  the ℤ[(1+√−11)/2] country, censused to 4×10⁹  ·  atlas piece 38",
       font=Fnt(30), fill=dim, anchor="mm")
# channel labels
for row, res in enumerate(order):
    yc = int((CT + (row + 0.5) * ch_h)/SS)
    lab = f"≡ {res}"
    cl = warm if res in {1,3,4,5,9} else ((150,160,190) if res == 0 else (95,115,150))
    d.text((62, yc), lab, font=Fnt(26), fill=cl, anchor="mm")
d.text((S-46, int((CT + (10.5) * ch_h)/SS) + 40, ),
       "five channels forbidden forever — non-residues of the ramified prime",
       font=Fnt(24), fill=(105, 128, 165), anchor="rm")
# beacons labels
d.text((int(x2px(np.log10(3))/SS)+6, int(CT/SS)-58, ), "ℓ=3 at 3\n(gap 1)",
       font=Fnt(23), fill=warm, anchor="lm", align="left")
d.text((int(x2px(np.log10(33092159))/SS)-8, int(CT/SS)-58, ),
       "ℓ=4 at 33,092,159  (gap 22)", font=Fnt(23), fill=warm, anchor="rm")
d.text((int(x2px(9.602)/SS)-8, int(CT/SS)-58, ), "ℓ=5: nowhere ≤ 4×10⁹ →",
       font=Fnt(23), fill=ice, anchor="rm")
for lg, l in [(np.log10(757), 4), (np.log10(2989), 5), (np.log10(28059605), 6)]:
    d.text((int(x2px(lg)/SS), int(RY/SS)-26, ), f"ℓ={l}", font=Fnt(21), fill=stee, anchor="mm")
d.text((int(x2px(0.1)/SS), int(RY/SS)+34, ),
       "the d = −1 country (piece 37): ℓ=4 by 757, ℓ=5 by 2989, ℓ=6 by 28,059,605 — marching is cheap where 2 ramifies",
       font=Fnt(24), fill=stee, anchor="lm")
d.text((int(0.105*W/SS)+12, int(IY0/SS)+40, ),
       "the ℓ=4 site, linear:  …3, 22, 22, 22, 3…  — four consecutive citizens in perfect step",
       font=Fnt(27), fill=(168, 178, 205), anchor="lm")
for i, (e, lab) in enumerate([(33092159, "33 092 159 = 31·1067489"), (33092181, "33 092 181 = 3²·3676909"),
               (33092203, "33 092 203 = 1291·25633"), (33092225, "33 092 225 = 5²·1323689")]):
    d.text((int(n2px(e)/SS), int(((IY0+IY1)/2 + 0.055*H)/SS)+40+(i%2)*34, ), lab,
           font=Fnt(20), fill=(200, 185, 150), anchor="mm")
d.text((S//2, S-160),
       "here 2 is inert and 11 is ramified: any run of ≥ 3 consecutive elements in arithmetic progression beyond small n must pay gap ≡ 0 (mod 22)",
       font=Fnt(26), fill=dim, anchor="mm")
d.text((S//2, S-114),
       "the toll 22 = 2 · 11 — the inert prime times the ramified one.  First ℓ=4 run only at 33,092,159 (all four factor-certified, witnesses exhibited);",
       font=Fnt(26), fill=dim, anchor="mm")
d.text((S//2, S-68),
       "no ℓ=5 run of consecutive elements exists below 4×10⁹  ·  |S ∩ [1, 4×10⁹]| = 593,798,441  ·  living residues mod 11: {1,3,4,5,9} + the thin ≡0 channel",
       font=Fnt(26), fill=warm, anchor="mm")
pil.save("toll_2560.png")
print("saved")
