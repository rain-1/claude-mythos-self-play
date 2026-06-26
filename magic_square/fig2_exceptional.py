"""Magic Square Fig 2 — the five exceptional groups, all from the octonions."""
import sys, math
sys.path.insert(0,'magic_square'); sys.path.insert(0,'octonions')
import figkit
from PIL import Image, ImageDraw
import colorsys

GROUPS=[("G₂",14,"Aut(𝕆)"),
        ("F₄",52,"isometries of 𝕆P²"),
        ("E₆",78,"collineations of 𝕆P²"),
        ("E₇",133,"magic square (ℍ,𝕆)"),
        ("E₈",248,"magic square (𝕆,𝕆)")]

def render(W=1600):
    Hh=1120
    img=Image.new("RGB",(W,Hh),(10,11,19)); d=ImageDraw.Draw(img,"RGBA")
    d.text((70,46),"The five exceptional Lie groups — all built from 𝕆",
           font=figkit.font("DejaVuSans-Bold.ttf",46),fill=(235,240,250))
    n=5; x0=W*0.10; dx=W*0.80/n; baseY=Hh*0.66
    fnm=figkit.font("DejaVuSans-Bold.ttf",54); fd=figkit.font("DejaVuSans.ttf",30); fr=figkit.font("DejaVuSans.ttf",27)
    maxr=Hh*0.16
    for i,(nm,dim,role) in enumerate(GROUPS):
        cx=x0+dx*(i+0.5); r=maxr*math.sqrt(dim)/math.sqrt(248)
        cy=baseY-r
        hue=0.12+0.5*i/5; rr,gg,bb=colorsys.hsv_to_rgb(hue%1,0.55,1.0); col=(int(rr*255),int(gg*255),int(bb*255))
        if nm=="E₈": col=(210,150,255)
        d.ellipse([cx-r-8,cy-r-8,cx+r+8,cy+r+8],fill=col+(45,))
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col+(80,),outline=col+(255,),width=5)
        wn=d.textlength(nm,font=fnm); a=fnm.getbbox(nm); d.text((cx-wn/2,cy-(a[3]-a[1])/2-a[1]),nm,font=fnm,fill=(255,255,255))
        wd=d.textlength(f"dim {dim}",font=fd); d.text((cx-wd/2,baseY+24),f"dim {dim}",font=fd,fill=col)
        # role text wrapped
        words=role.split(); lines=[]; cur=""
        for wd2 in words:
            if d.textlength((cur+" "+wd2).strip(),font=fr)<=dx*0.92: cur=(cur+" "+wd2).strip()
            else: lines.append(cur); cur=wd2
        lines.append(cur); yy=baseY+70
        for ln in lines:
            wl=d.textlength(ln,font=fr); d.text((cx-wl/2,yy),ln,font=fr,fill=(165,174,196)); yy+=34
        if i<4:
            d.text((cx+r+dx*0.20,cy if False else baseY-maxr*0.5),"⊂",font=figkit.font("DejaVuSans-Bold.ttf",46),fill=(140,150,175))
    # OP^2 callout box
    by=Hh*0.86
    d.rounded_rectangle([70,by-44,W-70,by+96],radius=18,outline=(255,180,90,200),width=3,fill=(40,32,20,80))
    d.text((100,by-30),"𝕆P²  —  the Cayley plane",font=figkit.font("DejaVuSans-Bold.ttf",40),fill=(255,210,140))
    d.text((100,by+22),"the octonionic projective plane · 16-dimensional · the LAST projective plane "
                       "(non-associativity forbids 𝕆P³)",font=fr,fill=(200,190,170))
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("Lie's classification of continuous symmetry has four infinite families and exactly five "
          "leftovers — the EXCEPTIONAL groups G₂, F₄, E₆, E₇, E₈. Every one of them is octonionic. "
          "G₂ is the automorphism group of 𝕆 (it permutes the seven Fano units). F₄ and E₆ are the "
          "isometries and collineations of the CAYLEY PLANE 𝕆P² — the octonionic projective plane, "
          "a 16-dimensional world that is the largest projective plane that can exist (octonion "
          "non-associativity kills 𝕆P³). E₇ and E₈ complete the octonionic row of the magic square, "
          "E₈ reaching dimension 248. So the five strangest objects in the theory of symmetry — the "
          "ones that fit no pattern — are all the same secret: they are what the 8-dimensional "
          "numbers do when you let them act. From a 7-point diagram to E₈, one thread runs through "
          "everything: the octonions.")
    fig=figkit.caption(viz,"MAGIC SQUARE · THE EXCEPTIONALS","G₂, F₄, E₆, E₇, E₈ — the octonionic five",
                       body,accent=(210,150,255))
    figkit.save(fig,"magic_square/02_exceptional_tower.png")
    print("done",fig.size)
