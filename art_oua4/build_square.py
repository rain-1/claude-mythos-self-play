import numpy as np, sys, time
from PIL import Image
from scipy.ndimage import gaussian_filter

# A Square in Every Loop — the Toeplitz inscribed-square conjecture.
# A wild star-shaped Jordan curve r(theta); we find inscribed squares (4 curve points
# forming a square) by locating where two "on-curve" defects both vanish, and draw the
# whole nested family glowing inside the loop, pegs (contact points) blazing.
S   = int(sys.argv[1]) if len(sys.argv)>1 else 2048
SS  = int(sys.argv[2]) if len(sys.argv)>2 else 2
seed= int(sys.argv[3]) if len(sys.argv)>3 else 7
tag = sys.argv[4] if len(sys.argv)>4 else ""
W=S*SS
rng=np.random.default_rng(seed)

# build a wiggly but simple (star-shaped) radial curve
ncoef=9
amp=rng.uniform(0.04,0.16,ncoef)*np.array([1,0.9,0.8,0.7,0.6,0.55,0.5,0.45,0.4])
ph =rng.uniform(0,2*np.pi,ncoef)
ks =np.arange(2,2+ncoef)
def rfun(th):
    s=np.ones_like(th)
    for a,k,p in zip(amp,ks,ph): s=s+a*np.cos(k*th+p)
    return s
# guarantee positivity / star-shaped
tt=np.linspace(0,2*np.pi,4000); rmin=rfun(tt).min()
assert rmin>0.2, f"curve not star-shaped rmin={rmin}"
def Pt(th):
    r=rfun(th); return np.stack([r*np.cos(th),r*np.sin(th)],-1)
def defect(p):
    ang=np.arctan2(p[...,1],p[...,0]); rad=np.hypot(p[...,0],p[...,1]); return rad-rfun(ang)
def rot90(v): return np.stack([-v[...,1],v[...,0]],-1)

t0=time.time()
M=900
th=np.linspace(0,2*np.pi,M,endpoint=False)
TH1,TH2=np.meshgrid(th,th,indexing='ij')
P1=Pt(TH1.ravel()).reshape(M,M,2); P2=Pt(TH2.ravel()).reshape(M,M,2)
s=P2-P1; C=P2+rot90(s); D=P1+rot90(s)
D1=defect(C); D2=defect(D)
def sc(F):
    a=F[:-1,:-1];b=F[1:,:-1];c=F[:-1,1:];d=F[1:,1:]
    return (np.minimum.reduce([a,b,c,d])<0)&(np.maximum.reduce([a,b,c,d])>0)
cand=sc(D1)&sc(D2); ii,jj=np.where(cand)
dt=th[1]-th[0]
def F(t1,t2):
    p1=Pt(np.array([t1]))[0];p2=Pt(np.array([t2]))[0]
    ss=p2-p1;c=p2+np.array([-ss[1],ss[0]]);d=p1+np.array([-ss[1],ss[0]])
    return np.array([defect(c[None])[0],defect(d[None])[0]])
sqs=[]
for i,j in zip(ii,jj):
    t1=th[i]+dt*0.5;t2=th[j]+dt*0.5;ok=False
    for _ in range(50):
        f=F(t1,t2)
        if np.max(np.abs(f))<1e-10: ok=True;break
        h=1e-6;J=np.array([(F(t1+h,t2)-f)/h,(F(t1,t2+h)-f)/h]).T
        try: stp=np.linalg.solve(J,f)
        except: break
        t1-=stp[0];t2-=stp[1]
    if ok:
        p1=Pt(np.array([t1]))[0];p2=Pt(np.array([t2]))[0]
        ss=p2-p1;c=p2+np.array([-ss[1],ss[0]]);d=p1+np.array([-ss[1],ss[0]])
        verts=np.array([p1,p2,c,d]);side=np.hypot(*ss);ctr=verts.mean(0)
        if side>0.06: sqs.append((side,ctr,verts))
# dedup by center+side
seen=set();uniq=[]
for side,ctr,verts in sqs:
    key=(round(ctr[0],2),round(ctr[1],2),round(side,2))
    if key in seen: continue
    seen.add(key);uniq.append((side,ctr,verts))
uniq.sort(key=lambda x:-x[0])
print(f"found {len(uniq)} inscribed squares in {round(time.time()-t0,1)}s  seed={seed}")
for side,ctr,_ in uniq[:14]: print("  side=%.3f ctr=(%.2f,%.2f)"%(side,ctr[0],ctr[1]))

