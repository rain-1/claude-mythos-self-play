"""
dequant.py — 03: THE STRAIGHTENING (Maslov dequantization).
For the curve with log-coefficients v_ij = -lam*q_ij, the amoeba lives in
(x,y)=(log|z|,log|w|); in SCALED coordinates (x/lam, y/lam) the amoeba is the argmax
region of the tropical polynomial max_ij(-q_ij + iX + jY) softened at scale 1/lam.
As lam -> infinity the soft amoeba COLLAPSES onto the tropical curve (Viro patchworking
/ Maslov dequantization: log_t linearises multiplication).  We overlay the scaled
amoeba at a ladder of lam values -> nested shells tightening onto the glowing PL
skeleton.  The same object as 01, filmed as the logarithm's base runs to infinity.
"""
import numpy as np
from tropical import poly_w_coeffs, roots_batch
from hero import curve, d3_group, A, tropical_field
from PIL import Image
from scipy import ndimage

def scaled_amoeba_density(d, lam, cu, cv, half, S, Nx=1500, Nth=2400):
    """Amoeba of the lam-curve, points scaled by 1/lam, embedded, D3-symmetrised,
    histogrammed in the FIXED frame (cu,cv,half)."""
    C,_=curve(d,lam)
    zr=(-lam*d*3-2, lam*d*3+2)
    xs=np.linspace(zr[0],zr[1],Nx); th=np.linspace(0,2*np.pi,Nth,endpoint=False)
    rng=np.random.default_rng(3); dx=(zr[1]-zr[0])/Nx
    G=d3_group(); u0e,v0e=cu-half,cv-half; inv=S/(2*half)
    Hflat=np.zeros(S*S); batch=[]
    for x0 in xs:
        x=x0+rng.uniform(-.5,.5)*dx
        z=np.exp(x+1j*th); R=roots_batch(poly_w_coeffs(C,z))
        X=(np.full(R.shape,x)/lam).ravel(); Y=(np.log(np.abs(R)+1e-300)/lam).ravel()
        P=A@np.vstack([X,Y]); U0,V0=P[0]-cu,P[1]-cv
        for g in G:
            u=cu+g[0,0]*U0+g[0,1]*V0; v=cv+g[1,0]*U0+g[1,1]*V0
            iu=((u-u0e)*inv).astype(np.intp); iv=((v-v0e)*inv).astype(np.intp)
            ok=(iu>=0)&(iu<S)&(iv>=0)&(iv<S); batch.append(iu[ok]*S+iv[ok])
        if len(batch)>=900:
            Hflat+=np.bincount(np.concatenate(batch),minlength=S*S); batch=[]
    if batch: Hflat+=np.bincount(np.concatenate(batch),minlength=S*S)
    H=Hflat.reshape(S,S).T[::-1]
    return H

def ramp(anchors):
    xs=np.array([a[0] for a in anchors]); cols=np.array([a[1] for a in anchors],float)
    return lambda t: np.stack([np.interp(np.clip(t,0,1),xs,cols[:,k]) for k in range(3)],-1)

def build(d=6, lams=(0.45,0.7,1.1,1.7,2.7,4.2), S=2048, tag='03_dequant'):
    # fixed frame from the tropical curve of valuation -q (lam-independent shape)
    cu,cv,half=frame_from_tropical(d,margin=1.85)
    shells=[]
    for lam in lams:
        H=scaled_amoeba_density(d,lam,cu,cv,half,S)
        H=ndimage.gaussian_filter(H,1.0)
        v=np.log1p(H); v/=v.max()+1e-9
        shells.append(v)
        print('lam',lam,'shell done',flush=True)
    np.save(f'{tag}_shells.npy',np.array(shells,np.float32))
    np.savez(f'{tag}_meta.npz',cu=cu,cv=cv,half=half,S=S,d=d,lams=np.array(lams))
    compose(tag)

def frame_from_tropical(d, margin=1.5):
    """Centre & half-window of the tropical honeycomb of valuation -q (scaled coords)."""
    pts=[(i,j) for i in range(d+1) for j in range(d+1) if i+j<=d]
    v=np.array([-(i*i+j*j+(d-i-j)**2) for (i,j) in pts])
    ii=np.array([p[0] for p in pts]); jj=np.array([p[1] for p in pts])
    W=30.0; g=np.linspace(-W,W,900); UU,VV=np.meshgrid(g,g)
    Ainv=np.linalg.inv(A); XY=Ainv@np.vstack([UU.ravel(),VV.ravel()]); Xg,Yg=XY[0],XY[1]
    T=v[None,:]+np.outer(Xg,ii)+np.outer(Yg,jj); arg=T.argmax(1)
    interior=[idx for idx,(i,j) in enumerate(pts) if 0<i and 0<j and i+j<d]
    msk=np.isin(arg,interior)
    cu=UU.ravel()[msk].mean(); cv=VV.ravel()[msk].mean()
    span=max(np.ptp(UU.ravel()[msk]), np.ptp(VV.ravel()[msk]))
    return cu,cv,span*margin*0.5

def compose(tag='03_dequant', thresh=0.05, bloom=0.35):
    shells=np.load(f'{tag}_shells.npy'); m=np.load(f'{tag}_meta.npz')
    lams=m['lams']; S=int(m['S']); d=int(m['d']); half=float(m['half']); cu=float(m['cu']); cv=float(m['cv'])
    n=len(lams)
    # colour ladder: fat/small-lam (survives only far out) = warm ember;
    # thin/large-lam (survives onto the skeleton) = cool cyan -> white limit.
    PAL=ramp([(0,(150,54,32)),(0.28,(206,104,44)),(0.5,(150,120,150)),
              (0.72,(58,150,196)),(1,(224,244,255))])
    # deepest surviving shell index per pixel + a smooth envelope brightness
    surv=np.full((S,S),-1.0); envel=np.zeros((S,S))
    for k in range(n):
        cov=shells[k]>thresh
        surv=np.where(cov,float(k),surv)
        envel=np.maximum(envel,shells[k])           # brightest coverage
    t=np.clip(surv,0,n-1)/(n-1)
    col=PAL(t)
    val=np.clip(envel,0,1)**0.7
    img=col*val[...,None]
    img=np.where((surv<0)[...,None],0,img)          # never-covered -> void
    # tropical curve of -q (the limit skeleton), crisp bright cool-white
    valm={(i,j):-(i*i+j*j+(d-i-j)**2) for i in range(d+1) for j in range(d+1) if i+j<=d}
    gap,_=tropical_field(valm,d,cu,cv,half,S); gap=gap[::-1]
    px=2*half/S; w=1.1*px*(d*0.5)
    spine=np.exp(-(gap/w)**2)*(envel>thresh)
    img=img+spine[...,None]*np.array([210,240,255.])*0.85
    if bloom>0:
        lum=img.mean(2); hot=np.clip((lum-165)/90,0,1)[...,None]*img
        for sg in (3,9,20): img=img+bloom*ndimage.gaussian_filter(hot,(sg,sg,0))*0.5
    # gentle vignette to calm the periphery
    yy,xx=np.mgrid[0:S,0:S]; r=np.hypot(xx-S/2,yy-S/2)/(S/2)
    img=img*np.clip(1.0-0.5*r**1.7,0.2,1.0)[...,None]
    img=np.clip(img,0,255)
    Image.fromarray(img.astype(np.uint8)).save(f'{tag}.png')
    print(tag,'composed')

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='compose': compose()
    else: build(S=int(sys.argv[1]) if len(sys.argv)>1 else 1200)
