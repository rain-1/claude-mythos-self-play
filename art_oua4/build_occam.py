import numpy as np, pickle, sys, time
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

# The Weight of the Simplest Explanation — the universal distribution m(x) over binary
# strings, measured from millions of small Turing machines (Coding Theorem Method).
# Each produced string is a tower at x = its binary fraction 0.s1s2..., height proportional
# to its weight (log frequency = -K(x)): the SIMPLEST strings tower over the random many.
pkl = sys.argv[1] if len(sys.argv)>1 else "tally_n5.pkl"   # comma-separated to merge
S   = int(sys.argv[2]) if len(sys.argv)>2 else 2048
SS  = int(sys.argv[3]) if len(sys.argv)>3 else 2
tag = sys.argv[4] if len(sys.argv)>4 else ""
from collections import Counter
dist=Counter(); meta=None
for p in pkl.split(","):
    d,m=pickle.load(open(p.strip(),"rb"))
    for s,c in d.items(): dist[s]+=c
    if meta is None: meta=dict(m)
    else:
        for k in ['N_sampled','N_halt','N_escape','N_loop','N_empty','N_toolong','B']: meta[k]+=m[k]
dist=dict(dist)
N=meta["N_halt"]
items=sorted(dist.items(), key=lambda kv:-kv[1])
print("distinct outputs:",len(items)," N_halt:",N," meta:",{k:meta[k] for k in ['n','K','B','T','N_sampled']})

def xfrac(s):
    v=0.0
    for i,ch in enumerate(s): v+=int(ch)*2.0**(-(i+1))
    return v
strs=[s for s,_ in items]
xs=np.array([xfrac(s) for s in strs])
Ls=np.array([len(s) for s in strs])
cs=np.array([c for _,c in items],float)
w =np.log(cs)               # weight ~ -K(x) (+const)
w-=w.min()-0.6              # keep all positive, small floor

W=S*SS
mL,mR,mT,mB=0.06,0.06,0.10,0.085
x0=mL*W; x1=(1-mR)*W
base=(1-mB)*W; top=mT*W
colbuf=np.zeros((W,W,3))
hmax=w.max()
# length -> colour (short=warm gold, mid=teal, long=cool violet)
def lcol(L):
    t=np.clip((L-1)/16.0,0,1)
    stops=[(0.0,np.array([255,205,110])),(0.4,np.array([90,200,180])),(0.75,np.array([70,130,235])),(1.0,np.array([150,90,230]))]
    for (a,c0),(b,c1) in zip(stops[:-1],stops[1:]):
        if t<=b:
            f=(t-a)/(b-a); return c0*(1-f)+c1*f
    return stops[-1][1]
order=np.argsort(cs)        # dim first so bright towers drawn on top
barw=max(1,int(0.6*SS))
t0=time.time()
for k in order:
    px=int(x0+xs[k]*(x1-x0))
    h=(w[k]/hmax)*(base-top)
    y_top=int(base-h)
    col=lcol(Ls[k])*(0.45+0.55*w[k]/hmax)
    xa=max(0,px-barw); xb=min(W,px+barw+1)
    colbuf[y_top:int(base),xa:xb]=np.maximum(colbuf[y_top:int(base),xa:xb],col)
    # bright peak-cap at the tower top (the simpler the brighter)
    cap=int(2.5*SS);
    colbuf[max(0,y_top-cap):y_top+cap, max(0,px-barw):min(W,px+barw+1)] = \
        np.maximum(colbuf[max(0,y_top-cap):y_top+cap, max(0,px-barw):min(W,px+barw+1)],
                   (col*0.4+np.array([255,250,235])*0.6)*(w[k]/hmax))
print("towers drawn in",round(time.time()-t0,1),"s")
# bloom + tone (two-scale glow)
glow1=gaussian_filter(colbuf,sigma=(1.4*SS,1.4*SS,0))
glow2=gaussian_filter(colbuf,sigma=(5.0*SS,5.0*SS,0))
img=colbuf*1.0 + glow1*0.8 + glow2*0.6
img=255*(1-np.exp(-img/150))
# faint baseline
bb=int(base)
img[bb:bb+max(1,SS),int(x0):int(x1)]=np.maximum(img[bb:bb+max(1,SS),int(x0):int(x1)],np.array([40,55,80]))
img=np.clip(img,0,255).astype(np.uint8)
im=Image.fromarray(img).resize((S,S),Image.LANCZOS)

# ---- labels on the tallest towers (drawn AFTER downscale, crisp) ----
d=ImageDraw.Draw(im)
try: font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",15)
except: font=ImageFont.load_default()
try: fonti=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",13)
except: fonti=font
sx=S/float(W)
labeled=[]
for k in np.argsort(-w)[:14]:
    px=x0*sx+xs[k]*(x1-x0)*sx
    h=(w[k]/hmax)*(base-top)*sx; y_top=base*sx-h
    if any(abs(px-lpx)<46 for lpx in labeled): continue
    labeled.append(px)
    s=strs[k]
    Kx=-np.log2(cs[k]/N)
    tw=d.textlength(s,font=font)
    yy=max(6, y_top-22)
    d.text((px-tw/2, yy), s, fill=(255,238,200), font=font)
    d.text((px-tw/2, yy+15), f"K≈{Kx:.1f}", fill=(120,150,180), font=fonti)
# title strip
d.text((int(x0*sx), int(0.028*S)), "THE WEIGHT OF THE SIMPLEST EXPLANATION", fill=(225,215,190), font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",19) if True else font)
d.text((int(x0*sx), int(0.058*S)), f"universal distribution m(x) over binary strings, from {meta['N_sampled']:,} random ({meta['n']},2) Turing machines  ·  height = log m(x) = -K(x)",
       fill=(120,140,165), font=fonti)
im.save(f"/home/user/claude-mythos-self-play/art_oua4/occam{tag}.png")
print("saved", f"occam{tag}.png")
