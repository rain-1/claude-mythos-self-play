"""Mathieu Fig 1 — the Steiner systems and the Mathieu groups."""
import sys, math
sys.path.insert(0,'mathieu'); sys.path.insert(0,'octonions')
import figkit
from PIL import Image, ImageDraw
import colorsys

def render(W=1600):
    Hh=1180
    img=Image.new("RGB",(W,Hh),(10,11,19)); d=ImageDraw.Draw(img,"RGBA")
    fh=figkit.font("DejaVuSans-Bold.ttf",46); fbig=figkit.font("DejaVuSans-Bold.ttf",52)
    fm=figkit.font("DejaVuSans.ttf",32); fs=figkit.font("DejaVuSans.ttf",28)
    d.text((70,46),"Steiner systems  S(t, k, n)  and the Mathieu groups",font=fh,fill=(235,240,250))
    d.text((70,112),"a collection of k-blocks among n points such that every t points lie in exactly one block",
           font=fs,fill=(160,170,195))
    rows=[("S(2,3,7)","7 points · blocks of 3 · 7 blocks","= the Fano plane","Aut = PSL(2,7)","168","2-transitive"),
          ("S(5,6,12)","12 points · blocks of 6 · 132 blocks","the Mathieu design","Aut = M₁₂","95 040","5-transitive"),
          ("S(5,8,24)","24 points · blocks of 8 · 759 octads","the great design","Aut = M₂₄","244 823 040","5-transitive")]
    y0=250; dy=240
    for i,(ssys,desc,note,grp,order,trans) in enumerate(rows):
        cy=y0+dy*i
        hue=0.55-0.14*i; r,g,b=colorsys.hsv_to_rgb(hue%1,0.5,1.0); col=(int(r*255),int(g*255),int(b*255))
        d.rounded_rectangle([60,cy-90,W-60,cy+120],radius=22,outline=col+(180,),width=3,fill=(col[0],col[1],col[2],16))
        d.text((90,cy-72),ssys,font=fbig,fill=(255,255,255))
        d.text((90,cy-2),desc,font=fm,fill=(200,208,228))
        d.text((90,cy+44),note,font=fs,fill=(160,168,190))
        # right column
        d.text((W-560,cy-72),grp,font=fbig,fill=col)
        d.text((W-560,cy-2),f"| G | = {order}",font=fm,fill=(210,216,235))
        d.text((W-560,cy+44),trans,font=fs,fill=(160,168,190))
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("A Steiner system S(t,k,n) is a set of n points together with a family of k-element "
          "'blocks' so perfectly balanced that every t points belong to exactly one block. The "
          "smallest interesting one is S(2,3,7): 7 points, 7 triples, any 2 points on exactly one "
          "line — that is precisely the FANO PLANE, and its symmetry group is our friend PSL(2,7). "
          "Climb to 5-fold balance and you reach the two great designs S(5,6,12) and S(5,8,24), "
          "whose symmetry groups are the Mathieu groups M₁₂ and M₂₄ — the first of the 26 SPORADIC "
          "simple groups, the outliers that belong to none of the infinite families. M₂₄ is "
          "5-transitive (it can carry any 5 points to any other 5) and has order 244,823,040. "
          "From it the structure keeps climbing: M₂₄ governs the Golay code, the Golay code builds "
          "the Leech lattice in 24 dimensions, and the Leech lattice's symmetries open onto the "
          "Monster. The Fano plane is the first rung of that ladder.")
    fig=figkit.caption(viz,"MATHIEU · THE CHAIN","From the Fano plane to M₂₄",
                       body,accent=(255,200,120))
    figkit.save(fig,"mathieu/01_steiner_chain.png")
    print("done",fig.size)
