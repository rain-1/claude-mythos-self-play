"""openai/math family 076 claims ±1 polynomials can be ULTRAFLAT: |P(z)|/sqrt(N) -> 1 uniformly on |z|=1, for all large N.
Four ±1 strings of length ~128, each drawn as a ring of beads around its modulus halo."""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from flat import modulus, rudin_shapiro, legendre
from caption import caption, CORAL, SOFT, F
S=int(sys.argv[1]); out=sys.argv[2]
seqs=[('a random string',np.where(np.random.default_rng(4).random(128)<0.5,-1,1)),
      ('Rudin–Shapiro',rudin_shapiro(7)),
      ('Legendre, rotated a quarter',legendre(127,32)),
      ('annealed for flatness',np.load('proto/flat_best.npy'))]
SS=2; W=S*SS; H=int(W*1.18); pw=W/2; top=W*0.02
img=Image.new('RGB',(W,H),(252,251,249))
WARM=[(250,150,160),(255,180,140),(253,210,120)]; COOL=[(140,200,240),(150,165,240),(190,160,240)]
fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(W*0.017))
def mix(P,h):
    h=h*(len(P)-1); i=min(int(h),len(P)-2); f=h-i; return tuple(int(P[i][k]*(1-f)+P[i+1][k]*f) for k in range(3))
for k,(name,e) in enumerate(seqs):
    e=np.asarray(e); N=len(e); m=modulus(e,4096)
    cx=(k%2+0.5)*pw; cy=top+(k//2+0.5)*pw*0.98
    r0=pw*0.165; th=2*np.pi*np.arange(4096)/4096
    # halo: polygon of r = r0*m; fill bulges warm, dents cool, via polar raster
    yy,xx=np.mgrid[0:int(pw),0:int(pw)]; dx=xx-pw/2; dy=yy-pw/2
    rr=np.hypot(dx,dy); ang=(np.arctan2(-dy,dx))%(2*np.pi); mi=m[(ang/(2*np.pi)*4096).astype(int)%4096]*r0
    bulge=(rr>r0)&(rr<mi); dent=(rr<r0)&(rr>mi)
    lay=np.zeros((int(pw),int(pw),4))
    t=np.clip((mi-r0)/(r0*1.4),0,1)
    lay[bulge,:3]=np.array([1.0,0.62,0.62])*(1-t[bulge,None])+np.array([1.0,0.80,0.60])*t[bulge,None]; lay[bulge,3]=0.85
    lay[dent,:3]=np.array([0.62,0.78,1.0]); lay[dent,3]=0.85
    inner=(rr<np.minimum(r0,mi)); lay[inner,:3]=np.array([0.97,0.96,0.99]); lay[inner,3]=1
    L=Image.fromarray((lay*255).astype(np.uint8),'RGBA').filter(ImageFilter.GaussianBlur(0.8))
    img.paste(L,(int(cx-pw/2),int(cy-pw/2)),L)
    d=ImageDraw.Draw(img)
    # halo outline + unit circle
    pts=[(cx+r0*m[i]*np.cos(th[i]),cy-r0*m[i]*np.sin(th[i])) for i in range(0,4096,2)]
    pass
    d.ellipse([cx-r0,cy-r0,cx+r0,cy+r0],outline=(205,190,210),width=max(1,W//2000))
    # beads
    R=pw*0.43; br=min(pw*0.0105,np.pi*R/N*0.85)
    sh=Image.new('L',(W,H),0); sd=ImageDraw.Draw(sh)
    pos=[(cx+R*np.cos(np.pi/2-2*np.pi*i/N),cy-R*np.sin(np.pi/2-2*np.pi*i/N)) for i in range(N)]
    for (x,y) in pos: sd.ellipse([x-br+br*0.2,y-br+br*0.3,x+br+br*0.2,y+br+br*0.3],fill=110)
    sh=sh.filter(ImageFilter.GaussianBlur(br*0.5)); a=np.asarray(img).astype(float)*(1-0.25*np.asarray(sh)[...,None]/255*np.array([0.9,0.9,0.5]))
    img=Image.fromarray(a.astype(np.uint8)); d=ImageDraw.Draw(img)
    for i,(x,y) in enumerate(pos):
        c=mix(WARM,i/N) if e[i]>0 else mix(COOL,i/N)
        d.ellipse([x-br,y-br,x+br,y+br],fill=tuple(int(v*0.92) for v in c)); d.ellipse([x-br*0.9,y-br*0.92,x+br*0.86,y+br*0.84],fill=c)
        d.ellipse([x-br*0.55,y-br*0.6,x-br*0.15,y-br*0.2],fill=tuple(int(255-(255-v)*0.35) for v in c))
    lab=f'{name}  ·  N = {N}  ·  |P|/√N from {m.min():.2f} to {m.max():.2f}'
    tw=d.textlength(lab,font=fs); d.text((cx-tw/2,cy+pw*0.465),lab,font=fs,fill=SOFT)
caption(img,W/2,top+2*pw*0.98+W*0.025,'Toward a Perfect Circle',
  'four strings of ±1 drawn as rings of beads (warm +1, cool −1); inside each, the modulus |P(z)|/√N around the unit circle',
  'warm where the halo bulges past the faint unit ring, cool where it dents inside  ·  a perfectly flat polynomial would leave no colour at all',
  W*0.040,align='center',line3='openai/math family 076 claims ±1 polynomials whose halo is as round as you like, for every large enough N; at sizes we can draw, none is')
img.resize((S,int(H/SS)),Image.LANCZOS).save(out)
