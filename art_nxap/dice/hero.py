import numpy as np, time, sys, json, math
from geom import *; from scene import *; import tracer
from PIL import Image
from scipy.ndimage import gaussian_filter
cfg=json.load(open(sys.argv[1])); size=int(sys.argv[2]); spp=int(sys.argv[3]); out=sys.argv[4]
ya=int(sys.argv[5]) if len(sys.argv)>5 else 0; yb=int(sys.argv[6]) if len(sys.argv)>6 else None

def make(kind, p):
    if kind=='prism': return prism(p['n'], p['L'])
    if kind=='trap': return trapezohedron(p['n'])
    return platonic(kind)

def Rz(a):
    c,s=math.cos(a),math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1.]])

S=Scene()
for d in cfg['dice']:
    V,F=make(d['kind'],d)
    if 'vref' in cfg:
        vol=mass_props(V,F)[0]; V=V*(cfg['vref']/vol)**(1/3)*d.get('size',1.0)
    seed=d.get('seed',0)
    while True:
        Vb,R,xr,f,_=pose_die(V,F,seed)
        want=d.get('land')  # 'side' / 'end' / None
        if want is None or (want=='side' and f>=2) or (want=='end' and f in (0,1)): break
        seed+=1
    R=Rz(math.radians(d.get('yaw',0)))@R
    zr=-(Vb@R.T)[:,2].min()
    S.add(Vb,F,R,(d['x'],d['y'],zr),SORBET[d['col']] if isinstance(d['col'],str) else d['col'],
          strength=d.get('strength',cfg.get('strength',0.9)),ink=tuple(cfg.get('ink',(0.36,0.29,0.42))),gscale=d.get('gscale',0.62))
PL,OB,GL,ATL=S.arrays()
SW=np.array(cfg['sweep']); PAP=np.array(cfg['paper'])
EN,s=sun_env(*cfg['sun'],**cfg.get('envkw',{})); LT=np.array(cfg['light'])
CB=np.array(cfg['cbox']); GH,GW=cfg['cgrid']
import os
cache=cfg.get('cgcache')
t=time.time()
if cache and os.path.exists(cache): CG=np.load(cache)
else:
    CG=tracer.photons(PL,OB,GL,ATL,EN,LT,CB,GH,GW,int(cfg['photons']),1)
    if cache: np.save(cache,CG)
CG=np.stack([gaussian_filter(CG[...,c],cfg.get('cblur',1.0)) for c in range(3)],-1); print('ph',time.time()-t,flush=True)
c=cfg['cam']; CAM=camera(c['eye'],c['tgt'],c['fov'],c.get('ap',0),c.get('focus'))
H=W=size
if yb is None: yb=H
t=time.time(); img=tracer.render(H,W,ya,yb,CAM,PL,OB,GL,ATL,SW,PAP,EN,LT,CG,CB,spp,24,7); print('r',time.time()-t,flush=True)
if out.endswith('.npy'): np.save(out,img.astype(np.float32))
else: Image.fromarray(tonemap(img,**cfg.get('tone',{}))).save(out)
