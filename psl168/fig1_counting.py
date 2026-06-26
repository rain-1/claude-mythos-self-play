"""Figure 1 — where 168 comes from (counting lens)."""
import numpy as np, sys, math
sys.path.insert(0,'psl168'); sys.path.insert(0,'octonions'); sys.path.insert(0,'triality')
import p168, figkit
from tdraw import Canvas
from PIL import ImageDraw
import colorsys

def linecol(k):
    r,g,b=colorsys.hsv_to_rgb(k/7.0,0.62,1.0); return np.array([r,g,b])

def heptagon_pos(cx,cy,R):
    return {i:(cx+R*math.cos(-2*math.pi*i/7+math.pi/2), cy-R*math.sin(-2*math.pi*i/7+math.pi/2)) for i in range(7)}

def render(W=1600):
    Hh=1180
    cv=Canvas(W,bg=(0.012,0.013,0.025))
    cx,cy,R=W*0.5, Hh*0.46, Hh*0.33
    pos=heptagon_pos(cx,cy,R)
    lines=p168.fano_cyclic_lines()
    for k,L in enumerate(lines):
        col=linecol(k); pts=[pos[i] for i in L]
        for a in range(3):
            cv.line(pts[a],pts[(a+1)%3],col,col,width=2.2,bright=0.34)
    for i in range(7):
        cv.splat(pos[i],(0.9,0.93,1.0),radius=W*0.013,bright=1.6)
        cv.splat(pos[i],(1,1,1),radius=W*0.005,bright=1.3)
    img=cv.finish(W,bloom=(W*0.0007+0.6,W*0.006),gloss=(0.5,0.3),expo=1.2)
    d=ImageDraw.Draw(img)
    fp=figkit.font("DejaVuSans-Bold.ttf",34)
    for i in range(7):
        x,y=pos[i]; dx,dy=x-cx,y-cy; n=math.hypot(dx,dy)
        lx,ly=x+dx/n*44,y+dy/n*44
        w=d.textlength(str(i),font=fp); d.text((lx-w/2,ly-20),str(i),font=fp,fill=(210,216,235))
    # Singer rotation arrow (z -> z+1 mod 7)
    fr=figkit.font("DejaVuSans.ttf",30)
    d.text((cx-150,cy-26),"Singer cycle",font=fr,fill=(170,180,205))
    d.text((cx-150,cy+10),"z → z+1",font=figkit.font("DejaVuSans-Bold.ttf",34),fill=(255,210,120))
    # counting equation (right side / below heptagon area)
    fe=figkit.font("DejaVuSans-Bold.ttf",46); fs=figkit.font("DejaVuSans.ttf",32)
    d.text((70,Hh-150),"| Aut(Fano) | = | GL(3,2) |",font=fe,fill=(235,240,250))
    d.text((70,Hh-92),"= (8−1)(8−2)(8−4) = 7 · 6 · 4 = 168",font=fe,fill=(255,210,120))
    return img.crop((0,0,W,Hh))

if __name__=="__main__":
    viz=render(1600)
    body=("Here is the Fano plane in its most symmetric dress: the 7 points are 0…6 on a circle, "
          "and the 7 lines are the translates of the single block {1,2,4} — the quadratic residues "
          "mod 7 — under the rotation z → z+1 (the Singer cycle). How many symmetries does it have? "
          "A symmetry is any relabelling of the 7 points that sends lines to lines, and these are "
          "exactly the invertible linear maps of the 3-bit space F₂³ (the cube of the previous "
          "gallery). Counting them is easy: the first basis vector can be any of 8−1 non-zero "
          "vectors, the second any of 8−2 outside its span, the third any of 8−4 outside their "
          "plane — so |GL(3,2)| = 7·6·4 = 168. This group is PSL(3,2), and it is SIMPLE: the "
          "second-smallest non-abelian simple group after A₅. Everything that follows is 168 "
          "wearing different masks.")
    fig=figkit.caption(viz,"FIGURE 1 · COUNTING","168 = the symmetries of the Fano plane",
                       body,accent=(255,210,120))
    figkit.save(fig,"psl168/01_counting_168.png")
    print("done",fig.size)
