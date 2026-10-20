import numpy as np, time, sys
from PIL import Image
import porcelain as P
SP='/tmp/claude-0/-home-user-claude-mythos-self-play/1158cf4a-3a4a-5fc9-95bf-b9f6e7ef9209/scratchpad/'
import teapot
V,F,N=teapot.teapot(40)
sc=P.Scene(); sc.add(V,F,0,N); sc.finish()
def surf_pts(V,F,k,rng):
    A=np.linalg.norm(np.cross(V[F[:,1]]-V[F[:,0]],V[F[:,2]]-V[F[:,0]]),axis=1)
    fi=rng.choice(len(F),k,p=A/A.sum()); a=rng.random(k);b=rng.random(k); m=a+b>1; a[m]=1-a[m]; b[m]=1-b[m]
    S=V[F[fi,0]]*(1-a-b)[:,None]+V[F[fi,1]]*a[:,None]+V[F[fi,2]]*b[:,None]
    return S, np.cross(V[F[fi,1]]-V[F[fi,0]],V[F[fi,2]]-V[F[fi,0]])
gl=P.Glazes()
gl.glaze(0, ground=(0.95,0.55,0.58), halo=(1.0,0.90,0.80), spec=1.0, rough=0.02, ring=0.05, ring_k=0.12, fibres=360, fib_k=0.4, halo_w=0.06, seam=0.006, bump=0.0, lobe=float(sys.argv[5]), petal=float(sys.argv[6]))
gl.material(1,3,wrap=0.0)
gl.SC[0]=[0.93,0.97,1.00, 0.62,0.80,0.98]
gl.SC[1]=[0.99,0.95,0.80, 0.98,0.86,0.55]
rng=np.random.default_rng(2)
k=140; S,fn=surf_pts(V,F,k,rng)
t0=rng.random(k)**2*0.6; sp=0.8+0.4*rng.random(k); spc=(rng.random(k)<0.3).astype(int)
gl.crystals(0,S,fn,t0,sp,spc,Tend=0.5,grid_n=40)
E=[0.70,0.80,1.0, 1.0,0.90,0.88, 0.95,0.85,0.85, 2,
   -0.45,0.75,0.5, 0.96, 14,13.5,13,   0.8,0.35,0.5, 0.988, 9,8.6,9.4]
L=[-6,9,6, 1.2, 1.35,1.28,1.2, 0.40,0.40,0.48, 1.0, 4.0, 0.5, 1.0, 1.0]
GP=[0.0, 0.62,0.86,0.80, 0.80,0.78,0.94, 2, 14, 1, 1, 0.006, 0.86,0.82,0.94, 30, 0.03]
W,H,spp=[int(x) for x in sys.argv[1:4]]
cam=P.look_at((7,4.5,9),(0.2,1.3,0),32) if len(sys.argv)<5 else P.look_at((2.5,2.4,4.0),(0.3,1.5,0.9),float(sys.argv[4]))
t=time.time(); img=P.render(sc,gl,cam,E,L,GP,W,H,spp,bands=2,verbose=False); print(time.time()-t)
Image.fromarray(P.tonemap(img,0.95)).save(SP+'tp1.png')
