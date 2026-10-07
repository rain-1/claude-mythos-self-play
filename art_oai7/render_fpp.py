"""openai/math family 212: planar first-passage percolation has no bigeodesics (claimed for iid nonatomic weights
with a second-moment condition). One geodesic tree from the centre on exponential weights, drawn as rivers."""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter
from fpp import tree
from caption import caption, CORAL, SOFT
S=int(sys.argv[1]); out=sys.argv[2]; N=int(sys.argv[3])
D,P,size,src=tree(N,seed=3)
SS=2; W=S*SS; H=int(W*1.13)
m=W*0.05; cell=(W-2*m)/(N-1)
PAL=np.array([[250,140,160],[255,175,140],[253,214,120],[180,224,140],[130,214,184],[130,196,240],[156,160,240],[220,150,230]],float)
def wheel(h):
    h=(h%1)*len(PAL); i=int(h)%len(PAL); f=h-int(h); return PAL[i]*(1-f)+PAL[(i+1)%len(PAL)]*f
img=Image.new('RGB',(W,H),(252,251,249))
# keep the ball of equal travel time that fits inside the grid (the limit shape)
edge=np.concatenate([D[0],D[-1],D[:,0],D[:,-1]]); T0=0.97*edge.min()
inside=(D<T0).ravel()
# soft shadow of the ball
ball=Image.fromarray(((D<T0)*255).astype(np.uint8)).resize((int(cell*(N-1)),int(cell*(N-1))),Image.BILINEAR).filter(ImageFilter.GaussianBlur(W*0.004))
bb=np.asarray(ball).astype(float)/255; base=np.asarray(img).astype(float)
o=int(m+W*0.004); reg=base[o:o+bb.shape[0],o:o+bb.shape[1]]; reg*=1-0.03*bb[...,None]*np.array([0.9,0.9,0.5])
img=Image.fromarray(base.astype(np.uint8))
c=src; cy0,cx0=divmod(c,N)
order=np.argsort(size)  # small first, big rivers on top
lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
thr=4
for v in order:
    if size[v]<thr or not inside[v]: continue
    p=P[v]
    if p<0: continue
    y1,x1=divmod(v,N); y2,x2=divmod(p,N)
    ang=np.arctan2(-(y1-cy0),x1-cx0)/(2*np.pi)
    col=wheel(ang+0.05)
    wdt=max(1.0,cell*(N/401)*0.16*(size[v]*(401/N)**2)**0.42)
    rpx=np.hypot(x1-cx0,y1-cy0)*cell; wdt=min(wdt,2.0+0.5*rpx)
    a=int(min(255,90+40*np.log10(size[v])))
    fc=tuple(col.astype(int))+(a,)
    d.line([(m+x1*cell,m+y1*cell),(m+x2*cell,m+y2*cell)],fill=fc,width=int(round(wdt)))
    if wdt>3:
        rr=wdt/2; d.ellipse([m+x1*cell-rr,m+y1*cell-rr,m+x1*cell+rr,m+y1*cell+rr],fill=fc)
img=Image.alpha_composite(img.convert('RGBA'),lay).convert('RGB'); dd=ImageDraw.Draw(img)
r=W*0.006; X,Y=m+cx0*cell,m+cy0*cell; dd.ellipse([X-r,Y-r,X+r,Y+r],fill=CORAL,outline=(255,255,255),width=max(2,W//1500))
caption(img,W/2,W-m*0.3+W*0.01,'Every Road Runs One Way Home',
  f'first-passage percolation on a {N}×{N} grid with exponential edge times: the tree of fastest routes from the coral centre',
  'width ~ how many fastest routes share the edge  ·  hue = compass direction  ·  the outline is one moment of equal travel time: the limit shape',
  W*0.038,align='center',line3='openai/math family 212 claims there are no bigeodesics: no infinite road is fastest in both directions at once')
img.resize((S,int(H/SS)),Image.LANCZOS).save(out)
