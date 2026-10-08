# Lattice points on the sphere |v| = n as a soap-film foam: one film cell per point (spherical Voronoi),
# film thickness -> Newton's interference colours (film.py). MO 515790.
import numpy as np, sys, json
from scipy.spatial import cKDTree, SphericalVoronoi
from PIL import Image
from film import film_rgb
from caps import E

def rot(ax,ay,az):
    cx,sx=np.cos(ax),np.sin(ax); cy,sy=np.cos(ay),np.sin(ay); cz,sz=np.cos(az),np.sin(az)
    Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]); Rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Rz@Ry@Rx

PAPER=np.array([0.988,0.982,0.976])
CORAL=np.array([0.96,0.42,0.40])

def shade(x,y,U,area,tree,R,P):
    """x,y: view coords of pixels inside the unit disc. Returns linear RGB."""
    r2=x*x+y*y; z=np.sqrt(np.clip(1-r2,0,1))
    Nv=np.stack([x,y,z],-1); Ns=Nv@R
    dd,ii=tree.query(Ns,k=2)
    c1=U[ii[:,0]]; c2=U[ii[:,1]]
    bd=(dd[:,1]**2-dd[:,0]**2)/(2*np.linalg.norm(c2-c1,axis=1))
    h=np.sqrt(area[ii[:,0]])                       # this cell's own size
    tt=np.clip(bd/h,0,1)                            # 0 on the border, ~0.5 at the centre
    # domed cell: a small spherical cap on each cell -> tilt the normal away from the site
    off=(Ns-c1)/h[:,None]
    Nd=Ns+P['dome']*h[:,None]*off
    Nd/=np.linalg.norm(Nd,axis=1,keepdims=True); Ndv=Nd@R.T
    cosi=np.clip(Ndv[:,2],0.03,1)
    # film thickness: drainage (thin at the crown, thick at the foot) + cell size + a slow swirl
    rel=np.log(area/area.mean())[ii[:,0]]
    yv=Nv[:,1]
    sw=np.sin(7*Ns[:,0]+3*np.sin(5*Ns[:,1]))*np.sin(6*Ns[:,2]+2*np.cos(4*Ns[:,0]))
    lo,hi=P['thick']
    u=0.5-0.40*yv+P['ak']*np.tanh(1.5*rel)+0.05*sw
    d=(lo+(hi-lo)*u)*(1-P['tk']*(1-np.clip(2*tt,0,1))**2)
    rgb=film_rgb(d,cosi)
    col=P['mix']+(1-P['mix'])*0.5*rgb
    fr=0.62+0.38*(1-cosi)**1.5
    col=PAPER*(1-fr[:,None])+col*fr[:,None]
    # plateau borders: thin white rims, a touch of lilac on their inner edge
    px=P['px']                                       # one output pixel in view units
    wb=P['bw']*px/ np.maximum(h,1e-9)               # border half-width in tt units (constant in pixels)
    rim=np.clip(1-(tt/np.maximum(wb,1e-9)-1),0,1)
    lil=np.exp(-((tt-1.8*wb)/(1.2*wb))**2)*0.25
    col=col*(1-lil[:,None])+lil[:,None]*np.array([0.80,0.74,0.95])
    col=col*(1-0.85*rim[:,None])+0.85*rim[:,None]*np.array([1.0,0.99,1.0])
    # coral cap
    if P.get('cap') is not None:
        cc,eps=P['cap']
        ang=np.arccos(np.clip(Ns@cc,-1,1))
        site_in=np.arccos(np.clip(c1@cc,-1,1))<eps
        e=np.abs(ang-eps)/px
        ring=np.clip(2.2*P['sc']-e,0,1)
        col=np.where((site_in&(rim>0.3))[:,None],col*(1-0.8*rim[:,None])+0.8*rim[:,None]*CORAL,col)
        col=col*(1-ring[:,None])+ring[:,None]*CORAL
    if P.get('dots'):
        dpx=dd[:,0]/px
        dot=np.clip(4.0*P['sc']-dpx,0,1)
        col=col*(1-dot[:,None])+dot[:,None]*np.where((P.get('cap') is not None and True) and site_in[:,None],CORAL,np.array([0.55,0.5,0.7]))
    # reflected windows on the domed cells and on the whole sphere
    V=np.array([0,0,1.0])
    def win(Nn,cx,cy,sx,sy,k):
        Rf=2*Nn[:,2:3]*Nn-V
        return k*np.exp(-(((Rf[:,0]-cx)/sx)**8+((Rf[:,1]-cy)/sy)**8))
    hl=win(Nv,-0.45,0.50,0.14,0.20,0.95)+win(Nv,-0.22,0.50,0.06,0.20,0.7)+0.35*win(Ndv,-0.40,0.50,0.16,0.22,1.0)
    col=col+np.clip(hl,0,1)[:,None]*(1-col)
    lim=np.clip((np.sqrt(r2)-0.955)/0.045,0,1)**1.5
    col=col*(1-0.45*lim[:,None])+0.45*lim[:,None]*np.array([0.78,0.76,0.95])
    return col

