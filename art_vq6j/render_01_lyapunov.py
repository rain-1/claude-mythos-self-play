import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import sys, time

SEQ="BBBBBBAAAAAA"; A0,A1,B0,B1=2.5,4.0,2.5,4.0
OUT=int(sys.argv[1]) if len(sys.argv)>1 else 4096
SS=int(sys.argv[2]) if len(sys.argv)>2 else 2
N=int(sys.argv[3]) if len(sys.argv)>3 else 800
WARM=int(sys.argv[4]) if len(sys.argv)>4 else 500
S=OUT*SS
seq=[0 if c=='A' else 1 for c in SEQ]; L=len(seq)
t0=time.time()
a=np.linspace(A0,A1,S,dtype=np.float32)
b=np.linspace(B1,B0,S,dtype=np.float32)  # top row = high b
lam=np.empty((S,S),dtype=np.float32)
CH=max(64, S//16)
for r0 in range(0,S,CH):
    r1=min(S,r0+CH)
    B=b[r0:r1,None]*np.ones((1,S),dtype=np.float32)
    A=a[None,:]*np.ones((r1-r0,1),dtype=np.float32)
    R=[A,B]
    x=np.full((r1-r0,S),0.5,dtype=np.float32)
    for n in range(WARM):
        x=R[seq[n%L]]*x*(1.0-x)
    acc=np.zeros((r1-r0,S),dtype=np.float32)
    for n in range(N):
        r=R[seq[(WARM+n)%L]]
        x=r*x*(1.0-x)
        acc+=np.log(np.maximum(np.abs(r*(1.0-2.0*x)),1e-12))
    lam[r0:r1]=acc/N
    print("band",r0,r1,"t=%.1f"%(time.time()-t0)); sys.stdout.flush()
np.save("_lam_full.npy", lam)
print("lam computed", lam.shape, "t=%.1f"%(time.time()-t0))

def colorize(lam, gold_k=1.7, fil_w=0.085):
    neg=lam<0
    d=np.clip(-lam,0,None).astype(np.float32); t=1-np.exp(-d*gold_k)
    def ramp(t,c0,c1,c2):
        a=np.clip(t*2,0,1); bb=np.clip(t*2-1,0,1)
        return [np.where(t<0.5,c0[k]+(c1[k]-c0[k])*a,c1[k]+(c2[k]-c1[k])*bb) for k in range(3)]
    sc=ramp(t,(0.28,0.05,0.0),(0.98,0.58,0.05),(1.0,0.92,0.66))
    p=np.clip(lam,0,None).astype(np.float32)
    dk=np.exp(-p*1.1)
    base=[0.012+(0.06-0.012)*dk,0.02+(0.09-0.02)*dk,0.05+(0.20-0.05)*dk]
    glow=np.exp(-(p/fil_w)**2)
    cc=[base[0]+glow*0.55,base[1]+glow*0.85,base[2]+glow*0.95]
    img=np.empty(lam.shape+(3,),dtype=np.float32)
    for k in range(3): img[...,k]=np.where(neg,sc[k],cc[k])
    return np.clip(img,0,1)

img=colorize(lam); del lam
# subtle bloom: lift bright filigree+gold
lum=img.mean(2)
mask=np.clip(lum-0.6,0,1)
for k in range(3):
    img[...,k]=np.clip(img[...,k]+0.18*gaussian_filter((mask*img[...,k]).astype(np.float32), sigma=SS*1.5),0,1)
out=(img*255).astype(np.uint8); del img
im=Image.fromarray(out)
if SS>1: im=im.resize((OUT,OUT),Image.LANCZOS)
im.save("01_edge_of_chaos.png")
print("SAVED 01_edge_of_chaos.png", im.size, "total t=%.1f"%(time.time()-t0))
