"""compose_fat6.py raw.png out.png — caption for the companion piece (same band as the hero)."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
import sorbet as sb
im = Image.open(sys.argv[1]).convert('RGB'); W, H = im.size
a = np.asarray(im, np.float32) / 255
yy = np.linspace(0, 1, H)[:, None, None]
band = np.clip((yy - 0.855) / 0.05, 0, 1) ** 1.5
a = a * (1 - band) + np.array([0.996, 0.992, 0.985]) * band
im = Image.fromarray((a * 255 + 0.5).clip(0, 255).astype(np.uint8)); dr = ImageDraw.Draw(im)
fs = W / 2560; ink = (92, 77, 102)
F = lambda k, s: ImageFont.truetype(sb.FONTS[k], int(s * fs))
dr.text((0.07 * W, 0.918 * H), 'As Wide as Six Can Be', fill=ink, font=F('serif_bold', 60), anchor='ls')
dr.text((0.07 * W, 0.948 * H), 'Six cylinders may be fatter than the ball they touch: radius (3 + √33)/8 = 1.09307…, seen down the three-fold axis.',
        fill=ink, font=F('italic', 25), anchor='ls')
dr.text((0.07 * W, 0.962 * H), 'Found again here from random starts (the best of 40), exactly Ogievetsky and Shlosman\'s conjectured optimum. The best seven found: r = 0.846934.',
        fill=ink, font=F('italic', 25), anchor='ls')
dr.text((0.07 * W, 0.981 * H), 'SLSQP over axes tangent to the sphere of radius 1 + r, pairwise axis distance ≥ 2r · 12 rod–rod + 6 rod–ball contacts (coral) · every rod touches four others',
        fill=(120, 105, 128), font=F('mono', 17), anchor='ls')
im.save(sys.argv[2], optimize=True); print('ok')
