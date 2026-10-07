import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, shift as nshift, zoom, distance_transform_edt
from hotspots import domain, neumann_mode
from caption import caption, CORAL, SOFT, F
S=int(sys.argv[1]); out=sys.argv[2]; N=int(sys.argv[3])
kinds=['bean','peanut','star','pear','blob','comma']
names={'bean':'bean','peanut':'peanut','star':'lopsided star','pear':'pear','blob':'blob','comma':'comma'}
PAPER=np.array([0.994,0.990,0.984])
WARM=np.array([[1.0,0.93,0.86],[1.0,0.84,0.72],[1.0,0.74,0.62],[0.99,0.64,0.62],[0.98,0.56,0.64]])
COOL=np.array([[0.90,0.94,1.0],[0.76,0.88,1.0],[0.66,0.80,1.0],[0.68,0.70,1.0],[0.76,0.64,0.98]])
def ramp(P,h):
    h=np.clip(h,0,1)*(len(P)-1); i=np.minimum(h.astype(int),len(P)-2); f=(h-i)[...,None]; return P[i]*(1-f)+P[i+1]*f
cols,rows=3,2; pw=S/cols; H=int(S*0.775)
img=np.ones((H,S,3))*PAPER
K=7  # bands each side
fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(S*0.0135))
labs=[]; beads=[]
for k,kind in enumerate(kinds):
    m,x,y=domain(kind,N); U,lam,lam2=neumann_mode(m)
    U=U/np.nanmax(np.abs(U))
    P=int(pw*0.92); f=P/N
    _,(J,I)=distance_transform_edt(~m,return_indices=True); Uf=U.copy(); Uf[~m]=U[J[~m],I[~m]]
    Uz=zoom(Uf,P/N,order=3)[:P,:P]
    m2,_,_=domain(kind,2*P); Mz=m2.reshape(P,2,P,2).mean((1,3))
    # smooth extension so bands reach the rim cleanly
    lev=np.sign(Uz)*np.ceil(np.abs(Uz)*K)/K  # signed band index/K
    hgt=np.abs(lev)*K*Mz
    colr=np.where((lev>0)[...,None],ramp(WARM,np.abs(lev)),ramp(COOL,np.abs(lev)))
    s=P/500
    up=nshift(hgt,(2.2*s,1.6*s),order=1,mode='nearest'); dsh=np.clip(up-hgt,0,None); dsh=2*(1-np.exp(-dsh/2))
    shadow=gaussian_filter(dsh,1.5*s)
    tl=nshift(hgt,(0.9*s,0.9*s),order=1,mode='nearest'); lit=1-np.exp(-np.clip(hgt-tl,0,None))
    colr=colr*(1-0.22*(1-np.exp(-shadow))[...,None]*np.array([0.9,0.9,0.55]))
    colr=colr+(1-colr)*0.5*lit[...,None]
    a=np.clip(Mz,0,1)[...,None]
    ox=int((k%cols)*pw+(pw-P)/2); oy=int(S*0.02+(k//cols)*pw*0.9+(pw*0.9-P)/2)
    # soft drop shadow of the whole domain
    ds=gaussian_filter(nshift(Mz,(4*s,3*s),order=1),4*s)
    reg=img[oy:oy+P,ox:ox+P]
    reg*=1-0.16*ds[...,None]*np.array([0.9,0.9,0.5])
    img[oy:oy+P,ox:ox+P]=reg*(1-a)+colr*a
    jm=np.nanargmax(U); jn=np.nanargmin(U)
    for j in (jm,jn):
        yy,xx=np.unravel_index(j,U.shape); beads.append((ox+xx*f,oy+yy*f))
    labs.append((ox+P/2,oy+P*1.0,f'{names[kind]}  ·  λ₂/λ₁ = {lam2/lam:.2f}'))
o=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(o)
r=S*0.0055
for (bx,by) in beads: d.ellipse([bx-r,by-r,bx+r,by+r],fill=CORAL,outline=(255,255,255),width=max(1,S//900))
for (lx,ly,t) in labs:
    tw=d.textlength(t,font=fs); d.text((lx-tw/2,ly-fs.size*0.2),t,font=fs,fill=SOFT)
caption(o,S/2,S*0.02+2*pw*0.9+S*0.03,'The Heat Leaves by the Edge',
  'the first nonzero Neumann eigenfunction on six smooth simply connected shapes: warm hills, cool valleys, seven paper terraces each way',
  'coral: the hottest and coldest points; every one sits on the rim  ·  finite differences, graph Laplacian on a fine grid',
  S*0.032,align='center',line3='openai/math family 369 claims a strict hot spots theorem: on every smooth bounded simply connected planar domain, no interior critical point')
o.save(out)
