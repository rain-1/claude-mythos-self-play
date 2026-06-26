"""Figure 4 — the Cayley-Dickson ladder (the construction lens).
R -> C -> H -> O, each step doubling dimension and losing a law. The imaginary
structure grows: nothing, one unit, a triangle (one Fano line = H), the whole
Fano plane (O). Beyond O the ladder breaks (sedenions: zero divisors)."""
import numpy as np, sys, math
sys.path.insert(0,'octonions')
import octo, figkit
from PIL import Image, ImageDraw

def fano_glyph(d, cx, cy, r, faded=False):
    # mini Fano: triangle + incircle + 7 nodes, coloured
    import math
    pos={}
    for lab,a in {2:90,4:210,7:330}.items():
        pos[lab]=(cx+r*math.cos(math.radians(a)), cy-r*math.sin(math.radians(a)))
    pos[1]=(cx,cy)
    pos[6]=tuple((np.array(pos[2])+np.array(pos[4]))/2)
    pos[5]=tuple((np.array(pos[2])+np.array(pos[7]))/2)
    pos[3]=tuple((np.array(pos[4])+np.array(pos[7]))/2)
    a=0.5 if faded else 1.0
    for (x,y,z) in [(2,6,4),(2,5,7),(4,3,7),(2,1,3),(4,1,5),(7,1,6)]:
        d.line([pos[x],pos[z]],fill=(150,160,190,int(150*a)),width=3)
    d.ellipse([cx-r/2,cy-r/2,cx+r/2,cy+r/2],outline=(150,160,190,int(150*a)),width=3)
    for k,p in pos.items():
        c=tuple(int(255*v*a) for v in octo.UNIT_RGB[k])
        d.ellipse([p[0]-11,p[1]-11,p[0]+11,p[1]+11],fill=c,outline=(255,255,255,int(220*a)),width=2)

def render(W=1600):
    H=1480
    img=Image.new("RGB",(W,H),(10,11,19)); d=ImageDraw.Draw(img,"RGBA")
    sym=figkit.font("DejaVuSans-Bold.ttf",96)
    big=figkit.font("DejaVuSans-Bold.ttf",40)
    med=figkit.font("DejaVuSans.ttf",32)
    sm =figkit.font("DejaVuSans.ttf",29)
    rows=[("ℝ","Real",1,0,"the line"),
          ("ℂ","Complex",2,1,"the plane"),
          ("ℍ","Quaternions",4,3,"= 1 Fano line"),
          ("𝕆","Octonions",8,7,"= the whole Fano plane"),
          ("𝕊","Sedenions",16,15,"the ladder breaks")]
    losses=["double → lose ORDERING","double → lose COMMUTATIVITY",
            "double → lose ASSOCIATIVITY  (still alternative)",
            "double → lose ALTERNATIVITY  (zero divisors appear)"]
    y0=70; dy=(H-140)//5
    gx=W*0.74
    for i,(s,name,dim,imag,note) in enumerate(rows):
        cyr=y0+dy*i+dy//2
        faded=(i==4)
        a=0.45 if faded else 1.0
        col=(235,240,250) if not faded else (150,156,176)
        d.text((90,cyr-64),s,font=sym,fill=col)
        d.text((250,cyr-58),name,font=big,fill=tuple(int(c) for c in col))
        d.text((252,cyr-4),f"dimension {dim}",font=med,fill=(int(180*a),int(190*a),int(210*a)))
        d.text((252,cyr+34),f"{imag} imaginary unit"+("s" if imag!=1 else ""),font=sm,fill=(int(150*a),int(158*a),int(180*a)))
        d.text((620,cyr+34),note,font=sm,fill=(int(150*a),int(158*a),int(180*a)))
        # glyph
        if imag==0:
            d.ellipse([gx-9,cyr-9,gx+9,cyr+9],fill=(int(210*a),)*3)
        elif imag==1:
            d.ellipse([gx-13,cyr-13,gx+13,cyr+13],fill=tuple(int(255*v*a) for v in octo.UNIT_RGB[1]),outline=(255,255,255,int(220*a)),width=2)
        elif imag==3:
            r=70; P=[(gx+r*math.cos(math.radians(90+120*k)),cyr-r*math.sin(math.radians(90+120*k))) for k in range(3)]
            for k in range(3): d.line([P[k],P[(k+1)%3]],fill=(150,160,190,int(160*a)),width=3)
            for k,lab in enumerate([2,4,7]):
                d.ellipse([P[k][0]-12,P[k][1]-12,P[k][0]+12,P[k][1]+12],fill=tuple(int(255*v*a) for v in octo.UNIT_RGB[lab]),outline=(255,255,255,int(220*a)),width=2)
        elif imag==7:
            fano_glyph(d,gx,cyr,95,faded=False)
        else:
            fano_glyph(d,gx,cyr,95,faded=True)
        # arrow to next
        if i<4:
            ay=cyr+dy//2-6
            d.line([(150,ay),(150,ay+24)],fill=(120,150,210,200),width=4)
            for dxv in (-7,7): d.line([(150,ay+24),(150+dxv,ay+12)],fill=(120,150,210,200),width=4)
            d.text((180,ay+2),losses[i],font=sm,fill=(150,175,225) if i<3 else (200,140,150))
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("The four normed division algebras are built by one repeated trick — the Cayley-Dickson "
          "doubling — and each doubling costs a law. From the ordered real line ℝ to the complex "
          "plane ℂ we lose ordering; to the quaternions ℍ we lose commutativity (ab ≠ ba); to the "
          "octonions 𝕆 we lose associativity ((ab)c ≠ a(bc)), keeping only the weaker ALTERNATIVE "
          "law. The imaginary part grows from nothing, to one unit, to a triangle — which is "
          "exactly one Fano line, i.e. one copy of ℍ — to the full seven-point Fano plane of 𝕆. "
          "Double once more and the ladder breaks: the 16-dimensional sedenions 𝕊 have zero "
          "divisors and are no longer a division algebra. 𝕆 is the end of the road: the largest "
          "place where division still works.")
    fig=figkit.caption(viz,"FIGURE 4 · THE CONSTRUCTION","Cayley–Dickson: how to build 𝕆, and what it costs",
                       body,accent=(150,190,255))
    figkit.save(fig,"octonions/04_cayley_dickson_ladder.png")
    print("done",fig.size)
