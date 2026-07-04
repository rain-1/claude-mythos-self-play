"""Render FPP piece: warm free geodesic tree + cool frozen limit-shape rings."""
import numpy as np, sys
from scipy.ndimage import gaussian_filter
sys.path.insert(0,'art_eygo'); import common as C
from PIL import Image

tag=sys.argv[1] if len(sys.argv)>1 else "fpp2048"
OUT=int(sys.argv[2]) if len(sys.argv)>2 else 2048
dist=np.load(f"art_eygo/{tag}_dist.npy"); flow=np.load(f"art_eygo/{tag}_flow.npy")
W=dist.shape[0]
fin=np.isfinite(dist); dmax=np.nanmax(dist[fin])

# ---- FREE: geodesic tree, brightness = log discharge (raw, dark bulk) ----
tb=(np.log1p(flow)/np.log1p(flow).max())**0.78   # dark bg, sparse bright rivers
tb=np.clip((tb-0.11)/0.89,0,1)                    # true-black floor
# desaturate dim capillaries (neutral slate, recedes) -> warms only on real rivers (no brown wash)
tree=C.ramp([(0,(0,0,0)),(0.32,(0.10,0.11,0.15)),(0.55,(0.40,0.34,0.30)),
             (0.72,(0.92,0.58,0.16)),(0.87,(1.0,0.85,0.44)),(1.0,(1.0,0.98,0.93))], tb)
# glow the main rivers so they bloom & survive downscale (read at thumbnail AND native)
gm=np.clip((tb-0.3)/0.7,0,1)
gl=C.bloom(gm,(1.2,3.5,10),(0.5,0.32,0.2))
tree=tree + gl[...,None]*np.array([1.0,0.72,0.32])*0.7

# ---- FROZEN: limit-shape rings = contours of (mildly smoothed) dist ----
ds=gaussian_filter(np.where(fin,dist,dmax),3.0)
lv=ds/dmax
K=17
g=(lv*K)%1.0; band=np.minimum(g,1-g)
ring=np.exp(-(band/0.028)**2)
ring*=np.clip(1.18-lv,0,1)        # fade outermost rings
cool=np.array([0.22,0.64,0.98])
rings=ring[...,None]*cool

# ---- compose: cool shape shows through the free tree's negative space ----
gap=np.clip(1.0-tb*1.4,0,1)
rgb=tree + 0.8*rings*gap[...,None]

# ---- origin focal bloom ----
core=np.zeros((W,W)); cc=W//2; core[cc-1:cc+2,cc-1:cc+2]=1.0
gl=C.bloom(core*8+ (tb>0.985)*tb, sigmas=(3,10,34), amps=(0.5,0.35,0.22))
rgb=rgb + gl[...,None]*np.array([1.0,0.85,0.55])

# tone
rgb=C.filmic(rgb,1.25)**(1/1.12)
im=C.to_img(rgb)
if OUT!=W: im=im.resize((OUT,OUT),Image.LANCZOS)
im.save(f"art_eygo/03_fpp.png")
print("saved art_eygo/03_fpp.png", im.size)
