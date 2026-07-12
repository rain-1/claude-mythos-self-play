# Rivers of Totient — hero renderer (4096², painterly pass over C engine output)
import numpy as np, sys
from PIL import Image
from scipy.ndimage import gaussian_filter

R      = 4096            # final size
PROTO  = '--proto' in sys.argv
if PROTO: R = 2048
SS     = 2               # stroke supersample
RS     = R*SS
X1, YCROP, N = 27.0, 0.86, 1<<27

def xpix(a, S): return (np.log2(a)+0.6)/(X1+0.9)*(S-1)
def ypix(a, phi, S): return (1.0 - phi/a)/YCROP*(S-1)

# ---------- load engine output ----------
raw = np.fromfile('rivers.bin', dtype=np.uint8)
rec = raw.reshape(-1,16)
A   = rec[:,0:4].copy().view(np.uint32).ravel().astype(np.int64)
NX  = rec[:,4:8].copy().view(np.uint32).ravel().astype(np.int64)
MS  = rec[:,8:16].copy().view(np.int64).ravel()
print('hero edges', len(A), 'mass max', MS.max())

# phi for every hero node: phi = next-a when next>0 else brute
PH = NX - A
need = np.where(NX==0)[0]
def phi_brute(n):
    r=n; m=n; p=2
    while p*p<=m:
        if m%p==0:
            r-=r//p
            while m%p==0: m//=p
        p+=1 if p==2 else 2
    if m>1: r-=r//m
    return r
for i in need: PH[i]=phi_brute(int(A[i]))
print('exit hero nodes needing brute phi:', len(need))

pos = {}
for a,ph in zip(A,PH): pos[a]=(xpix(a,RS), ypix(a,ph,RS))
nxt  = dict(zip(A,NX)); mss = dict(zip(A,MS))
Aset = set(A.tolist())

# ---------- assemble chains ----------
targets = set(NX[NX>0].tolist())
heads = [a for a in A.tolist() if a not in targets]
chains=[]
for h in heads:
    c=[h]; cur=h
    while True:
        nx=nxt.get(cur,0)
        if nx==0 or nx not in Aset:
            if nx!=0 and nx in pos: c.append(nx)
            break
        c.append(nx); cur=nx
    chains.append(c)
print('chains', len(chains), 'longest', max(len(c) for c in chains))

# ---------- stroke layers by mass octave, split by parity ----------
NB = 16
layE=[np.zeros((RS,RS),np.float32) for _ in range(NB)]
layO=[np.zeros((RS,RS),np.float32) for _ in range(NB)]

def splat_seg(g, x0,y0,x1,y1, w):
    S=g.shape[0]
    dx,dy=x1-x0,y1-y0
    n=int(max(abs(dx),abs(dy)))+1; n=min(n,8192)
    t=(np.arange(n)+0.5)/n
    xs=x0+t*dx; ys=y0+t*dy
    ix=np.floor(xs).astype(np.int64); iy=np.floor(ys).astype(np.int64)
    ok=(ix>=0)&(iy>=0)&(ix<S-1)&(iy<S-1)
    ix,iy,fx,fy=ix[ok],iy[ok],(xs-np.floor(xs))[ok],(ys-np.floor(ys))[ok]
    ws=w/n
    np.add.at(g,(iy,ix),ws*(1-fx)*(1-fy)); np.add.at(g,(iy,ix+1),ws*fx*(1-fy))
    np.add.at(g,(iy+1,ix),ws*(1-fx)*fy);   np.add.at(g,(iy+1,ix+1),ws*fx*fy)

# smooth each chain: Chaikin ×2 on the vertex list (keeps endpoints)
def chaikin(P,it=1):
    for _ in range(it):
        if len(P)<3: return P
        Q=[P[0]]
        for i in range(len(P)-1):
            p,q=np.array(P[i]),np.array(P[i+1])
            Q.append(tuple(0.75*p+0.25*q)); Q.append(tuple(0.25*p+0.75*q))
        Q.append(P[-1]); P=Q
    return P

