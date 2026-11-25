"""EARSHOT — hero.  Cut-paper night plain seen from a hill; every lamp is a fixed number of people drawn from the
simulated density u of the nonlocal Fisher-KPP equation; the ground is tinted by the 'dose' phi*u (what a newcomer would hear).
usage: earshot.py W snapshot_index out.png"""
import sys, numpy as np, scipy.fft as sf, numba as nb
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.special import j1
from PIL import Image, ImageDraw, ImageFont
W=int(sys.argv[1]); SN=int(sys.argv[2]); OUT=sys.argv[3]; SIM=sys.argv[4] if len(sys.argv)>4 else 'data/sim_front.npz'
S=W/1024.0; rng=np.random.default_rng(11)
d=np.load(SIM); u=d['snaps'][SN].astype(np.float64); L=float(d['L']); N=u.shape[0]; dx=L/N; tsnap=float(d['times'][SN]); s_par=float(d['s'])
k=2*np.pi*sf.fftfreq(N,dx); kx,ky=np.meshgrid(k,k,indexing='ij'); kk=np.hypot(kx,ky)
ph=np.where(kk>0,2*j1(kk)/np.where(kk>0,kk,1),1.0); dose=sf.ifft2(sf.fft2(u)*ph).real

# ---------- geometry: window, camera ----------
M=int(0.085*W); MB=int(0.150*W)                      # mat margins (bottom wider for the caption)
x0,x1,y0,y1=M,W-M,M,W-MB; ww=x1-x0; wh=y1-y0
HOR=0.255; f=0.70*ww; h=10.5; D0=25.0; yh=y0+HOR*wh; cx=x0+0.5*ww
def ground(sx,sy):
    q=(sy-yh)/f; Y=h/np.maximum(q,1e-6); X=(sx-cx)/f*Y; return X,Y-D0     # sim coords relative to the founder
def screen(X,Y):
    Yc=Y+D0; return cx+f*X/Yc, yh+f*h/Yc, Yc
yy,xx=np.mgrid[0:W,0:W].astype(np.float64)
def noise(shape,sig,seed):
    r=np.random.default_rng(seed).standard_normal(shape); r=gaussian_filter(r,sig,mode='wrap'); return r/r.std()
def hexc(sx): return np.array([int(sx[i:i+2],16) for i in (1,3,5)],float)/255
INK=dict(night=hexc('#0d1230'),deep=hexc('#151c46'),ind=hexc('#232d66'),dusk=hexc('#4a4a86'),mauve=hexc('#8a6f9c'),
         rose=hexc('#d79a9a'),peach=hexc('#f0c3a0'),cream=hexc('#f6ecd2'),lamp=hexc('#ffd98a'),amber=hexc('#f2a84a'),
         red=hexc('#d8362b'),mat=hexc('#efe6d0'),pencil=hexc('#4b4a55'),plain=hexc('#10163a'),settled=hexc('#27275c'))
img=np.zeros((W,W,3))
# ---------- sky: torn bands ----------
t=(yy-y0)/(yh-y0)
bands=[(0.00,'night'),(0.30,'deep'),(0.52,'ind'),(0.70,'dusk'),(0.82,'mauve'),(0.905,'rose'),(0.962,'peach')]
img[:]=INK['night']
for i,(lv,nm) in enumerate(bands[1:]):
    edge=lv+0.022*noise((W,),40*S,100+i)[None,:]+0.004*noise((W,),4*S,200+i)[None,:]+0.05*(xx/W-0.5)*(1 if i%2 else -1)
    a=np.clip((t-edge)*(yh-y0)/1.2+0.5,0,1)
    sh=np.clip(1-np.abs((t-edge)*(yh-y0)-3*S)/(5*S),0,1)*0.20*a      # shadow under the torn edge
    lip=np.clip(1-np.abs((t-edge)*(yh-y0)+0.2*S)/(1.3*S),0,1)*0.35    # pale torn fibre
    img=img*(1-a[...,None])+INK[nm]*a[...,None]
    img=img*(1-sh[...,None]); img=img+(INK['cream']-img)*lip[...,None]*0.5
