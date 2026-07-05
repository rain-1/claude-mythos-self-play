"""
coamoeba.py — 02: THE COAMOEBA.
The argument (phase) image of the same family of curves:
    Coamoeba(P) = { (arg z, arg w) mod 2pi : P(z,w)=0 }  on the torus.
Where the amoeba records log-MODULUS, the coamoeba records PHASE.  It is periodic
(a mosaic on the torus), and — for a maximally-sparse (Harnack) curve — its
complement is a union of parallelograms; the coamoeba's structure is dual to the
amoeba's.  We tile several fundamental domains so the periodicity reads.
Concept companion: modulus and phase are the two projections of one variety
(|.| and arg) — two faces of one object.
"""
import numpy as np
from tropical import sample_curve
from PIL import Image
from scipy import ndimage

def curve(d, lam):
    C=np.zeros((d+1,d+1),complex)
    for i in range(d+1):
        for j in range(d+1):
            if i+j<=d:
                k=d-i-j
                C[i,j]=((-1)**(i+j))*np.exp(-lam*(i*i+j*j+k*k))
    return C

def ramp(anchors):
    xs=np.array([a[0] for a in anchors]); cols=np.array([a[1] for a in anchors],float)
    def f(t):
        t=np.clip(t,0,1)
        return np.stack([np.interp(t,xs,cols[:,k]) for k in range(3)],-1)
    return f

# cyclic-ish palette for phase density (dark violet -> magenta -> gold -> cream)
PAL = ramp([(0,(8,6,22)),(0.2,(40,18,70)),(0.45,(120,34,110)),
            (0.68,(210,80,90)),(0.86,(240,170,80)),(1,(252,236,200))])

def sample_both(C,zr,Nx,Nth):
    """Sample (arg z, arg w) fixing z AND fixing w (symmetrises the z<->w roles),
    for a fuller coamoeba."""
    X,Y,TH,PH=sample_curve(C,zr,Nx,Nth)
    a=[TH]; b=[PH]
    # fix w, solve z: transpose the coeff matrix (swap roles of z,w)
    Xw,Yw,THw,PHw=sample_curve(C.T,zr,Nx,Nth)
    a.append(PHw); b.append(THw)   # note swap: here 'theta'=arg w, 'phi'=arg z
    return np.concatenate(a), np.concatenate(b)

def build(d,lam,S=1000,Nx=1600,Nth=2600,tiles=2,tag='coamoeba'):
    C=curve(d,lam)
    zr=(-lam*d*3-2, lam*d*3+2)
    TH,PH=sample_both(C,zr,Nx,Nth)
    m=np.isfinite(PH)&np.isfinite(TH)
    a=TH[m]; b=PH[m]
    # tile the torus 'tiles' times in each direction
    A=[]; B=[]
    for p in range(tiles):
        for q in range(tiles):
            A.append(a+2*np.pi*p); B.append(b+2*np.pi*q)
    a=np.concatenate(A); b=np.concatenate(B)
    rng=[[0,2*np.pi*tiles],[0,2*np.pi*tiles]]
    H,_,_=np.histogram2d(a,b,bins=S,range=rng)
    H=H.T[::-1]
    np.save(f'{tag}_H.npy',H)
    dens=np.log1p(H); dens/=dens.max()+1e-9
    img=PAL(dens**0.8)
    Image.fromarray(np.clip(img,0,255).astype(np.uint8)).save(f'{tag}.png')
    print(tag,'saved  fill',(H>0).mean().round(3))

if __name__=='__main__':
    import sys
    if len(sys.argv)>1:
        build(int(sys.argv[1]),float(sys.argv[2]),
              S=int(sys.argv[3]) if len(sys.argv)>3 else 1000,tag=sys.argv[-1])
    else:
        build(5,1.0,tag='coa_d5')
        build(6,0.9,tag='coa_d6')
