"""Carton render + caption band + a little (k, F) map of where each egg's recipe sits.
    python3 compose.py cfg.json render.png out.png
"""
import sys, json, numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, "..")
from caption import caption, font, INK, CORAL

cfg = json.load(open(sys.argv[1])); ren = Image.open(sys.argv[2]).convert("RGB"); out = sys.argv[3]
W = ren.width; band = int(W * 0.15)
bg = tuple(int(255 * c) for c in [0.975, 0.978, 0.99])
img = Image.new("RGB", (W, ren.height + band), bg)
img.paste(ren, (0, 0))
# soft fade from render into the band
fade = int(band * 0.35)
arr = np.asarray(img).astype(np.float32)
y0 = ren.height - fade
t = np.linspace(0, 1, fade)[:, None, None] ** 1.5
arr[y0:ren.height] = arr[y0:ren.height] * (1 - t) + np.array(bg) * t
img = Image.fromarray(arr.astype(np.uint8))
s = W / 4096
dr = ImageDraw.Draw(img)
caption(img, int(170 * s), ren.height - int(0.10 * band), int(2600 * s),
        cfg["title"], cfg["line"], cfg["legend"], scale=s * 1.05, series=cfg.get("series"))
# --- phase map: k horizontal, F vertical ---
mx0, my0, mw, mh = int(W - 1040 * s), ren.height - int(0.08 * band), int(860 * s), int(band * 0.86)
kmin, kmax, Fmin, Fmax = 0.046, 0.068, 0.008, 0.068
def P(k, F): return mx0 + (k - kmin) / (kmax - kmin) * mw, my0 + mh - (F - Fmin) / (Fmax - Fmin) * mh
# region where patterns can live: below the saddle-node curve k = sqrt(F)/2 - F
F = np.linspace(0.0005, 0.25, 400); k = np.sqrt(F) / 2 - F
poly = [P(kk, ff) for kk, ff in zip(k, F) if kmin <= kk <= kmax and ff <= Fmax]
reg = [P(kmin, Fmin)] + [P(kmin, ff) for ff in np.linspace(0, Fmax, 2)][1:] + []
lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
fill = [P(kmin, Fmin)] + [p for p in poly] + [P(kmax, Fmin)]
ld.polygon([P(kmin, Fmin), P(kmin, Fmax)] + [p for p in poly if p[1] >= P(0, Fmax)[1]] + [P(kmax, Fmax), P(kmax, Fmin)], fill=None)
# light wash for the 'two steady states' side (left of the curve)
left = [P(kmin, Fmin), P(kmin, Fmax)] + sorted([p for p in poly], key=lambda p: p[1]) + [P(kmin, Fmin)]
ld.polygon(left, fill=(255, 236, 228, 255))
img.paste(lay, (0, 0), lay)
dr = ImageDraw.Draw(img)
dr.line(poly, fill=INK, width=max(2, int(3 * s)))
dr.rectangle([mx0, my0, mx0 + mw, my0 + mh], outline=(170, 155, 178), width=max(1, int(2 * s)))
f = font("ital", 30 * s)
dr.text((mx0 + mw / 2 - 60 * s, my0 + mh + 8 * s), "kill rate k", font=f, fill=(128, 110, 136))
fv = font("ital", 30 * s)
txt = Image.new("RGBA", (int(260 * s), int(44 * s)), (0, 0, 0, 0))
ImageDraw.Draw(txt).text((0, 0), "feed rate F", font=fv, fill=(128, 110, 136, 255))
txt = txt.rotate(90, expand=True)
img.paste(txt, (int(mx0 - 50 * s), int(my0 + mh / 2 - 120 * s)), txt)
dr = ImageDraw.Draw(img)
for k_, e in enumerate(cfg["eggs"]):
    d = np.load(e["file"]); Fk = d["Fk"]
    x, y = P(Fk[1], Fk[0]); r = 17 * s
    base = tuple(int(255 * c) for c in e["base"]); dye = tuple(int(255 * c) for c in e["dye"])
    dr.ellipse([x - r, y - r * 1.25, x + r, y + r * 1.25], fill=dye, outline=INK, width=max(1, int(2 * s)))
    dr.ellipse([x - r * 0.45, y - r * 0.6, x + r * 0.1, y - r * 0.05], fill=base)
    dr.text((x + r * 1.2, y - r * 1.1), str(k_ + 1), font=font("reg", 26 * s), fill=INK)
img.save(out)
print("saved", out, img.size)
