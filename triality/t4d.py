"""Core 4D math for the triality exploration.
- 24-cell vertices (weight construction): 8_v = {+-e_i}, 8_s/8_c = {(+-1/2)^4} even/odd parity.
- edges = vertex pairs at minimal distance (the 24-cell's 96 edges)
- triality T: orthogonal 4x4, order 3, cyclically permuting the three 16-cells (found by group search)
- D4 roots, simple roots, Coxeter element + Coxeter-plane projection basis
"""
import numpy as np, itertools

# ---------- 24-cell, weight (minuscule) construction ----------
def cell24_weights():
    V=[]; cls=[]
    for i in range(4):                     # 8_v : +-e_i
        for s in (1,-1):
            v=[0,0,0,0]; v[i]=s; V.append(v); cls.append(0)
    for signs in itertools.product((1,-1),repeat=4):    # (+-1/2)^4
        v=[0.5*s for s in signs]
        parity=sum(1 for s in signs if s<0)%2
        V.append(v); cls.append(1 if parity==0 else 2)   # 1=8_s even, 2=8_c odd
    return np.array(V,float), np.array(cls)

def edges_of(V, tol=1e-6):
    n=len(V); D=np.sqrt(((V[:,None,:]-V[None,:,:])**2).sum(-1))
    dmin=D[D>tol].min()
    E=[(i,j) for i in range(n) for j in range(i+1,n) if abs(D[i,j]-dmin)<1e-6]
    return E, dmin

# ---------- group search for the triality isometry ----------
def _signed_perm_gens():
    G=[]
    # coordinate transpositions
    for (i,j) in [(0,1),(1,2),(2,3)]:
        M=np.eye(4); M[[i,j]]=M[[j,i]]; G.append(M)
    # sign flip of coord 0
    M=np.eye(4); M[0,0]=-1; G.append(M)
    return G

def _hadamard():
    return 0.5*np.array([[1,1,1,1],[1,1,-1,-1],[1,-1,1,-1],[1,-1,-1,1]],float)

def _key(M): return tuple(np.round(M.flatten()*1e6).astype(np.int64))

def symmetry_group():
    gens=_signed_perm_gens()+[_hadamard()]
    seen={_key(np.eye(4)):np.eye(4)}; frontier=[np.eye(4)]
    while frontier:
        nf=[]
        for M in frontier:
            for g in gens:
                P=g@M; k=_key(P)
                if k not in seen:
                    seen[k]=P; nf.append(P)
        frontier=nf
    return list(seen.values())

def vertex_perm(M, V, tol=1e-6):
    """return index permutation induced by M on vertex list V, or None if not a symmetry."""
    W=(M@V.T).T
    idx=[]
    for w in W:
        d=np.abs(V-w).sum(1); j=int(d.argmin())
        if d[j]>tol: return None
        idx.append(j)
    if len(set(idx))!=len(V): return None
    return idx

def find_triality():
    V,cls=cell24_weights()
    G=symmetry_group()
    for M in G:
        p=vertex_perm(M,V)
        if p is None: continue
        # induced action on classes: must cycle 0->1->2->0
        # check class of image of each class is constant
        img={}
        ok=True
        for i,j in enumerate(p):
            img.setdefault(cls[i],set()).add(cls[j])
        if any(len(s)!=1 for s in img.values()): continue
        m={c:next(iter(s)) for c,s in img.items()}
        if m.get(0)==1 and m.get(1)==2 and m.get(2)==0:
            # order 3?
            if np.allclose(M@M@M, np.eye(4), atol=1e-9):
                return M, V, cls, G
    raise RuntimeError("triality not found")

# ---------- D4 roots, simple roots, Coxeter plane ----------
def d4_roots():
    R=[]
    for i in range(4):
        for j in range(i+1,4):
            for si in (1,-1):
                for sj in (1,-1):
                    v=[0,0,0,0]; v[i]=si; v[j]=sj; R.append(v)
    return np.array(R,float)

def simple_roots():
    return np.array([[1,-1,0,0],[0,1,-1,0],[0,0,1,-1],[0,0,1,1]],float)

def reflection(v, a):
    return v - 2*np.dot(v,a)/np.dot(a,a)*a

def coxeter_element():
    S=simple_roots();
    def s(a):
        A=np.eye(4)
        for i in range(4):
            A[:,i]=reflection(np.eye(4)[:,i],a)
        return A
    C=np.eye(4)
    for a in S:
        C = s(a)@C
    return C

def coxeter_plane_basis():
    C=coxeter_element()
    w,v=np.linalg.eig(C)
    # eigenvalue closest to e^{i pi/3} (h=6)
    target=np.exp(1j*np.pi/3)
    k=int(np.argmin(np.abs(w-target)))
    z=v[:,k]
    u=np.real(z); t=np.imag(z)
    u=u/np.linalg.norm(u)
    t=t-np.dot(t,u)*u; t=t/np.linalg.norm(t)
    return u,t

def _coxeter_from_simples(S):
    def s(a):
        A=np.eye(4)
        for i in range(4):
            A[:,i]=reflection(np.eye(4)[:,i],a)
        return A
    C=np.eye(4)
    for a in S: C=s(a)@C
    return C

def f4_simple_roots():
    return np.array([[0,1,-1,0],[0,0,1,-1],[0,0,0,1],[0.5,-0.5,-0.5,-0.5]],float)

def coxeter_plane_basis_f4():
    C=_coxeter_from_simples(f4_simple_roots())
    w,v=np.linalg.eig(C)
    target=np.exp(1j*2*np.pi/12)            # F4 Coxeter number h=12
    k=int(np.argmin(np.abs(w-target)))
    z=v[:,k]; u=np.real(z); t=np.imag(z)
    u=u/np.linalg.norm(u); t=t-np.dot(t,u)*u; t=t/np.linalg.norm(t)
    return u,t

if __name__=="__main__":
    V,cls=cell24_weights()
    E,dmin=edges_of(V)
    print("vertices",len(V),"classes",[int((cls==k).sum()) for k in (0,1,2)])
    print("edges",len(E),"min dist",round(dmin,4))
    print("all norms ~1:", np.allclose(np.linalg.norm(V,axis=1),1))
    T,V,cls,G=find_triality()
    print("symmetry group order",len(G))
    print("triality T found, order3:",np.allclose(T@T@T,np.eye(4)))
    print("T orthogonal:",np.allclose(T@T.T,np.eye(4)))
    print("T=\n",np.round(T,3))
    p=vertex_perm(T,V)
    print("class map:",[ (int(cls[i]),int(cls[p[i]])) for i in [0,8,16] ])
    R=d4_roots(); print("D4 roots",len(R))
    u,t=coxeter_plane_basis(); print("coxeter plane basis ok, u.t=",round(float(np.dot(u,t)),6))
