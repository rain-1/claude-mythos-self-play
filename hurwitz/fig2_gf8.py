"""Hurwitz Fig 2 — GF(8), the field behind PSL(2,8), and its Fano-plane heart."""
import numpy as np, sys, math
sys.path.insert(0,'hurwitz'); sys.path.insert(0,'octonions'); sys.path.insert(0,'triality')
import figkit
from tdraw import Canvas
from PIL import ImageDraw
import colorsys

def gf8_mul(a,b):
    r=0
    for _ in range(3):
        if b&1: r^=a
        b>>=1; a<<=1
        if a&0b1000: a^=0b1011   # x^3 = x+1
    return r&0b111

def render(W=1600):
    Hh=1120
    # powers of alpha=x=2
    powers=[1];
    for _ in range(6): powers.append(gf8_mul(powers[-1],2))
    # powers = [1,2,4,3,6,7,5] = alpha^0..alpha^6
    cx,cy,R=W*0.5,Hh*0.46,Hh*0.33
    pos={powers[k]:(cx+R*math.cos(-2*math.pi*k/7+math.pi/2), cy-R*math.sin(-2*math.pi*k/7+math.pi/2)) for k in range(7)}
    cv=Canvas(W,bg=(0.012,0.013,0.025))
    # additive Fano lines: triples a,b,c nonzero with a^b^c=0
    from itertools import combinations
    GOLD=np.array([1.0,0.78,0.32])
    for a,b,c in combinations([1,2,3,4,5,6,7],3):
        if a^b^c==0:
            P=[pos[a],pos[b],pos[c]]
            for t in range(3): cv.line(P[t],P[(t+1)%3],GOLD*0.8,GOLD*0.8,width=1.6,bright=0.14)
    # multiplicative 7-cycle z->alpha z (rotation around heptagon)
    CY=np.array([0.4,0.8,1.0])
    for k in range(7):
        cv.line(pos[powers[k]],pos[powers[(k+1)%7]],CY,CY,width=2.4,bright=0.30)
    for v in pos:
        cv.splat(pos[v],(0.9,0.93,1.0),radius=W*0.012,bright=1.6); cv.splat(pos[v],(1,1,1),radius=W*0.004,bright=1.2)
    cv.splat((cx,cy),(1.0,0.5,0.7),radius=W*0.016,bright=1.0)        # 0 at centre
    img=cv.finish(W,bloom=(W*0.0007+0.6,W*0.006),gloss=(0.5,0.3),expo=1.2)
    d=ImageDraw.Draw(img); f=figkit.font("DejaVuSans-Bold.ttf",30); fs=figkit.font("DejaVuSans.ttf",27)
    for k in range(7):
        v=powers[k]; x,y=pos[v]; dx,dy=x-cx,y-cy; n=math.hypot(dx,dy)
        lab=("1" if k==0 else ("α" if k==1 else f"α{chr(0x2070+ (k if k<10 else 0))}".replace('α'+chr(0x2070),'α')))
        lab="α"+["⁰","¹","²","³","⁴","⁵","⁶"][k]
        d.text((x+dx/n*42-18,y+dy/n*42-16),lab,font=f,fill=(210,216,235))
    d.text((cx+14,cy-12),"0",font=f,fill=(255,170,200))
    # facts
    fe=figkit.font("DejaVuSans-Bold.ttf",36)
    d.text((60,Hh-120),"GF(8) = 𝔽₂[x]/(x³+x+1)",font=fe,fill=(235,240,250))
    d.text((60,Hh-72),"additive group = 𝔽₂³ (Fano)   ·   multiplicative group = C₇ (Singer)",font=fs,fill=(180,188,208))
    d.text((W-560,Hh-120),"| PSL(2,8) | = 8·9·7 = 504",font=fe,fill=(255,225,140))
    d.text((W-560,Hh-72),"acts on ℙ¹(GF(8)) = 9 points",font=fs,fill=(180,188,208))
    return img.crop((0,0,W,Hh))

if __name__=="__main__":
    viz=render(1600)
    body=("The Macbeath surface's group PSL(2,8) is built from the field of 8 elements, GF(8) = "
          "𝔽₂[x]/(x³+x+1). That field is secretly an old friend. Its eight elements added together "
          "(addition is just XOR of 3-bit strings) are precisely 𝔽₂³ — the Fano plane plus a zero "
          "(gold lines). Its seven NON-zero elements multiplied are the cyclic group C₇: powers of "
          "a single primitive element α run α⁰, α¹, …, α⁶ and back, the Singer cycle (blue ring) "
          "that rotated the Fano plane in the very first figure of the last gallery. So one finite "
          "field carries both the additive Fano geometry and its multiplicative symmetry at once. "
          "PSL(2,8) then acts as Möbius maps on the 9 points of the projective line ℙ¹(GF(8)), with "
          "order 8·9·7 = 504 = 84·6 — the Hurwitz group of genus 7.")
    fig=figkit.caption(viz,"HURWITZ · THE FIELD","GF(8): a field whose heart is the Fano plane",
                       body,accent=(150,200,255))
    figkit.save(fig,"hurwitz/02_gf8.png")
    print("done",fig.size)