# ---- render additively ----
allp=Pt(np.linspace(0,2*np.pi,8000))
mx=np.abs(allp).max(); scale=W*0.43/mx; cx=cy=W/2
def toW(p): return np.array([cx+scale*p[...,0], cy-scale*p[...,1]])
def splat_poly(buf,pts,wgt=1.0):
    X=cx+scale*pts[:,0]; Y=cy-scale*pts[:,1]
    seg=np.hypot(np.diff(X),np.diff(Y));cum=np.concatenate([[0],np.cumsum(seg)]);tot=cum[-1]
    ns=max(2,int(tot));ssamp=np.linspace(0,tot,ns)
    px=np.interp(ssamp,cum,X);py=np.interp(ssamp,cum,Y)
    xi=np.floor(px).astype(int);yi=np.floor(py).astype(int);fx=px-xi;fy=py-yi
    for ddx,wx in ((0,1-fx),(1,fx)):
        for ddy,wy in ((0,1-fy),(1,fy)):
            Xp=xi+ddx;Yp=yi+ddy;m=(Xp>=0)&(Xp<W)&(Yp>=0)&(Yp<W)
            np.add.at(buf,(Yp[m],Xp[m]),(wx*wy*wgt)[m])
def splat_pts(buf,pts,wgt,sigpx):
    for p in pts:
        X=cx+scale*p[0];Y=cy-scale*p[1]
        x0=int(X-4*sigpx);x1=int(X+4*sigpx);y0=int(Y-4*sigpx);y1=int(Y+4*sigpx)
        x0=max(0,x0);y0=max(0,y0);x1=min(W,x1);y1=min(W,y1)
        if x1<=x0 or y1<=y0: continue
        yy,xx=np.mgrid[y0:y1,x0:x1]
        buf[y0:y1,x0:x1]+=wgt*np.exp(-(((xx-X)**2+(yy-Y)**2)/(2*sigpx**2)))

curvebuf=np.zeros((W,W));
sqbuf=np.zeros((W,W,3)); pegbuf=np.zeros((W,W))
# curve
cl=np.vstack([allp,allp[:1]]); splat_poly(curvebuf,cl,1.0)
# squares colored by size rank (warm large -> cool small)
PAL=np.array([[255,196,96],[255,235,150],[120,220,200],[90,180,235],[170,130,240],[235,110,170],
              [120,235,150],[240,150,90],[150,200,255]],float)
lw=1.0
for r,(side,ctr,verts) in enumerate(uniq):
    col=PAL[r%len(PAL)]
    loop=np.vstack([verts,verts[:1]])
    tmp=np.zeros((W,W)); splat_poly(tmp,loop,1.0)
    for ch in range(3): sqbuf[...,ch]+=tmp*col[ch]/255.0
    splat_pts(pegbuf,verts,1.0,2.2*SS)
print("rasterized in",round(time.time()-t0,1),"s")

# compose — fatten thin lines (sigma~0.7*SS) so they survive the SS downscale, and
# scale line energy by SS (a 1px line loses ~SS brightness when downsampled by SS)
img=np.zeros((W,W,3))
# background curve: cool steel glow — the containing Jordan loop, read it clearly
curvebuf=gaussian_filter(curvebuf,sigma=0.7*SS)
cv=curvebuf/curvebuf.max()
cvglow=gaussian_filter(cv,sigma=1.4*SS)
img+= (cv[...,None])*np.array([175,200,220])*1.7*SS + (cvglow[...,None])*np.array([70,105,140])*1.2
# squares
sqbuf=gaussian_filter(sqbuf,sigma=(0.7*SS,0.7*SS,0))
sgl=gaussian_filter(sqbuf,sigma=(1.2*SS,1.2*SS,0))
img+= sqbuf*205*SS + sgl*130*SS
# pegs blazing
pg=pegbuf/ (pegbuf.max()+1e-9)
pgl=gaussian_filter(pg,sigma=3*SS)
img+= pg[...,None]*np.array([255,245,225])*200 + pgl[...,None]*np.array([255,210,150])*70
# tone
img=255*(1-np.exp(-img/120.0))
img=np.clip(img,0,255)
# deep void base
base=np.array([6,8,15]); img=np.maximum(img,base)
im=Image.fromarray(img.astype(np.uint8)).resize((S,S),Image.LANCZOS)
im.save(f"/home/user/claude-mythos-self-play/art_oua4/square{tag}.png")
print("saved", f"square{tag}.png", len(uniq),"squares")
