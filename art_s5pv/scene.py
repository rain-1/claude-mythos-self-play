# scene.py — pastel snow scene under a halo display: sky model, stereographic camera, snow, mother-of-pearl bead
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
D2R=np.pi/180
XYZ2RGB=np.array([[3.2406,-1.5372,-0.4986],[-0.9689,1.8758,0.0415],[0.0557,-0.2040,1.0570]],np.float32)

def cam_basis(caz,cel):
    f=np.array([np.cos(cel*D2R)*np.cos(caz*D2R),np.cos(cel*D2R)*np.sin(caz*D2R),np.sin(cel*D2R)])
    rt=np.cross(f,[0,0,1.]);rt/=np.linalg.norm(rt);up=np.cross(rt,f);return f,rt,up

def cam_dirs(W,H,caz,cel,sc,y0=0,y1=None):
    """unit view directions for pixels (stereographic, same convention as halo.c)"""
    if y1 is None:y1=H
    f,rt,up=cam_basis(caz,cel)
    px=np.arange(W,dtype=np.float32)+0.5;py=np.arange(y0,y1,dtype=np.float32)+0.5
    X,Y=np.meshgrid((px-W*0.5)/(W*0.5)/sc,-(py-H*0.5)/(W*0.5)/sc)
    r2=X*X+Y*Y;cz=(4-r2)/(4+r2);k=(1+cz)/2
    d=cz[...,None]*f+(X*k)[...,None]*rt+(Y*k)[...,None]*up
    return d.astype(np.float32)

def project(dirs,W,H,caz,cel,sc):
    f,rt,up=cam_basis(caz,cel)
    cz=dirs@f;k=sc*2/(1+cz)
    return W*0.5+k*(dirs@rt)*W*0.5, H*0.5-k*(dirs@up)*W*0.5

SUN_EL=22.0
SUN=np.array([np.cos(SUN_EL*D2R),0,np.sin(SUN_EL*D2R)],np.float32)

def smoothstep(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def sky_rgb(d):
    """base pastel sky (linear RGB) for unit directions d[...,3] (only meaningful for z>=0)"""
    el=np.arcsin(np.clip(d[...,2],-1,1))/D2R
    t=np.clip(el/90,0,1)
    zen=np.array([0.40,0.55,0.97],np.float32);mid=np.array([0.62,0.70,0.98],np.float32)
    hor=np.array([1.00,0.84,0.86],np.float32);low=np.array([1.0,0.93,0.80],np.float32)
    a=smoothstep(0,0.55,t)[...,None];b=smoothstep(0.35,1.0,t)[...,None]
    c=smoothstep(0,0.06,t)[...,None]
    base=low*(1-c)+hor*c;base=base*(1-a)+mid*a;base=base*(1-b)+zen*b
    g=np.degrees(np.arccos(np.clip(d@SUN,-1,1)))
    glow=(0.16*np.exp(-g/5)+0.14*np.exp(-g/30))[...,None]*np.array([1.0,0.90,0.72],np.float32)
    return (base*0.80+glow).astype(np.float32)

def vnoise(shape,cell,seed):
    rng=np.random.default_rng(seed);gh=shape[0]//cell+3;gw=shape[1]//cell+3
    g=rng.random((gh,gw)).astype(np.float32)
    z=zoom(g,cell,order=3)[:shape[0],:shape[1]];return z

def thinfilm_rgb(thick_nm,n=1.53):
    """reflectance colour of a thin film (normal incidence), returned as linear RGB in ~[0,1]"""
    lam=np.linspace(400,700,31,dtype=np.float32)
    def g1(x,m,s1,s2):
        t=(x-m)/np.where(x<m,s1,s2);return np.exp(-0.5*t*t)
    X=1.056*g1(lam,599.8,37.9,31.0)+0.362*g1(lam,442.0,16.0,26.7)-0.065*g1(lam,501.1,20.4,26.2)
    Y=0.821*g1(lam,568.8,46.9,40.5)+0.286*g1(lam,530.9,16.3,31.1)
    Z=1.217*g1(lam,437.0,11.8,36.0)+0.681*g1(lam,459.0,26.0,13.8)
    R=np.sin(2*np.pi*n*thick_nm[...,None]/lam)**2
    xyz=np.stack([(R*X).sum(-1),(R*Y).sum(-1),(R*Z).sum(-1)],-1)/Y.sum()
    return np.clip(xyz@XYZ2RGB.T,0,None)
