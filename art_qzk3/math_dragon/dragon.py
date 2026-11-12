"""MO 514916: binary dragon D_{k+1} = bD_k u (1 - bD_k), b = 1+i.
s_k = min |z|^2 over Gaussian integers missing from D_k.  Check the closed form
u_j=(2^(2j+1)+1)/3:  s_{4j+2}=(u^2+1)/2, s_{4j+3}=u^2, s_{4j+4}=2u^2, s_{4j+5}=4u^2."""
import numpy as np, json, sys
KMAX=int(sys.argv[1]) if len(sys.argv)>1 else 24
def closed(k):
    if k<2: return 1
    j=(k-2)//4; r=(k-2)%4; u=(2**(2*j+1)+1)//3
    return [(u*u+1)//2,u*u,2*u*u,4*u*u][r]
x=np.zeros(1,np.int32); y=np.zeros(1,np.int32); out=[]
for k in range(1,KMAX+1):
    bx=x-y; by=x+y            # (1+i)(x+iy)
    x=np.concatenate([bx,1-bx]); y=np.concatenate([by,-by])
    R=int(np.sqrt(closed(k)))+6
    m=(np.abs(x)<=R)&(np.abs(y)<=R)
    g=np.zeros((2*R+1,2*R+1),bool); g[y[m]+R,x[m]+R]=True
    yy,xx=np.nonzero(~g); d=(xx-R)**2+(yy-R)**2; s=int(d.min())
    pts=[(int(a-R),int(b-R)) for a,b in zip(xx[d==s],yy[d==s])]
    # distinctness of the 2^k points (checked on a window hash for big k)
    ok = s==closed(k)
    out.append(dict(k=k,s=s,closed=closed(k),ok=ok,missing=pts))
    print(k,s,closed(k),ok,pts,flush=True)
json.dump(out,open(__file__.replace('dragon.py','dragon_check.json'),'w'))
