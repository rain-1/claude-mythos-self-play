# All 25 kinds of decomposition of the 4-cube (up to Aut(Q4) and reversal), each drawn in its most symmetric pose.
import sys, json, itertools, numpy as np, math
from PIL import Image, ImageDraw
import koi, scene
W=int(sys.argv[1]); ss=int(sys.argv[2]); out=sys.argv[3]
J=json.load(open('../math_cube/solutions.json'))['d4_orbit_representatives']
def canon(c):
    i=c.index(0); return tuple(c[i:]+c[:i])
def key(S): return frozenset(canon(list(c)) for c in S)
def rev(S): return [list(reversed(c)) for c in S]
auts=[]
for p in itertools.permutations(range(4)):
    for f in range(16):
        auts.append(lambda v,p=p,f=f: sum((((v>>i)&1)<<p[i]) for i in range(4))^f)
s8=lambda v:(v>>1)|((1-(v&1))<<3)
def refl(v):
    x=[(v>>i)&1 for i in range(4)]; y=[x[0],1-x[3],1-x[2],1-x[1]]
    return sum(y[i]<<i for i in range(4))
D8=[]
for k in range(8):
    def rot(v,k=k):
        for _ in range(k): v=s8(v)
        return v
    D8.append(rot); D8.append(lambda v,rot=rot: rot(refl(v)))
def app(g,S): return [[g(v) for v in c] for c in S]
items=[]
for o in J:
    S=o['cycles']; best=None; seen=set()
    for g in auts:
        for T in (app(g,S), rev(app(g,S))):
            k=key(T)
            if k in seen: continue
            seen.add(k)
            sc=0
            for h in D8:
                kk=key(app(h,T))
                if kk==k: sc+=1
                elif kk==key(rev(T)): sc+=0.5
            if best is None or sc>best[0]: best=(sc,T)
    assert len(seen)==o['orbit_size_Aut_x_reversal'], (len(seen), o['orbit_size_Aut_x_reversal'])
    # order cycles so colours are stable: by first step from 0
    T=sorted([list(canon(c)) for c in best[1]], key=lambda c:c[1])
    items.append(dict(orbit=o['orbit'],size=len(seen),sym=best[0],S=T,paired=o['paired_type_cycle_plus_reverse'],chiral=o['chiral_not_equivalent_to_own_reversal']))
    print(o['orbit'],len(seen),best[0],o['paired_type_cycle_plus_reverse'],flush=True)
assert sum(i['size'] for i in items)==3312
items.sort(key=lambda i:(i['orbit']!=19, i['size'], -i['sym'], i['orbit']))
pos=scene.warp(scene.petrie(4),0.85)
m=int(W*0.014); cell=(W-2*m)//5; lab=int(cell*0.085); top=int(W*0.012)
H=top+5*(cell+lab)+int(W*0.105)
can=np.broadcast_to((koi.PAPER*255).astype(np.uint8),(H,W,3)).copy()
for n,it in enumerate(items):
    sc=scene.build(pos,it['S'],[0,1,2,3],seed=20+n,R=1.56,ppu=1/3.50,center=(0.5,0.5),flen=0.30,fw=0.031,fish_per_edge=0.75,pad_r=0.105,
                   petals=14,ripples=2,trail_w=0.040)
    img=koi.finish(koi.render(sc,cell,cell,ss=ss,strip=512,quiet=True),seed=n)
    r,c=divmod(n,5); y=top+r*(cell+lab); x=m+c*cell
    can[y:y+cell,x:x+cell]=img
im=Image.fromarray(can); dr=ImageDraw.Draw(im)
def ctext(cx,y,text,fn,sz,col=(92,77,102)):
    f=scene.font(fn,int(sz*W)); w=dr.textlength(text,font=f); dr.text((cx-w/2,y),text,font=f,fill=col)
for n,it in enumerate(items):
    r,c=divmod(n,5); y=top+r*(cell+lab)+cell-int(cell*0.012); x=m+c*cell+cell/2
    t=f"{it['size']} ways"
    extra=[]
    if it['paired']: extra.append("two loops, each swum both ways")
    if it['chiral']: extra.append("with its backwards twin")
    if it['orbit']==19: extra.append("the large pond")
    col=(232,96,80) if it['orbit']==19 else (92,77,102)
    ctext(x,y,t+("  ·  "+", ".join(extra) if extra else ""),'FreeSerifItalic',0.0105,col)
yb=top+5*(cell+lab)+int(W*0.004)
ctext(W/2,yb,"Twenty-Five Ponds",'FreeSerifBold',0.0300)
ctext(W/2,yb+0.040*W,"Every way to stock sixteen pads with four schools. Turning the cube, mirroring it, or sending every fish backwards does not make a new pond. Counted that way, the 3,312 ways are 25 kinds.",'FreeSerifItalic',0.0135)
ctext(W/2,yb+0.063*W,"each kind is shown in its most symmetric pose  ·  the number under a pond is how many of the 3,312 it stands for  ·  only five kinds are the easy answer, two loops each swum in both directions",'FreeSerifItalic',0.0105,(140,126,150))
im.save(out,optimize=True)
