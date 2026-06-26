"""The group of order 168 = PSL(2,7) = PSL(3,2) = GL(3,2), verified.
Also: Fano plane data (cyclic Singer model), P^1(F_7) Mobius action, hyperbolic
helpers for the (2,3,7) tiling / Klein quartic figures."""
import numpy as np, itertools

# ---------- GL(3,2) = Aut(Fano) , order 168 ----------
def gl32_order():
    cnt=0
    for bits in itertools.product([0,1],repeat=9):
        M=np.array(bits,int).reshape(3,3)
        # determinant over F2 via row reduction rank
        if _rank2(M)==3: cnt+=1
    return cnt

def _rank2(M):
    A=M.copy()%2; r=0; rows,cols=A.shape
    for c in range(cols):
        piv=None
        for i in range(r,rows):
            if A[i,c]%2==1: piv=i;break
        if piv is None: continue
        A[[r,piv]]=A[[piv,r]]
        for i in range(rows):
            if i!=r and A[i,c]%2==1: A[i]=(A[i]+A[r])%2
        r+=1
    return r

# ---------- Fano plane: cyclic Singer model on Z_7 ----------
# points 0..6 ; base block (Singer / planar difference set) = quadratic residues mod 7
QR7=sorted({(x*x)%7 for x in range(1,7)})        # {1,2,4}
def fano_cyclic_lines():
    return [tuple(sorted(((q+k)%7) for q in QR7)) for k in range(7)]

# ---------- P^1(F_7): 8 points 0..6, inf=7 ----------
INF=7
def mobius(a,b,c,d,x):
    # over F_7 on P^1; x in 0..6 or INF
    if x==INF:
        # (a*inf+b)/(c*inf+d) -> a/c
        return INF if c%7==0 else (a*pow(c,5,7))%7
    num=(a*x+b)%7; den=(c*x+d)%7
    if den==0: return INF
    return (num*pow(den,5,7))%7      # 1/den = den^5 mod 7 (Fermat)

def psl27_order():
    # count distinct Mobius maps with ad-bc=1 mod7, modulo +-I, as permutations of 8 pts
    seen=set()
    pts=list(range(8))
    for a in range(7):
        for b in range(7):
            for c in range(7):
                for d in range(7):
                    if (a*d-b*c)%7!=1: continue
                    perm=tuple(mobius(a,b,c,d,x) for x in [0,1,2,3,4,5,6,INF])
                    seen.add(perm)
    return len(seen)

# ---------- hyperbolic (Poincare disk) helpers ----------
def su11_rot(theta):
    return np.array([[np.exp(1j*theta/2),0],[0,np.exp(-1j*theta/2)]],complex)
def su11_trans(d):
    return np.array([[np.cosh(d/2),np.sinh(d/2)],[np.sinh(d/2),np.cosh(d/2)]],complex)
def mob_apply(M,z):
    return (M[0,0]*z+M[0,1])/(M[1,0]*z+M[1,1])

def geodesic_arc(p,q,n=40):
    """sample the hyperbolic geodesic between disk points p,q (complex) as n pts."""
    p=complex(p); q=complex(q)
    # solve orthogonal circle center c: 2Re(conj(p)c)=|p|^2+1 ; same for q
    A=np.array([[p.real,p.imag],[q.real,q.imag]])
    rhs=np.array([(abs(p)**2+1)/2,(abs(q)**2+1)/2])
    det=A[0,0]*A[1,1]-A[0,1]*A[1,0]
    if abs(det)<1e-9:           # geodesic through origin -> straight chord
        return [p+(q-p)*t for t in np.linspace(0,1,n)]
    cx=(rhs[0]*A[1,1]-rhs[1]*A[0,1])/det
    cy=(A[0,0]*rhs[1]-A[1,0]*rhs[0])/det
    c=complex(cx,cy); rho=abs(p-c)
    a0=np.angle(p-c); a1=np.angle(q-c)
    da=(a1-a0+np.pi)%(2*np.pi)-np.pi
    return [c+rho*np.exp(1j*(a0+da*t)) for t in np.linspace(0,1,n)]

if __name__=="__main__":
    print("|GL(3,2)|            =",gl32_order())
    print("Fano cyclic lines   =",fano_cyclic_lines())
    print("QR mod 7            =",QR7)
    print("|PSL(2,7)| on P^1   =",psl27_order())
    # check cyclic lines form a valid Fano (each pair once)
    from itertools import combinations
    pc={}
    for L in fano_cyclic_lines():
        for a,b in combinations(L,2): pc[frozenset((a,b))]=pc.get(frozenset((a,b)),0)+1
    print("every pair once     =",all(v==1 for v in pc.values()), "num pairs",len(pc))
