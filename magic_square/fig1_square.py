"""Magic Square Fig 1 — the Freudenthal-Tits magic square."""
import sys, math
sys.path.insert(0,'magic_square'); sys.path.insert(0,'octonions')
import figkit
from PIL import Image, ImageDraw

DIV=["ℝ","ℂ","ℍ","𝕆"]
CELL=[
 [("SO(3)",3),("SU(3)",8),("Sp(3)",21),("F₄",52)],
 [("SU(3)",8),("SU(3)²",16),("SU(6)",35),("E₆",78)],
 [("Sp(3)",21),("SU(6)",35),("SO(12)",66),("E₇",133)],
 [("F₄",52),("E₆",78),("E₇",133),("E₈",248)],
]
EXC={"F₄","E₆","E₇","E₈"}

def render(W=1600):
    n=5; margin=80; cs=(W-2*margin)//n; Hh=margin*2+cs*n
    img=Image.new("RGB",(W,Hh),(10,11,19)); d=ImageDraw.Draw(img,"RGBA")
    fhd=figkit.font("DejaVuSans-Bold.ttf",int(cs*0.42))
    fnm=figkit.font("DejaVuSans-Bold.ttf",int(cs*0.26))
    fdm=figkit.font("DejaVuSans.ttf",int(cs*0.17))
    def cell(r,c): return margin+c*cs, margin+r*cs
    def ctext(t,x,y,f,fill,dy=0):
        w=d.textlength(t,font=f); a=f.getbbox(t); d.text((x+cs/2-w/2,y+cs/2-(a[3]-a[1])/2-a[1]+dy),t,font=f,fill=fill)
    # corner
    x,y=cell(0,0); ctext("×",x,y,fhd,(120,130,155))
    for k in range(4):
        x,y=cell(0,k+1); d.rectangle([x+4,y+4,x+cs-4,y+cs-4],fill=(28,30,44)); ctext(DIV[k],x,y,fhd,(150,200,255))
        x,y=cell(k+1,0); d.rectangle([x+4,y+4,x+cs-4,y+cs-4],fill=(28,30,44)); ctext(DIV[k],x,y,fhd,(150,200,255))
    for r in range(4):
        for c in range(4):
            nm,dim=CELL[r][c]; x,y=cell(r+1,c+1)
            exc=nm in EXC
            if nm=="E₈": fill=(70,40,90,255); ec=(255,180,90)
            elif exc: fill=(40,32,60,235); ec=(255,180,90)
            else: fill=(20,26,40,235); ec=(70,90,120)
            d.rectangle([x+4,y+4,x+cs-4,y+cs-4],fill=fill,outline=ec,width=4 if exc else 2)
            ctext(nm,x,y,fnm,(255,235,200) if exc else (210,220,238),dy=-int(cs*0.10))
            ctext(f"dim {dim}",x,y,fdm,(230,190,140) if exc else (150,160,185),dy=int(cs*0.16))
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("One table, built by Freudenthal and Tits, ties the division algebras to the Lie groups. "
          "Index the rows and columns by ℝ, ℂ, ℍ, 𝕆, feed each pair into one uniform construction, "
          "and out comes a Lie algebra. The mundane corners give classical groups — orthogonal, "
          "unitary, symplectic. But the row and column belonging to the OCTONIONS produce, one "
          "after another, FOUR of the five exceptional Lie groups: F₄, E₆, E₇, and — where 𝕆 meets "
          "𝕆 — the magnificent E₈ of dimension 248. (The fifth exceptional, G₂, is Aut(𝕆) from the "
          "earlier gallery.) The exceptional groups are not random accidents in the classification "
          "of symmetry; they are the shadow the octonions cast. The whole strange, beautiful "
          "outer edge of Lie theory exists because, in eight dimensions, you can still divide.")
    fig=figkit.caption(viz,"MAGIC SQUARE · LIE THEORY","The Freudenthal–Tits magic square",
                       body,accent=(255,180,90))
    figkit.save(fig,"magic_square/01_magic_square.png")
    print("done",fig.size)
