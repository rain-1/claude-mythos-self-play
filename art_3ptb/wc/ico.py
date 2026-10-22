import numpy as np
from wc import *
phi=(1+5**0.5)/2
C=dict(rose='#ee7f9c',mint='#62cfa8',butter='#f2cb52',sky='#78b6ec',lilac='#ad92e6',peach='#f7a174',coral='#f2735f')
WHEEL=['rose','peach','butter','mint','sky','lilac']
def icosa():
    # vertex at top: axis through (0,1,phi) rotated to z
    V=[]
    for a in (-1,1):
        for b in (-phi,phi):
            V+= [(0,a,b),(a,b,0),(b,0,a)]
    V=np.array(V,float)
    top=np.array([0,1,phi])/np.linalg.norm([0,1,phi])
    z=np.array([0,0,1.]); v=np.cross(top,z); c=top@z; vx=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    Rm=np.eye(3)+vx+vx@vx/(1+c)
    V=V@Rm.T
    E=[(i,j) for i in range(12) for j in range(i+1,12) if abs(np.linalg.norm(V[i]-V[j])-2)<1e-6]
    F=[(i,j,k) for i in range(12) for j in range(i+1,12) for k in range(j+1,12)
       if all(abs(np.linalg.norm(V[p]-V[q])-2)<1e-6 for p,q in ((i,j),(j,k),(i,k)))]
    return V/ (2/ (2*np.sin(np.pi/5))),E,F   # scale so edge = s5 (ring circumradius 1)

def rot(ax,t):
    c,s=np.cos(t),np.sin(t)
    if ax=='x': return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if ax=='y': return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])

def paint_ico(S,cx,cy,scale,spin=None,tilt=-0.16,dens=0.17,light=(-0.5,-0.6,0.62)):
    V,E,F=icosa()
    top=np.argmax(V[:,2]); ring=[i for i in range(12) if abs(np.linalg.norm(V[i]-V[top])-2*np.sin(np.pi/5))<1e-6]
    if spin is None:
        spin=-np.arctan2(V[ring[0],1],V[ring[0],0])
    Rm=rot('x',tilt)@rot('z',spin)   # world z = up; view: x right, z up, y depth (toward viewer = -y)
    P=V@Rm.T
    def X(p): return np.stack([cx+p[...,0]*scale, cy-p[...,2]*scale],-1)
    K={k:pigment(hexrgb(v)) for k,v in C.items()}
    L=np.array(light);L/=np.linalg.norm(L)
    faces=[]
    for f in F:
        q=P[list(f)]; n=np.cross(q[1]-q[0],q[2]-q[0]); cen=q.mean(0)
        if n@cen<0: n=-n
        n/=np.linalg.norm(n)
        faces.append((f,n,cen,V[list(f)].mean(0)))
    view=np.array([0,-1.,0])
    back=[x for x in faces if x[1]@view<=0]; front=[x for x in faces if x[1]@view>0]
    back=[x[:3]+(x[3],) for x in back]
    s=S.s
    pc=P.mean(0)
    def hue(cw):
        q=cw@Rm.T-pc
        az=((np.arctan2(q[2],q[0])+3.7)/(2*np.pi))%1*len(WHEEL)
        i=int(az)%len(WHEEL); t=az-int(az)
        return K[WHEEL[i]]*(1-t)+K[WHEEL[(i+1)%len(WHEEL)]]*t
    for f,n,cen,cw in back:
        q=P[list(f)]; g=q.mean(0); q=g+(q-g)*0.97
        S.wash_poly(X(q),hue(cw),dens=dens*0.35,edge=0.3,wobble=3,mottle=0.1,gran=0.25)
    for f,n,cen,cw in front:
        q=P[list(f)]; g=q.mean(0); q=g+(q-g)*0.965
        lam=max(n@L,0)
        S.wash_poly(X(q),hue(cw),dens=dens*(0.6+0.25*(cw[2]<-0.1)+0.2*(cw[2]<0.6)-0.35*lam+0.25),edge=0.5,wobble=3,mottle=0.12,gran=0.3,pool=0.25)
    # edges: front solid, hidden faint dashed
    fe=set()
    for f,n,cen,cw in front:
        for a,b in ((0,1),(1,2),(0,2)): fe.add(tuple(sorted((f[a],f[b]))))
    for (i,j) in E:
        a,b=X(P[i]),X(P[j])
        if (i,j) in fe: S.line(a,b,0.6,over=7*s)
        else:
            m=12
            for t in range(0,m,2):
                S.line(a+(b-a)*t/m,a+(b-a)*(t+0.9)/m,0.3)
    # Euclid's triangle: apex, centre of the upper ring, a ring vertex
    ringc=V[ring].mean(0)
    # choose ring vertex most to the front-right
    rv=max(ring,key=lambda i: P[i,0])
    tri=np.array([P[top],ringc@Rm.T,P[rv]])
    S.wash_poly(X(tri),K['coral'],dens=0.22,edge=0.6,wobble=2,mottle=0.08)
    for a,b in ((0,1),(1,2),(0,2)): S.line(X(tri[a]),X(tri[b]),0.9,over=5*s)
    # ring circle (dashed ellipse) in pencil
    ang=np.linspace(0,2*np.pi,400)
    u=V[ring[0]]-ringc; u/=np.linalg.norm(u); w=np.cross([0,0,1],u)
    circ=(ringc+np.outer(np.cos(ang),u)+np.outer(np.sin(ang),w))@Rm.T
    pts=X(circ)
    for k in range(0,400,8): S.stroke(pts[k:k+5],0.35)
    # right-angle tick at ring centre
    a=tri[1]; d1=(tri[0]-a); d2=(tri[2]-a); d1/=np.linalg.norm(d1); d2/=np.linalg.norm(d2); e=0.09
    S.stroke(X(np.array([a+d1*e,a+d1*e+d2*e,a+d2*e])),0.6)
    return X,tri
if __name__=='__main__':
    from PIL import Image
    S=Sheet(1024,1024,seed=7)
    paint_ico(S,512,520,300)
    Image.fromarray(to8(S.finish())).save('../proto/ico1.png')
