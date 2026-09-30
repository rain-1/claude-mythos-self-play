"""compose_hero.py raw.png out.png — fade the bottom band of the ray-traced hero to paper and set the caption."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
import sorbet as sb

im = Image.open(sys.argv[1]).convert('RGB')
W, H = im.size
a = np.asarray(im, np.float32) / 255
yy = np.linspace(0, 1, H)[:, None, None]
paper = np.array([0.996, 0.992, 0.985])
band = np.clip((yy - 0.855) / 0.05, 0, 1) ** 1.5
a = a * (1 - band) + paper * band
im = Image.fromarray((a * 255 + 0.5).clip(0, 255).astype(np.uint8))
dr = ImageDraw.Draw(im)
fs = W / 2560
ink = (92, 77, 102)
F = lambda k, s: ImageFont.truetype(sb.FONTS[k], int(s * fs))
dr.text((0.07 * W, 0.918 * H), 'Six Hands on a Pearl', fill=ink, font=F('serif_bold', 60), anchor='ls')
dr.text((0.07 * W, 0.948 * H), 'Six unit cylinders of sorbet glass, every one touching a unit ball, none overlapping (MO 156008, asked c. 1990 by Kuperberg). Is six the most?',
        fill=ink, font=F('italic', 25), anchor='ls')
dr.text((0.07 * W, 0.962 * H), 'Yes: Matić and Radoičić proved it this July, by checking 2,954,984 boxes of polynomial inequalities. The seventh never fits.', fill=ink, font=F('italic', 25), anchor='ls')
dr.text((0.07 * W, 0.981 * H), "the 'burr' configuration (axes at distance 2 from the centre, three perpendicular pairs) · coral: its 18 contacts · glass absorbance ∝ chord length · tinted shadows on a paper wall",
        fill=(120, 105, 128), font=F('mono', 17), anchor='ls')
im.save(sys.argv[2], optimize=True)
print('ok')
