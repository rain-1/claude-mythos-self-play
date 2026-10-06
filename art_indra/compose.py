"""compose.py beauty.f32 W fog.f32 Wf out.png expo title line1 line2 line3 [band=1]
Adds the (upsampled) fog pass, extended-Reinhard tone map, soft caption band at the bottom."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import zoom, gaussian_filter
W = int(sys.argv[2]); img = np.fromfile(sys.argv[1], np.float32).reshape(-1, W, 3).astype(np.float64)
H = img.shape[0]
if sys.argv[3] != '-':
    Wf = int(sys.argv[4]); fog = np.fromfile(sys.argv[3], np.float32).reshape(-1, Wf, 3).astype(np.float64)
    fog = np.stack([gaussian_filter(fog[..., c], 1.0) for c in range(3)], -1)
    fog = zoom(fog, (H / fog.shape[0], W / Wf, 1), order=1)
    img = img + fog
ex = float(sys.argv[6]); w = 1.2
x = ex * img; v = x * (1 + x / (w * w)) / (1 + x)
v = np.clip(v, 0, 1)
band = float(sys.argv[11]) if len(sys.argv) > 11 else 1
if band:   # milky paper band under the caption
    yy = np.arange(H)[:, None, None] / H
    a = np.clip((yy - 0.835) / 0.05, 0, 1) * 0.82
    v = v * (1 - a) + a * np.array([0.993, 0.986, 0.976])
srgb = np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.power(v, 1 / 2.4) - 0.055)
im = Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8))
dr = ImageDraw.Draw(im); FD = '/usr/share/fonts/truetype/liberation/'; INK = (92, 77, 102)
tb = ImageFont.truetype(FD + 'LiberationSerif-Bold.ttf', int(0.032 * W))
ti = ImageFont.truetype(FD + 'LiberationSerif-Italic.ttf', int(0.0148 * W))
tr = ImageFont.truetype(FD + 'LiberationSerif-Regular.ttf', int(0.0122 * W))
x0, y = int(0.055 * W), int(0.875 * H)
dr.text((x0, y), sys.argv[7], font=tb, fill=INK); y += int(tb.size * 1.3)
for t, f in ((sys.argv[8], ti), (sys.argv[9], tr), (sys.argv[10], tr)):
    if t: dr.text((x0, y), t, font=f, fill=INK); y += int(f.size * 1.42)
im.save(sys.argv[5], optimize=True)
