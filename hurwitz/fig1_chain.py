"""Hurwitz Fig 1 — the bound 84(g-1) and the chain of Hurwitz surfaces."""
import numpy as np, sys, math
sys.path.insert(0,'hurwitz'); sys.path.insert(0,'octonions')
import figkit
from PIL import Image, ImageDraw
import colorsys

def render(W=1600):
    Hh=1240
    img=Image.new("RGB",(W,Hh),(10,11,19)); d=ImageDraw.Draw(img,"RGBA")
    fbound=figkit.font("DejaVuSans-Bold.ttf",64)
    fg=figkit.font("DejaVuSans-Bold.ttf",44); fm=figkit.font("DejaVuSans.ttf",32); fsm=figkit.font("DejaVuSans.ttf",27)
    # the bound
    t="| Aut(Σ_g) |   ≤   84 ( g − 1 )"
    w=d.textlength(t,font=fbound); d.text((W/2-w/2,54),t,font=fbound,fill=(255,225,140))
    d.text((W/2-360,140),"the Hurwitz bound — the most symmetry a genus-g surface can have",font=fsm,fill=(160,170,195))
    rungs=[(3,"Klein quartic","PSL(2,7)",168,"24 heptagons"),
           (7,"Macbeath surface","PSL(2,8)",504,"the next one up"),
           (14,"first Hurwitz triplet","PSL(2,13)",1092,"three surfaces at once")]
    y0=260; dy=240
    for i,(g,name,grp,order,note) in enumerate(rungs):
        cy=y0+dy*i
        hue=0.58-0.16*i; r,gg,b=colorsys.hsv_to_rgb(hue%1,0.55,1.0); col=(int(r*255),int(gg*255),int(b*255))
        # rung disk sized ~ sqrt(order)
        R=40+ (order/1092)**0.5*70
        cxk=180
        d.ellipse([cxk-R-8,cy-R-8,cxk+R+8,cy+R+8],fill=col+(40,))
        d.ellipse([cxk-R,cy-R,cxk+R,cy+R],fill=col+(70,),outline=col+(255,),width=4)
        gt=f"g={g}"; wgt=d.textlength(gt,font=fg); a=fg.getbbox(gt)
        d.text((cxk-wgt/2,cy-(a[3]-a[1])/2-a[1]),gt,font=fg,fill=(255,255,255))
        # text block
        tx=340
        d.text((tx,cy-72),name,font=fg,fill=(235,240,250))
        d.text((tx,cy-14),f"{grp}      | G | = {order}  =  84 · {g-1}",font=fm,fill=col)
        d.text((tx,cy+34),note,font=fsm,fill=(160,168,190))
    # common-source note at bottom of viz
    d.line([(80,y0+dy*3-60),(W-80,y0+dy*3-60)],fill=(50,55,72,255),width=3)
    d.text((90,y0+dy*3-36),"every one is a quotient of the (2,3,7) triangle group",font=fm,fill=(180,190,210))
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("How much symmetry can a surface have? For genus g ≥ 2, Hurwitz proved a hard ceiling: at "
          "most 84(g−1) orientation-preserving symmetries. A surface that hits the ceiling is "
          "called a HURWITZ surface, and its symmetry group a Hurwitz group. The Klein quartic is "
          "the very first: genus 3, 84·2 = 168 = PSL(2,7). The next possible genus is 7, giving "
          "504 = PSL(2,8), the Macbeath surface. Then genus 14 with 1092 = PSL(2,13) — and "
          "remarkably it is achieved by THREE different surfaces at once (the first Hurwitz "
          "triplet). The genera that admit a Hurwitz group are sparse and irregular, but the list "
          "is infinite. The unifying fact: every Hurwitz surface is the (2,3,7) triangle-group "
          "tiling — the same heptagons — rolled up by a different finite quotient. 168 was not a "
          "coincidence; it was the first note of an endless, uneven scale.")
    fig=figkit.caption(viz,"HURWITZ · THE BOUND","84(g−1): the most symmetric surfaces",
                       body,accent=(255,225,140))
    figkit.save(fig,"hurwitz/01_hurwitz_chain.png")
    print("done",fig.size)
