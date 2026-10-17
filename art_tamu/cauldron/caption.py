from PIL import Image, ImageDraw, ImageFont
import numpy as np
raw=Image.open('tray_raw.png'); W,H0=raw.size; PAD=200
a=np.asarray(raw).astype(np.float32); top=a[:40].mean((0,1))
im=Image.new('RGB',(W,H0+PAD),tuple(int(v) for v in top)); im.paste(raw,(0,PAD)); H=H0+PAD; d=ImageDraw.Draw(im); INK=(92,77,102); FD='/usr/share/fonts/truetype/'
ft=ImageFont.truetype(FD+'dejavu/DejaVuSerif-Bold.ttf',int(W*0.026))
fi=ImageFont.truetype(FD+'liberation/LiberationSerif-Italic.ttf',int(W*0.0150))
x,y=W*0.06,H*0.04
d.text((x,y),'One Hundred Twenty Secrets, Three Guesses Each on Average',font=ft,fill=INK)
L=['every secret ordering of five colours (MO 497111, the Magic Cauldron), with the guesses of an optimal player as rows of beads, first guess nearest you;',
   'after each guess you learn which places are right: those beads are clear glass, the misses frosted.  Short games at the back, long games in front.',
   'The tints count the games of 1, 2, 3, 4, 5 guesses: 1, 26, 66, 26, 1, the Eulerian numbers (also 1, 11, 11, 1 for four colours, 1, 4, 1 for three),',
   'so the average is exactly (n + 1)/2 = 3.  Conjecture: for every n.  Coral frames: the secret guessed at once, and the one that takes all five.']
for i,l in enumerate(L): d.text((x,y+W*0.037+i*W*0.019),l,font=fi,fill=INK)
im.save('../one_hundred_twenty_secrets.png')
