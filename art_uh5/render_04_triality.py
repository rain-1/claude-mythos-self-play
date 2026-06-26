"""04 — The Triality Engine (octonion Fano plane, tripled by triality).

The seven imaginary octonion units e_1..e_7 are the seven points of the Fano
plane (the smallest projective plane: 7 points, 7 lines, 3 points per line).
Each line is an oriented triple a->b->c meaning  e_a e_b = e_c  (reverse and
it negates) -- so the Fano plane literally IS the octonion multiplication table.
Here the abstract algebra is mapped onto the triangle's own geometry: the three
VERTICES, the three edge-MIDPOINTS, the CENTRE, and the INCIRCLE (the 7th line)
each carry a genuine octonion triple; medians run vertex->centre->opposite
midpoint.

Spin(8) has a unique order-3 outer automorphism -- TRIALITY -- cyclically
permuting its three 8-dimensional representations 8_v, 8_s, 8_c (octonion
multiplication 8_v x 8_s -> 8_c is the triality-equivariant map). So the emblem
is TRIPLED: three Fano planes pinwheeled at 120 degrees, one per representation,
cycled by the three central triality arrows around the D_4 hub.
"""
import numpy as np, math
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

LINES=[(1,2,3),(1,4,5),(1,7,6),(2,4,6),(2,5,7),(3,4,7),(3,6,5)]
CIRCLE=(3,6,5)
SUCC={}
for a,b,c in LINES:
    SUCC[(min(a,b),max(a,b),'')]=None  # placeholder
def succ_of(line):
    a,b,c=line; return {a:b,b:c,c:a}

def local_positions():
    P={}
    for lab,a in {2:90,4:210,7:330}.items():
        r=math.radians(a); P[lab]=np.array([math.cos(r),math.sin(r)])
    P[1]=np.array([0.0,0.0])
    P[6]=(P[2]+P[4])/2; P[5]=(P[2]+P[7])/2; P[3]=(P[4]+P[7])/2
    return P

def rot(v,deg):
    t=math.radians(deg); c,s=math.cos(t),math.sin(t)
    return np.array([c*v[0]-s*v[1], s*v[0]+c*v[1]])

def lerp(c1,c2,t): return tuple(int(round(c1[i]+(c2[i]-c1[i])*t)) for i in range(3))
def scale_col(c,f): return tuple(min(255,int(c[i]*f)) for i in range(3))

def arrowhead(d, p, ang, size, color):
    # p: tip point (x,y); ang: direction radians
    back=size; spread=math.radians(26)
    a1=ang+math.pi-spread; a2=ang+math.pi+spread
    q1=(p[0]+back*math.cos(a1), p[1]+back*math.sin(a1))
    q2=(p[0]+back*math.cos(a2), p[1]+back*math.sin(a2))
    d.polygon([p,q1,q2], fill=color)

