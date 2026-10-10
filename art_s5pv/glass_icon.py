# glass_icon.py — orthographic sorbet-glass hexagonal prism (convex half-spaces, chord tint + edge light)
import numpy as np
def rotm(ax,ang):
    ax=np.asarray(ax,float);ax/=np.linalg.norm(ax);c,s=np.cos(ang),np.sin(ang);x,y,z=ax
    return np.array([[c+x*x*(1-c),x*y*(1-c)-z*s,x*z*(1-c)+y*s],[y*x*(1-c)+z*s,c+y*y*(1-c),y*z*(1-c)-x*s],[z*x*(1-c)-y*s,z*y*(1-c)+x*s,c+z*z*(1-c)]])
def prism_planes(R,ratio):
    """planes n.x<=d of a hexagonal prism (apothem 1, half height ratio), rotated by R (crystal->view)"""
    ns=[np.array([np.cos(k*np.pi/3),np.sin(k*np.pi/3),0]) for k in range(6)]+[np.array([0,0,1.]),np.array([0,0,-1.])]
    ds=[1]*6+[ratio,ratio]
    return np.array([R@n for n in ns]),np.array(ds,float)
def render(size,R,ratio,tint,scale=2.2,bg=None):
    """returns rgb (size,size,3) float in [0,1] and alpha. view along -z (camera looks down -z), x right, y up"""
    n,dd=prism_planes(R,ratio)
    u=(np.arange(size)+0.5)/size*2-1
    X,Y=np.meshgrid(u*scale,-u*scale)
    o=np.stack([X,Y,np.full_like(X,10)],-1);dv=np.array([0,0,-1.])
    dn=n@dv;num=dd[None,None,:]-o@n.T
    t=num/np.where(np.abs(dn)<1e-12,1e-12,dn)
    te=np.where(dn<0,t,-1e9).max(-1);tx=np.where(dn>0,t,1e9).min(-1)
    hit=te<tx;ch=np.clip(tx-te,0,None)
    # edge light: at entry and exit points, slack to the second-nearest plane
    def edge(tt):
        p=o+tt[...,None]*dv;sl=dd[None,None,:]-p@n.T;sl=np.sort(np.abs(sl),-1)[...,1];return sl
    e=np.minimum(edge(te),edge(tx))
    ew=np.exp(-(e/(0.018*scale))**2)
    absb=np.asarray(tint,float)
    col=np.exp(-ch[...,None]*absb*0.55)
    # facet sheen from entry face normal
    fe=np.argmax(np.where(dn<0,t,-1e9),-1);nf=n[fe]
    sheen=np.clip(nf@np.array([-0.4,0.6,0.7]),0,1)**6*0.35
    rgb=col+sheen[...,None]+ew[...,None]*0.7
    a=hit.astype(float)
    return np.clip(rgb,0,1.2),a
