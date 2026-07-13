"""Verify the three localization theorems in code before any pixels (von Dyck discipline)."""
import numpy as np
from scipy.linalg import svdvals

rng = np.random.default_rng(7)

def gersh_discs(A):
    d = np.diag(A).astype(complex)
    R = np.sum(np.abs(A), axis=1) - np.abs(np.diag(A))   # row radii
    return d, R

def in_gershgorin(A, tol=1e-9):
    lam = np.linalg.eigvals(A)
    d, R = gersh_discs(A)
    ok = True
    for l in lam:
        if not np.any(np.abs(l - d) <= R + tol):
            ok = False
    return ok

def in_brauer(A, tol=1e-7):
    """Every eigenvalue lies in some Cassini oval |z-a_ii||z-a_jj| <= R_i R_j, i<j."""
    lam = np.linalg.eigvals(A)
    d, R = gersh_discs(A)
    n = len(d)
    ok = True
    for l in lam:
        inside = False
        for i in range(n):
            for j in range(i+1, n):
                if np.abs(l-d[i])*np.abs(l-d[j]) <= R[i]*R[j] + tol:
                    inside = True; break
            if inside: break
        if not inside: ok = False
    return ok

def capture_counts(A, tol=1e-9):
    """2nd Gershgorin theorem: connected component of k discs holds exactly k eigenvalues."""
    d, R = gersh_discs(A); n = len(d)
    # union-find on disc overlap
    parent = list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for i in range(n):
        for j in range(i+1,n):
            if np.abs(d[i]-d[j]) <= R[i]+R[j]:
                parent[find(i)]=find(j)
    comps={}
    for i in range(n): comps.setdefault(find(i),[]).append(i)
    lam = np.linalg.eigvals(A)
    results=[]
    for root,members in comps.items():
        # count eigenvalues inside the union of these discs (and not inside any other comp's discs)
        cnt=0
        for l in lam:
            if np.any(np.abs(l-d[members])<=R[members]+tol):
                cnt+=1
        results.append((len(members),cnt))
    return results

# --- Brauer is tighter than Gershgorin: Cassini ovals subset of disc union ---
def brauer_inside_gershgorin(A, N=200):
    d,R=gersh_discs(A); n=len(d)
    # sample points in each Cassini oval, check they lie in the disc union
    lo=min(d.real-R.max()); hi=max(d.real+R.max())
    xs=np.linspace(lo-1,hi+1,N); ys=np.linspace(lo-1,hi+1,N)
    X,Y=np.meshgrid(xs,ys); Z=X+1j*Y
    cass=np.zeros(Z.shape,bool)
    for i in range(n):
        for j in range(i+1,n):
            cass |= (np.abs(Z-d[i])*np.abs(Z-d[j]) <= R[i]*R[j])
    disc=np.zeros(Z.shape,bool)
    for i in range(n):
        disc |= (np.abs(Z-d[i])<=R[i])
    # every cassini point must be a disc point
    return np.all(disc[cass])

for trial in range(6):
    n=rng.integers(5,12)
    A=(rng.standard_normal((n,n))+1j*rng.standard_normal((n,n)))
    # make it diagonally interesting: boost diagonal spread
    A[np.diag_indices(n)] += rng.standard_normal(n)*4 + 1j*rng.standard_normal(n)*4
    g=in_gershgorin(A); b=in_brauer(A); bg=brauer_inside_gershgorin(A)
    caps=capture_counts(A)
    cap_ok=all(k==c for k,c in caps)
    print(f"trial {trial}: n={n}  gershgorin={g}  brauer={b}  brauer⊂disc={bg}  capture_exact={cap_ok}  comps={caps}")

# --- pseudospectra sanity: sigma_min at an eigenvalue is ~0 ---
A=rng.standard_normal((8,8))
lam=np.linalg.eigvals(A)
z=lam[0]
smin=svdvals(z*np.eye(8)-A).min()
print(f"pseudospectra: sigma_min at an eigenvalue = {smin:.2e} (should be ~0)")