def draw_fano(d, P0, scale, deg, base_col, W):
    """draw one Fano emblem centered at P0 (pixel), triangle radius=scale, rotated deg."""
    loc=local_positions()
    pos={lab: P0 + scale*rot(loc[lab],deg) for lab in loc}
    lw=max(2,int(scale*0.012))
    line_col=scale_col(base_col,0.85)
    # --- straight lines (sides + medians) ---
    for line in LINES:
        if line==CIRCLE: continue
        a,b,c=line
        pts=[a,b,c]
        # spatial order along the line
        o=sorted(pts, key=lambda L:(pos[L][0],pos[L][1]))
        # order by projecting onto principal axis
        dvec=pos[o[-1]]-pos[o[0]]; dvec=dvec/ (np.linalg.norm(dvec)+1e-9)
        o=sorted(pts, key=lambda L: np.dot(pos[L]-pos[o[0]],dvec))
        xy=[tuple(pos[o[0]]),tuple(pos[o[2]])]
        d.line(xy, fill=line_col, width=lw, joint='curve')
        # arrowheads on the two spatially-adjacent directed edges, per octonion cycle
        sc=succ_of(line)
        for (x,y) in [(o[0],o[1]),(o[1],o[2])]:
            if sc[x]==y: src,dst=x,y
            else: src,dst=y,x
            mid=(pos[src]+pos[dst])/2
            ang=math.atan2(pos[dst][1]-pos[src][1], pos[dst][0]-pos[src][0])
            tip=mid+0.06*scale*np.array([math.cos(ang),math.sin(ang)])
            arrowhead(d, tuple(tip), ang, scale*0.085, scale_col(base_col,1.15))
    # --- circle line (incircle through midpoints) ---
    cr=scale*0.5
    bb=[P0[0]-cr,P0[1]-cr,P0[0]+cr,P0[1]+cr]
    d.ellipse(bb, outline=line_col, width=lw)
    sc=succ_of(CIRCLE)
    mids=list(CIRCLE)
    angles={m: math.atan2(pos[m][1]-P0[1], pos[m][0]-P0[0]) for m in mids}
    mids_by_ang=sorted(mids, key=lambda m:angles[m]%(2*math.pi))
    n=len(mids_by_ang)
    for i in range(n):
        x=mids_by_ang[i]; y=mids_by_ang[(i+1)%n]
        if sc[x]==y: src,dst=x,y
        else: src,dst=y,x
        a0=angles[src]%(2*math.pi); a1=angles[dst]%(2*math.pi)
        # midpoint arc angle (shorter way)
        da=(a1-a0+math.pi)%(2*math.pi)-math.pi
        am=a0+da/2
        tip=(P0[0]+cr*math.cos(am), P0[1]+cr*math.sin(am))
        tang=am+math.pi/2*(1 if da>0 else -1)
        arrowhead(d, tip, tang, scale*0.075, scale_col(base_col,1.15))
    # --- nodes ---
    nr_v=scale*0.052; nr_m=scale*0.040; nr_c=scale*0.046
    roles={2:nr_v,4:nr_v,7:nr_v, 6:nr_m,5:nr_m,3:nr_m, 1:nr_c}
    try: font=ImageFont.truetype("DejaVuSans-Bold.ttf", int(scale*0.085))
    except Exception:
        try: font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(scale*0.085))
        except Exception: font=None
    for lab,nr in roles.items():
        x,y=pos[lab]
        core=scale_col(base_col,1.5)
        d.ellipse([x-nr,y-nr,x+nr,y+nr], fill=(min(255,core[0]+40),min(255,core[1]+40),min(255,core[2]+40)),
                  outline=(255,255,255), width=max(1,lw//2))
    return pos, font

def draw_labels(d, lobes, base_cols, scale):
    # draw e-index labels after all glow so they stay crisp; handled in main via overlay
    pass

def render(S=4096, ss=2, preview=False):
    W=S*ss
    cx=cy=W/2
    img=Image.new('RGB',(W,W),(0,0,0))
    d=ImageDraw.Draw(img)
    # background: radial vignette + faint rings
    bg=np.zeros((W,W,3),np.float32)
    yy,xx=np.mgrid[0:W,0:W]
    rr=np.sqrt((xx-cx)**2+(yy-cy)**2)/(W*0.5)
    base=np.clip(1.0-rr*0.9,0,1)
    bg[...,0]=0.012+0.020*base; bg[...,1]=0.016+0.028*base; bg[...,2]=0.030+0.055*base
    rings=0.5+0.5*np.cos(rr*40)
    bg+= (0.010*rings*np.exp(-rr*1.2))[...,None]*np.array([0.4,0.6,1.0])
    img=Image.fromarray((np.clip(bg,0,1)*255).astype('uint8'))
    d=ImageDraw.Draw(img,'RGBA')

    REPS=[((70,190,255),'8v'),((255,200,80),'8s'),((255,95,180),'8c')]  # v,s,c
    D=W*0.263; tri=W*0.137
    lobe_ang=[90,210,330]
    centers=[]
    # soft rep-colour halo behind each lobe (adds depth + colour; bloom spreads it)
    for k in range(3):
        a=math.radians(lobe_ang[k]); col=REPS[k][0]
        P0=(cx+D*math.cos(a), cy+D*math.sin(a)); hR=tri*1.25
        d.ellipse([P0[0]-hR,P0[1]-hR,P0[0]+hR,P0[1]+hR], fill=col+(26,))
    # D4 hub legs: connect central node to each lobe's inner edge (the Dynkin diagram)
    for k in range(3):
        a=math.radians(lobe_ang[k])
        legend=(cx+(D-tri*0.55)*math.cos(a), cy+(D-tri*0.55)*math.sin(a))
        d.line([(cx,cy),legend], fill=(170,195,255,150), width=max(2,int(W*0.0030)))
    # central triality arrows: three CHASING arcs (a chiral triskelion), gap near each leg
    rr2=W*0.100
    gap=math.radians(28)
    for k in range(3):
        a0=math.radians(lobe_ang[k])+gap
        a1=math.radians(lobe_ang[(k+1)%3])-gap
        sweep=(a1-a0)%(2*math.pi)
        c0=REPS[k][0]; c1=REPS[(k+1)%3][0]
        N=48
        for i in range(N-1):
            t0=i/(N-1); t1=(i+1)/(N-1)
            aa0=a0+sweep*t0; aa1=a0+sweep*t1
            p0=(cx+rr2*math.cos(aa0), cy+rr2*math.sin(aa0))
            p1=(cx+rr2*math.cos(aa1), cy+rr2*math.sin(aa1))
            d.line([p0,p1], fill=lerp(c0,c1,t0)+(230,), width=max(4,int(W*0.0062)))
        aa=a0+sweep*0.995
        tip=(cx+rr2*math.cos(aa), cy+rr2*math.sin(aa))
        arrowhead(d,tip,aa+math.pi/2,W*0.030,scale_col(c1,1.2)+(255,))
    hr=W*0.020
    d.ellipse([cx-hr,cy-hr,cx+hr,cy+hr], fill=(245,248,255), outline=(255,255,255), width=4)

    fonts=[]; poslist=[]
    for k in range(3):
        a=math.radians(lobe_ang[k])
        P0=np.array([cx+D*math.cos(a), cy+D*math.sin(a)])
        deg=lobe_ang[k]-90   # point triangle's top vertex radially outward
        pos,font=draw_fano(d,P0,tri,deg,REPS[k][0],W)
        poslist.append((pos,REPS[k][0])); fonts.append(font)
        centers.append((P0,REPS[k],a))

    arr=np.asarray(img).astype(np.float32)/255.0
    # bloom
    tight=np.stack([gaussian_filter(arr[...,c],W*0.0016) for c in range(3)],-1)
    wide =np.stack([gaussian_filter(arr[...,c],W*0.010) for c in range(3)],-1)
    glowed=arr+0.7*tight+0.35*wide
    glowed=1.0-np.exp(-1.3*glowed)
    out=Image.fromarray((np.clip(glowed,0,1)*255).astype('uint8'))
    # labels on top (crisp), after glow
    od=ImageDraw.Draw(out)
    if fonts[0] is not None:
        f=fonts[0]
        for (pos,col) in poslist:
            for lab,p in pos.items():
                txt=str(lab)
                bb=od.textbbox((0,0),txt,font=f)
                wgt=bb[2]-bb[0]; hgt=bb[3]-bb[1]
                od.text((p[0]-wgt/2-bb[0], p[1]-hgt/2-bb[1]), txt, font=f, fill=(8,10,18))
        # representation names outside each lobe
        try: bigf=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(tri*0.22))
        except Exception: bigf=f
        for (P0,(col,name),a) in centers:
            lp=(cx+(D+tri*1.30)*math.cos(a), cy+(D+tri*1.30)*math.sin(a))
            bb=od.textbbox((0,0),name,font=bigf); wgt=bb[2]-bb[0]; hgt=bb[3]-bb[1]
            od.text((lp[0]-wgt/2-bb[0], lp[1]-hgt/2-bb[1]), name, font=bigf,
                    fill=scale_col(col,1.1))
    out=out.resize((S,S),Image.LANCZOS)
    return out

if __name__=="__main__":
    import sys,time
    t0=time.time()
    if len(sys.argv)>1 and sys.argv[1]=='preview':
        render(S=900,ss=2).save('art_uh5/_prev04.png'); print('preview',time.time()-t0)
    else:
        render(S=4096,ss=2).save('art_uh5/04_the_triality_engine.png'); print('final',time.time()-t0)
