"""Render IDLA piece: warm occupation orb (frozen perfect disk) + electric
trembling log-correlated edge (the free frontier). Soft-haze register."""
import numpy as np, sys, pickle
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

# ---- FROZEN: occupation measure, HISTOGRAM-EQUALISED (huge dynamic range: 1..1.6M) ----
lg=np.log1p(visit.astype(np.float64))
veq=C.histeq(lg, mask=occ)                      # rank-transform reveals filamentary texture
veq=np.where(occ, veq, 0.0)
# sharpen the SRW-filament texture (unsharp mask on the equalised field)
tex = veq - gaussian_filter(veq,2.2)
v = np.clip(veq + 0.9*tex, 0, 1)
warm=C.ramp([(0,(0,0,0)),(0.22,(0.16,0.05,0.02)),(0.45,(0.55,0.24,0.06)),
             (0.68,(0.92,0.52,0.14)),(0.86,(1.0,0.78,0.32)),(1.0,(1.0,0.95,0.80))], v)
orb=warm*np.where(occ,1.0,0.0)[...,None]

# ---- FREE: trembling log-correlated frontier ----
bd = occ & ~binary_erosion(occ)                 # perimeter occupied cells
edge = gaussian_filter(bd.astype(float), 0.6)
glow = C.bloom(bd.astype(float),(1.2,4,12),(0.7,0.4,0.25))
cyan=np.array([0.30,0.85,1.0])
rim = edge[...,None]*cyan*1.4 + glow[...,None]*cyan*0.9

# ---- FREE trajectories: a FEW honest sample walks approaching the frozen set ----
# (fewer threads read better -- draw individual crisp polylines, not a splat scribble)
SS=2
trail_im=Image.new("RGB",(W*SS,W*SS),(0,0,0))
try:
    from PIL import ImageDraw
    with open("art_eygo/idla_trails.pkl","rb") as f: paths=pickle.load(f)
    rng2=np.random.default_rng(5)
    settled=[p for p in paths if len(p)>=10]
    pick=rng2.choice(len(settled), size=min(16,len(settled)), replace=False)
    dr=ImageDraw.Draw(trail_im,"RGB")
    for i in pick:
        p=settled[i]; L=len(p)
        seg=p[max(0,L-2200):]                      # near-boundary approach only
        pts=[((py-x0)*SS,(px-y0)*SS) for (px,py) in seg]  # image coords: col=x,row=y
        n=len(pts)
        for k in range(n-1):
            t=k/n
            col=tuple(int(c*255) for c in (0.10+0.75*t, 0.55+0.42*t, 0.65+0.35*t))
            dr.line([pts[k],pts[k+1]], fill=col, width=1)
except FileNotFoundError:
    pass
trail_im=trail_im.resize((W,W), Image.LANCZOS)
trail_arr=np.asarray(trail_im,dtype=float)/255.0
tg=C.bloom(trail_arr.max(-1),(0.9,2.5),(0.55,0.3))
trail_rgb=trail_arr*0.9 + tg[...,None]*np.array([0.35,0.85,1.0])*0.35

rgb = orb + rim + trail_rgb
rgb = C.filmic(rgb,1.3)**(1/1.1)
im=C.to_img(rgb)
# center in a square OUT canvas with black margin (negative space = 'not reached')
canvas=Image.new('RGB',(OUT,OUT),(0,0,0))
s=int(OUT*0.9); im2=im.resize((s,s),Image.LANCZOS)
canvas.paste(im2,((OUT-s)//2,(OUT-s)//2))
canvas.save("art_eygo/02_idla.png"); print("saved 02_idla.png W_native",W,"R",R)
