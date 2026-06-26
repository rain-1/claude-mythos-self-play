"""Animation — the Singer cycle. All 7 Fano lines are translates of one block
{1,2,4} (the quadratic residues mod 7) under z -> z+1. We step the highlight
through k = 0..6 and the single block sweeps out the entire plane."""
import numpy as np, sys, math
sys.path.insert(0,'psl168'); sys.path.insert(0,'triality'); sys.path.insert(0,'octonions')
import p168, figkit
from tdraw import Canvas
from PIL import Image, ImageDraw
import colorsys

def heptpos(cx,cy,R):
    return {i:(cx+R*math.cos(-2*math.pi*i/7+math.pi/2), cy-R*math.sin(-2*math.pi*i/7+math.pi/2)) for i in range(7)}

def frame(k,S=560,ss=2):
    W=S*ss; cx=cy=W/2; R=W*0.34
    pos=heptpos(cx,cy,R)
    lines=p168.fano_cyclic_lines()
    cv=Canvas(W,bg=(0.012,0.013,0.025))
    # all lines faint
    for L in lines:
        for a in range(3):
            cv.line(pos[L[a]],pos[L[(a+1)%3]],(0.5,0.55,0.7),(0.5,0.55,0.7),width=2.0*ss,bright=0.14)
    # highlighted block {1,2,4}+k
    base=tuple(sorted((q+k)%7 for q in p168.QR7))
    r,g,b=colorsys.hsv_to_rgb((k/7.0),0.6,1.0); col=np.array([r,g,b])
    for a in range(3):
        cv.line(pos[base[a]],pos[base[(a+1)%3]],col,col,width=3.4*ss,bright=0.6)
    for i in range(7):
        c=(1.0,0.95,0.5) if i in base else (0.85,0.88,1.0)
        cv.splat(pos[i],c,radius=W*0.014,bright=1.6 if i in base else 1.2)
        cv.splat(pos[i],(1,1,1),radius=W*0.005,bright=1.2)
    img=cv.finish(S,bloom=(W*0.0008+0.6,W*0.006),gloss=(0.5,0.3),expo=1.2)
    d=ImageDraw.Draw(img); f=figkit.font("DejaVuSans-Bold.ttf",int(S*0.05))
    for i in range(7):
        x,y=pos[i]; x/=ss; y/=ss
        dx,dy=x-S/2,y-S/2; n=math.hypot(dx,dy)
        lx,ly=x+dx/n*30,y+dy/n*30; w=d.textlength(str(i),font=f)
        d.text((lx-w/2,ly-18),str(i),font=f,fill=(220,225,240))
    lab=f"{{1,2,4}} + {k}  =  {{{base[0]},{base[1]},{base[2]}}}"
    fb=figkit.font("DejaVuSans-Bold.ttf",int(S*0.05))
    w=d.textlength(lab,font=fb); d.text((S/2-w/2,S-int(S*0.10)),lab,font=fb,fill=(int(r*255),int(g*255),int(b*255)))
    return img

def main():
    frames=[frame(k).convert("P",palette=Image.ADAPTIVE,colors=128) for k in range(7)]
    frames[0].save("psl168/anim_singer_cycle.gif",save_all=True,append_images=frames[1:],
                   duration=620,loop=0,optimize=True,disposal=2)
    print("done")

if __name__=="__main__":
    main()
