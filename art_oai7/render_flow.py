import numpy as np, sys
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from billiard import triangle
from flow import flow
from caption import caption, CORAL, INK, SOFT
S=int(sys.argv[1]); out=sys.argv[2]; n=int(sys.argv[3]); times=[float(x) for x in sys.argv[4].split(',')]
al=np.pi*(np.sqrt(2)-1)/2; be=np.pi/3
V=triangle(al,be); V=V-V.mean(0)
rng=np.random.default_rng(1)
r=np.sqrt(rng.random(n))*0.012; th=rng.random(n)*2*np.pi
P0=np.stack([r*np.cos(th),r*np.sin(th)],1)+np.array([-0.08,-0.02])
u=rng.random(n); ang=0.62+(u-0.5)*0.05
D0=np.stack([np.cos(ang),np.sin(ang)],1)
WHEEL=np.array([[0.98,0.55,0.62],[1.0,0.70,0.52],[1.0,0.86,0.48],[0.74,0.90,0.52],[0.52,0.86,0.74],[0.52,0.76,0.98],[0.66,0.64,1.0],[0.84,0.60,0.98]])
def wheel(h):
    h=np.clip(h,0,0.999)*(len(WHEEL)-1); i=h.astype(int); f=(h-i)[:,None]; return WHEEL[i]*(1-f)+WHEEL[i+1]*f
col=wheel(u)
H=int(S*0.98); img=np.ones((H,S,3))*np.array([0.994,0.990,0.984])
cols,rows=3,2; pw=S/cols; ph=pw*0.80; top=S*0.06
ext=np.ptp(V[:,0]); sc=pw*0.86/ext
for k,T in enumerate(times):
    Q=P0 if T==0 else flow(V,P0,D0,T)
    cx=(k%cols+0.5)*pw; cy=top+(k//cols+0.5)*ph+ph*0.05
    X=(cx+Q[:,0]*sc).astype(int); Y=(cy-Q[:,1]*sc).astype(int)
    ok=(X>=1)&(X<S-1)&(Y>=1)&(Y<H-1)
    order=rng.permutation(np.nonzero(ok)[0])
    rad=max(1,S//1100)
    for dy in range(-rad,rad+1):
        for dx in range(-rad,rad+1):
            if dx*dx+dy*dy>rad*rad+1: continue
            img[Y[order]+dy,X[order]+dx]=0.994*(1-0.92)+col[order]*0.92
    im=None
    # outline
    pts=[(cx+v[0]*sc,cy-v[1]*sc) for v in V]
    o=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(o)
    d.polygon(pts,outline=(150,132,162),width=max(1,S//900))
    from caption import F
    from PIL import ImageFont
    f=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(S*0.016))
    lab='t = 0' if T==0 else f't = {T:g}'
    tw=d.textlength(lab,font=f); d.text((cx-tw/2,cy+ph*0.25),lab,font=f,fill=SOFT)
    img=np.asarray(o).astype(float)/255
o=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8))
caption(o,S/2,top+2*ph+S*0.035,'A Drop in an Irrational Room',
  f'{n:,} billiard balls leave one tiny spot, nearly together; the triangle has angles (√2−1)π/2, π/3 and the rest',
  'coloured by starting direction  ·  openai/math family 150 claims every triangle with an irrational angle is weakly mixing',
  S*0.032,align='center',line3='polygon billiards have no chaos to spread a drop; only the corners split it, slowly, and still it reaches everywhere')
o=o.crop((0,int(S*0.075),S,int(S*0.81))); o.save(out)
