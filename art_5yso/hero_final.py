import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from zero_density import density

def draw_ring_and_beads(NN, half, aspect, n_beads=200, seed=7):
    xs=np.linspace(-half*aspect, half*aspect, NN); ys=np.linspace(-half,half,NN)
    VX,VY=np.meshgrid(xs,ys); R=np.hypot(VX,VY); A=np.arctan2(VY,VX)
    a1=np.linspace(-np.pi,np.pi,3601); g1=np.clip(density(a1),0,None); g1=np.minimum(g1,0.9)
    ga=np.interp(A,a1,g1); gnorm=ga/0.9
    ringamp=(0.22+0.78*gnorm)
    ringsig=1.4*(2*half/NN)                      # ~1.4 px in v-units
    ring=np.exp(-((R-1.0)**2)/(2*ringsig**2))*ringamp
    # beads by inverse-CDF of density
    aa=np.linspace(0,2*np.pi,6000); gg=np.clip(density(aa),0,None); gg=np.minimum(gg,0.9)+0.02
    cdf=np.cumsum(gg); cdf/=cdf[-1]
    u=(np.arange(n_beads)+0.5)/n_beads
    ba=np.interp(u,cdf,aa); bx=np.cos(ba); by=np.sin(ba)
    beads=np.zeros((NN,NN)); sig=NN/900*1.7
    px=((bx/(half*aspect))*0.5+0.5)*(NN-1); py=((by/half)*0.5+0.5)*(NN-1)
    for x0,y0 in zip(px,py):
        i0=int(max(0,y0-4*sig));i1=int(min(NN,y0+4*sig));j0=int(max(0,x0-4*sig));j1=int(min(NN,x0+4*sig))
        yy=np.arange(i0,i1)[:,None];xx=np.arange(j0,j1)[None,:]
        beads[i0:i1,j0:j1]+=np.exp(-((xx-x0)**2+(yy-y0)**2)/(2*sig**2))
    return ring, beads, R, A, VX, VY

def colorize(G, half, aspect, gamma=1.7, line_freq=9.0):
    NN=G.shape[0]; Fr=G.real; Fi=G.imag
    fb=(Fr-Fr.min())/(np.ptp(Fr)+1e-12)
    def lerp(a,b,t): t=t[...,None]; return np.array(a)*(1-t)+np.array(b)*t
    c0=np.array([0.015,0.02,0.06]); c1=np.array([0.04,0.17,0.26]); c2=np.array([0.93,0.55,0.16])
    bg=np.where(fb[...,None]<0.5,lerp(c0,c1,fb*2),lerp(c1,c2,(fb-0.5)*2))*0.6
    ring,beads,R,A,VX,VY=draw_ring_and_beads(NN,half,aspect)
    Rr=np.hypot(VX,VY)
    fl=np.abs(np.sin(Fi*line_freq))**10
    outer=np.clip((Rr-1.08)/0.25,0,1); flmask=0.05+0.95*outer
    img=bg+(fl*flmask)[...,None]*np.array([0.10,0.26,0.40])*0.60
    # physical real-temperature axis (v real >=0), Tc at v=1
    axis=np.exp(-(VY**2)/(2*0.004**2))*np.clip(VX/0.15,0,1)
    img+=axis[...,None]*np.array([0.35,0.30,0.22])*0.45
    ringcol=np.array([0.55,0.95,1.0]); beadcol=np.array([0.8,0.98,1.0])
    img+=ring[...,None]*ringcol*1.15
    img+=np.clip(beads,0,1.4)[...,None]*beadcol*0.9
    for vc,warm,g in [(1.0,np.array([1.0,0.85,0.55]),1.5),(-1.0,np.array([0.7,0.85,1.0]),0.75)]:
        dist=np.hypot(VX-vc,VY); blaze=np.exp(-(dist**2)/(2*(0.055)**2))
        img+=blaze[...,None]*warm*g
    img=np.clip(img,0,None)
    lum=img.sum(-1)/3; mask=np.clip((lum-0.55)/0.45,0,1)[...,None]*img
    bloom=np.stack([gaussian_filter(mask[...,k],NN/300) for k in range(3)],-1)
    img=img+bloom*0.6
    return np.clip(img,0,1)**(1/gamma)

if __name__=="__main__":
    d=np.load("field_hero.npz"); G=d['G']; half=float(d['half']); aspect=float(d['aspect'])
    img=colorize(G,half,aspect)
    Image.fromarray((img*255).astype(np.uint8)).save("01_the_selfdual_circle.png")
    print("saved 01_the_selfdual_circle.png", img.shape)