# moon + stars
mx,my,mr=x0+0.76*ww,y0+0.085*wh,0.030*ww
dm=np.hypot(xx-mx,yy-my)
img*= (1-0.35*np.clip(1-(np.hypot(xx-mx-5*S,yy-my-7*S)-mr)/(9*S),0,1)*(dm>mr))[...,None]
am=np.clip((mr-dm)/1.2+0.5,0,1); img=img+(INK['cream']*(0.97+0.03*noise((W,W),6*S,5)[...,None]*0.5)-img)*am[...,None]
halo=np.exp(-np.maximum(dm-mr,0)/(0.05*ww))*0.10; img=img+(INK['cream']-img)*(halo*(dm>mr))[...,None]
light=np.zeros((W,W))
@nb.njit(cache=True)
def splat(buf,px,py,rad,en):
    H,Wd=buf.shape
    for i in range(px.shape[0]):
        r=rad[i]; R=int(3*r)+1; x=px[i]; y=py[i]; ix=int(x); iy=int(y)
        if ix<R or iy<R or ix>=Wd-R or iy>=H-R: continue
        inv=1.0/(2*r*r)
        for a in range(iy-R,iy+R+1):
            for b in range(ix-R,ix+R+1):
                buf[a,b]+=en[i]*np.exp(-((b+0.5-x)**2+(a+0.5-y)**2)*inv)
ns=420; sxs=rng.uniform(x0,x1,ns); sys_=y0+(yh-y0)*rng.uniform(0,1,ns)**1.6*0.86
keep=np.hypot(sxs-mx,sys_-my)>mr*1.6; star=np.zeros((W,W))
splat(star,sxs[keep],sys_[keep],np.full(keep.sum(),0.55*S)*rng.uniform(0.7,1.5,keep.sum()),rng.uniform(0.3,1.0,keep.sum()))
img=img+(INK['cream']-img)*np.clip(star,0,1)[...,None]*0.9

# ---------- the plain ----------
below=yy>yh
X,Y=ground(xx,yy)
gi=(X+L/2)/dx-0.5; gj=(Y+L/2)/dx-0.5
dg=map_coordinates(dose,[gi,gj],order=1,mode='constant',cval=0.0)*below
depth=np.where(below,Y+D0,1e9); haze=np.clip(1-np.exp(-(depth-8)/55.0),0,1)
gcol=INK['plain'][None,None,:]+(INK['settled']-INK['plain'])[None,None,:]*np.clip(dg,0,1.25)[...,None]**1.3
gcol=gcol*(1+0.035*noise((W,W),1.2*S,7)[...,None]+0.03*noise((W,W),30*S,8)[...,None])
gcol=gcol+(INK['dusk']-gcol)*(haze[...,None]*0.75)
img=np.where(below[...,None],gcol,img)
# far hills (three sheets) at the horizon
for i,(amp,base,nm,sd) in enumerate([(0.020,0.006,'dusk',31),(0.030,-0.004,'ind',32),(0.016,-0.012,'deep',33)]):
    prof=yh-wh*(base+amp*np.clip(0.5+0.5*noise((W,),(70-18*i)*S,sd),0,None)**1.5*(1+0.6*np.sin(xx[0]/W*(5+2*i)+i)))
    prof=prof+0.8*S*noise((W,),2*S,sd+50)
    low=yh+wh*(0.012+0.010*i)
    a=np.clip((yy-prof[None,:])/1.2+0.5,0,1)*np.clip((low-yy)/(6*S)+0.5,0,1)
    sh=np.clip(1-(yy-low)/(7*S),0,1)*(yy>low)*0.25
    img=img*(1-sh[...,None]); img=img+(INK[nm]-img)*a[...,None]
    lip=np.clip(1-np.abs(yy-prof[None,:]-0.8*S)/(1.1*S),0,1)*0.22; img=img+(INK['cream']-img)*lip[...,None]

