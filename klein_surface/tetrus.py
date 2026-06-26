"""The 'tetrus' — a genus-3 surface with tetrahedral symmetry, the natural
shape of the Klein quartic. It is the boundary of a thickened tetrahedral frame
(4 vertices, 6 edges): genus = E - V + 1 = 6 - 4 + 1 = 3. Rendered by
sphere-tracing a signed-distance field, fully vectorised in numpy."""
import numpy as np, sys, math
sys.path.insert(0,'octonions')
import figkit
from PIL import Image

# regular tetrahedron vertices
TV=np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]],float)
EDGES=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
TUBE=0.52
KSMIN=0.32

def rotmat(ax,ay):
    cx,sx=math.cos(ax),math.sin(ax); cy,sy=math.cos(ay),math.sin(ay)
    Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    return Ry@Rx

def sdf(P, R):
    """P: (...,3). returns distance to fattened tetra frame."""
    Pr=P@R.T
    d=None
    for (i,j) in EDGES:
        a=TV[i]; b=TV[j]; ba=b-a
        pa=Pr-a
        h=np.clip((pa@ba)/(ba@ba),0,1)[...,None]
        dist=np.linalg.norm(pa-ba*h,axis=-1)-TUBE
        if d is None: d=dist
        else:
            k=KSMIN
            hh=np.clip(0.5+0.5*(dist-d)/k,0,1)
            d=dist*(1-hh)+d*hh - k*hh*(1-hh)
    return d

def render(S=1100, ss=1, ax=0.6, ay=0.9):
    W=S*ss
    R=rotmat(ax,ay)
    # camera
    cam=np.array([0,0,6.2]); f=2.4
    yy,xx=np.mgrid[0:W,0:W]
    px=(xx-W/2)/(W/2); py=-(yy-W/2)/(W/2)
    dirs=np.stack([px, py, -np.full_like(px,f)],-1)
    dirs/=np.linalg.norm(dirs,axis=-1,keepdims=True)
    ro=np.broadcast_to(cam,dirs.shape).copy()
    t=np.zeros((W,W)); hit=np.zeros((W,W),bool); alive=np.ones((W,W),bool)
    for _ in range(90):
        P=ro+dirs*t[...,None]
        dd=sdf(P,R)
        dd=np.where(alive,dd,1.0)
        t=t+np.where(alive,dd*0.9,0.0)
        newhit=alive&(dd<0.001)
        hit|=newhit; alive&=~newhit; alive&=(t<12)
        if not alive.any(): break
    P=ro+dirs*t[...,None]
    # normals
    e=0.004
    def g(off): return sdf(P+off,R)
    nx=g([e,0,0])-g([-e,0,0]); ny=g([0,e,0])-g([0,-e,0]); nz=g([0,0,e])-g([0,0,-e])
    N=np.stack([nx,ny,nz],-1); N/=(np.linalg.norm(N,axis=-1,keepdims=True)+1e-9)
    L=np.array([0.5,0.7,0.55]); L=L/np.linalg.norm(L)
    diff=np.clip((N*L).sum(-1),0,1)
    V=-dirs; H=(L+V); H/=np.linalg.norm(H,axis=-1,keepdims=True)+1e-9
    spec=np.clip((N*H).sum(-1),0,1)**40
    rim=(1-np.clip((N*V).sum(-1),0,1))**2.4
    # colour by position (rotated) -> teal..gold gradient
    Pr=P@R.T; u=np.clip((Pr[...,1]+1.7)/3.4,0,1)
    c1=np.array([0.10,0.55,0.65]); c2=np.array([1.0,0.78,0.35])
    base=c1*(1-u[...,None])+c2*u[...,None]
    col=base*(0.18+0.95*diff[...,None]) + spec[...,None]*np.array([1,1,0.95])*0.6 + rim[...,None]*np.array([0.3,0.55,0.9])*0.6
    bg=np.zeros((W,W,3))+np.array([0.02,0.025,0.05])
    rr=np.sqrt(px**2+py**2); bg+= (0.05*np.clip(1-rr,0,1))[...,None]*np.array([0.2,0.3,0.5])
    out=np.where(hit[...,None], col, bg)
    out=1.0-np.exp(-1.25*np.clip(out,0,None))
    img=Image.fromarray((np.clip(out,0,1)*255).astype('uint8'))
    if ss>1: img=img.resize((S,S),Image.LANCZOS)
    return img

if __name__=="__main__":
    import time; t0=time.time()
    viz=render(1100, ss=1, ax=0.95, ay=0.22)
    print("raymarch",round(time.time()-t0,1))
    body=("This is the Klein quartic given a body you can hold. Topologically it is a surface of "
          "genus 3 — a sphere with three handles — and the most natural way to build one with "
          "TETRAHEDRAL symmetry is to take the wire frame of a tetrahedron (4 corners, 6 struts) "
          "and thicken it into tubes. Counting handles: a graph of E edges and V vertices, "
          "fattened, gives a surface of genus E−V+1 = 6−4+1 = 3, exactly. The four-fold symmetry "
          "of the tetrahedron is visible in the four junctions and the holes between the struts. "
          "Wrap the {7,3} heptagon tiling of the previous gallery onto this shape and its 24 "
          "heptagons close up perfectly, carrying all 168 of the Klein quartic's symmetries. "
          "(Rendered by sphere-tracing a signed-distance field — no mesh, just the equation of "
          "distance-to-the-frame.)")
    fig=figkit.caption(viz,"BONUS · THE EMBEDDED SURFACE","The tetrus — the Klein quartic with a body",
                       body,accent=(120,210,235),W=1100)
    figkit.save(fig,"klein_surface/01_tetrus.png")
    print("done",fig.size)
