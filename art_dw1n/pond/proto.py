import sys, json, numpy as np, time
from PIL import Image
import koi, scene
W=int(sys.argv[1]); which=int(sys.argv[2]) if len(sys.argv)>2 else 0
A=[(0,1,5,4,12,8,9,13,15,14,10,11,3,7,6,2),(0,2,10,14,12,4,6,7,15,13,5,1,3,11,9,8),(0,4,5,7,3,2,6,14,15,11,10,8,12,13,9,1),(0,8,10,2,3,1,9,11,15,7,5,13,12,14,6,4)]
B=[(0,1,9,13,12,8,10,11,15,14,6,2,3,7,5,4),(0,2,6,7,3,11,10,14,15,13,9,8,12,4,5,1),(0,4,6,14,12,13,5,7,15,11,9,1,3,2,10,8),(0,8,9,11,3,1,5,13,15,7,6,4,12,14,10,2)]
sol=[A,B][which]
pos=scene.warp(scene.petrie(4),float(sys.argv[3]))
sc=scene.build(pos,sol,[0,1,2,3],R=1.56,ppu=1/3.72,flen=0.27,fw=0.027,fish_per_edge=1.25)
t=time.time(); out=koi.render(sc,W,W,ss=2,quiet=True); print(time.time()-t)
Image.fromarray(koi.finish(out)).save(f'proto_{which}_{W}_{sys.argv[3]}.png')
