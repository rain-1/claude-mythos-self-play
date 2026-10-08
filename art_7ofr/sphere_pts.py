import numpy as np, sys
def E(n):
    x=np.arange(-n,n+1)
    X,Y=np.meshgrid(x,x,indexing='ij')
    r=n*n-X*X-Y*Y
    m=r>=0
    z=np.sqrt(np.where(m,r,0)).round().astype(np.int64)
    ok=m&(z*z==r)
    P=[]
    for sgn in (1,-1):
        P.append(np.stack([X[ok],Y[ok],sgn*z[ok]],1))
    P=np.concatenate(P); P=np.unique(P,axis=0)
    return P
if __name__=="__main__":
    for n in [int(a) for a in sys.argv[1:]]:
        P=E(n); print(n,len(P), len(P)/n)
