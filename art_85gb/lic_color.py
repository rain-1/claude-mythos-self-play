import numpy as np
from scipy.ndimage import gaussian_filter

def color_lic(L, field, X, Y, C, world,
              div_gain=0.75, licgain=1.7, base=0.12, glow_amp=1.3):
    Ex,Ey,phi=field(X,Y); mag=np.sqrt(Ex*Ex+Ey*Ey)
    # LIC -> local-contrast luminance
    lo=gaussian_filter(L, 6); lic=(L-lo)
    s=np.std(lic)+1e-6; lic=np.clip(0.5+licgain*lic/(4*s),0,1)
    p=np.tanh(phi*div_gain)                      # -1..1  (source>0 sink<0)
    # diverging palette anchors
    cool=np.array([[0.02,0.05,0.14],[0.05,0.25,0.55],[0.15,0.6,0.85],[0.55,0.85,0.95]])
    warm=np.array([[0.02,0.05,0.14],[0.5,0.15,0.08],[0.9,0.45,0.1],[1.0,0.85,0.5]])
    def ramp(anch,t):  # t in 0..1
        n=len(anch)-1; f=np.clip(t,0,1)*n; i=np.clip(f.astype(int),0,n-1); fr=(f-i)[...,None]
        return anch[i]*(1-fr)+anch[i+1]*fr
    col=np.where((p>=0)[...,None], ramp(warm,p), ramp(cool,-p))
    rgb=col*(base+ (1-base)*lic[...,None])
    # charge glows
    glow=np.zeros_like(X)
    inv=(X.shape[0]-1)/(2*world)
    for cx,cy,q in C:
        r2=(X-cx)**2+(Y-cy)**2
        glow=np.maximum(glow, np.exp(-r2*inv*inv/ (10.0)) )  # tight core
    gcol=np.zeros_like(rgb)
    # tint glow by nearest charge sign
    for cx,cy,q in C:
        r2=(X-cx)**2+(Y-cy)**2
        g=np.exp(-r2/ (0.010))
        tint=np.array([1.0,0.8,0.45]) if q>0 else np.array([0.45,0.75,1.0])
        gcol+=g[...,None]*tint*glow_amp
    rgb=rgb+gcol
    return np.clip(rgb,0,1)

if __name__=="__main__":
    from PIL import Image
    from lic import make_field, lic
    import time
    configs={
      'hex':[(-0.6,0.0,1),(0.6,0.0,-1),(0.0,0.7,-1),(0.0,-0.7,1),(-0.5,-0.55,-1),(0.5,0.55,1)],
      'quad':[(-0.55,-0.55,1),(0.55,-0.55,-1),(0.55,0.55,1),(-0.55,0.55,-1)],
      'tri':[(0.0,0.75,1),(-0.65,-0.38,1),(0.65,-0.38,1),(0.0,0.0,-3)],
    }
    world=1.35
    for name,ch in configs.items():
        field,C=make_field(ch)
        t0=time.time(); L,X,Y=lic(field,700,steps=80,ds=1.0,seed=4)
        rgb=color_lic(L,field,X,Y,C,world)
        Image.fromarray((rgb*255).astype(np.uint8)).save(f'lic_{name}.png')
        print(name,"done",round(time.time()-t0,1))
