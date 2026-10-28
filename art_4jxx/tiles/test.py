import numpy as np, sys
from PIL import Image
from wall import render_wall
ty,tx=24,24
rng=np.random.default_rng(2)
g=np.fromfunction(lambda i,j: ((i+2*j)%5<2),(ty,tx)).astype(int)
c0=np.array([0.97,0.96,0.93]); c1=np.array([0.55,0.72,0.92])
cols=np.where(g[...,None]==1,c1,c0)
win={"rect":(-0.75,0.15,-0.35,0.95),"nx":2,"ny":3,"I":1.1,"room":0.08,"par":1.3}
img=render_wall(960,960,ty,tx,cols,None,win=win)
img=img/(1+img/3)*1.2
Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).save(sys.argv[1])
