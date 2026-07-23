"""The Rest of the Catalogue — incomplete open tetrahedra (6) and octahedra (185),
verified against Vejdemo-Johansson arXiv:2602.20425. Same register as the hero.
"""
import json, sys, numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation
from lib import line_splat, splat_pts, wide_bloom, filmic, to_img, nzpct
from platonic import TET_V, TET_E, OCT_V, OCT_E, rot_group_from_verts

FINAL = int(sys.argv[1]) if len(sys.argv)>1 else 1024
SS = 2; S = FINAL*SS; rs = FINAL/4096.0
d = json.load(open('platonic.json'))

def build(V, E):
    vperms = rot_group_from_verts(V, E)
    EIDX = {e:i for i,e in enumerate(E)}
    eps = []
    for vp in vperms:
        eps.append([EIDX[(min(vp[a],vp[b]),max(vp[a],vp[b]))] for a,b in E])
    return np.array(V,float), E, eps

def apply_ep(mask, ep):
    m=0
    for e in range(len(ep)):
        if mask>>e&1: m|=1<<ep[e]
    return m
def canon(mask, eps): return min(apply_ep(mask,ep) for ep in eps)

c30 = np.cos(np.pi/6)
def iso(p): x,y,z=p; return ((x-y)*c30*0.62,(x+y)*0.31-z*0.62)

def grounded(mask, V, E, eps):
    best=None; bs=None
    for ep in eps:
        m2 = apply_ep(mask, ep)
        zs=[V[a][2]+V[b][2] for e,(a,b) in enumerate(E) if m2>>e&1]
        sc=sum(zs)
        if bs is None or sc<bs: bs,best = sc,m2
    return best

def Rxyz(ax,ay,az):
    cx,sx=np.cos(ax),np.sin(ax); cy,sy=np.cos(ay),np.sin(ay); cz,sz=np.cos(az),np.sin(az)
    Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    Rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Rz@Ry@Rx
def best_view(V):
    "generic view rotation: maximize min pairwise projected vertex distance"
    best=None; bs=-1
    for ax in np.linspace(0,0.9,10):
        for ay in np.linspace(0,0.9,10):
            R = Rxyz(ax,ay,0)
            P = np.array([iso(R@v) for v in V])
            dm = np.hypot(P[:,0,None]-P[None,:,0], P[:,1,None]-P[None,:,1])
            np.fill_diagonal(dm,np.inf)
            s = dm.min()
            if s>bs: bs,best = s,R
    return best

def mirror_class(mask, V, E, eps):
    # reflection swap x<->y (preserves both vertex sets); horizontal flip in iso
    idx = {tuple(np.round(v,6)):i for i,v in enumerate(V)}
    vp = [idx[tuple(np.round([v[1],v[0],v[2]],6))] for v in V]
    EIDX = {e:i for i,e in enumerate(E)}
    ep = [EIDX[(min(vp[a],vp[b]),max(vp[a],vp[b]))] for a,b in E]
    return canon(apply_ep(mask, ep), eps), ep

VT, ET, epsT = build(TET_V, TET_E)
VT = VT/np.sqrt(3.0)*1.28
RV_T = None  # set after best_view defined
VO, EO, epsO = build(OCT_V, OCT_E)
tets, octs = d['tet'], d['oct']

# chirality + twin-adjacent ordering per k-group
def organize(classes, V, E, eps):
    mirr = {}
    for r in classes:
        mirr[r] = mirror_class(r, V, E, eps)[0]
    by_k = {}
    for r in classes: by_k.setdefault(bin(r).count('1'), []).append(r)
    out = {}
    for k,g in by_k.items():
        am = sorted([r for r in g if mirr[r]==r])
        ch=[]; seen=set()
        for r in sorted(g):
            if mirr[r]==r or r in seen: continue
            ch += [r, mirr[r]]; seen.add(r); seen.add(mirr[r])
        out[k] = am+ch
    return out, mirr
