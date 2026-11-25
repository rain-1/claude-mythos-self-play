"""FOUR WAYS TO FILL THE SAME LAND — sun print.  Each village exposes the paper over its disc of earshot, in proportion to
its people; the blue at a point is the dose phi*u there, so the mean blue of a panel IS its population density.
usage: sunprint.py W out.png"""
import sys, numpy as np, scipy.fft as sf
sys.path.insert(0,'math_earshot')
from scipy.ndimage import gaussian_filter, label, zoom, center_of_mass, sum as ndsum
from scipy.special import j1
from PIL import Image, ImageDraw, ImageFont
W=int(sys.argv[1]); OUT=sys.argv[2]; S=W/2048.0
def noise(shape,sig,seed):
    r=np.random.default_rng(seed).standard_normal(shape); r=gaussian_filter(r,sig,mode='wrap'); return r/r.std()
P=int(760*S); VIEW=8.0; ppu=P/VIEW
yy,xx=np.mgrid[0:P,0:P]; gx=(xx+.5)/ppu; gy=(yy+.5)/ppu
def discs(pts,m,L):
    """dose of point villages (open discs of radius 1, weight m/pi), periodic in L, sampled on the VIEW window"""
    d=np.zeros((P,P))
    for (x,y),mm in zip(pts,m):
        for ox in (-L,0,L):
            for oy in (-L,0,L):
                r=np.hypot(gx-x-ox,gy-y-oy)
                if r.min()<1.02: d+=mm/np.pi*np.clip((1-r)*ppu+0.5,0,1)
    return d
def villages(u,dx,thr=0.03):
    lab,n=label(u>thr*u.max()); idx=np.arange(1,n+1)
    m=ndsum(u,lab,idx)*dx*dx; c=np.array(center_of_mass(u,lab,idx)); return (c+0.5)*dx,m
panels=[]
# A: everyone everywhere
panels.append(dict(dose=np.ones((P,P)),pts=np.zeros((0,2)),m=[],dens=1.0,name='spread evenly',note='the least a full land can hold'))
# B: what the settlers leave (PDE, R^2/D = 100000)
d=np.load('data/sim_c100000.npz'); u=d['snaps'][-1].astype(float); L=float(d['L']); N=u.shape[0]; dx=L/N
k=2*np.pi*sf.fftfreq(N,dx); kx,ky=np.meshgrid(k,k,indexing='ij'); kk=np.hypot(kx,ky)
ph=np.where(kk>0,2*j1(kk)/np.where(kk>0,kk,1),1.0); c=sf.ifft2(sf.fft2(u)*ph).real
pts,m=villages(u,dx); dB=discs(pts,m,L)
panels.append(dict(dose=dB,pts=pts,m=m,dens=u.mean(),name='what slow wanderers settle into',note=f'R²/D = 100000, from a random scatter'))
print('B: dose at villages (field)',c[u>0.5*u.max()].mean(),'min dose',c.min(),'n',len(m))
# C: no wandering at all (D = 0), random start
from zero_diffusion import run
u=run(8.0,256,1,ret=True); dx=8.0/256; pts,m=villages(u,dx,1e-3)
panels.append(dict(dose=discs(pts,m,8.0),pts=pts,m=m,dens=u.mean(),name='no wandering at all: hamlets in constellations',note='D = 0, from a random scatter'))
print('C: n villages',len(m),'density',u.mean())
# D: the flower: hexagonal villages just out of earshot
a=1.0; pts=[]
for i in range(-12,24):
    for j in range(-4,14):
        x=(i+0.5*j)*a+0.31; y=j*a*np.sqrt(3)/2+0.27
        if -1.2<x<VIEW+1.2 and -1.2<y<VIEW+1.2: pts.append((x,y))
pts=np.array(pts); m=np.full(len(pts),np.pi)
dD=np.zeros((P,P))
for (x,y) in pts: dD+=np.clip((1-np.hypot(gx-x,gy-y))*ppu+0.5,0,1)        # open discs: a village is outside its neighbours' rings
panels.append(dict(dose=dD,pts=pts,m=m,dens=2*np.pi/np.sqrt(3),name='every village just out of earshot',note='2\u03C0/\u221A3: the fullest land found in any trial'))
print('D: mean dose in window',dD.mean())

