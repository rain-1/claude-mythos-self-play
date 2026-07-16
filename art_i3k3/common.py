import numpy as np
# The verified newly-reducible cubic (MathOverflow seed 2026-07-16):
#   f(x) = x^3 - x^2 - 3x + 1  is irreducible over Q,
#   but f^n factors into exactly TWO irreducibles of degree [3^{n-1}, 2*3^{n-1}]
#   for every n>=2  (verified to n=4 with sympy).  A permanent 1:2 schism.
# The roots of f^n are exactly f^{-n}(0): the arboreal preimage tree of 0.
FC = [1.0, -1.0, -3.0, 1.0]            # f coefficients
CUBFAC = np.roots([1,0,-4,-2])         # level-2 cubic factor x^3-4x-2 (basin A)
GOLD = np.array([1.00, 0.62, 0.15])
CYAN = np.array([0.17, 0.68, 1.00])
NEUT = np.array([0.90, 0.85, 0.72])
EMBER= np.array([1.00, 0.42, 0.14])
def f(z):  return z*z*z - z*z - 3*z + 1
def preim(z):                          # roots of f(w)=z
    return np.roots([1.0,-1.0,-3.0,(1.0-z)])

def build_tree(maxlevel, cap=2_000_000, seed=7):
    """Return dict level -> list of (value, basin) with basin fixed at level 2."""
    rng=np.random.default_rng(seed)
    L={1:[(complex(r),'N') for r in np.roots(FC)]}
    L2=[]
    for z in preim(0j):
        for w in preim(z):
            L2.append((w,'A' if min(abs(w-r) for r in CUBFAC)<1e-6 else 'B'))
    L[2]=L2; cur=L2
    for n in range(3,maxlevel+1):
        nxt=[]
        for w,l in cur:
            for v in preim(w): nxt.append((v,l))
        if len(nxt)>cap:
            idx=rng.choice(len(nxt),cap,replace=False)
            nxt=[nxt[i] for i in idx]
        cur=nxt; L[n]=cur
    return L

def basin_split(level):
    """roots of f^level split into (A_array, B_array) by basin."""
    L=build_tree(level)
    A=np.array([w for w,l in L[level] if l=='A'])
    B=np.array([w for w,l in L[level] if l=='B'])
    return A,B

def filmic(img,k=1.5,g=0.9):
    img=1-np.exp(-img*k)
    return np.clip(img,0,1)**g

def potential(Z, roots, chunk=1_500_000):
    """mean log|z - root| over roots (numerically-clean Green potential)."""
    out=np.zeros(len(Z)); r=roots[None,:]
    for i in range(0,len(Z),chunk):
        zz=Z[i:i+chunk][:,None]
        out[i:i+chunk]=np.mean(np.log(np.abs(zz-r)+1e-30),axis=1)
    return out

def downscale(img, factor):
    from PIL import Image
    h,w=img.shape[:2]
    im=Image.fromarray((np.clip(img,0,1)*255).astype('uint8'))
    return im.resize((w//factor,h//factor),Image.LANCZOS)
