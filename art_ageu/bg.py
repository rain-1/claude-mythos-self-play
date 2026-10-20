"""painted pastel sky for the floating scenes."""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
def fbm(H,W,rng,scales=(256,128,64,32),amps=(1,0.6,0.35,0.2)):
    out=np.zeros((H,W))
    for s,a in zip(scales,amps):
        h=max(2,H//s+2); w=max(2,W//s+2)
        n=rng.standard_normal((h,w))
        n=zoom(n,(H/h*1.0001,W/w*1.0001),order=3)[:H,:W]
        out+=a*n
    return out/np.std(out)
def sky(W,H,sun_xy,seed=3,sun_r=0.055):
    rng=np.random.default_rng(seed)
    y=np.linspace(0,1,H)[:,None,None]
    top=np.array([0.80,0.81,0.98]); mid=np.array([0.99,0.87,0.91]); bot=np.array([1.0,0.95,0.86])
    g=np.where(y<0.55, top+(mid-top)*(y/0.55), mid+(bot-mid)*((y-0.55)/0.45))
    img=np.broadcast_to(g,(H,W,3)).copy()
    # nebula veils
    n1=fbm(H,W,rng,(1024,512,256),(1,0.5,0.2)); n2=fbm(H,W,rng,(1024,512,256),(1,0.5,0.2))
    m1=np.clip(n1-0.2,0,None)**1.2*0.14; m2=np.clip(n2-0.3,0,None)**1.2*0.14
    img+= m1[...,None]*(np.array([0.80,1.0,0.92])-img)
    img+= m2[...,None]*(np.array([0.92,0.82,1.0])-img)
    # sun
    X,Y=np.meshgrid(np.arange(W),np.arange(H))
    r=np.hypot(X-sun_xy[0],Y-sun_xy[1])/W
    glow=np.exp(-(r/(sun_r*3.2))**2)*0.55+np.exp(-(r/(sun_r*9))**2)*0.25
    img+= glow[...,None]*(np.array([1.0,0.95,0.80])-img)
    disc=np.clip((sun_r-r)/(sun_r*0.25),0,1)**0.7
    core=np.exp(-(r/sun_r)**2*1.2)
    img=img*(1-disc[...,None])+(np.array([1.0,0.97,0.88])*(1-core[...,None])+np.array([1.0,1.0,0.97])*core[...,None])*disc[...,None]
    # stars
    ns=int(2600*(W*H)/(4096**2))+60
    sx=rng.random(ns)*W; sy=rng.random(ns)*H*0.85; b=rng.random(ns)**3
    cols=np.array([[1,1,1],[0.85,0.92,1],[1,0.9,0.95],[0.9,1,0.95],[1,0.97,0.85]])
    for i in range(ns):
        rad=(1.0+3.2*b[i])*W/4096
        x0=int(sx[i]); y0=int(sy[i]); R=int(rad*6)+2
        xs=slice(max(0,x0-R),min(W,x0+R+1)); ys=slice(max(0,y0-R),min(H,y0+R+1))
        xx,yy=np.meshgrid(np.arange(xs.start,xs.stop),np.arange(ys.start,ys.stop))
        d2=((xx-sx[i])**2+(yy-sy[i])**2)/(rad**2)
        a=np.exp(-d2)*0.9
        if b[i]>0.6:   # small four-point glint
            a+=0.35*np.exp(-np.abs(xx-sx[i])/rad*0.9-((yy-sy[i])/rad*2.2)**2)+0.35*np.exp(-np.abs(yy-sy[i])/rad*0.9-((xx-sx[i])/rad*2.2)**2)
        a=np.clip(a,0,1)[...,None]
        c=cols[i%5]
        img[ys,xs]=img[ys,xs]*(1-a)+c*a
    return np.clip(img,0,1)
