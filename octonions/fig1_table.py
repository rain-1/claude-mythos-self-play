"""Figure 1 — the octonion multiplication table (the algebraic lens)."""
import numpy as np, sys
sys.path.insert(0,'octonions')
import octo, figkit
from PIL import Image, ImageDraw

def render_table(W=1600):
    n=9; margin=70; cs=(W-2*margin)//n
    H=margin*2+cs*n
    img=Image.new("RGB",(W,H),(10,11,19)); d=ImageDraw.Draw(img)
    fbig=figkit.font("DejaVuSans-Bold.ttf",int(cs*0.30))
    fhd =figkit.font("DejaVuSans-Bold.ttf",int(cs*0.34))
    def cell_xy(r,c): return margin+c*cs, margin+r*cs
    def rgb(c,f=1.0): return tuple(min(255,int(255*v*f)) for v in c)
    def center(txt,x,y,fnt,fill):
        w=d.textlength(txt,font=fnt); a=fnt.getbbox(txt); h=a[3]-a[1]
        d.text((x+cs/2-w/2, y+cs/2-h/2-a[1]),txt,font=fnt,fill=fill)
    # header corner
    x,y=cell_xy(0,0); center("×",x,y,fhd,(150,160,185))
    for k in range(8):
        lab=octo.sub(k); col=rgb(octo.UNIT_RGB[k])
        x,y=cell_xy(0,k+1); d.rectangle([x+3,y+3,x+cs-3,y+cs-3],fill=(26,28,40)); center(lab,x,y,fhd,col)
        x,y=cell_xy(k+1,0); d.rectangle([x+3,y+3,x+cs-3,y+cs-3],fill=(26,28,40)); center(lab,x,y,fhd,col)
    # body
    for i in range(8):
        for j in range(8):
            s,k=octo.unit_mul(i,j)
            base=octo.UNIT_RGB[k]
            x,y=cell_xy(i+1,j+1)
            d.rectangle([x+3,y+3,x+cs-3,y+cs-3],fill=rgb(base,0.16),outline=(40,44,60),width=2)
            sign="" if (k==0 and s>0) else ("−" if s<0 else "+")
            if k==0: txt=("−1" if s<0 else "1")
            else: txt=sign+octo.sub(k)
            center(txt,x,y,fbig,rgb(base,1.0 if s>0 else 0.78))
    return img

if __name__=="__main__":
    viz=render_table(1600)
    body=("Reading row e_i across to column e_j gives the product e_i · e_j, coloured by its "
          "result. Three facts are visible at a glance. The main diagonal is all −1: every "
          "imaginary unit squares to minus one. The table is ANTI-symmetric across that diagonal "
          "(e_i e_j = − e_j e_i for i≠j) — the octonions are non-commutative. And each of the "
          "seven oriented Fano lines (1 2 3), (1 4 5), (1 7 6), (2 4 6), (2 5 7), (3 4 7), (3 6 5) "
          "is one cyclic rule e_i e_j = e_k hiding in the grid. The whole non-associative algebra "
          "of 8-dimensional numbers lives in this 8×8 square.")
    fig=figkit.caption(viz,"FIGURE 1 · THE ALGEBRA","The octonion multiplication table",
                       body,accent=(255,205,90))
    figkit.save(fig,"octonions/01_multiplication_table.png")
    print("done",fig.size)
