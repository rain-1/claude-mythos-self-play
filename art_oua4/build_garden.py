import numpy as np, pickle, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

# The Busy Beaver Garden — a specimen case of small-Turing-machine space-times, sorted
# from the instantly-quiet to the long-running champions. Most tiny programs do almost
# nothing; a rare few compute astonishing structure before halting (and which ones is
# uncomputable — the Busy Beaver function grows faster than anything you can name).
pkl = sys.argv[1] if len(sys.argv)>1 else "garden_n5.pkl"
S   = int(sys.argv[2]) if len(sys.argv)>2 else 2048
GRID= int(sys.argv[3]) if len(sys.argv)>3 else 8
tag = sys.argv[4] if len(sys.argv)>4 else ""
spec=pickle.load(open(pkl,"rb"))
key="comp" if "comp" in spec[0] else "steps"
spec=sorted(spec,key=lambda d:d[key])
spec=spec[int(0.18*len(spec)):]   # drop the near-empty simplest tiles
NT=GRID*GRID
# even spread across the sorted list
if len(spec)>NT:
    idx=np.round(np.linspace(0,len(spec)-1,NT)).astype(int)
    spec=[spec[i] for i in idx]
print("rendering",len(spec),"specimens; runtime range",spec[0]["steps"],"->",spec[-1]["steps"])

margin=int(0.022*S); top=int(0.075*S); botpad=int(0.018*S)
gut=max(2,int(0.004*S))
cellw=(S-2*margin-(GRID-1)*gut)//GRID
cellh=(S-top-botpad-(GRID-1)*gut)//GRID
img=np.zeros((S,S,3),np.float32)
bg=np.array([7,10,17],np.float32)
img[:]=bg

C0=np.array([10,16,26],np.float32)    # tape 0
C1=np.array([40,150,150],np.float32)  # tape 1 (teal)
CH=np.array([255,205,110],np.float32) # head worldline (gold)

def tile(d):
    ST=d["st"]; HD=d["hd"]; H,Wd=ST.shape
    # base colours
    rgb=np.where(ST[...,None]>0, C1, C0).astype(np.float32)
    # head worldline
    rows=np.arange(H)
    valid=(HD>=0)&(HD<Wd)
    rgb[rows[valid],HD[valid]]=CH
    return rgb

t=0
for gy in range(GRID):
    for gx in range(GRID):
        if t>=len(spec): break
        d=spec[t]; t+=1
        rgb=tile(d); H,Wd=rgb.shape[:2]
        # fit into cell preserving aspect
        sc=min(cellw/Wd, cellh/H)
        nw=max(1,int(Wd*sc)); nh=max(1,int(H*sc))
        im=Image.fromarray(rgb.astype(np.uint8)).resize((nw,nh),Image.NEAREST)
        a=np.asarray(im,np.float32)
        cy=top+gy*(cellh+gut); cx=margin+gx*(cellw+gut)
        oy=cy+(cellh-nh)//2; ox=cx+(cellw-nw)//2
        h2=min(nh, S-oy); w2=min(nw, S-ox)
        img[oy:oy+h2, ox:ox+w2]=a[:h2,:w2]

# subtle bloom on the bright (teal+gold) structure
struct=np.clip((img-bg),0,None)
glow=gaussian_filter(struct,sigma=(1.1,1.1,0))
out=img+glow*0.6
out=np.clip(out,0,255).astype(np.uint8)
im=Image.fromarray(out)
d=ImageDraw.Draw(im)
fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(0.0185*S))
fi=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",int(0.012*S))
d.text((margin,int(0.030*S)),"THE BUSY BEAVER GARDEN",fill=(228,218,196),font=fb)
d.text((margin,int(0.058*S)),
       f"space-times of {len(spec)} small (5-state, 2-symbol) Turing machines, sorted by space-time complexity  ·  "
       f"300 steps  ·  teal = tape, gold = the head's worldline",
       fill=(120,140,165),font=fi)
im.save(f"/home/user/claude-mythos-self-play/art_oua4/garden{tag}.png")
print("saved", f"garden{tag}.png")
