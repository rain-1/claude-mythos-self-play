"""ONE CURVE BENEATH EVERY LADDER — 2560^2.
The universal curve m(e) as a gold spine; 300 family members (a,e) as cyan
sparks, each sliding along its scaling thread onto the one curve. Insets:
the alternating-gauge triangle itself, and the exact facts.
python3 ladder_render.py [FINAL]
"""
import numpy as np, json, sys, math
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

FINAL = int(sys.argv[1]) if len(sys.argv)>1 else 900
SS = 2
S = FINAL*SS
rs = FINAL/2560.0

data = json.load(open('ladder_curve.json'))
curve = data['curve']          # (e, m, layer, err)
pts   = json.load(open('family_pts.json'))
estar = data['estar_refined']; hump = data['hump']

BAND = int(0.16*S)
x0, x1 = 0.07*S, 0.96*S
y0b, y1b = 0.055*S, S-BAND-0.03*S
LX0, LX1 = math.log(0.05), math.log(20.0)
WA = 0.018   # asinh scale
WMAX = math.asinh(80/WA*1.0)
def wy(m): return math.asinh(m/WA)
WLO, WHI = wy(-80), wy(0.09)*18   # asymmetric: reserve top space
WHI = wy(0.09) + 0.16*(wy(0.09)-WLO)
def to_px(e, m):
    fx = (math.log(e)-LX0)/(LX1-LX0)
    fy = (wy(m)-WLO)/(WHI-WLO)
    return x0+fx*(x1-x0), y1b-(y1b-y0b)*fy

ink  = np.zeros((S,S,3), np.float32)

def splat_poly(ptsxy, col, w, step=0.8):
    P = np.array(ptsxy, np.float32)
    dx, dy = np.diff(P[:,0]), np.diff(P[:,1])
    seglen = np.hypot(dx,dy); nsub = np.maximum(1,np.ceil(seglen/step).astype(int))
    idx = np.repeat(np.arange(len(dx)), nsub)
    cs = np.concatenate(([0],np.cumsum(nsub)))
    frac = (np.arange(int(nsub.sum())) - cs[idx])/nsub[idx]
    X = P[:-1,0][idx]+dx[idx]*frac; Y = P[:-1,1][idx]+dy[idx]*frac
    W = np.full(X.shape, w, np.float32)*(seglen[idx]/nsub[idx]+1e-9)
    xi=np.floor(X).astype(np.int64); yi=np.floor(Y).astype(np.int64)
    fx=(X-xi).astype(np.float32); fy=(Y-yi).astype(np.float32)
    c=np.asarray(col,np.float32)
    for ddx,ddy,ww in ((0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)):
        gx,gy=xi+ddx,yi+ddy
        m=(gx>=0)&(gx<S)&(gy>=0)&(gy<S)
        for ch in range(3):
            np.add.at(ink[...,ch], (gy[m],gx[m]), (W*ww)[m]*c[ch])

def star(px,py,rad,col,amp):
    r=int(max(2,rad*3.2)); yy,xx=np.ogrid[-r:r+1,-r:r+1]
    g=np.exp(-(xx*xx+yy*yy)/(2*rad*rad)).astype(np.float32)
    xa,ya=max(0,int(px)-r),max(0,int(py)-r); xb,yb=min(S,int(px)+r+1),min(S,int(py)+r+1)
    if xb<=xa or yb<=ya: return
    sub=g[ya-(int(py)-r):yb-(int(py)-r), xa-(int(px)-r):xb-(int(px)-r)]
    ink[ya:yb,xa:xb,:] += amp*sub[...,None]*np.asarray(col,np.float32)[None,None,:]

# --- zero axis + guide verticals ---
zx = [to_px(math.exp(LX0+t*(LX1-LX0)), 0.0) for t in np.linspace(0,1,200)]
splat_poly(zx, (0.25,0.30,0.42), 0.7*SS*rs)

# --- scaling threads: raw member -> landing on the curve ---
for ip, p in enumerate(pts):
    if ip % 2: continue
    if not (0.05 < p['e'] < 20): continue
    if p['M'] < -75 or p['Mu'] < -75: continue
    P0 = to_px(p['e'], p['M'])
    P1 = to_px(p['eu'], p['Mu'])
    mid = (0.5*(P0[0]+P1[0]), 0.5*(P0[1]+P1[1]) - 0.028*S*np.sign(P0[0]-P1[0]+1e-9))
    ts = np.linspace(0,1,60)
    bez = np.array([( (1-t)**2*P0[0]+2*(1-t)*t*mid[0]+t*t*P1[0],
             (1-t)**2*P0[1]+2*(1-t)*t*mid[1]+t*t*P1[1]) for t in ts])
    # gradient: cyan raw half, gold landing half
    splat_poly(bez[:31], (0.30,0.62,0.85), 0.34*SS*rs)
    splat_poly(bez[30:], (0.75,0.68,0.45), 0.34*SS*rs)
    star(P0[0],P0[1],1.5*SS*rs,(0.55,0.85,1.0),0.6)
    star(P1[0],P1[1],1.0*SS*rs,(1.0,0.8,0.35),0.4)

# --- the universal curve: gold spine (drawn last, on top) ---
cpts = [to_px(e, max(-80,min(0.09,m))) for e,m,_,_ in curve if 0.05<=e<=20]
splat_poly(cpts, (1.0,0.72,0.24), 3.8*SS*rs, step=0.5)
splat_poly(cpts, (1.0,0.9,0.6), 1.5*SS*rs, step=0.5)

