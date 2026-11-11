import sys, numpy as np, time
from PIL import Image
import koi, scene
W=int(sys.argv[1]); ss=int(sys.argv[2]); out=sys.argv[3]
A=[(0,1,5,4,12,8,9,13,15,14,10,11,3,7,6,2),(0,2,10,14,12,4,6,7,15,13,5,1,3,11,9,8),(0,4,5,7,3,2,6,14,15,11,10,8,12,13,9,1),(0,8,10,2,3,1,9,11,15,7,5,13,12,14,6,4)]
pos=scene.warp(scene.petrie(4),0.85)
sc=scene.build(pos,A,[0,1,2,3],R=1.56,ppu=1/3.8,center=(0.5,0.447),flen=0.27,fw=0.027,fish_per_edge=1.25,pad_r=0.102)
t=time.time(); img=koi.render(sc,W,W,ss=ss,strip=256,quiet=True); print(time.time()-t)
Image.fromarray(koi.finish(img)).save(out)
