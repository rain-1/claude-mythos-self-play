import sys, numpy as np, time
from PIL import Image
import koi, scene
W=int(sys.argv[1]); ss=int(sys.argv[2]); out=sys.argv[3]
A=[(0,1,5,4,12,8,9,13,15,14,10,11,3,7,6,2),(0,2,10,14,12,4,6,7,15,13,5,1,3,11,9,8),(0,4,5,7,3,2,6,14,15,11,10,8,12,13,9,1),(0,8,10,2,3,1,9,11,15,7,5,13,12,14,6,4)]
pos=scene.warp(scene.petrie(4),0.85)
sc=scene.build(pos,A,[0,1,2,3],R=1.56,ppu=1/3.8,center=(0.5,0.447),flen=0.27,fw=0.027,fish_per_edge=1.25,pad_r=0.102)
rng=np.random.default_rng(8)
gl=[]
paths=np.concatenate([l['path'][::6] for l in sc['loops']])
while len(gl)<38:
    a=rng.random()*6.283; r=1.5*rng.random()**0.5; x,y=r*np.cos(a),r*np.sin(a)
    if np.min(np.hypot(pos[:,0]-x,pos[:,1]-y))<0.14: continue
    gl.append((x,y,0.005+0.008*rng.random()**2))
sc['glints']=gl
H=koi.hexc
sc['flies']=[(-1.03,-1.03,0.9,0.135,H('#5f86ea')),(1.16,0.82,-2.2,0.125,H('#ff6f5c')),(0.26,1.38,2.6,0.115,H('#b565dc'))]
t=time.time(); img=koi.render(sc,W,W,ss=ss,strip=256,quiet=True); print(time.time()-t)
Image.fromarray(koi.finish(img)).save(out)
