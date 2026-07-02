import numpy as np, time

def make_field(charges):
    C=np.array(charges,np.float32)
    def field(X,Y):
        Ex=np.zeros_like(X); Ey=np.zeros_like(X); phi=np.zeros_like(X)
        for cx,cy,q in C:
            dx=X-cx; dy=Y-cy; r2=dx*dx+dy*dy+np.float32(1e-6)
            inv=q/r2
            Ex+=dx*inv; Ey+=dy*inv
            phi+=q*(np.float32(-0.5)*np.log(r2))
        return Ex,Ey,phi
    return field, C

def lic(field, W, steps=90, ds=1.0, world=1.38, seed=1):
    rng=np.random.default_rng(seed)
    noise=rng.random((W,W),dtype=np.float32)
    xs=np.linspace(-world,world,W,dtype=np.float32)
    X,Y=np.meshgrid(xs,xs)
    inv=np.float32((W-1)/(2*world))
    Wm=np.float32(world)
    def sample(px,py,out=None):
        fx=(px+Wm)*inv; fy=(py+Wm)*inv
        np.clip(fx,0,W-1.001,out=fx); np.clip(fy,0,W-1.001,out=fy)
        x0=fx.astype(np.int32); y0=fy.astype(np.int32)
        tx=fx-x0; ty=fy-y0
        x1=x0+1; y1=y0+1
        v=(noise[y0,x0]*(1-tx)*(1-ty)+noise[y0,x1]*tx*(1-ty)
           +noise[y1,x0]*(1-tx)*ty+noise[y1,x1]*tx*ty)
        return v
    def Enorm(px,py):
        Ex,Ey,_=field(px,py); m=np.sqrt(Ex*Ex+Ey*Ey)+np.float32(1e-9)
        return Ex/m, Ey/m
    acc=sample(X,Y).astype(np.float32); cnt=np.ones_like(acc)
    dw=np.float32(2*world/(W-1)*ds)
    for sgn in (np.float32(1),np.float32(-1)):
        px=X.copy(); py=Y.copy()
        for k in range(steps):
            ux,uy=Enorm(px,py)
            mx=px+sgn*ux*dw*np.float32(0.5); my=py+sgn*uy*dw*np.float32(0.5)
            ux2,uy2=Enorm(mx,my)
            px+=sgn*ux2*dw; py+=sgn*uy2*dw
            wgt=np.float32(0.5*(1+np.cos(np.pi*k/steps)))
            acc+=sample(px,py)*wgt; cnt+=wgt
    return acc/cnt, X, Y