for c in chains:
    P=[pos[a] for a in c if a in pos]
    if len(P)<2: continue
    Ps=chaikin(P)
    # map smoothed points back to per-edge mass: nearest original index
    k=(len(Ps)-1)/(len(P)-1)
    bcap = 0                              # width no longer encodes mass
    for i in range(len(Ps)-1):
        oi=min(int(i/k), len(c)-2)
        a=c[oi]; m=mss.get(a,64)
        b=int(np.log2(max(m,64)))-6          # bucket 0 at mass 64
        b=min(b,bcap)
        g = layO[b] if (a&1) else layE[b]
        splat_seg(g, Ps[i][0],Ps[i][1],Ps[i+1][0],Ps[i+1][1], float(m)**0.55)

# compose strokes: per bucket, core + body + glow
strokesE=np.zeros((RS,RS),np.float32); strokesO=np.zeros((RS,RS),np.float32)
for b in range(NB):
    wpx = 1.15*SS
    for lay,acc in ((layE[b],strokesE),(layO[b],strokesO)):
        if lay.max()==0: continue
        body=gaussian_filter(lay, wpx*0.55); body*= (wpx*0.55)
        glow=gaussian_filter(lay, wpx*2.6);  glow*= (wpx*0.9)
        acc += body + 0.55*glow
del layE, layO

def down(x):
    return x.reshape(R,SS,R,SS).mean(axis=(1,3))
sE=down(strokesE); sO=down(strokesO); del strokesE,strokesO

# ---------- fog ----------
F=np.fromfile('fog.f32',dtype=np.float32).reshape(5,4096,4096)
if PROTO:
    F=F.reshape(5,R,2,R,2).mean(axis=(2,4))*4
fogE,fogO,masE,masO,sfd=[gaussian_filter(F[i],0.7) for i in range(5)]

def nrm(ch,p=99.5):
    nz=ch[ch>0]
    return ch/np.percentile(nz,p) if nz.size else ch
masE=np.log1p(masE/np.percentile(masE[masE>0],90))
masO=np.log1p(masO/np.percentile(masO[masO>0],90))
fogE,fogO,masE,masO,sfd=[nrm(c) for c in (fogE,fogO,masE,masO,sfd)]
sEn=nrm(sE,99.9); sOn=nrm(sO,99.9)

# ---------- orbit + beads ----------
orb=np.loadtxt('orbit.txt')            # a phi sf mass
oa,oph,osf=orb[:,0],orb[:,1],orb[:,2].astype(int)
ox=xpix(oa,R); oy=ypix(oa,oph,R)
orbit_lay=np.zeros((R,R),np.float32)
ops=list(zip(ox,oy))
for i in range(len(ops)-1):
    splat_seg(orbit_lay, ops[i][0],ops[i][1],ops[i+1][0],ops[i+1][1], 1.6*R/2048)
orbit_core=gaussian_filter(orbit_lay,0.55)*1.2
orbit_glow=gaussian_filter(orbit_lay,0.9)*1.5+gaussian_filter(orbit_lay,3.5)*0.55
orbit_glow=nrm(orbit_glow,99.9); orbit_core=nrm(orbit_core,99.9)

def stamp(g,x0,y0,sig,amp):
    r=int(4*sig)+1
    xi,yi=int(x0),int(y0)
    x_lo,x_hi=max(0,xi-r),min(R,xi+r+1); y_lo,y_hi=max(0,yi-r),min(R,yi+r+1)
    if x_lo>=x_hi or y_lo>=y_hi: return
    ys,xs=np.mgrid[y_lo:y_hi,x_lo:x_hi].astype(np.float32)
    g[y_lo:y_hi,x_lo:x_hi]+=amp*np.exp(-((xs-x0)**2+(ys-y0)**2)/(2*sig*sig))
beads_sf=np.zeros((R,R),np.float32); beads_ns=np.zeros((R,R),np.float32)
for x0,y0,s in zip(ox,oy,osf):
    if not (0<=x0<R and 0<=y0<R): continue
    if s:
        stamp(beads_sf,x0,y0,0.0009*R,1.6); stamp(beads_sf,x0,y0,0.0032*R,0.30)
    else:
        stamp(beads_ns,x0,y0,0.0007*R,0.8)

