import sys, numpy as np, collections, json
from numpy.polynomial import polynomial as Pn
from gn import run, parts
from classify import mapdeg
from cwbase import in_cw_orbit
res={}
tl=float(sys.argv[1]); real=sys.argv[2]=='real'
configs=[tuple(map(int,c.split(','))) for c in sys.argv[3:]]
for kx,ky,j in configs:
    s,k=run(kx,ky,j,10**6,kx*100+ky*10+j+7,tl,real=real)
    c=collections.Counter(); ex={}
    for A,B,C,D in s:
        dx,dy=mapdeg(A,B),mapdeg(C,D)
        if dx==0 or dy==0: c[('deg0',dx,dy)]+=1; continue
        rng=np.random.default_rng(0); pts=[]
        for t in rng.normal(size=4)+0.3j*rng.normal(size=4):
            pts.append((np.array([Pn.polyval(t,A),Pn.polyval(t,B)]),np.array([Pn.polyval(t,C),Pn.polyval(t,D)])))
        cw=in_cw_orbit(pts)
        key=(dx,dy,'CW' if cw else 'new')
        c[key]+=1; ex.setdefault(key,(A,B,C,D))
    print((kx,ky,j),'starts',k,'conv',len(s),dict(c),flush=True)
    res[(kx,ky,j)]=ex
import pickle; pickle.dump(res,open('gn_%s_examples.pkl'%sys.argv[2],'wb'))
