# Convex shapes with arc-length (or angle) parametrisation s in [0,S), periodic extension.
# Each shape provides pt(s), W(s)=int_0^s B x B' (twice swept area), len(s) (arc length from 0), S, A (area), Ltot.
import numpy as np
from scipy.special import ellipeinc
def cross(a,b): return a[...,0]*b[...,1]-a[...,1]*b[...,0]
class Composite:
    """closed CCW boundary made of ('seg',P,Q) and ('arc',C,R,a0,a1) elements, parametrised by arc length."""
    def __init__(s,name,elems,scale_to_area=np.pi):
        s.name=name; s.elems0=elems; s._build(elems)
        if scale_to_area:
            k=np.sqrt(scale_to_area/s.A); el=[]
            for e in elems:
                if e[0]=='seg': el.append(('seg',np.asarray(e[1])*k,np.asarray(e[2])*k))
                else: el.append(('arc',np.asarray(e[1])*k,e[2]*k,e[3],e[4]))
            s._build(el)
    def _build(s,elems):
        s.elems=[]; off=0.0; Woff=0.0
        for e in elems:
            if e[0]=='seg':
                P=np.asarray(e[1],float); Q=np.asarray(e[2],float); l=np.linalg.norm(Q-P); u=(Q-P)/l
                s.elems.append(dict(kind='seg',P=P,u=u,l=l,off=off,Woff=Woff,k=0.0)); Woff+=cross(P,u)*l
            else:
                C=np.asarray(e[1],float); R=e[2]; a0,a1=e[3],e[4]; l=R*(a1-a0)
                d=dict(kind='arc',C=C,R=R,a0=a0,l=l,off=off,Woff=Woff,k=1/R); s.elems.append(d)
                Woff+=s._Warc(d,l)
            off+=l
        s.S=off; s.Ltot=off; s.Wtot=Woff; s.A=Woff/2
        s.offs=np.array([e['off'] for e in s.elems]+[off])
    @staticmethod
    def _Warc(d,sig):
        C,R,a0=d['C'],d['R'],d['a0']; a=a0+sig/R
        return R*(C[0]*(np.sin(a)-np.sin(a0))-C[1]*(np.cos(a)-np.cos(a0))+R*(a-a0))
    def _loc(s,x):
        x=np.asarray(x,float); n=np.floor(x/s.S); y=x-n*s.S
        idx=np.clip(np.searchsorted(s.offs,y,side='right')-1,0,len(s.elems)-1)
        return n,y,idx
    def pt(s,x):
        n,y,idx=s._loc(x); x=np.asarray(x,float); out=np.zeros(x.shape+(2,))
        for j,e in enumerate(s.elems):
            m=idx==j
            if not np.any(m): continue
            sig=y[m]-e['off']
            if e['kind']=='seg': out[m]=e['P']+sig[:,None]*e['u']
            else:
                a=e['a0']+sig/e['R']; out[m]=e['C']+e['R']*np.stack([np.cos(a),np.sin(a)],-1)
        return out
    def W(s,x):
        n,y,idx=s._loc(x); x=np.asarray(x,float); out=n*s.Wtot
        for j,e in enumerate(s.elems):
            m=idx==j
            if not np.any(m): continue
            sig=y[m]-e['off']
            out[m]=out[m]+e['Woff']+(cross(e['P'],e['u'])*sig if e['kind']=='seg' else s._Warc(e,sig))
        return out
    def length(s,x): return np.asarray(x,float)
    def sample(s,a,b,ds=0.004):
        """points along boundary from param a to b (a<b), including element corners."""
        n=max(2,int(np.ceil((b-a)/ds))+1); xs=np.linspace(a,b,n)
        k0=np.floor(a/s.S); cs=np.concatenate([s.offs[:-1]+k*s.S for k in (k0-1,k0,k0+1,k0+2)])
        xs=np.unique(np.concatenate([xs,cs[(cs>a)&(cs<b)]]))
        return s.pt(xs)
class Ellipse:
    def __init__(s,name,a,b,scale_to_area=np.pi):
        k=np.sqrt(scale_to_area/(np.pi*a*b)) if scale_to_area else 1.0
        s.name=name; s.a=a*k; s.b=b*k; s.S=2*np.pi; s.A=np.pi*s.a*s.b; s.Wtot=2*s.A
        assert s.a>=s.b; s.m=1-(s.b/s.a)**2
        s.Ltot=s.length(np.array([2*np.pi]))[0]
    def pt(s,t): t=np.asarray(t,float); return np.stack([s.a*np.cos(t),s.b*np.sin(t)],-1)
    def W(s,t): return s.a*s.b*np.asarray(t,float)
    def length(s,t):
        t=np.asarray(t,float); return s.a*(ellipeinc(t+np.pi/2,s.m)-ellipeinc(np.pi/2,s.m))
    def sample(s,a,b,ds=0.004):
        n=max(2,int(np.ceil((b-a)*max(s.a,s.b)/ds))+1); return s.pt(np.linspace(a,b,n))
def polygon(name,V):
    V=np.asarray(V,float); n=len(V); return Composite(name,[('seg',V[i],V[(i+1)%n]) for i in range(n)])
def regular(n,name):
    th=np.pi/2+2*np.pi*np.arange(n)/n; return polygon(name,np.stack([np.cos(th),np.sin(th)],1))
def all_shapes():
    S=[]
    S.append(Composite('disc',[('arc',(0,0),1.0,0.0,2*np.pi)]))
    S.append(polygon('square',[(0,0),(1,0),(1,1),(0,1)]))
    for asp in (1.5,2.0,3.0):
        S.append(polygon('rect_%g'%asp,[(0,0),(asp,0),(asp,1),(0,1)]))
    S.append(regular(3,'triangle'))
    S.append(regular(5,'pentagon'))
    S.append(regular(6,'hexagon'))
    for ba in (0.95,0.8,0.5):
        S.append(Ellipse('ellipse_b%g'%ba,1.0,ba))
    S.append(Composite('stadium',[('seg',(-1,-1),(1,-1)),('arc',(1,0),1.0,-np.pi/2,np.pi/2),
                                   ('seg',(1,1),(-1,1)),('arc',(-1,0),1.0,np.pi/2,3*np.pi/2)]))
    V=[np.array([np.cos(np.pi/2+2*np.pi*k/3),np.sin(np.pi/2+2*np.pi*k/3)]) for k in range(3)]
    el=[]
    for k in range(3):
        C=V[k]; P=V[(k+1)%3]; a0=np.arctan2(*(P-C)[::-1]); el.append(('arc',C,np.sqrt(3),a0,a0+np.pi/3))
    S.append(Composite('reuleaux',el))
    S.append(Composite('halfdisc',[('seg',(-1,0),(1,0)),('arc',(0,0),1.0,0.0,np.pi)]))
    return S
if __name__=="__main__":
    for sh in all_shapes():
        x=np.linspace(0,sh.S,20001); P=sh.pt(x)
        Ashoe=0.5*np.sum(cross(P[:-1],P[1:])); Lpoly=np.sum(np.linalg.norm(np.diff(P,axis=0),axis=1))
        # check W consistency & continuity
        print('%-12s A=%.6f (shoelace %.6f) L=%.6f (poly %.6f) W(S)/2=%.6f'%(sh.name,sh.A,Ashoe,sh.Ltot,Lpoly,sh.W(np.array([sh.S]))[0]/2))
