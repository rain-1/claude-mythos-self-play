import numpy as np, time, sys
from geom import *; from scene import *; import tracer
from PIL import Image
S=Scene()
dice=[(prism(5,1.62),'strawberry',0),(platonic('ico'),'mint',1),(prism(3,0.95),'butter',2),(platonic('cube'),'sky',3),(prism(7,1.8),'lilac',4)]
xs=np.linspace(-3.2,3.2,len(dice))
for (VF,col,sd),x in zip(dice,xs):
    V,F=VF; Vb,R,xr,f,_=pose_die(V,F,sd)
    S.add(Vb,F,R,(x,0.3*(sd%2),xr[2]),SORBET[col],strength=0.9,ink=(0.36,0.29,0.42))
PL,OB,GL,ATL=S.arrays()
SW=np.array([4.0,4.0]); PAP=np.array([0.96,0.955,0.95, 0.99,0.90,0.88, 0.93,0.90,1.0, 0.98,0.70,0.75, 0.0,0.09,6.0])
EN,s=sun_env(110,38); LT=np.array([2.6,2.45,2.25,0.55,0.05])
CB=np.array([-6,6,-6,4.0]); GH,GW=600,720
t=time.time(); CG=tracer.photons(PL,OB,GL,ATL,EN,LT,CB,GH,GW,4_000_000,1); print('ph',time.time()-t,CG.max())
from scipy.ndimage import gaussian_filter
CG=np.stack([gaussian_filter(CG[...,c],1.2) for c in range(3)],-1)
CAM=camera((0,-9.5,3.6),(0,0.2,0.6),42)
H,W=int(sys.argv[1])*3//4,int(sys.argv[1])
t=time.time(); img=tracer.render(H,W,0,H,CAM,PL,OB,GL,ATL,SW,PAP,EN,LT,CG,CB,int(sys.argv[2]),14,1); print('r',time.time()-t)
Image.fromarray(tonemap(img)).save('test1.png')
