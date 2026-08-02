"""PIECE 2 v3 — 'The Ladder of Fainter Creases' (monodromy curtain).
x-axis: u = log4|x| along the negative real axis, x = -4^u, u in [-0.7, 6.3].
y-axis: Im F_eps(x) / envelope(x) for ALL 2^(m+1) monodromy branches
eps (sign choices of the m+1 imaginary square roots at depth u).
One thread enters at the left; at every crease -4^m each thread splits
in two (exact pitchfork); the curtain converges to a Bernoulli-conv
Cantor dust of ratio ~1/6. Ink budget constant per column."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rendlib import Canvas
S = 2560; SS = 2
W = H = S * SS
U0, U1 = -0.7, 6.3
NM = 7           # creases 0..6 inside frame
NCOL = W
us = np.linspace(U0, U1, NCOL)

# imaginary term sizes t_n(u) = 3^-n sqrt(max(|x|/4^n - 1, 0)), |x| = 4^u
tn = np.zeros((NM, NCOL))
for n in range(NM):
    tn[n] = 3.0**-n * np.sqrt(np.maximum(4.0**(us - n) - 1.0, 0.0))
env = tn.sum(0) + 1e-30

# all 128 sign patterns
signs = np.array([[1 if (k >> n) & 1 == 0 else -1 for n in range(NM)]
                  for k in range(2**NM)])          # (128, 7)
V = (signs @ tn) / env[None, :]                     # (128, NCOL) in [-1,1]

# multiplicity: pattern k is "active" once all its flipped terms exist;
# before t_n is born (=0) patterns differing in sign_n coincide -> the
# curtain is drawn with per-column ink = const / (# distinct threads).
born = (tn > 0)                                      # (7, NCOL)
ndist = 2.0 ** born.sum(0)                           # distinct threads/column
inkpp = 1.0 / ndist                                  # per-pattern share (128/ndist coincide)
inkpp = inkpp * (128.0 / 2.0**NM)                    # normalize

# ---- render ----
cv = Canvas(W, H, (0.007, 0.009, 0.015))
def u2px(u): return (u - U0) / (U1 - U0) * (W - 1)
def v2px(v): return H/2 - v * (H * 0.40)

pxs = u2px(us)
GOLDT = np.array([1.00, 0.76, 0.34]); COPPER = np.array([0.96, 0.48, 0.22])
STEEL = np.array([0.40, 0.55, 0.85]); VIOL = np.array([0.58, 0.42, 0.85])

# draw each of the 128 branch threads as a polyline (adjacent-column segments)
for k in range(2**NM):
    v = V[k]
    ys = v2px(v)
    A = np.stack([pxs[:-1], ys[:-1]], 1)
    B = np.stack([pxs[1:], ys[1:]], 1)
    seglen = np.abs(np.diff(pxs)) + np.abs(np.diff(ys))
    # destiny coloring by final position (symmetric warm above / cool below)
    vf = v[-1]
    t = abs(vf)
    col = (GOLDT*(1-t) + COPPER*t) if vf >= 0 else (STEEL*(1-t) + VIOL*t)
    amp = 3.4 * (inkpp[:-1] * 0.5 + inkpp[1:] * 0.5)
    cv.segments(A, B, col, width=1.05*SS, amp=1.0, step=0.6,
                amp_per=amp, color_per=np.broadcast_to(col, (len(A), 3)))

# crease verticals + stars at the split loci u = m
for m in range(NM):
    px = u2px(float(m))
    cv.segments(np.array([[px, 0]]), np.array([[px, H-1]]),
                np.array([0.45, 0.80, 0.95]), width=1.1*SS, amp=0.035, step=0.8)
    # the split happens on the thread(s) at v where t_m is born: v = ±... at u=m
    # all threads pass smoothly; star at the envelope birth points y where new pitchforks open:
    amp = 2.6 * (0.66 ** m)
    # pitchfork loci: positions of threads at u=m (each is a split point)
    ci = np.argmin(np.abs(us - m))
    yy = np.unique(np.round(v2px(V[:, ci]), 1))
    cv.stars(np.full(len(yy), px), yy, np.array([1.0, 0.82, 0.40]),
             sigma=2.6*SS, amp=amp / max(len(yy)**0.5, 1))

cv.bloom(sigmas=(4*SS, 13*SS, 40*SS), gains=(0.40, 0.24, 0.12), thresh=0.38)
img = cv.tonemap(k=2.0, gamma=2.1)
pil = Image.fromarray(img).resize((S, S), Image.LANCZOS)
d = ImageDraw.Draw(pil)
FP = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def Fnt(sz): return ImageFont.truetype(FP, sz)
warm = (240, 212, 158); dim = (135, 142, 168); ice = (155, 210, 238)
d.text((S//2, 74), "T H E   L A D D E R   O F   F A I N T E R   C R E A S E S",
       font=Fnt(52), fill=warm, anchor="mm")
d.text((S//2, 130),
       "the monodromy of  F(z) = Σ 3⁻ⁿ√(1 + z/4ⁿ)  along the negative axis   ·   MO 513816",
       font=Fnt(30), fill=dim, anchor="mm")
for m in range(NM):
    px = int(u2px(float(m)) / SS)
    d.text((px, 190), f"−4^{m}", font=Fnt(27), fill=(220, 175, 112), anchor="mm")
d.text((int(u2px(-0.35)/SS), S//2 - 40), "one voice", font=Fnt(26), fill=ice, anchor="mm")
d.text((S//2, S-186),
       "each crease −4ⁿ is a square-root branch point of weight 3⁻ⁿ: every analytic continuation splits in two — by the sixth crease the",
       font=Fnt(27), fill=dim, anchor="mm")
d.text((S//2, S-142),
       "function is a chorus of 128 voices, a Bernoulli-convolution dust of ratio 1/6.  Infinitely many branch points ⇒ F is neither D-finite nor q-holonomic.",
       font=Fnt(27), fill=dim, anchor="mm")
d.text((S//2, S-90),
       "twin shores, one law:  c_m = C(½,m)/(1−4⁻ᵐ/3) at 0   ·   a_k = C(½,k)/(1−4ᵏ/6) at ∞   ·   between them x^(−log₄3)·Φ(log₄x), Φ̂ⱼ Γ-exact",
       font=Fnt(28), fill=warm, anchor="mm")
d.text((S//2, S-46),
       "exact identity  F = Σ aₖx^(½−k) + x^(−log₄3)Φ(log₄x)  verified to 10⁻⁵⁸ at x = 0.51, 2, 10, 100  (fexact.py) — the Taylor aperture |x|<1 sees one crease; the function owns them all",
       font=Fnt(23), fill=dim, anchor="mm")
pil.save("ladder_2560.png")
print("saved")
