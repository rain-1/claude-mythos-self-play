"""4096^2 hero: render a slightly larger square, crop so the basin sits high, caption on the paving."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import scene, sys

FONT = '/usr/share/fonts/truetype/freefont/'
out = sys.argv[1] if len(sys.argv) > 1 else 'five_waves_4096.png'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
span = 1.29
px = span / N
half = 0.685
Wr = int(round(2 * half / px))
kw = dict(W=Wr, ss=4, x0=-half, x1=half, out='/tmp/hero_full.png', lam=0.07, A=0.0040, ts=0.024, cope=0.02,
          amb=0.80, sunk=0.55, icap=4, absorb=[0.08, 0.03, 0.03], gsig=6e-5, glint=2, bss=2)
if N < 2000:
    kw['ss'] = 3; kw['bss'] = 3
im = scene.render(**kw)
cx0 = int(round((-0.645 + half) / px)); cy0 = int(round((-0.605 + half) / px))
im = im.crop((cx0, cy0, cx0 + N, cy0 + N))
# caption band: soften the paving toward paper, then text
a = np.asarray(im).astype(np.float32) / 255
y = np.arange(N)[:, None]
yb = 0.555 + 0.605  # world y of rim bottom, measured from the crop top
band = np.clip((y * px - (yb + 0.018)) / 0.03, 0, 1)
paper = np.array([0.985, 0.968, 0.955])
a = a * (1 - 0.85 * band[..., None]) + paper * 0.85 * band[..., None]
im = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
d = ImageDraw.Draw(im)
s = N / 4096
ink = (92, 77, 102)
ft = ImageFont.truetype(FONT + 'FreeSerifBold.ttf', int(86 * s))
fi = ImageFont.truetype(FONT + 'FreeSerifItalic.ttf', int(50 * s))
fm = ImageFont.truetype(FONT + 'FreeSerif.ttf', int(44 * s))
x = int(150 * s); y0 = int((yb + 0.040) / px)
d.text((x, y0), 'Every Wave Gets Its Share', font=ft, fill=ink)
d.text((x, y0 + int(112 * s)), 'Five waves of heights 1, .85, .7, .55, .4 cross a round basin. Floor sector k is the chance that wave k carries the sum.', font=fi, fill=ink)
d.text((x, y0 + int(178 * s)), '40.9% + 26.5% + 17.4% + 9.8% + 5.4% = 1 exactly (Weyl, 1938), although the five events overlap, and some points belong to none.', font=fm, fill=ink)
im.save(out)
print('saved', out)
