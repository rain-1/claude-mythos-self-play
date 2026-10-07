"""Billiard orbit in a triangle (openai/math family 150 claims weak mixing whenever one angle is irrational wrt pi)."""
import numpy as np
def triangle(alpha,beta):
    # vertices A=(0,0), B=(1,0), angles alpha at A, beta at B
    gamma=np.pi-alpha-beta
    c=1.0; b=np.sin(beta)/np.sin(gamma)*c
    C=np.array([b*np.cos(alpha),b*np.sin(alpha)])
    return np.array([[0,0],[1,0],C])
def orbit(V,p,ang,nb):
    d=np.array([np.cos(ang),np.sin(ang)]); pts=[p.copy()]; last=-1
    for _ in range(nb):
        best=None
        for e in range(3):
            if e==last: continue
            a,b=V[e],V[(e+1)%3]; s=b-a
            M=np.array([[d[0],-s[0]],[d[1],-s[1]]])
            try: t,u=np.linalg.solve(M,a-p)
            except np.linalg.LinAlgError: continue
            if t>1e-12 and -1e-12<=u<=1+1e-12 and (best is None or t<best[0]): best=(t,e,s)
        t,e,s=best; p=p+t*d; n=np.array([-s[1],s[0]]); n/=np.linalg.norm(n)
        d=d-2*np.dot(d,n)*n; last=e; pts.append(p.copy())
    return np.array(pts)
