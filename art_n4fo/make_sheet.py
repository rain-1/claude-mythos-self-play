"""Assemble the titled triptych contact sheet."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np

paths=['gershgorin_I_the_certain_cage.png',
       'gershgorin_II_the_tighter_cage.png',
       'gershgorin_III_the_ghost.png']
labels=['I · THE CERTAIN CAGE','II · THE TIGHTER CAGE','III · THE GHOST']
subs=['Gershgorin discs + the capture theorem',
      "Brauer's ovals of Cassini",
      'pseudospectra of a non-normal matrix']

H=900
ims=[Image.open(p).convert('RGB') for p in paths]
ims=[im.resize((H,H),Image.LANCZOS) for im in ims]
pad=40; gap=30; top=150; bot=90
W=H*3+gap*2+pad*2
sheet=Image.new('RGB',(W,H+top+bot),(0,0,0))
d=ImageDraw.Draw(sheet)

def font(sz,bold=False):
    for pth in ([ "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" ] if bold else
                [ "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" ]):
        try: return ImageFont.truetype(pth,sz)
        except: pass
    return ImageFont.load_default()

title=font(58,bold=True); sub=font(26); lab=font(30,bold=True); cap=font(22)
gold=(212,168,92); dim=(150,150,160); blue=(120,150,190)

t="WHERE THE REAL MUST BE"
w=d.textlength(t,font=title); d.text(((W-w)/2,34),t,font=title,fill=gold)
s="the spectrum is a root no formula can name — yet the matrix cages it"
w=d.textlength(s,font=sub); d.text(((W-w)/2,104),s,font=sub,fill=dim)

x=pad
for im,l,sb in zip(ims,labels,subs):
    sheet.paste(im,(x,top))
    w=d.textlength(l,font=lab); d.text((x+(H-w)/2,top+H+14),l,font=lab,fill=gold)
    w=d.textlength(sb,font=cap); d.text((x+(H-w)/2,top+H+52),sb,font=cap,fill=blue)
    x+=H+gap
sheet.save('triptych.png')
print('triptych.png',sheet.size)
