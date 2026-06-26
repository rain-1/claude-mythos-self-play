"""Hurwitz Fig 3 — GF(8) as its two operation tables (addition & multiplication)."""
import sys, math
sys.path.insert(0,'hurwitz'); sys.path.insert(0,'octonions')
import figkit
from PIL import Image, ImageDraw
import colorsys

def gf8_mul(a,b):
    r=0
    for _ in range(3):
        if b&1: r^=a
        b>>=1; a<<=1
        if a&0b1000: a^=0b1011
    return r&0b111

# display order: 0, then powers of alpha=2
POW=[1]
for _ in range(6): POW.append(gf8_mul(POW[-1],2))
ORDER=[0]+POW                       # [0,1,2,4,3,6,7,5]
LAB=["0","1","α","α²","α³","α⁴","α⁵","α⁶"]
POS={v:i for i,v in enumerate(ORDER)}

def elt_color(v):
    if v==0: return (70,76,96)
    k=POW.index(v)
    r,g,b=colorsys.hsv_to_rgb(k/7.0,0.6,1.0); return (int(r*255),int(g*255),int(b*255))

def draw_table(d, x0,y0,cs, op, title, figkit):
    fhd=figkit.font("DejaVuSans-Bold.ttf",int(cs*0.40))
    fc=figkit.font("DejaVuSans-Bold.ttf",int(cs*0.40))
    ft=figkit.font("DejaVuSans-Bold.ttf",int(cs*0.5))
    def cell(r,c): return x0+c*cs, y0+r*cs
    def ctext(t,x,y,f,fill):
        w=d.textlength(t,font=f); a=f.getbbox(t); d.text((x+cs/2-w/2,y+cs/2-(a[3]-a[1])/2-a[1]),t,font=f,fill=fill)
    d.text((x0+cs*0.1, y0-cs*1.25), title, font=ft, fill=(235,240,250))
    sym="+" if op=="add" else "×"
    x,y=cell(0,0); ctext(sym,x,y,fhd,(150,160,185))
    for k in range(8):
        v=ORDER[k]; col=elt_color(v)
        x,y=cell(0,k+1); d.rectangle([x+3,y+3,x+cs-3,y+cs-3],fill=(26,28,40)); ctext(LAB[k],x,y,fc,col)
        x,y=cell(k+1,0); d.rectangle([x+3,y+3,x+cs-3,y+cs-3],fill=(26,28,40)); ctext(LAB[k],x,y,fc,col)
    for ri in range(8):
        for ci in range(8):
            a=ORDER[ri]; b=ORDER[ci]
            res=(a^b) if op=="add" else gf8_mul(a,b)
            col=elt_color(res); x,y=cell(ri+1,ci+1)
            d.rectangle([x+3,y+3,x+cs-3,y+cs-3],fill=tuple(int(c*0.22) for c in col),outline=(40,44,60),width=2)
            ctext(LAB[POS[res]],x,y,fc,col)

def render(W=1700):
    cs=int(W*0.045); margin=70
    tw=9*cs
    Hh=margin+int(cs*1.4)+9*cs+margin
    img=Image.new("RGB",(W,Hh),(10,11,19)); d=ImageDraw.Draw(img)
    y0=margin+int(cs*1.3)
    draw_table(d, margin, y0, cs, "add", "Addition  ( = XOR )", figkit)
    draw_table(d, W-margin-tw, y0, cs, "mul", "Multiplication", figkit)
    return img

if __name__=="__main__":
    viz=render(1700)
    body=("A field is two interlocking arithmetics on the same set, and the most honest portrait of "
          "GF(8) is simply its two tables. On the LEFT, addition: it is just bitwise XOR of the "
          "3-bit codes, so every element is its own negative and the table is the flat, symmetric "
          "structure of the vector space 𝔽₂³ (the Fano plane's points plus zero). On the RIGHT, "
          "multiplication of the seven non-zero elements: written as powers of a single generator α "
          "it becomes pure cyclic addition of exponents, α^i · α^j = α^(i+j mod 7) — the clean "
          "diagonal Latin-square of the cyclic group C₇. Two completely different patterns, the "
          "additive and the multiplicative, living on one set of eight symbols: that tension is "
          "exactly what a finite field is, and it is the engine inside PSL(2,8) and the Macbeath "
          "surface.")
    fig=figkit.caption(viz,"HURWITZ · THE FIELD, CONCRETELY","GF(8) is its two tables",
                       body,accent=(150,200,255),W=1700)
    figkit.save(fig,"hurwitz/03_gf8_tables.png")
    print("done",fig.size)
