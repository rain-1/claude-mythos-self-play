"""No Four Corners Alike: a square crystalline-glaze dish; 14x14 crystals coloured by a square-free
2-colouring (no axis-parallel square has 4 corners of one colour), anti-symmetric under a quarter turn."""
import numpy as np, json, sys, time, math
from PIL import Image
import porcelain as P
SPD='/tmp/claude-0/-home-user-claude-mythos-self-play/1158cf4a-3a4a-5fc9-95bf-b9f6e7ef9209/scratchpad/'
W=int(sys.argv[1]); spp=int(sys.argv[2]); out=sys.argv[3]; H=W
Tf=float(sys.argv[4]) if len(sys.argv)>4 else 0.55
col=np.array(json.load(open('math_squaregame/squarefree.json'))['14_sym'])
n=14
# dish height field
def sup(x,z,p=7): return (np.abs(x)**p+np.abs(z)**p)**(1/p)
R=1.42; g=900
xs=np.linspace(-R,R,g); X,Z=np.meshgrid(xs,xs); rho=sup(X,Z)
well=1.0; rim=1.30
Hh=np.where(rho<well,0.07,0.0)
t=np.clip((rho-well)/(rim-well),0,1)
Hh=np.where(rho>=well, 0.07+0.11*(t*t*(3-2*t))**0.9, Hh)
# outer lip: round down to the table between rim and R
u=np.clip((rho-rim)/(R-rim),0,1)
Hh=np.where(rho>rim, 0.18*np.sqrt(np.maximum(1-u**2,0)), Hh)
Hh=np.where(rho>=R*0.999,0.0,Hh)
V,F=P.grid_mesh(Hh,-R,R,-R,R)
# orient up
Nn=P.vertex_normals(V,F)
if Nn[len(V)//2,1]<0: F=F[:,::-1]; Nn=-Nn
# materials: gold band near the rim crest
cen=V[F].mean(1); rc=sup(cen[:,0],cen[:,2])
mat=np.where((rc>rim-0.012)&(rc<rim+0.035),3,0)
mat=np.where(rc>=R*0.995,-1,mat)
sc=P.Scene()
for m in (0,3):
    sel=mat==m
    used=np.unique(F[sel]); remap=-np.ones(len(V),int); remap[used]=np.arange(len(used))
    sc.add(V[used],remap[F[sel]],m,Nn[used])
import teapot
TP=len(sys.argv)>7 and sys.argv[7]=='tea'
if TP:
    Vt,Ft,Nt=teapot.teapot(40)
    ang=math.radians(-150); Rm=np.array([[math.cos(ang),0,math.sin(ang)],[0,1,0],[-math.sin(ang),0,math.cos(ang)]])
    Vt=(Vt*0.42)@Rm.T+np.array([1.05,0.0,-2.45]); Nt=Nt@Rm.T
    sc.add(Vt,Ft,6,Nt)
sc.finish()
gl=P.Glazes(10)
if TP:
    rng2=np.random.default_rng(3)
    St,Stn=P.poisson_surface(Vt,Ft,60,0.24,rng2); kt=len(St)
    gl.glaze(6, ground=(0.70,0.88,0.84), halo=(0.86,0.97,0.93), spec=1.0, rough=0.02, ring=0.03, ring_k=0.05,
             fibres=300, fib_k=0.42, halo_w=0.02, seam=0.003, twist=0.01, lobe=0.3, petal=0.3)
    gl.crystals(6,St,Stn,rng2.random(kt)*0.06,np.ones(kt),np.where(rng2.random(kt)<0.6,0,1),Tend=0.21,grid_n=48)
GC=[(0.97,0.92,0.84),(0.66,0.85,0.82),(0.84,0.80,0.95),(0.98,0.80,0.72)][int(sys.argv[6])]
gl.glaze(0, ground=GC, halo=(1.0,0.99,0.97), spec=1.0, rough=0.02, ring=0.011, ring_k=0.06,
         fibres=260, fib_k=0.42, halo_w=0.010, seam=0.0012, twist=0.01, lobe=0.3, petal=0.3)
PAL=[([0.90,0.96,1.00, 0.45,0.66,0.97],[1.00,0.92,0.92, 0.97,0.48,0.60]),
     ([1.00,0.99,0.92, 0.99,0.86,0.50],[1.00,0.94,0.93, 0.98,0.55,0.62]),
     ([1.00,1.00,1.00, 0.70,0.88,1.00],[1.00,0.97,0.88, 0.99,0.80,0.48]),
     ([0.98,1.00,1.00, 0.55,0.80,0.96],[1.00,1.00,0.96, 0.92,0.96,0.80])][int(sys.argv[6])]
gl.SC[0]=PAL[0]; gl.SC[1]=PAL[1]
gl.material(3,1,(0.98,0.72,0.36),wrap=0.0,spec=1.0,F0=1.0,rough=0.03)
gl.material(5,3,wrap=0.0)
rng=np.random.default_rng(11)
cell=1.84/n
S=[];spc=[]
for i in range(n):
    for j in range(n):
        x=-0.92+(j+0.5)*cell; z=-0.92+(i+0.5)*cell
        S.append([x+rng.normal(0,0.06)*cell,0.07,z+rng.normal(0,0.06)*cell]); spc.append(col[i,j])
S=np.array(S); k=len(S)
t0=rng.random(k)*0.18*cell; spd=np.ones(k)
gl.crystals(0,S,np.tile([0,1,0.],(k,1)),t0,spd,np.array(spc),Tend=Tf*cell,grid_n=64)
E=[0.80,0.84,1.0, 1.0,0.92,0.92, 0.96,0.90,0.88, 2,
   -0.55,0.70,0.45, 0.975, 12,11.5,11,   0.6,0.55,-0.6, 0.985, 6,6.2,7]
L=[-8,6,3, 1.2, 1.0,0.95,0.90, 0.42,0.42,0.50, 1.0, 1.5, 0.55, 1.0, 1.0]
GP=[0.0, 0.99,0.97,0.96, 0.97,0.80,0.84, 1, 0.16, 1, 5, 0.0, 1,1,1, 60, 0.035]
cam=P.look_at((0.25,5.6,1.1),(0.0,0.0,0.03),34,aperture=0.0,focus=5.6)
if TP: cam=P.look_at((0.35,4.4,3.4),(0.15,0.10,-0.62),43,aperture=0.035,focus=5.45)
t=time.time(); img=P.render(sc,gl,cam,E,L,GP,W,H,spp,bands=8,verbose=W>1500); print('render',time.time()-t)
np.save(SPD+out+'.npy',img)
Image.fromarray(P.tonemap(img,float(sys.argv[5]) if len(sys.argv)>5 else 1.0)).save(SPD+out+'.png')
