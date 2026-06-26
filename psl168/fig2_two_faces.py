"""Figure 2 — two faces of the same group of order 168 (isomorphism lens)."""
import numpy as np, sys, math
sys.path.insert(0,'psl168'); sys.path.insert(0,'octonions'); sys.path.insert(0,'triality')
import p168, figkit
from tdraw import Canvas
from PIL import ImageDraw
import colorsys

def linecol(k):
    r,g,b=colorsys.hsv_to_rgb(k/7.0,0.6,1.0); return np.array([r,g,b])

def render(W=1600):
    Hh=1020
    cv=Canvas(W,bg=(0.012,0.013,0.025))
    # ---- left: Fano (7 points, 7 lines) ----
    cxf,cyf,Rf=W*0.265,Hh*0.52,Hh*0.31
    pf={i:(cxf+Rf*math.cos(-2*math.pi*i/7+math.pi/2), cyf-Rf*math.sin(-2*math.pi*i/7+math.pi/2)) for i in range(7)}
    for k,L in enumerate(p168.fano_cyclic_lines()):
        col=linecol(k); pts=[pf[i] for i in L]
        for a in range(3): cv.line(pts[a],pts[(a+1)%3],col,col,width=2.0,bright=0.30)
    for i in range(7):
        cv.splat(pf[i],(0.9,0.93,1.0),radius=W*0.012,bright=1.6); cv.splat(pf[i],(1,1,1),radius=W*0.004,bright=1.2)
    # ---- right: P^1(F_7): 0..6 on circle, inf at centre ----
    cxg,cyg,Rg=W*0.735,Hh*0.52,Hh*0.31
    pg={i:(cxg+Rg*math.cos(-2*math.pi*i/7+math.pi/2), cyg-Rg*math.sin(-2*math.pi*i/7+math.pi/2)) for i in range(7)}
    pg[p168.INF]=(cxg,cyg)
    GOLD=np.array([1.0,0.8,0.35]); CYAN=np.array([0.35,0.78,1.0])
    # involution z->-1/z : (0 inf)(1 6)(2 3)(4 5) as cyan chords
    for a,b in [(0,p168.INF),(1,6),(2,3),(4,5)]:
        cv.line(pg[a],pg[b],CYAN,CYAN,width=2.4,bright=0.34)
    # z->z+1 ring (gold) around the 7 finite points
    for i in range(7):
        cv.line(pg[i],pg[(i+1)%7],GOLD,GOLD,width=2.2,bright=0.30)
    for i in range(7):
        cv.splat(pg[i],(0.9,0.93,1.0),radius=W*0.012,bright=1.6); cv.splat(pg[i],(1,1,1),radius=W*0.004,bright=1.2)
    cv.splat(pg[p168.INF],(1.0,0.5,0.7),radius=W*0.014,bright=1.4)
    img=cv.finish(W,bloom=(W*0.0007+0.6,W*0.006),gloss=(0.5,0.3),expo=1.2)
    d=ImageDraw.Draw(img)
    fe=figkit.font("DejaVuSans-Bold.ttf",54); fs=figkit.font("DejaVuSans.ttf",30); fp=figkit.font("DejaVuSans-Bold.ttf",30)
    eq="PSL(3,2)   ≅   PSL(2,7)        | G | = 168"
    w=d.textlength(eq,font=fe); d.text((W/2-w/2,26),eq,font=fe,fill=(235,240,250))
    d.text((W/2-20,Hh*0.52-36),"≅",font=figkit.font("DejaVuSans-Bold.ttf",60),fill=(150,160,185))
    for i in range(7):
        for pos,c in [(pf,(200,210,235)),(pg,(200,210,235))]:
            x,y=pos[i]; cc=(cxf,cyf) if pos is pf else (cxg,cyg)
            dx,dy=x-cc[0],y-cc[1]; n=math.hypot(dx,dy)
            lx,ly=x+dx/n*40,y+dy/n*40; w=d.textlength(str(i),font=fp)
            d.text((lx-w/2,ly-18),str(i),font=fp,fill=c)
    d.text((pg[p168.INF][0]+18,pg[p168.INF][1]-12),"∞",font=fp,fill=(255,170,200))
    d.text((cxf-150,Hh-44),"7 points · 7 lines",font=fs,fill=(180,188,208))
    d.text((cxg-190,Hh-44),"8 points on the line P¹(𝔽₇)",font=fs,fill=(180,188,208))
    # legend for right
    d.text((cxg-200,Hh-92),"gold: z→z+1   cyan: z→−1/z",font=figkit.font("DejaVuSans.ttf",26),fill=(150,158,180))
    return img.crop((0,0,W,Hh))

if __name__=="__main__":
    viz=render(1600)
    body=("The group of order 168 has two completely different natural homes, and they are the same "
          "group. On the LEFT it is PSL(3,2): symmetries of the 7-point Fano plane, i.e. linear "
          "algebra over the 2-element field 𝔽₂. On the RIGHT it is PSL(2,7): Möbius transformations "
          "z ↦ (az+b)/(cz+d) acting on the projective line over the 7-element field 𝔽₇, which has "
          "8 points (0,1,…,6 and ∞). Two generators suffice there — the translation z→z+1 (a "
          "7-cycle around the rim, gold) and the inversion z→−1/z (the involution (0 ∞)(1 6)(2 3)"
          "(4 5), cyan). That a group built from 𝔽₂ in dimension 3 equals one built from 𝔽₇ in "
          "dimension 2 is a small miracle — one of the exceptional isomorphisms between the "
          "families of finite simple groups.")
    fig=figkit.caption(viz,"FIGURE 2 · THE ISOMORPHISM","One group of order 168, two worlds",
                       body,accent=(150,200,255))
    figkit.save(fig,"psl168/02_two_faces.png")
    print("done",fig.size)
