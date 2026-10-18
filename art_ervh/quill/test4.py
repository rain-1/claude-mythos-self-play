import numpy as np, json, time
from PIL import Image
import quill as Q, sampler as SM
d5=json.load(open('../math_poly/runs/t5.json'))['found']; d7=json.load(open('../math_poly/runs/e7.json'))['found']
d9=json.load(open('../math_poly/runs/t9.json'))['found']
tri=np.array([[0.04,0.06],[1.0,0.32],[0.25,0.97]]); 
rng=np.random.default_rng(5)
polys=[np.array(x['verts']) for x in [d5[0],d5[7],d7[3],d7[40],None,d7[9],d9[0],d9[1],d9[2]] if x is not None]
polys.insert(4,None)
k=2; S=300*k; gx=90*k; tilt=30; cs=np.cos(np.radians(tilt))
Ww=int(3*S+2*gx+2*130*k); Hw=int((3*S+2*gx)/cs+2*130*k/cs)
t=time.time()
H,A,G=SM.build(polys,3,3,S,gx,gx/cs,tilt,k,130*k/cs,4,Ww,Hw)
print('build',time.time()-t); t=time.time()
img=Q.render(H,A,tilt_deg=tilt,spp=4,out_w=Ww//k,light=(-0.65,0.30,0.70),amb=(0.62,0.62,0.70),sun=(0.75,0.72,0.68),G=G)
print('render',time.time()-t)
Image.fromarray(Q.tonemap(img)).save('proto/t4.png')
