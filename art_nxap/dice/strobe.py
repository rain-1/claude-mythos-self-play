import numpy as np, math, sys, json, time
from geom import *; from scene import *; import sim, tracer
from PIL import Image
from scipy.ndimage import gaussian_filter
cfg=json.load(open(sys.argv[1])); Wd=int(sys.argv[2]); spp=int(sys.argv[3]); out=sys.argv[4]
V,F=prism(5,cfg.get('L',1.62))
vol=mass_props(V,F)[0]; V=V*(2.2/vol)**(1/3)
Vb,Nb,Ii=sim.prepare(V,F)
seed=cfg['seed']; rng=np.random.default_rng(seed); u=rng.random(9)
q0=sim.rand_quat(u[0],u[1],u[2]); rec=np.zeros((40000,7))
f,t,n=sim.throw(Vb,Nb,Ii,np.array([0,0,cfg.get('h0',2.6)]),q0,np.array(cfg.get('v0',[3.2,0,0.8])),np.array([1.5*(2*u[6]-1),9*(2*u[7]-1),2*(2*u[8]-1)]),cfg.get('e',0.45),0.35,2e-4,15.0,5,rec)
rec=rec[:n]; P=rec[:,:3]
# pick copies: greedy, min centroid separation
sep=cfg.get('sep',1.45); idx=[0]
for k in range(1,n):
    if np.linalg.norm(P[k]-P[idx[-1]])>=sep: idx.append(k)
if np.linalg.norm(P[-1]-P[idx[-1]])<sep: idx[-1]=n-1
else: idx.append(n-1)
print('copies',len(idx),'face',f)
wheel=['strawberry','coral','peach','butter','lime','mint','sky','periwinkle','lilac','bubblegum']
def lerp(a,b,t): return tuple(a[i]*(1-t)+b[i]*t for i in range(3))
S=Scene()
off=np.array(cfg.get('off',[0,0,0]))
K=len(idx)
for j,k in enumerate(idx):
    s=j/(K-1)*(len(wheel)-1); i0=int(min(s,len(wheel)-2)); col=lerp(SORBET[wheel[i0]],SORBET[wheel[i0+1]],s-i0)
    R=sim.qrot(rec[k,3:])
    S.add(Vb,F,R,P[k]+off,col,strength=cfg.get('strength',1.0),ink=tuple(cfg.get('ink',(0.36,0.29,0.42))))
PL,OB,GL,ATL=S.arrays()
np.save(out+'.path.npy',P)
SW=np.array(cfg['sweep']); PAP=np.array(cfg['paper'])
EN,s=sun_env(*cfg['sun']); LT=np.array(cfg['light'])
CB=np.array(cfg['cbox']); GH,GW=cfg['cgrid']
t0=time.time(); CG=tracer.photons(PL,OB,GL,ATL,EN,LT,CB,GH,GW,int(cfg['photons']),1)
CG=np.stack([gaussian_filter(CG[...,c],cfg.get('cblur',1.0)) for c in range(3)],-1); print('ph',time.time()-t0,flush=True)
c=cfg['cam']; CAM=camera(c['eye'],c['tgt'],c['fov'],c.get('ap',0),c.get('focus'))
H=int(Wd*cfg.get('aspect',0.5625))
t0=time.time(); img=tracer.render(H,Wd,0,H,CAM,PL,OB,GL,ATL,SW,PAP,EN,LT,CG,CB,spp,24,7); print('r',time.time()-t0,flush=True)
if out.endswith('.npy'): np.save(out,img.astype(np.float32))
else: Image.fromarray(tonemap(img,**cfg.get('tone',{}))).save(out)
