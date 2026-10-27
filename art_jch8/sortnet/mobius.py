import numpy as np, sys, rsn, tubes, time, json
from scipy import ndimage as ndi
from PIL import Image
from flat import wheel, hexrgb
def rotx(a): c,s=np.cos(a),np.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def rotz(a): c,s=np.cos(a),np.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def build(n,seed,Rc=1.0,hw=0.42,lift=0.035,smooth=0.7,twist=1):
    w=rsn.network(n,seed); P=rsn.trajectories(n,w); N=len(w)
    curves=[]
    for i in range(n):
        y=P[:,i].astype(float)
        # periodic extension: next lap the wire continues reversed
        ext=np.concatenate([n-1-y[:-1],y[:-1],n-1-y])
        ys=ndi.gaussian_filter1d(ext,N/n*smooth)[N:2*N+1]
        dy=np.gradient(ys)
        t=np.arange(N+1)/N; u=2*np.pi*t
        v=hw*(2*ys/(n-1)-1)
        c=np.cos(u/2); s=np.sin(u/2)
        X=(Rc+v*c)*np.cos(u); Y=(Rc+v*c)*np.sin(u); Z=v*s
        # surface normal ~ (cos u * s... ) via cross product of partials
        Xu=np.stack([-(Rc+v*c)*np.sin(u)-0.5*v*s*np.cos(u), (Rc+v*c)*np.cos(u)-0.5*v*s*np.sin(u), 0.5*v*c],1)
        Xv=np.stack([c*np.cos(u),c*np.sin(u),s],1)
        nn=np.cross(Xu,Xv); nn/=np.linalg.norm(nn,axis=1,keepdims=True)
        off=lift*np.tanh(dy*n/3)[:,None]*nn
        curves.append(np.stack([X,Y,Z],1)+off)
    return curves
def render(n=40,seed=5,W=1600,H=1200,ss=2,out='mob.png',tilt=1.05,spin=0.3,dist=4.2,rad=None,hw=0.42,fov=0.62,cy=0.47,sun=(-0.5,0.55,0.75)):
    t0=time.time()
    curves=build(n,seed,hw=hw)
    Rm=rotx(-tilt)@rotz(spin)
    W2,H2=W*ss,H*ss; f=0.5*W2/np.tan(fov/2)
    if rad is None: rad=0.42*2*hw/n
    floor_z=-0.62
    Xs=[];Ys=[];Zs=[];Rs=[];Cs=[];Wp=[]
    for i,C in enumerate(curves):
        Q=tubes.resample(C,rad*0.3) if False else C
        # dense resample in 3D
        seg=np.linalg.norm(np.diff(Q,axis=0),axis=1); s=np.concatenate([[0],np.cumsum(seg)]); tt=np.arange(0,s[-1],rad*0.25)
        Q=np.stack([np.interp(tt,s,Q[:,k]) for k in range(3)],1)
        Wp.append(Q)
        V=Q@Rm.T; V[:,2]-=dist           # camera at origin looking -z
        x=W2/2+f*V[:,0]/(-V[:,2]); y=H2*cy-f*V[:,1]/(-V[:,2]); r=f*rad/(-V[:,2])
        Xs.append(x);Ys.append(y);Zs.append(V[:,2]*f/(-V[:,2]).mean()*0+V[:,2]*400*ss);Rs.append(r);Cs.append(np.full(len(x),i))
    X=np.concatenate(Xs);Y=np.concatenate(Ys);Z=np.concatenate(Zs);R=np.concatenate(Rs);C=np.concatenate(Cs);WP=np.concatenate(Wp)
    zb=np.full((H2,W2),-1e18); nrm=np.zeros((H2,W2,3)); ib=np.full((H2,W2),-1,np.int64); ub=np.zeros((H2,W2),np.int64)
    # z in splat is 'larger = closer'; scale radius term consistent: use depth in px units
    tubes.splat(X,Y,Z,R,C,W2,H2,zb,nrm,ib,ub)
    # --- floor (world z=floor_z) shadow: project tubes along sun onto floor, then to screen
    L=np.array(sun,float); L/=np.linalg.norm(L)
    tsh=(WP[:,2]-floor_z)/L[2]; F=WP-tsh[:,None]*L
    V=F@Rm.T; V[:,2]-=dist
    fx=W2/2+f*V[:,0]/(-V[:,2]); fy=H2*cy-f*V[:,1]/(-V[:,2]); fr=f*rad/(-V[:,2])*1.1
    M=np.zeros((H2,W2)); tubes.splat_mask(fx,fy,fr,W2,H2,M,np.ones(len(fx)))
    M=ndi.gaussian_filter(M,4*ss)
    # self shadow via light-space depth map
    LS=64*ss; e1=np.cross(L,[0,0,1.]); e1/=np.linalg.norm(e1); e2=np.cross(L,e1)
    a=WP@e1; b=WP@e2; dep=WP@L
    res=1400; amin,amax,bmin,bmax=a.min()-.1,a.max()+.1,b.min()-.1,b.max()+.1; sc=res/max(amax-amin,bmax-bmin)
    lz=np.full((res,res),-1e18); ln=np.zeros((res,res,3)); li=np.full((res,res),-1,np.int64); lu=np.zeros((res,res),np.int64)
    tubes.splat((a-amin)*sc,(b-bmin)*sc,dep*sc,np.full(len(a),rad*sc),C,res,res,lz,ln,li,lu)
    on=ib>=0
    k=ub[on]; pk=WP[k]
    # surface point approx = centre + normal(world)*rad ; normal view->world
    nv=nrm[on]*np.array([1,-1,1]); nw=nv@Rm
    ps=pk+nw*rad*0.9
    pa=((ps@e1-amin)*sc).astype(int).clip(0,res-1); pb=((ps@e2-bmin)*sc).astype(int).clip(0,res-1)
    lit=(ps@L*sc+1.2>=ndi.maximum_filter(lz,3)[pb,pa]).astype(float)
    litimg=np.ones((H2,W2)); litimg[on]=lit; litimg=ndi.gaussian_filter(litimg,0.8*ss)
    # shading
    cols=wheel(np.arange(n)/(n-1))
    lam=np.clip(nw@L,0,1)
    Vdir=-(pk@Rm.T-np.array([0,0,dist])); Vdir/=np.linalg.norm(Vdir,axis=1,keepdims=True); Vw=Vdir@Rm
    Hh=L[None]+Vw; Hh/=np.linalg.norm(Hh,axis=1,keepdims=True)
    spec=np.clip(np.sum(nw*Hh,1),0,1)**28
    base=cols[ib[on]]
    sl=litimg[on]
    shade=0.78+0.36*lam*(0.55+0.45*sl)
    cool=np.array([0.86,0.88,1.0])
    tubec=base*shade[:,None]*(1-0.12*(1-sl[:,None])*(1-cool))+0.55*(spec*sl)[:,None]
    # paper sweep background (gradient), floor shadow tint
    yy=np.linspace(0,1,H2)[:,None,None]
    bg=np.array([0.995,0.988,0.978])*(1-0.03*yy)+np.array([0.0,0.0,0.0])
    img=np.broadcast_to(bg,(H2,W2,3)).copy()
    img*=1-0.25*np.clip(M,0,1)[...,None]*np.array([0.55,0.5,0.2])
    img[on]=tubec
    img=np.clip(img,0,1)
    im=Image.fromarray((img*255).astype(np.uint8)).resize((W,H),Image.LANCZOS); im.save(out); print('saved',out,time.time()-t0)
    return im
if __name__=='__main__':
    render(n=int(sys.argv[1]),seed=int(sys.argv[2]),out=sys.argv[3])
