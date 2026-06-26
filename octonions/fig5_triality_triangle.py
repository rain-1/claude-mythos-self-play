"""Figure 5 — the triality triangle (representation-theory lens).
so(8) has three inequivalent 8-dim irreps: 8_v (vector), 8_s, 8_c (spinors).
Octonion multiplication is a triality-equivariant trilinear form coupling all
three; triality is the order-3 outer automorphism cycling them."""
import numpy as np, sys, math
sys.path.insert(0,'octonions'); sys.path.insert(0,'triality')
import figkit
from tdraw import Canvas
from PIL import ImageDraw

CV=np.array([70,190,255])/255; CS=np.array([255,200,80])/255; CC=np.array([255,95,180])/255

def render(W=1600):
    Hh=1500; cx=W/2; cy=Hh*0.46
    R=Hh*0.32
    ang=[90,210,330]; cols=[CV,CS,CC]
    names=["8ᵥ","8ₛ","8c"]; longn=["vector","spinor","co-spinor"]
    P=[(cx+R*math.cos(math.radians(a)), cy-R*math.sin(math.radians(a))) for a in ang]
    cv=Canvas(W,bg=(0.012,0.013,0.025))
    # lines from each space into the central trilinear form
    for k in range(3):
        cv.line(P[k],(cx,cy),cols[k]*0.7,cols[k],width=2.4,bright=0.33)
    # chiral triality 3-cycle (outer ring arcs)
    rr=R*1.16
    for k in range(3):
        a0=math.radians(ang[k])+math.radians(26); a1=math.radians(ang[(k+1)%3])-math.radians(26)
        # go the short chiral way (decreasing angle in screen = +120 visual)
        sweep=((a1-a0)%(2*math.pi))
        N=40
        for i in range(N-1):
            t0=i/(N-1); t1=(i+1)/(N-1)
            aa0=a0+sweep*t0; aa1=a0+sweep*t1
            p0=(cx+rr*math.cos(aa0), cy-rr*math.sin(aa0)); p1=(cx+rr*math.cos(aa1), cy-rr*math.sin(aa1))
            c=cols[k]*(1-t0)+cols[(k+1)%3]*t0
            cv.line(p0,p1,c,c,width=3.0,bright=0.5)
    # nodes
    for k in range(3):
        cv.splat(P[k],cols[k],radius=W*0.052,bright=0.9)
        cv.splat(P[k],(1,1,1),radius=W*0.016,bright=0.7)
    cv.splat((cx,cy),(0.85,0.9,1.0),radius=W*0.030,bright=0.8)
    img=cv.finish(W,bloom=(W*0.0008+0.6,W*0.007),gloss=(0.5,0.3),expo=1.18)
    d=ImageDraw.Draw(img)
    # arrowheads at the leading end of each triality arc (chirality)
    rgb=lambda c:tuple(int(255*v) for v in c)
    for k in range(3):
        a1=math.radians(ang[(k+1)%3])-math.radians(26)
        tip=(cx+rr*math.cos(a1), cy-rr*math.sin(a1))
        # tangent direction of travel (screen y inverted): d/da (cos, -sin) = (-sin, -cos)
        tx,ty=-math.sin(a1), -math.cos(a1)
        ang0=math.atan2(ty,tx); sz=26; sp=math.radians(28)
        q1=(tip[0]-sz*math.cos(ang0-sp), tip[1]-sz*math.sin(ang0-sp))
        q2=(tip[0]-sz*math.cos(ang0+sp), tip[1]-sz*math.sin(ang0+sp))
        d.polygon([tip,q1,q2],fill=rgb(cols[(k+1)%3]))
    fb=figkit.font("DejaVuSans-Bold.ttf",62); fs=figkit.font("DejaVuSans.ttf",32)
    fc=figkit.font("DejaVuSans-Bold.ttf",44); feq=figkit.font("DejaVuSans-Bold.ttf",38)
    def ctext(x,y,t,f,fill):
        w=d.textlength(t,font=f); a=f.getbbox(t); d.text((x-w/2,y-(a[3]-a[1])/2-a[1]),t,font=f,fill=fill)
    for k in range(3):
        ctext(P[k][0],P[k][1]-10,names[k],fb,(12,14,22))
        ctext(P[k][0],P[k][1]+44,longn[k],fs,(20,22,30))
    ctext(cx,cy,"t",fc,(20,24,34))
    # arrow label for the 3-cycle
    ctext(cx,cy-R*1.42,"triality  (order 3)",fs,(200,210,235))
    eq="t(x, y, z) = ⟨ x · y , z ⟩      — one invariant, symmetric under  8ᵥ → 8ₛ → 8c"
    w=d.textlength(eq,font=feq); d.text((cx-w/2, Hh-70),eq,font=feq,fill=(225,232,245))
    return img.crop((0,0,W,Hh))

if __name__=="__main__":
    viz=render(1600)
    body=("Unlike every other rotation algebra, so(8) has THREE different 8-dimensional irreducible "
          "representations: the vector rep 8ᵥ and two spinor reps 8ₛ, 8c. Octonion multiplication "
          "ties them together: the map (x, y) ↦ x·y sends 8ᵥ × 8ₛ into 8c, and packaged as the "
          "trilinear form t(x,y,z) = ⟨x·y, z⟩ it is a single Spin(8)-invariant that treats all "
          "three spaces symmetrically. TRIALITY is the order-3 outer automorphism that cyclically "
          "permutes them, 8ᵥ → 8ₛ → 8c → 8ᵥ — the unique 3-fold symmetry no other simple Lie "
          "algebra possesses. It exists precisely because, in eight dimensions, vectors and "
          "spinors have the same size and the octonions supply the product that braids them.")
    fig=figkit.caption(viz,"FIGURE 5 · REPRESENTATION THEORY","The triality triangle of Spin(8)",
                       body,accent=(180,160,255))
    figkit.save(fig,"octonions/05_triality_triangle.png")
    print("done",fig.size)
