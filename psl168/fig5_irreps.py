"""Figure 5 — the six irreducible representations of PSL(2,7) (rep-theory lens)."""
import numpy as np, sys, math
sys.path.insert(0,'psl168'); sys.path.insert(0,'octonions')
import figkit
from PIL import Image, ImageDraw
import colorsys

def render(W=1600):
    Hh=1180
    img=Image.new("RGB",(W,Hh),(10,11,19)); d=ImageDraw.Draw(img,"RGBA")
    reps=[(1,"trivial","every group has it"),
          (3,"𝟑","embeds the Klein quartic in ℂP²"),
          (3,"𝟑̄","its mirror (complex conjugate)"),
          (6,"𝟔","discrete series, q−1"),
          (7,"𝟕","Steinberg, q  — the Fano points"),
          (8,"𝟖","principal series, q+1 — the line ℙ¹(𝔽₇)")]
    fbig=figkit.font("DejaVuSans-Bold.ttf",60)
    fdim=figkit.font("DejaVuSans-Bold.ttf",44)
    flab=figkit.font("DejaVuSans.ttf",32)
    # disks sized by dimension, in a row
    cxs=[W*x for x in (0.10,0.235,0.37,0.52,0.685,0.87)]
    cy=Hh*0.40
    maxr=Hh*0.16
    for i,(dim,name,desc) in enumerate(reps):
        r=maxr*math.sqrt(dim)/math.sqrt(8)
        hue=i/6.0; rr,gg,bb=colorsys.hsv_to_rgb(hue,0.55,1.0)
        col=(int(rr*255),int(gg*255),int(bb*255))
        x=cxs[i]
        d.ellipse([x-r-8,cy-r-8,x+r+8,cy+r+8],fill=col+(45,))
        d.ellipse([x-r,cy-r,x+r,cy+r],fill=col+(90,),outline=col+(255,),width=5)
        # dim number centered
        t=str(dim); w=d.textlength(t,font=fdim); a=fdim.getbbox(t)
        d.text((x-w/2,cy-(a[3]-a[1])/2-a[1]),t,font=fdim,fill=(255,255,255))
        # description below, wrapped
        words=desc.split(); lines=[]; cur=""
        for wd in words:
            if d.textlength((cur+" "+wd).strip(),font=flab)<=W*0.16: cur=(cur+" "+wd).strip()
            else: lines.append(cur); cur=wd
        lines.append(cur)
        yy=cy+maxr+30
        for ln in lines:
            w2=d.textlength(ln,font=flab); d.text((x-w2/2,yy),ln,font=flab,fill=(180,188,208)); yy+=38
    # the sum-of-squares identity
    fe=figkit.font("DejaVuSans-Bold.ttf",50)
    eq="1² + 3² + 3² + 6² + 7² + 8²  =  168  =  | PSL(2,7) |"
    w=d.textlength(eq,font=fe); d.text((W/2-w/2,Hh-150),eq,font=fe,fill=(255,225,140))
    ft=figkit.font("DejaVuSans.ttf",30)
    t2="six conjugacy classes  →  six irreducible representations"
    w2=d.textlength(t2,font=ft); d.text((W/2-w2/2,Hh-86),t2,font=ft,fill=(160,170,195))
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("A finite group is mirrored by its irreducible representations — the indivisible ways it "
          "can act by matrices. PSL(2,7) has six conjugacy classes, so exactly six irreducibles, of "
          "dimensions 1, 3, 3̄, 6, 7 and 8 (the circles are scaled by dimension). The grand identity "
          "of character theory says the squares of these add up to the size of the group: "
          "1+9+9+36+49+64 = 168. Each one is a different face we have already met. The 7-dimensional "
          "rep is the Fano points; the 8-dimensional one is the projective line ℙ¹(𝔽₇). And the two "
          "3-dimensional reps — complex conjugates of each other — are the deepest: they realise "
          "PSL(2,7) as symmetries of complex projective 3-space, where it fixes the cubic curve "
          "x³y + y³z + z³x = 0. That is the Klein quartic. Representation theory is why a group of "
          "permutations of 7 points can also be a symmetry of a curved surface.")
    fig=figkit.caption(viz,"FIGURE 5 · REPRESENTATION THEORY","The six irreducibles — and why 168 = Σ d²",
                       body,accent=(255,225,140))
    figkit.save(fig,"psl168/05_irreducible_reps.png")
    print("done",fig.size)
