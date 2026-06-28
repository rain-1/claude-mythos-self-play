import numpy as np, pickle, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

# Render the hunted (confined, non-triangular) small-TM space-times.
pkl  = sys.argv[1] if len(sys.argv)>1 else "hunt_n5.pkl"
S    = int(sys.argv[2]) if len(sys.argv)>2 else 2048
GRID = int(sys.argv[3]) if len(sys.argv)>3 else 7
sortk= sys.argv[4] if len(sys.argv)>4 else "confine"   # confine | comp | dirchg
tag  = sys.argv[5] if len(sys.argv)>5 else ""
spec=pickle.load(open(pkl,"rb"))
spec=sorted(spec,key=lambda d:-d.get(sortk,0))
NT=GRID*GRID
spec=spec[:NT]
spec=sorted(spec,key=lambda d:d.get("confine",0))   # arrange low->high confinement L->R
print(f"rendering {len(spec)} by {sortk}; confine {spec[0]['confine']}..{spec[-1]['confine']} comp {min(s['comp'] for s in spec)}..{max(s['comp'] for s in spec)}")

margin=int(0.022*S); top=int(0.075*S); botpad=int(0.018*S); gut=max(2,int(0.004*S))
cellw=(S-2*margin-(GRID-1)*gut)//GRID
cellh=(S-top-botpad-(GRID-1)*gut)//GRID
bg=np.array([7,10,17],np.float32); img=np.zeros((S,S,3),np.float32); img[:]=bg
C0=np.array([10,16,26],np.float32); C1=np.array([40,150,150],np.float32); CH=np.array([255,205,110],np.float32)

def tile(d):
    ST=d["st"]; HD=d["hd"]; H,Wd=ST.shape
    rgb=np.where(ST[...,None]>0,C1,C0).astype(np.float32)
    rows=np.arange(H); valid=(HD>=0)&(HD<Wd)
    rgb[rows[valid],HD[valid]]=CH
    return rgb

t=0
for gy in range(GRID):
    for gx in range(GRID):
        if t>=len(spec): break
        d=spec[t]; t+=1; rgb=tile(d); H,Wd=rgb.shape[:2]
        sc=min(cellw/Wd, cellh/H); nw=max(1,int(Wd*sc)); nh=max(1,int(H*sc))
        im=Image.fromarray(rgb.astype(np.uint8)).resize((nw,nh),Image.NEAREST)
        a=np.asarray(im,np.float32)
        cy=top+gy*(cellh+gut); cx=margin+gx*(cellw+gut)
        oy=cy+(cellh-nh)//2; ox=cx+(cellw-nw)//2
        h2=min(nh,S-oy); w2=min(nw,S-ox); img[oy:oy+h2,ox:ox+w2]=a[:h2,:w2]

struct=np.clip(img-bg,0,None); glow=gaussian_filter(struct,sigma=(1.0,1.0,0))
out=np.clip(img+glow*0.6,0,255).astype(np.uint8)
im=Image.fromarray(out); d=ImageDraw.Draw(im)
fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(0.0185*S))
fi=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",int(0.012*S))
d.text((margin,int(0.030*S)),"THE BUSY BEAVER GARDEN — THE RARE ONES",fill=(228,218,196),font=fb)
d.text((margin,int(0.058*S)),
   f"{len(spec)} small (5-state, 2-symbol) Turing machines selected for CONFINEMENT (head revisits each column many times) "
   "— the bouncers that build structure, not the typical drift-cone.  teal=tape, gold=head worldline",
   fill=(120,140,165),font=fi)
im.save(f"/home/user/claude-mythos-self-play/art_oua4/hunt{tag}.png")
print("saved", f"hunt{tag}.png")
