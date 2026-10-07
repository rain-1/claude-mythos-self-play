"""openai/math family 226: the double-dimer loop ensemble (Temperleyan) converges to nested CLE4.
Two uniform dimer coverings overlaid; every loop is a paper sheet, nested by depth."""
import numpy as np, sys
from PIL import Image
from scipy.ndimage import gaussian_filter, shift as nshift
from dimers import loops
from caption import caption, CORAL
S=int(sys.argv[1]); out=sys.argv[2]; m=int(sys.argv[3]); s1,s2=int(sys.argv[4]),int(sys.argv[5])
L=loops(m,s1,s2); Sg=2*m+1
SS=1; mg=0.06; G=int(S*(1-2*mg)); cell=G/Sg
Lmin=int(sys.argv[6]) if len(sys.argv)>6 else 30
WHEEL=np.array([[0.98,0.62,0.68],[1.0,0.74,0.60],[1.0,0.88,0.58],[0.80,0.93,0.62],[0.60,0.90,0.80],[0.62,0.82,1.0],[0.72,0.74,1.0],[0.84,0.72,1.0]],np.float32)
PAPER=np.array([0.994,0.990,0.984],np.float32)
def wheel(h):
    h=np.clip(h,0,0.999)*(len(WHEEL)-1); i=int(h); f=h-i; return WHEEL[i]*(1-f)+WHEEL[i+1]*f
items=[]
for c in L:
    if len(c)<Lmin: continue
    Y=(c[:,0]+0.5)*cell; X=(c[:,1]+0.5)*cell
    a=0.5*np.sum(X*np.roll(Y,-1)-np.roll(X,-1)*Y); items.append((abs(a),len(c),X,Y))
items.sort(key=lambda t:-t[0]); nbig=len(items)
img=np.ones((G,G,3),np.float32)*PAPER; hgt=np.zeros((G,G),np.float32)
lmax=np.log(items[0][1]); lmin=np.log(Lmin)
sig=1.3*cell
for area,n,X,Y in items:
    pad=int(4*sig)+2
    x0=max(int(X.min())-pad,0); x1=min(int(X.max())+pad+1,G); y0=max(int(Y.min())-pad,0); y1=min(int(Y.max())+pad+1,G)
    w,h=x1-x0,y1-y0; acc=np.zeros((h,w+1),np.int32)
    xs,ys=X-x0,Y-y0; xa,ya=np.roll(xs,-1),np.roll(ys,-1)
    lo=np.minimum(ys,ya); hi=np.maximum(ys,ya); r0=np.ceil(lo-0.5).astype(int); r1=np.ceil(hi-0.5).astype(int); cnt=r1-r0; k=cnt>0
    idx=np.repeat(np.nonzero(k)[0],cnt[k]); off=np.arange(len(idx))-np.repeat(np.cumsum(cnt[k])-cnt[k],cnt[k])
    j=r0[idx]+off; yc=j+0.5; t=(yc-ys[idx])/(ya[idx]-ys[idx]); xc=xs[idx]+t*(xa[idx]-xs[idx])
    col=np.clip(np.ceil(xc-0.5).astype(int),0,w); sgn=np.where(ya[idx]>ys[idx],1,-1)
    ok=(j>=0)&(j<h); np.add.at(acc,(j[ok],col[ok]),sgn[ok])
    ind=(np.cumsum(acc,axis=1)[:,:w]!=0).astype(np.float32)
    al=np.clip((gaussian_filter(ind,sig)-0.5)*3+0.5,0,1)
    c=wheel(1-(np.log(n)-lmin)/(lmax-lmin))
    reg=img[y0:y1,x0:x1]; img[y0:y1,x0:x1]=reg*(1-al[...,None])+c*al[...,None]
    hgt[y0:y1,x0:x1]+=al
H=G; s=H/1000
up=nshift(hgt,(2.0*s,1.5*s),order=1,mode='nearest'); d=np.clip(up-hgt,0,None); d=2*(1-np.exp(-d/2))
img*=1-0.30*(1-np.exp(-gaussian_filter(d,1.4*s)))[...,None]*np.array([0.55,0.50,0.30])*1.9
tl=nshift(hgt,(0.8*s,0.8*s),order=1,mode='nearest'); lit=1-np.exp(-np.clip(hgt-tl,0,None))
img=img+(1-img)*0.45*lit[...,None]
print('drawn',nbig,'max nesting',hgt.max())
Hc=int(S*1.16); can=np.ones((Hc,S,3))*PAPER
o=int(S*mg); can[o:o+H,o:o+H]=img
im=Image.fromarray((np.clip(can,0,1)*255).astype(np.uint8))
caption(im,S/2,o+H+S*0.03,'Two Tilings Make Rings',
  f'two independent uniform dimer coverings of a {Sg}×{Sg} Temperleyan square, laid on top of each other: they close into {len(L):,} loops',
  f'the {nbig:,} loops of at least {Lmin} sites as paper sheets, hue by length from strawberry (longest) to periwinkle  ·  exact sampling: Temperley + Wilson',
  S*0.036,align='center',line3='openai/math family 226 claims the loops converge, as curves, to nested CLE₄: the same loop soup at every scale')
im.save(out)
