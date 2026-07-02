import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

d=np.load('dbm_big.npz')
age=d['age']; parent=d['parent']; phi=d['phi'].astype(np.float32); N=age.shape[0]
print("N",N,"cells",(age>=0).sum(),"agemax",age.max())

order=np.argsort(-age.ravel()); flat_age=age.ravel()
size=np.ones(N*N, np.int64); par=parent.ravel()
for idx in order:
    if flat_age[idx]<0: break
    p=par[idx]
    if p>=0: size[p]+=size[idx]
maxsize=size.max()

def agecol(t):
    anch=np.array([[0.55,0.06,0.62],[0.30,0.14,0.90],[0.18,0.55,0.99],
                   [0.55,0.9,1.0],[0.92,0.98,1.0]])
    n=len(anch)-1; f=np.clip(t,0,1)*n; i=min(int(f),n-1); fr=f-i
    return anch[i]*(1-fr)+anch[i+1]*fr

S=4096
# --- zoomed coordinate map: center tree, fill ~0.86 of frame ---
ys0,xs0=np.nonzero(age>=0); cy=ys0.mean(); cx=xs0.mean()
maxr=np.sqrt(((ys0-cy)**2+(xs0-cx)**2)).max()
zoom=0.86*(S/2)/(maxr* (S/N)) * (S/N)   # solve so maxr*mapscale=0.86*S/2
mapscale=0.86*(S/2)/maxr
def M(gy,gx): return ((gx-cx)*mapscale+S/2, (gy-cy)*mapscale+S/2)

# --- faint field-magnitude haze (|grad phi|): field concentrating at tips ---
gy,gx=np.gradient(gaussian_filter(phi,1.2))
fmag=np.sqrt(gy*gy+gx*gx)
fmag=np.clip(fmag/np.percentile(fmag,99.5),0,1)**0.7
# upscale haze to S with same zoom mapping (resize then affine via PIL is messy;
# instead rebuild haze on the S grid by sampling)
from scipy.ndimage import map_coordinates
Yg,Xg=np.mgrid[0:S,0:S]
srcx=(Xg-S/2)/mapscale+cx; srcy=(Yg-S/2)/mapscale+cy
haze=map_coordinates(fmag,[srcy.ravel(),srcx.ravel()],order=1,mode='constant',cval=0).reshape(S,S)
haze=gaussian_filter(haze,4)
del Yg,Xg,srcx,srcy

img=Image.new('RGB',(S,S),(0,0,0)); dr=ImageDraw.Draw(img)
amax=age.max(); lmax=np.log1p(maxsize)
cells=sorted([(age[y,x],y,x) for y,x in zip(ys0,xs0)])
for a,y,x in cells:
    p=par[y*N+x]
    if p<0: continue
    py,px=divmod(p,N)
    col=tuple(int(c*255) for c in np.clip(agecol(a/amax),0,1))
    w=1.1+6.6*(np.log1p(size[y*N+x])/lmax)
    dr.line([M(py,px),M(y,x)], fill=col, width=max(1,int(round(w))))
core=np.asarray(img,np.float32)/255.0
b1=np.stack([gaussian_filter(core[...,c],3) for c in range(3)],-1)
b2=np.stack([gaussian_filter(core[...,c],11) for c in range(3)],-1)
b3=np.stack([gaussian_filter(core[...,c],32) for c in range(3)],-1)
out=core + 0.75*b1 + 0.6*b2 + 0.5*b3
# add cool haze (dim) behind
hcol=np.array([0.10,0.22,0.55])
out=out + 0.16*haze[...,None]*hcol
out=1-np.exp(-1.5*out)
out=np.clip(out,0,1)**0.9
out=(out[0::2,0::2]+out[1::2,0::2]+out[0::2,1::2]+out[1::2,1::2])*0.25
im=(np.clip(out,0,1)*255).astype(np.uint8)
Image.fromarray(im).save('02_lichtenberg.png')
Image.fromarray(im).resize((820,820),Image.LANCZOS).save('02_preview.png')
print("saved", im.shape, "mapscale",round(mapscale,3))
