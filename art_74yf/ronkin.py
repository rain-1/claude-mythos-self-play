"""
ronkin.py — 02 companion: THE RONKIN FUNCTION and the ORDER MAP.
N(x,y) = (1/(2pi)^2) int int log|P(e^{x+is},e^{y+it})| ds dt  is a CONVEX function.
Its gradient  grad N  takes exactly the INTEGER lattice value (i,j) on the bounded
complement component of the amoeba of 'order (i,j)' (Forsberg-Passare-Tsikh), and is
non-integer only ON the amoeba itself.  So rounding grad N labels every hole by a
lattice point of the Newton polygon; the discontinuity locus of that label IS the
tropical curve.  This is the amoeba's COMBINATORIAL skeleton: the same object, but
now the negative space is the subject, coloured by its arithmetic name.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from tropical import ronkin_and_order

A = np.array([[0.0, np.sqrt(3)/2],[-1.0, 0.5]])

def curve(d, lam):
    C=np.zeros((d+1,d+1),complex)
    for i in range(d+1):
        for j in range(d+1):
            if i+j<=d:
                k=d-i-j
                C[i,j]=((-1)**(i+j))*np.exp(-lam*(i*i+j*j+k*k))
    return C

def build(d,lam,half,Ng=220,Kphase=112,tag='ronkin'):
    C=curve(d,lam)
    # frame in (x,y): the symmetric-embedding center maps back; sample a square that
    # covers the body.  Use a generous (x,y) window then embed.
    R=half/ (np.sqrt(3)/2) * 1.15   # rough back-map scale
    xr=(-R,R); yr=(-R,R)
    N,gx,gy=ronkin_and_order(C,xr,yr,Ng,Ng,Kphase)
    np.savez(f'{tag}_field.npz',N=N,gx=gx,gy=gy,xr=xr,yr=yr,d=d,lam=lam,half=half)
    print(tag,'computed N range',round(N.min(),2),round(N.max(),2),
          'grad max',round(np.hypot(gx,gy).max(),2))
    return N,gx,gy,xr,yr

if __name__=='__main__':
    import sys
    d=int(sys.argv[1]); lam=float(sys.argv[2]); half=float(sys.argv[3])
    Ng=int(sys.argv[4]) if len(sys.argv)>4 else 220
    build(d,lam,half,Ng=Ng,tag=sys.argv[-1] if not sys.argv[-1][0].isdigit() else 'ronkin')