# ---------- trunk: the doubling-lock master river 4 -> 6 -> 8 -> ... ----------
trunk_lay=np.zeros((R,R),np.float32)
a=4; pts=[]
while a<= (1<<27):
    ph=phi_brute(a); pts.append((xpix(a,R),ypix(a,ph,R))); a=a+ph
for i in range(len(pts)-1):
    w=2.4*np.exp(-i/14.0)+0.55
    splat_seg(trunk_lay, pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1], w)
trunk_glow=gaussian_filter(trunk_lay,1.0)*1.5+gaussian_filter(trunk_lay,4.0)*0.6
trunk_glow=nrm(trunk_glow,99.9)

# ---------- confluence sparks ----------
cf=np.loadtxt('confl.txt')             # a mass hin parity
ca,cm,ch,cp=cf[:,0],cf[:,1],cf[:,2],cf[:,3].astype(int)
sel=cm>=512
ca,cm,ch,cp=ca[sel],cm[sel],ch[sel],cp[sel]
print('confluence sparks drawn:', len(ca))
sparkE=np.zeros((R,R),np.float32); sparkO=np.zeros((R,R),np.float32)
for i in range(len(ca)):
    a=int(ca[i]); ph=phi_brute(a)
    x0,y0=xpix(a,R),ypix(a,ph,R)
    if not (0<=x0<R and 0<=y0<R): continue
    amp=(np.log2(cm[i])-8)*0.25*(1+0.15*ch[i])
    sig=0.0016*R*(1+0.12*np.log2(cm[i]/512+1))
    stamp(sparkO if cp[i] else sparkE, x0,y0,sig,amp)
sparkE=nrm(sparkE,99.9) if sparkE.max()>0 else sparkE
sparkO=nrm(sparkO,99.9) if sparkO.max()>0 else sparkO

# ---------- compose ----------
img=np.zeros((R,R,3),np.float32)
def add(img, field, rgb, gain):
    for i in range(3): img[:,:,i]+=gain*field*rgb[i]

# palette
c_fogE =(0.16,0.34,0.55)   # steel blue sea fog
c_fogO =(0.42,0.26,0.18)   # dusk ember sky fog
c_masE =(0.35,0.75,0.95)   # cyan rivers
c_masO =(0.95,0.55,0.28)   # amber rivers
c_strE =(0.50,0.83,1.00)   # bright river cores
c_strO =(1.00,0.76,0.42)
c_orb  =(1.00,0.78,0.30)   # gold
c_sf   =(0.85,0.88,0.95)   # silver dust
c_bead =(1.00,0.95,0.80)
c_ns   =(0.80,0.45,0.25)
c_spE  =(0.80,0.95,1.00)
c_spO  =(1.00,0.85,0.60)

FB=1.0 if PROTO else 1.35
add(img, np.tanh(fogE*1.3), c_fogE, 0.42*FB)
add(img, np.tanh(fogO*1.3), c_fogO, 0.43*FB)
add(img, np.tanh(masE*1.2), c_masE, 0.27*FB)
add(img, np.tanh(masO*1.05), c_masO, 0.21*FB)
add(img, np.tanh(sfd *1.2), c_sf,   0.20*FB)
add(img, np.tanh(sEn*2.6),  c_strE, 1.15)
add(img, np.tanh(sOn*2.6),  c_strO, 1.15)
add(img, sparkE, c_spE, 0.7)
add(img, sparkO, c_spO, 0.7)
add(img, np.tanh(orbit_glow*2.2), c_orb, 1.30)
add(img, np.tanh(orbit_core*2.5), (1.0,0.97,0.88), 0.85)
add(img, beads_sf, c_bead, 1.3)
add(img, beads_ns, c_ns, 0.9)

# right-edge exposure roll-off (everything exits there; let it breathe out)
xn=np.linspace(0,1,R)[None,:,None]
rolloff=1-0.65*np.clip((xn-0.90)/0.10,0,1)**2
img*=rolloff
# filmic + gamma
out=1-np.exp(-1.35*img)
out=np.clip(out,0,1)**(1/2.05)
Image.fromarray((out*255).astype(np.uint8)).save('rivers_hero.png' if not PROTO else 'rivers_proto.png')
print('saved', 'proto' if PROTO else 'full')
