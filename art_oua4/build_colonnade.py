import numpy as np, pickle, sys, hashlib
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

# The hunted machines are CONFINED bouncers — tall tapering spires with the head's gold
# zigzag worldline. Present them as a colonnade of luminous specimens, not square tiles.
pkl=sys.argv[1] if len(sys.argv)>1 else "hunt_n5.pkl"
S  =int(sys.argv[2]) if len(sys.argv)>2 else 2048
NCOL=int(sys.argv[3]) if len(sys.argv)>3 else 30
tag=sys.argv[4] if len(sys.argv)>4 else ""
spec=pickle.load(open(pkl,"rb"))
# dedup by spacetime content hash
seen=set(); uniq=[]
for d in spec:
    h=hashlib.md5(d["st"].tobytes()).hexdigest()
    if h in seen: continue
    seen.add(h); uniq.append(d)
# diversity: spread across (width, comp) — sort by width then pick evenly, then ensure comp spread
uniq=sorted(uniq,key=lambda d:(d["width"],d["comp"]))
if len(uniq)>NCOL:
    ix=np.round(np.linspace(0,len(uniq)-1,NCOL)).astype(int); uniq=[uniq[i] for i in ix]
print(f"{len(uniq)} unique specimens; widths {min(d['width'] for d in uniq)}..{max(d['width'] for d in uniq)}")

top=int(0.072*S); botpad=int(0.02*S); side=int(0.012*S); gap=max(4,int(0.004*S))
Hav=S-top-botpad
N=len(uniq)
stripw=(S-2*side-(N-1)*gap)//N
bg=np.array([7,10,16],np.float32); img=np.zeros((S,S,3),np.float32); img[:]=bg
C0=np.array([9,15,24],np.float32); C1=np.array([46,165,162],np.float32); CH=np.array([255,206,112],np.float32)

x=side
for d in uniq:
    ST=d["st"]; HD=d["hd"]; H,Wd=ST.shape
    rgb=np.where(ST[...,None]>0,C1,C0).astype(np.float32)
    r=np.arange(H); v=(HD>=0)&(HD<Wd); rgb[r[v],HD[v]]=CH
    im=Image.fromarray(rgb.astype(np.uint8)).resize((stripw,Hav),Image.NEAREST)
    a=np.asarray(im,np.float32)
    img[top:top+Hav, x:x+stripw]=a
    x+=stripw+gap

struct=np.clip(img-bg,0,None); glow=gaussian_filter(struct,sigma=(1.0,1.0,0))
out=np.clip(img+glow*0.55,0,255).astype(np.uint8)
im=Image.fromarray(out); dd=ImageDraw.Draw(im)
fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(0.0185*S))
fi=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",int(0.0105*S))
dd.text((side,int(0.026*S)),"THE RARE ONES — CONFINED TURING MACHINES",fill=(228,218,196),font=fb)
dd.text((side,int(0.051*S)),
   f"{N} machines hunted from millions for CONFINEMENT — the head bounces in place (steps ≫ width), carving a "
   "tapering spire instead of a drift-triangle.  gold = the head's zigzag worldline",
   fill=(120,140,165),font=fi)
im.save(f"/home/user/claude-mythos-self-play/art_oua4/colonnade{tag}.png")
print("saved", f"colonnade{tag}.png")