tetK, tmirr = organize(tets, VT, TET_E, epsT)
octK, omirr = organize(octs, VO, OCT_E, epsO)
namph = sum(1 for r in octs if omirr[r]==r)
print("octa amphichiral:", namph, "chiral pairs:", (185-namph)//2)

RV_T = best_view(VT)
RV_O = best_view(VO)
ROWCAP = 16
rows = []   # (solid, k, list)
def balanced(g):
    nr = int(np.ceil(len(g)/ROWCAP))
    per = int(np.ceil(len(g)/nr))
    return [g[i:i+per] for i in range(0,len(g),per)]
for k in sorted(tetK): rows.append(('T', k, tetK[k]))
rows.append(('T', 6, [63]))             # ghost complete tetrahedron
for k in sorted(octK):
    for chunk in balanced(octK[k]): rows.append(('O', k, chunk))
rows.append(('O', 12, [ (1<<12)-1 ]))   # ghost complete octahedron
NR = len(rows)
cellw = S/(ROWCAP+0.8); cellh = S/(NR+1.8)
sc_base = min(cellw,cellh)*0.60

warm=np.zeros((S,S),np.float32); warmk=np.zeros((S,S),np.float32)
cold=np.zeros((S,S),np.float32); bead=np.zeros((S,S),np.float32)
row_meta=[]
for ri,(sol,k,row) in enumerate(rows):
    V,E,eps = (VT,ET,epsT) if sol=='T' else (VO,EO,epsO)
    RVIEW = RV_T if sol=='T' else RV_O
    mirr = tmirr if sol=='T' else omirr
    NE=len(E)
    y0=(ri+1.0)*cellh
    xoff=(S-len(row)*cellw)/2
    row_meta.append((sol,k,y0))
    knorm=(k-3)/9.0 if sol=='O' else (k-3)/9.0*0.5+0.06
    handled={}
    for ci,mask in enumerate(row):
        ghost_only = (k==12) or (sol=='T' and k==6)
        if ghost_only: m, mdraw = 0, False
        elif mask in handled: m, mdraw = handled[mask], True
        else:
            m = grounded(mask,V,E,eps); mdraw=False
            if mirr[mask]!=mask and ci+1<len(row) and row[ci+1]==mirr[mask]:
                handled[mirr[mask]] = m
        cx=xoff+(ci+0.5)*cellw
        deg={}; P={}
        for e,(a,b) in enumerate(E):
            va = V[a] if not mdraw else np.array([V[a][1],V[a][0],V[a][2]])
            vb = V[b] if not mdraw else np.array([V[b][1],V[b][0],V[b][2]])
            pa,pb = iso(RVIEW@np.asarray(va,float)), iso(RVIEW@np.asarray(vb,float))
            A=(cx+pa[0]*sc_base, y0-pa[1]*sc_base); B=(cx+pb[0]*sc_base, y0-pb[1]*sc_base)
            if (not ghost_only) and (m>>e&1):
                line_splat(warm,[A[0]],[A[1]],[B[0]],[B[1]],1.0)
                line_splat(warmk,[A[0]],[A[1]],[B[0]],[B[1]],knorm)
                deg[a]=deg.get(a,0)+1; deg[b]=deg.get(b,0)+1
                P[a]=A; P[b]=B
            else:
                line_splat(cold,[A[0]],[A[1]],[B[0]],[B[1]],1.0)
        for v,dv in deg.items():
            if dv>=2: splat_pts(bead,np.array([P[v][0]]),np.array([P[v][1]]),2.2)

def stroke(l,w,bl): return gaussian_filter(grey_dilation(l,size=(int(w),int(w))),bl)
wq=stroke(warm,max(2,2.4*SS*rs),1.1*SS*rs); wkq=stroke(warmk,max(2,2.4*SS*rs),1.1*SS*rs)
cq=stroke(cold,max(2,1.6*SS*rs),2.0*SS*rs); bq=gaussian_filter(bead,2.4*SS*rs)
nm=nzpct(wq,88); wq/=nm; wkq/=nm; cq/=nzpct(cq,90); bq/=nzpct(bq,95)
kpix=np.where(wq>1e-4,wkq/np.maximum(wq,1e-4),0)
glow=wide_bloom(wq,15*SS*rs); glow/=max(glow.max(),1e-9)
silver=np.array([0.62,0.76,0.98]); gold=np.array([1.10,0.78,0.30])
col=silver[None,None,:]*(1-kpix[...,None])+gold[None,None,:]*kpix[...,None]
bright=0.62+0.66*kpix
rgb=np.zeros((S,S,3),np.float32)
rgb+=col*(wq*bright)[...,None]
pool=wide_bloom(np.roll(warm,int(26*SS*rs),axis=0),24*SS*rs); pool/=max(pool.max(),1e-9)
rgb[...,0]+=0.10*pool; rgb[...,1]+=0.065*pool; rgb[...,2]+=0.035*pool
rgb[...,0]+=0.40*glow; rgb[...,1]+=0.34*glow; rgb[...,2]+=0.26*glow
gg=0.17
rgb[...,0]+=gg*0.42*cq; rgb[...,1]+=gg*0.72*cq; rgb[...,2]+=gg*1.05*cq
rgb[...,0]+=0.85*bq; rgb[...,1]+=0.82*bq; rgb[...,2]+=0.72*bq
out=filmic(rgb,k=1.3,gamma=0.84)
from PIL import Image, ImageDraw, ImageFont
img=to_img(out).resize((FINAL,FINAL),Image.LANCZOS)
draw=ImageDraw.Draw(img)
try:
    fs=max(10,int(15*FINAL/1024))
    font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",fs)
    fontB=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",int(fs*1.2))
except: font=fontB=ImageFont.load_default()
done=set()
for sol,k,y0 in row_meta:
    key=(sol,k)
    if key in done: continue
    done.add(key)
    t = f"{k}"
    if sol=='T' and k==min(tetK): t="TETRAHEDRA  3"
    if sol=='O' and k==3: t="OCTAHEDRA  3"
    ghost_lab = (sol=='O' and k==12) or (sol=='T' and k==6)
    colr=(90,110,140) if ghost_lab else (150,160,175)
    draw.text((int(0.014*FINAL),int(y0/SS-6*FINAL/1024)), t, fill=colr, font=fontB)
draw.text((int(0.014*FINAL), int(0.977*FINAL)),
 "ALL 6 INCOMPLETE OPEN TETRAHEDRA · ALL 185 OCTAHEDRA · VERIFIED · BEYOND: 2,423,206 DODECAHEDRA, 16,096,166 ICOSAHEDRA",
 fill=(120,124,135), font=font) if False else None
draw.text((int(0.014*FINAL), int(0.977*FINAL)),
 "ALL 6 INCOMPLETE OPEN TETRAHEDRA + ALL 185 OCTAHEDRA — BEYOND THIS WALL, ALSO VERIFIED: 2,423,206 DODECAHEDRA + 16,096,166 ICOSAHEDRA",
 fill=(120,124,135), font=font)
img.save(f'catalogue_{FINAL}.png'); print("saved", f'catalogue_{FINAL}.png')
