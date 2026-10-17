import argparse, numpy as np
from PIL import Image, ImageDraw, ImageFont
ap=argparse.ArgumentParser(); ap.add_argument('--inp'); ap.add_argument('--out'); a=ap.parse_args()
im=Image.open(a.inp); W,H=im.size; d=ImageDraw.Draw(im); INK=(92,77,102); FD='/usr/share/fonts/truetype/'
ft=ImageFont.truetype(FD+'dejavu/DejaVuSerif-Bold.ttf',int(W*0.027))
fi=ImageFont.truetype(FD+'liberation/LiberationSerif-Italic.ttf',int(W*0.0150))
x,y=W*0.045,H*0.06
d.text((x,y),'Every Other Island Lives Only in the Lake',font=ft,fill=INK)
L=['one island per octave of n, from n ≈ 500 far away to n ≈ two million close by; its ridge is c(n) − n/2, Conway’s $10,000 sequence, mirrored in the water',
   'the mint ridge is c*(n) − n/2 from MO 366772: above the water in even octaves, a hill inside the hill;',
   'in odd octaves it sinks, and the lake shows a mint hill that stands on no island.',
   'Conjecture: the mint never leaves the lilac. Proved here: its sign flips with the octave; checked to n = 2²⁸.']
for i,l in enumerate(L): d.text((x,y+W*0.040+i*W*0.0205),l,font=fi,fill=INK)
im.save(a.out)
