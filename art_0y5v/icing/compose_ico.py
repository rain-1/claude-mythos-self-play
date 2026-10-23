import sys; sys.path.insert(0,'..')
from PIL import Image
from caption import caption
img=Image.open('ico_raw.png').convert('RGB'); W,H=img.size; s=W/4096
title='Thirty Whole Numbers'
line=('The icosahedron’s graph laid flat with straight edges, and every edge a whole number of sugar beads: '
      '159, 109, 56, 55, 49, 39 and 16. Count them.')
legend=('Points (x/2, y·√3/2) with (x, y) = (±159, −53), (0, 106), (±71, −13), (±55, −29), (±16, 42), (±39, −13), (0, 26); '
        'turning by 120° maps the drawing to itself, so colour = orbit. Harborth asked whether every planar graph '
        'has such a drawing — still open (MathOverflow 163845).')
img,y=caption(img,title,line,legend,int(300*s),int(H*0.858),int(3500*s),scale=s*1.12,fade=(int(H*0.835),int(H*0.858),(226,242,236)))
img.save('../every_edge_whole.png'); print(y/H)
