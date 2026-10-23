# Y-partitions of the unit disc into 3 convex pieces of equal area and perimeter.
# junction p=(r,0) (rotation fixed), boundary points at angles t0<t1<t2 (cyclic).
import numpy as np
from scipy.optimize import least_squares
def pieces(x):
    r,a,b,c=x; P=np.array([r,0.0]); T=np.array([a,b,c])
    out=[]
    for i in range(3):
        u=T[i]; v=T[(i+1)%3]+ (2*np.pi if i==2 else 0)
        phi=v-u; A=np.array([np.cos(u),np.sin(u)]); B=np.array([np.cos(v),np.sin(v)])
        seg=0.5*(phi-np.sin(phi))                       # between chord AB and arc
        tri=0.5*((A-P)[0]*(B-P)[1]-(A-P)[1]*(B-P)[0])  # signed, ccw positive
        area=seg+tri; per=phi+np.linalg.norm(A-P)+np.linalg.norm(B-P)
        out.append((area,per))
    return np.array(out)
def F(x):
    q=pieces(x); return np.r_[q[:,0]-np.pi/3, q[0,1]-q[1,1], q[1,1]-q[2,1]]
def convex(x):
    r,a,b,c=x; P=np.array([r,0.]); T=[a,b,c]
    ang=[np.arctan2(np.sin(t)-0,np.cos(t)-r) for t in T]
    d=np.sort(np.mod(np.array(ang),2*np.pi)); gaps=np.diff(np.r_[d,d[0]+2*np.pi])
    return gaps.max()<=np.pi+1e-9, gaps
sols=[]
rng=np.random.default_rng(1)
for k in range(20000):
    r=rng.uniform(0,0.95); t=np.sort(rng.uniform(-np.pi,np.pi,3))
    s=least_squares(F,np.r_[r,t],xtol=1e-15,ftol=1e-15,gtol=1e-15)
    if np.abs(F(s.x)).max()<1e-11 and 0<=s.x[0]<1 and s.x[1]<s.x[2]<s.x[3]<s.x[1]+2*np.pi:
        x=s.x.copy()
        ok,g=convex(x)
        key=np.round(np.r_[x[0],np.sort(np.mod(np.diff(np.r_[x[1:],x[1]+2*np.pi]),2*np.pi))],7)
        if not any(np.allclose(key,k2,atol=1e-6) for k2,_ in sols): sols.append((key,x)); print(key, ok, np.round(pieces(x),6).tolist())
