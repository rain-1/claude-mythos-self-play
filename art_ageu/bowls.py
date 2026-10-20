"""Sixty-One Bowls: the 61 up-down permutations a1<a2>a3<a4>a5<a6 as ruffled crystalline-glaze bowls;
the six values are the rim heights around each bowl. Sorted by first value (the Entringer row 16,16,14,10,5)
and laid in a centred hexagon (61 = 1+6+12+18+24) row by row, ox-turning (boustrophedon)."""
import numpy as np, sys, time, math
from itertools import permutations
from PIL import Image
import porcelain as P
SPD='/tmp/claude-0/-home-user-claude-mythos-self-play/1158cf4a-3a4a-5fc9-95bf-b9f6e7ef9209/scratchpad/'
W=int(sys.argv[1]); spp=int(sys.argv[2]); out=sys.argv[3]; H=W
amp=float(sys.argv[4]) if len(sys.argv)>4 else 0.20
TEND=float(sys.argv[6]) if len(sys.argv)>6 else 0.55
A=sorted([p for p in permutations(range(1,7)) if p[0]<p[1]>p[2]<p[3]>p[4]<p[5]])
rows=[5,6,7,8,9,8,7,6,5]; sp=2.16
pos=[];dirs=[]
k=0
for r,nr in enumerate(rows):
    z=(r-4)*sp*math.sqrt(3)/2
    xs=[(c-(nr-1)/2)*sp for c in range(nr)]
    d=1
    if r%2==1: xs=xs[::-1]; d=-1
    for x in xs: pos.append((x,z)); dirs.append(d)
assert len(pos)==61
def rim_fn(vals,th,phase):
    # periodic cubic (Catmull-Rom) interpolation of 6 values at angles phase+2πk/6
    m=(np.array(vals,float)-3.5)/2.5
    u=((th-phase)/(2*np.pi)*6)%6
    i=np.floor(u).astype(int); t=u-i
    p0=m[(i-1)%6];p1=m[i%6];p2=m[(i+1)%6];p3=m[(i+2)%6]
    return 0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3)
def bowl(cx,cz,vals,phase,nr=40,nt=180,R=0.98):
    rho=np.linspace(0,1,nr); th=np.linspace(0,2*np.pi,nt,endpoint=False)
    Rh,Th=np.meshgrid(rho,th,indexing='ij')
    m=rim_fn(vals,Th,phase)
    rr=R*Rh*(1+0.10*m*Rh**4)
    y=0.06+0.42*Rh**2*(1-0.25*Rh)+amp*m*Rh**5
    V=np.stack([cx+rr*np.cos(Th),y,cz+rr*np.sin(Th)],-1).reshape(-1,3)
    idx=lambda i,j:i*nt+(j%nt)
    F=[]
    for i in range(nr-1):
        for j in range(nt):
            a=idx(i,j);b=idx(i,j+1);c=idx(i+1,j);d=idx(i+1,j+1)
            F.append([a,c,b]);F.append([b,c,d])
    F=np.array(F,np.int64)
    rimC=V.reshape(nr,nt,3)[-1]
    return V,F,rimC
sc=P.Scene(); gl=P.Glazes(12)
HUE={1:(0.98,0.70,0.74),2:(0.99,0.80,0.66),3:(0.99,0.92,0.66),4:(0.70,0.90,0.80),5:(0.70,0.82,0.98)}
rng=np.random.default_rng(5)
seeds={c:([],[]) for c in HUE}
for n,(p,(x,z),d) in enumerate(zip(A,pos,dirs)):
    phase=0.0 if d>0 else math.pi   # value a1 points the way the ox walks
    V,F,rimC=bowl(x,z,p,phase)
    N=P.vertex_normals(V,F)
    if N[0,1]<0: N=-N
    mat=p[0]
    sc.add(V,F,mat,N)
    Cv,Fv,Nv=P.tube(rimC,0.028,12,closed=True); sc.add(Cv,Fv,7,Nv)
    # crystals: one at the bottom, a few on the walls
    Vr=V.reshape(40,180,3)
    pts=[Vr[0,0]]; nm=[(0,1,0)]
    for q in range(0):
        i=rng.integers(12,30); j=rng.integers(0,180)
        pts.append(Vr[i,j]); nm.append(N.reshape(40,180,3)[i,j])
    seeds[mat][0].extend(pts); seeds[mat][1].extend(nm)
for c,col in HUE.items():
    gl.glaze(c, ground=col, halo=tuple(min(1,v+0.10) for v in col), spec=1.0, rough=0.02, ring=0.05, ring_k=0.05,
             fibres=300, fib_k=0.42, halo_w=0.03, seam=0.004, twist=0.01, lobe=0.35, petal=0.3)
    S=np.array(seeds[c][0]); Sn=np.array(seeds[c][1]); kk=len(S)
    t0=np.where(np.arange(kk)==0,0,0)+rng.random(kk)*0.25
    t0[S[:,1]<0.07]=0.0
    spd=np.ones(kk); spc=np.full(kk,c)
    gl.crystals(c,S,Sn,t0,spd,spc,Tend=TEND,grid_n=96)
CR={1:(0.62,0.80,0.99),2:(0.95,0.62,0.72),3:(0.66,0.86,0.80),4:(0.80,0.72,0.97),5:(0.99,0.80,0.62)}
for c in CR: gl.SC[c]=[1.0,1.0,1.0,*CR[c]]
gl.material(7,1,(0.98,0.72,0.36),wrap=0.0,spec=1.0,F0=1.0,rough=0.04)
gl.material(9,3,wrap=0.0)
t=time.time(); sc.finish(); print('bvh',time.time()-t, flush=True)
E=[0.82,0.85,1.0, 1.0,0.93,0.92, 0.96,0.90,0.88, 2,
   -0.55,0.70,0.45, 0.975, 10,9.6,9.2,   0.6,0.55,-0.6, 0.985, 5,5.2,6]
L=[-16,11,-6, 2.0, 1.22,1.14,1.06, 0.55,0.54,0.58, 1.0, 3.0, 0.55, 1.0, 1.0]
GP=[0.0, 0.97,0.95,0.93, 0.92,0.92,0.98, 2, 14.0, 1, 9, 0.0, 1,1,1, 80, 0.03]
cam=P.look_at((0.0,23,13.5),(0,0,0.3),44,aperture=0.0,focus=26)
t=time.time(); img=P.render(sc,gl,cam,E,L,GP,W,H,spp,bands=8,verbose=W>1500); print('render',time.time()-t)
np.save(SPD+out+'.npy',img)
Image.fromarray(P.tonemap(img,float(sys.argv[5]) if len(sys.argv)>5 else 0.95)).save(SPD+out+'.png')
