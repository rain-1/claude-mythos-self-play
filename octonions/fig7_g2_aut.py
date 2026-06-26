"""Figure 7 — G2 = Aut(O): the symmetry that ties it all together (Lie lens).
Left: the Fano plane = octonion multiplication. Right: the G2 root system.
The continuous symmetries preserving octonion multiplication form the smallest
exceptional Lie group G2 (dim 14) — which is ALSO the subgroup of Spin(8) fixed
by triality. Fano + octonions + triality, one object."""
import numpy as np, sys, math
sys.path.insert(0,'octonions'); sys.path.insert(0,'triality')
import octo, figkit
from tdraw import Canvas
from PIL import ImageDraw

def render(W=1600):
    Hh=980
    cv=Canvas(W,bg=(0.012,0.013,0.025))
    rgb=lambda k,f=1.0:tuple(min(1.0,v*f) for v in octo.UNIT_RGB[k])
    # ---- left: Fano plane ----
    cxf,cyf,r = W*0.27, Hh*0.5, Hh*0.30
    pos={}
    for lab,a in {2:90,4:210,7:330}.items():
        pos[lab]=(cxf+r*math.cos(math.radians(a)), cyf-r*math.sin(math.radians(a)))
    pos[1]=(cxf,cyf)
    pos[6]=tuple((np.array(pos[2])+np.array(pos[4]))/2)
    pos[5]=tuple((np.array(pos[2])+np.array(pos[7]))/2)
    pos[3]=tuple((np.array(pos[4])+np.array(pos[7]))/2)
    for (x,y,z) in [(2,6,4),(2,5,7),(4,3,7),(2,1,3),(4,1,5),(7,1,6)]:
        cv.line(pos[x],pos[z],(0.6,0.64,0.78),(0.6,0.64,0.78),width=2.4,bright=0.34)
    # incircle
    for t in range(72):
        a0=2*math.pi*t/72; a1=2*math.pi*(t+1)/72
        p0=(cxf+r/2*math.cos(a0),cyf-r/2*math.sin(a0)); p1=(cxf+r/2*math.cos(a1),cyf-r/2*math.sin(a1))
        cv.line(p0,p1,(0.6,0.64,0.78),(0.6,0.64,0.78),width=2.4,bright=0.34)
    for k,p in pos.items():
        cv.splat(p,rgb(k),radius=W*0.013,bright=1.5); cv.splat(p,(1,1,1),radius=W*0.004,bright=1.2)
    # ---- right: G2 root system ----
    cxg,cyg = W*0.73, Hh*0.5; sc=Hh*0.30
    WARM=np.array([255,200,90])/255; COOL=np.array([90,200,255])/255
    short=np.array([(math.cos(math.radians(60*k)),math.sin(math.radians(60*k))) for k in range(6)])
    long =np.array([(math.sqrt(3)*math.cos(math.radians(30+60*k)),math.sqrt(3)*math.sin(math.radians(30+60*k))) for k in range(6)])
    s_scr=np.stack([cxg+short[:,0]*sc/1.732, cyg-short[:,1]*sc/1.732],1)
    l_scr=np.stack([cxg+long[:,0]*sc/1.732, cyg-long[:,1]*sc/1.732],1)
    for p in s_scr: cv.line((cxg,cyg),tuple(p),WARM*0.6,WARM,width=1.4,bright=0.2)
    for p in l_scr: cv.line((cxg,cyg),tuple(p),COOL*0.6,COOL,width=1.4,bright=0.2)
    for k in range(6): cv.line(tuple(s_scr[k]),tuple(s_scr[(k+1)%6]),WARM,WARM,width=1.8,bright=0.38)
    for k in range(6): cv.line(tuple(l_scr[k]),tuple(l_scr[(k+2)%6]),COOL,COOL,width=1.8,bright=0.38)
    for p in s_scr: cv.splat(tuple(p),WARM,radius=W*0.011,bright=1.5); cv.splat(tuple(p),(1,1,1),radius=W*0.0035,bright=1.1)
    for p in l_scr: cv.splat(tuple(p),COOL,radius=W*0.011,bright=1.5); cv.splat(tuple(p),(1,1,1),radius=W*0.0035,bright=1.1)
    cv.splat((cxg,cyg),(1.0,0.43,0.7),radius=W*0.016,bright=0.7)
    img=cv.finish(W,bloom=(W*0.0007+0.6,W*0.006),gloss=(0.5,0.3),expo=1.2)
    d=ImageDraw.Draw(img)
    fs=figkit.font("DejaVuSans.ttf",30)
    # top-banner equation
    eq="Aut(𝕆)   =   G₂"
    fe=figkit.font("DejaVuSans-Bold.ttf",58)
    w=d.textlength(eq,font=fe); d.text((W/2-w/2, 30),eq,font=fe,fill=(235,240,250))
    # connector between panels
    fcon=figkit.font("DejaVuSans-Bold.ttf",60)
    d.text((W/2-22, Hh*0.5-40),"≅",font=fcon,fill=(150,160,185))
    d.text((W*0.27-150, Hh-64),"the Fano product",font=fs,fill=(180,188,208))
    d.text((W*0.73-160, Hh-64),"the G₂ root system",font=fs,fill=(180,188,208))
    return img.crop((0,0,W,Hh))

if __name__=="__main__":
    viz=render(1600)
    body=("Ask which continuous symmetries preserve the octonion product — the rotations g of the "
          "7-dimensional space of imaginary octonions with g(x)·g(y) = g(x·y) for all x, y. The "
          "answer is the smallest of the five exceptional Lie groups: G₂, of dimension 14. Its root "
          "system (right) is the densest rank-2 system — 6 short roots in a hexagon, 6 long roots in "
          "a hexagram — and its smallest non-trivial representation is exactly the 7 imaginary units "
          "of the Fano plane (left). G₂ is where the three threads of this gallery meet: it is "
          "Aut(𝕆), the symmetry group of the Fano multiplication, and it is also the subgroup of "
          "Spin(8) left fixed by triality. The exceptional begins exactly where the octonions do.")
    fig=figkit.caption(viz,"FIGURE 7 · LIE THEORY","G₂ = the symmetries of the octonions",
                       body,accent=(255,205,90))
    figkit.save(fig,"octonions/07_g2_automorphisms.png")
    print("done",fig.size)
