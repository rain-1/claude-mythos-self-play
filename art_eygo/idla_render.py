"""Render IDLA piece: warm occupation orb (frozen perfect disk) + electric
trembling log-correlated edge (the free frontier). Soft-haze register."""
import numpy as np, sys
from scipy.ndimage import gaussian_filter, binary_erosion
sys.path.insert(0,'art_eygo'); import common as C
from PIL import Image

OUT=int(sys.argv[1]) if len(sys.argv)>1 else 2048
occ=np.load("art_eygo/idla_occ.npy"); visit=np.load("art_eygo/idla_visit.npy")
M=occ.shape[0]
# crop tight to disk + margin, then work in a square
ys,xs=np.where(occ); cy,cx=int(ys.mean()),int(xs.mean())
R=int(np.sqrt(occ.sum()/np.pi)); half=int(R*1.32)
y0,y1=cy-half,cy+half; x0,x1=cx-half,cx+half
occ=occ[y0:y1,x0:x1]; visit=visit[y0:y1,x0:x1]; W=occ.shape[0]

# ---- FROZEN: occupation measure (Green's function glow, center-bright) ----
v=np.log1p(visit.astype(np.float64))
v/= v.max()+1e-9
# reveal SRW filament texture via mild high-pass (not a flat disk)
v = np.clip(v + 0.55*(v-gaussian_filter(v,3.0)), 0, None)
warm=C.ramp([(0,(0,0,0)),(0.28,(0.20,0.05,0.02)),(0.55,(0.75,0.30,0.06)),
             (0.80,(1.0,0.66,0.20)),(1.0,(1.0,0.93,0.72))], v**0.9)
orb=warm*np.clip(v*1.15,0,1)[...,None]

# ---- FREE: trembling log-correlated frontier ----
bd = occ & ~binary_erosion(occ)                 # perimeter occupied cells
edge = gaussian_filter(bd.astype(float), 0.6)
glow = C.bloom(bd.astype(float),(1.2,4,12),(0.7,0.4,0.25))
cyan=np.array([0.30,0.85,1.0])
rim = edge[...,None]*cyan*1.4 + glow[...,None]*cyan*0.9

rgb = orb + rim
rgb = C.filmic(rgb,1.3)**(1/1.1)
im=C.to_img(rgb)
# center in a square OUT canvas with black margin (negative space = 'not reached')
canvas=Image.new('RGB',(OUT,OUT),(0,0,0))
s=int(OUT*0.9); im2=im.resize((s,s),Image.LANCZOS)
canvas.paste(im2,((OUT-s)//2,(OUT-s)//2))
canvas.save("art_eygo/02_idla.png"); print("saved 02_idla.png W_native",W,"R",R)
