"""Assemble the annotated triptych contact sheet 'What the Bending Keeps'."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np

FD="/usr/share/fonts/truetype/dejavu/"
def F(name,sz): return ImageFont.truetype(FD+name,sz)

H=1180            # panel height
GAP=60
MARGX=90
TOP=290
CAPH=510
W=MARGX*2+3*H+2*GAP
HT=TOP+H+CAPH

canvas=Image.new("RGB",(W,HT),(6,6,9))
d=ImageDraw.Draw(canvas)

def load(p):
    im=Image.open(p).convert("RGB")
    return im.resize((H,H),Image.LANCZOS)

panels=[
 ("art_50e7/hero_bellows.png","THE BELLOWS",
  ["Steffen's flexible polyhedron, breathing.","9 vertices · 21 rigid bars · 14 faces — every",
   "edge length frozen, yet the shape turns. Its",
   "volume holds at 200.777 to 13 digits while",
   "it flexes: Sabitov's Bellows Theorem. Ghosts",
   "= flex phase; the gold skeleton is one rest breath."],
  (255,205,120)),
 ("art_50e7/comp_road.png","THE ONLY ROAD",
  ["The whole freedom of the solid is one circle:",
   "vertex v₉ riding the loop γ. Off it, terrain of",
   "edge-length violation rises; inside, a void of",
   "shapes that cannot exist at all. Only the lit",
   "arc is travelled — the road that the bars permit,",
   "and nothing else."],
  (255,196,110)),
 ("art_50e7/comp_cauchy.png","CAUCHY'S CAGE",
  ["The same 9 vertices, 21 edges, 14 faces —",
   "made convex. Now the flex-space collapses to",
   "the 6 rigid motions and nothing more: it is",
   "frozen solid. Cauchy, 1813 — a convex",
   "polyhedron cannot bend. Steffen is the dent",
   "that found the loophole."],
  (255,210,150)),
]

# title
d.text((MARGX,70),"WHAT THE BENDING KEEPS",font=F("DejaVuSerif-Bold.ttf",96),fill=(238,232,222))
d.text((MARGX,196),"rigidity, flexibility, and the volume a moving cage still cannot change  ·  from MathOverflow: “Is the dodecahedron flexible?”",
       font=F("DejaVuSans.ttf",34),fill=(150,150,168))

for i,(path,title,lines,gold) in enumerate(panels):
    x=MARGX+i*(H+GAP); y=TOP
    try:
        canvas.paste(load(path),(x,y))
    except FileNotFoundError:
        d.rectangle([x,y,x+H,y+H],outline=(60,60,70))
    # accent bar + title
    cy=y+H+34
    d.rectangle([x,cy+6,x+16,cy+58],fill=gold)
    d.text((x+34,cy),title,font=F("DejaVuSans-Bold.ttf",50),fill=gold)
    ty=cy+92
    for ln in lines:
        d.text((x,ty),ln,font=F("DejaVuSans.ttf",31),fill=(196,198,208)); ty+=44

# footnote
d.text((MARGX,HT-58),
 "procedural pixel art · 4096² hero + 2560² panels · flex verified: edge lengths to 9e-15, Bellows volume to 6e-13, rigidity kernel = 6   ·   claude/determined-tesla-50e79u",
 font=F("DejaVuSansMono.ttf",25),fill=(120,120,135))

canvas.save("art_50e7/triptych_contactsheet.png")
print("saved contact sheet",canvas.size)
