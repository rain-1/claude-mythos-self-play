import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
from tone import tone
parts = [np.load(f'hero_{k}.npy') for k in range(8)]
x = np.concatenate(parts, 0)
t8 = tone(x, 0.75).astype(np.float32) / 255
m = t8.mean(axis=2, keepdims=True)
t8 = m + (t8 - m) * 1.22                     # saturation
t8 = 0.5 + (t8 - 0.5) * 1.06 + 0.012           # gentle contrast, keep it bright
im = Image.fromarray((np.clip(t8, 0, 1) * 255 + 0.5).astype(np.uint8))
W, H = im.size
d = ImageDraw.Draw(im)
ink = (82, 68, 96)
fb = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', int(H * 0.034))
fi = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf', int(H * 0.0155))
fs = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', int(H * 0.0135))
tx, ty = int(W * 0.035), int(H * 0.03)
d.text((tx, ty), 'As Tall as What It Sees', font=fb, fill=ink); ty += int(H * 0.048)
lines = ['The two-dimensional city-building array (MO 516465) on lots 0 ≤ i, j < 72, the origin at the far corner.',
         'Each building is the shortest whose rooftop sees, along its street and its avenue,',
         'exactly as many earlier rooftops as it has floors. The city is symmetric, so we look down the diagonal.',
         'The coral tower at (19, 19) has fourteen floors and strings a line to each of the fourteen roofs it sees.',
         'On the diagonal every height is even. Records: 14, 30, 34, 66, 222 at n = 19, 458, 493, 748, 1036.']
for k, l in enumerate(lines):
    d.text((tx, ty), l, font=fi if k == 0 else fs, fill=ink); ty += int(H * (0.024 if k == 0 else 0.020))
im.save('as_tall_as_what_it_sees.png')
