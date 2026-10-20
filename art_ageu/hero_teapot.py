"""Hero: Russell's teapot, crystalline-glazed, adrift between the orbits of Earth and Mars."""
import numpy as np, time, sys, math
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
import porcelain as P, teapot
SPD='/tmp/claude-0/-home-user-claude-mythos-self-play/1158cf4a-3a4a-5fc9-95bf-b9f6e7ef9209/scratchpad/'
W=int(sys.argv[1]); spp=int(sys.argv[2]); out=sys.argv[3]
H=W
def rot(yaw,pitch,roll):
    cy,sy=math.cos(yaw),math.sin(yaw); cp,sp=math.cos(pitch),math.sin(pitch); cr,sr=math.cos(roll),math.sin(roll)
    Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]); Rx=np.array([[1,0,0],[0,cp,-sp],[0,sp,cp]]); Rz=np.array([[cr,-sr,0],[sr,cr,0],[0,0,1]])
    return Ry@Rx@Rz
rng=np.random.default_rng(7)
sc=P.Scene(); gl=P.Glazes(10)
# --- teapot
V,F,N=teapot.teapot(48)
V=V-np.array([0.2,1.55,0]); R=rot(math.radians(-28),math.radians(10),math.radians(-9))
V=V@R.T; N=N@R.T
sc.add(V,F,0,N)
S,Sn=P.poisson_surface(V,F,75,0.55,rng)
k=len(S); t0=rng.random(k)**1.5*0.45; spd=0.75+0.5*rng.random(k)
spc=rng.choice([0,1,2],k,p=[0.46,0.30,0.24])
gl.glaze(0, ground=(0.97,0.62,0.66), halo=(1.0,0.88,0.82), spec=1.0, rough=0.02, ring=0.085, ring_k=0.05,
         fibres=420, fib_k=0.42, halo_w=0.05, seam=0.006, twist=0.012, lobe=0.35, petal=0.3)
gl.SC[0]=[1.00,1.00,1.00, 0.70,0.85,1.00]
gl.SC[1]=[1.00,0.98,0.86, 0.99,0.86,0.56]
gl.SC[2]=[0.92,0.99,0.95, 0.62,0.90,0.78]
gl.crystals(0,S,Sn,t0,spd,spc,Tend=0.47,grid_n=48)
# --- sun, orbits
Sun=np.array([-17.79,7.16,-26.69])
nrm=np.array([0.12,1.0,0.10]); nrm/=np.linalg.norm(nrm)
e1=np.cross(nrm,[0,0,1.]); e1/=np.linalg.norm(e1); e2=np.cross(nrm,e1)
tp=np.array([0.,0.,0.])
d=tp-Sun; d-=nrm*np.dot(d,nrm); Rt=np.linalg.norm(d); ang_t=math.atan2(np.dot(d,e2),np.dot(d,e1))
Sun_p=tp-d  # sun projected so the teapot orbit passes through origin
ratios={'earth':0.80,'tea':1.0,'mars':1.24}
th=np.linspace(0,2*np.pi,4000,endpoint=False)
def orbit(r): return Sun_p+r*(np.cos(th)[:,None]*e1+np.sin(th)[:,None]*e2)
for name,mat in (('earth',3),('tea',3),('mars',3)):
    C=orbit(Rt*ratios[name])
    # keep only points in front-ish of camera region to save tris
    keep=(C[:,2]>-60)&(C[:,2]<12)&(np.abs(C[:,0])<40)
    idx=np.nonzero(keep)[0]
    if len(idx)<2: continue
    Cv,Fv,Nv=P.tube(C[idx],0.035 if name!='tea' else 0.025,16,closed=False)
    sc.add(Cv,Fv,mat,Nv)
gl.material(3,1,(1.0,0.80,0.45),wrap=0.0,spec=1.0,F0=1.0,rough=0.05)
# planets on their orbits
def onorb(r,a): return Sun_p+r*(math.cos(a)*e1+math.sin(a)*e2)
cam=P.look_at((1.4,2.6,16.5),(-1.6,0.5,0),38,aperture=0.05,focus=16.6)
def place(r,target):
    best=None
    for a in np.linspace(-np.pi,np.pi,20000):
        p=onorb(r,a); x,y,z=P.project(cam,p,1,1)
        if z<3: continue
        dd=(x-target[0])**2+(y-target[1])**2
        if best is None or dd<best[0]: best=(dd,p)
    return best[1]
pe=place(Rt*ratios['earth'],(float(sys.argv[4]),float(sys.argv[5])))
pm=place(Rt*ratios['mars'],(float(sys.argv[6]),float(sys.argv[7])))
print('earth',pe,'mars',pm)
for c,r,mat,col,cols in ((pe,0.62,1,(0.62,0.82,0.95),[[0.90,0.99,0.93,0.60,0.88,0.72],[0.99,0.99,1.0,0.85,0.92,1.0]]),
                         (pm,0.45,2,(1.0,0.66,0.50),[[1.0,0.93,0.82,0.98,0.78,0.62],[1.0,0.97,0.93,1.0,0.86,0.80]])):
    Vs,Fs,Ns=P.sphere(c,r,160,80); sc.add(Vs,Fs,mat,Ns)
    Ss,Sns=P.poisson_surface(Vs,Fs,40,r*0.38,rng)
    kk=len(Ss); base=4 if mat==1 else 6
    gl.SC[base]=cols[0]; gl.SC[base+1]=cols[1]
    gl.glaze(mat, ground=col, halo=tuple(min(1,x+0.12) for x in col), spec=1.0, rough=0.02, ring=0.03*r, ring_k=0.08,
             fibres=300, fib_k=0.4, halo_w=0.04*r, seam=0.004*r, twist=0.01, lobe=0.3, petal=0.3)
    gl.crystals(mat,Ss,Sns,rng.random(kk)*0.2*r,np.full(kk,1.0),base+rng.integers(0,2,kk),Tend=0.30*r,grid_n=32)
sc.finish()
# --- lights/env
sd=(Sun-tp)/np.linalg.norm(Sun-tp)
E=[0.78,0.78,0.98, 1.0,0.86,0.90, 1.0,0.92,0.80, 3,
   *sd, 0.985, 16,14.5,12,   0.75,-0.2,0.62, 0.975, 5,5.4,7,   -0.2,0.9,0.4, 0.99, 6,6,6.5]
Lp=Sun*0.25
L=[*Lp, 3.5, 1.55,1.42,1.30, 0.50,0.48,0.58, 1.0, 6.0, 0.5, 1.0, 0.0]
GP=[-100, 1,1,1, 1,1,1, 0, 1, 0, 0, 0.0, 1,1,1, 1, 0]
t=time.time(); img=P.render(sc,gl,cam,E,L,GP,W,H,spp,bands=8,verbose=W>1500); print('render',time.time()-t)
np.save(SPD+out+'.npy',img); sun=np.array(P.project(cam,Sun,W,H)); print('sun px',sun/W); np.save(SPD+out+'_sun.npy',sun)