# tangent of slope -1/2 at e=1 (in data coords: m = -(e-1)/2), dashed
for t0 in np.linspace(-0.6,0.6,21):
    e_a, e_b = math.exp(t0-0.016), math.exp(t0+0.016)
    seg = [to_px(e_a, -(e_a-1)/2), to_px(e_b, -(e_b-1)/2)]
    if abs(-(e_a-1)/2) < 75: splat_poly(seg, (1.0,0.42,0.5), 1.6*SS*rs)

# special points
for (ee, mm, col, rad, amp) in [
    (estar, 0.0, (1.0,1.0,1.0), 4.4, 1.8),
    (1.0, 0.0, (1.0,0.85,0.45), 4.4, 1.7),
    (hump[0], hump[1], (1.0,0.65,0.85), 3.0, 1.3),
    (1/math.sqrt(2), 0.0654503310928441/math.sqrt(2), (0.55,1.0,0.75), 3.6, 1.5)]:
    px,py = to_px(ee,mm); star(px,py,rad*SS*rs,col,amp)

# --- inset: the alternating ladder itself (gauge deviation of a=1/2, e=1/sqrt2) ---
NI=72
e0=1/math.sqrt(2)
A=np.array([e0]); tri=np.full((NI,NI),np.nan,np.float32)
for n in range(1,NI):
    inter = 0.5/A[:-1]+0.5/A[1:]
    A=np.concatenate(([e0],inter,[e0])) if n>=2 else np.array([e0,e0])
    d=((-1)**n)*(A-1.0)
    tri[n,:n+1]=d
iw=ih=int(0.30*S); ix,iy=int(0.652*S),int(0.045*S)
img_t=np.zeros((NI,NI,3),np.float32)
mag=np.log10(np.abs(tri)+1e-16); mag=np.clip((mag+9.5)/9.5,0,1)**1.4
pos=tri>0
img_t[...,0]=np.where(pos,1.0,0.22)*mag
img_t[...,1]=np.where(pos,0.72,0.52)*mag
img_t[...,2]=np.where(pos,0.22,0.88)*mag
img_t=np.nan_to_num(img_t)
from scipy.ndimage import zoom as _zoom
sc=ih/NI
big=np.clip(_zoom(img_t,(sc,sc,1),order=0),0,1)
bh,bw=big.shape[:2]
ink[iy:iy+bh, ix:ix+bw,:]=ink[iy:iy+bh, ix:ix+bw,:]*0.06+big*1.15

# --- tone map ---
img = 1.0-np.exp(-ink*1.0)
img = np.clip(img,0,1)**(1/1.3)
img8=(img*255+np.random.uniform(-0.5,0.5,img.shape)).clip(0,255).astype(np.uint8)
out=Image.fromarray(img8).resize((FINAL,FINAL),Image.LANCZOS)

d2=ImageDraw.Draw(out)
def font(sz,bold=False):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if bold else ''),sz)
    except Exception: return ImageFont.load_default()
bandy=FINAL-BAND//SS
d2.rectangle([0,bandy,FINAL,FINAL],fill=(6,7,10))
fs=max(9,int(31*rs))
d2.text((int(0.05*FINAL),bandy+int(0.012*FINAL)),'ONE CURVE BENEATH EVERY LADDER',font=font(int(64*rs),True),fill=(255,214,120))
caps=[
 'The reciprocal-Pascal family  A(n,k) = a/A(n−1,k−1) + a/A(n−1,k), edges e — for every (a,e) the deviation from the fixed point √(2a)',
 'obeys (−1)^n·2^(−n)·C(n,k) times one constant M̄(a,e).  THEOREM (scaling, one line): M̄(a,e) = √(2a)·m(e/√(2a)) — one universal curve',
 'm beneath the whole two-parameter family; certified here on 300 members, max residual 3.0e−11 (cyan sparks slide home on their threads).',
 'THEOREM: m(1)=0 and m′(1) = −1/2 exactly (the derivative triangle’s parity-averaged mass is −1/2 at every depth: row sums alternate 1, −2).',
 'The curve crosses zero again at e* = 0.6119453567… (a new constant?), peaks at (0.788, +0.0569), and dives ≈ −e^(1.2±0.1) as e→∞.',
 'Green star: the mother triangle (a=1, e=1), M̄ = 0.06545033…, reproduced and reduced.  Rose dashes: the −1/2 law.  Inset: the ladder itself,',
 'gauge deviation (−1)^n(A−1) for e=1/√2 — gold above the fixed point, blue below, the boundary tower contracting at ratio −1/3.   MO 514552 family.']
ytxt=bandy+int(0.038*FINAL)
for c in caps:
    d2.text((int(0.05*FINAL),ytxt),c,font=font(fs),fill=(158,168,190)); ytxt+=int(fs*1.42)
# axis labels
d2.text((int(0.07*FINAL),int(0.012*FINAL)),'m(e)  (asinh scale)',font=font(fs),fill=(120,150,190))
for ee,lab in [(0.1,'e = 0.1'),(0.6119453567467,'e*'),(1.0,'1'),(10.0,'10')]:
    px,_=to_px(ee,0.0); d2.text((px/SS-10*rs,bandy-int(0.03*FINAL)),lab,font=font(fs),fill=(120,150,190))
out.save('ladder_%d.png'%FINAL)
print('saved ladder_%d.png'%FINAL)
