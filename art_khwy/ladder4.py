"""PIECE 2 v4 — 'The Ladder of Fainter Creases' (monodromy spectrum).
y = Im F_branch(-4^u) / 2^u : threads converge to the Cantor spectrum
{sum ±6^-n}. Pitchforks open with sqrt curves at every crease u=m.
The central Cantor void hosts a x6 zoom inset of the upper band --
the same picture, a sixth as loud (self-similarity made visible)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rendlib import Canvas
S = 2560; SS = 2
W = H = S * SS
U0, U1 = -0.7, 6.3
NM = 7
NCOL = 2200
us = np.linspace(U0, U1, NCOL)

tn = np.zeros((NM, NCOL))
for n in range(NM):
    tn[n] = 3.0**-n * np.sqrt(np.maximum(4.0**(us - n) - 1.0, 0.0))
scale = 2.0 ** us
signs = np.array([[1 if (k >> n) & 1 == 0 else -1 for n in range(NM)]
                  for k in range(2**NM)])
V = (signs @ tn) / scale[None, :]          # -> Cantor spectrum in [-1.2, 1.2]
born = (tn > 0)
ndist = 2.0 ** born.sum(0)
inkpp = 128.0 / ndist / 2.0**NM

cv = Canvas(W, H, (0.0012, 0.0014, 0.0030))
YS = H * 0.355 / 1.32
def u2px(u): return (u - U0) / (U1 - U0) * (W - 1)
def v2px(v): return H/2 - v * YS
pxs = u2px(us)

GOLDT = np.array([1.00, 0.76, 0.34]); COPPER = np.array([0.97, 0.50, 0.22])
STEEL = np.array([0.42, 0.58, 0.88]); VIOL = np.array([0.60, 0.44, 0.88])

def thread_color(vf):
    t = min(abs(vf) / 1.25, 1.0)
    return (GOLDT*(1-t) + COPPER*t) if vf >= 0 else (STEEL*(1-t) + VIOL*t)

def draw_threads(xmap, ymap, sel, base_amp, wid):
    for k in sel:
        v = V[k]
        xs = xmap(us); ys = ymap(v)
        ok = np.isfinite(ys)
        A = np.stack([xs[:-1], ys[:-1]], 1)
        B = np.stack([xs[1:], ys[1:]], 1)
        m = ok[:-1] & ok[1:]
        if not m.any(): continue
        col = thread_color(v[-1])
        amp = base_amp * (inkpp[:-1] * 0.5 + inkpp[1:] * 0.5)
        cv.segments(A[m], B[m], col, width=wid, amp=1.0, step=0.6,
                    amp_per=amp[m], color_per=np.broadcast_to(col, (int(m.sum()), 3)))

# main curtain
draw_threads(lambda u: u2px(u), lambda v: v2px(v), range(2**NM), 3.2, 1.1*SS)

# crease verticals + split stars
for m in range(NM):
    px = u2px(float(m))
    cv.segments(np.array([[px, 0]]), np.array([[px, H-1]]),
                np.array([0.45, 0.80, 0.95]), width=1.1*SS, amp=0.030, step=0.8)
    ci = np.argmin(np.abs(us - m))
    yy = np.unique(np.round(v2px(V[:, ci]), 0))
    amp = 2.4 * (0.68 ** m)
    cv.stars(np.full(len(yy), px), yy, np.array([1.0, 0.84, 0.44]),
             sigma=2.4*SS, amp=amp / max(len(yy)**0.5, 1))

# ---- x6 zoom inset in the Cantor void ----
IX0, IX1 = 0.315*W, 0.965*W
IY0, IY1 = 0.355*H, 0.645*H
icx = (IY0+IY1)/2; ih = (IY1-IY0)
def xmap_in(u): return IX0 + (u - U0) / (U1 - U0) * (IX1 - IX0)
def ymap_in(v):
    vp = (v - 1.0) * 6.0
    y = icx - vp * (ih/2) / 1.35
    y = np.where((y > IY0+2) & (y < IY1-2), y, np.nan)
    return y
top = [k for k in range(2**NM) if signs[k, 0] == 1]
draw_threads(xmap_in, ymap_in, top, 2.4, 0.95*SS)
# frame
fr = np.array([[IX0, IY0], [IX1, IY0], [IX1, IY1], [IX0, IY1]])
cv.segments(fr, np.roll(fr, -1, axis=0), np.array([0.60, 0.68, 0.85]),
            width=1.0*SS, amp=0.16, step=0.8)
# connector whiskers from the top band into the inset
cv.segments(np.array([[u2px(6.0), v2px(0.8)], [u2px(6.0), v2px(1.2)]]),
            np.array([[IX1, IY1], [IX1, IY0]]),
            np.array([0.60, 0.68, 0.85]), width=0.9*SS, amp=0.05, step=0.9)

cv.bloom(sigmas=(4*SS, 13*SS, 40*SS), gains=(0.42, 0.25, 0.13), thresh=0.36)
img = cv.tonemap(k=2.0, gamma=2.1)
pil = Image.fromarray(img).resize((S, S), Image.LANCZOS)
d = ImageDraw.Draw(pil)
FP = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def Fnt(sz): return ImageFont.truetype(FP, sz)
warm = (240, 212, 158); dim = (135, 142, 168); ice = (155, 210, 238)
d.text((S//2, 74), "T H E   L A D D E R   O F   F A I N T E R   C R E A S E S",
       font=Fnt(52), fill=warm, anchor="mm")
d.text((S//2, 130),
       "the monodromy of  F(z) = Σ 3⁻ⁿ√(1 + z/4ⁿ)  along the negative axis,  scaled by √|z|   ·   MO 513816",
       font=Fnt(30), fill=dim, anchor="mm")
for m in range(NM):
    px = int(u2px(float(m)) / SS)
    d.text((px, 196), f"−4^{m}", font=Fnt(27), fill=(220, 175, 112), anchor="mm")
d.text((int(u2px(-0.45)/SS), int(H/2/SS) - 60, ), "one voice", font=Fnt(26), fill=(200, 214, 235), anchor="mm")
d.text((int((IX0+90)/SS), int((IY0+55)/SS), ), "× 6  —  the upper band again: the same music, a sixth as loud",
       font=Fnt(27), fill=(168, 178, 205), anchor="lm")
d.text((S//2, S-186),
       "each crease −4ⁿ is a square-root branch point of weight 3⁻ⁿ: every analytic continuation splits in two — by the sixth crease the function",
       font=Fnt(26), fill=dim, anchor="mm")
d.text((S//2, S-144),
       "is a chorus of 128 voices settling onto the Cantor spectrum {Σ ±6⁻ⁿ}.  Infinitely many branch points ⇒ F is neither D-finite nor q-holonomic.",
       font=Fnt(26), fill=dim, anchor="mm")
d.text((S//2, S-92),
       "twin shores, one law:   c_m = C(½,m)/(1−4⁻ᵐ/3)  at 0    ·    a_k = C(½,k)/(1−4ᵏ/6)  at ∞    ·    between them  x^(−log₄3)·Φ(log₄x),  Φ̂ⱼ Γ-exact",
       font=Fnt(27), fill=warm, anchor="mm")
d.text((S//2, S-48),
       "exact identity  F = Σ aₖx^(½−k) + x^(−log₄3)Φ(log₄x)  verified to 10⁻⁵⁸ at x = 0.51, 2, 10, 100 — the Taylor aperture |x| < 1 hears one voice; the function owns the chorus",
       font=Fnt(23), fill=dim, anchor="mm")
pil.save("ladder_2560.png")
print("saved")