# ---------- the sheet ----------
paper=np.array([0.957,0.937,0.878]); img=np.ones((W,W,3))*paper
img*= (1+0.016*noise((W,W),0.9*S,1)[...,None]+0.012*noise((W,W),50*S,2)[...,None])
blue_lo=np.array([0.36,0.56,0.74]); blue_hi=np.array([0.035,0.115,0.29])
MX=int(204*S); GAP=int(120*S); MY=int(90*S); RG=int(140*S)
YY,XX=np.mgrid[0:W,0:W]
for n,p in enumerate(panels):
    ox=MX+(n%2)*(P+GAP); oy=MY+(n//2)*(P+RG)
    pad=int(34*S); sl=(slice(oy-pad,oy+P+pad),slice(ox-pad,ox+P+pad)); Q=P+2*pad
    dose=np.pad(p['dose'],pad,mode='edge')
    # brushed coat: ragged left/right ends, streaks along the stroke
    y2,x2=np.mgrid[0:Q,0:Q]
    rag=noise((Q,),6*S,10+n)*9*S+noise((Q,),1.5*S,20+n)*5*S; rag2=noise((Q,),6*S,30+n)*9*S+noise((Q,),1.5*S,40+n)*5*S
    coat=np.clip((x2-pad*0.45-rag[:,None])/(3*S),0,1)*np.clip((Q-pad*0.45-rag2[:,None]-x2)/(3*S),0,1)
    tb=noise((Q,),30*S,50+n)*3*S
    coat*=np.clip((y2-pad*0.55-tb[None,:])/(2.5*S),0,1)*np.clip((Q-pad*0.55-tb[None,:]-y2)/(2.5*S),0,1)
    streak=1+0.05*gaussian_filter(np.random.default_rng(60+n).standard_normal((Q,Q)),(1.2*S,60*S))/0.02*0.02
    streak=1+0.9*gaussian_filter(np.random.default_rng(60+n).standard_normal((Q,Q)),(1.5*S,70*S))
    b=1-np.exp(-0.50*dose*np.clip(streak,0.8,1.2))
    # pins: unexposed paper where a village stands
    pin=np.zeros((Q,Q))
    for (x,y),mm in zip(p['pts'],p['m']):
        px=x*ppu+pad; py=y*ppu+pad
        if -20<px<Q+20 and -20<py<Q+20:
            r=np.hypot(x2+.5-px,y2+.5-py); rad=(2.2+3.4*np.sqrt(mm/np.pi))*S
            pin=np.maximum(pin,np.clip((rad-r)/(1.6*S)+0.5,0,1))
    b=gaussian_filter(b,0.7*S)*(1-0.93*pin)
    col=blue_lo[None,None,:]*(1-b[...,None])+blue_hi[None,None,:]*b[...,None]
    t=np.clip(b*1.9,0,1)[...,None]; col=paper*(1-t)+col*t
    col*= (1+0.03*noise((Q,Q),0.8*S,70+n)[...,None])
    a=coat[...,None]; img[sl]=img[sl]*(1-a)+col*a
    p['box']=(ox,oy)
im=Image.fromarray((np.clip(img,0,1)*255+.5).astype(np.uint8)); dr=ImageDraw.Draw(im)
F=lambda nm,sz: ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{nm}.ttf',int(sz*S))
pc=(78,78,90); rc=(205,52,42)
for n,p in enumerate(panels):
    ox,oy=p['box']
    dr.text((ox,oy+P+int(34*S)),f"{p['dens']:.2f}",font=F('Regular',50),fill=pc)
    dr.text((ox+int(150*S),oy+P+int(38*S)),p['name'],font=F('Italic',27),fill=pc)
    dr.text((ox+int(150*S),oy+P+int(70*S)),p['note'],font=F('Regular',21),fill=pc)
    if len(p['pts']):                      # red ring: one village's earshot
        c=np.array(p['pts']); i=np.argmin(np.hypot(c[:,0]-VIEW*0.55,c[:,1]-VIEW*0.45)); x,y=c[i]*ppu
        for w in range(int(3*S)): dr.ellipse((ox+x-ppu-w*0.5,oy+y-ppu-w*0.5,ox+x+ppu+w*0.5,oy+y+ppu+w*0.5),outline=rc)
ty=W-int(136*S)
dr.text((MX,ty),'Four Ways to Fill the Same Land',font=F('Regular',46),fill=pc)
dr.text((MX,ty+int(58*S)),'Each village exposes the paper as far as it can be heard, in proportion to its people (white pins). The blue is what a newcomer would hear; nowhere is it paler than at a village.',font=F('Italic',22.5),fill=pc)
tw=dr.textlength('number = people per unit of land; red ring = earshot',font=F('Italic',21))
dr.text((W-MX-tw,ty+int(14*S)),'number = people per unit of land; red ring = earshot',font=F('Italic',21),fill=rc)
im.save(OUT); print('saved',OUT)