def render(n=1001, W=1024, out='_foam.png', ss=2, tilt=(0.42,0.63,0.17), strip=256, cap=True, capview=(0.30,-0.22,0.93), lay=(0.5,0.48,0.40), loupe=None, **kw):
    P=dict(dome=0.35,thick=(330,1000),mix=0.30,tk=0.10,ak=0.10,bw=0.9)
    P.update(kw)
    Pt=E(n).astype(float); U=Pt/n
    sv=SphericalVoronoi(U); area=sv.calculate_areas()
    tree=cKDTree(U); R=rot(*tilt)
    if cap:
        res=[r for r in json.load(open(cap)) if r[0]==n][0] if isinstance(cap,str) else None
        cc=np.array(res[4]) if res else None
        if cc is not None:
            # put the richest cap where the eye goes first: rotate so cc sits at view (0.18,0.12)
            cc=cc/np.linalg.norm(cc); P['cap']=(cc, n**-0.4)
            a=R@cc; b=np.array(capview,float); b/=np.linalg.norm(b)
            k=np.cross(a,b); sn=np.linalg.norm(k); cs=a@b; k/=sn
            K=np.array([[0,-k[2],k[1]],[k[2],0,-k[0]],[-k[1],k[0],0]])
            R=(np.eye(3)+sn*K+(1-cs)*K@K)@R
    Ws=W*ss; Rp=lay[2]*Ws; cxy=lay[0]*Ws; cyy=lay[1]*Ws
    P['px']=1.0/(lay[2]*W); P['sc']=W/1024; P['bw']=P['bw']*P['sc']**0.5
    img=np.empty((Ws,Ws,3),np.float32)
    xx=np.arange(Ws)
    for y0 in range(0,Ws,strip):
        yy=np.arange(y0,min(Ws,y0+strip))
        X,Y=np.meshgrid(xx,yy)
        x=(X-cxy)/Rp; y=-(Y-cyy)/Rp; r2=x*x+y*y
        bg=np.ones(X.shape+(3,))*PAPER
        # soft lilac shadow + a faint caustic ring of light under the bubble
        sx=(X-cxy)/(0.85*Rp); sy=(Y-(cyy+1.15*Rp))/(0.11*Rp); q=np.hypot(sx,sy)
        bg=bg*(1-0.10*np.exp(-q**2)[...,None]*np.array([0.45,0.5,0.15]))
        bg=bg+0.035*np.exp(-((q-0.55)/0.12)**2)[...,None]*np.array([1.0,0.85,0.9])
        ins=r2<1.0
        if ins.any():
            bg[ins]=shade(x[ins],y[ins],U,area,tree,R,P)
        e=np.clip((1-np.sqrt(r2))*Rp/ss*1.0+0.5,0,1)[...,None]   # AA silhouette
        if loupe is not None:
            lx,ly,lr,zm=loupe; cv=np.array(capview,float); cv/=np.linalg.norm(cv)
            dl=np.hypot(X-lx*Ws,Y-ly*Ws)/(lr*Ws)
            # coral tether from the cap to the loupe
            px0=np.array([cxy+cv[0]*Rp, cyy-cv[1]*Rp]); px1=np.array([lx*Ws,ly*Ws])
            dv=px1-px0; L=np.linalg.norm(dv); dv/=L
            tq=np.clip((X-px0[0])*dv[0]+(Y-px0[1])*dv[1],0,L)
            dist=np.hypot(X-px0[0]-tq*dv[0],Y-px0[1]-tq*dv[1])
            th=np.clip(1.6*ss*P['sc']-dist,0,1)*(tq>P['cap'][1]*Rp*1.05)*(dl>1)*(r2>1)
            bg=bg*(1-0.8*th[...,None])+0.8*th[...,None]*CORAL
            il=dl<1
            if il.any():
                lxs=(X[il]-lx*Ws)/(lr*Ws)*P['cap'][1]*zm+cv[0]; lys=-(Y[il]-ly*Ws)/(lr*Ws)*P['cap'][1]*zm+cv[1]
                Pl=dict(P); Pl['px']=P['px']*P['cap'][1]*zm/lr*lay[2]; Pl['dots']=True
                Pl['bw']=P['bw']*1.6
                bg[il]=shade(lxs,lys,U,area,tree,R,Pl)
                # glass rim of the loupe
                rr=np.clip(1-np.abs(dl-1)*lr*Ws/(3.0*ss*P['sc']),0,1)
                bg=bg*(1-0.9*rr[...,None])+0.9*rr[...,None]*np.array([0.97,0.55,0.52])
                gl=np.clip((dl-0.93)/0.07,0,1)*(dl<1)
                bg=bg+0.25*gl[...,None]*(1-bg)
        img[y0:y0+len(yy)]=bg
    im=Image.fromarray((np.clip(img,0,1)**(1/2.2)*255).astype(np.uint8))
    if ss>1: im=im.resize((W,W),Image.LANCZOS)
    im.save(out)
    print(out,len(U),'points')

if __name__=="__main__":
    render(int(sys.argv[1]), W=int(sys.argv[2]), out=sys.argv[3])
