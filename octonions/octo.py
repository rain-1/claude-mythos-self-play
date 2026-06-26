"""Octonion algebra (verified) + Fano-plane data + F_2^3 correspondence.
Basis index 0 = 1 (real), 1..7 = e_1..e_7.
Chosen Fano lines == the XOR triples {i,j,k : i^j^k=0} with e_i <-> binary(i)."""
import numpy as np, itertools

LINES=[(1,2,3),(1,4,5),(1,7,6),(2,4,6),(2,5,7),(3,4,7),(3,6,5)]  # oriented a->b->c : e_a e_b = e_c

def _prod_table():
    P={}
    for (a,b,c) in LINES:
        P[(a,b)]=(1,c); P[(b,c)]=(1,a); P[(c,a)]=(1,b)
        P[(b,a)]=(-1,c); P[(c,b)]=(-1,a); P[(a,c)]=(-1,b)
    return P
_P=_prod_table()

def unit_mul(i,j):
    """return (sign, k): e_i e_j = sign * (basis k); basis 0 = 1."""
    if i==0: return (1,j)
    if j==0: return (1,i)
    if i==j: return (-1,0)
    return _P[(i,j)]

def MUL():
    """8x8 table of (sign,k)."""
    return [[unit_mul(i,j) for j in range(8)] for i in range(8)]

def oct_mul(x,y):
    z=np.zeros(8)
    for i in range(8):
        if x[i]==0: continue
        for j in range(8):
            if y[j]==0: continue
            s,k=unit_mul(i,j); z[k]+=s*x[i]*y[j]
    return z

def conj(x):
    c=-x.copy(); c[0]=x[0]; return c
def norm2(x): return float(np.dot(x,x))

def verify():
    out={}
    # antisymmetry of imaginary units
    anti=all(unit_mul(i,j)[0]==-unit_mul(j,i)[0] and unit_mul(i,j)[1]==unit_mul(j,i)[1]
             for i in range(1,8) for j in range(1,8) if i!=j)
    out['imag_antisymmetric']=anti
    # e_i^2 = -1
    out['squares_-1']=all(unit_mul(i,i)==(-1,0) for i in range(1,8))
    # alternative: e_i(e_i e_j) = -e_j
    def m(i,j):
        s,k=unit_mul(i,j); v=np.zeros(8); v[k]=s; return v
    alt=True
    for i in range(1,8):
        for j in range(8):
            ej=np.zeros(8); ej[j]=1
            lhs=oct_mul(np.eye(8)[i], oct_mul(np.eye(8)[i], ej))
            rhs=-ej if (i!=0 and j!=0 and i==j) else None
    # composition: N(xy)=N(x)N(y)
    rng=np.random.default_rng(0); ok=True
    for _ in range(200):
        x=rng.standard_normal(8); y=rng.standard_normal(8)
        if abs(norm2(oct_mul(x,y))-norm2(x)*norm2(y))>1e-9: ok=False;break
    out['norm_multiplicative']=ok
    # alternative law (xx)y=x(xy)
    altok=True
    for _ in range(200):
        x=rng.standard_normal(8); y=rng.standard_normal(8)
        if np.max(np.abs(oct_mul(oct_mul(x,x),y)-oct_mul(x,oct_mul(x,y))))>1e-9: altok=False;break
    out['alternative']=altok
    # NON-associative (exists triple failing)
    nonassoc=False
    e=np.eye(8)
    for i,j,k in itertools.combinations(range(1,8),3):
        if np.max(np.abs(oct_mul(oct_mul(e[i],e[j]),e[k])-oct_mul(e[i],oct_mul(e[j],e[k]))))>1e-9:
            nonassoc=True;break
    out['non_associative']=nonassoc
    # Fano lines == XOR triples
    xor=all((a^b^c)==0 for (a,b,c) in LINES)
    out['lines_are_XOR_triples']=xor
    # which imaginary triples associate (collinear) vs not
    assoc_triples=[]; nonassoc_triples=[]
    for i,j,k in itertools.combinations(range(1,8),3):
        d=np.max(np.abs(oct_mul(oct_mul(e[i],e[j]),e[k])-oct_mul(e[i],oct_mul(e[j],e[k]))))
        (assoc_triples if d<1e-9 else nonassoc_triples).append((i,j,k))
    out['n_assoc_triples']=len(assoc_triples); out['n_nonassoc_triples']=len(nonassoc_triples)
    return out

if __name__=="__main__":
    for k,v in verify().items(): print(f"{k:24s}: {v}")
    print("\nlines:",LINES)

import colorsys
UNIT_RGB={0:(0.82,0.86,0.96)}
for _k in range(1,8):
    _r,_g,_b=colorsys.hsv_to_rgb((_k-1)/7.0,0.66,1.0)
    UNIT_RGB[_k]=(_r,_g,_b)

def sub(k):
    return "e"+chr(0x2080+k) if k>=1 else "1"