# ---------- lamps: one lamp per 1/RHO people ----------
RHO=420.0
lam=u*dx*dx*RHO; cnt=rng.poisson(lam); ii,jj=np.nonzero(cnt); rep=cnt[ii,jj]
ii=np.repeat(ii,rep); jj=np.repeat(jj,rep); nl=ii.size
LX=(ii+rng.random(nl))*dx-L/2; LY=(jj+rng.random(nl))*dx-L/2
px,py,dep=screen(LX,LY); ok=(dep>h/((y1-yh)/f)*0.9)
px,py,dep,LX,LY=px[ok],py[ok],dep[ok],LX[ok],LY[ok]
sc=f/dep                                             # pixels per unit at that depth
rad=np.clip(0.0052*sc*rng.uniform(0.75,1.3,px.size),0.42*S,None)
en=(0.0052*sc/rad)**2*rng.uniform(0.6,1.25,px.size)*np.exp(-(dep-8)/90.0)
splat(light,px,py,rad,en)
population=u.sum()*dx*dx
# founder: where the run began (sim centre)
fx,fy,fd=screen(0.0,0.0)
A=1-np.exp(-2.1*light); glow=gaussian_filter(light,5*S)+0.6*gaussian_filter(light,16*S)
G=1-np.exp(-0.42*glow)
warm=INK['lamp'][None,None,:]*(1-0.5*np.clip(A,0,1)[...,None])+INK['cream'][None,None,:]*0.5*np.clip(A,0,1)[...,None]
img=img+(INK['amber']-img)*(G*below)[...,None]*0.55
img=img+(warm-img)*(A*below)[...,None]
# earshot ring round the founder (radius 1) in red thread, and the founder's red lamp
th=np.linspace(0,2*np.pi,4000); rx,ry,_=screen(np.cos(th),np.sin(th))
ring=np.zeros((W,W)); splat(ring,rx,ry,np.full(th.size,0.55*S),np.full(th.size,0.42))
ring2=np.zeros((W,W)); splat(ring2,np.array([fx]),np.array([fy]),np.array([1.7*S]),np.array([1.5]))
ra=np.clip(ring,0,1)*0.95+np.clip(ring2,0,1)
img=img+(INK['red']-img)*np.clip(ra,0,1)[...,None]

# ---------- foreground: the hill we stand on, a tree, a listener ----------
prof=y1-wh*(0.055+0.075*np.exp(-((xx[0]-x0-0.16*ww)/(0.30*ww))**2)+0.012*noise((W,),60*S,41))+1.0*S*noise((W,),2.5*S,42)
a=np.clip((yy-prof[None,:])/1.2+0.5,0,1)
sh=np.clip(1-(prof[None,:]-yy)/(16*S),0,1)*(yy<prof[None,:])*0.45
img=img*(1-sh[...,None]); fg=INK['night']*0.62*(1+0.05*noise((W,W),1.5*S,43)[...,None])
img=img+(fg-img)*a[...,None]
lip=np.clip(1-np.abs(yy-prof[None,:]-1.0*S)/(1.2*S),0,1)*0.30; img=img+(INK['dusk']-img)*lip[...,None]
def blob(mask): 
    global img
    m=np.clip(mask,0,1)[...,None]; img=img+(INK['night']*0.62-img)*m
