"""Non-Pappus arrangement: 9 pseudolines in RP^2 drawn in the stereographic disc of the upper hemisphere.
Each pseudoline is a polyline from a rim point to its antipode. The Pappus line p is bent to miss its middle C."""
import numpy as np, geom
def stereo(P): return P[:,:2]/(1+P[:,2:3])
def great_half(n,K):
    u=geom.unit(np.cross(n,[0,0,1.])); w=np.cross(n,u)
    if w[2]<0: w=-w
    t=np.linspace(0,np.pi,K); return np.outer(np.cos(t),u)+np.outer(np.sin(t),w),u,w,t
def build(xfile='Y5.npy',K=6000,bend=0.035,sig=0.13,rot=0.0):
    x=np.load(xfile)
    lines,A,B,C=geom.config(x[:9].reshape(3,3),np.sort(x[9:12]),np.sort(x[12:15]))
    R=np.array([[np.cos(rot),-np.sin(rot),0],[np.sin(rot),np.cos(rot),0],[0,0,1]])
    lines={k:R@v for k,v in lines.items()}; C={k:R@v for k,v in C.items()}
    # which C is the middle one along p
    _,u0,w0,_=great_half(lines['p'],3)
    tt0=sorted((np.arctan2(np.dot(c,w0),np.dot(c,u0)),kk) for kk,c in C.items())
    cmid=tt0[1][1]
    paths={}; 
    order=['l','m','A1B2','A1B3','A2B1','A2B3','A3B1','A3B2','p']
    for k in order:
        P,u,w,t=great_half(lines[k],K)
        if k=='p':
            n=lines[k]
            tt={kk:np.arctan2(np.dot(c,w),np.dot(c,u)) for kk,c in C.items()}
            others=[kk for kk in C if kk!=cmid]
            ta,tb=sorted(tt[kk] for kk in others)
            tm=tt[cmid]
            fr=np.where(t<tm,(t-ta)/(tm-ta),(tb-t)/(tb-tm)); fr=np.clip(fr,0,1)
            disp=bend*(3*fr**2-2*fr**3)
            P=P+disp[:,None]*n[None]; P/=np.linalg.norm(P,axis=1,keepdims=True)
            global P_MID
            P_MID=(stereo(P[np.argmin(abs(t-tt[cmid]))][None])[0]+stereo(C[cmid][None])[0])/2
        paths[k]=stereo(P)
    # crossing points (vertices of the drawing) from the straight lines, excluding p∩{C3 lines} which moved
    return paths,lines,C,cmid,order
def vertices(paths,tol=2e-3):
    """intersections of the actual polylines (segment tests), merged into plazas with multiplicity."""
    ks=list(paths); pts=[]
    for i in range(len(ks)):
        for j in range(i+1,len(ks)):
            a=paths[ks[i]]; b=paths[ks[j]]
            # coarse search
            from scipy.spatial import cKDTree
            T=cKDTree(b); d,idx=T.query(a); k=np.argmin(d)
            pts.append((a[k]+b[idx[k]])/2)
    pts=np.array(pts); groups=[]
    for p in pts:
        for g in groups:
            if np.linalg.norm(g[0]-p)<tol: g[1]+=1; break
        else: groups.append([p,1])
    return [(g[0],{1:2,3:3,6:4}.get(g[1],g[1])) for g in groups]
if __name__=='__main__':
    paths,lines,C,cmid,order=build()
    V=vertices(paths)
    print(cmid,len(V),sorted(m for _,m in V))
