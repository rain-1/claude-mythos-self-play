"""Compose the triptych contact sheet from the three final panels."""
from PIL import Image, ImageDraw
import sys

hero=Image.open("art_eygo/01_hero.png")     # 4096
idla=Image.open("art_eygo/02_idla.png")     # 2048
fpp =Image.open("art_eygo/03_fpp.png")      # 2048

Hh=1500                                       # panel height for the strip
def fit(im,h):
    w=int(im.size[0]*h/im.size[1]); return im.resize((w,h),Image.LANCZOS)
panels=[fit(idla,Hh), fit(hero,Hh), fit(fpp,Hh)]   # free-shape | frozen-hero | free-tree
gap=36; pad=48
W=sum(p.size[0] for p in panels)+gap*2+pad*2
sheet=Image.new('RGB',(W,Hh+pad*2),(8,8,11))
x=pad
for p in panels:
    sheet.paste(p,(x,pad)); x+=p.size[0]+gap
sheet.save("art_eygo/triptych.png")
# a smaller preview
sheet.resize((sheet.size[0]//3,sheet.size[1]//3),Image.LANCZOS).save("art_eygo/triptych_prev.png")
print("saved triptych.png", sheet.size)