# cypress
tx=x0+0.115*ww; tb=prof[int(tx)]+4*S; thh=0.175*wh
tt=np.clip((tb-yy)/thh,0,1); wdt=0.0125*ww*np.sin(np.pi*np.clip(tt,0,1)**0.55)**0.8*(1+0.10*noise((W,W),4*S,44))
blob((wdt-np.abs(xx-tx-0.0012*ww*np.sin(tt*7)))/1.2*((yy<tb)&(yy>tb-thh))); blob((2.2*S-np.abs(xx-tx))/1.2*((yy<tb+6*S)&(yy>tb-0.3*thh)))
# listener: a small standing figure with a hand to the ear
lx=x0+0.205*ww; lb=prof[int(lx)]+3*S; lh=0.078*wh
def cap(ax,ay,bx,by,r):
    pax=xx-ax; pay=yy-ay; bax=bx-ax; bay=by-ay; hh=np.clip((pax*bax+pay*bay)/(bax*bax+bay*bay),0,1)
    return (r-np.hypot(pax-bax*hh,pay-bay*hh))/1.2+0.5
blob(cap(lx,lb,lx-0.10*lh,lb-0.50*lh,0.085*lh)); blob(cap(lx+0.16*lh,lb,lx+0.06*lh,lb-0.50*lh,0.085*lh))      # legs
blob(cap(lx-0.02*lh,lb-0.50*lh,lx+0.02*lh,lb-0.84*lh,0.15*lh))                                                # coat
blob((0.105*lh-np.hypot(xx-lx-0.05*lh,yy-lb+1.0*lh))/1.2+0.5)                                               # head
blob(cap(lx+0.10*lh,lb-0.80*lh,lx+0.30*lh,lb-0.70*lh,0.05*lh)); blob(cap(lx+0.30*lh,lb-0.70*lh,lx+0.17*lh,lb-0.98*lh,0.045*lh))  # arm to the ear

# paper grain inside the window, then the mat
img*= (1+0.022*noise((W,W),0.8*S,9))[...,None]
inwin=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
mat=INK['mat'][None,None,:]*(1+0.018*noise((W,W),1.0*S,60)[...,None]+0.012*noise((W,W),40*S,61)[...,None])
dx_in=np.minimum(np.minimum(xx-x0,x1-xx),np.minimum(yy-y0,y1-yy))
img*= (1-0.55*np.exp(-np.maximum(np.minimum(xx-x0,yy-y0),0)/(10*S))*inwin)[...,None]      # shadow cast by the mat (light from top-left)
out=np.where(inwin[...,None],img,mat)
bev=(dx_in<0)&(dx_in>-3.5*S); out=np.where(bev[...,None],out*0.5+0.5*np.array([1,1,0.97])*np.where((xx<x0)|(yy<y0),0.80,1.03)[...,None],out)
im=Image.fromarray((np.clip(out,0,1)*255+0.5).astype(np.uint8)); dr=ImageDraw.Draw(im)
F=lambda nm,sz: ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{nm}.ttf',int(sz*S))
pc=tuple(int(v*255) for v in INK['pencil']); rc=tuple(int(v*255) for v in INK['red'])
nlamps=int(px.size)
dr.text((x0,y1+int(20*S)),'Earshot',font=F('Regular',34),fill=pc)
dr.text((x0,y1+int(62*S)),'Everyone competes with whoever lives within earshot. The settlers spread at a steady pace, and behind them the land',font=F('Italic',15.2),fill=pc)
dr.text((x0,y1+int(82*S)),'gathers into villages just too far apart to hear one another. Between the villages nobody lives, and the land is full.',font=F('Italic',15.2),fill=pc)
cap2=f'uₜ = DΔu + u(1 − φ*u), φ = the disc of radius R, R²/D = {s_par:.0f}, time {tsnap:.0f}.  {nlamps:,} lamps, one per 1/{RHO:.0f} of what a unit square holds when spread evenly.'
dr.text((x0,y1+int(110*S)),cap2,font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',int(10.6*S)),fill=pc)
tw=dr.textlength('red ring: earshot of the first settler',font=F('Italic',12.2))
dr.text((x1-tw,y1+int(26*S)),'red ring: earshot of the first settler',font=F('Italic',12.2),fill=rc)
im.save(OUT); print('saved',OUT,'lamps',nlamps,'population',population,'t',tsnap)
